import os
import re
import random
import string
import glob
import datetime
import json
import urllib.request
import urllib.parse

cnb_path = 'datas/cnb.json'
haitun_path = 'datas/haitun.json'
lz_path = 'datas/lz.json'

# 控制开关和追踪器文件路径
lock_file_path = 'datas/控制开关.txt'
tracker_path = 'datas/最新接口文件名.txt'

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
# ⏰ 【每月 1 号自动大洗牌与控制开关自动生成逻辑】 (原汁原味保留)
# ====================================================================
today = datetime.datetime.now()
current_month = str(today.month) 
is_reset_day = (today.day == 1)

saved_month = ""
saved_code = ""

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
elif is_reset_day and saved_month == current_month:
    current_token = saved_code
    print(f"🔒 【安全阀拦截】保持当月原暗号: {current_token}")
else:
    if not saved_code or len(saved_code) != 3 or "-" not in (content if os.path.exists(lock_file_path) else ""):
        current_token = ''.join(random.choices(string.ascii_lowercase + string.digits, k=3))
        with open(lock_file_path, 'w', encoding='utf-8') as f:
            f.write(f"{current_month}-{current_token}")
    else:
        current_token = saved_code
    print(f"📡 正常沿用本月密锁: {current_token}")

if current_token in ["全量版", "纯净版"]:
    output_filename = "蝴蝶影视全量版.json"
else:
    output_filename = f"蝴蝶影视全量版{current_token}.json"

output_path = f"datas/{output_filename}"
print(f"🎯 最终结算 -> 目标输出：{output_filename}")

# ====================================================================
# 🛡️ 【金蝉脱壳：全量版过期旧线自动全文字大轰炸】 (原汁原味保留)
# ====================================================================
old_configs = glob.glob('datas/蝴蝶影视全量版*.json') + glob.glob('datas/蝴蝶影视*.json') + glob.glob('datas/老杨TV*.json')
for old_file in old_configs:
    if os.path.basename(old_file) != output_filename:
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

def load_json_safe(path):
    if not os.path.exists(path):
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except Exception as e:
            print(f"❌ 错误：{path} JSON 格式不正确！")
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
    if "name" in item:
        item["name"] = f"{item['name']}｜Tg：@huliys9"
for item in haitun_lives:
    if "name" in item:
        item["name"] = f"{item['name']}｜Tg：@huliys9"

cnb_sites = json_cnb.get("sites", [])
cnb_lives = json_cnb.get("lives", [])

combined_parses = json_haitun.get("parses", []) + json_lz.get("parses", []) + json_cnb.get("parses", [])

custom_keys = {site.get("key") for site in MY_CUSTOM_SITES if site.get("key")}
upstream_sites = haitun_sites + lz_nsfw_list + cnb_sites
clean_upstream_sites = [site for site in upstream_sites if site.get("key") not in custom_keys]
json_cnb["sites"] = clean_upstream_sites + MY_CUSTOM_SITES

custom_live_names = {live.get("name") for live in MY_CUSTOM_LIVES if live.get("name")}
base_lives = haitun_lives + cnb_lives

clean_base_lives = [
    live for live in base_lives if live.get("name") not in custom_live_names and "日本女优" not in live.get("name", "") and "日本女友" not in live.get("name", "")
]

inserted_count = 0 
for custom_live in MY_CUSTOM_LIVES:
    live_name = custom_live.get("name", "")
    if "🔞" in live_name:
        clean_base_lives.append(custom_live)
    else:
        insert_idx = 5 + inserted_count
        if len(clean_base_lives) >= insert_idx:
            clean_base_lives.insert(insert_idx, custom_live)
        else:
            clean_base_lives.append(custom_live)
        inserted_count += 1

json_cnb["lives"] = clean_base_lives

final_json_text = json.dumps(json_cnb, ensure_ascii=False, indent=4)
final_json_text = final_json_text.replace('"key": "hajim-腾讯备"', '"spider": "./tvbox.jar",\n            "key": "hajim-腾讯备"')
final_json_text = final_json_text.replace('"key": "茫茫"', '"spider": "./tvbox.jar",\n            "key": "茫茫"')
final_json_text = final_json_text.replace('🐬', '').replace('海豚影视', '').replace('海豚', '')
final_json_text = final_json_text.replace('完全免费，如有收费的都是骗子', '').replace('交流群 TG：@hshsjk9', '')

