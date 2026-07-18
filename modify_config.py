import os
import re
import random
import string
import glob
import datetime
import json
import urllib.request
import urllib.parse
import copy

cnb_path = 'datas/cnb.json'
haitun_path = 'datas/haitun.json'
lz_path = 'datas/lz.json'

# 控制开关和追踪器文件路径
lock_file_path = 'datas/控制开关.txt'
tracker_path = 'datas/最新接口文件名.txt'

# ====================================================================
# 🌐 【全局通道与资源配置区】
# ====================================================================
GITHUB_PROXY = "https://gh-proxy.org/"
# 抽离原本硬编码的电视端 Logo 图标路径，方便以后一键修改
DEFAULT_LOGO_URL = "https://img.naixiai.cn/2026/06/18/IMG_6638.jpeg"

# ====================================================================
# 🚫 【新增：自定义黑名单关键词过滤区】
# ====================================================================
BLOCK_KEYWORDS = ["羊壳", "弹幕", "不可用"]

# ====================================================================
# ✍️ 【通道一：老杨专属点播手工加线区】
# ====================================================================
MY_CUSTOM_SITES = [
    {
        "key": "山楂影视",
        "name": "山楂影视.py",  
        "type": 3,
        "api": "https://ghfast.top/https://raw.githubusercontent.com/GodLike631/test/refs/heads/main/datas/%E5%B1%B1%E6%A5%82%E5%BD%B1%E8%A7%86.py",
        "searchable": 1,
        "quickSearch": 1
    },
    {
        "key": "红果短剧",
        "name": "红果短剧.py",  
        "type": 3,
        "api": "https://ghfast.top/https://raw.githubusercontent.com/GodLike631/test/refs/heads/main/datas/%E7%BA%A2%E6%9E%9C%E7%9F%AD%E5%89%A7.py",
        "searchable": 1,
        "quickSearch": 1
    }
]

# ====================================================================
# 📺 【通道二：老杨专属直播手工加线区（从第 6 位开始正向依序后排）】
# ====================================================================
MY_CUSTOM_LIVES = [
    {
      "name": "锋云直播｜Tg：@huliys9",
      "type": 3,
      "url": "https://gh-proxy.org/https://raw.githubusercontent.com/807080747/zv/refs/heads/main/suale.txt",
      "ua": "okhttp/5.3.2",
      "timeout": 10,
      "playerType": 2
    },
    {
        "name": "最新电影｜Tg：@huliys9",
        "type": 0,
        "ua": "okhttp/5.3.2",
        "url": "https://ghfast.top/https://raw.githubusercontent.com/GodLike631/Ly_18/refs/heads/main/datas/%E6%9C%80%E6%96%B0%E7%94%B5%E5%BD%B1.m3u"
    },
    {
        "name": "Kimentanm",
        "type": 0,
        "url": "https://ghfast.top/https://raw.githubusercontent.com/Kimentanm/aptv/master/m3u/iptv.m3u",
        "playerType": 2
    },
    {
      "name": "综合直播",
      "type": 0,
      "playerType": 2,
      "url": "https://ghfast.top/https://raw.githubusercontent.com/develop202/migu_video/refs/heads/main/interface.txt",
      "ua": "bingcha/1.1 (mianfeifenxiang) "
    },
    {
        "name": "央卫TV｜Tg：@huliys9",
        "type": 0,
        "ua": "okhttp/5.3.2",
        "url": "http://47.120.41.246:8025/vip/jar/zb.php"
    },
    {
        "name": "超稳定流畅｜Tg：@huliys9",
        "type": 0,
        "ua": "okhttp/5.3.2",
        "url": "https://ghfast.top/https://raw.githubusercontent.com/GodLike631/test/refs/heads/main/datas/%E8%B6%85%E7%A8%B3%E5%AE%9A%E6%B5%81%E7%95%85.txt"
    },
    {
        "name": "国产直播🔞｜Tg：@huliys9",
        "type": 0,
        "ua": "okhttp/5.3.2",
        "url": "https://ghfast.top/https://raw.githubusercontent.com/Ameria22/TV/refs/heads/main/data/01%E5%9B%BD%E4%BA%A7%E7%9B%B4%E6%92%AD_20260417_024507.m3u"
    },
    {
        "name": "国产精品🔞｜Tg：@huliys9",
        "type": 0,
        "ua": "okhttp/5.3.2",
        "url": "https://ghfast.top/https://raw.githubusercontent.com/Ameria22/TV/refs/heads/main/data/01%E5%9B%BD%E4%BA%A7%E7%B2%BE%E5%93%81_20260417_024507.m3u"
    },
    {
        "name": "探花🔞｜Tg：@huliys9",
        "type": 0,
        "ua": "okhttp/5.3.2",
        "url": "https://raw.githubusercontent.com/Ameria22/TV/refs/heads/main/data/01%E6%8E%A2%E8%8A%B1%E7%BA%A6%E7%82%AE_20260417_024507.m3u"
    },
    {
        "name": "欧美🔞｜Tg：@huliys9",
        "type": 0,
        "ua": "okhttp/5.3.2",
        "url": "https://ghfast.top/https://raw.githubusercontent.com/Ameria22/TV/refs/heads/main/data/%E6%AC%A7%E7%BE%8E%E9%A2%91%E9%81%93.m3u"
    },
    {
        "name": "咪咕｜Tg：@huliys9",
        "type": 0,
        "ua": "okhttp/5.3.2",
        "url": "https://develop202.github.io/migu_video/interface.txt"
    },
    {
      "name": "Gather「IPTV」｜Tg：@huliys9",
      "type": 3,
      "url": "https://iptv.yang-1989.xyz/playlist.m3u",
      "epg":"https://material.yang-1989.xyz/epg.xml.gz",
      "ua": "okhttp/5.3.2",
      "timeout": 10,
      "playerType": 2
    },
    {
      "name": "Live「直播」｜Tg：@huliys9",
      "type": 3,
      "url": "https://live.yang-1989.eu.org/Live.m3u",
      "ua": "okhttp/5.3.2",
      "timeout": 10,
      "playerType": 2
    },
    {
      "name": "myTV「香港」｜Tg：@huliys9",
      "type": 3,
      "url": "https://iptv.yang-1989.xyz/myTV/playlist.m3u",
      "epg":"https://material.yang-1989.xyz/epg.xml.gz",
      "ua": "okhttp/5.3.2",
      "timeout": 10,
      "playerType": 2
    },
]

