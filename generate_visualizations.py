"""
STEP 4. 고품질 시각화 3종 생성 및 images/ 저장 스크립트

1. images/01_audience_trend_ma.png: 일별 관객수 및 7일/30일 이동평균선 추세
2. images/02_dow_and_monthly_pattern.png: 요일별 패턴(주말 2.19배) 및 월별 계절성 비교
3. images/03_outlier_peaks_annotated.png: 역대 TOP 5 이상치(피크) 및 원인 영화 어노테이션
"""
import os
import sys
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd

# 1. 폰트 및 한글 깨짐 방지 설정
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

os.makedirs("images", exist_ok=True)
IN_PATH = os.path.join("data", "daily_boxoffice_features.csv")
df = pd.read_csv(IN_PATH, encoding="utf-8-sig")
df["date"] = pd.to_datetime(df["date"])

print("=" * 65)
print("🎨 [STEP 4] 리포트용 고품질 시각화 3종 생성 시작")
print("=" * 65)

# -------------------------------------------------------------
# 시각화 1: 2024~2025 일별 관객수 및 이동평균선(7일/30일) 추세
# -------------------------------------------------------------
plt.figure(figsize=(14, 6), dpi=300)
ax = plt.subplot(1, 1, 1)

# 원본 관객수 (연한 회청색)
ax.plot(df["date"], df["total_audi"], color="#b0bec5", alpha=0.5, linewidth=1.0, label="일별 관객수 (원시 데이터)")
# 7일 이동평균 (오렌지)
ax.plot(df["date"], df["ma_7"], color="#ff7043", linewidth=1.8, label="7일 이동평균 (요일 노이즈 평활화)")
# 30일 이동평균 (네이비 굵은 선)
ax.plot(df["date"], df["ma_30"], color="#1a237e", linewidth=2.5, label="30일 이동평균 (월간 계절성/추세선)")

ax.set_title("2024~2025년 대한민국 극장가 일별 관객수 및 이동평균선(MA) 추세", fontsize=15, fontweight="bold", pad=15)
ax.set_xlabel("날짜 (Date)", fontsize=11, labelpad=8)
ax.set_ylabel("일별 관객수 (명)", fontsize=11, labelpad=8)
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"{int(x/10000):,}만"))
ax.grid(True, linestyle="--", alpha=0.5)
ax.legend(loc="upper right", frameon=True, facecolor="white", edgecolor="#cfd8dc", fontsize=10)

img1_path = os.path.join("images", "01_audience_trend_ma.png")
plt.tight_layout()
plt.savefig(img1_path, dpi=300)
plt.close()
print(f"✅ [1/3] 시각화 1 저장 완료: {img1_path}")

# -------------------------------------------------------------
# 시각화 2: 요일별 관객 분포 & 월별 성수기/비수기 계절성 비교 (1행 2열)
# -------------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(16, 6), dpi=300)

# (좌측) 요일별 평균 관객수
dow_order = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
dow_avg = df.groupby("day_of_week")["total_audi"].mean().reindex(dow_order)

colors = ["#90a4ae", "#90a4ae", "#42a5f5", "#90a4ae", "#5c6bc0", "#e53935", "#ef5350"]
bars = axes[0].bar(dow_order, dow_avg, color=colors, edgecolor="black", linewidth=0.6, width=0.65)

# 평일 / 주말 평균 점선
weekday_avg = df[~df["is_weekend"]]["total_audi"].mean()
weekend_avg = df[df["is_weekend"]]["total_audi"].mean()
axes[0].axhline(weekday_avg, color="#37474f", linestyle="--", alpha=0.7, label=f"평일 평균: {int(weekday_avg/10000):.1f}만명")
axes[0].axhline(weekend_avg, color="#b71c1c", linestyle="--", alpha=0.7, label=f"주말 평균: {int(weekend_avg/10000):.1f}만명 (평일의 2.19배)")

for bar in bars:
    yval = bar.get_height()
    axes[0].text(bar.get_x() + bar.get_width() / 2.0, yval + 10000, f"{int(yval/10000):.1f}만",
                 ha="center", va="bottom", fontsize=9, fontweight="bold")

axes[0].set_title("요일별 평균 관객수 (수요일 반등 & 주말 쏠림)", fontsize=13, fontweight="bold", pad=12)
axes[0].set_ylabel("평균 관객수 (명)", fontsize=11)
axes[0].yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"{int(x/10000):,}만"))
axes[0].grid(axis="y", linestyle="--", alpha=0.5)
axes[0].legend(loc="upper left", fontsize=9)