path_replacements = {
    './spider.jar': 'https://cnb.cool/fish2018/xs/-/git/raw/main/spider.jar',
    './XBPQ/': 'https://cnb.cool/fish2018/xs/-/git/raw/main/XBPQ/',
    './XYQHiker/': 'https://cnb.cool/fish2018/xs/-/git/raw/main/XYQHiker/',
    './js/': 'https://cnb.cool/fish2018/xs/-/git/raw/main/js/',
    './json/': 'https://cnb.cool/fish2018/xs/-/git/raw/main/json/',
    './py/': 'https://cnb.cool/fish2018/xs/-/git/raw/main/py/',
    'http://127.0.0.1:9978/file/TVBox/logo.png': 'https://img.naixiai.cn/2026/06/18/IMG_6638.jpeg'
}
for src, dst in path_replacements.items():
    final_json_text = final_json_text.replace(src, dst)

thanks_warning = "👑 🚨 重要提示：本接口密码不定期全自动更换！如果遇到失效或断流，请及时回 Telegram 频道（@huliys9）获取当前最新密码!"
welcome_notice = "👑 欢迎使用【蝴蝶影视粉丝专属缝合专线】！本接口由蝴蝶影视结合多方大底包无损重排而成，干净流畅。🚨 重要提示：本接口密码不定期全自动更换！如果遇到失效或断流，请及时回 Telegram 频道（@huliys9）获取当前最新密码!"

