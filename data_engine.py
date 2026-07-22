import os
import re
import pandas as pd
import numpy as np

SUSI_EXCEL_PATH = os.path.join(os.path.dirname(__file__), "2026 IDA입시연구소 수시배치표 ver.10 통합엑셀.xlsx")
JUNGSI_EXCEL_PATH = os.path.join(os.path.dirname(__file__), "정시_전국.xlsx")
SUSI_CACHE_PKL = os.path.join(os.path.dirname(__file__), "susi_cache.pkl")
JUNGSI_CACHE_PKL = os.path.join(os.path.dirname(__file__), "jungsi_cache.pkl")

UNIV_RANK_TIER = {
    "서울대": 1, "서울대학교": 1, "연세대": 2, "연세대학교": 2, "고려대": 2, "고려대학교": 2,
    "서강대": 3, "서강대학교": 3, "성균관대": 3, "성균관대학교": 3, "한양대": 3, "한양대학교": 3, "이화여대": 3, "이화여자대학교": 3,
    "중앙대": 4, "중앙대학교": 4, "경희대": 4, "경희대학교": 4, "한국외대": 4, "한국외국어대학교": 4, "서울시립대": 4, "서울시립대학교": 4,
    "건국대": 5, "건국대학교": 5, "동국대": 5, "동국대학교": 5, "홍익대": 5, "홍익대학교": 5, "숙명여대": 5, "숙명여자대학교": 5,
    "국민대": 6, "국민대학교": 6, "숭실대": 6, "숭실대학교": 6, "세종대": 6, "세종대학교": 6, "단국대": 6, "단국대학교": 6,
    "인하대": 6, "인하대학교": 6, "아주대": 6, "아주대학교": 6, "가천대": 6, "가천대학교": 6, "광운대": 6, "광운대학교": 6,
    "명지대": 7, "명지대학교": 7, "상명대": 7, "상명대학교": 7, "가톨릭대": 7, "가톨릭대학교": 7, "부산대": 7, "부산대학교": 7, "경북대": 7, "경북대학교": 7,
    "인천대": 8, "인천대학교": 8, "경기대": 8, "경기대학교": 8, "성신여대": 8, "성신여자대학교": 8, "덕성여대": 8, "덕성여자대학교": 8,
    "전남대": 8, "전남대학교": 8, "충남대": 8, "충남대학교": 8, "전북대": 8, "전북대학교": 8, "충북대": 8, "충북대학교": 8
}