# ====================================================================
# ⏰ 【自动换锁与手动更改密码检测逻辑】
# ====================================================================
today = datetime.datetime.now()
current_month = str(today.month) 
is_reset_day = (today.day == 1)

saved_month = ""
saved_code = ""
is_new_token_generated = False

if os.path.exists(lock_file_path):
    with open(lock_file_path, 'r', encoding='utf-8') as f:
        content = f.read().strip()
        if "-" in content:
            saved_month, saved_code = content.split("-", 1)
        else:
            saved_code = content

if is_reset_day and saved_month != current_month:
    current_token = ''.join(random.choices(string.ascii_lowercase + string.digits, k=3))
    with open(lock_file_path, 'w', encoding='utf-8') as f:
        f.write(f"{current_month}-{current_token}")
    print(f"⏰ 【每月1号全新硬核洗牌】已生成本月新密锁: {current_token}")
    is_new_token_generated = True
elif is_reset_day and saved_month == current_month:
    current_token = saved_code
else:
    if not saved_code or len(saved_code) != 3 or "-" not in (content if os.path.exists(lock_file_path) else ""):
        current_token = ''.join(random.choices(string.ascii_lowercase + string.digits, k=3))
        with open(lock_file_path, 'w', encoding='utf-8') as f:
            f.write(f"{current_month}-{current_token}")
    else:
        current_token = saved_code

# 确定动态密码命名规则（双版本名字矩阵化）
if current_token in ["全量版", "纯净版"]:
    full_output_filename = "蝴蝶影视全量版.json"
    clean_output_filename = "蝴蝶影视纯净版.json"
else:
    full_output_filename = f"蝴蝶影视全量版{current_token}.json"
    clean_output_filename = f"蝴蝶影视纯净版{current_token}.json"

