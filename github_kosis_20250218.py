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
     "category_en": "Health & Welfare", "category_kr": "보건,복지", "source_en": "Ministry of Health and Welfare, Livelihood Protection Recipients Statistics", "source_kr": "보건복지부, 국민기초생활보장수급자현황"},
    {"orgId": "350", "tblId": "TX_35003_A003", "itmId": "16350AAB7", "objL1" : "11101HJG00", "objL2" : "15350AB000", "prdSe": "Y", "name_en": "Medical Personnel (person)", "name_kr" : "의료인력수 (명)", "decimal_places": 0,
     "category_en": "Health & Welfare", "category_kr": "보건,복지", "source_en": "National Health Insurance Service, Medical Service Usage Statistics by Region", "source_kr": "국민건강보험공단, 지역별의료이용통계"}, 
    {"orgId": "117", "tblId": "DT_117N_A00023", "itmId": "16117ac000101", "objL1" : "15117AC000101", "objL2" : "11101SSB20", "objL3" : "15117AC001101", "prdSe": "Y", "name_en": "Cancers (person)", "name_kr" : "암발생자수 (명)", "decimal_places": 0,
    "category_en": "Health & Welfare", "category_kr": "보건,복지", "source_en": "Ministry of Health and Welfare, Cancer Registration Statistics", "source_kr": "보건복지부, 암등록통계"}, 
    {"orgId": "177", "tblId": "DT_11702_N012", "itmId": "RATIO", "objL1" : "1", "objL2" : "103", "prdSe": "Y", "name_en": "Monthly Alcohol Drinking (%)", "name_kr" : "음주율 (%)", "decimal_places": 1,
    "category_en": "Health & Welfare", "category_kr": "보건,복지", "source_en": "Korea Disease Contrl and Prevention Agency, Korea National Health and Nutrition Examination Survey", "source_kr": "질병관리청, 국민건강영양조사"}, 
    {"orgId": "101", "tblId": "DT_1B34E01", "objL1" : "0", "objL2" : "0", "objL3" : "00", "itmId": "T1", "prdSe": "Y", "name_en": "Mortality rate (per 100 thousand person)", "name_kr" : "사망률 (십만명당)", "decimal_places": 0,
    "category_en": "Health & Welfare", "category_kr": "보건,복지", "source_en": "Statistics Korea, Causes of Death Statistics", "source_kr": "통계청, 사망원인통계"}, 
    {"orgId": "117", "tblId": "DT_11761_N005", "itmId": "00", "objL1" : "00", "objL2" : "CHUT0", "objL3" : "TT", "prdSe": "Y", "name_en": "Number of The Registered Disabled (person)", "name_kr" : "장애인인구 (명)", "decimal_places": 0,
     "category_en": "Health & Welfare", "category_kr": "보건,복지", "source_en": "Ministry of Health and Welfare, Registered Disabled Persons", "source_kr": "보건복지부, 장애인현황"}, 
    {"orgId": "350", "tblId": "DT_35007_N130", "itmId": "001", "objL1" : "15350AC400Z1", "objL2" : "001", "objL3" : "001", "prdSe": "Y", "name_en": "Average Height (㎝)", "name_kr" : "평균신장 (㎝)", "decimal_places": 2,
     "category_en": "Health & Welfare", "category_kr": "보건,복지", "source_en": "National Health Insurance Service, National Health Screening Statistics", "source_kr": "국민건강보험공단, 건강검진통계"}, 
    {"orgId": "112", "tblId": "DT_15407_NN001", "itmId": "A", "objL1" : "01", "prdSe": "Y", "name_en": "Child Care Center (Place)", "name_kr" : "어린이집수 (개소)", "decimal_places": 0,
    "category_en": "Health & Welfare", "category_kr": "보건,복지", "source_en": "Ministry of Education, Statistics on Childcare Facilities and Users", "source_kr": "교육부, 어린이집및이용자통계"},
    {"orgId": "101", "tblId": "DT_1DA7001S", "itmId": "T80", "objL1" : "0", "prdSe": "Y", "name_en": "Unemployment rate (%)", "name_kr" : "실업률 (%)", "decimal_places": 1,
     "category_en": "Education & Labor", "category_kr": "교육,노동", "source_en": "Statistics Korea, Economically Active Population Survey", "source_kr": "통계청, 경제활동인구조사"},
    {"orgId": "101", "tblId": "DT_1DA7001S", "itmId": "T90", "objL1" : "0", "prdSe": "Y", "name_en": "Employment to population ratio (%)", "name_kr" : "고용률 (%)", "decimal_places": 1,
    "category_en": "Education & Labor", "category_kr": "교육,노동", "source_en": "Statistics Korea, Economically Active Population Survey", "source_kr": "통계청, 경제활동인구조사"},
    {"orgId": "101", "tblId": "DT_1DA7001S", "itmId": "T20", "objL1" : "0", "prdSe": "Y", "name_en": "Economically Active Population (Thousand Person)", "name_kr" : "경제활동인구 (명)", "decimal_places": 0,
     "category_en": "Education & Labor", "category_kr": "교육,노동", "source_en": "Statistics Korea, Economically Active Population Survey", "source_kr": "통계청, 경제활동인구조사"},
    {"orgId": "334", "tblId": "DT_1963003_002", "itmId": "00", "objL1" : "00", "objL2" : "A001", "objL3" : "C_1", "prdSe": "Y", "name_en": "Elementary School Students (Person)", "name_kr" : "초등학교 학생수 (명)", "decimal_places": 0,
     "category_en": "Education & Labor", "category_kr": "교육,노동", "source_en": "Korean Educational Development Institute, Statistics of Education", "source_kr": "한국교육개발원, 교육기본통계"},
    {"orgId": "334", "tblId": "DT_1963003_003", "itmId": "00", "objL1" : "00", "objL2" : "A001", "objL3" : "H_1", "prdSe": "Y", "name_en": "Middle School Students (Person)", "name_kr" : "중학교 학생수 (명)", "decimal_places": 0,
     "category_en": "Education & Labor", "category_kr": "교육,노동", "source_en": "Korean Educational Development Institute, Statistics of Education", "source_kr": "한국교육개발원, 교육기본통계"},
    {"orgId": "334", "tblId": "DT_1963003_004", "itmId": "00", "objL1" : "00", "objL2" : "A001", "objL3" : "H_1", "prdSe": "Y", "name_en": "High School Students (Person)", "name_kr" : "고등학교 학생수 (명)", "decimal_places": 0,
     "category_en": "Education & Labor", "category_kr": "교육,노동", "source_en": "Korean Educational Development Institute, Statistics of Education", "source_kr": "한국교육개발원, 교육기본통계"},
    {"orgId": "344", "tblId": "DT_344N_1D8A_AA", "itmId": "T001", "objL1" : "TOTAL", "prdSe": "Y", "name_en": "Indices of Labor Productivity (2020=100)", "name_kr" : "노동생산성지수 (2020=100)", "decimal_places": 1,
     "category_en": "Education & Labor", "category_kr": "교육,노동", "source_en": "Korea Productivity Center, Labor Productivity Index", "source_kr": "한국생산성본부, 노동생산성지수"},
    {"orgId": "118", "tblId": "DT_118N_MON041", "itmId": "13103110311MD_7", "objL1" : "15118INDUSTRY_9S0", "objL2" : "size01", "prdSe": "Y", "name_en": "Total hours Worked (Hour)", "name_kr" : "전체 근로시간 (시간)", "decimal_places": 1,
     "category_en": "Education & Labor", "category_kr": "교육,노동", "source_en": "Ministry of Employment and Labor, Labor Force Survey at Establishments", "source_kr": "고용노동부, 사업체노동력조사"}, #  근로시간('11~'19)    
    {"orgId": "118", "tblId": "DT_118N_MON051", "itmId": "13103110311MD_7", "objL1" : "190326INDUSTRY_10S0", "objL2" : "size01", "prdSe": "Y", "name_en": "Total hours Worked (Hour)", "name_kr" : "전체 근로시간 (시간)", "decimal_places": 1,
     "category_en": "Education & Labor", "category_kr": "교육,노동", "source_en": "Ministry of Employment and Labor, Labor Force Survey at Establishments", "source_kr": "고용노동부, 사업체노동력조사"}, #  근로시간('20~)
    {"orgId": "101", "tblId": "DT_1ES4F09S", "itmId": "T10", "objL1" : "00", "prdSe": "Y", "name_en": "Dual-earner households (1,000 household)", "name_kr" : "맞벌이가구 (천가구)", "decimal_places": 0,
     "category_en": "Education & Labor", "category_kr": "교육,노동", "source_en": "Statistics Korea, Local Area Labour Force Survey", "source_kr": "통계청, 지역별고용조사"},
    {"orgId": "101", "tblId": "DT_1HDCA02_HF", "objL1" : "A0100", "objL2" : "B3000", "objL3" : "C06", "itmId": "T01", "prdSe": "Y", "name_en": "Average of all households Liabilities (10 thousand won)", "name_kr" : "전가구 평균부채 (만원)", "decimal_places": 2,
     "category_en": "Income, Consumption & Assets", "category_kr": "소득,소비,자산", "source_en": "Statistics Korea, Bank of Korea, Financial Supervisory Service, Survey of Household Finances and Living Conditions", "source_kr": "통계청, 한국은행, 금융감독원, 가계금융복지조"}, #  부채('10~'11)
    {"orgId": "101", "tblId": "DT_1HDBA01", "objL1" : "A0100", "objL2" : "B0500", "objL3" : "C06", "itmId": "T01", "prdSe": "Y", "name_en": "Average of all households Liabilities (10 thousand won)", "name_kr" : "전가구 평균부채 (만원)", "decimal_places": 2,
     "category_en": "Income, Consumption & Assets", "category_kr": "소득,소비,자산", "source_en": "Statistics Korea, Bank of Korea, Financial Supervisory Service, Survey of Household Finances and Living Conditions", "source_kr": "통계청, 한국은행, 금융감독원, 가계금융복지조"}, #  부채('12~'17)
    {"orgId": "101", "tblId": "DT_1HDAAA01", "objL1" : "A0100", "objL2" : "B0500", "objL3" : "C06", "itmId": "T01", "prdSe": "Y", "name_en": "Average of all households Liabilities (10 thousand won)", "name_kr" : "전가구 평균부채 (만원)", "decimal_places": 2,
     "category_en": "Income, Consumption & Assets", "category_kr": "소득,소비,자산", "source_en": "Statistics Korea, Bank of Korea, Financial Supervisory Service, Survey of Household Finances and Living Conditions", "source_kr": "통계청, 한국은행, 금융감독원, 가계금융복지조"}, #  부채('18~)
    {"orgId": "101", "tblId": "DT_1J22001", "objL1" : "T10", "objL2" : "0", "itmId": "T", "prdSe": "Y", "name_en": "CPI (2020*100)", "name_kr" : "소비자물가조사 (2020=100)", "decimal_places": 2,
     "category_en": "Income, Consumption & Assets", "category_kr": "소득,소비,자산", "source_en": "Statistics Korea, Consumer Price Survey (Index)", "source_kr": "통계청, 소비자물가조사"}    
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