# 주요 대학별 2025/2026학년도 수시 모집요강 검정고시 환산 등급표 (공식 비교내신 구간 매핑)
UNIV_GED_TABLES = {
    # 1. 공주대학교 (공식 모집요강: 100점=3.00등급, 95점=4.00등급, 90점=5.00등급, 85점=6.00등급, 80점=7.00등급, 75점=8.00등급, 70점=9.00등급)
    '공주대학교': [(100, 3.00), (95, 4.00), (90, 5.00), (85, 6.00), (80, 7.00), (75, 8.00), (70, 9.00)],
    '국립공주대학교': [(100, 3.00), (95, 4.00), (90, 5.00), (85, 6.00), (80, 7.00), (75, 8.00), (70, 9.00)],
    '공주대': [(100, 3.00), (95, 4.00), (90, 5.00), (85, 6.00), (80, 7.00), (75, 8.00), (70, 9.00)],

    # 2. 충북대학교 (공식 모집요강: 100점=3.00등급, 95점=3.50등급, 90점=4.00등급, 80점=4.50등급)
    '충북대학교': [(100, 3.00), (95, 3.50), (90, 4.00), (80, 4.50), (70, 5.00), (0, 9.00)],
    '충북대': [(100, 3.00), (95, 3.50), (90, 4.00), (80, 4.50), (70, 5.00), (0, 9.00)],

    # 2. 가천대학교 (100점 1.00등급 / 98점 2.00등급 / 95점 3.00등급 / 90점 4.00등급)
    '가천대학교': [(100, 1.00), (98, 2.00), (95, 3.00), (90, 4.00), (85, 5.00), (0, 6.00)],
    '가천대': [(100, 1.00), (98, 2.00), (95, 3.00), (90, 4.00), (85, 5.00), (0, 6.00)],

    # 3. 삼육대 / 서경대 / 을지대 (100점 1.00등급 / 98점 1.50등급 / 95점 2.00등급 / 90점 3.00등급)
    '삼육대학교': [(100, 1.00), (98, 1.50), (95, 2.00), (90, 3.00), (85, 4.00), (0, 5.00)],
    '삼육대': [(100, 1.00), (98, 1.50), (95, 2.00), (90, 3.00), (85, 4.00), (0, 5.00)],
    '서경대학교': [(100, 1.00), (98, 1.50), (95, 2.00), (90, 3.00), (85, 4.00), (0, 5.00)],
    '서경대': [(100, 1.00), (98, 1.50), (95, 2.00), (90, 3.00), (85, 4.00), (0, 5.00)],
    '을지대학교': [(100, 1.00), (98, 1.50), (95, 2.00), (90, 3.00), (85, 4.00), (0, 5.00)],
    '을지대': [(100, 1.00), (98, 1.50), (95, 2.00), (90, 3.00), (85, 4.00), (0, 5.00)],

    # 4. 명지대학교 (100점 3.00등급 / 98점 3.50등급 / 95점 4.00등급 / 90점 5.00등급)
    '명지대학교': [(100, 3.00), (98, 3.50), (95, 4.00), (90, 5.00), (85, 6.00), (0, 7.00)],
    '명지대': [(100, 3.00), (98, 3.50), (95, 4.00), (90, 5.00), (85, 6.00), (0, 7.00)],

    # 5. 충남대학교 (2026 수시 모집요강 공식: 95점 이상 75점 부여 = 3.50등급 / 100점도 3.50등급)
    '충남대학교': [(95, 3.50), (90, 4.50), (85, 5.50), (80, 6.50), (0, 7.50)],
    '충남대': [(95, 3.50), (90, 4.50), (85, 5.50), (80, 6.50), (0, 7.50)],

    # 6. 여대 라인 & 수원대 (100점 1.50등급 / 98점 2.00등급 / 95점 2.50등급 / 90점 3.50등급)
    '덕성여자대학교': [(100, 1.50), (98, 2.00), (95, 2.50), (90, 3.50), (85, 4.50), (0, 5.50)],
    '덕성여대': [(100, 1.50), (98, 2.00), (95, 2.50), (90, 3.50), (85, 4.50), (0, 5.50)],
    '서울여자대학교': [(100, 1.50), (98, 2.00), (95, 2.50), (90, 3.50), (85, 4.50), (0, 5.50)],
    '서울여대': [(100, 1.50), (98, 2.00), (95, 2.50), (90, 3.50), (85, 4.50), (0, 5.50)],
    '동덕여자대학교': [(100, 1.50), (98, 2.00), (95, 2.50), (90, 3.50), (85, 4.50), (0, 5.50)],
    '동덕여대': [(100, 1.50), (98, 2.00), (95, 2.50), (90, 3.50), (85, 4.50), (0, 5.50)],
    '성신여자대학교': [(100, 1.50), (98, 2.00), (95, 2.50), (90, 3.50), (85, 4.50), (0, 5.50)],
    '성신여대': [(100, 1.50), (98, 2.00), (95, 2.50), (90, 3.50), (85, 4.50), (0, 5.50)],
    '수원대학교': [(100, 1.50), (98, 2.00), (95, 2.50), (90, 3.50), (85, 4.50), (0, 5.50)],
    '수원대': [(100, 1.50), (98, 2.00), (95, 2.50), (90, 3.50), (85, 4.50), (0, 5.50)],

    # 7. 수도권 주요 4년제 (경기대 / 한성대 / 동국대 / 숭실대 / 단국대 / 국민대 / 세종대 / 광운대 / 아주대 / 인하대 / 인천대 등)
    '경기대학교': [(100, 2.00), (98, 2.50), (95, 3.00), (90, 4.00), (85, 5.00), (0, 6.00)],
    '경기대': [(100, 2.00), (98, 2.50), (95, 3.00), (90, 4.00), (85, 5.00), (0, 6.00)],
    '한성대학교': [(100, 2.00), (98, 2.50), (95, 3.00), (90, 4.00), (85, 5.00), (0, 6.00)],
    '한성대': [(100, 2.00), (98, 2.50), (95, 3.00), (90, 4.00), (85, 5.00), (0, 6.00)],
    '동국대학교': [(100, 2.00), (98, 2.50), (95, 3.00), (90, 4.00), (85, 5.00), (0, 6.00)],
    '동국대': [(100, 2.00), (98, 2.50), (95, 3.00), (90, 4.00), (85, 5.00), (0, 6.00)],
    '숭실대학교': [(100, 2.00), (98, 2.50), (95, 3.00), (90, 4.00), (85, 5.00), (0, 6.00)],
    '숭실대': [(100, 2.00), (98, 2.50), (95, 3.00), (90, 4.00), (85, 5.00), (0, 6.00)],
    '단국대학교': [(100, 2.00), (98, 2.50), (95, 3.00), (90, 4.00), (85, 5.00), (0, 6.00)],
    '단국대': [(100, 2.00), (98, 2.50), (95, 3.00), (90, 4.00), (85, 5.00), (0, 6.00)],
    '국민대학교': [(100, 2.00), (98, 2.50), (95, 3.00), (90, 4.00), (85, 5.00), (0, 6.00)],
    '국민대': [(100, 2.00), (98, 2.50), (95, 3.00), (90, 4.00), (85, 5.00), (0, 6.00)],
    '세종대학교': [(100, 2.00), (98, 2.50), (95, 3.00), (90, 4.00), (85, 5.00), (0, 6.00)],
    '세종대': [(100, 2.00), (98, 2.50), (95, 3.00), (90, 4.00), (85, 5.00), (0, 6.00)],
    '광운대학교': [(100, 2.00), (98, 2.50), (95, 3.00), (90, 4.00), (85, 5.00), (0, 6.00)],
    '광운대': [(100, 2.00), (98, 2.50), (95, 3.00), (90, 4.00), (85, 5.00), (0, 6.00)],
    '아주대학교': [(100, 2.00), (98, 2.50), (95, 3.00), (90, 4.00), (85, 5.00), (0, 6.00)],
    '아주대': [(100, 2.00), (98, 2.50), (95, 3.00), (90, 4.00), (85, 5.00), (0, 6.00)],
    '인하대학교': [(100, 2.00), (98, 2.50), (95, 3.00), (90, 4.00), (85, 5.00), (0, 6.00)],
    '인하대': [(100, 2.00), (98, 2.50), (95, 3.00), (90, 4.00), (85, 5.00), (0, 6.00)],
    '인천대학교': [(100, 2.00), (98, 2.50), (95, 3.00), (90, 4.00), (85, 5.00), (0, 6.00)],
    '인천대': [(100, 2.00), (98, 2.50), (95, 3.00), (90, 4.00), (85, 5.00), (0, 6.00)],
    '한양대학교(ERICA)': [(100, 2.00), (98, 2.50), (95, 3.00), (90, 4.00), (85, 5.00), (0, 6.00)],
    '고려대학교(세종)': [(100, 2.00), (98, 2.50), (95, 3.00), (90, 4.00), (85, 5.00), (0, 6.00)],
    '연세대학교(미래)': [(100, 2.00), (98, 2.50), (95, 3.00), (90, 4.00), (85, 5.00), (0, 6.00)],
    '한국공학대학교': [(100, 2.00), (98, 2.50), (95, 3.00), (90, 4.00), (85, 5.00), (0, 6.00)],
    '한국공학대': [(100, 2.00), (98, 2.50), (95, 3.00), (90, 4.00), (85, 5.00), (0, 6.00)],
    '한국항공대학교': [(100, 2.00), (98, 2.50), (95, 3.00), (90, 4.00), (85, 5.00), (0, 6.00)],
    '한국항공대': [(100, 2.00), (98, 2.50), (95, 3.00), (90, 4.00), (85, 5.00), (0, 6.00)],

    # 8. 지방 거점 국립대 (부산대, 경북대, 전남대, 전북대, 강원대, 제주대, 경상국립대, 부경대 등)
    '부산대학교': [(100, 2.50), (98, 3.00), (95, 3.50), (90, 4.50), (85, 5.50), (0, 6.50)],
    '부산대': [(100, 2.50), (98, 3.00), (95, 3.50), (90, 4.50), (85, 5.50), (0, 6.50)],
    '경북대학교': [(100, 2.50), (98, 3.00), (95, 3.50), (90, 4.50), (85, 5.50), (0, 6.50)],
    '경북대': [(100, 2.50), (98, 3.00), (95, 3.50), (90, 4.50), (85, 5.50), (0, 6.50)],
    '전남대학교': [(100, 2.50), (98, 3.00), (95, 3.50), (90, 4.50), (85, 5.50), (0, 6.50)],
    '전남대': [(100, 2.50), (98, 3.00), (95, 3.50), (90, 4.50), (85, 5.50), (0, 6.50)],
    '전북대학교': [(100, 2.50), (98, 3.00), (95, 3.50), (90, 4.50), (85, 5.50), (0, 6.50)],
    '전북대': [(100, 2.50), (98, 3.00), (95, 3.50), (90, 4.50), (85, 5.50), (0, 6.50)],
    '강원대학교': [(100, 2.50), (98, 3.00), (95, 3.50), (90, 4.50), (85, 5.50), (0, 6.50)],
    '강원대': [(100, 2.50), (98, 3.00), (95, 3.50), (90, 4.50), (85, 5.50), (0, 6.50)],
    '제주대학교': [(100, 2.50), (98, 3.00), (95, 3.50), (90, 4.50), (85, 5.50), (0, 6.50)],
    '제주대': [(100, 2.50), (98, 3.00), (95, 3.50), (90, 4.50), (85, 5.50), (0, 6.50)],
    '경상국립대학교': [(100, 2.50), (98, 3.00), (95, 3.50), (90, 4.50), (85, 5.50), (0, 6.50)],
    '경상국립대': [(100, 2.50), (98, 3.00), (95, 3.50), (90, 4.50), (85, 5.50), (0, 6.50)],
    '부경대학교': [(100, 2.50), (98, 3.00), (95, 3.50), (90, 4.50), (85, 5.50), (0, 6.50)],
    '부경대': [(100, 2.50), (98, 3.00), (95, 3.50), (90, 4.50), (85, 5.50), (0, 6.50)],
}

