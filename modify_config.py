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

# ====================================================================
# 1. 提取 CNB 仓库里的【所有】站点（不做任何过滤，全量无损提取）
# ====================================================================
if split_key in text_cnb:
    cnb_sites_block = text_cnb.split(split_key, 1)[1].split(']', 1)[0]
    
    # 精确匹配每一个完整的站点花括号块 { ... }，强力保护 ext 内部嵌套的复杂大括号
    cnb_sites_list = re.findall(r'\{\s*"key"\s*:\s*".*?"\s*,.*?\}\s*(?=\s*,\s*\[|\s*,\s*\{|\s*$)', cnb_sites_block, re.DOTALL)
    if not cnb_sites_list:
        cnb_sites_list = re.findall(r'\{.*?\}', cnb_sites_block, re.DOTALL)

    for site_text in cnb_sites_list:
        cleaned_site = site_text.strip().strip(',')
        if cleaned_site:
            # 自动修复括号闭合瑕疵
            if cleaned_site.count('{') > cleaned_site.count('}'):
                cleaned_site += "}"
            
            # ====================================================================
            # 【全线网络化打通】：由于是全量融合，所有站点的相对路径都必须升级为网络绝对路径
            # ====================================================================
            # 1. 如果站点本身没有指定 jar 爬虫包，强制让它认回 CNB 官方亲生的 spider.jar
            if '"jar"' not in cleaned_site:
                cleaned_site = cleaned_site.replace('{', '{\n      "jar": "https://cnb.cool/fish2018/xs/-/git/raw/main/spider.jar",', 1)
            
            # 2. 批量补全所有相对路径前缀，确保全量线路的子配置文件全线复活
            cleaned_site = cleaned_site.replace('./XBPQ/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/XBPQ/')
            cleaned_site = cleaned_site.replace('./XYQHiker/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/XYQHiker/')
            cleaned_site = cleaned_site.replace('./js/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/js/')
            cleaned_site = cleaned_site.replace('./json/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/json/')
            cleaned_site = cleaned_site.replace('./py/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/py/')
            
            extracted_cnb_lines.append(cleaned_site)

# 重组 CNB 的全量站点板块
cnb_final_block = ",\n    ".join(extracted_cnb_lines)

# ====================================================================
# 2. 注入海豚大配置框架的最前面（让海豚的直播、解析、核心规则安全打底）
# ====================================================================
if split_key in text_haitun and cnb_final_block:
    parts_haitun = text_haitun.split(split_key, 1)
    haitun_front = parts_haitun[0] + split_key
    haitun_back = parts_haitun[1].strip().lstrip(',')
    
    # 终极无缝硬缝合
    final_json_text = haitun_front + "\n    " + cnb_final_block + ",\n    " + haitun_back
else:
    final_json_text = text_haitun

# ====================================================================
# 3. 全局品牌定制与规整
# ====================================================================
final_json_text = final_json_text.replace('"spider": "./spider.jar"', '"spider": "./tvbox.jar"')
final_json_text = final_json_text.replace(
    '"warningText": "注意:如果别人倒卖海豚影视接口收费的都是骗子,没有qq群微信群，只有tg官方交流群 TG：@hshsjk"', 
    '"warningText": "欢迎使用老杨自用全量缝合专线，本接口完全免费！"'
)

# 消除合并可能导致的末尾多余逗号瑕疵
final_json_text = re.sub(r',\s*\]', '\n  ]', final_json_text)

# 4. 写入 local_config.json 存盘
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(final_json_text)

print("⚡ 【全量无损融合版】CNB 所有内容已完美并入海豚框架，网络依赖全面打通！")
