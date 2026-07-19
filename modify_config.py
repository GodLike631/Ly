# -*- coding: utf-8 -*-
"""
蝴蝶影视 缝合矩阵自动编译流 (现代升级版)
"""
import re
import sys
import json
import random
import string
import logging
import copy
import datetime
import urllib.request
import urllib.parse
from pathlib import Path

# 引入独立配置文件
import config

# ====================================================================
# 🎛️ 【初始化统一日志输出环境】
# ====================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[logging.StreamHandler(sys.stdout)]
)


# ====================================================================
# 📡 【统一网络请求处理函数】
# ====================================================================
def send_telegram_request(token, chat_id, text):
    """统一 Telegram Markdown 消息发送函数"""
    if not token or not chat_id:
        logging.warning("⚠️ 缺失 TG_TOKEN 或 TG_CHAT_ID，跳过发送 TG 通知。")
        return False
        
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "parse_mode": "Markdown",
        "text": text
    }
    
    try:
        data = urllib.parse.urlencode(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, method="POST")
        with urllib.request.urlopen(req, timeout=15) as response:
            if response.status == 200:
                logging.info("🚀 [网络请求] Telegram 蝴蝶消息直发成功！")
                return True
    except Exception as e:
        logging.error(f"❌ [网络请求] Telegram 发送失败: {e}")
        if hasattr(e, 'read'):
            try:
                error_detail = e.read().decode('utf-8')
                logging.error(f"🚨 [网络请求] TG 服务器返回的真实死因: {error_detail}")
            except Exception:
                pass
    return False


# ====================================================================
# 🛡️ 【智能容灾本地 JSON 安全加载模块】
# ====================================================================
def load_json_safe(file_path: Path) -> dict:
    """具备智能容灾和老本备份的正统 JSON 加载器"""
    backup_path = file_path.parent / f"{file_path.stem}_backup{file_path.suffix}"
    current_data = None
    is_current_valid = False

    if file_path.exists():
        try:
            current_data = json.loads(file_path.read_text(encoding='utf-8'))
            if isinstance(current_data, dict) and ("sites" in current_data or "lives" in current_data or "parses" in current_data):
                is_current_valid = True
            else:
                logging.warning(f"⚠️ 警告：{file_path.name} JSON 结构不符合底包规范，判定为坏源！")
        except Exception:
            logging.warning(f"⚠️ 警告：{file_path.name} 发生损坏或为空，无法正常进行 JSON 解析！")

    if is_current_valid:
        try:
            backup_path.write_text(json.dumps(current_data, ensure_ascii=False, indent=4), encoding='utf-8')
            logging.info(f"✅ 成功：{file_path.name} 核心校验通过，已成功备份至本地。")
        except Exception as backup_err:
            logging.error(f"🚨 备份同步到本地写入失败: {backup_err}")
        return current_data
    else:
        logging.error(f"🚨 触发容灾机制：上游数据源 {file_path.name} 已失效！开启安全降级...")
        if backup_path.exists():
            try:
                backup_data = json.loads(backup_path.read_text(encoding='utf-8'))
                logging.info(f"🥇 容灾成功！已成功加载上一次同步的历史底包数据: {backup_path.name}")
                file_path.write_text(json.dumps(backup_data, ensure_ascii=False, indent=4), encoding='utf-8')
                return backup_data
            except Exception:
                logging.critical(f"❌ 严重错误：本地历史老本 {backup_path.name} 也意外损坏！")
        else:
            logging.critical(f"❌ 严重错误：未能在本地库中检索到历史备份文件 {backup_path.name}！")
        return {}


