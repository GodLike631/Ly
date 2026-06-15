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
# 1. 物理提取海豚源里的 sites（视频站）和 lives（直播源）内部的纯文本
# ====================================================================
def get_array_inner_text(content, key):
    split_key = f'"{key}": ['
    if split_key not in content:
        return ""
    after_key = content.split(split_key, 1)[1]
    if '],' in after_key:
        inner_text = after_key.split('],', 1)[0]
    else:
        inner_text = after_key.split(']', 1)[0]
    return inner_text.strip()

haitun_sites_text = get_array_inner_text(text_haitun, "sites")
haitun_lives_text = get_array_inner_text(text_haitun, "lives")

# ====================================================================
# 2. 逆向注入：把海豚的内容，无缝贴进 CNB 对应的数组最前面
# ====================================================================
final_json_text = text_cnb

# 注入视频站点
if haitun_sites_text and '"sites": [' in final_json_text:
    haitun_sites_text = haitun_sites_text.rstrip(',')
    final_json_text = final_json_text.replace('"sites": [', f'"sites": [\n    {haitun_sites_text},\n    ', 1)

# 注入直播源
if haitun_lives_text and '"lives": [' in final_json_text:
    haitun_lives_text = haitun_lives_text.rstrip(',')
    final_json_text = final_json_text.replace('"lives": [', f'"lives": [\n    {haitun_lives_text},\n    ', 1)

# ====================================================================
# 【全方位无死角路径清洗手术】：
# 必须彻底斩断所有相对路径的隐患，不管是带有 "./" 的、还是漏掉的，
# 全部死死地锁定到 CNB 的官方网络绝对路径上！
# ====================================================================
# 1. 核心蜘蛛包无脑物理替换
final_json_text = final_json_text.replace('"./spider.jar"', '"https://cnb.cool/fish2018/xs/-/git/raw/main/spider.jar"')
final_json_text = final_json_text.replace('"/spider.jar"', '"https://cnb.cool/fish2018/xs/-/git/raw/main/spider.jar"')
final_json_text = final_json_text.replace(' "spider.jar"', '"https://cnb.cool/fish2018/xs/-/git/raw/main/spider.jar"')

# 2. 各种相对路径子文件夹，批量地毯式轰炸替换
final_json_text = final_json_text.replace('./XBPQ/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/XBPQ/')
final_json_text = final_json_text.replace('./XYQHiker/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/XYQHiker/')
final_json_text = final_json_text.replace('./js/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/js/')
final_json_text = final_json_text.replace('./json/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/json/')
final_json_text = final_json_text.replace('./py/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/py/')

# ====================================================================
# 3. 定制老杨自用全量缝合专线品牌头部
# ====================================================================
final_json_text = final_json_text.replace('"warningText": "欢迎使用鱼儿自用缝合专线，完全免费！"', '"warningText": "欢迎使用老杨自用全量缝合专线，本接口完全免费！"')

# 强力消除尾部符号瑕疵
final_json_text = re.sub(r'\[\s*,', '[', final_json_text)
final_json_text = re.sub(r',\s*\]', '\n  ]', final_json_text)

# 写入本地文件存盘
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(final_json_text)

print("🚀 【全覆盖无死角清洗版】合流成功，相对路径隐患已全部扫除！")
