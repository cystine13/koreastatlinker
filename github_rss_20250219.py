import os
import feedparser
import json
import requests
import base64
from datetime import datetime, timedelta
from translate import Translator

# GitHub 설정
GITHUB_TOKEN = os.getenv("TOKEN")  # GitHub Secrets에서 불러오기
REPO_NAME = "cystine13/koreastatlinker"  # 저장소 이름
FILE_PATH = "news_posts.json"  # GitHub에 저장할 파일 경로
BRANCH_NAME = "main"  # 저장소의 기본 브랜치

# 번역 함수
def translate_text(text, src="ko", dest="en"):
    try:
        translator = Translator(from_lang=src, to_lang=dest)
        return translator.translate(text)
    except Exception:
        return text  # 번역 실패 시 원문 반환

# RSS 데이터 가져오기
def fetch_and_filter_rss(rss_url, target_date, date_format, source_kr, source_en):
    feed = feedparser.parse(rss_url)
    filtered_news = []

    for entry in feed.entries:
        title_kr = entry.title
        link = entry.link

        try:
            date_parsed = datetime.strptime(entry.published, date_format)
            formatted_date = date_parsed.strftime("%Y-%m-%d")
        except (AttributeError, ValueError):
            continue

        if formatted_date == target_date:
            title_en = translate_text(title_kr)
            filtered_news.append({
                "title_kr": title_kr,
                "title_en": title_en,
                "link": link,
                "date": formatted_date,
                "source_kr": source_kr,
                "source_en": source_en
            })

    return filtered_news

# GitHub 업로드 함수 (로컬 JSON 파일 없이 처리)
def upload_to_github(repo, file_path, data, branch_name):
    url = f"https://api.github.com/repos/{repo}/contents/{file_path}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    # 기존 데이터 가져오기
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        sha = response.json().get("sha")
        github_content = json.loads(base64.b64decode(response.json()["content"]).decode("utf-8"))
        data.extend(github_content)  # 데이터 병합 및 중복 제거
        data = list({v["title_kr"]: v for v in data}.values())
    else:
        sha = None

    # GitHub에 업로드
    encoded_content = base64.b64encode(json.dumps(data, ensure_ascii=False, indent=4).encode("utf-8")).decode("utf-8")
    payload = {"message": "Update news_posts.json", "content": encoded_content, "branch": branch_name}
    if sha:
        payload["sha"] = sha  # 기존 파일 덮어쓰기

    response = requests.put(url, headers=headers, json=payload)
    return response.status_code in [200, 201]

# 메인 실행 함수
def main():
    target_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    rss_feeds = [
        {
            "url": "https://kostat.go.kr/board.es?mid=a10403040000&bid=107&nPage=1&act=rss",
            "date_format": "%Y%m%d%H%M",
            "source_kr": "통계청",
            "source_en": "Statistics Korea"
        },
        {
            "url": "https://kostat.go.kr/board.es?mid=a10403040000&bid=107&nPage=2&act=rss",
            "date_format": "%Y%m%d%H%M",
            "source_kr": "통계청",
            "source_en": "Statistics Korea"
        },
        {
            "url": "https://kostat.go.kr/board.es?mid=a10403040000&bid=107&nPage=3&act=rss",
            "date_format": "%Y%m%d%H%M",
            "source_kr": "통계청",
            "source_en": "Statistics Korea"
        },
        {
            "url": "https://kostat.go.kr/board.es?mid=a10403040000&bid=107&nPage=4&act=rss",
            "date_format": "%Y%m%d%H%M",
            "source_kr": "통계청",
            "source_en": "Statistics Korea"
        },        
        {
            "url": "https://kostat.go.kr/board.es?mid=a10301010000&bid=a103010100&act=rss",
            "date_format": "%Y%m%d%H%M",
            "source_kr": "통계청",
            "source_en": "Statistics Korea"
        },
        {
            "url": "https://www.bok.or.kr/portal/bbs/B0000501/news.rss?menuNo=201264",
            "date_format": "%a, %d %b %Y %H:%M:%S %z",
            "source_kr": "한국은행",
            "source_en": "Bank of Korea"
        }
    ]

    all_news = []
    for feed in rss_feeds:
        all_news.extend(fetch_and_filter_rss(feed["url"], target_date, feed["date_format"], feed["source_kr"], feed["source_en"]))

    # GitHub에 업로드
    success = upload_to_github(REPO_NAME, FILE_PATH, all_news, BRANCH_NAME)
    if success:
        print("✅ GitHub 업데이트 완료!")
    else:
        print("❌ GitHub 업데이트 실패!")

if __name__ == "__main__":
    main()