# ====================================================================
# ⏰ 【每月 1 号自动大洗牌与密锁控制模块】
# ====================================================================
def manage_monthly_token():
    """管理每月密码生存周期控制"""
    today = datetime.datetime.now()
    current_month = str(today.month)
    is_reset_day = (today.day == 1)

    saved_month, saved_code = "", ""
    is_new_token_generated = False

    if config.LOCK_FILE_PATH.exists():
        content = config.LOCK_FILE_PATH.read_text(encoding='utf-8').strip()
        if "-" in content:
            saved_month, saved_code = content.split("-", 1)
        else:
            saved_code = content

    if is_reset_day and saved_month != current_month:
        current_token = ''.join(random.choices(string.ascii_lowercase + string.digits, k=3))
        config.LOCK_FILE_PATH.write_text(f"{current_month}-{current_token}", encoding='utf-8')
        logging.info(f"⏰ 【每月1号全新硬核洗牌】已生成本月新密锁: {current_token}")
        is_new_token_generated = True
    elif is_reset_day and saved_month == current_month:
        current_token = saved_code
    else:
        if not saved_code or len(saved_code) != 3 or "-" not in (config.LOCK_FILE_PATH.read_text(encoding='utf-8') if config.LOCK_FILE_PATH.exists() else ""):
            current_token = ''.join(random.choices(string.ascii_lowercase + string.digits, k=3))
            config.LOCK_FILE_PATH.write_text(f"{current_month}-{current_token}", encoding='utf-8')
        else:
            current_token = saved_code

    if current_token in ["全量版", "纯净版"]:
        full_output_filename = f"{config.BASE_OUTPUT_FULL}.json"
        clean_output_filename = f"{config.BASE_OUTPUT_CLEAN}.json"
    else:
        full_output_filename = f"{config.BASE_OUTPUT_FULL}{current_token}.json"
        clean_output_filename = f"{config.BASE_OUTPUT_CLEAN}{current_token}.json"

    return current_token, full_output_filename, clean_output_filename, is_new_token_generated


# ====================================================================
# 🛡️ 【过期接口金蝉脱壳爆破模块】
# ====================================================================
def execute_trap_boom(full_output_filename, clean_output_filename):
    """金蝉脱壳：全自动过期大轰炸提示"""
    if not config.DATA_DIR.exists():
        config.DATA_DIR.mkdir(parents=True, exist_ok=True)
        
    old_configs = list(config.DATA_DIR.glob(f'{config.BASE_OUTPUT_FULL}*.json')) + \
                  list(config.DATA_DIR.glob(f'{config.BASE_OUTPUT_CLEAN}*.json')) + \
                  list(config.DATA_DIR.glob('蝴蝶影视*.json')) + \
                  list(config.DATA_DIR.glob('老杨TV*.json'))

    for old_file in old_configs:
        if old_file.name != full_output_filename and old_file.name != clean_output_filename:
            try:
                trap_json = {
                    "spider": "", 
                    "notice": config.TRAP_NOTICE_TEXT,
                    "warningText": config.TRAP_WARNING_TEXT,
                    "sites": [
                        {"key": "蝴蝶纯文字提示", "name": config.TRAP_SITE_NAME_1, "type": 3, "api": "csp_JuDou", "searchable": 0, "quickSearch": 0, "filterable": 0},
                        {"key": "蝴蝶纯文字提示2", "name": config.TRAP_SITE_NAME_2, "type": 3, "api": "csp_JuDou", "searchable": 0, "quickSearch": 0, "filterable": 0}
                    ],
                    "lives": [
                        {"group": config.TRAP_LIVE_GROUP, "channels": [{"name": config.TRAP_LIVE_CHANNEL, "urls": ["http://127.0.0.1"]}]}
                    ]
                }
                old_file.write_text(json.dumps(trap_json, ensure_ascii=False, indent=4), encoding='utf-8')
            except Exception:
                pass

    for garbage in config.DATA_DIR.glob('config_*.json'):
        try:
            garbage.unlink()
        except Exception:
            pass


