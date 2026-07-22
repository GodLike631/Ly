# -*- coding: utf-8 -*-
"""
M3U 直播源存量巡检与自动清洗脚本 (GitHub Actions 专属)
"""
import os
import re
import json
import requests
import subprocess
from urllib.parse import urlparse, urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed

# 路径自动定位：指向 datas 文件夹下的 custom_lives.m3u
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TARGET_M3U = os.path.join(BASE_DIR, "datas", "custom_lives.m3u")

# 配置项
MAX_WORKERS = 40          # 并发检测线程数 (推荐 10-15)
TIMEOUT = 3               # HTTP 超时时间 (秒)
ENABLE_FFMPEG = True      # 是否开启 FFmpeg 深层视频流探测

# 广告/劫持/失效重定向黑名单
AD_KEYWORDS = [
    "guanggao", "notice", "redirect", "error.m3u8", "ad.m3u8", 
    "welcome", "invalid", "vip_ad", "gg.m3u8", "test.m3u8", "解析失败"
]

def get_tv_headers(url: str) -> dict:
    """构建电视盒子专用 Headers (模拟 Android 11 + TVBox / ExoPlayer)"""
    parsed = urlparse(url)
    origin_host = f"{parsed.scheme}://{parsed.netloc}"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 11; SmartTV Build/RQ3A.210905.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.105 Mobile Safari/537.36 ExoPlayer/2.18.1',
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8',
        'Connection': 'keep-alive',
        'Referer': origin_host + '/',
        'Origin': origin_host
    }

    if "migu" in url.lower():
        headers['User-Agent'] = 'MiguVideo/3.9.0 (Android; SmartTV)'
        headers['Referer'] = 'https://www.miguvideo.com/'

    return headers

def check_ffprobe_valid(url: str, headers: dict) -> bool:
    """使用 ffprobe 检测视频流编码及帧率"""
    user_agent = headers.get('User-Agent', '')
    cmd = [
        'ffprobe', '-v', 'quiet', '-print_format', 'json',
        '-user_agent', user_agent,
        '-show_streams', '-timeout', str(TIMEOUT * 1000000), url
    ]
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=TIMEOUT + 1)
        data = json.loads(res.stdout)
        for stream in data.get('streams', []):
            if stream.get('codec_type') == 'video':
                fps_eval = stream.get('r_frame_rate', '0/1')
                if '/' in fps_eval:
                    num, den = map(float, fps_eval.split('/'))
                    fps = num / den if den > 0 else 0
                    if fps >= 10:
                        return True
    except Exception:
        pass
    return False

def extract_first_ts_url(m3u8_url: str, m3u8_text: str, headers: dict) -> str:
    """智能解析 M3U8 文本，提取第一个真正的 TS 切片 URL（含二级 M3U8 嵌套处理）"""
    lines = [line.strip() for line in m3u8_text.splitlines() if line.strip() and not line.startswith("#")]
    if not lines:
        return None

    first_line = lines[0]
    full_url = urljoin(m3u8_url, first_line)

    if ".m3u8" in first_line.lower() or "m3u8" in full_url.lower():
        try:
            sub_res = requests.get(full_url, headers=headers, timeout=TIMEOUT, stream=True)
            if sub_res.status_code < 400:
                sub_text = sub_res.raw.read(4096).decode('utf-8', errors='ignore')
                sub_lines = [l.strip() for l in sub_text.splitlines() if l.strip() and not l.startswith("#")]
                if sub_lines:
                    return urljoin(full_url, sub_lines[0])
        except Exception:
            pass

    return full_url

