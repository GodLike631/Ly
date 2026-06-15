import json
import os
import re

cnb_path = 'datas/cnb.json'
haitun_path = 'datas/haitun.json'
output_path = 'datas/local_config.json'

# 初始化最终的无损合流大框架
final_data = {
    "spider": "./tvbox.jar",  # 默认强制锁死为兼容性更广的 tvbox 核心
    "logo": "https://img.freepik.com/free-vector/cute-dolphin-swimming-cartoon-vector-icon-illustration-animal-nature-icon-isolated-flat-vector_138676-12582.jpg?semt=ais_hybrid&w=740&q=80",
    "wallpaper": "http://tool.teyonds.com/api",
    "warningText": "欢迎使用老杨自用全量缝合专线，本接口完全免费！",
    "sites": [],
    "parses": [],
    "lives": [],
    "rules": [],
    "flags": [],
    "ads": [],
    "doh": [],
    "ijk": []
}

# 强力文本提取器：用正则直接从文本中抠出指定数组中括号 [ ... ] 内部的所有对象块
def extract_objects_from_array(content, key):
    # 先定位到 "key": [
    pattern = r'"' + key + r'"\s*:\s*\[(.*?)\]\s*(?=\s*,\s*"|\s*\})'
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        return []
    
    block = match.group(1).strip()
    # 按照每个 {} 独立对象进行切分提取
    # 针对 sites 做了防 ext 嵌套花括号切碎的高级匹配
    if key == "sites":
        items = re.findall(r'\{\s*"key"\s*:\s*".*?"\s*,.*?\}\s*(?=\s*,\s*\[|\s*,\s*\{|\s*$)', block, re.DOTALL)
    else:
        items = re.findall(r'\{.*?\}', block, re.DOTALL)
        
    return [item.strip().strip(',') for item in items if item.strip()]

def read_file_text(path):
    if not os.path.exists(path):
        return ""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

text_cnb = read_file_text(cnb_path)
text_haitun = read_file_text(haitun_path)

# 全局去重字典集合
seen_site_keys = set()
seen_parse_urls = set()
seen_live_urls = set()

# ==================== 【1. 全量提取与网络化升级 CNB 的站点】 ====================
cnb_sites = extract_objects_from_array(text_cnb, "sites")
for site_text in cnb_sites:
    # 自动修复括号闭合
    if site_text.count('{') > site_text.count('}'):
        site_text += "}"
        
    # 核心网络路径升级，保证 CNB 的内容异地独立运行不失效
    if '"jar"' not in site_text:
        site_text = site_text.replace('{', '{\n      "jar": "https://cnb.cool/fish2018/xs/-/git/raw/main/spider.jar",', 1)
        
    site_text = site_text.replace('./XBPQ/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/XBPQ/')
    site_text = site_text.replace('./XYQHiker/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/XYQHiker/')
    site_text = site_text.replace('./js/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/js/')
    site_text = site_text.replace('./json/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/json/')
    site_text = site_text.replace('./py/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/py/')
    
    # 用正则抓出 key 用来去重
    key_match = re.search(r'"key"\s*:\s*"(.*?)"', site_text)
    if key_match:
        key_val = key_match.group(1)
        if key_val not in seen_site_keys:
            seen_site_keys.add(key_val)
            final_data["sites"].append(site_text)

# ==================== 【2. 全量提取海豚源的站点并合流（去重）】 ====================
haitun_sites = extract_objects_from_array(text_haitun, "sites")
for site_text in haitun_sites:
    if site_text.count('{') > site_text.count('}'):
        site_text += "}"
    key_match = re.search(r'"key"\s*:\s*"(.*?)"', site_text)
    if key_match:
        key_val = key_match.group(1)
        if key_val not in seen_site_keys:
            seen_site_keys.add(key_val)
            final_data["sites"].append(site_text)

# ==================== 【3. 全量融合去重解析接口 (parses)】 ====================
cnb_parses = extract_objects_from_array(text_cnb, "parses")
haitun_parses = extract_objects_from_array(text_haitun, "parses")

for parse_text in (cnb_parses + haitun_parses):
    url_match = re.search(r'"url"\s*:\s*"(.*?)"', parse_text)
    if url_match:
        url_val = url_match.group(1)
        if url_val not in seen_parse_urls:
            seen_parse_urls.add(url_val)
            final_data["parses"].append(parse_text)

# ==================== 【4. 全量融合去重直播源 (lives)】 ====================
cnb_lives = extract_objects_from_array(text_cnb, "lives")
haitun_lives = extract_objects_from_array(text_haitun, "lives")

for live_text in (cnb_lives + haitun_lives):
    url_match = re.search(r'"url"\s*:\s*"(.*?)"', live_text)
    if url_match:
        url_val = url_match.group(1)
        if url_val not in seen_live_urls:
            seen_live_urls.add(url_val)
            final_data["lives"].append(live_text)

# ==================== 【5. 完整并入 rules, flags, ads, doh, ijk】 ====================
for array_name in ["rules", "flags", "ads", "doh", "ijk"]:
    block_cnb = extract_objects_from_array(text_cnb, array_name)
    block_ht = extract_objects_from_array(text_haitun, array_name)
    # 合并两边的规则段
    combined_blocks = list(set(block_cnb + block_ht))
    final_data[array_name] = combined_blocks

# ==================== 【6. 硬核字符串纯文本组装生成最终文件】 ====================
def make_json_array_text(item_list):
    return ",\n    ".join(item_list)

final_json_text = f"""{{
  "spider": "{final_data['spider']}",
  "logo": "{final_data['logo']}",
  "wallpaper": "{final_data['wallpaper']}",
  "warningText": "{final_data['warningText']}",
  "sites": [
    {make_json_array_text(final_data['sites'])}
  ],
  "parses": [
    {make_json_array_text(final_data['parses'])}
  ],
  "lives": [
    {make_json_array_text(final_data['lives'])}
  ],
  "rules": [
    {make_json_array_text(final_data['rules'])}
  ],
  "flags": [
    {make_json_array_text(final_data['flags'])}
  ],
  "ads": [
    {make_json_array_text(final_data['ads'])}
  ],
  "doh": [
    {make_json_array_text(final_data['doh'])}
  ],
  "ijk": [
    {make_json_array_text(final_data['ijk'])}
  ]
}}"""

# 强效清洗行尾可能留下的语法瑕疵（比如空数组导致 [ , ] 错位）
final_json_text = re.sub(r'\[\s*,', '[', final_json_text)
final_json_text = re.sub(r',\s*\]', '\n  ]', final_json_text)

with open(output_path, 'w', encoding='utf-8') as f:
    f.write(final_json_text)

print("⚡ 真正意义上的全内容无损缝合大融合完成！")