# ====================================================================
# ⚙️ 【核心数据深度清洗与重映射重载引擎】
# ====================================================================
def process_and_merge_data():
    """解析、过滤、清洗底层 JSON 链条"""
    json_cnb = load_json_safe(config.CNB_PATH)
    json_haitun = load_json_safe(config.HAITUN_PATH)
    json_lz = load_json_safe(config.LZ_PATH)

    haitun_sites = json_haitun.get("sites", [])
    haitun_lives = json_haitun.get("lives", [])
    lz_sites = json_lz.get("sites", [])

    lz_nsfw_list = []
    for item in lz_sites:
        if "🔞" in item.get("name", ""):
            raw_name = item["name"].replace("🔞", "").strip()
            item["name"] = f"{raw_name}｜🔞"
            if "api" in item and isinstance(item["api"], str):
                if item["api"].startswith("./py/"):
                    item["api"] = item["api"].replace("./py/", "https://gh-proxy.com/https://raw.githubusercontent.com/ediart/tvbox/refs/heads/main/lz/py/")
                elif item["api"].startswith("./js/"):
                    item["api"] = item["api"].replace("./js/", "https://gh-proxy.com/https://raw.githubusercontent.com/ediart/tvbox/refs/heads/main/lz/js/")
                elif item["api"].startswith("./"):
                    item["api"] = item["api"].replace("./", "https://gh-proxy.com/https://raw.githubusercontent.com/ediart/tvbox/refs/heads/main/lz/")
            lz_nsfw_list.append(item)

    for item in haitun_sites:
        if "name" in item:
            item["name"] = f"{item['name']}{config.MY_TG_SUFFIX}"
    for item in haitun_lives:
        if "name" in item:
            item["name"] = f"{item['name']}{config.MY_TG_SUFFIX}"

    cnb_sites = json_cnb.get("sites", [])
    cnb_lives = json_cnb.get("lives", [])

    combined_parses = json_haitun.get("parses", []) + json_lz.get("parses", []) + json_cnb.get("parses", [])

    custom_keys = {site.get("key") for site in config.MY_CUSTOM_SITES if site.get("key")}
    upstream_sites = haitun_sites + lz_nsfw_list + cnb_sites
    clean_upstream_sites = [site for site in upstream_sites if site.get("key") not in custom_keys]

    if config.BLOCK_KEYWORDS:
        clean_upstream_sites = [
            site for site in clean_upstream_sites 
            if not any(kw.lower() in site.get("name", "").lower() for kw in config.BLOCK_KEYWORDS if kw)
        ]

    json_cnb["sites"] = clean_upstream_sites + config.MY_CUSTOM_SITES

    custom_live_names = {live.get("name") for live in config.MY_CUSTOM_LIVES if live.get("name")}
    base_lives = haitun_lives + cnb_lives

    clean_base_lives = [
        live for live in base_lives 
        if live.get("name") not in custom_live_names 
        and not any(kw in live.get("name", "") for kw in config.BLOCK_MALICIOUS_KEYWORDS)
    ]

    if config.BLOCK_KEYWORDS:
        clean_base_lives = [
            live for live in clean_base_lives 
            if not any(kw.lower() in live.get("name", "").lower() for kw in config.BLOCK_KEYWORDS if kw)
        ]

    inserted_count = 0 
    for custom_live in config.MY_CUSTOM_LIVES:
        live_name = custom_live.get("name", "")
        if config.BLOCK_KEYWORDS and any(kw.lower() in live_name.lower() for kw in config.BLOCK_KEYWORDS if kw):
            continue
            
        if "🔞" in live_name:
            clean_base_lives.append(custom_live)
        else:
            insert_idx = min(5 + inserted_count, len(clean_base_lives))
            clean_base_lives.insert(insert_idx, custom_live)
            inserted_count += 1

    json_cnb["lives"] = clean_base_lives
    return json_cnb, combined_parses


