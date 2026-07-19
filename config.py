# -*- coding: utf-8 -*-
"""
蝴蝶影视 缝合矩阵 - 核心配置文件
"""
from pathlib import Path

# ====================================================================
# 🌐 【一、全局核心路径与网络代理配置区】
# ====================================================================
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "datas"

CNB_PATH = DATA_DIR / "cnb.json"
HAITUN_PATH = DATA_DIR / "haitun.json"
LZ_PATH = DATA_DIR / "lz.json"

LOCK_FILE_PATH = DATA_DIR / "控制开关.txt"
TRACKER_PATH = DATA_DIR / "最新接口文件名.txt"

GITHUB_PROXY = ""  # 蝴蝶影视当前为空
DEFAULT_LOGO_URL = "https://img.naixiai.cn/2026/06/18/IMG_6638.jpeg"

# ====================================================================
# 🚫 【二、双版本过滤依据、广告拦截与恶意杂质直接清洗区】
# ====================================================================
BLOCK_KEYWORDS = ["羊壳", "弹幕", "不可用"]
UPSTREAM_DIRTY_WORDS = ['🐬', '海豚影视', '海豚', '完全免费，如有收费的都是骗子', '交流群 TG：@hshsjk9']
AD_HOSTS_LIST = ["vip.wwgz.cn", "lziplayer.com", "m3u8.apibdzy.com", "cj.ffzyapi.com", "api.hbzyapi.com"]

# 1. 纯净版分流依据（新增欧美过滤）
NSFW_KEYWORDS = ["🔞", "福利", "探花", "约炮", "色播", "av", "爆料", "欧美", "蜜桃"]
# 2. 上游全线杂质强力清洗
BLOCK_MALICIOUS_KEYWORDS = ["日本女优", "日本女友"]

# ====================================================================
# 👑 【三、老杨专属品牌：引流后缀、自定义替换与视觉定制区】
# ====================================================================
MY_QQ_GROUP = "532637640"
MY_PROMO_CHANNEL = "@huliys9"
MY_TG_SUFFIX = "｜Tg：@huliys9"
LOGO_PREFIX = "🦋"

WALLPAPER_FULL = "https://img.naixiai.cn/2026/wallpapers/full_vip.jpg"
WALLPAPER_CLEAN = "https://img.naixiai.cn/2026/wallpapers/home_clean.jpg"

HOT_VIDEO_KEY = "热播影视"
HOT_VIDEO_SITE_NAME = f"🦋热播 • APP｜此接口非原创，合并自海豚佬 and 鱼佬接口，感谢两位大佬的付出，如有侵权，联系删除｜{MY_TG_SUFFIX.strip('｜')}"

MY_NAME_REPLACEMENTS = {
    # 示例: "原词": "目标新词",
}

# ====================================================================
# 🔒 【四、双版本输出控制与“金蝉脱壳”过期大轰炸配置区】
# ====================================================================
BASE_OUTPUT_FULL = "蝴蝶影视全量版"
BASE_OUTPUT_CLEAN = "蝴蝶影视纯净版"

TRAP_NOTICE_TEXT = f"⚠️ 警告：关注Tg频道（{MY_PROMO_CHANNEL}）获取最新接口密码\n\n当前专线已过期断流！老链接已彻底作废！"
TRAP_WARNING_TEXT = f"👑 特别提示：关注Tg频道（{MY_PROMO_CHANNEL}）获取最新接口"
TRAP_SITE_NAME_1 = f"🚨 ⚠️ 警告：关注Tg频道（{MY_PROMO_CHANNEL}）获取最新接口密码\n\n当前专线已过期断流！老链接已彻底作废！🚨 当前专线密码已过期断流！"
TRAP_SITE_NAME_2 = f"🚨 ⚠️ 警告：关注Tg频道（{MY_PROMO_CHANNEL}）获取最新接口密码\n\n当前专线已过期断流！老链接已彻底作废！"
TRAP_LIVE_GROUP = "🚨 接口过期断流 ｜ 提示"
TRAP_LIVE_CHANNEL = f"👉 线路已过期 ➡️ 关注Tg频道（{MY_PROMO_CHANNEL}）获取最新接口密码\n\n当前专线已过期断流！老链接已彻底作废！"

# ====================================================================
# 📡 【五、客户端通知弹窗与 DOH/JS 注入高级规则配置区】
# ====================================================================
THANKS_WARNING = f"\n\n👑 🚨 重要提示：本接口密码不定期全自动更换！如果遇到失效或断流，请及时回 Telegram 频道（{MY_PROMO_CHANNEL}）获取当前最新密码!"
WELCOME_NOTICE_FULL = "👑 欢迎使用【蝴蝶影视粉丝专属全量专线】！本接口由蝴蝶影视结合多方大底包无损重排而成，干净流畅.🚨 重要提示：本接口密码不定期全自动更换！"
WELCOME_NOTICE_CLEAN = "🏡 欢迎使用【蝴蝶影视专属绿色客厅专线】！本接口已全面过滤敏感、擦边和福利内容，全家老少看电视更安全、更绿色！"

