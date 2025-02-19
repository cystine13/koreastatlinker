import os
import base64
import requests
import json
from datetime import datetime

# GitHub 정보
GITHUB_TOKEN = os.getenv("TOKEN")
GITHUB_REPO = "cystine13/koreastatlinker"  # 리포지토리 이름
GITHUB_FILE_PATH = "population_data.json"  # 업로드할 파일 경로
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"

# KOSIS API 인증키
API_KEY = os.getenv("KOSIS_API_KEY")

# API URL 및 공통 매개변수
BASE_URL = "https://kosis.kr/openapi/Param/statisticsParameterData.do"
current_year = datetime.now().year
common_params = {
    "method": "getList",
    "apiKey": API_KEY,
    "startPrdDe": "2000",  # 시작 연도
    "endPrdDe": str(current_year - 1),  # 종료 연도를 전년도 자동 설정
    "format": "json",
    "jsonVD": "Y"
}

# 데이터 수집 항목
items = [
    {"orgId": "101", "tblId": "DT_1IN1502", "objL1" : "00", "itmId": "T200", "prdSe": "Y", "name": "Household (households)", "decimal_places": 0, "category_en": "Population", "category_kr": "인구"},      # 가구수
    {"orgId": "101", "tblId": "DT_1B8000F", "objL1" : "11", "itmId": "T1", "prdSe": "Y", "name": "Births (Person)", "decimal_places": 0, "category_en": "Population", "category_kr": "인구"},      # 출생아수    
    {"orgId": "101", "tblId": "DT_1PL1502", "itmId": "T00", "objL1" : "00", "objL2" : "000", "prdSe": "Y", "name": "One Person Households (household)", "decimal_places": 0, "category_en": "Population", "category_kr": "인구"},  # 1인가구('15~)
    {"orgId": "101", "tblId": "DT_1B8000H", "itmId": "T12", "objL1" : "00", "prdSe": "Y", "name": "Total Fertility Rate (per woman of childbearing age)", "decimal_places": 3, "category_en": "Population", "category_kr": "인구"},  # 합계출산율('90~)
    {"orgId": "101", "tblId": "DT_1B8000F", "itmId": "T1", "objL1" : "41", "prdSe": "Y", "name": "Marriages (cases)", "decimal_places": 0, "category_en": "Population", "category_kr": "인구"},  # 혼인건수('70~)
    {"orgId": "101", "tblId": "DT_1JC1516", "itmId": "T30", "objL1" : "00", "objL2" : "00", "prdSe": "Y", "name": "Average size of household members (In person)", "decimal_places": 1, "category_en": "Population", "category_kr": "인구"},  #  평균가구원수('15~)
    {"orgId": "101", "tblId": "DT_1JD1501", "itmId": "T10", "objL1" : "00", "prdSe": "Y", "name": "Multicultural Households (household)", "decimal_places": 0, "category_en": "Population", "category_kr": "인구"},  #  다문화가구('15~)
    {"orgId": "111", "tblId": "DT_1B040A8", "objL1": "AAX000", "objL2": "13102870964B.0", "objL3": "AAB000", "itmId": "13103870964T1", "prdSe": "Y", "name": "Registered Foreigners (Person)", "decimal_places": 0, "category_en": "Population", "category_kr": "인구"},      # 등록외국인('09~)    
    {"orgId": "101", "tblId": "DT_1B040A3", "objL1" : "00", "itmId": "T20", "prdSe": "Y", "name": "Resident Population (Person)", "decimal_places": 0, "category_en": "Population", "category_kr": "인구"},  # 주민등록인구
    {"orgId": "101", "tblId": "DT_1B26003_A01", "itmId": "T70", "objL1" : "00", "objL2" : "00", "prdSe": "Y", "name": "Internal Migrants (Person)", "decimal_places": 0, "category_en": "Population", "category_kr": "인구"},  # 국내인구 이동자수('70~)
    {"orgId": "101", "tblId": "DT_1B040B3", "objL1" : "00", "itmId": "T1", "prdSe": "Y", "name": "Resident Households (households)", "decimal_places": 0, "category_en": "Population", "category_kr": "인구"},      # 주민등록세대수
    {"orgId": "101", "tblId": "DT_1B08024", "itmId": "T7", "objL1" : "00", "prdSe": "Y", "name": "Population Density (Per ㎢)", "decimal_places": 1, "category_en": "Population", "category_kr": "인구"},  # 인구밀도('66~)
    {"orgId": "101", "tblId": "DT_1B41", "objL1" : "01", "itmId": "T6", "prdSe": "Y", "name": "Expectation of life at age (Years)", "decimal_places": 1, "category_en": "Health & Welfare", "category_kr": "보건,복지"},      # 기대수명
    {"orgId": "101", "tblId": "DT_1B8000F", "objL1" : "12", "itmId": "T1", "prdSe": "Y", "name": "Deaths (Person)", "decimal_places": 0, "category_en": "Health & Welfare", "category_kr": "보건,복지"},      # 사망자수
    {"orgId": "101", "tblId": "DT_1B34E01", "objL1" : "J06", "objL2" : "0", "objL3" : "00", "itmId": "T5", "prdSe": "Y", "name": "Intentional self-harm (per 100 thousand person)", "decimal_places": 1, "category_en": "Health & Welfare", "category_kr": "보건,복지"},      # 자살율
    {"orgId": "177", "tblId": "DT_11702_N101", "itmId": "RATIO", "objL1" : "1", "objL2" : "103", "prdSe": "Y", "name": "Rate of Obesity (%)", "decimal_places": 1, "category_en": "Health & Welfare", "category_kr": "보건,복지"},      # 비만율
    {"orgId": "117", "tblId": "DT_11714_N001", "itmId": "TT", "objL1" : "00", "prdSe": "Y", "name": "Recipient of National Basic Livelihood (person)", "decimal_places": 0, "category_en": "Health & Welfare", "category_kr": "보건,복지"},      # 국민기초생활수급자
    {"orgId": "350", "tblId": "TX_35003_A003", "itmId": "16350AAB7", "objL1" : "11101HJG00", "objL2" : "15350AB000", "prdSe": "Y", "name": "Medical Personnel (person)", "decimal_places": 0, "category_en": "Health & Welfare", "category_kr": "보건,복지"},      # 의료인력수
    {"orgId": "117", "tblId": "DT_117N_A00023", "itmId": "16117ac000101", "objL1" : "15117AC000101", "objL2" : "11101SSB20", "objL3" : "15117AC001101", "prdSe": "Y", "name": "Cancers (person)", "decimal_places": 0, "category_en": "Health & Welfare", "category_kr": "보건,복지"},      # 암발생자수
    {"orgId": "177", "tblId": "DT_11702_N012", "itmId": "RATIO", "objL1" : "1", "objL2" : "103", "prdSe": "Y", "name": "Monthly Alcohol Drinking (%)", "decimal_places": 1, "category_en": "Health & Welfare", "category_kr": "보건,복지"},      # 음주율   
    {"orgId": "101", "tblId": "DT_1B34E01", "objL1" : "0", "objL2" : "0", "objL3" : "00", "itmId": "T1", "prdSe": "Y", "name": "Mortality rate (per 100 thousand person)", "decimal_places": 0, "category_en": "Health & Welfare", "category_kr": "보건,복지"},      # 사망률
    {"orgId": "117", "tblId": "DT_11761_N005", "itmId": "00", "objL1" : "00", "objL2" : "CHUT0", "objL3" : "TT", "prdSe": "Y", "name": "Number of The Registered Disabled (person)", "decimal_places": 0, "category_en": "Health & Welfare", "category_kr": "보건,복지"},      # 장애인인구
    {"orgId": "350", "tblId": "DT_35007_N130", "itmId": "001", "objL1" : "15350AC400Z1", "objL2" : "001", "objL3" : "001", "prdSe": "Y", "name": "Average Height (cm)", "decimal_places": 2, "category_en": "Health & Welfare", "category_kr": "보건,복지"},      # 평균신장
    {"orgId": "117", "tblId": "DT_15407_NN001", "itmId": "A", "objL1" : "01", "prdSe": "Y", "name": "Child Care Center (Place)", "decimal_places": 0, "category_en": "Health & Welfare", "category_kr": "보건,복지"},      # 어린이집수
    {"orgId": "101", "tblId": "DT_1DA7001S", "objL1" : "0", "itmId": "T80", "prdSe": "Y", "name": "Unemployment rate (%)", "decimal_places": 1, "category_en": "Education & Labor", "category_kr": "교육,노동"},      # 실업률
    {"orgId": "101", "tblId": "DT_1DA7001S", "objL1" : "0", "itmId": "T90", "prdSe": "Y", "name": "Employment to population ratio (%)", "decimal_places": 1, "category_en": "Education & Labor", "category_kr": "교육,노동"},      # 고용률
    {"orgId": "101", "tblId": "DT_1DA7001S", "itmId": "T20", "objL1" : "0", "prdSe": "Y", "name": "Economically Active Population (Thousand Person)", "decimal_places": 0, "category_en": "Education & Labor", "category_kr": "교육,노동"},      # 경제활동인구
    {"orgId": "334", "tblId": "DT_1963003_002", "itmId": "00", "objL1" : "00", "objL2" : "A001", "objL3" : "C_1", "prdSe": "Y", "name": "Elementary School Students (Person)", "decimal_places": 0, "category_en": "Education & Labor", "category_kr": "교육,노동"},      # 초등학교 학생수
    {"orgId": "334", "tblId": "DT_1963003_003", "itmId": "00", "objL1" : "00", "objL2" : "A001", "objL3" : "H_1", "prdSe": "Y", "name": "Middle School Students (Person)", "decimal_places": 0, "category_en": "Education & Labor", "category_kr": "교육,노동"},      # 중학교 학생수
    {"orgId": "334", "tblId": "DT_1963003_004", "itmId": "00", "objL1" : "00", "objL2" : "A001", "objL3" : "H_1", "prdSe": "Y", "name": "High School Students (Person)", "decimal_places": 0, "category_en": "Education & Labor", "category_kr": "교육,노동"},      # 고등학교 학생수
    {"orgId": "344", "tblId": "DT_344N_1D8A_AA", "itmId": "T001", "objL1" : "TOTAL", "prdSe": "Y", "name": "Indices of Labor Productivity (2020=100)", "decimal_places": 1, "category_en": "Education & Labor", "category_kr": "교육,노동"},      # 노동생산성지수
    {"orgId": "118", "tblId": "DT_118N_MON041", "itmId": "13103110311MD_7", "objL1" : "15118INDUSTRY_9S0", "objL2" : "size01", "prdSe": "Y", "name": "Total hours Worked (Hour)", "decimal_places": 1, "category_en": "Education & Labor", "category_kr": "교육,노동"},      # 근로시간('11~'19)    
    {"orgId": "118", "tblId": "DT_118N_MON051", "itmId": "13103110311MD_7", "objL1" : "190326INDUSTRY_10S0", "objL2" : "size01", "prdSe": "Y", "name": "Total hours Worked (Hour)", "decimal_places": 1, "category_en": "Education & Labor", "category_kr": "교육,노동"},      # 근로시간('20~)    
    {"orgId": "101", "tblId": "DT_1HDCA02_HF", "objL1" : "A0100", "objL2" : "B3000", "objL3" : "C06", "itmId": "T01", "prdSe": "Y", "name": "Liabilities (10 thousand won)", "decimal_places": 2, "category_en": "Income, Consumption & Assets", "category_kr": "소득,소비,자산"},      # 부채('10~'11)
    {"orgId": "101", "tblId": "DT_1HDBA01", "objL1" : "A0100", "objL2" : "B0500", "objL3" : "C06", "itmId": "T01", "prdSe": "Y", "name": "Liabilities (10 thousand won)", "decimal_places": 2, "category_en": "Income, Consumption & Assets", "category_kr": "소득,소비,자산"},      # 부채('12~'17)
    {"orgId": "101", "tblId": "DT_1HDAAA01", "objL1" : "A0100", "objL2" : "B0500", "objL3" : "C06", "itmId": "T01", "prdSe": "Y", "name": "Liabilities (10 thousand won)", "decimal_places": 2, "category_en": "Income, Consumption & Assets", "category_kr": "소득,소비,자산"},      # 부채('18~)
    {"orgId": "101", "tblId": "DT_1J22001", "objL1" : "T10", "objL2" : "0", "itmId": "T", "prdSe": "Y", "name": "CPI (2020*100)", "decimal_places": 2, "category_en": "Income, Consumption & Assets", "category_kr": "소득,소비,자산"},      # 소비자물가지수('65~)    
    {"orgId": "132", "tblId": "TX_132_2009_H1001", "objL1" : "15132JJB001", "itmId": "T01", "prdSe": "Y", "name": "Crime Occurrence (Cases)", "decimal_places": 0, "category_en": "Crime & Safety", "category_kr": "범죄와 안전"},      # 범죄발생건수('90~'10)    
    {"orgId": "132", "tblId": "DT_13204_2011_211", "objL1" : "00", "itmId": "AA", "prdSe": "Y", "name": "Crime Occurrence (Cases)", "decimal_places": 0, "category_en": "Crime & Safety", "category_kr": "범죄와 안전"},      # 범죄발생건수('11~'22)
    {"orgId": "132", "tblId": "DT_132004_A001", "objL1" : "A01", "objL2" : "B01", "itmId": "T001", "prdSe": "Y", "name": "Crime Occurrence (Cases)", "decimal_places": 0, "category_en": "Crime & Safety", "category_kr": "범죄와 안전"},      # 범죄발생건수('23~)
    {"orgId": "117", "tblId": "DT_117064_A009", "objL1" : "B01", "itmId": "T001", "prdSe": "Y", "name": "Child Abuse (Cases)", "decimal_places": 0, "category_en": "Crime & Safety", "category_kr": "범죄와 안전"},      # 아동학대건수    
    {"orgId": "301", "tblId": "DT_200Y101", "objL1" : "13102136288ACC_ITEM.1010101", "itmId": "13103136288999", "prdSe": "Y", "name": "GDP (Hund.M U$)", "decimal_places": 1, "category_en": "Economy & Market", "category_kr": "경제일반,경기"},      # 국내총생산GDP
    {"orgId": "116", "tblId": "DT_MLTM_2300", "objL1" : "13102874596A.0001", "objL2" : "13102874596B.0001", "objL3" : "13102874596C.0001", "itmId": "13103874596T1", "prdSe": "Y", "name": "Area of the land (㎡)", "decimal_places": 1, "category_en": "Land Use", "category_kr": "국토이용"},      # 국토면적
    {"orgId": "343", "tblId": "DT_343_2010_S0027", "objL1" : "13102792814A.02", "itmId": "13103792814T1", "prdSe": "Y", "name": "KOSPI Index (1980.1.4=100)", "decimal_places": 2, "category_en": "Economy & Market", "category_kr": "경제일반,경기"},      # KOSPI 지수('76~)
    {"orgId": "101", "tblId": "DT_1F02001", "objL1" : "00", "objL2" : "C", "itmId": "T10", "prdSe": "Y", "name": "Index of Manufacturing Production (2020=100)", "decimal_places": 1, "category_en": "Mining & Manufacturing", "category_kr": "광업,제조업"},      # 제조업생산지수('75~)
    {"orgId": "101", "tblId": "DT_1KC2020", "objL1" : "T", "itmId": "T2", "prdSe": "Y", "name": "Index of Services Production (2020=100)", "decimal_places": 1, "category_en": "Retail, Wholesale and Services", "category_kr": "도소매,서비스"},      # 서비스업생산지수('00~)
    {"orgId": "101", "tblId": "DT_1KE10041", "objL1" : "000", "objL2" : "00", "itmId": "T20", "prdSe": "Y", "name": "Transaction value of Online shopping mall (Million Won)", "decimal_places": 0, "category_en": "Retail, Wholesale and Services", "category_kr": "도소매,서비스"},      # 온라인쇼핑몰거래액('17~)
    {"orgId": "337", "tblId": "DT_337001_001", "objL1" : "B002", "itmId": "T001", "prdSe": "Y", "name": "New and Renewable Energy Production (toe)", "decimal_places": 0, "category_en": "Enviroment & Energy", "category_kr": "환경,에너지"}      # 신재생에너지생산량('16~)
]