# ====================================================================
# 🧮 文本清洗与对象二次编译模块
# ====================================================================
def text_level_wash_and_compile(json_cnb, combined_parses):
    """进行物理字符串级替换和硬编码纠偏，编译最终字典对象"""
    final_json_text = json.dumps(json_cnb, ensure_ascii=False, indent=4)
    final_json_text = final_json_text.replace(
        '"key": "hajim-腾讯备"', '"spider": "./tvbox.jar",\n            "key": "hajim-腾讯备"'
    ).replace(
        '"key": "茫茫"', '"spider": "./tvbox.jar",\n            "key": "茫茫"'
    )

    for dirty_word in config.UPSTREAM_DIRTY_WORDS:
        final_json_text = final_json_text.replace(dirty_word, '')

    for src, dst in config.PATH_REPLACEMENTS.items():
        final_json_text = final_json_text.replace(src, dst)

    ordered_obj = json.loads(final_json_text)
    if "warningText" in ordered_obj: 
        ordered_obj.pop("warningText")
        
    unique_parses = []
    seen_names = set()
    for p in combined_parses:
        name = p.get("name", "")
        if name and name not in seen_names:
            unique_parses.append(p)
            seen_names.add(name)
    ordered_obj["parses"] = unique_parses

    if "doh" in ordered_obj and isinstance(ordered_obj["doh"], list):
        for doh_item in ordered_obj["doh"]:
            if doh_item.get("url", "").endswith("/dns-quer"): 
                doh_item["url"] = doh_item["url"] + "y"
        if not any(d.get("name") == config.ALI_DOH_CONFIG["name"] for d in ordered_obj["doh"]): 
            ordered_obj["doh"].insert(0, config.ALI_DOH_CONFIG)

    if "rules" in ordered_obj and isinstance(ordered_obj["rules"], list):
        current_rules = ordered_obj.get("rules", [])
        ad_hosts = list(config.AD_HOSTS_LIST)
        for rule in current_rules:
            if isinstance(rule, dict) and "hosts" in rule:
                for h in rule["hosts"]:
                    if h not in ad_hosts: 
                        ad_hosts.append(h)
        js_injection_rule = {"name": "蝴蝶影视·云端高级去广告JS注入", "hosts": ad_hosts, "script": config.CUSTOM_AD_BLOCK_JS}
        ordered_obj["rules"] = [js_injection_rule] + [r for r in current_rules if r.get("name") != "蝴蝶影视·云端高级去广告JS注入"]

    if "lives" in ordered_obj and isinstance(ordered_obj["lives"], list):
        clean_lives = []
        for live in ordered_obj["lives"]:
            if live and isinstance(live, dict):
                if not live.get("ua") or live.get("ua") == "okhttp": 
                    live["ua"] = "okhttp/5.3.2"
                
                if "name" in live:
                    l_raw_name = live["name"]
                    for src_word, dst_word in config.MY_NAME_REPLACEMENTS.items():
                        l_raw_name = l_raw_name.replace(src_word, dst_word)
                    live["name"] = l_raw_name
                clean_lives.append(live)
        ordered_obj["lives"] = clean_lives

    block_1_rebo, block_2_yingshi, block_3_duanju, block_4_dongman, block_5_cili, block_6_tiyu, block_7_shaoer, block_8_yinyue, block_9_fuli = [], [], [], [], [], [], [], [], []
    tg_tail_count = 0

    for site in ordered_obj.get("sites", []):
        if "name" not in site: 
            continue
        raw_name = site["name"]
        
        if any(kw in raw_name for kw in config.BLOCK_MALICIOUS_KEYWORDS):
            continue
            
        s_key, s_genre, s_api = site.get("key", ""), site.get("genre", ""), site.get("api", "")
        for char in ['丨', '┃', ' ']: 
            raw_name = raw_name.strip(char)
        raw_name = re.sub(r'\s+', ' ', raw_name)
        if config.MY_TG_SUFFIX in raw_name:
            tg_tail_count += 1
            if tg_tail_count > 5: 
                raw_name = raw_name.replace(config.MY_TG_SUFFIX, "").strip()
        
        if not raw_name.startswith(config.LOGO_PREFIX):
            raw_name = f"{config.LOGO_PREFIX} {raw_name}"
            
        for src_word, dst_word in config.MY_NAME_REPLACEMENTS.items():
            raw_name = raw_name.replace(src_word, dst_word)
            
        if "ext" in site and site["ext"] == {}: 
            site["ext"] = ""
        if isinstance(s_api, str) and "PanWebShare" in s_api:
            site["api"] = "csp_PanWebShare"
            if "jar" in site: 
                site.pop("jar")

        is_guazi = "瓜子" in raw_name or "GZ" == s_key
        is_nsfw = False if is_guazi else ("🔞" in raw_name or "色播" in raw_name or "av" in s_key.lower() or "瓜" in raw_name or "爆料" in raw_name or "chat" in raw_name.lower() or "cam" in raw_name.lower() or "panda" in raw_name.lower() or "video" in raw_name.lower() or "md" in s_key.lower())
        
        if s_key == config.HOT_VIDEO_KEY:
            site["name"] = config.HOT_VIDEO_SITE_NAME
            site["category"] = "综合"
            block_1_rebo.append(site)
        elif "豆瓣" in raw_name and "首页" in raw_name:
            site["name"] = f"{config.LOGO_PREFIX} 豆瓣 • 首页"
            site["category"] = "综合"
            site["searchable"] = 0
            block_2_yingshi.append(site)
        elif is_nsfw:
            site["name"] = raw_name
            site["category"] = "福利"
            block_9_fuli.append(site)
        elif "短剧" in raw_name or "剧场" in raw_name:
            if "dj" in raw_name.lower() or "dj" in s_key.lower():
                site["name"] = raw_name
                site["category"] = "音乐"
                site["searchable"] = 0
                block_8_yinyue.append(site)
            else:
                site["name"] = raw_name
                site["category"] = "短剧"
                site["genre"] = "shortdrama"
                block_3_duanju.append(site)
        elif "动漫" in raw_name or "新番" in raw_name or "anime" in s_key.lower() or "a1" in raw_name.lower():
            site["name"] = raw_name
            site["category"] = "动漫"
            block_4_dongman.append(site)
        elif "磁力" in raw_name or "索" in raw_name or "盘" in raw_name or "云盘" in raw_name or "4k" in raw_name.lower():
            site["name"] = raw_name
            site["category"] = "网盘/磁力"
            if "PanWebShare" in site.get("api", ""): 
                site["changeable"] = 1
            block_5_cili.append(site)
        elif "体育" in raw_name or "球" in raw_name or "直播" in raw_name:
            site["name"] = raw_name
            site["category"] = "体育/直播"
            block_6_tiyu.append(site)
        elif "少儿" in raw_name or "课堂" in raw_name or "教学" in raw_name or "教育" in raw_name:
            site["name"] = raw_name
            site["category"] = "少儿"
            site["searchable"] = 0
            block_7_shaoer.append(site)
        elif "音乐" in raw_name or "网易云" in raw_name or "听书" in raw_name or "唱会" in raw_name or "fm" in raw_name.lower() or "相声" in raw_name or "小品" in raw_name or "戏曲" in raw_name or "推送" in raw_name or "配置" in raw_name or "版本" in raw_name or "本地" in raw_name or "dj" in raw_name.lower() or "dj" in s_key.lower():
            site["name"] = raw_name
            site["category"] = "音乐" if ("音乐" in raw_name or "网易云" in raw_name or "听书" in raw_name or "fm" in raw_name.lower() or "dj" in raw_name.lower() or "dj" in s_key.lower()) else "综合"
            site["searchable"] = 0
            block_8_yinyue.append(site)
        else:
            site["name"] = raw_name
            site["category"] = "综合"
            block_2_yingshi.append(site)

        if site.get("category") not in ["少儿", "音乐"] and "searchable" not in site: 
            site["searchable"] = 1

    for site in block_2_yingshi:
        if site.get("key") == "AQY": 
            site["name"] = f"{config.LOGO_PREFIX} 爱奇艺 {config.MY_TG_SUFFIX}"

    ordered_obj["sites"] = (block_1_rebo + block_2_yingshi + block_3_duanju + block_4_dongman + block_6_tiyu + block_7_shaoer + block_8_yinyue + block_5_cili + block_9_fuli)
    return ordered_obj