# 검정고시 교과전형 지원 불가 / 비교내신 미적용 대학 목록 (오직 논술전형만 허용)
TOP_TIER_NO_GED_GYOKA_UNIVS = [
    '서울대학교', '서울대', '연세대학교', '연세대', '고려대학교', '고려대',
    '서강대학교', '서강대', '성균관대학교', '성균관대', '한양대학교', '한양대',
    '중앙대학교', '중앙대', '경희대학교', '경희대', '한국외국어대학교', '한국외대',
    '이화여자대학교', '이화여대', '서울시립대학교', '서울시립대',
    '건국대학교', '건국대', '동국대학교', '동국대', '홍익대학교', '홍익대',
    '숙명여자대학교', '숙명여대', '국민대학교', '국민대', '숭실대학교', '숭실대',
    '세종대학교', '세종대', '광운대학교', '광운대', '단국대학교', '단국대',
    '아주대학교', '아주대', '인하대학교', '인하대', '한양대학교(ERICA)',
    '가천대학교', '가천대', '경기대학교', '경기대', '한국공학대학교', '한국공학대',
    '한국항공대학교', '한국항공대', '고려대학교(세종)', '연세대학교(미래)',
    '부산대학교', '부산대', '경북대학교', '경북대'
]

# 국공립 대학 식별 키워드
NATIONAL_PUBLIC_UNIV_KEYWORDS = [
    '서울대학교', '서울대', '부산대학교', '부산대', '경북대학교', '경북대',
    '전남대학교', '전남대', '전북대학교', '전북대', '충남대학교', '충남대',
    '충북대학교', '충북대', '강원대학교', '강원대', '제주대학교', '제주대',
    '경상국립대학교', '경상국립대', '서울시립대학교', '서울시립대', '인천대학교', '인천대',
    '서울과학기술대학교', '서울과기대', '한경국립대학교', '한경대', '한국교통대학교', '교통대',
    '한국해양대학교', '목포해양대학교', '해양대', '공주대학교', '공주대', '순천대학교', '순천대',
    '안동대학교', '안동대', '창원대학교', '창원대', '금오공과대학교', '금오공대',
    '목포대학교', '목포대', '군산대학교', '군산대', '강릉원주대학교', '강릉원주대',
    '한국전통문화대학교', '한국교원대학교', '교원대', '한국체육대학교', '한국체대',
    '경인교육대학교', '공주교육대학교', '광주교육대학교', '대구교육대학교', '부산교육대학교',
    '서울교육대학교', '전주교육대학교', '청주교육대학교', '춘천교육대학교', '진주교육대학교',
    '교대', '국립', '공립', '도립'
]

