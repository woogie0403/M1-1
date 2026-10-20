# 🎬 2024-2025 대한민국 극장가 관객수 시계열 분석 프로젝트

본 프로젝트는 영화진흥위원회(KOBIS) Open API를 활용하여 2024년 1월 1일부터 2025년 12월 31일까지 731일간의 일별 박스오피스 데이터를 수집하고, 시계열 분석 기법(이동평균, 변화율, 요일/월별 계절성 통계)을 적용하여 극장 시장의 구조적 변화와 요일 효과, 이상치 독점 현상을 규명한 분석 프로젝트입니다.

---

## 📁 프로젝트 폴더 구조

```text
M1-1/
|-- data/
|   |-- kobis_daily_top10_2024_2025.csv   # 원본 수집 데이터 (7,310행)
|   |-- daily_boxoffice_2024_2025.csv      # 일별 정제 데이터 (731행)
|   |-- daily_boxoffice_features.csv      # 시계열 피처 완성 데이터 (19개 컬럼)
|-- images/
|   |-- 01_audience_trend_ma.png          # 전체 추세 및 7일/30일 이동평균선
|   |-- 02_dow_and_monthly_pattern.png    # 요일별 관객 패턴 및 월별 계절성 비교
|   |-- 03_outlier_peaks_annotated.png    # 관객수 TOP 5 피크(이상치) & 원인 영화
|-- collect_data.py                       # [STEP 1] KOBIS API 데이터 수집 스크립트
|-- retry_failed.py                       # [STEP 1 보조] 실패 일자 재수집 스크립트
|-- clean_data.py                         # [STEP 2] 데이터 정제 및 일별 집계 (EDA)
|-- time_series_analysis.py               # [STEP 3] 시계열 지표(MA, 변화율 등) 계산
|-- generate_visualizations.py            # [STEP 4] 300 DPI 고해상도 시각화 생성
|-- REPORT.md                             # [최종] 분석 리포트 (Fact-Why-Action 인사이트)
|-- PROGRESS.md                           # 프로젝트 전체 진행 체크리스트
|-- requirements.txt                      # 파이썬 의존성 패키지 목록
|-- .env                                  # API 키 보관 (보안상 .gitignore 처리)
|-- .gitignore                            # Git 추적 제외 목록
```

---

## 🚀 재현 실행 방법 (Reproducibility)

### 1. 가상환경 및 패키지 설치
Python 3.10 이상 환경에서 아래 명령어를 실행합니다:
```bash
pip install -r requirements.txt
```

### 2. KOBIS API 키 설정
`.env` 파일에 발급받은 영진위 KOBIS API 키를 설정합니다:
```text
KOBIS_API_KEY=your_kobis_api_key_here
```

### 3. 단계별 파이프라인 실행
순서대로 실행하면 데이터 수집부터 분석, 시각화까지 전체 파이프라인이 자동 재현됩니다:

```bash
# 1단계: 2024-2025 일별 박스오피스 수집 (약 5-10분 소요)
python collect_data.py

# 2단계: 데이터 정제 및 일별 시계열 집계 (EDA)
python clean_data.py

# 3단계: 시계열 분석 기법 3종 적용 및 피처 엔지니어링
python time_series_analysis.py

# 4단계: 고해상도(300 DPI) 시각화 3종 생성 (images/ 폴더)
python generate_visualizations.py
```

---

## 📊 핵심 분석 결과 요약

1. **연간 총량 비교**: 2024년(1.16억 명) 대비 2025년(0.98억 명)에 **-15.52% 역성장**했습니다. 상반기 천만 블록버스터 IP 부재와 티켓값 인상에 따른 OTT 대체 소비가 주요 원인으로 분석됩니다.
2. **요일별 패턴**: 주간 최저점인 화요일(평균 16.7만 명) 대비 **수요일(평균 27.8만 명)에 관객수가 +66.2% 폭증**합니다. 수요일 신작 개봉 및 '문화가 있는 날(50% 할인)' 정책 효과가 뚜렷하며, 주말(토/일)은 평일 대비 **2.19배**의 관객이 몰립니다.
3. **이상치 피크 & 독과점**: 연간 최대 관객일은 2년 연속 **12월 25일 크리스마스**(151.8만 / 134.8만 명)였습니다. 특히 2024년 4월 27일에는 《범죄도시4》가 **당일 관객의 94.74%를 독식**하는 압도적 스크린 과점 현상이 관찰되었습니다.

👉 상세한 분석 결과와 시각화, 전략 제안은 [REPORT.md](REPORT.md)에서 확인하실 수 있습니다.