# ====================================================================
# 🔀 【双版本矩阵分流构建与下发调度模块】
# ====================================================================
def build_and_dispatch_matrix(ordered_obj, current_token, full_output_filename, clean_output_filename, is_new_token_generated):
    """处理双版本精细分流，比对差异，构建并下发最终订阅链路"""
    import os
    
    full_version_obj = copy.deepcopy(ordered_obj)
    full_version_obj["notice"] = config.WELCOME_NOTICE_FULL + config.THANKS_WARNING
    full_version_obj["wallpaper"] = config.WALLPAPER_FULL
    
    full_final_out = {"notice": full_version_obj.pop("notice")}
    full_final_out.update(full_version_obj)

    clean_version_obj = copy.deepcopy(ordered_obj)
    clean_version_obj["notice"] = config.WELCOME_NOTICE_CLEAN + config.THANKS_WARNING
    clean_version_obj["wallpaper"] = config.WALLPAPER_CLEAN
    
    clean_version_obj["sites"] = [
        s for s in clean_version_obj.get("sites", [])
        if not any(kw in s.get("name", "") or kw in s.get("category", "") or kw in s.get("key", "").lower() for kw in config.NSFW_KEYWORDS)
    ]
    clean_version_obj["lives"] = [
        l for l in clean_version_obj.get("lives", [])
        if not any(kw in l.get("name", "") for kw in config.NSFW_KEYWORDS)
    ]
    
    clean_final_out = {"notice": clean_version_obj.pop("notice")}
    clean_final_out.update(clean_version_obj)

    full_output_path = config.DATA_DIR / full_output_filename
    clean_output_path = config.DATA_DIR / clean_output_filename

    tg_token = os.getenv("TG_TOKEN")
    tg_chat_id = os.getenv("TG_CHAT_ID")
    repo_info = os.getenv("GITHUB_REPOSITORY", "GodLike631/Ly_18")
    branch_info = os.getenv("GITHUB_REF_NAME", "main")
    
    full_raw_url = f"https://raw.githubusercontent.com/{repo_info}/refs/heads/{branch_info}/datas/{full_output_filename}"
    clean_raw_url = f"https://raw.githubusercontent.com/{repo_info}/refs/heads/{branch_info}/datas/{clean_output_filename}"
    
    full_sub_url = f"{config.GITHUB_PROXY}{full_raw_url}" if config.GITHUB_PROXY else full_raw_url
    clean_sub_url = f"{config.GITHUB_PROXY}{clean_raw_url}" if config.GITHUB_PROXY else clean_raw_url
    
    current_time = (datetime.datetime.utcnow() + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M")
    is_password_changed = False
    old_file_name = ""
    
    if config.TRACKER_PATH.exists():
        old_file_name = config.TRACKER_PATH.read_text(encoding='utf-8').strip()
            
    if old_file_name != full_output_filename and old_file_name != "":
        is_password_changed = True

    # 🟢 情况一：触发密码变更 ➡️ 发送专属大通知
    if is_password_changed or is_new_token_generated:
        pwd_msg = config.TG_PWD_MSG_TEMPLATE.format(
            current_time=current_time,
            current_token=current_token,
            full_sub_url=full_sub_url,
            clean_sub_url=clean_sub_url
        )
        send_telegram_request(tg_token, tg_chat_id, pwd_msg)
                
    # 🟢 情况二：没有换密码 ➡️ 对比 Diff 变动明细
    else:
        try:
            old_sites_names, old_lives_names = set(), set()
            old_file_path = config.DATA_DIR / old_file_name
            if old_file_path.exists():
                old_data = json.loads(old_file_path.read_text(encoding='utf-8'))
                old_sites_names = {s.get("name", "").strip() for s in old_data.get("sites", []) if s.get("name")}
                old_lives_names = {l.get("name", "").strip() for l in old_data.get("lives", []) if l.get("name")}

            new_sites_names = {s.get("name", "").strip() for s in full_final_out.get("sites", []) if s.get("name")}
            new_lives_names = {l.get("name", "").strip() for l in full_final_out.get("lives", []) if l.get("name")}

            added_sites = sorted(list(new_sites_names - old_sites_names))
            deleted_sites = sorted(list(old_sites_names - new_sites_names))
            added_lives = sorted(list(new_lives_names - old_lives_names))
            deleted_lives = sorted(list(old_lives_names - new_lives_names))

            if added_sites or deleted_sites or added_lives or deleted_lives:
                msg_lines = ["📝 *【 变动明细预览 】*", "📊 *━━━━━━━━━━━━━━*"]
                
                if added_sites or deleted_sites:
                    msg_lines.append("📺 *【点播线路变动】*")
                    if added_sites:
                        msg_lines.append("➕ *新增点播*：")
                        msg_lines.extend([f"  🟢 {name}" for name in added_sites[:config.TG_MAX_DISPLAY]])
                        if len(added_sites) > config.TG_MAX_DISPLAY: 
                            msg_lines.append(f"  ... 等更多共 {len(added_sites)} 个新点播源")
                    if deleted_sites:
                        if added_sites: msg_lines.append("")
                        msg_lines.append("➖ *剔除点播*：")
                        msg_lines.extend([f"  🔴 {name}" for name in deleted_sites[:config.TG_MAX_DISPLAY]])
                        if len(deleted_sites) > config.TG_MAX_DISPLAY: 
                            msg_lines.append(f"  ... 等更多共 {len(deleted_sites)} 个失效点播源")
                    msg_lines.append("📊 *━━━━━━━━━━━━━━*")
                    
                if added_lives or deleted_lives:
                    if len(msg_lines) > 2: 
                        msg_lines.append("")
                    msg_lines.append("📡 *【直播源站变动】*")
                    if added_lives:
                        msg_lines.append("➕ *新增直播*：")
                        msg_lines.extend([f"  🟢 {name}" for name in added_lives[:config.TG_MAX_DISPLAY]])
                        if len(added_lives) > config.TG_MAX_DISPLAY: 
                            msg_lines.append(f"  ... 等更多共 {len(added_lives)} 个新直播源")
                    if deleted_lives:
                        if added_lives: msg_lines.append("")
                        msg_lines.append("➖ *剔除直播*：")
                        msg_lines.extend([f"  🔴 {name}" for name in deleted_lives[:config.TG_MAX_DISPLAY]])
                        if len(deleted_lives) > config.TG_MAX_DISPLAY: 
                            msg_lines.append(f"  ... 等更多共 {len(deleted_lives)} 个失效直播源")
                    msg_lines.append("📊 *━━━━━━━━━━━━━━*")
                
                detail_msg = "\n".join(msg_lines)
                
                full_msg = config.TG_UPDATE_MSG_TEMPLATE.format(
                    current_time=current_time,
                    detail_msg=detail_msg,
                    full_sub_url=full_sub_url,
                    clean_sub_url=clean_sub_url
                )

                send_telegram_request(tg_token, tg_chat_id, full_msg)
            else:
                logging.info("⏭️ 没有任何名录实际变动，智能拦截名录变更通知。")
        except Exception as diff_err:
            logging.error(f"⚠️ 对比变动异常: {diff_err}")

    # 数据落盘与追踪器写回
    full_output_path.write_text(json.dumps(full_final_out, ensure_ascii=False, indent=4), encoding='utf-8')
    clean_output_path.write_text(json.dumps(clean_final_out, ensure_ascii=False, indent=4), encoding='utf-8')
    config.TRACKER_PATH.write_text(full_output_filename, encoding='utf-8')
    logging.info("🎉 编译写出完成 -> 蝴蝶影视全量与纯净双通道实体构建完毕")


# ====================================================================
# 🚀 【程序统一主入口】
# ====================================================================
def main():
    try:
        logging.info("🚀 蝴蝶影视 自动模块化编译架构管道启动...")
        
        # 1. 管理动态密码锁
        current_token, full_out_name, clean_out_name, is_new_token = manage_monthly_token()
        
        # 2. 爆破旧接口老资产
        execute_trap_boom(full_out_name, clean_out_name)
        
        # 3. 加载与过滤底层核心 JSON 数据
        json_cnb, combined_parses = process_and_merge_data()
        
        # 4. 文本清洗与二次逻辑编译
        ordered_obj = text_level_wash_and_compile(json_cnb, combined_parses)
        
        # 5. 双通道打包分流下发
        build_and_dispatch_matrix(ordered_obj, current_token, full_out_name, clean_out_name, is_new_token)
        
        # 保底控制开关复核
        today = datetime.datetime.now()
        if not config.LOCK_FILE_PATH.exists() or "-" not in config.LOCK_FILE_PATH.read_text(encoding='utf-8'):
            config.LOCK_FILE_PATH.write_text(f"{today.month}-{current_token}", encoding='utf-8')
            
        logging.info("🎉 蝴蝶影视矩阵编译顺利完成，完美收官！")
        
    except Exception as e:
        logging.critical(f"❌ 运行失败，核心总线崩溃: {e}", exc_info=True)


if __name__ == "__main__":
    main()
