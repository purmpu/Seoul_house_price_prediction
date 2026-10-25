import requests
import pandas as pd
import time
from tqdm import tqdm

# ========= 사용자 설정 =========
INPUT_CSV  = "BaseData"
OUTPUT_CSV = "편의시설.csv"

API_KEY = ""
RADIUS  = 1000
SLEEP_SEC = 0.15
# =================================

URL = "https://dapi.kakao.com/v2/local/search/keyword.json"
HEADERS = {"Authorization": f"KakaoAK {API_KEY}"}

# 👉 검색할 query + category 목록(확장 가능)
categories = {
    "school_total":   ("학교",      "SC4"),
    "subway_total":   ("지하철역",  "SW8"),
    "public_total":   ("공공기관",  "PO3"),
    "hospital_total": ("병원",      "HP8"),
    "mart_total":     ("대형마트",  "MT1"),
}


def kakao_total_count(query, category, lng, lat):
    """
    지정된 조건(query, category, 좌표)으로 Kakao API total_count 조회.
    실패하면 0.
    """
    try:
        params = {
            "query": query,
            "x": lng,       # 경도
            "y": lat,       # 위도
            "radius": RADIUS,
            "category_group_code": category
        }
        r = requests.get(URL, params=params, headers=HEADERS, timeout=10)

        if r.status_code == 200:
            js = r.json()
            return js["meta"].get("total_count", 0)
        else:
            return 0
    except:
        return 0


# CSV 읽기
df = pd.read_csv('BaseData.csv')

# 모든 카테고리에 대해 반복 수행
for new_col, (query, category) in categories.items():
    print(f"📡 카테고리 처리 중: {new_col} ({query}/{category})")

    results = []

    for _, row in tqdm(df.iterrows(), total=len(df)):
        lat = row["lat"]
        lng = row["lng"]

        total = kakao_total_count(query, category, lng, lat)
        results.append(total)

        time.sleep(SLEEP_SEC)

    # 새 열 추가
    df[new_col] = results

# 최종 저장
df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")

print(f"✅ 모든 카테고리 처리 완료! 저장됨: {OUTPUT_CSV}")