# ====================================================================
# 🛡️ 【金蝉脱壳：全自动过期大轰炸提示（支持全量版与纯净版双线扫描）】
# ====================================================================
old_configs = glob.glob('datas/蝴蝶影视全量版*.json') + glob.glob('datas/蝴蝶影视纯净版*.json') + glob.glob('datas/蝴蝶影视*.json') + glob.glob('datas/老杨TV*.json')
for old_file in old_configs:
    old_base = os.path.basename(old_file)
    if old_base != full_output_filename and old_base != clean_output_filename:
        try:
            trap_json = {
                "spider": "", 
                "notice": f"⚠️ 警告：关注Tg频道（@huliys9）获取最新接口密码\n\n当前专线已过期断流！老链接已彻底作废！",
                "warningText": "👑 特别提示：关注Tg频道（@huliys9）获取最新接口",
                "sites": [
                    {"key": "蝴蝶纯文字提示", "name": "🚨 ⚠️ 警告：关注Tg频道（@huliys9）获取最新接口密码\n\n当前专线已过期断流！老链接已彻底作废！🚨 当前专线密码已过期断流！", "type": 3, "api": "csp_JuDou", "searchable": 0, "quickSearch": 0, "filterable": 0},
                    {"key": "蝴蝶纯文字提示2", "name": "🚨 ⚠️ 警告：关注Tg频道（@huliys9）获取最新接口密码\n\n当前专线已过期断流！老链接已彻底作废！", "type": 3, "api": "csp_JuDou", "searchable": 0, "quickSearch": 0, "filterable": 0}
                ],
                "lives": [
                    {"group": "🚨 接口过期断流 ｜ 提示", "channels": [{"name": "👉 线路已过期 ➡️ 关注Tg频道（@huliys9）获取最新接口密码\n\n当前专线已过期断流！老链接已彻底作废！", "urls": ["http://127.0.0.1"]}]}
                ]
            }
            with open(old_file, 'w', encoding='utf-8') as f:
                json.dump(trap_json, f, ensure_ascii=False, indent=4)
        except:
            pass

for garbage in glob.glob('datas/config_*.json'):
    try: os.remove(garbage)
    except: pass


# ====================================================================
# 🛡️ 【方案 B 核心升级：具备智能容灾和老本备份的正统 JSON 加载器】
# ====================================================================
def load_json_safe(path):
    dir_name = os.path.dirname(path)
    base_name = os.path.basename(path)
    name_part, ext_part = os.path.splitext(base_name)
    backup_path = os.path.join(dir_name, f"{name_part}_backup{ext_part}")

    current_data = None
    is_current_valid = False

    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            try:
                current_data = json.load(f)
                if isinstance(current_data, dict) and ("sites" in current_data or "lives" in current_data or "parses" in current_data):
                    is_current_valid = True
                else:
                    print(f"⚠️ 警告：{path} JSON 结构不符合底包规范，判定为坏源！")
            except Exception:
                print(f"⚠️ 警告：{path} 发生损坏或为空，无法正常进行 JSON 解析！")

    if is_current_valid:
        try:
            with open(backup_path, 'w', encoding='utf-8') as b_f:
                json.dump(current_data, b_f, ensure_ascii=False, indent=4)
            print(f"✅ 成功：{path} 核心校验通过，已成功备份至本地。")
        except Exception as backup_err:
            print(f"🚨 备份同步到本地写入失败: {backup_err}")
        return current_data
    else:
        print(f"🚨 触发容灾机制：上游数据源 {path} 已失效！开启安全降级...")
        if os.path.exists(backup_path):
            with open(backup_path, 'r', encoding='utf-8') as b_f:
                try:
                    backup_data = json.load(b_f)
                    print(f"🥇 容灾成功！已成功加载上一次同步的历史底包数据: {backup_path}")
                    with open(path, 'w', encoding='utf-8') as f:
                        json.dump(backup_data, f, ensure_ascii=False, indent=4)
                    return backup_data
                except Exception:
                    print(f"❌ 严重错误：本地历史老本 {backup_path} 也意外损坏！")
        else:
            print(f"❌ 严重错误：未能在本地库中检索到历史备份文件 {backup_path}！")
        
        return {}

json_cnb = load_json_safe(cnb_path)
json_haitun = load_json_safe(haitun_path)
json_lz = load_json_safe(lz_path)

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
    if "name" in item: item["name"] = f"{item['name']}｜Tg：@huliys9"
for item in haitun_lives:
    if "name" in item: item["name"] = f"{item['name']}｜Tg：@huliys9"

cnb_sites = json_cnb.get("sites", [])
cnb_lives = json_cnb.get("lives", [])

combined_parses = json_haitun.get("parses", []) + json_lz.get("parses", []) + json_cnb.get("parses", [])

custom_keys = {site.get("key") for site in MY_CUSTOM_SITES if site.get("key")}
upstream_sites = haitun_sites + lz_nsfw_list + cnb_sites
clean_upstream_sites = [site for site in upstream_sites if site.get("key") not in custom_keys]

if BLOCK_KEYWORDS:
    filtered_upstream_sites = []
    for site in clean_upstream_sites:
        s_name = site.get("name", "")
        if any(kw.lower() in s_name.lower() for kw in BLOCK_KEYWORDS if kw):
            continue
        filtered_upstream_sites.append(site)
    clean_upstream_sites = filtered_upstream_sites