ALI_DOH_CONFIG = {"name": "AliDNS", "url": "https://dns.alidns.com/dns-query", "ips": ["223.5.5.5", "223.6.6.6"]}

CUSTOM_AD_BLOCK_JS = [
    "console.log('蝴蝶影视 WebView 去广告模块启动');",
    "window.addEventListener('DOMContentLoaded', function() {",
    "   document.querySelectorAll('video').forEach(v => { v.muted = true; v.play().catch(e=>{}); });",
    "   Function.prototype.__constructor__ = Function.prototype.constructor;",
    "   Function.prototype.constructor = function() { if (arguments && typeof arguments[0] === 'string' && arguments[0].includes('debugger')) { return function(){}; } return Function.prototype.__constructor__.apply(this, arguments); };",
    "});",
    "setInterval(() => { let selectors = ['.adv-class', '.pop-banner', '#notice-modal', '[id*=\"partner\"]', '[class*=\"baidu\"]', 'iframe[src*=\"game\"]', 'iframe[src*=\"bet\"]', '#pop-ad', '.sidebar-ads', 'a[href*=\"999\"]']; selectors.forEach(sel => { document.querySelectorAll(sel).forEach(el => el.remove()); }); }, 400);"
]

PATH_REPLACEMENTS = {
    './spider.jar': 'https://cnb.cool/fish2018/xs/-/git/raw/main/spider.jar',
    './XBPQ/': 'https://cnb.cool/fish2018/xs/-/git/raw/main/XBPQ/',
    './XYQHiker/': 'https://cnb.cool/fish2018/xs/-/git/raw/main/XYQHiker/',
    './js/': 'https://cnb.cool/fish2018/xs/-/git/raw/main/js/',
    './json/': 'https://cnb.cool/fish2018/xs/-/git/raw/main/json/',
    './py/': 'https://cnb.cool/fish2018/xs/-/git/raw/main/py/',
    'http://127.0.0.1:9978/file/TVBox/logo.png': DEFAULT_LOGO_URL
}

# 🎯 【TG推送核心配置盘】
TG_MAX_DISPLAY = 15

# 🔑 密码锁变更时的蝴蝶影视大通知
TG_PWD_MSG_TEMPLATE = (
    "🔔 *蝴蝶影视全量版 · 全新硬核双通道密码锁发布* 🔔\n\n"
    "📅 *生效时间*：`{current_time}` (北京时间)\n"
    "🔑 *全新专线密锁*：`{current_token}`\n\n"
    "🚀 *重要提示*：\n密码锁已成功交替！旧接口已全线开启【金蝉脱壳】大轰炸，老链接彻底作废，请及时复制下方对应通道的最新链接！\n\n"
    "🔞 *最新【蝴蝶影视全量版】矩阵订阅*：\n`{full_sub_url}`\n\n"
    "🏡 *最新【蝴蝶影视纯净版】客厅订阅*：\n`{clean_sub_url}`\n\n"
    f"👑 矩阵连接已在后台全自动换锁，请及时前往电视端更新。若电视端遇到断流请尝试重启软件或前往TG频道（{MY_PROMO_CHANNEL}）获取支持！"
)

# 📝 日常更新（Diff变动）时的通知
TG_UPDATE_MSG_TEMPLATE = (
    "🔔 *蝴蝶影视全量版 缝合矩阵接口变更通知* 🔔\n\n"
    "📅 *更新时间*：{current_time} (北京时间)\n"
    "🚀 *变动说明*：检测到上游数据源更新或手工区调整，双版本配置已全自动编译上链！\n\n"
    "{detail_msg}\n\n"
    "📡 *【 最新多版本订阅矩阵 (点击可自动复制)】*：\n\n"
    "🔞 *1. 蝴蝶影视全量版* (包含全部线路):\n`{full_sub_url}`\n\n"
    "🏡 *2. 蝴蝶影视纯净版* (已自动全面过滤敏感内容):\n`{clean_sub_url}`\n\n"
    f"👑 全量版与纯净版已在后台无缝更新。更新配置即可，若遇到断流请尝试重启软件或及时前往TG频道（{MY_PROMO_CHANNEL}）获取当前最新密码锁！"
)

# ====================================================================
# ✍️ 【通道一：手工点播加线区】
# ====================================================================
MY_CUSTOM_SITES = [
    {
        "key": "山楂影视",
        "name": "山楂影视.py",  
        "type": 3,
        "api": "https://ghfast.top/https://raw.githubusercontent.com/GodLike631/test/refs/heads/main/datas/%E5%B1%B1%E6%A5%82%E5%BD%B1%E8%A7%86.py",
        "searchable": 1,
        "quickSearch": 1
    },
    {
        "key": "红果短剧",
        "name": "红果短剧.py",  
        "type": 3,
        "api": "https://ghfast.top/https://raw.githubusercontent.com/GodLike631/test/refs/heads/main/datas/%E7%BA%A2%E6%9E%9C%E7%9F%AD%E5%89%A7.py",
        "searchable": 1,
        "quickSearch": 1
    }
]

