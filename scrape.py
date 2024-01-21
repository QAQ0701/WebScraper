from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import requests
from bs4 import BeautifulSoup
import chardet
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

NEXTCHP_XPATH = "ADD ur own"
OUTLIST = []
ChpNum = 0  # counter


def detect_encoding(content):
    result = chardet.detect(content)
    return result["encoding"]


def scrape_paragraph(url):
    response = requests.get(url)
    r1 = ""  ## things to filter out
    r2 = ""
    r3 = ""
    if response.status_code == 200:
        # Detect the encoding of the content
        detected_encoding = detect_encoding(response.content)
        global ENCODING
        ENCODING = detected_encoding

        # Parse HTML content using BeautifulSoup with the detected encoding
        soup = BeautifulSoup(
            response.content, "html.parser", from_encoding=detected_encoding
        )

        paragraphs = soup.find_all("p")
        # text_content = soup.get_text()

        # Phrases to remove
        phrases_to_remove = [r1, r2, r3]

        # Remove paragraphs containing any of the specified phrases
        paragraphs = [
            paragraph
            for paragraph in paragraphs
            if not any(phrase in paragraph.get_text() for phrase in phrases_to_remove)
        ]

        for paragraph in paragraphs:
            print(paragraph.get_text())
        return paragraphs
    else:
        print("Failed to retrieve the web page. Status code:", response.status_code)


def getdata(url):
    r = requests.get(url)
    html = r.text.split("\n")
    # print(html)
    # print(type(html))
    ##specific uses##
    # for line in html:
    #     if "var npage =" in line:
    #         currpage = int(line.split("=")[1][1:2])
    #     elif "var totalpage =" in line:
    #         totalpage = int(line.split("=")[1][1:2])
    # return currpage, totalpage


def get_links(url, curr, total):
    list = [url]
    if curr == 1:
        root = url.split(".html")[0]
        end = ".html"
        for i in range(2, total + 1):
            list.append(root + "_" + str(i) + end)
    print(list)
    return list


def navigate_page(url, driver):
    driver.get(url)
    # nextChp = driver.find_element(By.XPATH, NEXTCHP_XPATH)
    # currpage, totalpage = getdata(url)
    # subpages = get_links(url, currpage, totalpage)
    global ChpNum
    OUTLIST.append("\n\tChapter " + str(ChpNum) + "\n")
    # for page in subpages:
    #     OUTLIST.append(scrape_paragraph(page))
    ChpNum += 1
    while totalpage > 0:
        nextChp = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, NEXTCHP_XPATH))
        )
        nextChp.click()
        totalpage -= 1
        time.sleep(0.1)
    current_url = driver.current_url
    return current_url


def write(list, encode):
    try:
        # Save the information to a text file
        with open("output.txt", "a", encoding=encode) as output_file:
            for paragraphs in list:
                for paragraph in paragraphs:
                    if type(paragraph) != str:
                        output_file.write(paragraph.get_text() + "\n")
                    else:
                        output_file.write(paragraph)
            # output_file.write(text_content)
        print(f"Text extracted from {url} and saved to {OUTPUT_PATH}.")
    except:
        print("Failed to save into txt")


if __name__ == "__main__":
    url = "add ur url here"
    OUTPUT_PATH = "output.txt"
    c = 13
    driver = webdriver.Chrome()
    while c > 0:
        url = navigate_page(url, driver)
        print("Next CHP: " + url)
        write(OUTLIST, ENCODING)
        c -= 1
        OUTLIST.clear()
