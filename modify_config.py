import json
import os
import re

cnb_path = 'datas/cnb.json'
haitun_path = 'datas/haitun.json'
output_path = 'datas/local_config.json'

# 1. 建立终极合流大框架，默认以海豚的壳子打底
final_data = {
    "spider": "./tvbox.jar",
    "logo": "https://img.freepik.com/free-vector/cute-dolphin-swimming-cartoon-vector-icon-illustration-animal-nature-icon-isolated-flat-vector_138676-12582.jpg?semt=ais_hybrid&w=740&q=80",
    "wallpaper": "http://tool.teyonds.com/api",
    "warningText": "欢迎使用老杨自用缝合专线，完全免费！",
    "sites": [],
    "parses": [],
    "lives": [],
    "rules": [],
    "flags": [],
    "ads": [],
    "doh": []
}

# 强力鲁棒性加载器：专门硬解影视接口中不规范的逗号、空行和行注释
def load_json_safely(path):
    if not os.path.exists(path):
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    # 剃掉行注释 // 和块注释 /* */
    content = re.sub(r'//.*', '', content)
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    try:
        if '{' in content and '}' in content:
            content = content[content.find('{'):content.rfind('}')+1]
        return eval(content, {"true": True, "false": False, "null": None})
    except Exception:
        return {}

data_cnb = load_json_safely(cnb_path)
data_haitun = load_json_safely(haitun_path)

# 全局唯一性去重集合
seen_site_keys = set()
seen_parse_urls = set()
seen_live_urls = set()

# 【第一步】继承基础的高级解析架构（优先拿海豚源的 rules、flags、ads、doh、ijk）
for k in ["rules", "flags", "ads", "doh", "ijk", "spider", "logo", "wallpaper", "warningText"]:
    if data_haitun and k in data_haitun and data_haitun[k]:
        final_data[k] = data_haitun[k]
    elif data_cnb and k in data_cnb and data_cnb[k]:
        final_data[k] = data_cnb[k]

# 【第二步】完整合并视频站点 (sites) 并按照 key 去重
all_sites = []
if data_cnb and 'sites' in data_cnb and isinstance(data_cnb['sites'], list): all_sites.extend(data_cnb['sites'])
if data_haitun and 'sites' in data_haitun and isinstance(data_haitun['sites'], list): all_sites.extend(data_haitun['sites'])

for site in all_sites:
    key = site.get('key')
    if key and key not in seen_site_keys:
        seen_site_keys.add(key)
        final_data['sites'].append(site)

# 【第三步】完整合并解析接口 (parses) 并按照 url 去重
all_parses = []
if data_cnb and 'parses' in data_cnb and isinstance(data_cnb['parses'], list): all_parses.extend(data_cnb['parses'])
if data_haitun and 'parses' in data_haitun and isinstance(data_haitun['parses'], list): all_parses.extend(data_haitun['parses'])

for parse in all_parses:
    url = parse.get('url')
    if url and url not in seen_parse_urls:
        seen_parse_urls.add(url)
        final_data['parses'].append(parse)

# 【第四步】完整合并直播源 (lives) 并按照 url 去重
all_lives = []
if data_cnb and 'lives' in data_cnb and isinstance(data_cnb['lives'], list): all_lives.extend(data_cnb['lives'])
if data_haitun and 'lives' in data_haitun and isinstance(data_haitun['lives'], list): all_lives.extend(data_haitun['lives'])

for live in all_lives:
    url = live.get('url')
    if url and url not in seen_live_urls:
        seen_live_urls.add(url)
        final_data['lives'].append(live)

# 【第五步】规整输出标准的 JSON 文件
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(final_data, f, ensure_ascii=False, indent=2)

print("🎉 两个仓库已在云端完整合并去重存盘！")