# ====================================================================
# 📺 【通道二：手工直播加线区】
# ====================================================================
MY_CUSTOM_LIVES = [
    {
        "name": f"乡村电视 {MY_TG_SUFFIX}",
        "type": 0,
        "playerType": 2,
        "ua": "okhttp/5.3.2",
        "url": "https://gh-proxy.com/https://raw.githubusercontent.com/GodLike631/test/refs/heads/main/datas/%E4%B9%A1%E6%9D%91%E7%94%B5%E8%A7%86.txt"
    },
    {
      "name": f"锋云直播{MY_TG_SUFFIX}",
      "type": 3,
      "url": "https://gh-proxy.org/https://raw.githubusercontent.com/807080747/zv/refs/heads/main/suale.txt",
      "ua": "okhttp/5.3.2",
      "timeout": 10,
      "playerType": 2
    },
    {
        "name": f"最新电影{MY_TG_SUFFIX}",
        "type": 0,
        "ua": "okhttp/5.3.2",
        "url": "https://ghfast.top/https://raw.githubusercontent.com/GodLike631/Ly_18/refs/heads/main/datas/%E6%9C%80%E6%96%B0%E7%94%B5%E5%BD%B1.m3u"
    },
    {
        "name": "Kimentanm",
        "type": 0,
        "url": "https://ghfast.top/https://raw.githubusercontent.com/Kimentanm/aptv/master/m3u/iptv.m3u",
        "playerType": 2
    },
    {
      "name": f"综合直播{MY_TG_SUFFIX}",
      "type": 0,
      "playerType": 2,
      "url": "https://ghfast.top/https://raw.githubusercontent.com/develop202/migu_video/refs/heads/main/interface.txt",
      "ua": "bingcha/1.1 (mianfeifenxiang) "
    },
    {
        "name": f"央卫TV{MY_TG_SUFFIX}",
        "type": 0,
        "ua": "okhttp/5.3.2",
        "url": "http://47.120.41.246:8025/vip/jar/zb.php"
    },
    {
        "name": f"超稳定流畅{MY_TG_SUFFIX}",
        "type": 0,
        "ua": "okhttp/5.3.2",
        "url": "https://ghfast.top/https://raw.githubusercontent.com/GodLike631/test/refs/heads/main/datas/%E8%B6%85%E7%A8%B3%E5%AE%9A%E6%B5%81%E7%95%85.txt"
    },
    {
        "name": f"国产直播🔞{MY_TG_SUFFIX}",
        "type": 0,
        "ua": "okhttp/5.3.2",
        "url": "https://ghfast.top/https://raw.githubusercontent.com/Ameria22/TV/refs/heads/main/data/01%E5%9B%BD%E4%BA%A7%E7%9B%B4%E6%92%AD_20260417_024507.m3u"
    },
    {
        "name": f"国产精品🔞{MY_TG_SUFFIX}",
        "type": 0,
        "ua": "okhttp/5.3.2",
        "url": "https://ghfast.top/https://raw.githubusercontent.com/Ameria22/TV/refs/heads/main/data/01%E5%9B%BD%E4%BA%A7%E7%B2%BE%E5%93%81_20260417_024507.m3u"
    },
    {
        "name": f"4K福利🔞{MY_TG_SUFFIX}",
        "type": 0,
        "ua": "okhttp/5.3.2",
        "url": "https://ghfast.top/https://raw.githubusercontent.com/Ameria22/TV/refs/heads/main/data/4k%E7%A6%8F%E5%88%A9.m3u"
    },
    {
        "name": f"探花🔞{MY_TG_SUFFIX}",
        "type": 0,
        "ua": "okhttp/5.3.2",
        "url": "https://raw.githubusercontent.com/Ameria22/TV/refs/heads/main/data/01%E6%8E%A2%E8%8A%B1%E7%BA%A6%E7%82%AE_20260417_024507.m3u"
    },
    {
        "name": f"咪咕{MY_TG_SUFFIX}",
        "type": 0,
        "ua": "okhttp/5.3.2",
        "url": "https://develop202.github.io/migu_video/interface.txt"
    },
    {
      "name": f"Gather「IPTV」{MY_TG_SUFFIX}",
      "type": 3,
      "url": "https://iptv.yang-1989.xyz/playlist.m3u",
      "epg":"https://material.yang-1989.xyz/epg.xml.gz",
      "ua": "okhttp/5.3.2",
      "timeout": 10,
      "playerType": 2
    },
    {
      "name": f"Live「直播」{MY_TG_SUFFIX}",
      "type": 3,
      "url": "https://live.yang-1989.eu.org/Live.m3u",
      "ua": "okhttp/5.3.2",
      "timeout": 10,
      "playerType": 2
    },
    {
      "name": f"myTV「香港」{MY_TG_SUFFIX}",
      "type": 3,
      "url": "https://iptv.yang-1989.xyz/myTV/playlist.m3u",
      "epg":"https://material.yang-1989.xyz/epg.xml.gz",
      "ua": "okhttp/5.3.2",
      "timeout": 10,
      "playerType": 2
    },
]