# 데이터 수집 및 저장
data_by_year = {str(year): {} for year in range(int(common_params["startPrdDe"]), int(common_params["endPrdDe"]) + 1)}

for item in items:
    # 필요 매개변수만 params에 추가
    params = {**common_params, "orgId": item["orgId"], "tblId": item["tblId"], "itmId": item["itmId"], "prdSe": item["prdSe"]}
    if "objL1" in item:
        params["objL1"] = item["objL1"]
    if "objL2" in item:
        params["objL2"] = item["objL2"]
    if "objL3" in item:
        params["objL3"] = item["objL3"]

    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        for entry in data:
            year = entry["PRD_DE"]
            value = entry["DT"]
            if year in data_by_year:  # 정의된 연도 범위 내 데이터만 처리
                # 소수점 자리수에 맞게 값 포맷팅
                decimal_places = item.get("decimal_places", 2)
                formatted_value = round(float(value), decimal_places)
                # 천 단위 콤마 추가
                formatted_with_commas = f"{formatted_value:,.{decimal_places}f}"
                
                data_by_year[year][item["name"]] = {
                    "value": formatted_with_commas,
                    "category_en": item["category_en"],
                    "category_kr": item["category_kr"]
                }
    else:
        print(f"Failed to fetch {item['name']} data. Status code:", response.status_code)

# JSON 파일 생성
json_content = json.dumps(data_by_year, ensure_ascii=False, indent=4)

# Base64로 인코딩
encoded_content = base64.b64encode(json_content.encode("utf-8")).decode("utf-8")

# GitHub에 JSON 파일 업로드
def upload_to_github(content, message):
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    # 현재 파일 상태 확인 (sha 값 가져오기)
    get_response = requests.get(GITHUB_API_URL, headers=headers)
    sha = get_response.json().get("sha") if get_response.status_code == 200 else None

    # 업로드 데이터
    data = {
        "message": message,
        "content": content,  # Base64 인코딩된 내용
    }
    if sha:
        data["sha"] = sha  # 기존 파일 덮어쓰기

    # 파일 업로드 요청
    put_response = requests.put(GITHUB_API_URL, headers=headers, json=data)
    return put_response.status_code, put_response.json()

# GitHub에 업로드 실행
status_code, result = upload_to_github(encoded_content, "Update population_data.json")
if status_code in [200, 201]:
    print("GitHub update succeeded.")
else:
    print("GitHub update failed.")
    print(result)
