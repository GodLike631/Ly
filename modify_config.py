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

split_key = '"sites": ['
extracted_cnb_lines = []

if split_key in text_cnb:
    cnb_sites_block = text_cnb.split(split_key, 1)[1].split(']', 1)[0]
    
    # 精确匹配每一个完整的站点花括号块 { ... }
    cnb_sites_list = re.findall(r'\{\s*"key"\s*:\s*".*?"\s*,.*?\}\s*(?=\s*,\s*\{|\s*$)', cnb_sites_block, re.DOTALL)
    if not cnb_sites_list:
        cnb_sites_list = re.findall(r'\{.*?\}', cnb_sites_block, re.DOTALL)

    for site_text in cnb_sites_list:
        # 只保留含有 APP、4K、Nostr推荐 的站点
        if "APP" in site_text.upper() or "4K" in site_text or "Nostr推荐" in site_text:
            cleaned_site = site_text.strip().strip(',')
            if cleaned_site:
                if cleaned_site.count('{') > cleaned_site.count('}'):
                    cleaned_site += "}"
                
                # ====================================================================
                # 【核心复活手术】：将 CNB APP 线路的底层依赖全部引向 CNB 的官方网络绝对路径
                # ====================================================================
                # 1. 强行让这批 APP 线路认回属于它们的 spider 爬虫文件
                if '"jar"' not in cleaned_site:
                    # 如果站点本身没写 jar，我们在它内部强行插入一条，指向 CNB 官方的 spider.jar 绝对路径
                    cleaned_site = cleaned_site.replace('{', '{\n      "jar": "https://cnb.cool/fish2018/xs/-/git/raw/main/spider.jar",', 1)
                
                # 2. 强行补全相对路径（将 ./XBPQ/ 和 ./XYQHiker/ 替换为官方绝对网络链接）
                cleaned_site = cleaned_site.replace('./XBPQ/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/XBPQ/')
                cleaned_site = cleaned_site.replace('./XYQHiker/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/XYQHiker/')
                cleaned_site = cleaned_site.replace('./js/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/js/')
                cleaned_site = cleaned_site.replace('./json/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/json/')
                cleaned_site = cleaned_site.replace('./py/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/py/')
                
                extracted_cnb_lines.append(cleaned_site)

# 将剥离出且经过“网络打通”的 APP 专线重组
cnb_final_block = ",\n    ".join(extracted_cnb_lines)

# 2. 注入海豚大框架的最前面（保持海豚原本的所有直播、解析和 tvbox.jar 框架不变）
if split_key in text_haitun and cnb_final_block:
    parts_haitun = text_haitun.split(split_key, 1)
    haitun_front = parts_haitun[0] + split_key
    haitun_back = parts_haitun[1].strip().lstrip(',')
    
    final_json_text = haitun_front + "\n    " + cnb_final_block + ",\n    " + haitun_back
else:
    final_json_text = text_haitun

# 3. 定制老杨专属品牌公告
final_json_text = final_json_text.replace('"spider": "./spider.jar"', '"spider": "./tvbox.jar"')
final_json_text = final_json_text.replace(
    '"warningText": "注意:如果别人倒卖海豚影视接口收费的都是骗子,没有qq群微信群，只有tg官方交流群 TG：@hshsjk"', 
    '"warningText": "欢迎使用老杨自用缝合专线，本接口完全免费！"'
)

# 强力消除尾部符号瑕疵
final_json_text = re.sub(r',\s*\]', '\n  ]', final_json_text)

# 4. 写入本地文件
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(final_json_text)

print("⚡ APP线路底层网络依赖打通，全线复活合流完成！")
