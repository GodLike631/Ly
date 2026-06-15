import os

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
# 1. 从 CNB 中精准定向剥离：只保留包含 APP、4K、Nostr推荐 的站点整块
# ====================================================================
split_key = '"sites": ['
extracted_cnb_lines = []

if split_key in text_cnb:
    # 拿到 sites 数组内部的所有文本
    cnb_sites_block = text_cnb.split(split_key, 1)[1].split(']', 1)[0]
    
    # 将文本切成独立的对象字符串（按每个站点的花括号分割）
    # 用正则是为了防止换行符干扰，将每一个 { ... } 站点提取出来
    import re
    cnb_sites_list = re.findall(r'\{.*?\}', cnb_sites_block, re.DOTALL)
    
    for site_text in cnb_sites_list:
        # 精准匹配：只保留含有 APP、4K、Nostr推荐 的站点文本
        if "APP" in site_text.upper() or "4K" in site_text or "Nostr推荐" in site_text:
            # 清理掉前后可能残留的换行和逗号，统一规范化
            cleaned_site = site_text.strip().strip(',')
            if cleaned_site:
                extracted_cnb_lines.append(cleaned_site)

# 将剥离出来的这几条最优质线路，用逗号和换行拼成一个干净的文本块
cnb_final_block = ",\n    ".join(extracted_cnb_lines)

# ====================================================================
# 2. 将剥离出来的文本块，无缝注入到海豚源的最前方
# ====================================================================
if split_key in text_haitun and cnb_final_block:
    parts_haitun = text_haitun.split(split_key, 1)
    haitun_front = parts_haitun[0] + split_key  # 框架前半段
    haitun_back = parts_haitun[1].strip().lstrip(',') # 框架后半段（顺手剃掉开头的多余逗号）
    
    # 终极无缝拼接：前半段 + CNB精确摘取线 + 逗号换行 + 海豚原有全线
    final_json_text = haitun_front + "\n    " + cnb_final_block + ",\n    " + haitun_back
else:
    final_json_text = text_haitun

# ====================================================================
# 3. 定制老杨自用专属品牌头部（不改动任何核心解析及线路数据）
# ====================================================================
final_json_text = final_json_text.replace('"spider": "./spider.jar"', '"spider": "./tvbox.jar"')
final_json_text = final_json_text.replace(
    '"warningText": "注意:如果别人倒卖海豚影视接口收费的都是骗子,没有qq群微信群，只有tg官方交流群 TG：@hshsjk"', 
    '"warningText": "欢迎使用老杨自用缝合专线，本接口完全免费！"'
)

# 彻底洗掉由于拼接可能导致的特殊语法残缺（比如行尾出现 , ] 的低级错误）
final_json_text = re.sub(r',\s*\]', '\n  ]', final_json_text)

# 4. 写入存盘
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(final_json_text)

print("⚡ 精准定向剥离合流完成！")
