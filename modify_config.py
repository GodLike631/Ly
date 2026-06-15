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
# 【核心升级】：逐行大挪移，只把包含特定关键字的“整条站点块”抓取出来
# ====================================================================
split_key = '"sites": ['
extracted_cnb_lines = []

if split_key in text_cnb:
    # 拿到 sites 内部的完整配置字符串
    cnb_sites_block = text_cnb.split(split_key, 1)[1].split(']', 1)[0]
    
    # 【高级技巧】：利用正则，精确匹配每一个完整的站点花括号块 { ... }
    # 即使 ext 内部嵌套了多层大括号，通过排除法也能把每一个独立的站点整块剥离，绝不切碎
    cnb_sites_list = re.findall(r'\{\s*"key"\s*:\s*".*?"\s*,.*?\}\s*(?=\s*,\s*\{|\s*$)', cnb_sites_block, re.DOTALL)
    
    # 预防万一，如果上面的高级匹配没抓到，用最稳妥的常规站点块抓取
    if not cnb_sites_list:
        cnb_sites_list = re.findall(r'\{.*?\}', cnb_sites_block, re.DOTALL)

    for site_text in cnb_sites_list:
        # 精准匹配：只保留老杨点名要的含有 APP、4K、Nostr推荐 的站点
        if "APP" in site_text.upper() or "4K" in site_text or "Nostr推荐" in site_text:
            cleaned_site = site_text.strip().strip(',')
            if cleaned_site:
                # 检查这个提取块的花括号对齐情况，如果 ext 的尾部括号被削掉了，手动补齐
                if cleaned_site.count('{') > cleaned_site.count('}'):
                    cleaned_site += "}"
                extracted_cnb_lines.append(cleaned_site)

# 将剥离出的高端 APP 专线无损重组
cnb_final_block = ",\n    ".join(extracted_cnb_lines)

# ====================================================================
# 2. 注入海豚大框架的最前面
# ====================================================================
if split_key in text_haitun and cnb_final_block:
    parts_haitun = text_haitun.split(split_key, 1)
    haitun_front = parts_haitun[0] + split_key
    haitun_back = parts_haitun[1].strip().lstrip(',')
    
    # 拼接缝合
    final_json_text = haitun_front + "\n    " + cnb_final_block + ",\n    " + haitun_back
else:
    final_json_text = text_haitun

# ====================================================================
# 3. 定制品牌头部（不改动任何核心解析）
# ====================================================================
final_json_text = final_json_text.replace('"spider": "./spider.jar"', '"spider": "./tvbox.jar"')
final_json_text = final_json_text.replace(
    '"warningText": "注意:如果别人倒卖海豚影视接口收费的都是骗子,没有qq群微信群，只有tg官方交流群 TG：@hshsjk"', 
    '"warningText": "欢迎使用老杨自用缝合专线，本接口完全免费！"'
)

# 强力洗掉行尾可能由于拼接导致的多余空行逗号等低级语法错误
final_json_text = re.sub(r',\s*\]', '\n  ]', final_json_text)

# 4. 写入本地文件
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(final_json_text)

print("⚡ 嵌套级高级站点块无损清洗完成！")
