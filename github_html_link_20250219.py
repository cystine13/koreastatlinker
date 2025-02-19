import os
import base64
import requests
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from translate import Translator
from datetime import datetime, timedelta

# GitHub 설정
GITHUB_TOKEN = os.getenv("TOKEN")  # GitHub Secrets에서 가져오기
REPO_NAME = "cystine13/koreastatlinker"
FILE_PATH = "news_posts.json"
BRANCH_NAME = "main"

# 크롤링 설정
rss_feeds = [
    #에너지통계월보
    {
        "url": "https://www.kesis.net/sub/sub_0003.jsp?M_MENU_ID=M_M_002&S_MENU_ID=S_M_011",
        "source_kr": "국가에너지통계종합정보시스템",
        "source_en": "Korea Energy Statistical Information System",
        "row_selector": "table tbody tr",
        "title_selector": "td.bbs_title a",
        "date_selector": "td.bbs_dt.color_gray",
        "date_format": "%Y-%m-%d"  # 날짜 형식
    },
    #에너지통계연보
    {

        "url": "https://www.kesis.net/sub/sub_0003.jsp?M_MENU_ID=M_M_002&S_MENU_ID=S_M_012",
        "source_kr": "국가에너지통계종합정보시스",
        "source_en": "Korea Energy Statistical Information System",
        "row_selector": "table tbody tr",
        "title_selector": "td.bbs_title a",
        "date_selector": "td.bbs_dt.color_gray",
        "date_format": "%Y-%m-%d"  # 날짜 형식
    },
    #지역에너지통계
    {
        "url": "https://www.kesis.net/sub/sub_0003.jsp?M_MENU_ID=M_M_002&S_MENU_ID=S_M_013",
        "source_kr": "국가에너지통계종합정보시스",
        "source_en": "Korea Energy Statistical Information System",
        "row_selector": "table tbody tr",
        "title_selector": "td.bbs_title a",
        "date_selector": "td.bbs_dt.color_gray",
        "date_format": "%Y-%m-%d"  # 날짜 형식
    },
    #부동산통계
    {
        "url": "https://www.reb.or.kr/r-one/portal/bbs/rpt/searchBulletinPage.do",
        "source_kr": "부동산 통계정보",
        "source_en": "Real Estate Statistics Information System",
        "row_selector": "table tbody tr",
        "title_selector": "td.title.left a",
        "date_selector": "td.date.userDttm",
        "date_format": "%Y-%m-%d"  # 날짜 형식
    }
]

# 번역 함수
def translate_text(text, src="ko", dest="en"):
    try:
        translator = Translator(from_lang=src, to_lang=dest)
        return translator.translate(text)
    except Exception:
        return text

# 크롤링 함수
def scrape_feed(feed, target_date):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    driver.get(feed["url"])

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, feed["row_selector"]))
    )

    rows = driver.find_elements(By.CSS_SELECTOR, feed["row_selector"])
    data = []

    for row in rows:
        try:
            raw_date = row.find_element(By.CSS_SELECTOR, feed["date_selector"]).text.strip()
            date = datetime.strptime(raw_date, feed["date_format"]).strftime("%Y-%m-%d")

            if date != target_date:
                continue

            title_element = row.find_element(By.CSS_SELECTOR, feed["title_selector"])
            title_kr = title_element.text.strip()
            link = feed["url"]
            title_en = translate_text(title_kr)

            data.append({
                "title_kr": title_kr,
                "title_en": title_en,
                "link": link,
                "date": date,
                "source_kr": feed["source_kr"],
                "source_en": feed["source_en"]
            })
        except Exception:
            continue

    driver.quit()
    return data

# 메인 실행 함수
def main():
    target_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    all_news = []

    for feed in rss_feeds:
        all_news.extend(scrape_feed(feed, target_date))

    if all_news:
        upload_to_github(REPO_NAME, FILE_PATH, all_news, BRANCH_NAME)

if __name__ == "__main__":
    main()
