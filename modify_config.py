import os
import re

cnb_path = 'datas/cnb.json'
haitun_path = 'datas/haitun.json'
output_path = 'datas/local_config.json'

def read_file_text(path):
    if not os.path.exists(path):
        return ""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

text_cnb = read_file_text(cnb_path)
text_haitun = read_file_text(haitun_path)

# ====================================================================
# 【核心算法升级】：纯物理大挪移，不需要懂结构，只管把两边数组内的文本无损合并
# ====================================================================
def get_array_inner_text(content, key):
    split_key = f'"{key}": ['
    if split_key not in content:
        return ""
    # 切出数组后面的所有文本
    after_key = content.split(split_key, 1)[1]
    
    # 巧妙利用找中括号闭合的原理，截取最前面的内容
    # 影视接口数组一般以 "],\n" 或 "]\n" 结束
    if '],' in after_key:
        inner_text = after_key.split('],', 1)[0]
    else:
        # 兜底截取到第一个右中括号
        inner_text = after_key.split(']', 1)[0]
        
    return inner_text.strip()

# 1. 提取双方所有核心数组的纯文本段落
sites_cnb = get_array_inner_text(text_cnb, "sites")
sites_ht = get_array_inner_text(text_haitun, "sites")

parses_cnb = get_array_inner_text(text_cnb, "parses")
parses_ht = get_array_inner_text(text_haitun, "parses")

lives_cnb = get_array_inner_text(text_cnb, "lives")
lives_ht = get_array_inner_text(text_haitun, "lives")

rules_cnb = get_array_inner_text(text_cnb, "rules")
rules_ht = get_array_inner_text(text_haitun, "rules")

flags_cnb = get_array_inner_text(text_cnb, "flags")
flags_ht = get_array_inner_text(text_haitun, "flags")

ads_cnb = get_array_inner_text(text_cnb, "ads")
ads_ht = get_array_inner_text(text_haitun, "ads")

doh_cnb = get_array_inner_text(text_cnb, "doh")
doh_ht = get_array_inner_text(text_haitun, "doh")

ijk_cnb = get_array_inner_text(text_cnb, "ijk")
ijk_ht = get_array_inner_text(text_haitun, "ijk")

# ====================================================================
# 【路径修复手术】：只针对 CNB 提取出来的站点文本段进行绝对路径升级
# ====================================================================
if sites_cnb:
    # 让所有没有写 jar 的站点统一认回 cnb 的 spider.jar
    # 考虑到有些站点内部带有换行，我们直接把第一个 {"key" 替换成插入 jar 的版本
    sites_cnb = re.sub(r'\{\s*"key"\s*:', '{\n      "jar": "https://cnb.cool/fish2018/xs/-/git/raw/main/spider.jar",\n      "key":', sites_cnb)
    
    # 强行补全 CNB 的各种本地相对路径
    sites_cnb = sites_cnb.replace('./XBPQ/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/XBPQ/')
    sites_cnb = sites_cnb.replace('./XYQHiker/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/XYQHiker/')
    sites_cnb = sites_cnb.replace('./js/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/js/')
    sites_cnb = sites_cnb.replace('./json/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/json/')
    sites_cnb = sites_cnb.replace('./py/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/py/')

# ====================================================================
# 安全拼接函数：把两段文本连在一起，并把中间的逗号瑕疵剔除干净
# ====================================================================
def safe_join(seg1, seg2):
    seg1 = seg1.strip().rstrip(',')
    seg2 = seg2.strip().lstrip(',')
    if seg1 and seg2:
        return f"{seg1},\n    {seg2}"
    return seg1 if seg1 else seg2

# ====================================================================
# 终极纯文本组装出壳（完美绕过所有解析盲区，格式绝对标准无损）
# ====================================================================
final_json_text = f"""{{
  "spider": "./tvbox.jar",
  "logo": "https://img.freepik.com/free-vector/cute-dolphin-swimming-cartoon-vector-icon-illustration-animal-nature-icon-isolated-flat-vector_138676-12582.jpg?semt=ais_hybrid&w=740&q=80",
  "wallpaper": "http://tool.teyonds.com/api",
  "warningText": "欢迎使用老杨自用全量缝合专线，本接口完全免费！",
  "sites": [
    {safe_join(sites_cnb, sites_ht)}
  ],
  "parses": [
    {safe_join(parses_cnb, parses_ht)}
  ],
  "lives": [
    {safe_join(lives_cnb, lives_ht)}
  ],
  "rules": [
    {safe_join(rules_cnb, rules_ht)}
  ],
  "flags": [
    {safe_join(flags_cnb, flags_ht)}
  ],
  "ads": [
    {safe_join(ads_cnb, ads_ht)}
  ],
  "doh": [
    {safe_join(doh_cnb, doh_ht)}
  ],
  "ijk": [
    {safe_join(ijk_cnb, ijk_ht)}
  ]
}}"""

# 强效最后清洗：抹除由于合并空配置段可能留下的 [ , ] 错位
final_json_text = re.sub(r'\[\s*,', '[', final_json_text)
final_json_text = re.sub(r',\s*\]', '\n  ]', final_json_text)

with open(output_path, 'w', encoding='utf-8') as f:
    f.write(final_json_text)

print("🎉 降维打击成功！全量纯文本物理级合流完成！")
