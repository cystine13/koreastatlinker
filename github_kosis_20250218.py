import os
import base64
import requests
import json
from datetime import datetime

# 🔒 GitHub 정보 (환경 변수 사용)
GITHUB_TOKEN = os.getenv("TOKEN")
GITHUB_REPO = "cystine13/koreastatlinker"
GITHUB_FILE_PATH = "k-indicator_data.json"  # 📌 업로드할 JSON 파일명
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"

# 🔒 KOSIS API 인증키 (환경 변수 사용)
API_KEY = os.getenv("KOSIS_API_KEY")

# 📌 KOSIS API URL 및 공통 매개변수
BASE_URL = "https://kosis.kr/openapi/Param/statisticsParameterData.do"
current_year = datetime.now().year
start_year = 2000  # 시작 연도
end_year = current_year - 1  # 종료 연도를 전년도까지 자동 설정

# 📌 데이터 수집 항목 (여러 개 가능)
items = [
    {"orgId": "101", "tblId": "DT_1IN1502", "itmId": "T200", "objL1": "00", "prdSe": "Y", "name_en": "Household (households)", "name_kr": "가구수 (가구)", "decimal_places": 0,
     "category_en": "Population", "category_kr": "인구", "source_en": "Statistics Korea, Population Census", "source_kr": "통계청, 인구총조사"},
    {"orgId": "101", "tblId": "DT_1B8000F", "itmId": "T1", "objL1": "11", "prdSe": "Y", "name_en": "Births (Person)", "name_kr": "출생아수 (명)", "decimal_places": 0,
     "category_en": "Population", "category_kr": "인구", "source_en": "Statistics Korea, Vital Statistics", "source_kr": "통계청, 인구동향조사"},
    {"orgId": "101", "tblId": "DT_1PL1502", "itmId": "T00", "objL1": "00", "objL2": "000", "prdSe": "Y", "name_en": "One Person Households (household)", "name_kr": "1인 가구수 (가구)", "decimal_places": 0,
     "category_en": "Population", "category_kr": "인구", "source_en": "Statistics Korea, Population Census", "source_kr": "통계청, 인구총조사"},
    {"orgId": "101", "tblId": "DT_1B8000H", "itmId": "T12", "objL1": "00", "prdSe": "Y", "name_en": "Total Fertility Rate (per woman of childbearing age)", "name_kr": "합계출산율 (명/가임여성1명당)", "decimal_places": 3,
     "category_en": "Population", "category_kr": "인구", "source_en": "Statistics Korea, Vital Statistics", "source_kr": "통계청, 인구동향조사"},
    {"orgId": "101", "tblId": "DT_1B8000F", "itmId": "T1", "objL1": "41", "prdSe": "Y", "name_en": "Marriages (cases)", "name_kr": "혼인건수 (건)", "decimal_places": 0,
     "category_en": "Population", "category_kr": "인구", "source_en": "Statistics Korea, Vital Statistics", "source_kr": "통계청, 인구동향조사"},
    {"orgId": "101", "tblId": "DT_1JC1516", "itmId": "T30", "objL1": "00", "objL2": "00", "prdSe": "Y", "name_en": "Average Household Size (Persons)", "name_kr": "평균 가구원수 (명)", "decimal_places": 1,
     "category_en": "Population", "category_kr": "인구", "source_en": "Statistics Korea, Population Census", "source_kr": "통계청, 인구총조사"},
    {"orgId": "101", "tblId": "DT_1JD1501", "itmId": "T10", "objL1": "00", "prdSe": "Y", "name_en": "Multicultural Households", "name_kr": "다문화 가구 (가구)", "decimal_places": 0,
     "category_en": "Population", "category_kr": "인구", "source_en": "Statistics Korea, Population Census", "source_kr": "통계청, 인구총조사"},
    {"orgId": "111", "tblId": "DT_1B040A8", "objL1": "AAX000", "objL2": "13102870964B.0", "objL3": "AAB000", "itmId": "13103870964T1", "prdSe": "Y", "name_en": "Registered Foreigners (Persons)", "name_kr": "등록 외국인 (명)", "decimal_places": 0,
     "category_en": "Population", "category_kr": "인구", "source_en": "Ministry of Justice, Statistics of Arrivals and Departures", "source_kr": "법무부, 출입국자및체류외국인통계"},
    {"orgId": "101", "tblId": "DT_1B040A3", "objL1": "00", "itmId": "T20", "prdSe": "Y", "name_en": "Resident Population (Persons)", "name_kr": "주민등록인구 (명)", "decimal_places": 0,
     "category_en": "Population", "category_kr": "인구", "source_en": "Ministry of the Interior and Safety, Population Statistics Based on Resident Registration", "source_kr": "행정안전부, 주민등록인구현황"},
    {"orgId": "101", "tblId": "DT_1B26003_A01", "itmId": "T70", "objL1": "00", "objL2": "00", "prdSe": "Y", "name_en": "Internal Migrants (Persons)", "name_kr": "국내인구 이동자수 (명)", "decimal_places": 0,
     "category_en": "Population", "category_kr": "인구", "source_en": "Statistics Korea, Internal Migration Statistics", "source_kr": "통계청, 국내인구이동통계"},
    {"orgId": "101", "tblId": "DT_1B040B3", "objL1": "00", "itmId": "T1", "prdSe": "Y", "name_en": "Resident Households (Households)", "name_kr": "주민등록세대수 (세대)", "decimal_places": 0,
     "category_en": "Population", "category_kr": "인구", "source_en": "Ministry of the Interior and Safety, Population Statistics Based on Resident Registration", "source_kr": "행정안전부, 주민등록인구현황"},
    {"orgId": "101", "tblId": "DT_1B08024", "itmId": "T7", "objL1": "00", "prdSe": "Y", "name_en": "Population Density (per/㎢)", "name_kr": "인구밀도 (명/㎢)", "decimal_places": 1,
     "category_en": "Population", "category_kr": "인구", "source_en": "Statistics Korea, Population Census", "source_kr": "통계청, 인구총조사"},
    {"orgId": "101", "tblId": "DT_1B41", "objL1": "01", "itmId": "T6", "prdSe": "Y", "name_en": "Life Expectancy (Years)", "name_kr": "기대수명 (년)", "decimal_places": 1,
     "category_en": "Health & Welfare", "category_kr": "보건, 복지", "source_en": "Statistics Korea, Life Tables By Province", "source_kr": "통계청, 생명표"},
    {"orgId": "101", "tblId": "DT_1B8000F", "objL1": "12", "itmId": "T1", "prdSe": "Y", "name_en": "Deaths (Persons)", "name_kr": "사망자수 (명)", "decimal_places": 0,
     "category_en": "Health & Welfare", "category_kr": "보건, 복지", "source_en": "Statistics Korea, Causes of Death Statistics", "source_kr": "통계청, 사망원인통계"},
    {"orgId": "101", "tblId": "DT_1B34E01", "objL1": "J06", "objL2": "0", "objL3": "00", "itmId": "T5", "prdSe": "Y", "name_en": "Suicide Rate (per 100k Persons)", "name_kr": "자살률 (십만명당)" , "decimal_places": 1,
     "category_en": "Health & Welfare", "category_kr": "보건, 복지", "source_en": "Statistics Korea, Causes of Death Statistics", "source_kr": "통계청, 사망원인통계"},
    {"orgId": "117", "tblId": "DT_11714_N001", "itmId": "TT", "objL1" : "00", "prdSe": "Y", "name_en": "Recipient of National Basic Livelihood (person)", "name_kr": "국민기초생활수급자수 (명)", "decimal_places": 0,
     "category_en": "Health & Welfare", "category_kr": "보건,복지", "source_en": "Ministry of Health and Welfare, Livelihood Protection Recipients Statistics", "source_kr": "보건복지부, 국민기초생활보장수급자현황"}    
]