json_cnb["sites"] = clean_upstream_sites + MY_CUSTOM_SITES

custom_live_names = {live.get("name") for live in MY_CUSTOM_LIVES if live.get("name")}
base_lives = haitun_lives + cnb_lives

clean_base_lives = [
    live for live in base_lives 
    if live.get("name") not in custom_live_names 
    and "日本女优" not in live.get("name", "") 
    and "日本女友" not in live.get("name", "")
]

if BLOCK_KEYWORDS:
    filtered_base_lives = []
    for live in clean_base_lives:
        l_name = live.get("name", "")
        if any(kw.lower() in l_name.lower() for kw in BLOCK_KEYWORDS if kw):
            continue
        filtered_base_lives.append(live)
    clean_base_lives = filtered_base_lives

inserted_count = 0 
for custom_live in MY_CUSTOM_LIVES:
    live_name = custom_live.get("name", "")
    
    if BLOCK_KEYWORDS and any(kw.lower() in live_name.lower() for kw in BLOCK_KEYWORDS if kw):
        continue
        
    if "🔞" in live_name:
        clean_base_lives.append(custom_live)
    else:
        insert_idx = min(5 + inserted_count, len(clean_base_lives))
        clean_base_lives.insert(insert_idx, custom_live)
        inserted_count += 1

json_cnb["lives"] = clean_base_lives

final_json_text = json.dumps(json_cnb, ensure_ascii=False, indent=4)
final_json_text = final_json_text.replace('"key": "hajim-腾讯备"', '"spider": "./tvbox.jar",\n            "key": "hajim-腾讯备"').replace('"key": "茫茫"', '"spider": "./tvbox.jar",\n            "key": "茫茫"')
final_json_text = final_json_text.replace('🐬', '').replace('海豚影视', '').replace('海豚', '').replace('完全免费，如有收费的都是骗子', '').replace('交流群 TG：@hshsjk9', '')

path_replacements = {
    './spider.jar': 'https://cnb.cool/fish2018/xs/-/git/raw/main/spider.jar',
    './XBPQ/': 'https://cnb.cool/fish2018/xs/-/git/raw/main/XBPQ/',
    './XYQHiker/': 'https://cnb.cool/fish2018/xs/-/git/raw/main/XYQHiker/',
    './js/': 'https://cnb.cool/fish2018/xs/-/git/raw/main/js/',
    './json/': 'https://cnb.cool/fish2018/xs/-/git/raw/main/json/',
    './py/': 'https://cnb.cool/fish2018/xs/-/git/raw/main/py/',
    'http://127.0.0.1:9978/file/TVBox/logo.png': DEFAULT_LOGO_URL
}
for src, dst in path_replacements.items():
    final_json_text = final_json_text.replace(src, dst)

thanks_warning = "\n\n👑 🚨 重要提示：本接口密码不定期全自动更换！如果遇到失效或断流，请及时回 Telegram 频道（@huliys9）获取当前最新密码!"

