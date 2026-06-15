import json
import os
import re

cnb_path = 'datas/cnb.json'
haitun_path = 'datas/haitun.json'
output_path = 'datas/local_config.json'

# 强力容错读取器：能把各种行尾多逗号、不规范的多余空行强行掰正，并转成 Python 的数据对象
def load_file_to_object(path):
    if not os.path.exists(path):
        print(f"❌ 错误：找不到文件 {path}")
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 彻底剃掉全线注释（// 和 /* */）
    content = re.sub(r'//.*', '', content)
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    
    # 用 eval 强行降维打击，无视一切末尾多出逗号等低级 JSON 格式错误
    try:
        if '{' in content and '}' in content:
            content = content[content.find('{'):content.rfind('}')+1]
        return eval(content, {"true": True, "false": False, "null": None})
    except Exception as e:
        print(f"❌ 解析 {path} 失败: {e}")
        return {}

print("🔄 开始全量加载并融合两条上游线路数据...")
data_cnb = load_file_to_object(cnb_path)
data_haitun = load_file_to_object(haitun_path)

if not data_haitun:
    print("❌ 致命错误：海豚源未能成功硬解，请检查文件是否存在！")
    exit(1)

# ====================================================================
# 核心大挪移：由于海豚源是大框架，我们直接将 CNB 的 sites（视频站）提取出来，
# 塞进海豚源大框架的 sites 列表最前面！这样做能保证所有的规则、直播、解析绝不漏掉。
# ====================================================================

cnb_sites = data_cnb.get('sites', []) if isinstance(data_cnb.get('sites'), list) else []
haitun_sites = data_haitun.get('sites', []) if isinstance(data_haitun.get('sites'), list) else []

# 建立全局视频站 key 去重集合，保证两个源合并后，相同的站不会重复出现
seen_keys = set()
merged_sites = []

# 1. 优先塞入 CNB 的全部核心站点[span_1](start_span)[span_1](end_span)
for site in cnb_sites:
    key = site.get('key')
    if key and key not in seen_keys:
        seen_keys.add(key)
        merged_sites.append(site)

# 2. 紧接着跟上海豚源的所有站点[span_2](start_span)[span_2](end_span)
for site in haitun_sites:
    key = site.get('key')
    if key and key not in seen_keys:
        seen_keys.add(key)
        merged_sites.append(site)

# 将提纯合流后的全新站点列表，写回到海豚大配置里
data_haitun['sites'] = merged_sites

# ====================================================================
# 核心微调：将最上方的防倒卖提示与公告切掉，定制成你自己的专属品牌
# ====================================================================
data_haitun['spider'] = "./tvbox.jar"
data_haitun['warningText'] = "欢迎使用老杨自用缝合专线，本接口完全免费！"

# ====================================================================
# 最终盘存：调用大厂级别的标准 json.dump，它在写出文件时，
# 会自动将内存里的数据转换成绝对规范、绝不漏掉或多出任何逗号的标准 JSON[span_3](start_span)[span_3](end_span)
# ====================================================================
with open(output_path, 'w', encoding='utf-8') as f:
    # ensure_ascii=False 确保中文和 🐬 🔞 这些复杂字符绝不产生乱码转义[span_4](start_span)[span_4](end_span)
    # indent=2 保证缩进漂亮，蜂蜜影视和电视盒子 100% 能够完美读取加载[span_5](start_span)[span_5](end_span)
    json.dump(data_haitun, f, ensure_ascii=False, indent=2)

print(f"🎉 终极无缝合流成功！总合并站点总数：{len(data_haitun['sites'])} 个")
