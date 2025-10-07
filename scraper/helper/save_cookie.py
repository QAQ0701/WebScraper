import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from CONSTANTS import COOKIES_DIR, CREDENTIALS_PATH
from helper.utils import read_json

import time

SAVE_PATH = f"{COOKIES_DIR}/jjwxc_cookies.json"
CREDENTIALS = read_json(CREDENTIALS_PATH, "jjwxc")


def save_cookies_jj(sleep_time=20):

    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    # options.add_argument("--headless=new")  # optional: remove if you want to see browser
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options=options)

    try:
        url = "https://www.jjwxc.net"
        driver.get(url)
        wait = WebDriverWait(driver, 25)

        login = wait.until(EC.presence_of_element_located((By.ID, "jj_login")))
        login.click()

        loginname = wait.until(EC.presence_of_element_located((By.ID, "loginname")))
        loginname.send_keys(CREDENTIALS["username"])
        loginpassword = wait.until(
            EC.presence_of_element_located((By.ID, "loginpassword"))
        )
        loginpassword.send_keys(CREDENTIALS["password"])

        time.sleep(sleep_time)

        # Dump cookies
        cookies = driver.get_cookies()

        # Save cookies to a single JSON object
        data_to_save = {"cookies": cookies}
        with open(SAVE_PATH, "w", encoding="utf-8") as f:
            json.dump(data_to_save, f, indent=2)
        print("Cookies saved to jjwxc_cookies.json")

    finally:
        driver.quit()