try:
    final_obj = json.loads(final_json_text)
    if "warningText" in final_obj: final_obj.pop("warningText")
    
    ordered_obj = {}
    ordered_obj.update(final_obj)
    
    try:
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
                if doh_item.get("url", "").endswith("/dns-quer"): doh_item["url"] = doh_item["url"] + "y"
            ali_doh = {"name": "AliDNS", "url": "https://dns.alidns.com/dns-query", "ips": ["223.5.5.5", "223.6.6.6"]}
            if not any(d.get("name") == "AliDNS" for d in ordered_obj["doh"]): ordered_obj["doh"].insert(0, ali_doh)

        if "rules" in ordered_obj and isinstance(ordered_obj["rules"], list):
            custom_js_rules = [
                "console.log('蝴蝶影视 WebView 去广告模块启动');",
                "window.addEventListener('DOMContentLoaded', function() {",
                "   document.querySelectorAll('video').forEach(v => { v.muted = true; v.play().catch(e=>{}); });",
                "   Function.prototype.__constructor__ = Function.prototype.constructor;",
                "   Function.prototype.constructor = function() { if (arguments && typeof arguments[0] === 'string' && arguments[0].includes('debugger')) { return function(){}; } return Function.prototype.__constructor__.apply(this, arguments); };",
                "});",
                "setInterval(() => { let selectors = ['.adv-class', '.pop-banner', '#notice-modal', '[id*=\"partner\"]', '[class*=\"baidu\"]', 'iframe[src*=\"game\"]', 'iframe[src*=\"bet\"]', '#pop-ad', '.sidebar-ads', 'a[href*=\"999\"]']; selectors.forEach(sel => { document.querySelectorAll(sel).forEach(el => el.remove()); }); }, 400);"
            ]
            current_rules = ordered_obj.get("rules", [])
            ad_hosts = ["vip.wwgz.cn", "lziplayer.com", "m3u8.apibdzy.com", "cj.ffzyapi.com", "api.hbzyapi.com"]
            for rule in current_rules:
                if isinstance(rule, dict) and "hosts" in rule:
                    for h in rule["hosts"]:
                        if h not in ad_hosts: ad_hosts.append(h)
            js_injection_rule = {"name": "蝴蝶影视·云端高级去广告JS注入", "hosts": ad_hosts, "script": custom_js_rules}
            ordered_obj["rules"] = [js_injection_rule] + [r for r in current_rules if r.get("name") != "蝴蝶影视·云端高级去广告JS注入"]

        if "lives" in ordered_obj and isinstance(ordered_obj["lives"], list):
            clean_lives = []
            for live in ordered_obj["lives"]:
                if live and isinstance(live, dict):
                    if not live.get("ua") or live.get("ua") == "okhttp": live["ua"] = "okhttp/5.3.2"
                    clean_lives.append(live)
            ordered_obj["lives"] = clean_lives

        block_1_rebo, block_2_yingshi, block_3_duanju, block_4_dongman, block_5_cili, block_6_tiyu, block_7_shaoer, block_8_yinyue, block_9_fuli = [], [], [], [], [], [], [], [], []
        tg_tail_count = 0
 
        for site in ordered_obj.get("sites", []):
            if "name" not in site: continue
            raw_name = site["name"]
            s_key, s_genre, s_api = site.get("key", ""), site.get("genre", ""), site.get("api", "")
            for char in ['丨', '┃', ' ']: raw_name = raw_name.strip(char)
            raw_name = re.sub(r'\s+', ' ', raw_name)
            if "｜Tg：@huliys9" in raw_name:
                tg_tail_count += 1
                if tg_tail_count > 5: raw_name = raw_name.replace("｜Tg：@huliys9", "").strip()
            elif "｜Tg:@huliys9" in raw_name:
                tg_tail_count += 1
                if tg_tail_count > 5: raw_name = raw_name.replace("｜Tg:@huliys9", "").strip()
                
            if "ext" in site and site["ext"] == {}: site["ext"] = ""
            if isinstance(s_api, str) and "PanWebShare" in s_api:
                site["api"] = "csp_PanWebShare"
                if "jar" in site: site.pop("jar")

            is_guazi = "瓜子" in raw_name or "GZ" == s_key
            is_nsfw = False if is_guazi else ("🔞" in raw_name or "色播" in raw_name or "av" in s_key.lower() or "瓜" in raw_name or "爆料" in raw_name or "chat" in raw_name.lower() or "cam" in raw_name.lower() or "panda" in raw_name.lower() or "video" in raw_name.lower() or "md" in s_key.lower())
            
            if s_key == "热播影视":
                site["name"] = "热播 • APP｜此接口非原创，合并自海豚佬 and 鱼佬接口，感谢两位大佬的付出，如有侵权，联系删除｜@huliys9"
                site["category"] = "综合"
                block_1_rebo.append(site)
            elif "豆瓣" in raw_name and "首页" in raw_name:
                site["name"] = "🦋 豆瓣 • 首页"
                site["category"] = "综合"
                site["searchable"] = 0
                block_2_yingshi.append(site)
            elif is_nsfw:
                if not raw_name.startswith("🦋"): raw_name = f"🦋 {raw_name}"
                site["name"] = raw_name
                site["category"] = "福利"
                block_9_fuli.append(site)
            elif "短剧" in raw_name or "剧场" in raw_name:
                if "dj" in raw_name.lower() or "dj" in s_key.lower():
                    if not raw_name.startswith("🦋"): raw_name = f"🦋 {raw_name}"
                    site["name"] = raw_name
                    site["category"] = "音乐"
                    site["searchable"] = 0
                    block_8_yinyue.append(site)
                else:
                    if not raw_name.startswith("🦋"): raw_name = f"🦋 {raw_name}"
                    site["name"] = raw_name
                    site["category"] = "短剧"
                    site["genre"] = "shortdrama"
                    block_3_duanju.append(site)
            elif "动漫" in raw_name or "新番" in raw_name or "anime" in s_key.lower() or "a1" in raw_name.lower():
                if not raw_name.startswith("🦋"): raw_name = f"🦋 {raw_name}"
                site["name"] = raw_name
                site["category"] = "动漫"
                block_4_dongman.append(site)
            elif "磁力" in raw_name or "索" in raw_name or "盘" in raw_name or "云盘" in raw_name or "4k" in raw_name.lower():
                if not raw_name.startswith("🦋"): raw_name = f"🦋 {raw_name}"
                site["name"] = raw_name
                site["category"] = "网盘/磁力"
                if "PanWebShare" in site.get("api", ""): site["changeable"] = 1
                block_5_cili.append(site)
            elif "体育" in raw_name or "球" in raw_name or "直播" in raw_name:
                if not raw_name.startswith("🦋"): raw_name = f"🦋 {raw_name}"
                site["name"] = raw_name
                site["category"] = "体育/直播"
                block_6_tiyu.append(site)
            elif "少儿" in raw_name or "课堂" in raw_name or "教学" in raw_name or "教育" in raw_name:
                if not raw_name.startswith("🦋"): raw_name = f"🦋 {raw_name}"
                site["name"] = raw_name
                site["category"] = "少儿"
                site["searchable"] = 0
                block_7_shaoer.append(site)
            elif "音乐" in raw_name or "网易云" in raw_name or "听书" in raw_name or "唱会" in raw_name or "fm" in raw_name.lower() or "相声" in raw_name or "小品" in raw_name or "戏曲" in raw_name or "推送" in raw_name or "配置" in raw_name or "版本" in raw_name or "本地" in raw_name or "dj" in raw_name.lower() or "dj" in s_key.lower():
                if not raw_name.startswith("🦋"): raw_name = f"🦋 {raw_name}"
                site["name"] = raw_name
                site["category"] = "音乐" if ("音乐" in raw_name or "网易云" in raw_name or "听书" in raw_name or "fm" in raw_name.lower() or "dj" in raw_name.lower() or "dj" in s_key.lower()) else "综合"
                site["searchable"] = 0
                block_8_yinyue.append(site)
            else:
                if not raw_name.startswith("🦋"): raw_name = f"🦋 {raw_name}"
                site["name"] = raw_name
                site["category"] = "综合"
                block_2_yingshi.append(site)

            if site.get("category") not in ["少儿", "音乐"] and "searchable" not in site: site["searchable"] = 1

        for site in block_2_yingshi:
            if site.get("key") == "AQY": site["name"] = "🦋 爱奇艺 ｜Tg：@huliys9"

        ordered_obj["sites"] = (block_1_rebo + block_2_yingshi + block_3_duanju + block_4_dongman + block_6_tiyu + block_7_shaoer + block_8_yinyue + block_5_cili + block_9_fuli)
    except Exception as merge_err:
        print(f"⚠️ 分类合并发生异常: {merge_err}")

    # ====================================================================
    # 🔀 【双版本分流处理核心区】
    # ====================================================================
    # 1. 构造【全量至尊版】
    full_version_obj = copy.deepcopy(ordered_obj)
    full_welcome_notice = "👑 欢迎使用【蝴蝶影视粉丝专属全量至尊专线】！本接口由蝴蝶影视结合多方大底包无损重排而成，干净流畅。🚨 重要提示：本接口密码不定期全自动更换！"
    full_version_obj["notice"] = full_welcome_notice + thanks_warning
    
    full_final_out = {}
    if "notice" in full_version_obj: full_final_out["notice"] = full_version_obj.pop("notice")
    full_final_out.update(full_version_obj)

    # 2. 构造【客厅纯净版】
    clean_version_obj = copy.deepcopy(ordered_obj)
    clean_welcome_notice = "🏡 欢迎使用【蝴蝶影视专属绿色客厅专线】！本接口已全面过滤敏感、擦边和福利内容，全家老少看电视更安全、更绿色！"
    clean_version_obj["notice"] = clean_welcome_notice + thanks_warning
    
    nsfw_keywords = ["🔞", "福利", "探花", "约炮", "色播", "av", "爆料", "欧美", "蜜桃"]
    clean_version_obj["sites"] = [
        s for s in clean_version_obj.get("sites", [])
        if not any(kw in s.get("name", "") or kw in s.get("category", "") or kw in s.get("key", "").lower() for kw in nsfw_keywords)
    ]
    clean_version_obj["lives"] = [
        l for l in clean_version_obj.get("lives", [])
        if not any(kw in l.get("name", "") for kw in nsfw_keywords)
    ]
    
    clean_final_out = {}
    if "notice" in clean_version_obj: clean_final_out["notice"] = clean_version_obj.pop("notice")
    clean_final_out.update(clean_version_obj)

    # 设定绝对写入路径
    full_output_path = f"datas/{full_output_filename}"
    clean_output_path = f"datas/{clean_output_filename}"

    # ====================================================================
    # 🎯 【双向判定与 Markdown 排版下发区域】
    # ====================================================================
    tg_token = os.getenv("TG_TOKEN")
    tg_chat_id = os.getenv("TG_CHAT_ID")
    github_repo = os.getenv("GITHUB_REPOSITORY", "GodLike631/Ly_18")
    branch_info = os.getenv("GITHUB_REF_NAME", "main")
    
    # 高精度完美补全 refs/heads/ 核心物理节点
    full_raw_url = f"https://raw.githubusercontent.com/{github_repo}/refs/heads/{branch_info}/datas/{full_output_filename}"
    clean_raw_url = f"https://raw.githubusercontent.com/{github_repo}/refs/heads/{branch_info}/datas/{clean_output_filename}"
    
    full_sub_url = f"{GITHUB_PROXY}{full_raw_url}" if GITHUB_PROXY else full_raw_url
    clean_sub_url = f"{GITHUB_PROXY}{clean_raw_url}" if GITHUB_PROXY else clean_raw_url
    
    current_time = (datetime.datetime.utcnow() + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M")

    is_password_changed = False
    old_file_name = ""
    
    if os.path.exists(tracker_path):
        with open(tracker_path, 'r', encoding='utf-8') as f: 
            old_file_name = f.read().strip()
            
    if old_file_name != full_output_filename and old_file_name != "":
        is_password_changed = True

    # 🟢 情况一：触发密码变更 ➡️ 推送高亮 Markdown 专属大通知，并且强制彻底跳过名录变更
    if is_password_changed or is_new_token_generated:
        try:
            pwd_msg = "🔔 *蝴蝶影视全量版 · 全新硬核双通道密码锁发布* 🔔\n\n"
            pwd_msg += f"📅 *生效时间*：`{current_time}` (北京时间)\n"
            pwd_msg += f"🔑 *全新专线密锁*：`{current_token}`\n\n"
            pwd_msg += "🚀 *重要提示*：\n密码锁已成功交替！旧接口已全线开启【金蝉脱壳】大轰炸，老链接彻底作废，请及时复制下方对应通道的最新链接！\n\n"
            pwd_msg += f"🔞 *最新【蝴蝶影视全量版】矩阵订阅*：\n`{full_sub_url}`\n\n"
            pwd_msg += f"🏡 *最新【蝴蝶影视纯净版】客厅订阅*：\n`{clean_sub_url}`\n\n"
            pwd_msg += "👑 矩阵连接已在后台全自动换锁，请及时前往电视端更新。若电视端遇到断流请尝试重启软件或前往频道（@huliys9）获取支持！"

            pwd_url = f"https://api.telegram.org/bot{tg_token}/sendMessage"
            pwd_data = urllib.parse.urlencode({"chat_id": tg_chat_id, "parse_mode": "Markdown", "text": pwd_msg}).encode("utf-8")
            pwd_req = urllib.request.Request(pwd_url, data=pwd_data)
            with urllib.request.urlopen(pwd_req, timeout=15) as response:
                print("🚀 [专属密码通道] 蝴蝶影视密锁高档 Markdown 通知直发成功！")
        except Exception as pwd_err:
            print(f"❌ [专属密码通道] 发送通知失败: {pwd_err}")
            if hasattr(pwd_err, 'read'):
                print(f"🚨 [专属密码通道] TG服务器返回的真实死因: {pwd_err.read().decode('utf-8')}")
                
    # 🟢 情况二：没有换密码 ➡️ 正常对比 Diff，下发高精度限流 Markdown 变更通知
    else:
        try:
            old_sites_names, old_lives_names = set(), set()
            old_file_path = f"datas/{old_file_name}"
            if os.path.exists(old_file_path):
                with open(old_file_path, 'r', encoding='utf-8') as f:
                    old_data = json.load(f)
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
                MAX_DISPLAY = 15
                
                if added_sites or deleted_sites:
                    msg_lines.append("📺 *【点播线路变动】*")
                    if added_sites:
                        msg_lines.append("➕ *新增点播*：")
                        msg_lines.extend([f"  🟢 {name}" for name in added_sites[:MAX_DISPLAY]])
                        if len(added_sites) > MAX_DISPLAY: msg_lines.append(f"  ... 等更多共 {len(added_sites)} 个新点播源")
                    if deleted_sites:
                        if added_sites: msg_lines.append("")
                        msg_lines.append("➖ *剔除点播*：")
                        msg_lines.extend([f"  🔴 {name}" for name in deleted_sites[:MAX_DISPLAY]])
                        if len(deleted_sites) > MAX_DISPLAY: msg_lines.append(f"  ... 等更多共 {len(deleted_sites)} 个失效点播源")
                    msg_lines.append("📊 *━━━━━━━━━━━━━━*")
                    
                if added_lives or deleted_lives:
                    if len(msg_lines) > 2: msg_lines.append("")
                    msg_lines.append("📡 *【直播源站变动】*")
                    if added_lives:
                        msg_lines.append("➕ *新增直播*：")
                        msg_lines.extend([f"  🟢 {name}" for name in added_lives[:MAX_DISPLAY]])
                        if len(added_lives) > MAX_DISPLAY: msg_lines.append(f"  ... 等更多共 {len(added_lives)} 个新直播源")
                    if deleted_lives:
                        if added_lives: msg_lines.append("")
                        msg_lines.append("➖ *剔除直播*：")
                        msg_lines.extend([f"  🔴 {name}" for name in deleted_lives[:MAX_DISPLAY]])
                        if len(deleted_lives) > MAX_DISPLAY: msg_lines.append(f"  ... 等更多共 {len(deleted_lives)} 个失效直播源")
                    msg_lines.append("📊 *━━━━━━━━━━━━━━*")
                
                if tg_token and tg_chat_id:
                    detail_msg = "\n".join(msg_lines)
                    
                    full_msg = "🔔 *蝴蝶影视全量版 缝合矩阵接口变更通知* 🔔\n\n"
                    full_msg += f"📅 *更新时间*：{current_time} (北京时间)\n"
                    full_msg += "🚀 *变动说明*：检测到上游数据源更新或手工区调整，双版本配置已全自动编译上链！\n\n"
                    full_msg += f"{detail_msg}\n\n"
                    full_msg += "📡 *【 最新多版本订阅矩阵 (点击可自动复制)】*：\n\n"
                    full_msg += f"🔞 *1. 蝴蝶影视全量版* (包含全部线路):\n`{full_sub_url}`\n\n"
                    full_msg += f"🏡 *2. 蝴蝶影视纯净版* (已自动全面过滤敏感内容):\n`{clean_sub_url}`\n\n"
                    full_msg += "👑 全量版与纯净版已在后台无缝更新。更新配置即可，若遇到断流请尝试重启软件或及时前往频道（@huliys9）获取当前最新密码锁！"

                    url = f"https://api.telegram.org/bot{tg_token}/sendMessage"
                    data = urllib.parse.urlencode({"chat_id": tg_chat_id, "parse_mode": "Markdown", "text": full_msg}).encode("utf-8")
                    req = urllib.request.Request(url, data=data)
                    try:
                        with urllib.request.urlopen(req, timeout=15) as response:
                            print("🚀 Telegram 多版本矩阵变更通知 Markdown 直发成功！")
                    except Exception as net_err:
                        print(f"❌ Telegram 发送网络失败: {net_err}")
                        if hasattr(net_err, 'read'):
                            print(f"🚨 TG服务器返回的真实死因: {net_err.read().decode('utf-8')}")
            else:
                print("⏭️ 没有任何名录实际变动，智能拦截名录变更通知。")
        except Exception as diff_err:
            print(f"⚠️ 对比变动异常: {diff_err}")

    # 数据实体写出与追踪器改写（雷打不动，最后落盘，保证历史无污染）
    with open(full_output_path, 'w', encoding='utf-8') as f: json.dump(full_final_out, f, ensure_ascii=False, indent=4)
    with open(clean_output_path, 'w', encoding='utf-8') as f: json.dump(clean_final_out, f, ensure_ascii=False, indent=4)
    with open(tracker_path, 'w', encoding='utf-8') as f: f.write(full_output_filename)
    print(f"🎉 编译写出完成 -> 蝴蝶影视全量与纯净双通道实体构建完毕")

except Exception as e:
    print(f"❌ 运行失败: {e}")

if not os.path.exists(lock_file_path) or "-" not in (open(lock_file_path, 'r', encoding='utf-8').read() if os.path.exists(lock_file_path) else ""):
    with open(lock_file_path, 'w', encoding='utf-8') as f: f.write(f"{current_month}-{current_token}")
