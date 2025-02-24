import os
import json
import base64
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# GitHub 설정
GITHUB_TOKEN = os.getenv("TOKEN")  # GitHub Secrets에서 가져오기
REPO_OWNER = "cystine13"
REPO_NAME = "koreastatlinker"
JSON_FILE_PATH = "news_posts.json"
LATEST_UPDATE_FILE = "latest_update_date.txt"
CHECK_URL = "https://jumin.mois.go.kr/statMonth.do"

# 최신 뉴스 확인 및 업데이트
def latest_news():
    response = requests.get(CHECK_URL)
    soup = BeautifulSoup(response.text, "html.parser")

    year_element = soup.select_one("select[name='searchYearEnd'] option[selected]")
    month_element = soup.select_one("select[name='searchMonthEnd'] option[selected]")
    latest_year = year_element.text.strip() if year_element else None
    latest_month = month_element.text.strip() if month_element else None

    github_api_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{LATEST_UPDATE_FILE}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    response = requests.get(github_api_url, headers=headers)
    if response.status_code == 200:
        content = base64.b64decode(response.json()["content"]).decode("utf-8").strip()
        stored_year, stored_month = content.split(" ")
        if stored_year == latest_year and stored_month == latest_month:
            return []  # 최신 데이터와 동일하면 추가 없음
    
    encoded_content = base64.b64encode(f"{latest_year} {latest_month}".encode("utf-8")).decode("utf-8")
    payload = {"message": "Update latest_update_date.txt", "content": encoded_content, "branch": "main"}
    if response.status_code == 200:
        payload["sha"] = response.json().get("sha")
    requests.put(github_api_url, json=payload, headers=headers)

    return [{
        "title_kr": f"{latest_year} {latest_month} 주민등록인구통계",
        "title_en": f"Resident Population Statistics for {latest_year[:-1]}.{int(latest_month[:-1]):02d}",
        "link": CHECK_URL,
        "date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
        "source_kr": "행정안전부 주민등록인구통계",
        "source_en": "MOIS Resident Population Statistics"
    }]

# 뉴스 JSON 업데이트
def update_news_json(news_data):
    github_api_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{JSON_FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    response = requests.get(github_api_url, headers=headers)
    if response.status_code == 200:
        existing_data = json.loads(base64.b64decode(response.json()["content"]).decode("utf-8"))
        news_data = existing_data + news_data
        encoded_content = base64.b64encode(json.dumps(news_data, ensure_ascii=False, indent=4).encode("utf-8")).decode("utf-8")
        payload = {"message": "Update news_posts.json", "content": encoded_content, "branch": "main"}
        payload["sha"] = response.json().get("sha")
        requests.put(github_api_url, json=payload, headers=headers)
    else:
        encoded_content = base64.b64encode(json.dumps(news_data, ensure_ascii=False, indent=4).encode("utf-8")).decode("utf-8")
        payload = {"message": "Create news_posts.json", "content": encoded_content, "branch": "main"}
        requests.put(github_api_url, json=payload, headers=headers)

# 실행
if __name__ == "__main__":
    latest_news_data = latest_news()
    if latest_news_data:
        update_news_json(latest_news_data)