def check_channel_valid(item: dict) -> tuple:
    """全套高阶融合校验 (智能 TS 解析 + 电视UA + 3重防广告)"""
    url = item["url"]
    headers = get_tv_headers(url)
    
    if url.startswith("rtp://") or url.startswith("udp://"):
        return item, True, "PASS"

    hit_kw = next((kw for kw in AD_KEYWORDS if kw in url.lower()), None)
    if hit_kw:
        return item, False, f"URL命中广告黑名单[{hit_kw}]"

    try:
        res = requests.get(url, headers=headers, timeout=TIMEOUT, stream=True, allow_redirects=True)
        if res.status_code >= 400:
            return item, False, f"HTTP响应错误({res.status_code})"

        content_bytes = res.raw.read(4096)
        content_head = content_bytes.decode('utf-8', errors='ignore').lower()

        hit_txt_kw = next((kw for kw in AD_KEYWORDS if kw in content_head), None)
        if hit_txt_kw:
            return item, False, f"内容包含广告关键词[{hit_txt_kw}]"

        durations = re.findall(r'#extinf:([\d\.]+)', content_head)
        if durations:
            total_time = sum(float(d) for d in durations)
            if total_time < 6 and len(durations) <= 2:
                return item, False, f"疑似短时广告片(时长{total_time:.1f}s,切片数{len(durations)})"

        first_ts_url = extract_first_ts_url(url, content_head, headers)
        if first_ts_url and not first_ts_url.endswith(".m3u8"):
            try:
                ts_res = requests.get(first_ts_url, headers=headers, timeout=TIMEOUT, stream=True)
                if ts_res.status_code < 400:
                    chunk = next(ts_res.iter_content(chunk_size=65536), None)
                    if not chunk or len(chunk) < 512:
                        return item, False, "TS切片数据包空/过小"
                else:
                    if not ENABLE_FFMPEG:
                        return item, False, f"TS切片获取失败({ts_res.status_code})"
            except Exception:
                if not ENABLE_FFMPEG:
                    return item, False, "TS切片连接超时/死链"

        if ENABLE_FFMPEG:
            if not check_ffprobe_valid(url, headers):
                return item, False, "FFmpeg未识别到有效视频流/无画面"

        return item, True, "PASS"
    except requests.exceptions.Timeout:
        return item, False, f"HTTP连接超时({TIMEOUT}s)"
    except Exception:
        return item, False, "网络请求失败"

def parse_m3u_file(file_path: str) -> list:
    """从已有的 datas/custom_lives.m3u 中解析频道名称、分组及 URL"""
    if not os.path.exists(file_path):
        print(f"❌ 找不到需要巡检的文件: {file_path}")
        return []

    channels = []
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
                    name = name_match.group(1).strip() if name_match else "未命名频道"
                    
                    group_match = re.search(r'group-title="([^"]+)"', current_extinf)
                    group = group_match.group(1) if group_match else "其他"

                    channels.append({"name": name, "url": line, "group": group})
                    current_extinf = None

    return channels

def main():
    print(f"🔍 开始对存量文件 '{TARGET_M3U}' 进行自动化巡检...")
    channels = parse_m3u_file(TARGET_M3U)
    total_raw = len(channels)
    
    if total_raw == 0:
        print("❌ 未发现任何有效存量线路，脚本退出。")
        return

    print(f"📊 载入成功！共需要复检 {total_raw} 条存量线路...\n")

    valid_channels = []
    print(f"⚡ 已开启全套连通性巡检 (线程数: {MAX_WORKERS}, 超时: {TIMEOUT}s)...")
    print("=" * 80)
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(check_channel_valid, ch) for ch in channels]
        completed = 0
        for future in as_completed(futures):
            item, is_valid, reason = future.result()
            completed += 1
            if is_valid:
                valid_channels.append(item)
                print(f"[{completed}/{total_raw}] ✅ 存活: {item['name']} ({len(valid_channels)}/{total_raw})")
            else:
                print(f"[{completed}/{total_raw}] ❌ 清洗: {item['name']} | 原因: {reason} ({len(valid_channels)}/{total_raw})")
                
    print("=" * 80)
    print("✅ 连通性检测完毕！\n")

    # 确保存储目录存在
    os.makedirs(os.path.dirname(TARGET_M3U), exist_ok=True)

    # 重构写入 datas/custom_lives.m3u
    m3u_lines = ['#EXTM3U x-tvg-url="https://material.yang-1989.xyz/epg.xml.gz"']
    for ch in valid_channels:
        m3u_lines.append(f'#EXTINF:-1 tvg-name="{ch["name"]}" group-title="{ch["group"]}",{ch["name"]}')
        m3u_lines.append(ch["url"])

    with open(TARGET_M3U, "w", encoding="utf-8") as f:
        f.write("\n".join(m3u_lines) + "\n")

    print(f"🎉 处理完成！原本 {total_raw} 条 -> 剩余有效 {len(valid_channels)} 条，已保存至 '{TARGET_M3U}'")

if __name__ == "__main__":
    main()
