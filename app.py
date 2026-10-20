"""
보너스 STEP B. Streamlit 인터랙티브 웹 대시보드

실행 방법:
streamlit run app.py
"""
import os
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="대한민국 극장가 관객수 시계열 대시보드",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 맑은 고딕 한글 폰트 설정
plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

# 2. 데이터 로드 (캐싱으로 고속 로딩)
@st.cache_data
def load_data():
    csv_path = os.path.join("data", "daily_boxoffice_features.csv")
    df = pd.read_csv(csv_path, encoding="utf-8-sig")
    df["date"] = pd.to_datetime(df["date"])
    return df

df_raw = load_data()

# 3. 사이드바 인터랙티브 필터 컨트롤러
st.sidebar.title("🎛️ 탐색 필터 컨트롤러")
st.sidebar.markdown("조건을 변경하면 대시보드가 실시간으로 반응합니다.")

# (1) 연도 선택
year_options = ["전체 (2024-2025)", "2024년", "2025년"]
selected_year = st.sidebar.selectbox("📅 분석 연도 선택", year_options)

if selected_year == "2024년":
    df_filtered = df_raw[df_raw["year"] == 2024].copy()
elif selected_year == "2025년":
    df_filtered = df_raw[df_raw["year"] == 2025].copy()
else:
    df_filtered = df_raw.copy()

# (2) 날짜 범위 선택
min_date = df_filtered["date"].min().date()
max_date = df_filtered["date"].max().date()

date_range = st.sidebar.date_input(
    "📆 날짜 상세 범위",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_d, end_d = date_range
    df_filtered = df_filtered[(df_filtered["date"].dt.date >= start_d) & (df_filtered["date"].dt.date <= end_d)]

# (3) 요일 필터 (멀티셀렉트)
all_days = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
selected_days = st.sidebar.multiselect(
    "📌 요일 선택 (기본: 전체)",
    options=all_days,
    default=all_days
)
df_filtered = df_filtered[df_filtered["day_of_week"].isin(selected_days)]

# (4) 특정 영화 검색 필터
movie_search = st.sidebar.text_input("🔍 특정 1위 영화 검색 (예: 파묘, 범죄도시, 하얼빈, 아바타)", "")
if movie_search:
    df_filtered = df_filtered[df_filtered["top_movie"].str.contains(movie_search, na=False)]

st.sidebar.markdown("---")
st.sidebar.caption("데이터 출처: 영화진흥위원회 KOBIS Open API")

# 4. 메인 대시보드 헤더
st.title("🎬 2024-2025 대한민국 극장가 관객수 시계열 탐색 대시보드")
st.markdown("""
본 대시보드는 **영진위 KOBIS 일별 박스오피스 731일 데이터**를 기반으로 구현된 인터랙티브 분석 서비스입니다.  
사이드바의 **기간, 요일, 영화 필터**를 조작하며 극장 시장의 패턴을 직접 탐색해 보세요.
""")

# 5. 핵심 KPI 메트릭 카드 (4열)
col1, col2, col3, col4 = st.columns(4)

total_audi = df_filtered["total_audi"].sum() if len(df_filtered) > 0 else 0
avg_audi = int(df_filtered["total_audi"].mean()) if len(df_filtered) > 0 else 0

# 주말 관객 비율
weekend_audi = df_filtered[df_filtered["is_weekend"]]["total_audi"].sum() if len(df_filtered) > 0 else 0
weekend_ratio = (weekend_audi / total_audi * 100) if total_audi > 0 else 0

# 최고 피크일
if len(df_filtered) > 0:
    max_row = df_filtered.loc[df_filtered["total_audi"].idxmax()]
    max_info = f"{max_row['top_movie']} ({int(max_row['total_audi']/10000):,}만)"
else:
    max_info = "데이터 없음"

col1.metric("총 관객수", f"{int(total_audi/10000):,}만 명", help="선택된 조건의 누적 관객수 합계")
col2.metric("일평균 관객수", f"{int(avg_audi/10000):.1f}만 명", help="선택된 조건의 하루 평균 관객수")
col3.metric("주말 관객 쏠림 비율", f"{weekend_ratio:.1f}%", help="토·일요일 관객이 차지하는 비중")
col4.metric("기간 내 최고 피크작", max_info, help="선택된 기간 중 하루 관객수 1위 영화")

st.markdown("---")

if len(df_filtered) == 0:
    st.warning("⚠️ 선택하신 필터 조건에 해당하는 데이터가 없습니다. 사이드바의 필터를 조정해 주세요.")
    st.stop()

# 6. 탭별 심층 분석
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 시계열 추세 & 이동평균선",
    "📅 요일 및 월별 패턴",
    "🏆 흥행 피크 & 1위 영화 랭킹",
    "💾 정제 데이터 조회 & 다운로드"
])

