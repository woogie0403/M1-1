# 📋 진행 체크리스트 (AI 응용 학습 미션)

> 대한민국 극장가 일별 박스오피스 시계열 분석 프로젝트 (2024-2025)
> **기본 과제(STEP 0-6) 및 보너스 과제 2종(웹 대시보드 + 시계열 분해) 전수 완결!**

## ▶ 프로젝트 상태: 🎉 [최종 완성 100%]
모든 필수 요구사항과 보너스 옵션이 구현되었으며, 실전 5분 발표 대본과 Q&A 방어 가이드까지 패키징되었습니다.

---

## 🎯 확정 및 구현 완료 내역
| 항목 | 내용 |
| :--- | :--- |
| 주제 | 대한민국 극장가 일별 관객수 시계열 분석 (2024-2025) |
| 데이터 출처 | 영화진흥위원회 KOBIS Open API (일별 박스오피스 TOP 10) |
| 기간 | 2024-01-01 - 2025-12-31 (731일 전수 수집 완료, 결측일 0건) |
| 원본 파일 | `data/kobis_daily_top10_2024_2025.csv` (총 7,310행) |
| 정제 파일 | `data/daily_boxoffice_2024_2025.csv` (총 731행) |
| 분석 파일 | `data/daily_boxoffice_features.csv` (총 731행, 이동평균·변화율 등 19개 지표 완성) |
| 시각화 파일 | `images/` 폴더 내 총 4종 고해상도(300 DPI) 차트 완성 |
| 리포트 파일 | `REPORT.md` (Fact-Why-Action 3단 구조, 한계점, AI 사용 로그, 보너스 섹션 완비) |
| 가이드 문서 | `README.md` (재현 실행 순서, 요구사항 점검표, **5분 발표 대본 & Q&A**) |
| 웹 대시보드 | `app.py` (Streamlit 기반 인터랙티브 탐색 서비스) |
| 시계열 분해 | `time_series_decomposition.py` (Trend, Seasonal, Residual 4단 수학적 분해) |
| 의존성 환경 | `requirements.txt` (pandas, requests, matplotlib, streamlit, statsmodels 등) |
| API 키 보안 | `.env` 파일에 보관 (`.gitignore`로 GitHub 업로드 완벽 격리) |

---

## ✅ STEP별 체크리스트

### STEP 0. 준비
- [x] 과제 PDF 분석
- [x] 주제 확정 (대한민국 극장 박스오피스 시계열)
- [x] KOBIS API 키 발급 및 작동 확인
- [x] `.env`, `.gitignore` 생성 및 보안 조치
- [x] git 저장소 초기화 (`cb58d3a`)

### STEP 1. 데이터 수집 & 질문 정의
- [x] 분석 질문 3개 확정
- [x] 수집 스크립트 작성 (`collect_data.py`, `retry_failed.py`)
- [x] `python collect_data.py` 실행 완료
- [x] `data/kobis_daily_top10_2024_2025.csv` 생성 확인 (731일, 7,310행, 실패 0건)
- [x] STEP 1 완료 git 커밋 (`328bea5`)

### STEP 2. 데이터 정제 & 탐색 (EDA)
- [x] 원본 CSV 로드 및 데이터 기본 정보 점검
- [x] 숫자형 컬럼 타입 변환 (`audiCnt`, `salesAmt` 등 int64 변환)
- [x] 일별 극장 관객수/매출액 집계 (`daily_boxoffice_2024_2025.csv`) 생성 (731일, 결측일 0건)
- [x] 당일 1위 영화(`top_movie`), 1위 점유율(`top1_share`), 요일명 등 피처 생성
- [x] 결측치/이상치 처리 기준 수립 및 2024 vs 2025 연간 통계 확인
- [x] STEP 2 완료 git 커밋 (`f983df6`)

### STEP 3. 시계열 분석 (기법 3종 적용)
- [x] 기법 1: 단기 7일 MA 및 중기 30일 MA (이동평균) 계산
- [x] 기법 2: 전일 대비(`pct_change(1)`) 및 전주 동일 요일 대비(`pct_change(7)`) 변화율 계산
- [x] 기법 3: 요일별(Day-of-Week) 및 월별(Month) 그룹 통계 산출
- [x] 분석 결과 통합 시계열 데이터셋(`data/daily_boxoffice_features.csv`) 저장
- [x] STEP 3 완료 git 커밋 (`d3bb6ef`)

### STEP 4. 시각화 (2개 이상 필수, 권장 3개)
- [x] 시각화 1: `images/01_audience_trend_ma.png` (2024-2025 일별 추세선 + 7일/30일 이동평균선)
- [x] 시각화 2: `images/02_dow_and_monthly_pattern.png` (요일별 관객 패턴 & 월별 성수기 계절성 서브플롯)
- [x] 시각화 3: `images/03_outlier_peaks_annotated.png` (일별 관객수 급등 Top 5 피크 & 원인 영화 어노테이션)
- [x] 시각화 개선: 텍스트 겹침 완전 해결, y축 여백 확대, 기호(-) 교체 및 300 DPI 완료
- [x] STEP 4 완료 git 커밋 (`a6f059e`, `ffb9f52`)

### STEP 5. 인사이트 도출 (3개 이상)
- [x] 인사이트 1: 2024 vs 2025 극장가 연간 총량 및 회복 추세 비교 (-15.52% 역성장)
- [x] 인사이트 2: 요일별 관객 쏠림 비율 및 요일 효과 (수요일 +66.2% 반등, 주말 2.19배)
- [x] 인사이트 3: 메가 히트작이 전체 극장가에 미치는 파급력 (12/25 크리스마스 특수, 범죄도시4 94.7% 독점)
- [x] 각 인사이트를 `관찰(Fact) → 원인(Why) → 행동 제안(Action)`으로 구조화
- [x] STEP 5 완료 git 커밋 (`f402980`)

### STEP 6. 리포트 & 제출 패키징
- [x] `REPORT.md` 작성 (분석 주제, 질문, 데이터 설명, 시각화, 인사이트, 한계점)
- [x] AI 사용 로그 섹션 작성 (작업, 사용 이유, 검증 방법)
- [x] `README.md` 작성 (프로젝트 개요, 재현 실행 순서, 의존성 안내)
- [x] `requirements.txt` 최신화
- [x] STEP 6 완료 git 커밋 (`3fa764e`)

### 🎁 보너스 과제 (2종 전수 완결)
- [x] **보너스 1**: Streamlit 인터랙티브 웹 대시보드 (`app.py`) 개발 완료
- [x] **보너스 2**: 시계열 심화 4단 분해(`time_series_decomposition.py`, `images/04_time_series_decomposition.png`) 및 지표 도출
- [x] `README.md`에 보너스 과제 수행 내역 및 대시보드 실행 가이드 반영
- [x] `README.md`에 과제 요구사항 최종 점검표 반영
- [x] `README.md`에 **실전 5분 발표 대본 & 슬라이드별 스피치 멘트, 심사위원 Q&A 방어 전략** 추가
- [x] `REPORT.md`에 보너스 과제 심화 섹션(8절) 추가
- [x] GitHub 원격 저장소 (`https://github.com/woogie0403/M1-1`) push 완료
- [x] 최종 전체 패키징 Git 커밋 및 원격 동기화 완료
