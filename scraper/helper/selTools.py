# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


def get_title(wait, by, value):
    try:
        ele = wait.until(EC.presence_of_element_located((by, value)))
        text = ele.text.strip()
        return text
    except:
        ele = wait.until(EC.presence_of_element_located((by, value)))
        print(ele)
        return ele


def next_page(driver, by, value):
    ele = driver.find_element(by, value)
    driver.execute_script("arguments[0].scrollIntoView();", ele)
    ele.click()


def multi_next_page(driver, by, sec, chp):
    try:
        next_page_link = driver.find_element(by, sec)
    except:
        next_page_link = driver.find_element(By.XPATH, chp)
    driver.execute_script("arguments[0].scrollIntoView();", next_page_link)
    next_page_link.click()