# 광역권 지역 매핑 (광역시/특별시 연계)
REGION_MAPPING = {
    '서울': '서울',
    '경기': '경기',
    '인천': '인천',
    '수도권': '서울|경기|인천',
    '충남': '충남|대전|충청',
    '대전': '충남|대전|충청',
    '충남/대전': '충남|대전|충청',
    '충북': '충북|세종|충청',
    '세종': '충북|세종|충청',
    '충북/세종': '충북|세종|충청',
    '경북': '경북|대구',
    '대구': '경북|대구',
    '경북/대구': '경북|대구',
    '경남': '경남|부산|울산',
    '부산': '경남|부산|울산',
    '울산': '경남|부산|울산',
    '경남/부산/울산': '경남|부산|울산',
    '전남': '전남|광주',
    '광주': '전남|광주',
    '전남/광주': '전남|광주',
    '전북': '전북',
    '강원': '강원',
    '제주': '제주'
}

# 대학 약칭/풀네임 검색 매핑
UNIV_ABBR_MAPPING = {
    '충남대': '충남대|충남대학교',
    '충북대': '충북대|충북대학교',
    '공주대': '공주대|공주대학교',
    '부산대': '부산대|부산대학교',
    '경북대': '경북대|경북대학교',
    '전남대': '전남대|전남대학교',
    '전북대': '전북대|전북대학교',
    '강원대': '강원대|강원대학교',
    '제주대': '제주대|제주대학교',
    '경상국립대': '경상국립대|경상국립대학교',
    '부경대': '부경대|부경대학교',
    '가천대': '가천대|가천대학교',
    '경기대': '경기대|경기대학교',
    '서경대': '서경대|서경대학교',
    '덕성여대': '덕성여대|덕성여자대학교',
    '서울여대': '서울여대|서울여자대학교',
    '동덕여대': '동덕여대|동덕여자대학교',
    '성신여대': '성신여대|성신여자대학교',
    '숙명여대': '숙명여대|숙명여자대학교',
    '이화여대': '이화여대|이화여자대학교',
    '서울대': '서울대|서울대학교',
    '연세대': '연세대|연세대학교',
    '고려대': '고려대|고려대학교',
    '서강대': '서강대|서강대학교',
    '성균관대': '성균관대|성균관대학교',
    '한양대': '한양대|한양대학교',
    '중앙대': '중앙대|중앙대학교',
    '경희대': '경희대|경희대학교',
    '한국외대': '한국외대|한국외국어대학교',
    '서울시립대': '서울시립대|서울시립대학교',
    '건국대': '건국대|건국대학교',
    '동국대': '동국대|동국대학교',
    '홍익대': '홍익대|홍익대학교',
    '국민대': '국민대|국민대학교',
    '숭실대': '숭실대|숭실대학교',
    '세종대': '세종대|세종대학교',
    '광운대': '광운대|광운대학교',
    '단국대': '단국대|단국대학교',
    '아주대': '아주대|아주대학교',
    '인하대': '인하대|인하대학교',
    '명지대': '명지대|명지대학교',
    '삼육대': '삼육대|삼육대학교',
    '상명대': '상명대|상명대학교',
    '한성대': '한성대|한성대학교',
    '수원대': '수원대|수원대학교',
    '을지대': '을지대|을지대학교'
}

# 대학교별 전형명 자동 변환 사전 (최신 수시 모집요강 기준)
ADMISSION_NAME_MAPPING = {
    # "대학명": {"엑셀 원본 세부전형명": "화면에 띄울 최신 전형명"}
    # 예시: "국민대학교": {"학교생활우수자전형": "국민프런티어II전형"}
    # 원장님이 확인하시는 대로 아래에 계속 추가해 주시면 됩니다.
}

