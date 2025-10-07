from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from helper.utils import delete_existing_file, write_append, clean_txt, read_json
from CONSTANTS import LOCAL_JSON_PATH, OUTPUT_DIR, CLEANED_DIR
from helper.selTools import get_title, next_page

import time

URL = read_json(LOCAL_JSON_PATH, "52")["url"]
OUTPUT_PATH = f"{OUTPUT_DIR}/52scrapedText.txt"
MATCH_STRINGS = [
    "目录 上一页 下一页 尾页",
    "小贴士：如果觉得52书库不错，记得收藏网址",
    "传送门：排行榜单 | 好书推荐 |",
    "传送门",
    "目录上一页 下一页",
    "目录 下一页 尾页",
    "目录 上一页",
    "小贴士:找看好看得小说，就来52书库呀~www.52shuku.vip",
    "哦豁，小伙伴们如果觉得52书库不错，记得收藏网址",
    "传送门：排行榜单 | 找书指南 |",
    "Tips:看好看的小说，就来52书库呀",
    "52书库",
    "====",
]


if __name__ == "__main__":

    delete_existing_file(OUTPUT_PATH)

    # ---- Initialize driver ---
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Enable headless mode
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 25)
    driver.get(URL)

    # ---- Get the book title ---
    book_title = get_title(wait, By.ID, "nr_title")
    CLEANED_PATH = f"{CLEANED_DIR}/{book_title}.txt"

    i = 1

    try:
        while True:
            time.sleep(0.4)
            book_content_element = wait.until(
                EC.presence_of_element_located((By.ID, "nr1"))
            )
            # book_content_element = driver.find_element(By.ID, "nr1")
            # Get the text inside the #BookContent element
            text = book_content_element.text

            remove_after_match = "作者有话"
            # Split the text at the matched string
            result = text.split(remove_after_match)[0]

            write_append(result + "\n", OUTPUT_PATH)

            next_page(driver, By.XPATH, "//a[text()='下一页']")

            # --increment page # --
            print(f"Page {i}")
            i += 1

    except:
        print("ended")

    clean_txt(OUTPUT_PATH, CLEANED_PATH, MATCH_STRINGS)
