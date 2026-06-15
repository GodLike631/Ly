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
# 核心技巧：无脑提取海豚源里的 sites（视频站）和 lives（直播源）内部的纯文本
# ====================================================================
def get_array_inner_text(content, key):
    split_key = f'"{key}": ['
    if split_key not in content:
        return ""
    after_key = content.split(split_key, 1)[1]
    # 影视接口数组一般以 "],\n" 或 "]\n" 结束，直接截取中括号内部
    if '],' in after_key:
        inner_text = after_key.split('],', 1)[0]
    else:
        inner_text = after_key.split(']', 1)[0]
    return inner_text.strip()

haitun_sites_text = get_array_inner_text(text_haitun, "sites")
haitun_lives_text = get_array_inner_text(text_haitun, "lives")

# ====================================================================
# 逆向注入：把海豚的内容，无缝贴进 CNB 对应的数组最前面
# ====================================================================
final_json_text = text_cnb

# 1. 注入视频站点
if haitun_sites_text and '"sites": [' in final_json_text:
    haitun_sites_text = haitun_sites_text.rstrip(',')
    # 在 CNB 的 '"sites": [' 后面立刻追加海豚的站点，并补上逗号换行
    final_json_text = final_json_text.replace('"sites": [', f'"sites": [\n    {haitun_sites_text},\n    ', 1)

# 2. 注入直播源
if haitun_lives_text and '"lives": [' in final_json_text:
    haitun_lives_text = haitun_lives_text.rstrip(',')
    # 在 CNB 的 '"lives": [' 后面立刻追加海豚的直播，并补上逗号换行
    final_json_text = final_json_text.replace('"lives": [', f'"lives": [\n    {haitun_lives_text},\n    ', 1)

# ====================================================================
# 定制老杨自用专属品牌头部
# ====================================================================
# 由于使用了 CNB 做底座，它的全局 spider 默认就是 ./spider.jar，完全不用改动，APP线路天生复活！
final_json_text = final_json_text.replace('"warningText": "欢迎使用鱼儿自用缝合专线，完全免费！"', '"warningText": "欢迎使用老杨自用缝合专线，本接口完全免费！"')

# 强力消除尾部符号瑕疵（清洗掉可能残留下来的多余逗号）
final_json_text = re.sub(r'\[\s*,', '[', final_json_text)
final_json_text = re.sub(r',\s*\]', '\n  ]', final_json_text)

# 写入本地 local_config.json 存盘
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(final_json_text)

print("🎉 逆向思维大胜利！以 CNB 为底座全量缝合成功！")
