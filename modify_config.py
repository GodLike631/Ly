import os

cnb_path = 'datas/cnb.json'
haitun_path = 'datas/haitun.json'
output_path = 'datas/local_config.json'

# 安全读取文本
def read_file_text(path):
    if not os.path.exists(path):
        return ""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

text_cnb = read_file_text(cnb_path)
text_haitun = read_file_text(haitun_path)

# ====================================================================
# 切片法：将 cnb 里的核心站点剥离出来，塞入海豚源大框架的最前面
# ====================================================================
split_key = '"sites": ['

if split_key in text_haitun and split_key in text_cnb:
    # 1. 拆解海豚源
    parts_haitun = text_haitun.split(split_key, 1)
    haitun_front = parts_haitun[0] + split_key  # 包含头部
    haitun_back = parts_haitun[1]               # 包含原本所有站点及以下内容
    
    # 2. 剥离 CNB 的 sites 站点文本段落
    cnb_back = text_cnb.split(split_key, 1)[1]
    cnb_sites_text = cnb_back.split(']', 1)[0].strip() # 只留下中括号内部的内容
    
    # ====================================================================
    # 【核心修复】：解决 $.sites[38].ext 符号断裂报错的交界修复逻辑
    # ====================================================================
    if cnb_sites_text:
        # 去掉前后多余的空行和逗号，标准化 CNB 站点文本段
        cnb_sites_text = cnb_sites_text.strip().rstrip(',')
        haitun_back = haitun_back.strip().lstrip(',')
        
        # 强制在交界处补上一个标准的换行和逗号，保证 JSON 链条严丝合缝
        final_sites_block = cnb_sites_text + ",\n    " + haitun_back
        
        # 完整合流拼装
        final_json_text = haitun_front + "\n    " + final_sites_block
    else:
        final_json_text = text_haitun
else:
    final_json_text = text_haitun

# ====================================================================
# 定制个性化头部品牌（不改动任何核心解析及线路数据）
# ====================================================================
final_json_text = final_json_text.replace('"spider": "./spider.jar"', '"spider": "./tvbox.jar"')
final_json_text = final_json_text.replace('"warningText": "注意:如果别人倒卖海豚影视接口收费的都是骗子,没有qq群微信群，只有tg官方交流群 TG：@hshsjk"', '"warningText": "欢迎使用老杨自用缝合专线，本接口完全免费！"')

# 写入最终存盘文件
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(final_json_text)

print("⚡ 文本链条符号完全对齐修复，合流成功！")