class AdmissionDataEngine:
    def __init__(self):
        self.df_susi = None
        self.df_jungsi = None
        self._load_data()

    def is_national_public(self, univ_name):
        univ_str = str(univ_name).strip()
        if '남서울' in univ_str:
            return False
        return any(k in univ_str for k in NATIONAL_PUBLIC_UNIV_KEYWORDS)

    def get_univ_tier(self, univ_name):
        univ_name = str(univ_name).strip()
        for key, tier in UNIV_RANK_TIER.items():
            if key in univ_name:
                return tier
        return 20

    def _load_data(self):
        print("하바나-트리니티 대입 데이터 로딩 중...")
        # 1. 수시 데이터 캐시 빠른 로드
        if os.path.exists(SUSI_CACHE_PKL):
            try:
                self.df_susi = pd.read_pickle(SUSI_CACHE_PKL)
                print(f"수시 데이터 캐시 로드 완료: {len(self.df_susi)}개 모집단위")
            except Exception as e:
                print(f"수시 캐시 실패: {e}")
                self.df_susi = None

        if self.df_susi is None and os.path.exists(SUSI_EXCEL_PATH):
            try:
                df_s = pd.read_excel(SUSI_EXCEL_PATH, sheet_name="전체 대학", header=3)
                cols = df_s.columns.tolist()
                df_s = df_s.rename(columns={
                    cols[1]: '지역',
                    cols[2]: '대학',
                    cols[3]: '전형',
                    cols[4]: '세부전형',
                    cols[5]: '계열',
                    cols[6]: '학과',
                    cols[8]: '일정_2026',
                    cols[10]: '지원자격_2026',
                    cols[12]: '전형요소_2026',
                    cols[14]: '최저학력기준_2026',
                    cols[22]: '모집인원_2026',
                    cols[27]: '경쟁률_2023',
                    cols[28]: '경쟁률_2024',
                    cols[29]: '경쟁률_2025',
                    cols[39]: '입결컷_2023',
                    cols[40]: '입결컷_2024',
                    cols[42]: '입결컷_2025',
                    cols[55]: '학종_명문특목',
                    cols[56]: '학종_특목자사',
                    cols[57]: '학종_하위특목',
                    cols[58]: '학종_상위일반',
                    cols[59]: '일반고_컷'
                })
                df_s = df_s.dropna(subset=['대학', '학과']).copy()
                df_s['대학'] = df_s['대학'].astype(str).str.strip()
                df_s['학과'] = df_s['학과'].astype(str).str.strip()
                df_s['전형'] = df_s['전형'].fillna('전체').astype(str).str.strip()
                df_s['세부전형'] = df_s['세부전형'].fillna('').astype(str).str.strip()
                df_s['지역'] = df_s['지역'].fillna('기타').astype(str).str.strip()
                df_s['계열'] = df_s['계열'].fillna('공통').astype(str).str.strip()
                
                df_s['Cut_2025'] = df_s['일반고_컷'].apply(self._parse_grade).fillna(df_s['입결컷_2025'].apply(self._parse_grade))
                df_s['Cut_2024'] = df_s['입결컷_2024'].apply(self._parse_grade)
                df_s['Cut_2023'] = df_s['입결컷_2023'].apply(self._parse_grade)
                
                df_s['Cutoff_3yr'] = df_s.apply(self._calc_3yr_avg, axis=1)
                df_s['Univ_Tier'] = df_s['대학'].apply(self.get_univ_tier)
                
                self.df_susi = df_s
                try:
                    df_s.to_pickle(SUSI_CACHE_PKL)
                except Exception:
                    pass
                print(f"수시 데이터 엑셀 로드 및 캐시 저장 완료: {len(df_s)}개 모집단위")
            except Exception as e:
                print(f"수시 데이터 로드 실패: {e}")
                self.df_susi = pd.DataFrame()

        # 2. 정시 데이터 캐시 빠른 로드
        if os.path.exists(JUNGSI_CACHE_PKL):
            try:
                self.df_jungsi = pd.read_pickle(JUNGSI_CACHE_PKL)
                print(f"정시 데이터 캐시 로드 완료: {len(self.df_jungsi)}개 모집단위")
            except Exception as e:
                print(f"정시 캐시 실패: {e}")
                self.df_jungsi = None

        if self.df_jungsi is None and os.path.exists(JUNGSI_EXCEL_PATH):
            try:
                df_j = pd.read_excel(JUNGSI_EXCEL_PATH, sheet_name="Sheet1", header=3)
                cols_j = df_j.columns.tolist()
                df_j = df_j.rename(columns={
                    cols_j[0]: '대학',
                    cols_j[1]: '지역',
                    cols_j[2]: '군',
                    cols_j[3]: '수학반영',
                    cols_j[4]: '탐구반영',
                    cols_j[5]: '학과',
                    cols_j[6]: '모집인원',
                    cols_j[7]: '경쟁률_2025',
                    cols_j[14]: '경쟁률_2024',
                    cols_j[9]: 'cut1_2025',
                    cols_j[12]: '백분위70컷_2025',
                    cols_j[16]: 'cut1_2024',
                    cols_j[19]: '백분위70컷_2024',
                    cols_j[20]: '전형요소'
                })
                df_j = df_j.dropna(subset=['대학', '학과']).copy()
                df_j['대학'] = df_j['대학'].astype(str).str.strip()
                df_j['학과'] = df_j['학과'].astype(str).str.strip()
                df_j['지역'] = df_j['지역'].fillna('기타').astype(str).str.strip()
                df_j['군'] = df_j['군'].fillna('기타').astype(str).str.strip()
                
                df_j['Cut_2025'] = df_j['백분위70컷_2025'].apply(self._parse_float).fillna(df_j['cut1_2025'].apply(self._parse_float))
                df_j['Cut_2024'] = df_j['백분위70컷_2024'].apply(self._parse_float).fillna(df_j['cut1_2024'].apply(self._parse_float))
                df_j['Cutoff_3yr'] = df_j.apply(lambda r: r['Cut_2025'] if not pd.isna(r['Cut_2025']) else r['Cut_2024'], axis=1)
                df_j['Univ_Tier'] = df_j['대학'].apply(self.get_univ_tier)
                
                self.df_jungsi = df_j
                try:
                    df_j.to_pickle(JUNGSI_CACHE_PKL)
                except Exception:
                    pass
                print(f"정시 데이터 엑셀 로드 및 캐시 저장 완료: {len(df_j)}개 모집단위")
            except Exception as e:
                print(f"정시 데이터 로드 실패: {e}")
                self.df_jungsi = pd.DataFrame()

    def _calc_3yr_avg(self, row):
        c25 = row['Cut_2025']
        c24 = row['Cut_2024']
        c23 = row['Cut_2023']
        vals = []
        weights = []
        if not pd.isna(c25): vals.append(c25); weights.append(0.5)
        if not pd.isna(c24): vals.append(c24); weights.append(0.3)
        if not pd.isna(c23): vals.append(c23); weights.append(0.2)
        if not vals: return np.nan
        return float(np.average(vals, weights=weights))

    def _parse_grade(self, val):
        if pd.isna(val): return np.nan
        val_str = str(val).strip()
        match = re.search(r'([1-9]\.\d{1,2})', val_str)
        if match: return float(match.group(1))
        match_int = re.search(r'^([1-9])$', val_str)
        if match_int: return float(match_int.group(1))
        return np.nan

    def _parse_float(self, val):
        if pd.isna(val): return np.nan
        val_str = str(val).strip()
        match = re.search(r'(\d{1,3}\.?\d{0,2})', val_str)
        if match:
            try:
                num = float(match.group(1))
                if 0 <= num <= 100: return num
            except: pass
        return np.nan

    def convert_ged_to_gpa(self, ged_score, university_name, region):
        """
        2025/2026학년도 대학별 공식 검정고시 비교내신 환산표 적용 (선형 보간 정밀 산출):
        1. 개별 대학 공식 환산 구간 테이블 매핑
        2. 구간 사이 점수는 비율 선형 보간 (Linear Interpolation) 처리하여 96.0점 등에 정확한 등급 산출
        """
        score = float(ged_score)
        univ_name = str(university_name).strip()
        
        # 개별 대학 테이블 매핑
        table = None
        for u_key, t in UNIV_GED_TABLES.items():
            if u_key in univ_name:
                table = t
                break
        
        if table:
            # table format: [(cutoff_score, grade), ...] sorted descending by cutoff_score
            if score >= table[0][0]:
                return float(table[0][1])
            for i in range(len(table) - 1):
                high_s, high_g = table[i]
                low_s, low_g = table[i+1]
                if low_s <= score < high_s:
                    ratio = (high_s - score) / (high_s - low_s)
                    calc_grade = high_g + ratio * (low_g - high_g)
                    return round(calc_grade, 2)
            return float(table[-1][1])

        # 기본 일반 4년제 대학 (표준 환산 구간: 100점 2.00, 98점 2.50, 95점 3.00, 90점 4.00, 85점 5.00)
        if score >= 100: return 2.00
        elif score >= 98: return round(2.00 + (100 - score) / 2.0 * 0.50, 2)
        elif score >= 95: return round(2.50 + (98 - score) / 3.0 * 0.50, 2)
        elif score >= 90: return round(3.00 + (95 - score) / 5.0 * 1.00, 2)
        elif score >= 85: return round(4.00 + (90 - score) / 5.0 * 1.00, 2)
        else: return min(9.0, round(5.00 + (85 - score) / 85.0 * 4.00, 2))

    def diagnose_susi(self, input_type, score_val, region_filter="전체", univ_filter="전체", category_filter="전체", type_filter="전체", dept_filter="", univ_type_filter="전체", sort_by="status"):
        """
        수시 대입 진단 엔진:
        - input_type == 'ged' 인 경우:
          1) '학생부종합전형(학종)' 및 지원 불가 전형 자동 제외
          2) 교과 지원 불가 상위권/수도권 대학 자동 제외 (오직 논술만 비교내신 처리)
          3) 검정고시 인정 대학은 2026학년도 공식 비교내신 선형보간 정밀 환산표 적용
        """
        if self.df_susi is None or self.df_susi.empty:
            return []

        df = self.df_susi.copy()
        
        if region_filter and region_filter != "전체":
            region_pattern = REGION_MAPPING.get(region_filter, region_filter)
            df = df[df['지역'].str.contains(region_pattern, case=False, na=False)]
        if univ_filter and univ_filter != "전체":
            u_clean = univ_filter.strip()
            u_pattern = UNIV_ABBR_MAPPING.get(u_clean, u_clean)
            if '|' not in u_pattern and u_pattern.endswith('대'):
                stem = u_pattern[:-1]
                u_pattern = f"{stem}대|{stem}대학교"
            df = df[df['대학'].str.contains(u_pattern, case=False, na=False)]
        if category_filter != "전체":
            df = df[df['계열'].str.contains(category_filter, case=False, na=False)]
        if type_filter != "전체":
            df = df[df['전형'].str.contains(type_filter, case=False, na=False)]
        if dept_filter and dept_filter.strip():
            df = df[df['학과'].str.contains(dept_filter.strip(), case=False, na=False)]

        if univ_type_filter == "국공립":
            df = df[df['대학'].apply(self.is_national_public)]
        elif univ_type_filter == "사립":
            df = df[~df['대학'].apply(self.is_national_public)]

        results = []
        for _, row in df.iterrows():
            univ = str(row['대학'])
            region = str(row['지역'])
            t_type = str(row['전형'])
            sub_type = str(row['세부전형'])
            
            # 전형명 자동 변환 사전 적용
            if univ in ADMISSION_NAME_MAPPING and sub_type in ADMISSION_NAME_MAPPING[univ]:
                sub_type = ADMISSION_NAME_MAPPING[univ][sub_type]
                
            eligibility = str(row['지원자격_2026']) if not pd.isna(row['지원자격_2026']) else ''
            elements_str = str(row['전형요소_2026']) if not pd.isna(row['전형요소_2026']) else ''
            
            cutoff_3yr = row['Cutoff_3yr']
            cut_2025 = row['Cut_2025']
            cut_2024 = row['Cut_2024']
            cut_2023 = row['Cut_2023']
            tier = row['Univ_Tier']

            is_nonsul_flag = False
            user_grade_display = ""

            # 0. 비일반적 특별전형 (특수교육, 만학도, 성인학습자, 재직자, 장애인, 농어촌, 기회균형 등) 수시 전체(내신/검정고시 공통) 필터링
            combined_text = (t_type + " " + sub_type + " " + elements_str + " " + eligibility).lower()
            non_standard_keywords = [
                '특수교육', '특수교육대상자', '장애인', '장애인등', '장애인 등',
                '만학도', '성인학습자', '평생학습자', '재직자', '산업체', '선취업',
                '북한이탈주민', '탈북', '다문화', '서해5도', '군인', '부사관', '보훈', '국가유공자', '유공자',
                '농어촌', '농어촌학생', '기회균형', '기회 균형', '기회균등', '기회 균등', '사회배려', '사회통합',
                '특성화고재직자', '특성화고졸재직자', '차상위', '기초생활', '한부모'
            ]
            if any(kw in combined_text for kw in non_standard_keywords):
                continue

            # 검정고시 검색 시 필수 제외 및 정밀 비교내신 처리
            if input_type == 'ged':
                # 1. 학생부종합전형(학종), 서류평가 위주 전형, 실기/특기자 완전 제외
                if any(k in combined_text for k in ['종합', '학종', '학생부종합', '학생부 종합', '서류 100', '서류100', '서류 80', '서류80', '서류 70', '서류70', '실기', '특기자']):
                    continue
                
                # 2. 검정고시 지원 불가 / 자격 미달 키워드 엄격 제외
                ineligible_ged_keywords = [
                    '검정불가', '검정 불가', '검정고시 등 제외', '검정고시 제외', '검정제외', '검정고시 불허', '검정고시 불응',
                    '검정고시 출신자 제외', '검정고시 합격자 제외', '석차등급 산출 불가한자 제외', '석차등급 산출 불가', '석차등급 미산출',
                    '3개 학기', '3개학기', '5개 학기', '5개학기', '학교생활기록부 보유자', '학생부 보유자',
                    '학교장추천', '학교장 추천', '고교장추천', '고교장 추천', '고교별 추천', '고교별추천', '고교추천',
                    '학교별 추천', '학교별추천', '추천인원', '추천형', '지역인재', '지역 인재',
                    '지역균형', '지역 균형', '지역기회', '특성화고', '마이스터고', '전문계고', '고교졸업예정자', '졸업예정자만', '재학생만', '고교 졸업예정자'
                ]
                if any(kw in combined_text for kw in ineligible_ged_keywords):
                    continue

                # 3. 교과 지원 불가 상위권/수도권 대학 (오직 논술전형만 비교내신 지원 가능)
                is_top_tier = any(top_u in univ for top_u in TOP_TIER_NO_GED_GYOKA_UNIVS)
                is_nonsul = ('논술' in t_type or '논술' in sub_type or '논술' in elements_str)
                
                if is_top_tier:
                    if not is_nonsul:
                        continue
                    else:
                        is_nonsul_flag = True
                        user_grade_calc = 1.50  # 진단용 기준 등급
                        user_grade_display = "논술 비교내신 (논술점수 반영)"
                else:
                    user_grade_calc = self.convert_ged_to_gpa(score_val, univ, region)
                    user_grade_display = f"{user_grade_calc:.2f} 등급"

                user_grade = user_grade_calc
            else:
                user_grade = float(score_val)
                user_grade_display = f"{user_grade:.2f} 등급"
                
            if pd.isna(cutoff_3yr):
                continue
            else:
                diff = round(user_grade - cutoff_3yr, 2)
                
                if is_nonsul_flag:
                    status = "소신 (논술 100%/비교내신)"
                    status_code = 0
                else:
                    # 사용자 정의 정밀 진단 기준 (수정됨):
                    # 소신: 환산등급 대비 +0.15 초과 ~ +0.20 이하 등급 상향 (0.15 < diff <= 0.20)
                    # 적정: 환산등급 대비 -0.20 이상 ~ +0.15 이하 등급 (-0.20 <= diff <= 0.15)
                    # 안정: 환산등급 대비 -0.30 이상 ~ -0.20 미만 등급 하향 (-0.30 <= diff < -0.20)
                    if diff > 0.20 or diff < -0.30:
                        continue
                    elif diff > 0.15:
                        status = "소신 (경쟁적)"
                        status_code = 0
                    elif diff >= -0.20:
                        status = "적정 (합격유력)"
                        status_code = 1
                    else:
                        status = "안정 (매우유리)"
                        status_code = 2
            
            elements = str(row['전형요소_2026']) if not pd.isna(row['전형요소_2026']) else '학생부 100%'
            requirements = str(row['최저학력기준_2026']) if not pd.isna(row['최저학력기준_2026']) else '없음'

            results.append({
                'id': f"susi_{row.name}",
                'univ': univ,
                'tier': tier,
                'region': region,
                'type': t_type,
                'sub_type': sub_type,
                'category': str(row['계열']),
                'department': str(row['학과']),
                'capacity': str(row['모집인원_2026']) if not pd.isna(row['모집인원_2026']) else '-',
                'competition_2025': str(row['경쟁률_2025']) if not pd.isna(row['경쟁률_2025']) else '-',
                'competition_2024': str(row['경쟁률_2024']) if not pd.isna(row['경쟁률_2024']) else '-',
                'cutoff_3yr': round(cutoff_3yr, 2),
                'cut_2025': round(cut_2025, 2) if not pd.isna(cut_2025) else '-',
                'cut_2024': round(cut_2024, 2) if not pd.isna(cut_2024) else '-',
                'cut_2023': round(cut_2023, 2) if not pd.isna(cut_2023) else '-',
                'user_grade': user_grade_display,
                'diff': diff,
                'status': status,
                'status_code': status_code,
                'elements': elements,
                'requirements': requirements,
                'eligibility': eligibility if eligibility else '전체',
                'schedule': str(row['일정_2026']) if not pd.isna(row.get('일정_2026')) else '-',
                'hakjong_scores': {
                    'myungmun': str(row['학종_명문특목']) if not pd.isna(row.get('학종_명문특목')) else '-',
                    'teukmok': str(row['학종_특목자사']) if not pd.isna(row.get('학종_특목자사')) else '-',
                    'low_teukmok': str(row['학종_하위특목']) if not pd.isna(row.get('학종_하위특목')) else '-',
                    'high_ilban': str(row['학종_상위일반']) if not pd.isna(row.get('학종_상위일반')) else '-',
                    'ilban': str(row['일반고_컷']) if not pd.isna(row.get('일반고_컷')) else '-'
                } if '종합' in t_type else None
            })
            
        if sort_by == "rank":
            results.sort(key=lambda x: (x['tier'], x['status_code'], x['cutoff_3yr'], x['univ'], x['department']))
        else: # status 기본 (소신(0) -> 적정(1) -> 안정(2))
            results.sort(key=lambda x: (x['status_code'], x['tier'], x['cutoff_3yr'], x['univ'], x['department']))

        return results

    def diagnose_jungsi(self, percentile_val, region_filter="전체", group_filter="전체", dept_filter="", sort_by="status"):
        """
        정시 표준 대입 상담 진단 범주 (상식선 범위 반영):
        - 소신 (경쟁적 / 현실적 상향): -4.0 <= diff < -1.0
        - 적정 (합격유력 / 적정 타겟): -1.0 <= diff <= 3.0
        - 안정 (매우유리 / 현실적 하향안정): 3.0 < diff <= 10.0
        """
        if self.df_jungsi is None or self.df_jungsi.empty:
            return []

        df = self.df_jungsi.copy()
        
        if region_filter and region_filter != "전체":
            region_pattern = REGION_MAPPING.get(region_filter, region_filter)
            df = df[df['지역'].str.contains(region_pattern, case=False, na=False)]
        if group_filter != "전체":
            df = df[df['군'].str.contains(group_filter, case=False, na=False)]
        if dept_filter and dept_filter != "":
            df = df[df['학과'].str.contains(dept_filter, case=False, na=False)]

        results = []
        user_p = float(percentile_val)
        
        for _, row in df.iterrows():
            univ = str(row['대학'])
            region = str(row['지역'])
            group = str(row['군'])
            
            # 정시 비일반적 특별전형 (특수교육, 만학도, 성인학습자, 재직자, 장애인, 농어촌, 기회균형 등) 필터링
            t_type = str(row.get('전형', '')) if '전형' in row else ''
            sub_type = str(row.get('세부전형', '')) if '세부전형' in row else ''
            dept = str(row.get('학과', '')) if '학과' in row else ''
            elements_str = str(row.get('전형요소', '')) if '전형요소' in row else ''
            
            combined_jungsi_text = (t_type + " " + sub_type + " " + dept + " " + elements_str).lower()
            non_standard_keywords = [
                '특수교육', '특수교육대상자', '장애인', '장애인등', '장애인 등',
                '만학도', '성인학습자', '평생학습자', '재직자', '산업체', '선취업',
                '북한이탈주민', '탈북', '다문화', '서해5도', '군인', '부사관', '보훈', '국가유공자', '유공자',
                '농어촌', '농어촌학생', '기회균형', '기회 균형', '기회균등', '기회 균등', '사회배려', '사회통합',
                '특성화고재직자', '특성화고졸재직자', '차상위', '기초생활', '한부모'
            ]
            if any(kw in combined_jungsi_text for kw in non_standard_keywords):
                continue

            cutoff_3yr = row['Cutoff_3yr']
            cut_2025 = row['Cut_2025']
            cut_2024 = row['Cut_2024']
            tier = row['Univ_Tier']
            
            if pd.isna(cutoff_3yr):
                continue
            else:
                diff = round(user_p - cutoff_3yr, 2)
                
                # 정시 대입상담 상식선 기준
                if diff < -4.0:
                    continue  # 과도한 상향 도전 제외
                elif diff < -1.0:
                    status = "소신 (경쟁적)"
                    status_code = 0  # 소신 0순위 상단 배치!
                elif diff <= 3.0:
                    status = "적정 (합격유력)"
                    status_code = 1
                elif diff <= 10.0:
                    status = "안정 (매우유리)"
                    status_code = 2
                else:
                    continue  # 과도한 하향안정 제외
                    
            elements = str(row['전형요소']) if not pd.isna(row['전형요소']) else '수능 100%'

            results.append({
                'id': f"jungsi_{row.name}",
                'univ': univ,
                'tier': tier,
                'region': region,
                'group': group,
                'department': str(row['학과']),
                'capacity': str(row['모집인원']) if not pd.isna(row['모집인원']) else '-',
                'competition_2025': str(row['경쟁률_2025']) if not pd.isna(row['경쟁률_2025']) else '-',
                'cutoff_3yr': round(cutoff_3yr, 1),
                'cut_2025': round(cut_2025, 1) if not pd.isna(cut_2025) else '-',
                'cut_2024': round(cut_2024, 1) if not pd.isna(cut_2024) else '-',
                'user_percentile': round(user_p, 1),
                'diff': diff,
                'status': status,
                'status_code': status_code,
                'elements': elements,
                'math_ref': str(row['수학반영']) if not pd.isna(row['수학반영']) else '공통',
                'tamgu_ref': str(row['탐구반영']) if not pd.isna(row['탐구반영']) else '공통'
            })
            
        if sort_by == "rank":
            results.sort(key=lambda x: (x['tier'], x['status_code'], -x['cutoff_3yr'], x['univ'], x['department']))
        else: # status 기본 (소신(0) -> 적정(1) -> 안정(2))
            results.sort(key=lambda x: (x['status_code'], x['tier'], -x['cutoff_3yr'], x['univ'], x['department']))

        return results

engine = AdmissionDataEngine()
