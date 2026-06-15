import os
import re

cnb_path = 'datas/cnb.json'
haitun_path = 'datas/haitun.json'
output_path = 'datas/local_config.json'

# 安全读取文件文本
def read_file_text(path):
    if not os.path.exists(path):
        return ""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

text_cnb = read_file_text(cnb_path)
text_haitun = read_file_text(haitun_path)

# 核心文本提取器：用正则直接抠出指定数组方括号 [ ... ] 内部的所有文本
def extract_array_content(content, key):
    # 匹配 "sites": [ 到 对应的 ] 之间的内容
    pattern = r'"' + key + r'"\s*:\s*\[(.*?)\]\s*(,\s*"|\s*\})'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""

# 1. 提取 CNB 的全部核心
sites_cnb = extract_array_content(text_cnb, "sites")
parses_cnb = extract_array_content(text_cnb, "parses")
lives_cnb = extract_array_content(text_cnb, "lives")

# 2. 提取 海豚的全部核心
sites_haitun = extract_array_content(text_haitun, "sites")
parses_haitun = extract_array_content(text_haitun, "parses")
lives_haitun = extract_array_content(text_haitun, "lives")

# 3. 强行文本级别揉合去重（把重合的逗号处理干净）
def merge_segments(seg1, seg2):
    seg1 = seg1.strip().strip(',')
    seg2 = seg2.strip().strip(',')
    if seg1 and seg2:
        return f"{seg1},\n    {seg2}"
    return seg1 if seg1 else seg2

final_sites = merge_segments(sites_cnb, sites_haitun)
final_parses = merge_segments(parses_cnb, parses_haitun)
final_lives = merge_segments(lives_cnb, lives_haitun)

# 4. 从 cnb 中把 rules, flags, ads, doh, ijk 数组块原封不动抠出来顶上去
rules_block = extract_array_content(text_cnb, "rules")
flags_block = extract_array_content(text_cnb, "flags")
ads_block = extract_array_content(text_cnb, "ads")
doh_block = extract_array_content(text_cnb, "doh")
ijk_block = extract_array_content(text_cnb, "ijk")

# 如果 cnb 缺失某些底层架构，则用海豚的补上
if not rules_block: rules_block = extract_array_content(text_haitun, "rules")
if not flags_block: flags_block = extract_array_content(text_haitun, "flags")
if not ads_block: ads_block = extract_array_content(text_haitun, "ads")
if not doh_block: doh_block = extract_array_content(text_haitun, "doh")
if not ijk_block: ijk_block = extract_array_content(text_haitun, "ijk")

# 5. 硬核纯文本拼装输出（完全绕过标准的 JSON 编码，直接生成最终文件！）
final_json_text = f"""{{
  "spider": "./tvbox.jar",
  "logo": "https://img.freepik.com/free-vector/cute-dolphin-swimming-cartoon-vector-icon-illustration-animal-nature-icon-isolated-flat-vector_138676-12582.jpg?semt=ais_hybrid&w=740&q=80",
  "wallpaper": "http://tool.teyonds.com/api",
  "warningText": "欢迎使用老杨自用缝合专线，本接口完全免费！",
  "sites": [
    {final_sites}
  ],
  "parses": [
    {final_parses}
  ],
  "lives": [
    {final_lives}
  ],
  "rules": [
    {rules_block}
  ],
  "flags": [
    {flags_block}
  ],
  "ads": [
    {ads_block}
  ],
  "doh": [
    {doh_block}
  ],
  "ijk": [
    {ijk_block}
  ]
}}"""

# 强力清洗行尾可能留下的多余空行逗号瑕疵
final_json_text = re.sub(r',\s*\]', '\n  ]', final_json_text)

with open(output_path, 'w', encoding='utf-8') as f:
    f.write(final_json_text)

print("🚀 文本级无损强行拆解缝合完成！")
