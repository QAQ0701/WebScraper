from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC

from helper.utils import delete_existing_file, write_append, clean_txt, read_json
from helper.selTools import multi_next_page

from CONSTANTS import LOCAL_JSON_PATH, OUTPUT_DIR, CLEANED_DIR

import time


URL = read_json(LOCAL_JSON_PATH, "ranwen")["url"]
OUTPUT_PATH = f"{OUTPUT_DIR}/rw.txt"
CLEANED_PATH = f"{CLEANED_DIR}/ranwen_cleaned.txt"
FILTER = [
    "本章已閱讀完畢(請點擊下一章繼續閱讀!)",
]

if __name__ == "__main__":

    delete_existing_file(OUTPUT_PATH)
    delete_existing_file(CLEANED_PATH)

    # c = 5
    # chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Enable headless mode
    # driver = webdriver.Chrome(options=chrome_options)
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 25)
    driver.get(URL)

    i = 1
    try:
        while True:
            time.sleep(0.3)

            book_content_element = driver.find_element(By.ID, "read_conent_box")
            # Get the text inside the #BookContent element
            text = book_content_element.text

            remove_after_match = "作者有話要說"

            # Split the text at the matched string
            result = text.split(remove_after_match)[0]

            write_append(result + "\n", OUTPUT_PATH)
            print(f"Page {i}")
            i += 1

            multi_next_page(
                driver, By.XPATH, "//a[text()='下一頁']", "//a[text()='下一章']"
            )

    except Exception as e:
        print(e)
        print(f"ended")

    clean_txt(OUTPUT_PATH, CLEANED_PATH, FILTER)
