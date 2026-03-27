# Lotto Analysis

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![Pytest](https://img.shields.io/badge/Test-pytest-0A9EDC?style=flat-square&logo=pytest&logoColor=white)
![Scikit-learn](https://img.shields.io/badge/ML-scikit--learn-F7931E?style=flat-square&logo=scikitlearn&logoColor=white)
![XGBoost](https://img.shields.io/badge/Model-XGBoost-006400?style=flat-square)
![GitHub](https://img.shields.io/badge/Version%20Control-GitHub-181717?style=flat-square&logo=github&logoColor=white)

한국 로또(6/45) 과거 데이터를 바탕으로 수집, 전처리, 시각화, 통계 분석, 모델 비교를 수행하는 프로젝트입니다.

## 🎯 1. 주제 및 선정 이유

- 이 프로젝트는 데이터를 해석할 때 시각화를 중요하게 본다는 점에서 출발했습니다.
- 로또 데이터 역시 숫자 목록으로만 보기보다, 번호 빈도 분포, 합계 분포, 홀짝 비율, 시계열 변화 등을 시각화하면 패턴 존재 여부를 더 직관적으로 확인할 수 있다고 생각했습니다.
- 그래서 "로또는 정말 랜덤인가?"라는 질문을 데이터 시각화와 통계 분석을 통해 검토하는 방향으로 주제를 선정했습니다.
- 목표는 단순한 당첨 예측보다, 과거 데이터에서 예측 가능한 구조가 실제로 존재하는지 확인하는 것입니다.

## ⚙️ 2. 설정 및 실행 방법

설치:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r app\requirements.txt
```

실행:

```powershell
python app/main.py data --source excel
python app/main.py features --window 20
python app/main.py model --window 20 --test-ratio 0.2 --random-seed 42
```

전체 파이프라인:

```powershell
python app/main.py all --source excel --window 20 --test-ratio 0.2 --random-seed 42
```

테스트:

```powershell
pytest app/tests
```

자동 수집 관련 안내:

- 기존 `auto`, `auto_browser` 경로 대신 HTML 기반 동기화를 `app` 내부에서 사용합니다.
- 동행복권 사이트의 접근 제한 때문에 환경에 따라 정상 동작하지 않을 수 있습니다.
- 현재 프로젝트의 기본 데이터 수집 경로는 `excel` 기준으로 사용하는 것을 권장합니다.

## 📁 3. 프로젝트 구조

```text
lotto-analysis/
├─ app/
│  ├─ data/
│  │  ├─ raw/
│  │  └─ processed/
│  ├─ notebooks/
│  ├─ reports/
│  ├─ src/
│  │  ├─ analysis/
│  │  ├─ data/
│  │  ├─ features/
│  │  ├─ models/
│  │  └─ visualization/
│  ├─ tests/
│  ├─ main.py
│  └─ requirements.txt
├─ docker/
├─ Makefile
└─ README.md
```

## 📊 4. 분석 결과

### 모델 비교

| Model | Holdout avg_hit | Holdout number_level_accuracy | Backtest mean_avg_hit | Backtest mean_number_level_accuracy |
| --- | ---: | ---: | ---: | ---: |
| **logistic_regression** | **0.891** | **0.773** | **0.868** | **0.772** |
| **random_baseline** | **0.883** | **0.773** | **0.872** | **0.772** |
| classifier_chain | 0.883 | 0.773 | - | - |
| xgboost | 0.812 | 0.769 | - | - |
| freq_heuristic | 0.766 | 0.767 | 0.782 | 0.768 |
| random_forest | 0.749 | 0.767 | - | - |
| gap_heuristic | 0.715 | 0.765 | 0.805 | 0.769 |

### 어떤 기준이 좋은가

- `subset_accuracy`는 모든 모델이 `0.0`이어서 비교 기준으로 의미가 거의 없었습니다.
- `number_level_accuracy`는 값이 전반적으로 높게 나와 모델 간 차이를 구분하기에는 한계가 있습니다.
- 그래서 실제로 몇 개 번호를 맞췄는지 보여주는 `avg_hit`가 가장 해석하기 좋은 기준입니다.
- 특히 단일 holdout보다 여러 구간에서 반복 검증한 `Backtest mean_avg_hit`를 더 우선적으로 보는 것이 안정적입니다.

### 최종 해석

- Holdout 기준 최고 모델은 **`logistic_regression`** 입니다.
- 반복 검증인 backtest 기준 최고 모델은 **`random_baseline`** 입니다.
- 따라서 현재 결과에서는 특정 모델이 랜덤 기준을 뚜렷하게 이겼다고 보기 어렵습니다.
- 전체적으로는 로또 데이터에서 강한 예측 신호를 찾기 어렵다는 해석이 더 타당합니다.

## 🛠️ 5. 사용된 스킬셋

- Data: `pandas`, `numpy`, `requests`, `openpyxl`
- Visualization: `matplotlib`, `seaborn`, `jupyterlab`
- Statistics: `scipy`, `statsmodels`
- Machine Learning: `scikit-learn`, `xgboost`, `mlxtend`, `joblib`
- Test: `pytest`
- Workflow: `Git`, `GitHub`

## Run Guide

The project still uses the local Excel workbook as the raw data source, but the workbook is now updated from an HTML result page instead of the removed official JSON endpoint.

- Canonical raw workbook: `app/data/raw/lotto_history_latest.xlsx`
- Sync logic: `app/src/data/sync_lotto_html.py`
- Current HTML source: `pyony.com` per-round lotto result page
- Sync behavior: checks the last saved round, fetches only later rounds, and stops immediately when the next round does not exist

### 1. Start Docker

This starts the Jupyter container and keeps it running.

```powershell
docker compose -f docker/docker-compose.yml up --build
```

### 2. Open Notebook

After the container starts, Jupyter Notebook/Lab is available in the browser.

- URL: `http://localhost:8888`
- You can keep using notebooks in `app/notebooks/` as before.

### 3. Run Sync Only

This updates only the raw Excel workbook. It checks the last stored round and appends new rounds only.

```powershell
docker compose -f docker/docker-compose.yml exec jupyter python main.py sync
```

### 4. Run Data Step

This loads the Excel source, preprocesses it, validates it, and writes the processed dataset.

```powershell
docker compose -f docker/docker-compose.yml exec jupyter python main.py data --source excel
```

### 5. Run Full Pipeline

This runs the full workflow: data preprocessing, feature generation, and model execution.

```powershell
docker compose -f docker/docker-compose.yml exec jupyter python main.py all --source excel --window 20 --test-ratio 0.2 --random-seed 42
```

### 6. Command Roles Summary

- `sync`: raw Excel only update
- `data --source excel`: sync if needed, then preprocess and validate data
- `all --source excel ...`: sync if needed, then run data, features, and model steps end-to-end

### 7. Terminal Usage

- Run `docker compose -f docker/docker-compose.yml up --build` in one terminal.
- Run `docker compose ... exec ...` commands in another terminal while the container is running.
