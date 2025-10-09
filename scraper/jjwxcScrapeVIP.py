from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from helper.utils import delete_existing_file, write_append, clean_txt
from helper.selTools import get_title
from jjwxc_helper.jj_helper import (
    ensure_latest_font,
    is_content_loaded,
    decode_VIP,
)
from jjwxc_helper.CONSTANTS_JJ import (
    FONT_PATH,
    GLYPH_DIR,
    MAP_PATH,
    COOKIES_PATH,
    OUTPUT_PATH,
    MATCH_STRINGS,
    DOMAIN,
    MAX_RETRIES,
    LOCAL_JSON_PATH,
    VIP,
    URL,
)
from CONSTANTS import CLEANED_DIR, LOG_PATH
from logger_config import setup_logger

import time
import os
import json
import logging


# ======================================
#            GLOBAL CONFIG
# ======================================
logger = setup_logger()
logger.info("Starting jjwxcScrapeVIP...")


# ======================================
#            HELPER FUNCTIONS
# ======================================
def cleanup():
    driver.quit()
    delete_existing_file(MAP_PATH)


def loadCookies(driver):
    with open(COOKIES_PATH, "r") as file:
        COOKIES = json.load(file)["cookies"]
    for cookie in COOKIES:
        # Ensure cookie has the correct domain
        if "domain" in cookie and "jjwxc.net" in cookie["domain"]:
            try:
                driver.add_cookie(cookie)
                # logging.info(f"Added cookie {cookie.get('name')}")
            except Exception as e:
                logging.info(f"Error adding cookie {cookie.get('name')}: {e}")
        else:
            logging.info(f"Invalid cookie: {cookie}")


# ======================================
#            MAIN SCRAPER
# ======================================
if __name__ == "__main__":
    # --- Initialize driver ---
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  # debug
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    if VIP:
        chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 25)

    if VIP:
        driver.get(DOMAIN)
        loadCookies(driver)
        time.sleep(0.5)
        # Refresh the page to apply cookies
        driver.refresh()
    driver.get(URL)

    # ---  Get Title of Novel ---
    title = get_title(wait, By.CLASS_NAME, "bigtext")
    CLEANED_PATH = f"{CLEANED_DIR}/{title}.txt"
    delete_existing_file(CLEANED_PATH)
    delete_existing_file(OUTPUT_PATH)
    delete_existing_file(FONT_PATH)

    # --- Chapter Count Starting from i ---
    i = 1
    # --- Main Scrape Loop ---
    try:
        while True:
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "novelbody")))
            logging.info(f"\n[Chapter {i}] Processing...")
            # --- Check and update font if changed ---
            if VIP:
                ensure_latest_font(driver)
            # break # debug
            write_append(f"第{i}章 \n", OUTPUT_PATH)
            i += 1
            # --- Get Book Content ---
            # chapNum = driver.find_element(By.TAG_NAME, "h2").text + "\n"
            retries = 0
            text = ""

            while retries < MAX_RETRIES:
                try:
                    if VIP:
                        WebDriverWait(driver, 10, poll_frequency=0.5).until(
                            is_content_loaded
                        )

                    text = driver.find_element(By.CLASS_NAME, "novelbody").text.strip()
                    if text:
                        break  # content loaded successfully
                    else:
                        logging.error("Content not loaded, raising exception...")
                        raise Exception

                except Exception as e:
                    retries += 1
                    logging.info(
                        f"Content not loaded, waiting for 5s ... attempt {retries} ({e})"
                    )
                    logging.info(f"text content: {text}")
                    # driver.refresh()
                    time.sleep(5)

            if not text:
                logging.error("Failed to load content after multiple attempts")
                break

            remove_after_match = "作者有话说"

            # Split the text at the matched string
            result = text.split(remove_after_match)[0]
            output_txt = decode_VIP(result) if VIP else result
            write_append(output_txt + "\n", OUTPUT_PATH)

            # break  # debug
            # --- Go to next page ---
            try:
                next_page_link = driver.find_element(
                    By.XPATH, "//span[@class='bigtext' and text()='下一章→']"
                )
                driver.execute_script("arguments[0].scrollIntoView();", next_page_link)
                next_page_link.click()
                time.sleep(0.8)
            except Exception as e:
                logging.info(f"\n[End] No more chapters found. {e}")
                break
    except Exception as e:
        logging.warning(f"[Error] Scraping ended with: {e}")
    # --- Clean Output ---
    clean_txt(OUTPUT_PATH, CLEANED_PATH, MATCH_STRINGS)  # debug
    cleanup()
