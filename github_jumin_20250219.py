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

# 최신 자료 확인
def check_latest_update():
    response = requests.get(CHECK_URL)
    soup = BeautifulSoup(response.text, "html.parser")

    year_element = soup.select_one("select[name='searchYearEnd'] option[selected]")
    month_element = soup.select_one("select[name='searchMonthEnd'] option[selected]")

    return year_element.text.strip() if year_element else None, month_element.text.strip() if month_element else None

# JSON 파일 업데이트 (새 데이터로 덮어쓰기)
def update_github_json(latest_year, latest_month):
    new_data = [{
        "title_kr": f"{latest_year} {latest_month} 주민등록인구통계",
        "title_en": f"Resident Population Statistics for {latest_year[:-1]}.{int(latest_month[:-1]):02d}",
        "link": CHECK_URL,
        "date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
        "source_kr": "행정안전부 주민등록인구통계",
        "source_en": "MOIS Resident Population Statistics"
    }]

    new_content = json.dumps(new_data, ensure_ascii=False, indent=4)
    encoded_content = base64.b64encode(new_content.encode("utf-8")).decode("utf-8")
    upload_to_github(JSON_FILE_PATH, encoded_content)

# 업데이트 날짜 파일 저장
def write_latest_update_date(year, month):
    encoded_content = base64.b64encode(f"{year} {month}".encode("utf-8")).decode("utf-8")
    upload_to_github(LATEST_UPDATE_FILE, encoded_content)

# GitHub에 파일 업로드
def upload_to_github(file_path, encoded_content):
    github_api_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{file_path}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    response = requests.get(github_api_url, headers=headers)
    sha = response.json().get("sha") if response.status_code == 200 else None

    payload = {"message": f"Update {file_path}", "content": encoded_content, "branch": "main"}
    if sha:
        payload["sha"] = sha

    requests.put(github_api_url, json=payload, headers=headers)

# 메인 실행
def main():
    latest_year, latest_month = check_latest_update()
    if latest_year and latest_month:
        update_github_json(latest_year, latest_month)
        write_latest_update_date(latest_year, latest_month)

if __name__ == "__main__":
    main()