# 📌 데이터를 저장할 딕셔너리 (연도별로 정리)
data_by_year = {str(year): [] for year in range(start_year, end_year + 1)}

# 🔄 KOSIS API 데이터 요청 함수
def fetch_kosis_data(item):
    """KOSIS에서 특정 지표 데이터를 수집하는 함수"""
    params = {
        "method": "getData",
        "apiKey": API_KEY,
        "format": "json",
        "jsonVD": "Y",
        "orgId": item["orgId"],
        "tblId": item["tblId"],
        "prdSe": item["prdSe"],
        "startPrdDe": str(start_year),
        "endPrdDe": str(end_year),
        "objL1": item["objL1"],
        "itmId": item["itmId"]
    }

    # 🔥 objL2, objL3가 있는 경우 추가
    if "objL2" in item:
        params["objL2"] = item["objL2"]
    if "objL3" in item:
        params["objL3"] = item["objL3"]

    response = requests.get(BASE_URL, params=params)

    if response.status_code == 200:
        data = response.json()

        if isinstance(data, list) and len(data) > 0:
            for entry in data:
                year = entry["PRD_DE"]
                value = entry["DT"]

                # 🔹 소수점 자리수 적용 및 천 단위 콤마 추가
                decimal_places = item["decimal_places"]
                formatted_value = f"{round(float(value), decimal_places):,.{decimal_places}f}"

                # 🔹 JSON 데이터 구조에 맞게 저장
                data_by_year[year].append({
                    "name_en": item["name_en"],
                    "name_kr": item["name_kr"],
                    "value": formatted_value,
                    "category_en": item["category_en"],
                    "category_kr": item["category_kr"],
                    "source_en": item["source_en"],
                    "source_kr": item["source_kr"]
                })
        else:
            print(f"⚠ 데이터 없음: {item['name_en']} ({item['tblId']})")
    else:
        print(f"❌ API 요청 실패: {item['name_en']} ({item['tblId']}) - 상태 코드 {response.status_code}")
        print("🔍 응답 데이터:", response.text)

# 🔄 여러 개 지표 데이터 요청 실행
for item in items:
    fetch_kosis_data(item)

# 📌 JSON 파일 저장
json_filename = "k-indicator_data.json"
with open(json_filename, "w", encoding="utf-8") as json_file:
    json.dump(data_by_year, json_file, ensure_ascii=False, indent=4)

print(f"✅ 데이터 수집 완료! JSON 파일 저장됨: {json_filename}")

# 🔄 GitHub에 업로드하는 함수
def upload_to_github(content, message):
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    # 🔍 현재 파일 상태 확인 (SHA 값 가져오기)
    get_response = requests.get(GITHUB_API_URL, headers=headers)
    sha = get_response.json().get("sha") if get_response.status_code == 200 else None

    # 📌 업로드 데이터 생성
    data = {
        "message": message,
        "content": content,  # Base64 인코딩된 내용
    }
    if sha:
        data["sha"] = sha  # 기존 파일 덮어쓰기

    # 🔥 GitHub 업로드 요청
    put_response = requests.put(GITHUB_API_URL, headers=headers, json=data)
    return put_response.status_code, put_response.json()

# 📌 JSON 파일을 Base64로 인코딩하여 GitHub에 업로드
with open(json_filename, "r", encoding="utf-8") as file:
    encoded_content = base64.b64encode(file.read().encode("utf-8")).decode("utf-8")

status_code, result = upload_to_github(encoded_content, "Update k-indicator_data.json")

if status_code in [200, 201]:
    print("✅ GitHub 업데이트 성공!")
else:
    print("❌ GitHub 업데이트 실패!")
    print(result)
