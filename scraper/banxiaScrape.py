from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from helper.utils import delete_existing_file, write_append, clean_txt, read_json
from helper.selTools import get_title, next_page
from CONSTANTS import LOCAL_JSON_PATH, OUTPUT_DIR, CLEANED_DIR

import time

json_input = read_json(LOCAL_JSON_PATH, "banxia")
URL = json_input["url"]
OUTPUT_PATH = f"{OUTPUT_DIR}/banxia.txt"
FILTER = [
    "本站無彈出廣告",
]


if __name__ == "__main__":
    delete_existing_file(OUTPUT_PATH)

    # ---- Initialize driver ---
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Enable headless mode
    driver = webdriver.Chrome(options=chrome_options)
    # driver = webdriver.Chrome() #debug use
    wait = WebDriverWait(driver, 25)
    driver.get(URL)

    # ---- Get the book title ---
    novel_title = get_title(wait, By.XPATH, "//a[@rel='category tag']")
    print(novel_title)
    CLEANED_PATH = f"{CLEANED_DIR}/{novel_title}.txt"
    delete_existing_file(CLEANED_PATH)

    # ---- Loop to Get the book content ---
    i = 1
    try:
        while True:
            print(f"Page {i}")
            i += 1
            time.sleep(0.2)

            title = get_title(wait, By.ID, "nr_title")
            write_append(f"{title}\n", OUTPUT_PATH)

            book_content_element = driver.find_element(By.ID, "nr1")
            text = book_content_element.text

            remove_after_match = "作者有话"

            # Split the text at the matched string
            result = text.split(remove_after_match)[0]

            write_append(text + "\n", OUTPUT_PATH)

            next_page(driver, By.ID, "next_url")
    except Exception as e:
        print("ended with " + str(e))

    clean_txt(OUTPUT_PATH, CLEANED_PATH, FILTER)
