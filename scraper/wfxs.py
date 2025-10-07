from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC

from helper.utils import delete_existing_file, write_append, clean_txt, read_json
from helper.selTools import get_title, multi_next_page
from CONSTANTS import LOCAL_JSON_PATH, OUTPUT_DIR, CLEANED_DIR

import time

# --- CONSTANTS ---
URL = read_json(LOCAL_JSON_PATH, "wfxs")["url"]
OUTPUT_PATH = f"{OUTPUT_DIR}/wfxs.txt"
FILTER = [
    "↑返回頂部↑",
    "本章已閱讀完畢(請點擊下一章繼續閱讀!",
    "分享到Facebook",
    "分享到Line",
    "分享到Twitter",
]

if __name__ == "__main__":
    # ---- Initialize driver ---
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 25)
    driver.get(URL)

    elements = driver.find_elements(By.TAG_NAME, "h2")
    if elements:
        book_title = elements[0].text
    else:
        elements = driver.find_elements(By.CLASS_NAME, "book")
        book_title = elements[0].text if elements else "Title not found"
    print(book_title)

    CLEANED_PATH = f"{CLEANED_DIR}/{book_title}.txt"
    delete_existing_file(OUTPUT_PATH)
    delete_existing_file(CLEANED_PATH)

    i = 1
    try:
        while True:
            time.sleep(0.2)
            title = get_title(wait, By.TAG_NAME, "h1")
            if "(1/" in title:
                write_append(f"第{i}章\n", OUTPUT_PATH)
                print(f"CHP {i}")
                i += 1

            try:
                content_id = "content"
                book_content_element = driver.find_element(By.ID, content_id)
            except:
                content_id = "read_conent_box"
                book_content_element = driver.find_element(By.ID, content_id)
                continue
            # Get the text inside the #BookContent element
            text = book_content_element.text
            write_append(text + "\n", OUTPUT_PATH)

            multi_next_page(
                driver, By.XPATH, "//a[text()='下一頁']", "//a[text()='下一章']"
            )
            time.sleep(0.2)

    except Exception as e:
        print("ended", e)

    clean_txt(OUTPUT_PATH, CLEANED_PATH, FILTER)
