from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC

from helper.utils import delete_existing_file, write_append, clean_txt, read_json
from helper.selTools import get_title, next_page
from CONSTANTS import LOCAL_JSON_PATH, OUTPUT_DIR, CLEANED_DIR

import time

# --- CONSTANTS ---
URL = read_json(LOCAL_JSON_PATH, "weifeng")["url"]
OUTPUT_PATH = f"{OUTPUT_DIR}/weifeng.txt"
FILTER = [
    "↑返回頂部↑",
]

if __name__ == "__main__":
    delete_existing_file(OUTPUT_PATH)
    # ---- Initialize driver ---
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Enable headless mode
    # driver = webdriver.Chrome(options=chrome_options)
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 25)
    driver.get(URL)

    book_title = get_title(wait, By.TAG_NAME, "h2")
    CLEANED_PATH = f"{CLEANED_DIR}/{book_title}.txt"

    i = 1
    try:
        while True:
            time.sleep(0.2)
            book_content_element = driver.find_element(By.ID, "rtext")
            # Get the text inside the #BookContent element
            text = book_content_element.text
            write_append(text + "\n", OUTPUT_PATH)

            next_page(driver, By.ID, "linkNext")
            print(f"Page {i}")
            time.sleep(0.5)
            i += 1

    except Exception as e:
        print("ended", e)

    # clean_txt(OUTPUT_PATH, CLEANED_PATH, FILTER)