# (우측) 2024 vs 2025 월별 총 관객수 비교
monthly_24 = df[df["year"] == 2024].groupby("month")["total_audi"].sum()
monthly_25 = df[df["year"] == 2025].groupby("month")["total_audi"].sum()
months = np.arange(1, 13)
width = 0.38

axes[1].bar(months - width / 2, monthly_24, width=width, color="#00897b", edgecolor="black", linewidth=0.5, label="2024년 (총 1.16억명)")
axes[1].bar(months + width / 2, monthly_25, width=width, color="#fb8c00", edgecolor="black", linewidth=0.5, label="2025년 (총 0.98억명)")

axes[1].set_title("2024 vs 2025 월별 총 관객수 비교 (연말/여름 성수기)", fontsize=13, fontweight="bold", pad=12)
axes[1].set_xlabel("월 (Month)", fontsize=11)
axes[1].set_ylabel("월간 총 관객수 (명)", fontsize=11)
axes[1].set_xticks(months)
axes[1].set_xticklabels([f"{m}월" for m in months])
axes[1].yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"{int(x/10000):,}만"))
axes[1].grid(axis="y", linestyle="--", alpha=0.5)
axes[1].legend(loc="upper left", fontsize=10)

img2_path = os.path.join("images", "02_dow_and_monthly_pattern.png")
plt.tight_layout()
plt.savefig(img2_path, dpi=300)
plt.close()
print(f"✅ [2/3] 시각화 2 저장 완료: {img2_path}")

# -------------------------------------------------------------
# 시각화 3: 역대 TOP 5 이상치(피크) & 원인 영화 어노테이션
# -------------------------------------------------------------
plt.figure(figsize=(15, 7), dpi=300)
ax = plt.subplot(1, 1, 1)

ax.plot(df["date"], df["total_audi"], color="#90caf9", alpha=0.7, linewidth=1.2, label="일별 관객수")
ax.plot(df["date"], df["ma_7"], color="#3949ab", alpha=0.8, linewidth=1.5, linestyle=":", label="7일 이동평균선")

# TOP 5 피크 데이 선정
top5 = df.sort_values("total_audi", ascending=False).head(5)
ax.scatter(top5["date"], top5["total_audi"], color="#d50000", s=90, zorder=5, edgecolor="black", label="관객수 TOP 5 피크 (이상치)")

# 화살표 어노테이션 설정 (가독성을 위한 오프셋 튜닝)
offsets = [
    (15, 35),    # 2024-12-25 크리스마스
    (-130, 30),  # 2025-12-25 크리스마스
    (-25, 40),   # 2024-04-27 범죄도시4
    (-130, 40),  # 2024-03-01 삼일절 파묘
    (15, -45)    # 2024-03-02 토요일 파묘
]

for (_, r), (ox, oy) in zip(top5.iterrows(), offsets):
    txt = f"[{r['date'].strftime('%Y-%m-%d')}]\n1위: {r['top_movie']}\n{r['total_audi']:,}명 (점유율 {r['top1_share']}%)"
    ax.annotate(
        txt,
        xy=(r["date"], r["total_audi"]),
        xytext=(ox, oy),
        textcoords="offset points",
        fontsize=8.5,
        fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.4", fc="#fff9c4", ec="#f57f17", lw=1.2, alpha=0.95),
        arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0.15", color="#b71c1c", lw=1.5)
    )

ax.set_title("2024~2025년 대한민국 극장가 관객수 TOP 5 피크(이상치) & 원인 영화", fontsize=15, fontweight="bold", pad=15)
ax.set_xlabel("날짜 (Date)", fontsize=11, labelpad=8)
ax.set_ylabel("일별 관객수 (명)", fontsize=11, labelpad=8)
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"{int(x/10000):,}만"))
ax.grid(True, linestyle="--", alpha=0.5)
ax.legend(loc="upper left", frameon=True, facecolor="white", edgecolor="#cfd8dc", fontsize=10)

img3_path = os.path.join("images", "03_outlier_peaks_annotated.png")
plt.tight_layout()
plt.savefig(img3_path, dpi=300)
plt.close()
print(f"✅ [3/3] 시각화 3 저장 완료: {img3_path}")
print("=" * 65)
