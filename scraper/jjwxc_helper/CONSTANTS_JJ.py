from CONSTANTS import LOCAL_JSON_PATH, OUTPUT_DIR, COOKIES_DIR, LOG_PATH
from helper.utils import read_json

FONT_PATH = "scraper/jjwxc_helper/data/current_font.woff2"
GLYPH_DIR = "scraper/jjwxc_helper/data/jjwxc_glyphs"
MAP_PATH = "scraper/jjwxc_helper/data/map.json"
NETLOG_PATH = "scraper/jjwxc_helper/data/network_logs.json"
LOCAL_JSON_PATH = LOCAL_JSON_PATH
COOKIES_PATH = f"{COOKIES_DIR}/jjwxc_cookies.json"
OUTPUT_PATH = f"{OUTPUT_DIR}/jjwxcVIP.txt"
LOG_PATH = LOG_PATH
MATCH_STRINGS = [
    "[收藏此章节] [免费得晋江币] [投诉]",
    "插入书签",
    "[收藏此章节] [推荐给朋友] [投诉色情有害、数据造假 、原创违规、伪更]",
    "@无限好文，尽在晋江文学城",
]
DOMAIN = "https://www.jjwxc.net"
MAX_RETRIES = 3

json_value = read_json(LOCAL_JSON_PATH, "jjwxc")
if json_value["VIP"] == "false":
    VIP = False
else:
    VIP = True
json_value = read_json(LOCAL_JSON_PATH, "jjwxc")
URL = json_value["url"]