# [TAB 1] 시계열 추세 & 이동평균선
with tab1:
    st.subheader("일별 관객수 및 7일/30일 이동평균선(MA) 추세")
    st.caption("• 7일 이동평균(오렌지): 요일 노이즈 평활화 | • 30일 이동평균(네이비): 월간 계절성 및 시장 모멘텀")
    
    fig, ax = plt.subplots(figsize=(14, 5.5), dpi=200)
    ax.plot(df_filtered["date"], df_filtered["total_audi"], color="#b0bec5", alpha=0.45, linewidth=1.0, label="일별 관객수")
    if "ma_7" in df_filtered.columns:
        ax.plot(df_filtered["date"], df_filtered["ma_7"], color="#ff7043", linewidth=1.8, label="7일 이동평균 (MA 7)")
    if "ma_30" in df_filtered.columns:
        ax.plot(df_filtered["date"], df_filtered["ma_30"], color="#1a237e", linewidth=2.4, label="30일 이동평균 (MA 30)")
    
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"{int(x/10000):,}만"))
    ax.set_ylabel("관객수 (명)")
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(loc="upper right", frameon=True, facecolor="white")
    st.pyplot(fig)
    plt.close()

# [TAB 2] 요일 및 월별 패턴
with tab2:
    col_t1, col_t2 = st.columns(2)
    
    with col_t1:
        st.subheader("요일별 평균 관객수")
        dow_stat = df_filtered.groupby("day_of_week")["total_audi"].mean().reindex(all_days).dropna()
        fig_dow, ax_dow = plt.subplots(figsize=(7, 4.5), dpi=200)
        colors = ["#90a4ae", "#90a4ae", "#42a5f5", "#90a4ae", "#5c6bc0", "#e53935", "#ef5350"]
        bars = ax_dow.bar(dow_stat.index, dow_stat.values, color=colors[:len(dow_stat)], edgecolor="black", linewidth=0.5)
        for b in bars:
            y = b.get_height()
            ax_dow.text(b.get_x() + b.get_width()/2.0, y + 5000, f"{int(y/10000):.1f}만", ha="center", fontsize=8.5, fontweight="bold")
        ax_dow.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"{int(x/10000):,}만"))
        ax_dow.grid(axis="y", linestyle="--", alpha=0.5)
        st.pyplot(fig_dow)
        plt.close()
        st.info("💡 **수요일 급반등**: 신작 개봉 및 매월 마지막 주 수요일 '문화가 있는 날(50% 할인)' 효과로 화요일 대비 급증합니다.")

    with col_t2:
        st.subheader("월별 누적 관객수 (계절성)")
        df_filtered["year_month"] = df_filtered["date"].dt.strftime("%Y-%m")
        ym_stat = df_filtered.groupby("year_month")["total_audi"].sum()
        fig_m, ax_m = plt.subplots(figsize=(8, 4.5), dpi=200)
        ax_m.bar(ym_stat.index, ym_stat.values, color="#00897b", edgecolor="black", linewidth=0.5)
        ax_m.set_xticklabels(ym_stat.index, rotation=45, ha="right")
        ax_m.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f"{int(x/10000):,}만"))
        ax_m.grid(axis="y", linestyle="--", alpha=0.5)
        st.pyplot(fig_m)
        plt.close()
        st.info("❄️ **연말/여름 성수기**: 12월 크리스마스 시즌과 7-8월 여름방학 시즌에 관객수가 집중됩니다.")

# [TAB 3] 흥행 피크 & 1위 영화 랭킹
with tab3:
    col_p1, col_p2 = st.columns([1.2, 1])
    
    with col_p1:
        st.subheader("선택 조건 내 관객수 TOP 10 피크 일자")
        top10_days = df_filtered.sort_values("total_audi", ascending=False).head(10)[
            ["date", "day_of_week", "top_movie", "total_audi", "top1_share"]
        ].copy()
        top10_days["date"] = top10_days["date"].dt.strftime("%Y-%m-%d")
        top10_days["total_audi"] = top10_days["total_audi"].apply(lambda x: f"{x:,}명")
        top10_days["top1_share"] = top10_days["top1_share"].apply(lambda x: f"{x:.1f}%")
        top10_days.columns = ["날짜", "요일", "당일 1위 영화", "일별 총 관객수", "1위 점유율"]
        st.dataframe(top10_days.reset_index(drop=True), use_container_width=True)

    with col_p2:
        st.subheader("1위 최장 유지 영화 TOP 5")
        top_movies = df_filtered["top_movie"].value_counts().head(5)
        fig_top, ax_top = plt.subplots(figsize=(6, 4.5), dpi=200)
        ax_top.barh(top_movies.index[::-1], top_movies.values[::-1], color="#fb8c00", edgecolor="black", linewidth=0.5)
        for i, v in enumerate(top_movies.values[::-1]):
            ax_top.text(v + 0.5, i, f"{v}일", va="center", fontweight="bold", fontsize=9)
        ax_top.set_xlabel("1위 유지 일수 (일)")
        ax_top.grid(axis="x", linestyle="--", alpha=0.5)
        st.pyplot(fig_top)
        plt.close()

# [TAB 4] 정제 데이터 조회 & 다운로드
with tab4:
    st.subheader("정제된 시계열 데이터프레임 미리보기")
    st.dataframe(df_filtered.head(50), use_container_width=True)
    
    csv_data = df_filtered.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
    st.download_button(
        label="📥 필터링된 데이터 CSV 다운로드",
        data=csv_data,
        file_name="filtered_boxoffice_data.csv",
        mime="text/csv"
    )
