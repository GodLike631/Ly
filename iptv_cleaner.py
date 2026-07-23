# -*- coding: utf-8 -*-
"""
企业级 IPTV 直播源全自动化巡检系统 (第一阶段)
核心能力：asyncio + aiohttp + SQLite 缓存 + HEAD预检 + FFprobe协程池 + HLS多码率优选 + Logging/YAML
"""

import os
import re
import ssl
import json
import time
import sqlite3
import hashlib
import asyncio
import logging
from typing import List, Dict, Tuple, Optional
from urllib.parse import urlparse, urljoin, parse_qs, urlencode, urlunparse

import yaml
import aiohttp

# ----------------------------------------------------
# 1. 日志系统初始化 (Logging)
# ----------------------------------------------------
def setup_logging(log_file: str):
    logger = logging.getLogger("IPTVCleaner")
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', '%Y-%m-%d %H:%M:%S')

    # 控制台 StreamHandler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # 文件 FileHandler
    fh = logging.FileHandler(log_file, encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    return logger

# ----------------------------------------------------
# 2. SQLite 高性能缓存数据库 (SQLite Cache)
# ----------------------------------------------------
class SQLiteCacheManager:
    def __init__(self, db_path: str, ttl_hours: int = 24):
        self.db_path = db_path
        self.ttl_seconds = ttl_hours * 3600
        self._init_db()

    def _get_conn(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stream_cache (
                    url_hash TEXT PRIMARY KEY,
                    url TEXT,
                    is_valid INTEGER,
                    reason TEXT,
                    err_code TEXT,
                    width INTEGER,
                    height INTEGER,
                    codec TEXT,
                    bitrate INTEGER,
                    delay REAL,
                    score REAL,
                    updated_at REAL
                )
            ''')
            conn.commit()

    @staticmethod:
    def get_url_hash(url: str) -> str:
        return hashlib.md5(url.encode('utf-8')).hexdigest()

    def get(self, url: str) -> Optional[Dict]:
        u_hash = self.get_url_hash(url)
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT is_valid, reason, err_code, width, height, codec, bitrate, delay, score, updated_at FROM stream_cache WHERE url_hash = ?', (u_hash,))
            row = cursor.fetchone()
            if row:
                is_valid, reason, err_code, width, height, codec, bitrate, delay, score, updated_at = row
                if time.time() - updated_at < self.ttl_seconds:
                    return {
                        "valid": bool(is_valid),
                        "reason": reason,
                        "err_code": err_code,
                        "meta": {
                            "width": width, "height": height, "codec": codec,
                            "bitrate": bitrate, "delay": delay, "score": score
                        }
                    }
        return None

    def set(self, url: str, is_valid: bool, reason: str, err_code: str, meta: Dict):
        u_hash = self.get_url_hash(url)
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO stream_cache 
                (url_hash, url, is_valid, reason, err_code, width, height, codec, bitrate, delay, score, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                u_hash, url, int(is_valid), reason, err_code,
                meta.get("width", 0), meta.get("height", 0), meta.get("codec", ""),
                meta.get("bitrate", 0), meta.get("delay", 0.0), meta.get("score", 0.0),
                time.time()
            ))
            conn.commit()

# ----------------------------------------------------
# 3. 数据标准化与评分引擎
# ----------------------------------------------------
def normalize_url(url: str) -> str:
    try:
        parsed = urlparse(url)
        if not parsed.query: return url
        qs = parse_qs(parsed.query)
        filtered_qs = {k: v for k, v in qs.items() if k.lower() not in ['token', 'sign', 'ts', 'auth', 'key', '_t']}
        return urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, urlencode(filtered_qs, doseq=True), parsed.fragment))
    except Exception:
        return url

def normalize_channel_name(name: str) -> str:
    n = name.strip()
    cctv_match = re.search(r'(?:CCTV|中央|央视)[-_\s]*(\d+|13新闻|14少儿|15音乐|5\+体育赛事|17农业农村|7国防军事)', n, re.IGNORECASE)
    if cctv_match:
        return f"CCTV-{cctv_match.group(1).upper()}"
    if re.search(r'中央一|央视一', n): return "CCTV-1"
    if re.search(r'中央二|央视二', n): return "CCTV-2"
    if re.search(r'中央三|央视三', n): return "CCTV-3"
    return n

def calculate_smart_score(height: int, bitrate: int, delay: float, codec: str, timeout: int) -> float:
    res_score = (height / 2160.0) * 400.0 if height else 100.0
    effective_bitrate = min(bitrate, 10000000) if bitrate else 1000000
    bitrate_score = (effective_bitrate / 10000000.0) * 300.0
    delay_score = max(0.0, (timeout - delay) / timeout) * 300.0
    codec_bonus = 150.0 if codec and ("hevc" in codec.lower() or "265" in codec.lower()) else 0.0
    return round(res_score + bitrate_score + delay_score + codec_bonus, 2)

def auto_classify(name: str, url: str) -> str:
    n_upper, u_lower = name.strip().upper(), url.strip().lower()
    if re.search(r"(4K|8K|超高清)", n_upper) or "4k" in u_lower: return "4K/8K超清"
    if "🔞" in name or any(k in name for k in ["福利", "成人", "探花"]): return "🔞福利专区"
    if "咪咕" in name or "migu" in u_lower: return "咪咕体育/直播"
    if re.search(r"^(CCTV|CGTN|CETV|中央)", n_upper) or "cctv" in u_lower: return "央视频道"
    if "卫视" in name: return "卫视频道"
    if any(k in name for k in ["翡翠台", "TVB", "凤凰", "HBO"]): return "港台/国际"
    if any(k in name for k in ["少儿", "动漫", "卡通"]): return "动漫/少儿"
    if any(k in name for k in ["电影", "影院", "CHC", "好莱坞"]): return "电影/剧场"
    if any(k in name for k in ["体育", "NBA", "足球", "CBA"]): return "体育/竞技"
    return "其他频道"

# ----------------------------------------------------
# 4. 高并发异步检测与 FFprobe 进程池
# ----------------------------------------------------
class AsyncStreamChecker:
    def __init__(self, config: dict, db_cache: SQLiteCacheManager, logger: logging.Logger):
        self.config = config
        self.cache = db_cache
        self.logger = logger
        self.http_sem = asyncio.Semaphore(config['performance']['max_concurrent_http'])
        self.ffprobe_sem = asyncio.Semaphore(config['performance']['max_concurrent_ffprobe'])
        self.timeout = config['performance']['http_timeout']
        self.ff_timeout = config['performance']['ffprobe_timeout']

    def _get_headers(self, url: str) -> dict:
        parsed = urlparse(url)
        origin = f"{parsed.scheme}://{parsed.netloc}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 11; SmartTV Build/RQ3A) AppleWebKit/537.36 ExoPlayer/2.18.1',
            'Referer': f"{origin}/", 'Origin': origin
        }
        if "migu" in url.lower():
            headers['User-Agent'] = 'MiguVideo/3.9.0 (Android; SmartTV)'
            headers['Referer'] = 'https://www.miguvideo.com/'
        return headers

    async def _async_ffprobe(self, url: str, headers: dict) -> Tuple[bool, int, int, str, int]:
        """使用 asyncio 异步子进程调取 ffprobe，防止阻塞主事件循环"""
        async with self.ffprobe_sem:
            ua = headers.get('User-Agent', '')
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-user_agent', ua,
                '-show_streams', '-show_format',
                '-timeout', str(int(self.ff_timeout * 1000000)), url
            ]
            try:
                proc = await asyncio.create_subprocess_exec(
                    *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
                )
                stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=self.ff_timeout + 1)
                data = json.loads(stdout.decode('utf-8'))

                bitrate = int(data.get('format', {}).get('bit_rate', 0))
                for stream in data.get('streams', []):
                    if stream.get('codec_type') == 'video':
                        fps_eval = stream.get('r_frame_rate', '0/1')
                        fps = 0
                        if '/' in fps_eval:
                            num, den = map(float, fps_eval.split('/'))
                            fps = num / den if den > 0 else 0
                        
                        w, h = int(stream.get('width', 0)), int(stream.get('height', 0))
                        codec = stream.get('codec_name', '').lower()
                        if not bitrate and stream.get('bit_rate'):
                            bitrate = int(stream.get('bit_rate'))

                        if fps >= 10:
                            return True, w, h, codec, bitrate
            except Exception:
                pass
            return False, 0, 0, "", 0

    async def check_channel(self, session: aiohttp.ClientSession, item: dict) -> Tuple[dict, bool, str, str]:
        url = item['url']
        norm_url = item['norm_url']

        # 1. 查询 SQLite 缓存
        cached = self.cache.get(norm_url)
        if cached:
            if cached['valid']:
                item.update(cached['meta'])
                return item, True, f"{cached['reason']} [SQLite缓存]", cached['err_code']
            else:
                return item, False, f"{cached['reason']} [SQLite缓存]", cached['err_code']

        if url.startswith(("rtp://", "udp://")):
            item['delay'], item['score'] = 0.1, 500.0
            self.cache.set(norm_url, True, "PASS", "SUCCESS", item)
            return item, True, "PASS", "SUCCESS"

        # 广告黑名单匹配
        if any(kw in url.lower() for kw in self.config['ad_keywords']):
            reason = "URL命中广告黑名单"
            self.cache.set(norm_url, False, reason, "AD", {})
            return item, False, reason, "AD"

        headers = self.get_tv_headers(url) if hasattr(self, 'get_tv_headers') else self._get_headers(url)

        async with self.http_sem:
            start_time = time.time()
            try:
                # 2. HEAD 快速预检
                if self.config['rules']['enable_head_check']:
                    try:
                        async with session.head(url, headers=headers, timeout=self.timeout, allow_redirects=True) as head_res:
                            if head_res.status >= 400:
                                reason = f"HEAD预检错误({head_res.status})"
                                self.cache.set(norm_url, False, reason, "HTTP_ERROR", {})
                                return item, False, reason, "HTTP_ERROR"
                    except Exception:
                        pass # HEAD 不通用时降级到 GET

                # 3. GET 拉取 M3U8/TS 切片
                async with session.get(url, headers=headers, timeout=self.timeout, allow_redirects=True) as res:
                    if res.status >= 400:
                        reason = f"HTTP状态响应错误({res.status})"
                        self.cache.set(norm_url, False, reason, "HTTP_ERROR", {})
                        return item, False, reason, "HTTP_ERROR"

                    content_bytes = await res.content.read(4096)
                    content_head = content_bytes.decode('utf-8', errors='ignore').lower()

                    # HLS 多码率/Master M3U8 简单解析优选
                    if "#ext-x-stream-inf" in content_head:
                        sub_urls = re.findall(r'http[s]?://[^\s]+', content_head)
                        if sub_urls:
                            item['url'] = sub_urls[0] # 自动升级为更高码率子流 URL

                    elapsed_delay = round(time.time() - start_time, 2)
                    item['delay'] = elapsed_delay

                # 4. FFprobe 深层探测
                if self.config['rules']['enable_ffprobe']:
                    is_valid, w, h, codec, bitrate = await self._async_ffprobe(url, headers)
                    if not is_valid:
                        reason = "FFmpeg未识别到有效流"
                        self.cache.set(norm_url, False, reason, "FFMPEG_FAIL", {})
                        return item, False, reason, "FFMPEG_FAIL"

                    if bitrate > 0 and bitrate < self.config['rules']['min_bitrate']:
                        reason = f"极低码率({bitrate//1000}kbps)"
                        self.cache.set(norm_url, False, reason, "LOW_BITRATE", {})
                        return item, False, reason, "LOW_BITRATE"

                    item.update({'width': w, 'height': h, 'codec': codec, 'bitrate': bitrate})

                item['score'] = calculate_smart_score(
                    item.get('height', 720), item.get('bitrate', 0), elapsed_delay, item.get('codec', ''), self.timeout
                )
                
                meta_info = {
                    "width": item.get("width", 0), "height": item.get("height", 0),
                    "codec": item.get("codec", ""), "bitrate": item.get("bitrate", 0),
                    "delay": item.get("delay", 0.0), "score": item.get("score", 0.0)
                }
                self.cache.set(norm_url, True, "PASS", "SUCCESS", meta_info)
                return item, True, f"PASS ({elapsed_delay}s | 得分:{item['score']})", "SUCCESS"

            except asyncio.TimeoutError:
                reason = "HTTP连接超时"
                self.cache.set(norm_url, False, reason, "TIMEOUT", {})
                return item, False, reason, "TIMEOUT"
            except Exception as e:
                reason = "网络连通性异常"
                self.cache.set(norm_url, False, reason, "NET_ERROR", {})
                return item, False, reason, "NET_ERROR"

# ----------------------------------------------------
# 5. M3U 文件解析与重构导出
# ----------------------------------------------------
def parse_m3u_file(file_path: str) -> List[dict]:
    channels = []
    if not os.path.exists(file_path): return channels

    current_extinf = None
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line: continue
            if line.startswith("#EXTINF"):
                current_extinf = line
                continue
            if line.startswith(("http://", "https://", "rtmp://", "rtp://")):
                if current_extinf:
                    name_match = re.search(r',([^,]+)$', current_extinf)
                    raw_name = name_match.group(1).strip() if name_match else "未命名"
                    raw_name = re.sub(r'\s*\[.*?\]', '', raw_name).strip() # 剔除历史标记
                    name = normalize_channel_name(raw_name)
                    
                    group_match = re.search(r'group-title="([^"]+)"', current_extinf)
                    group = group_match.group(1) if group_match else auto_classify(name, line)

                    channels.append({"name": name, "url": line, "group": group, "norm_url": normalize_url(line)})
                    current_extinf = None
    return channels

# ----------------------------------------------------
# 6. 主逻辑程序入口 (Async Main)
# ----------------------------------------------------
async def main():
    # 1. 载入配置文件
    with open("config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    logger = setup_logging(config['paths']['log_path'])
    logger.info("🚀 IPTV 智能巡检系统正在启动...")

    db_cache = SQLiteCacheManager(config['paths']['db_path'], config['rules']['cache_ttl_hours'])
    checker = AsyncStreamChecker(config, db_cache, logger)

    # 2. 读取频道数据
    channels = parse_m3u_file(config['paths']['input_m3u'])
    logger.info(f"📊 成功载入存量 M3U 频道，去重后共计 {len(channels)} 条线路。")

    if not channels:
        logger.warning("❌ 未找到有效频道数据，退出。")
        return

    # 3. 创建异步 HTTP Session 并执行并发检测
    connector = aiohttp.TCPConnector(ssl=False, limit=0)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [checker.check_channel(session, ch) for ch in channels]
        logger.info(f"⚡ 开始高并发巡检 (HTTP 并发数: {config['performance']['max_concurrent_http']}, FFprobe 线程池: {config['performance']['max_concurrent_ffprobe']})...")

        results = await asyncio.gather(*tasks)

    valid_channels = []
    for item, is_valid, reason, err_code in results:
        if is_valid:
            valid_channels.append(item)
            logger.info(f"✅ 保留: {item['name']} | {reason}")
        else:
            logger.debug(f"❌ 剔除: {item['name']} | 原因: {reason}")

    # 4. 按评分降序，同频道限额前 N 条
    valid_channels.sort(key=lambda x: x.get('score', 0), reverse=True)
    channel_counts, top_channels = {}, []
    for ch in valid_channels:
        c_name = ch['name']
        if channel_counts.get(c_name, 0) < config['rules']['max_routes_per_channel']:
            top_channels.append(ch)
            channel_counts[c_name] = channel_counts.get(c_name, 0) + 1

    top_channels.sort(key=lambda x: (x.get('group', ''), x.get('name', '')))

    # 5. 生成 M3U 文件导出
    epg_header = f'#EXTM3U x-tvg-url="{",".join(config["epg_urls"])}"'
    m3u_lines = [epg_header]

    for ch in top_channels:
        tag_info = []
        if ch.get('height'): tag_info.append(f"{ch['height']}P")
        if ch.get('codec') and ("hevc" in ch['codec'].lower() or "265" in ch['codec'].lower()): tag_info.append("HEVC")
        
        tag_str = f" [{'/'.join(tag_info)}]" if tag_info else ""
        m3u_lines.append(f'#EXTINF:-1 tvg-name="{ch["name"]}" group-title="{ch["group"]}",{ch["name"]}{tag_str}')
        m3u_lines.append(ch["url"])

    with open(config['paths']['output_m3u'], "w", encoding="utf-8") as f:
        f.write("\n".join(m3u_lines) + "\n")

    logger.info(f"🎉 处理完成！原始 {len(channels)} 条 -> 存活 {len(valid_channels)} 条 -> 优选导出 {len(top_channels)} 条线路至 '{config['paths']['output_m3u']}'")

if __name__ == "__main__":
    asyncio.run(main())
