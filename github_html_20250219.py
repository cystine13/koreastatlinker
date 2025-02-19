import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from translate import Translator
from datetime import datetime, timedelta
import requests
import json
import base64

# GitHub 설정
GITHUB_TOKEN = os.getenv("TOKEN")  # GitHub Secrets에서 가져오기
REPO_NAME = "cystine13/koreastatlinker"
FILE_PATH = "news_posts.json"
BRANCH_NAME = "main"

# 사이트별 크롤링 설정
rss_feeds = [
    #통계누리
    {
        "url": "https://stat.molit.go.kr/portal/notice/newNoticeView.do?tab=colmn",
        "source_kr": "국토교통부 통계누리",
        "source_en": "Ministry of Land, Infrastructure, and Transport (MOLIT) Statistics System",
        "row_selector": "tbody tr",
        "title_selector": "td.mobile-show.tl a",
        "date_selector": "dd",
        "date_format": "%Y-%m-%d"  # 날짜 형식
    },
    #농림추산식품부
    {
        "url": "https://www.mafra.go.kr/home/5102/subview.do",
        "source_kr": "농림축산식품부",
        "source_en": "Ministry of Agriculture, Food and Rural Affairs",
        "row_selector": "table tbody tr",
        "title_selector": "td p a",
        "date_selector": "dd.date",
        "date_format": "%Y.%m.%d"  # 날짜 형식
    }  
]

# 번역 함수
def translate_text(text, src="ko", dest="en"):
    try:
        translator = Translator(from_lang=src, to_lang=dest)
        return translator.translate(text)
    except Exception:
        return text  # 번역 실패 시 원문 반환

# GitHub 업로드 함수
def upload_to_github(repo, file_path, data, branch_name):
    url = f"https://api.github.com/repos/{repo}/contents/{file_path}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        sha = response.json().get("sha")
        existing_content = json.loads(base64.b64decode(response.json()["content"]).decode("utf-8"))
        data.extend(existing_content)
        data = list({item["title_kr"]: item for item in data}.values())  # 중복 제거
    else:
        sha = None

    encoded_content = base64.b64encode(json.dumps(data, ensure_ascii=False, indent=4).encode("utf-8")).decode("utf-8")
    payload = {"message": "Update news_posts.json", "content": encoded_content, "branch": branch_name}
    if sha:
        payload["sha"] = sha

    response = requests.put(url, headers=headers, json=payload)
    return response.status_code in [200, 201]

# 크롤링 함수
def scrape_site(feed, target_date):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    driver.get(feed["url"])

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, feed["row_selector"]))
    )

    news_data = []
    rows = driver.find_elements(By.CSS_SELECTOR, feed["row_selector"])
    for row in rows:
        try:
            raw_date = row.find_element(By.CSS_SELECTOR, feed["date_selector"]).text.strip()
            date = datetime.strptime(raw_date, feed["date_format"]).strftime("%Y-%m-%d")

            if date != target_date:
                continue

            title_element = row.find_element(By.CSS_SELECTOR, feed["title_selector"])
            title_kr = title_element.text.strip()
            link = title_element.get_attribute("href")
            title_en = translate_text(title_kr)

            news_data.append({
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
    return news_data

# 메인 실행 함수
def main():
    target_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    all_news = []

    for feed in rss_feeds:
        all_news.extend(scrape_site(feed, target_date))

    if all_news:
        upload_to_github(REPO_NAME, FILE_PATH, all_news, BRANCH_NAME)

if __name__ == "__main__":
    main()
