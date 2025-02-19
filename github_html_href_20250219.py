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
import re

# GitHub 설정
GITHUB_TOKEN = os.getenv("TOKEN")  # GitHub Secrets에서 가져오기
REPO_NAME = "cystine13/koreastatlinker"
FILE_PATH = "combined_rss_data.json"
BRANCH_NAME = "main"

# 크롤링 설정
rss_feeds = [
    {
        "url": "https://www.mss.go.kr/site/smba/foffice/ex/statDB/stReportRoList.do?gb=1",
        "row_selector": "table tbody tr",
        "title_selector": "td.alignLeft a",
        "date_selector": "td:nth-child(5)",
        "date_format": "%Y/%m/%d",  # 사이트별 날짜 형식
        "link_generator": lambda href: re.search(r"doStReportDetailView\('(\d+)'\)", href).group(1),
        "link_template": "https://www.mss.go.kr/site/smba/foffice/ex/statDB/StReportContentDetailView.do?gb=1&reSeq={}",
        "source_en": "SMEs Statistics System",
        "source_kr": "중소기업 통계"
    },
    {
        "url": "https://www.mss.go.kr/site/smba/foffice/ex/linkage/linkageList.do?target=T001",
        "row_selector": "table tbody tr",
        "title_selector": "td.subject a",
        "date_selector": "td:nth-child(6)",
        "date_format": "%Y-%m-%d",  # 다른 형식
        "link_generator": lambda href: re.search(r"doLinkageFView\((\d+),", href).group(1),
        "link_template": "https://www.mss.go.kr/site/smba/foffice/ex/linkage/linkageView.do?target=T001&b_idx={}",
        "source_en": "SMEs Statistics System",
        "source_kr": "중소기업 통계"
    },
    #에너지수급동향
    {
        "url": "https://www.kesis.net/sub/sub_0005.jsp?M_MENU_ID=M_M_002&S_MENU_ID=S_M_016",
        "row_selector": "table tbody tr",
        "title_selector": "td.bbs_content p.bbs_t a",
        "date_selector": "td.bbs_content p.bbs_c",
        "date_format": "발간물 | %Y-%m-%d",  # 사이트별 날짜 형식
        "link_generator": lambda href: re.search(r"detailPage\('C_011','(\d+)'\)", href).group(1),
        "link_template": "https://www.kesis.net/sub/sub_0005_01.jsp?CATEGORY_ID=C_011&M_MENU_ID=M_M_002&S_MENU_ID=S_M_016&SEQ={}",
        "source_en": "Korea Energy Statistical Information System",
        "source_kr": "국가에너지통계종합정보시스템"        
    },
    #가구에너지패널조사
    {
        "url": "https://www.kesis.net/sub/sub_0005.jsp?M_MENU_ID=M_M_002&S_MENU_ID=S_M_015",
        "row_selector": "table tbody tr",
        "title_selector": "td.bbs_content p.bbs_t a",
        "date_selector": "td.bbs_content p.bbs_c",
        "date_format": "발간물 | %Y-%m-%d",  # 사이트별 날짜 형식
        "link_generator": lambda href: re.search(r"detailPage\('C_010','(\d+)'\)", href).group(1),
        "link_template": "https://www.kesis.net/sub/sub_0005_01.jsp?CATEGORY_ID=C_010&M_MENU_ID=M_M_002&S_MENU_ID=S_M_015&SEQ={}",
        "source_en": "Korea Energy Statistical Information System",
        "source_kr": "국가에너지통계종합정보시스템"        
    },
    #에너지총조사
    {
        "url": "https://www.kesis.net/sub/sub_0005.jsp?M_MENU_ID=M_M_002&S_MENU_ID=S_M_015",
        "row_selector": "table tbody tr",
        "title_selector": "td.bbs_content p.bbs_t a",
        "date_selector": "td.bbs_content p.bbs_c",
        "date_format": "발간물 | %Y-%m-%d",  # 사이트별 날짜 형식
        "link_generator": lambda href: re.search(r"detailPage\('C_010','(\d+)'\)", href).group(1),
        "link_template": "https://www.kesis.net/sub/sub_0005_01.jsp?CATEGORY_ID=C_010&M_MENU_ID=M_M_002&S_MENU_ID=S_M_015&SEQ={}",
        "source_en": "Korea Energy Statistical Information System",
        "source_kr": "국가에너지통계종합정보시스템"  
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
            href = title_element.get_attribute("href")

            report_id = feed["link_generator"](href)
            link = feed["link_template"].format(report_id)
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
