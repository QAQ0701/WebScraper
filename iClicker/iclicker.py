from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime

from scraper.helper.utils import read_json

import time
import os
import sys
import random

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome()
# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
actions = ActionChains(driver)
wait = WebDriverWait(driver, 25)

# Open the webpage
login_url = "https://student.iclicker.com/#/login"  # Update this URL
driver.get(login_url)

username_field = wait.until(
    EC.element_to_be_clickable((By.ID, "input-email"))  # Update the ID
)
password_field = wait.until(
    EC.element_to_be_clickable((By.ID, "input-password"))  # Update the ID
)
login_button = wait.until(
    EC.element_to_be_clickable((By.ID, "sign-in-button"))  # Update the ID
)

# Send credentials and submit
cred = read_json("credentials.json", "iclicker")
saved_username = cred["username"]
saved_password = cred["password"]
username_field.send_keys(saved_username)
password_field.send_keys(saved_password)
login_button.click()

course103 = wait.until(
    EC.element_to_be_clickable(
        (By.XPATH, "//label[text()='CPSC 304 - Section 103 - Relational Databases']")
    )
)

course103.click()
time.sleep(300)

joinBtn = wait.until(EC.element_to_be_clickable((By.ID, "btnJoin")))

joinBtn.click()

while True:
    now = datetime.now()
    # Get the current time
    now = datetime.now()

    # Check if it's before 5 PM
    if now.hour < 17 or (now.hour == 17 and now.minute == 0):
        print(f"It's before 5 PM, {now}")
    else:
        print("It's 5 PM or later.")
        break

    try:
        r = random.randint(0, 1)
        if r == 0:
            clickerB = wait.until(
                EC.element_to_be_clickable((By.ID, "multiple-choice-b"))
            )
            clickerB.click()
            print("CLICKED B, sleeping for 1 min 20 sec")
        if r == 1:
            clickerA = wait.until(
                EC.element_to_be_clickable((By.ID, "multiple-choice-a"))
            )
            clickerA.click()
            print("CLICKED A, sleeping for 1 min 20 sec")
        time.sleep(80)
    except Exception as e:
        print("sleeping for 35s")
        time.sleep(35)
