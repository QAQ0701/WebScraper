from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC

from helper.utils import delete_existing_file, write_append, clean_txt, read_json
from CONSTANTS import LOCAL_JSON_PATH, OUTPUT_DIR, CLEANED_DIR

import chardet
import time
import requests
import os

URL = read_json(LOCAL_JSON_PATH, "3322")["url"]
OUTPUT_PATH = f"{OUTPUT_DIR}/3322.txt"
FILTER = [
    "上一章",
    "下一章",
    "返回目录",
    "加入书签",
]


def write_append(text, filename):
    try:
        # Save the information to a text file
        with open(filename, "a", encoding="utf-8") as output_file:
            output_file.write(text)
            # output_file.write(text_content)
        # print(f"saved to {OUTPUT_PATH}.")
    except:
        print("Failed to save into txt")


if __name__ == "__main__":
    delete_existing_file(OUTPUT_PATH)

    # ---- Initialize driver ---
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Enable headless mode
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 25)
    driver.get(URL)

    cleaned_file = f"{CLEANED_DIR}/3322_cleaned.txt"

    i = 1

    try:
        while True:
            time.sleep(0.2)
            book_content_element = driver.find_element(By.ID, "novelcontent")
            # Get the text inside the #BookContent element
            text = book_content_element.text
            write_append(text, OUTPUT_PATH)

            next_page_link = driver.find_element(By.XPATH, "//a[text()='下一章']")
            driver.execute_script("arguments[0].scrollIntoView();", next_page_link)
            next_page_link.click()
            print(f"Page {i}")
            time.sleep(0.5)
            i += 1

    except:
        print("ended")

    clean_txt(OUTPUT_PATH, cleaned_file, FILTER)
