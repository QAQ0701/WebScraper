from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from jjwxc_helper.PUAglyph_to_image import render_given_pua_glyphs
from jjwxc_helper.glyphTOunicode import generate_map
from helper.utils import delete_existing_file, write_append, clean_txt, read_json
from helper.selTools import get_title
from jjwxc_helper.jj_helper import (
    load_pua_map,
    extract_pua_chars,
    decode_font,
    ensure_latest_font,
    is_content_loaded,
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
)
from CONSTANTS import CLEANED_DIR

import time
import os
import json


# ======================================
#            GLOBAL CONFIG
# ======================================
json_value = read_json(LOCAL_JSON_PATH, "jjwxc")
URL = json_value["url"]
if json_value["VIP"] == "false":
    VIP = False
else:
    VIP = True


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
                # print(f"Added cookie {cookie.get('name')}")
            except Exception as e:
                print(f"Error adding cookie {cookie.get('name')}: {e}")
        else:
            print(f"Invalid cookie: {cookie}")


# ======================================
#            MAIN SCRAPER
# ======================================
if __name__ == "__main__":
    # --- Initialize driver ---
    chrome_options = Options()
    # chrome_options.add_argument("--headless=new")  # Optional headless
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
            print(f"\n[Chapter {i}] Processing...")
            # --- Check and update font if changed ---
            if VIP:
                ensure_latest_font(driver)

            write_append(f"第{i}章 \n", OUTPUT_PATH)
            i += 1
            # --- Get Book Content ---

            # chapNum = driver.find_element(By.TAG_NAME, "h2").text + "\n"
            retries = 0
            text = ""

            while retries < MAX_RETRIES:
                try:
                    if VIP:
                        # wait.until(
                        #     EC.presence_of_element_located((By.CLASS_NAME, "novelbody"))
                        # )
                        # Wait up to 10 seconds for content
                        WebDriverWait(driver, 10, poll_frequency=0.5).until(
                            is_content_loaded
                        )
                        text = driver.find_element(By.CLASS_NAME, "novelbody").text
                        break  # Success
                    else:
                        text = driver.find_element(By.CLASS_NAME, "novelbody").text
                        break

                except Exception as TimeoutException:
                    retries += 1
                    print(f"Content not loaded, refreshing page... attempt {retries}")
                    driver.refresh()
                    time.sleep(2)  # Give the page a moment to start loading again

            if not text:
                print("Failed to load content after multiple attempts")
                break

            remove_after_match = "作者有话说"

            # Split the text at the matched string
            result = text.split(remove_after_match)[0]
            if VIP:
                # --- Decypher ---
                if os.path.exists(FONT_PATH):
                    puas = extract_pua_chars(result)
                    # #PUA to Image
                    render_given_pua_glyphs(puas, FONT_PATH, GLYPH_DIR, 64)
                    # #Image to UNICODE MAP
                    print("\n[Generating Map]")
                    generate_map(MAP_PATH)
                    time.sleep(0.5)
                    # --- Decode Font ---
                    PUA_MAPPING = load_pua_map(MAP_PATH)
                    decoded_text = decode_font(result, PUA_MAPPING)
                    write_append(f"{decoded_text}\n", OUTPUT_PATH)
            else:
                write_append(f"{result}\n", OUTPUT_PATH)

            # break  # debug
            # --- Go to next page ---
            try:
                next_page_link = driver.find_element(
                    By.XPATH, "//span[@class='bigtext' and text()='下一章→']"
                )
                driver.execute_script("arguments[0].scrollIntoView();", next_page_link)
                next_page_link.click()
                time.sleep(0.8)
            except Exception:
                print("\n[End] No more chapters found.")
                break
    except Exception as e:
        print(f"[Error] Scraping ended with: {e}")
    # --- Clean Output ---
    clean_txt(OUTPUT_PATH, CLEANED_PATH, MATCH_STRINGS)
    cleanup()
