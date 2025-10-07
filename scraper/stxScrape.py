from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

from helper.utils import delete_existing_file, write_append, read_json
from helper.selTools import get_title, next_page
from CONSTANTS import LOCAL_JSON_PATH, OUTPUT_DIR, CLEANED_DIR

import time

URL = read_json(LOCAL_JSON_PATH, "stx")["url"]
OUTPUT_PATH = f"{OUTPUT_DIR}/stx_output.txt"

if __name__ == "__main__":
    # ---- Initialize driver ---
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Enable headless mode
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 25)
    driver.get(URL)

    i = 1
    while True:
        try:
            time.sleep(0.6)
            book_content_element = driver.find_element(By.CSS_SELECTOR, "#BookContent")
            # Get the text inside the #BookContent element
            text = book_content_element.text
            write_append(text, OUTPUT_PATH)

            next_page(driver, By.PARTIAL_LINK_TEXT, "下壹頁")
            print(f"Page {i}")
            i += 1
            # c -= 1
        except Exception as e:
            print("Ended at page", i)
            break
    driver.quit()
