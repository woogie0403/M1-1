"""
STEP 1. KOBIS 일별 박스오피스 데이터 수집 스크립트

- 출처: 영화진흥위원회 KOBIS Open API (일별 박스오피스)
- 기간: 2024-01-01 ~ 2025-12-31 (731일)
- 결과: data/kobis_daily_top10_2024_2025.csv (하루당 TOP 10 영화, 약 7,310행)
"""
import os
import time

import pandas as pd
import requests
from dotenv import load_dotenv

# 1. API 키 불러오기 (.env 파일에서 읽음 -> 코드에 키를 직접 쓰지 않음)
load_dotenv()
API_KEY = os.getenv("KOBIS_API_KEY")
if not API_KEY:
    raise SystemExit("❌ .env 파일에 KOBIS_API_KEY가 없습니다.")

URL = "http://kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json"
START, END = "2024-01-01", "2025-12-31"
OUT_PATH = os.path.join("data", "kobis_daily_top10_2024_2025.csv")

os.makedirs("data", exist_ok=True)
os.makedirs("images", exist_ok=True)


def fetch_one_day(target_dt: str, retries: int = 3) -> list[dict]:
    """하루치 TOP 10 박스오피스를 가져온다. 실패하면 최대 3번 재시도."""
    params = {"key": API_KEY, "targetDt": target_dt, "itemPerPage": 10}
    for attempt in range(1, retries + 1):
        try:
            res = requests.get(URL, params=params, timeout=10)
            data = res.json()
            if "faultInfo" in data:  # 키 오류, 호출 한도 초과 등
                raise RuntimeError(data["faultInfo"])
            return data["boxOfficeResult"]["dailyBoxOfficeList"]
        except Exception as e:
            print(f"  ⚠️ {target_dt} {attempt}번째 시도 실패: {e}")
            time.sleep(2)
    return []  # 3번 모두 실패한 날은 빈 리스트 -> 나중에 결측 확인


# 2. 날짜를 하루씩 돌면서 수집
dates = pd.date_range(START, END, freq="D")
rows, failed = [], []
print(f"📥 {START} ~ {END} ({len(dates)}일) 수집 시작...")

for i, day in enumerate(dates, start=1):
    target_dt = day.strftime("%Y%m%d")
    movies = fetch_one_day(target_dt)
    if not movies:
        failed.append(target_dt)
    for m in movies:
        rows.append({
            "date": day.strftime("%Y-%m-%d"),
            "rank": m["rank"],
            "movieNm": m["movieNm"],
            "openDt": m["openDt"],
            "audiCnt": m["audiCnt"],      # 당일 관객수
            "audiAcc": m["audiAcc"],      # 누적 관객수
            "salesAmt": m["salesAmt"],    # 당일 매출액
            "scrnCnt": m["scrnCnt"],      # 스크린 수
            "showCnt": m["showCnt"],      # 상영 횟수
        })
    if i % 50 == 0 or i == len(dates):
        print(f"  ... {i}/{len(dates)}일 완료")
    time.sleep(0.1)  # 서버에 부담을 주지 않도록 잠깐 쉼

# 3. CSV 저장 (엑셀에서 한글이 깨지지 않도록 utf-8-sig)
df = pd.DataFrame(rows)
df.to_csv(OUT_PATH, index=False, encoding="utf-8-sig")

print(f"\n💾 저장 완료: {OUT_PATH}")
print(f"📊 전체 행 수: {len(df)} / 수집된 날짜 수: {df['date'].nunique()}")
print(f"❗ 수집 실패한 날짜: {failed if failed else '없음'}")
print("\n[미리보기]")
print(df.head(3).to_string(index=False))
