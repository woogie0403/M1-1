"""
보너스 STEP A. 시계열 분해 (Time Series Decomposition)

- 기법: 덧셈 모델 (Additive Decomposition, period=7 일주일 주기)
- 4단 분해:
  1. Observed (원시 일별 관객수)
  2. Trend (순수 추세: 7일 주기 평활화)
  3. Seasonal (주간 계절성: 토/일 급등, 화요일 급락 7일 파동)
  4. Residual (잔차/이상치: 크리스마스, 범죄도시4 등 특수 이벤트 스파이크)
- 결과 저장: images/04_time_series_decomposition.png
"""
import os
import sys
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
from statsmodels.tsa.seasonal import seasonal_decompose

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

IN_PATH = os.path.join("data", "daily_boxoffice_features.csv")
OUT_IMG = os.path.join("images", "04_time_series_decomposition.png")

print("=" * 65)
print("🔬 [보너스 STEP A] 시계열 분해(Decomposition) 분석 시작")
print("=" * 65)

# 1. 데이터 로드 및 시계열 인덱스 설정
df = pd.read_csv(IN_PATH, encoding="utf-8-sig")
df["date"] = pd.to_datetime(df["date"])
df = df.set_index("date")

# 2. 7일 주기(주간) 덧셈 모델 시계열 분해
decomp = seasonal_decompose(df["total_audi"], model="additive", period=7)

# 3. 4단 서브플롯 시각화 (Observed, Trend, Seasonal, Residual)
fig, axes = plt.subplots(4, 1, figsize=(15, 11), sharex=True, dpi=300)

# (1) Observed
axes[0].plot(decomp.observed.index, decomp.observed.values, color="#455a64", linewidth=1.1)
axes[0].set_title("1. 원시 관객수 (Observed: 일별 TOP 10 총합)", fontsize=11, fontweight="bold", loc="left", pad=5)
axes[0].yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"{int(x/10000):,}만"))
axes[0].grid(True, linestyle="--", alpha=0.4)

# (2) Trend
axes[1].plot(decomp.trend.index, decomp.trend.values, color="#1565c0", linewidth=2.0)
axes[1].set_title("2. 추세 (Trend: 7일 주기 요일 노이즈를 제거한 순수 시장 흐름)", fontsize=11, fontweight="bold", loc="left", pad=5)
axes[1].yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"{int(x/10000):,}만"))
axes[1].grid(True, linestyle="--", alpha=0.4)

# (3) Seasonal (일주일 주기 파동)
axes[2].plot(decomp.seasonal.index, decomp.seasonal.values, color="#2e7d32", linewidth=1.0)
axes[2].set_title("3. 주간 계절성 (Seasonal: 토·일 급등, 화요일 급락의 7일 주기 진동)", fontsize=11, fontweight="bold", loc="left", pad=5)
axes[2].yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"{int(x/10000):+,}만"))
axes[2].grid(True, linestyle="--", alpha=0.4)

# (4) Residual (특수 이벤트 잔차)
axes[3].plot(decomp.resid.index, decomp.resid.values, color="#c62828", linewidth=1.0, alpha=0.8)
axes[3].axhline(0, color="black", linestyle="--", linewidth=0.8, alpha=0.7)
axes[3].set_title("4. 잔차 / 노이즈 (Residual: 크리스마스·삼일절 등 통계적 이상치 스파이크)", fontsize=11, fontweight="bold", loc="left", pad=5)
axes[3].yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"{int(x/10000):+,}만"))
axes[3].set_xlabel("날짜 (Date)", fontsize=11, labelpad=8)
axes[3].grid(True, linestyle="--", alpha=0.4)

plt.suptitle("2024-2025 대한민국 극장가 일별 관객수 시계열 분해 (Trend - Seasonal - Resid)", fontsize=15, fontweight="bold", y=0.995)
plt.tight_layout()
plt.savefig(OUT_IMG, dpi=300)
plt.close()

# 4. 계절성 및 잔차 통계 요약 출력
dow_seasonal = decomp.seasonal.head(7)
print("📊 [7일 주간 계절성 편차 요약]")
day_names = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
for dt, val in dow_seasonal.items():
    d_name = dt.day_name()
    kr_name = {"Monday":"월요일","Tuesday":"화요일","Wednesday":"수요일","Thursday":"목요일","Friday":"금요일","Saturday":"토요일","Sunday":"일요일"}.get(d_name, d_name)
    print(f"  • {kr_name}: 평균 대비 {val:+,.0f}명")

top_resids = decomp.resid.dropna().sort_values(ascending=False).head(3)
print("\n🔥 [잔차(Residual) 역대 최고 스파이크 TOP 3 - 돌발 특수]")
for dt, val in top_resids.items():
    row = df.loc[dt]
    print(f"  • {dt.strftime('%Y-%m-%d')} ({row['day_of_week']}): +{val:,.0f}명 이상치 (1위: {row['top_movie']})")

print(f"\n💾 시계열 분해 시각화 저장 완료: {OUT_IMG}")
print("=" * 65)
