"""
STEP 1 보조. 수집에 실패해서 빠진 날짜만 다시 받아 CSV에 채워 넣는 스크립트

사용법: python retry_failed.py
- data/kobis_daily_top10_2024_2025.csv 를 읽어서 빠진 날짜를 찾는다.
- 빠진 날짜만 다시 요청한다. (대기 시간 30초, 최대 5번 재시도)
- 원래 CSV에 합친 뒤 날짜/순위 순서로 정렬해서 다시 저장한다.
"""
import os
import time

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("KOBIS_API_KEY")
URL = "http://kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json"
START, END = "2024-01-01", "2025-12-31"
CSV_PATH = os.path.join("data", "kobis_daily_top10_2024_2025.csv")

# 1. 기존 CSV에서 빠진 날짜 찾기
df = pd.read_csv(CSV_PATH, encoding="utf-8-sig")
all_dates = set(pd.date_range(START, END, freq="D").strftime("%Y-%m-%d"))
have_dates = set(df["date"].unique())
missing = sorted(all_dates - have_dates)

if not missing:
    raise SystemExit("✅ 빠진 날짜가 없습니다. 다시 받을 필요가 없어요.")

print(f"🔍 빠진 날짜 {len(missing)}개: {missing}")

# 2. 빠진 날짜만 다시 요청 (서버가 느릴 수 있으니 더 오래, 더 여러 번 기다림)
new_rows, still_failed = [], []
for date_str in missing:
    params = {"key": API_KEY, "targetDt": date_str.replace("-", ""), "itemPerPage": 10}
    movies = []
    for attempt in range(1, 6):
        try:
            data = requests.get(URL, params=params, timeout=30).json()
            if "faultInfo" in data:
                raise RuntimeError(data["faultInfo"])
            movies = data["boxOfficeResult"]["dailyBoxOfficeList"]
            break
        except Exception as e:
            print(f"  ⚠️ {date_str} {attempt}번째 시도 실패: {e}")
            time.sleep(attempt * 3)  # 실패할수록 더 오래 쉬었다가 재시도

    if not movies:
        still_failed.append(date_str)
        continue

    print(f"  ✅ {date_str} 성공 ({len(movies)}편)")
    for m in movies:
        new_rows.append({
            "date": date_str,
            "rank": m["rank"],
            "movieNm": m["movieNm"],
            "openDt": m["openDt"],
            "audiCnt": m["audiCnt"],
            "audiAcc": m["audiAcc"],
            "salesAmt": m["salesAmt"],
            "scrnCnt": m["scrnCnt"],
            "showCnt": m["showCnt"],
        })

# 3. 합치고 정렬해서 저장
if new_rows:
    df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
    df["rank"] = df["rank"].astype(int)
    df = df.sort_values(["date", "rank"]).reset_index(drop=True)
    df.to_csv(CSV_PATH, index=False, encoding="utf-8-sig")

print(f"\n💾 저장 완료: {CSV_PATH}")
print(f"📊 수집된 날짜 수: {df['date'].nunique()} / 731")
print(f"❗ 아직도 실패한 날짜: {still_failed if still_failed else '없음'}")
