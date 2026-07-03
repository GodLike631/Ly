import os
import re
import random
import string
import glob
import datetime
import json

cnb_path = 'datas/cnb.json'
haitun_path = 'datas/haitun.json'
lz_path = 'datas/lz.json'

# 控制开关和追踪器文件路径
lock_file_path = 'datas/控制开关.txt'
tracker_path = 'datas/最新接口文件名.txt'

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
    print(f"⏰ 【每月1号全新硬核洗牌】检测到进入新月份 {current_month} 月！已全自动抽签生成本月新密锁: {current_token}")
elif is_reset_day and saved_month == current_month:
    current_token = saved_code
    print(f"🔒 【安全阀拦截】今日 1 号已经是当月第二次运行，保持原暗号: {current_token}")
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
            print(f"📡 【金蝉脱壳】已成功将过期旧线调包为纯文字大轰炸: {old_file}")
        except Exception as e:
            pass

for garbage in glob.glob('datas/config_*.json'):
    try: os.remove(garbage)
    except: pass


# ====================================================================
# 🧠 【核心逻辑：正统 JSON 对象读取与合并逻辑】 (原汁原味保留)
# ====================================================================
def load_json_safe(path):
    if not os.path.exists(path):
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except Exception as e:
            print(f"❌ 错误：{path} JSON 格式不正确！无法解析。")
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

country_live_dict = {
    "name": "乡村电视 ｜Tg：@huliys9",
    "type": 0,
    "playerType": 2,
    "ua": "okhttp/5.3.2",
    "url": "https://gh-proxy.com/https://raw.githubusercontent.com/GodLike631/test/refs/heads/main/datas/%E4%B9%A1%E6%9D%91%E7%94%B5%E8%A7%86.txt"
}
if len(haitun_lives) >= 5:
    haitun_lives.insert(5, country_live_dict)
else:
    haitun_lives.append(country_live_dict)

cnb_sites = json_cnb.get("sites", [])
cnb_lives = json_cnb.get("lives", [])

combined_parses = json_haitun.get("parses", []) + json_lz.get("parses", []) + json_cnb.get("parses", [])

json_cnb["sites"] = haitun_sites + lz_nsfw_list + cnb_sites
json_cnb["lives"] = haitun_lives + cnb_lives

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
welcome_notice = "👑 欢迎使用【蝴蝶影视粉丝专属缝合专线】！本接口由蝴蝶影视结合海豚佬&鱼佬的优质核心资源缝合而成，纯净无广告！🚨 重要提示：本接口密码不定期全自动更换！如果遇到失效或断流，请及时回 Telegram 频道（@huliys9）获取当前最新密码！"

