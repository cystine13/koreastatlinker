import os
import base64
import requests
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from translate import Translator
from datetime import datetime, timedelta
import re

# GitHub 설정
GITHUB_TOKEN = os.getenv("TOKEN")  # GitHub Secrets에서 가져오기
REPO_NAME = "cystine13/koreastatlinker"
FILE_PATH = "news_posts.json"
BRANCH_NAME = "main"

# 크롤링 설정
rss_feeds = [
    {
        "url": "https://www.mediastat.or.kr/kor/board/BoardList.html?board_class=BOARD02",
        "row_selector": "table tbody tr",
        "title_selector": "td.t_a_l.w50pct a",
        "date_ym_selector": "span.date_top",
        "date_d_selector": "span.date_bott",
        "date_format": "%Y.%m.%d",
        "link_template": "https://www.mediastat.or.kr/kor/board/BoardDetail.html?board_class=BOARD02&board_seq={}",
        "source_kr": "방송통신위원회 방송통계포털",
        "source_en": "MEDIA STAT"
    }
]

# 번역 함수
def translate_text(text, src="ko", dest="en"):
    try:
        translator = Translator(from_lang=src, to_lang=dest)
        return translator.translate(text)
    except Exception:
        return text

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
            date_top = row.find_element(By.CSS_SELECTOR, "span.date_top").text.strip()
            date_bott = row.find_element(By.CSS_SELECTOR, "span.date_bott").text.strip()
            raw_date = f"{date_top}.{date_bott}"
            date = datetime.strptime(raw_date, feed["date_format"]).strftime("%Y-%m-%d")

            if date != target_date:
                continue

            title_element = row.find_element(By.CSS_SELECTOR, feed["title_selector"])
            title_kr = title_element.text.strip()
            post_id = title_element.get_attribute("rel")
            link = feed["link_template"].format(post_id)
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
