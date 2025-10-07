from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from helper.utils import delete_existing_file, write_append, clean_txt, read_json
from helper.selTools import get_title, next_page
from CONSTANTS import LOCAL_JSON_PATH, OUTPUT_DIR, CLEANED_DIR

import time

URL = read_json(LOCAL_JSON_PATH, "zgzl")["url"]
OUTPUT_PATH = f"{OUTPUT_DIR}/zgzl.txt"
FILTER = [
    "本站無彈出廣告",
    "内容未完，下一页继续阅读",
    "《关闭小说畅读模式体验更好》",
    "【本章阅读完毕，更多请搜索】",
]

if __name__ == "__main__":
    delete_existing_file(OUTPUT_PATH)
    # ---- Initialize driver ---
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Enable headless mode
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 25)
    driver.get(URL)

    container = driver.find_element(By.CLASS_NAME, "nav_name")
    ntitle = container.find_element(By.TAG_NAME, "h1").text
    print(ntitle)
    CLEANED_PATH = f"{CLEANED_DIR}/{ntitle}.txt"

    i = 1
    c = 1
    try:
        while True:
            print(f"Page {i}")
            i += 1
            time.sleep(0.2)
            container = driver.find_element(By.CLASS_NAME, "bookname")
            title = container.find_element(By.TAG_NAME, "h1")

            book_content_element = driver.find_element(By.ID, "content")
            text = book_content_element.text

            remove_after_match = "作者有话"
            # Split the text at the matched string
            result = text.split(remove_after_match)[0]

            if "(1 /" in title.text:
                write_append(f"第{c}章 :{title.text}\n", OUTPUT_PATH)
                c += 1
            write_append(text + "\n", OUTPUT_PATH)

            next_page(driver, By.XPATH, "//a[text()='下一页']")
    except:
        print("ended")

    clean_txt(OUTPUT_PATH, CLEANED_PATH, FILTER)
