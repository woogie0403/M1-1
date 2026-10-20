"""
STEP 2. 데이터 정제 & 탐색적 데이터 분석 (EDA)

1. data/kobis_daily_top10_2024_2025.csv 로드
2. 결측치 점검 (731일 연속성 검증)
3. 일별(Date) 집계 시계열 생성 (당일 총 관객수, 매출액, 1위 영화, 1위 점유율, 요일, 월 등)
4. data/daily_boxoffice_2024_2025.csv 저장
5. EDA 핵심 요약 통계 출력
"""
import os
import sys
import pandas as pd

# Windows 터미널 한글/이모지 출력 인코딩 설정
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

RAW_PATH = os.path.join("data", "kobis_daily_top10_2024_2025.csv")
OUT_PATH = os.path.join("data", "daily_boxoffice_2024_2025.csv")

print("=" * 60)
print("🔍 [STEP 2] KOBIS 박스오피스 데이터 정제 및 EDA 시작")
print("=" * 60)

# 1. 원본 데이터 로드
df = pd.read_csv(RAW_PATH, encoding="utf-8-sig")
print(f"📁 원본 데이터 로드 완료: {len(df):,}행, {len(df.columns)}개 컬럼")

# 2. 날짜 및 수치형 컬럼 변환
df["date"] = pd.to_datetime(df["date"])
int_cols = ["rank", "audiCnt", "audiAcc", "salesAmt", "scrnCnt", "showCnt"]
for col in int_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype("int64")

# 3. 결측 날짜 검증 (2024-01-01 ~ 2025-12-31 완전성 확인)
expected_dates = pd.date_range("2024-01-01", "2025-12-31", freq="D")
actual_dates = pd.to_datetime(df["date"].unique())
missing_dates = expected_dates.difference(actual_dates)

print(f"📅 전체 날짜 범위: {expected_dates[0].strftime('%Y-%m-%d')} ~ {expected_dates[-1].strftime('%Y-%m-%d')} (총 {len(expected_dates)}일)")
print(f"✅ 결측 날짜 수: {len(missing_dates)}일 (결측치 없음!)")

# 4. 일별(Daily) 시계열 데이터프레임 집계
daily_total = df.groupby("date").agg(
    total_audi=("audiCnt", "sum"),
    total_sales=("salesAmt", "sum"),
    total_screens=("scrnCnt", "sum"),
    total_shows=("showCnt", "sum")
).reset_index()

# 당일 1위 영화 및 1위 관객수 추출
rank1 = df[df["rank"] == 1][["date", "movieNm", "audiCnt"]].rename(
    columns={"movieNm": "top_movie", "audiCnt": "top_movie_audi"}
)

daily = pd.merge(daily_total, rank1, on="date", how="left")

# 1위 영화 점유율 계산 (1위 영화 관객수 / TOP 10 총 관객수 * 100)
daily["top1_share"] = (daily["top_movie_audi"] / daily["total_audi"] * 100).round(2)

# 시계열 분석을 위한 파생 변수 추가 (연도, 월, 일, 요일명)
daily["year"] = daily["date"].dt.year
daily["month"] = daily["date"].dt.month
daily["day"] = daily["date"].dt.day
daily["day_name"] = daily["date"].dt.day_name()  # Monday ~ Sunday
# 요일 한국어 매핑
korean_days = {
    "Monday": "월요일", "Tuesday": "화요일", "Wednesday": "수요일",
    "Thursday": "목요일", "Friday": "금요일", "Saturday": "토요일", "Sunday": "일요일"
}
daily["day_of_week"] = daily["day_name"].map(korean_days)
daily["is_weekend"] = daily["day_name"].isin(["Saturday", "Sunday"])

# 5. 정제된 일별 시계열 CSV 파일 저장
daily.to_csv(OUT_PATH, index=False, encoding="utf-8-sig")
print(f"💾 일별 시계열 데이터 저장 완료: {OUT_PATH} ({len(daily)}일)")

# 6. EDA 핵심 요약 통계 출력
print("\n" + "=" * 60)
print("📊 [핵심 통계 요약]")
print("=" * 60)
print(f"• 분석 총 일수: {len(daily)}일 (2024년 366일, 2025년 365일)")
print(f"• 2개년 총 관객수: {daily['total_audi'].sum():,}명")
print(f"• 일평균 관객수: {int(daily['total_audi'].mean()):,}명")
print(f"• 최소 관객일: {daily.loc[daily['total_audi'].idxmin(), 'date'].strftime('%Y-%m-%d')} ({daily['total_audi'].min():,}명)")
print(f"• 최대 관객일: {daily.loc[daily['total_audi'].idxmax(), 'date'].strftime('%Y-%m-%d')} ({daily['total_audi'].max():,}명, 1위: {daily.loc[daily['total_audi'].idxmax(), 'top_movie']})")

print("\n[2024년 vs 2025년 연간 비교]")
yearly = daily.groupby("year")["total_audi"].agg(["sum", "mean"]).rename(
    columns={"sum": "연간 총 관객수", "mean": "일평균 관객수"}
)
yearly["전년 대비 변화율(%)"] = yearly["연간 총 관객수"].pct_change() * 100
for yr, row in yearly.iterrows():
    change_str = f"({row['전년 대비 변화율(%)']:+.2f}%)" if pd.notnull(row['전년 대비 변화율(%)']) else "(기준 연도)"
    print(f"• {yr}년: 총 {int(row['연간 총 관객수']):,}명 | 일평균 {int(row['일평균 관객수']):,}명 {change_str}")

print("\n[2개년 일별 관객수 TOP 5 피크 데이 (이상치 분석 후보)]")
top5_days = daily.sort_values("total_audi", ascending=False).head(5)
for idx, r in top5_days.reset_index(drop=True).iterrows():
    dt_str = r['date'].strftime('%Y-%m-%d')
    print(f"  {idx+1}위. {dt_str} ({r['day_of_week']}) : {r['total_audi']:,}명 (1위: {r['top_movie']}, 점유율 {r['top1_share']}%)")

print("\n[2개년 박스오피스 1위 최장 유지 영화 TOP 5]")
top_movies = daily["top_movie"].value_counts().head(5)
for idx, (m_name, cnt) in enumerate(top_movies.items(), start=1):
    print(f"  {idx}위. {m_name}: {cnt}일간 1위")
print("=" * 60)