try:
    final_obj = json.loads(final_json_text)
    final_obj["notice"] = welcome_notice
    final_obj["warningText"] = thanks_warning
    
    ordered_obj = {}
    if "notice" in final_obj: ordered_obj["notice"] = final_obj.pop("notice")
    if "warningText" in final_obj: ordered_obj["warningText"] = final_obj.pop("warningText")
    ordered_obj.update(final_obj)
    
    # ====================================================================
    # 🌟【全新黑科技注入區：大屏體驗極致優化】
    # ====================================================================
    try:
        # --- 1. 解析器去重與優化加载 ---
        unique_parses = []
        seen_names = set()
        for p in combined_parses:
            name = p.get("name", "")
            if name and name not in seen_names:
                unique_parses.append(p)
                seen_names.add(name)
        ordered_obj["parses"] = unique_parses

        # --- 2. 注入国内低延迟高防 AliDNS 到 doh 的最前列 并纠正潜在拼写错误 ---
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

        # --- 3. 彻底扫除直播 lives 列表末端隐蔽的空对象 {}，杜绝闪退 ---
        if "lives" in ordered_obj and isinstance(ordered_obj["lives"], list):
            ordered_obj["lives"] = [live for live in ordered_obj["lives"] if live]

        # --- 4. 雲端高級去廣告 WebView JS 腳本強勢注入 ---
        custom_js_rules = [
            "console.log('蝴蝶影視高級WebView攔截器啟動');",
            "window.addEventListener('DOMContentLoaded', function() {",
            "   document.querySelectorAll('video').forEach(v => { v.muted = true; v.play().catch(e=>{}); });",
            "   Function.prototype.__constructor__ = Function.prototype.constructor;",
            "   Function.prototype.constructor = function() { if (arguments && typeof arguments[0] === 'string' && arguments[0].includes('debugger')) { return function(){}; } return Function.prototype.__constructor__.apply(this, arguments); };",
            "});",
            "setInterval(() => {",
            "   let selectors = ['.adv-class', '.pop-banner', '#notice-modal', '[id*=\"partner\"]', '[class*=\"baidu\"]', 'iframe[src*=\"game\"]', 'iframe[src*=\"bet\"]', '#pop-ad', '.sidebar-ads', 'a[href*=\"999\"]'];",
            "   selectors.forEach(sel => { document.querySelectorAll(sel).forEach(el => el.remove()); });",
            "}, 400);"
        ]

        current_rules = ordered_obj.get("rules", [])
        if not isinstance(current_rules, list):
            current_rules = []
            
        ad_hosts = ["vip.wwgz.cn", "lziplayer.com", "m3u8.apibdzy.com", "cj.ffzyapi.com", "api.hbzyapi.com"]
        for rule in current_rules:
            if isinstance(rule, dict) and "hosts" in rule:
                for h in rule["hosts"]:
                    if h not in ad_hosts: ad_hosts.append(h)

        js_injection_rule = {
            "name": "蝴蝶影视·雲端高級去廣告JS注入",
            "hosts": ad_hosts,
            "script": custom_js_rules
        }
        ordered_obj["rules"] = [js_injection_rule] + [r for r in current_rules if r.get("name") != "老楊TV·雲端高級去廣告JS注入"]

        # --- 5 & 6. 🏆【核心重写：九大方阵智能清洗洗牌 与 热播影视精准置顶长鸣谢算法】 ---
        block_1_rebo = []         # 1. 🏆 热播影视专属置顶方阵 (仅限 key: 热播影视)
        block_2_yingshi = []      # 2. 影视/追剧/APP大类
        block_3_duanju = []       # 3. 短剧/剧场
        block_4_dongman = []      # 4. 动漫类
        block_5_cili = []         # 5. 网盘/磁力/4K (配合Token未配自动不加载特性)
        block_6_tiyu = []         # 6. 体育/看球/直播
        block_7_shaoer = []       # 7. 少儿课堂/教育
        block_8_yinyue = []       # 8. 音乐/听书/功能线/DJ
        block_9_fuli = []         # 9. 福利/18禁 (绝对大沉底)

        tg_tail_count = 0  
        for site in ordered_obj.get("sites", []):
            if "name" not in site:
                continue
                
            raw_name = site["name"]
            s_key = site.get("key", "")
            s_genre = site.get("genre", "")
            s_api = site.get("api", "")

            # 🛠️ 1. 清洗名称里的脏字符
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

            # 🛠️ 2. 【网盘净化】网盘组件去后缀强行洗白，完美解决Token未配引发的死锁漏洞
            if isinstance(s_api, str) and "PanWebShare" in s_api:
                site["api"] = "csp_PanWebShare"
                if "jar" in site:
                    site.pop("jar")

            # 🛠️ 3. 瓜子靶向保护：防误伤，强力摘出
            is_guazi = "瓜子" in raw_name or "GZ" == s_key

            # 🛠️ 4. 精准捕获福利关键字（排除瓜子后）
            is_nsfw = False if is_guazi else ("🔞" in raw_name or "色播" in raw_name or "av" in s_key.lower() or "瓜" in raw_name or "爆料" in raw_name or "chat" in raw_name.lower() or "cam" in raw_name.lower() or "panda" in raw_name.lower() or "video" in raw_name.lower() or "md" in s_key.lower())

            # 🛠️ 5. 【硬核硬对齐】判定是否为唯一的特定置顶源 "key": "热播影视"
            is_target_rebo_main = (s_key == "热播影视")

            # 🛠️ 6. 彻底完成洗牌分流与名字特调
            if is_target_rebo_main:
                # 🎯 热播影视登顶：注入大长鸣谢词后缀，推入置顶第一位 block_1
                site["name"] = "热播 • APP｜此接口非原创，合并自海豚佬 and 鱼佬接口，感谢两位大佬的付出，如有侵权，联系删除｜@huliys9"
                site["category"] = "综合"
                block_1_rebo.append(site)

            elif "豆瓣" in raw_name and "首页" in raw_name:
                # 豆瓣解绑：恢复其原本清净名，归队普通影视区 block_2
                site["name"] = "🦋 豆瓣 • 首页"
                site["category"] = "综合"
                site["searchable"] = 0
                block_2_yingshi.append(site)

            elif is_nsfw:
                if not raw_name.startswith("🦋"): raw_name = f"🦋 {raw_name}"
                site["name"] = raw_name
                site["category"] = "福利"
                site["searchable"] = 0  
                site["quickSearch"] = 0
                block_9_fuli.append(site)
                
            elif "短剧" in raw_name or "剧场" in raw_name:
                # 包含 DJ/dj 关键词的线一律强行分流进入音乐阵营
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
                
            elif "磁力" in raw_name or "索" in raw_name or "盘" in raw_name or "云盘" in raw_name or "4k" in raw_name.lower() or "PanWebShare" in str(s_api):
                if not raw_name.startswith("🦋"): raw_name = f"🦋 {raw_name}"
                site["name"] = raw_name
                site["category"] = "网盘/磁力"
                
                # 锁定网盘被动检索，强制实施沉底降权以免疫本地历史死锁
                site["searchable"] = 0
                site["quickSearch"] = 0
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
                # 默认综合大类（保留包含 key: rb 在内的其余非置顶影视普适线路位置）
                if not raw_name.startswith("🦋"): raw_name = f"🦋 {raw_name}"
                site["name"] = raw_name
                site["category"] = "综合"
                block_2_yingshi.append(site)

            # 🛠️ 7. 补齐非音乐少儿类的全局搜索功能开关
            if site.get("category") not in ["少儿", "音乐"] and "searchable" not in site:
                site["searchable"] = 1

        # 🛠️ 8. 爱奇艺官方名称规格对齐
        for site in block_2_yingshi:
            if site.get("key") == "AQY":
                site["name"] = "🦋 爱奇艺 ｜Tg：@huliys9"

        # 👑 【新首页硬组装】"key": "热播影视" 携长致谢完美置顶（Index 0），另一个热播"key": "rb"随大部队在综合影视区排列
        ordered_obj["sites"] = (
            block_1_rebo +         # 1. 🎯 "key": "热播影视" 绝对置顶
            block_2_yingshi +      # 2. 传统综合影视单线路 (包含回归的豆瓣首页和保留原位的 key: rb 线路)
            block_3_duanju +       # 3. 独立短剧
            block_4_dongman +      # 4. 动漫新番
            block_6_tiyu +         # 5. 体育直播
            block_7_shaoer +       # 6. 少儿课堂
            block_8_yinyue +       # 7. 音乐/听书/功能辅助线
            block_5_cili +         # 8. 网盘/磁力/4K降权沉底区
            block_9_fuli           # 9. 福利18禁安全坠尾
        )
        print(f"🚀 【洗牌结算】蝴蝶影视全量版合并重组完成！热播 APP 已精准承接置顶，网盘依赖全面洗白降权。")

    except Exception as inner_e:
        print(f"⚠️ 提示：高级大屏排版美化阶段跳过，原因: {inner_e}")

    # ====================================================================
    # 🌟【数据安全落盘】
    # ====================================================================
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(ordered_obj, f, ensure_ascii=False, indent=4)
        
    with open(tracker_path, 'w', encoding='utf-8') as f:
        f.write(output_filename)
        
    print(f"🎉 全量版更新成功！配置已写出至: {output_path}")

except Exception as e:
    print(f"❌ 严重错误：最后的本地渲染失败，原因: {e}")

if not os.path.exists(lock_file_path) or "-" not in (open(lock_file_path, 'r', encoding='utf-8').read() if os.path.exists(lock_file_path) else ""):
    with open(lock_file_path, 'w', encoding='utf-8') as f:
        f.write(f"{current_month}-{current_token}")