try:
    final_obj = json.loads(final_json_text)
    final_obj["notice"] = welcome_notice
    if "warningText" in final_obj:
        final_obj.pop("warningText")
        
    ordered_obj = {}
    if "notice" in final_obj: 
        ordered_obj["notice"] = final_obj.pop("notice")
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
                if doh_item.get("url", "").endswith("/dns-quer"):
                    doh_item["url"] = doh_item["url"] + "y"
            
            ali_doh = {
                "name": "AliDNS",
                "url": "https://dns.alidns.com/dns-query",
                "ips": ["223.5.5.5", "223.6.6.6"]
            }
            if not any(d.get("name") == "AliDNS" for d in ordered_obj["doh"]):
                ordered_obj["doh"].insert(0, ali_doh)

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
            js_injection_rule = {
                "name": "蝴蝶影视·云端高级去广告JS注入",
                "hosts": ad_hosts,
                "script": custom_js_rules
            }
            ordered_obj["rules"] = [js_injection_rule] + [r for r in current_rules if r.get("name") != "蝴蝶影视·云端高级去广告JS注入"]

        if "lives" in ordered_obj and isinstance(ordered_obj["lives"], list):
            clean_lives = []
            for live in ordered_obj["lives"]:
                if live and isinstance(live, dict):
                    if not live.get("ua") or live.get("ua") == "okhttp":
                        live["ua"] = "okhttp/5.3.2"
                    clean_lives.append(live)
            ordered_obj["lives"] = clean_lives

        block_1_rebo = []         
        block_2_yingshi = []      
        block_3_duanju = []       
        block_4_dongman = []      
        block_5_cili = []         
        block_6_tiyu = []         
        block_7_shaoer = []       
        block_8_yinyue = []       
        block_9_fuli = []         

        tg_tail_count = 0
        for site in ordered_obj.get("sites", []):
            if "name" not in site:
                continue
                
            raw_name = site["name"]
            s_key = site.get("key", "")
            s_genre = site.get("genre", "")
            s_api = site.get("api", "")

            for char in ['丨', '┃', ' ']:
                raw_name = raw_name.strip(char)
            raw_name = re.sub(r'\s+', ' ', raw_name)
            
            if "｜Tg：@huliys9" in raw_name:
                tg_tail_count += 1
                if tg_tail_count > 5: raw_name = raw_name.replace("｜Tg：@huliys9", "").strip()
            elif "｜Tg:@huliys9" in raw_name:
                tg_tail_count += 1
                if tg_tail_count > 5: raw_name = raw_name.replace("｜Tg:@huliys9", "").strip()

            if "ext" in site and site["ext"] == {}:
                site["ext"] = ""

            if isinstance(s_api, str) and "PanWebShare" in s_api:
                site["api"] = "csp_PanWebShare"
                if "jar" in site:
                    site.pop("jar")

            is_guazi = "瓜子" in raw_name or "GZ" == s_key
            is_nsfw = False if is_guazi else ("🔞" in raw_name or "色播" in raw_name or "av" in s_key.lower() or "瓜" in raw_name or "爆料" in raw_name or "chat" in raw_name.lower() or "cam" in raw_name.lower() or "panda" in raw_name.lower() or "video" in raw_name.lower() or "md" in s_key.lower())
            is_target_rebo_main = (s_key == "热播影视")

            if is_target_rebo_main:
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
                if "PanWebShare" in site.get("api", ""):
                    site["changeable"] = 1
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
                if "音乐" in raw_name or "网易云" in raw_name or "听书" in raw_name or "fm" in raw_name.lower() or "dj" in raw_name.lower() or "dj" in s_key.lower():
                    site["category"] = "音乐"
                else:
                    site["category"] = "综合"
                site["searchable"] = 0
                block_8_yinyue.append(site)
            else:
                if not raw_name.startswith("🦋"): raw_name = f"🦋 {raw_name}"
                site["name"] = raw_name
                site["category"] = "综合"
                block_2_yingshi.append(site)

            if site.get("category") not in ["少儿", "音乐"] and "searchable" not in site:
                site["searchable"] = 1

        for site in block_2_yingshi:
            if site.get("key") == "AQY":
                site["name"] = "🦋 爱奇艺 ｜Tg：@huliys9"

        ordered_obj["sites"] = (
            block_1_rebo + block_2_yingshi + block_3_duanju + block_4_dongman +
            block_6_tiyu + block_7_shaoer + block_8_yinyue + block_5_cili + block_9_fuli
        )
        print(f"🚀 【洗牌结算】双通道完全体融合重组完成！")
    except Exception as inner_e:
        print(f"⚠️ 提示：高级大屏排版美化阶段跳过: {inner_e}")

    # ====================================================================
    # 🎯 【超高精度对比：新旧 JSON 最终文件的 Sites 与 Lives 精准中文名录对比】
    # ====================================================================
    try:
        old_sites_names, old_lives_names = set(), set()
        if os.path.exists(tracker_path):
            with open(tracker_path, 'r', encoding='utf-8') as f:
                old_file_name = f.read().strip()
            old_file_path = f"datas/{old_file_name}"
            if os.path.exists(old_file_path):
                with open(old_file_path, 'r', encoding='utf-8') as f:
                    old_data = json.load(f)
                    old_sites_names = {s.get("name", "").strip() for s in old_data.get("sites", []) if s.get("name")}
                    old_lives_names = {l.get("name", "").strip() for l in old_data.get("lives", []) if l.get("name")}

        new_sites_names = {s.get("name", "").strip() for s in ordered_obj.get("sites", []) if s.get("name")}
        new_lives_names = {l.get("name", "").strip() for l in ordered_obj.get("lives", []) if l.get("name")}

        # 分离点播与直播的实际中文名称名录增减
        added_sites = sorted(list(new_sites_names - old_sites_names))
        deleted_sites = sorted(list(old_sites_names - new_sites_names))
        added_lives = sorted(list(new_lives_names - old_lives_names))
        deleted_lives = sorted(list(old_lives_names - new_lives_names))

        if added_sites or deleted_sites or added_lives or deleted_lives:
            msg_lines = ["📝 *【 变动明细预览 】*", "📊 *━━━━━━━━━━━━━━━*"]
            
            # 点播线变动展示
            if added_sites or deleted_sites:
                msg_lines.append("📺 *【点播线路变动】*")
                if added_sites:
                    msg_lines.append("➕ *新增点播*：")
                    msg_lines.extend([f"🟢 {name}" for name in added_sites])
                if deleted_sites:
                    if added_sites: msg_lines.append("")
                    msg_lines.append("➖ *剔除点播*：")
                    msg_lines.extend([f"🔴 {name}" for name in deleted_sites])
                msg_lines.append("📊 *━━━━━━━━━━━━━━━*")
                
            # 直播线变动展示
            if added_lives or deleted_lives:
                if len(msg_lines) > 2: msg_lines.append("")
                msg_lines.append("📡 *【直播源站变动】*")
                if added_lives:
                    msg_lines.append("➕ *新增直播*：")
                    msg_lines.extend([f"🟢 {name}" for name in added_lives])
                if deleted_lives:
                    if added_lives: msg_lines.append("")
                    msg_lines.append("➖ *剔除直播*：")
                    msg_lines.extend([f"🔴 {name}" for name in deleted_lives])
                msg_lines.append("📊 *━━━━━━━━━━━━━━━*")

            # 抓取工作流注入的 TG 变量，开启 Python 高速网络直发
            tg_token = os.getenv("TG_TOKEN")
            tg_chat_id = os.getenv("TG_CHAT_ID")
            github_repo = os.getenv("GITHUB_REPO", "GodLike631/Ly_18")
            
            if tg_token and tg_chat_id:
                current_time = (datetime.datetime.utcnow() + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M")
                detail_msg = "\n".join(msg_lines)
                
                # 动态捕捉最新的加密后或大洗牌后的接口链接
                subscribe_url = f"https://raw.githubusercontent.com/{github_repo}/refs/heads/main/datas/{output_filename}"

                # 完美复现和组装您原始文件里的报头和报尾结构
                full_msg = f"🔔 *蝴蝶影视全量版接口变更明细通知* 🔔\n\n"
                full_msg += f"📅 *更新时间*：{current_time} (北京时间)\n"
                full_msg += f"🚀 *变动说明*：检测到上游数据源更新或手工区线路调整，新接口配置已全自动编译上链！\n\n"
                full_msg += f"{detail_msg}\n\n"
                full_msg += f"🔗 *【 全量版专用链接 】* (点击可自动复制)：\n`{subscribe_url}`\n\n"
                full_msg += f"👑 全量版链接已在后台无缝更新，更新接口即可！若电视端遇到断流请尝试重启软件或及时前往频道（@huliys9）获取当前最新密码锁！"

                # 原生 urllib 安全投递，永不卡缓冲区死锁
                url = f"https://api.telegram.org/bot{tg_token}/sendMessage"
                data = urllib.parse.urlencode({"chat_id": tg_chat_id, "parse_mode": "Markdown", "text": full_msg}).encode("utf-8")
                req = urllib.request.Request(url, data=data)
                try:
                    with urllib.request.urlopen(req, timeout=15) as response:
                        print("🚀 Telegram 蝴蝶全量版变更通知通过 Python 直发成功！")
                except Exception as net_err:
                    print(f"❌ Telegram 推送网络异常失败: {net_err}")
            else:
                print("⚠️ 提示：未检测到绑定的 TG_TOKEN 或 TG_CHAT_ID，跳过通知发送。")
        else:
            print("⏭️ 没有任何中文名录线路发生增减，智能拦截通知流程。")
            
    except Exception as diff_err:
        print(f"⚠️ 对比变动异常: {diff_err}")

    # 原逻辑：写出最终生成的完整 JSON 字典并更新追踪器
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(ordered_obj, f, ensure_ascii=False, indent=4)
        
    with open(tracker_path, 'w', encoding='utf-8') as f:
        f.write(output_filename)
    print(f"🎉 编译打包完成: {output_path}")
except Exception as e:
    print(f"❌ 运行失败: {e}")

if not os.path.exists(lock_file_path) or "-" not in (open(lock_file_path, 'r', encoding='utf-8').read() if os.path.exists(lock_file_path) else ""):
    with open(lock_file_path, 'w', encoding='utf-8') as f:
        f.write(f"{current_month}-{current_token}")
