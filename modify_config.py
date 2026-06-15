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
        # ====================================================================
        # 【全线硬核接口捕获】：通过底层的 API 核心名字识别，绕过所有特殊竖线干扰
        # ====================================================================
        is_target = False
        
        # 1. 优先捕获你原本点名要的所有 APP 线路和 4K、Nostr 线
        if "APP" in site_text.upper() or "4K" in site_text or "Nostr推荐" in site_text:
            is_target = True
            
        # 2. 扩大范围：通过硬核 API 接口关键字，把动漫、磁力、4K网盘、B站合集、体育、音乐全捞出来
        if not is_target:
            # 这些是 cnb.json 里除了直播和测试外，所有优质线路的底层 api 核心特征
            hardcore_apis = [
                "drpy2", "csp_Wogg", "csp_PanWebShare", "csp_PanAli", "csp_PanQuark", 
                "csp_PanUC", "csp_PanBaidu", "csp_PanSou", "csp_GugeSo", "csp_XiongdiPan", 
                "csp_Baiku", "csp_MiSou", "csp_GuiGui", "csp_HunHePan", "csp_TianYiSou", 
                "csp_QuPanSo", "csp_Kanqiu", "csp_QiutongTY", "csp_GuaziTY", "csp_KafeiTY", 
                "csp_919TY", "csp_Djuu", "csp_Djlh", "csp_QingtingFM", "csp_TingShijie", 
                "csp_AppLY", "csp_Bili", "csp_FirstAid", "csp_JianPian", "csp_Xlys", 
                "csp_QnMp4", "csp_BLSGod", "csp_New6v", "csp_MeijuMi", "csp_Xunlei8", 
                "csp_DyGod", "csp_BiliYS", "csp_SP360"
            ]
            for api in hardcore_apis:
                if api in site_text:
                    is_target = True
                    break

        # 3. 严格拦截：剔除没用的测试线、本地视频线和手机推送通道
        if "Nostr测试" in site_text or "本地｜视频" in site_text or "push_agent" in site_text:
            is_target = False

        if is_target:
            cleaned_site = site_text.strip().strip(',')
            if cleaned_site:
                if cleaned_site.count('{') > cleaned_site.count('}'):
                    cleaned_site += "}"
                
                # ====================================================================
                # 【路径复活手术】：将 CNB 线路的相对路径全部无损升级为官方网络绝对路径
                # ====================================================================
                if '"jar"' not in cleaned_site:
                    cleaned_site = cleaned_site.replace('{', '{\n      "jar": "https://cnb.cool/fish2018/xs/-/git/raw/main/spider.jar",', 1)
                
                cleaned_site = cleaned_site.replace('./XBPQ/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/XBPQ/')
                cleaned_site = cleaned_site.replace('./XYQHiker/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/XYQHiker/')
                cleaned_site = cleaned_site.replace('./js/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/js/')
                cleaned_site = cleaned_site.replace('./json/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/json/')
                cleaned_site = cleaned_site.replace('./py/', 'https://cnb.cool/fish2018/xs/-/git/raw/main/py/')
                
                extracted_cnb_lines.append(cleaned_site)

# 重组所有过滤出来的优质专线文本段
cnb_final_block = ",\n    ".join(extracted_cnb_lines)

# 2. 注入海豚大框架的最前面
if split_key in text_haitun and cnb_final_block:
    parts_haitun = text_haitun.split(split_key, 1)
    haitun_front = parts_haitun[0] + split_key
    haitun_back = parts_haitun[1].strip().lstrip(',')
    
    final_json_text = haitun_front + "\n    " + cnb_final_block + ",\n    " + haitun_back
else:
    final_json_text = text_haitun

# 3. 定制品牌公告
final_json_text = final_json_text.replace('"spider": "./spider.jar"', '"spider": "./tvbox.jar"')
final_json_text = final_json_text.replace(
    '"warningText": "注意:如果别人倒卖海豚影视接口收费的都是骗子,没有qq群微信群，只有tg官方交流群 TG：@hshsjk"', 
    '"warningText": "欢迎使用老杨自用缝合专线，本接口完全免费！"'
)

# 清洗行尾可能由于拼接留下的多余逗号
final_json_text = re.sub(r',\s*\]', '\n  ]', final_json_text)

# 4. 写入本地存盘
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(final_json_text)

print("⚡ 【底层硬核API捕获版】除直播外的全线优质站点已全部复活并入海豚源！")
