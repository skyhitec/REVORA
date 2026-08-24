# REVORA — AI-Powered Payment Revenue Recovery

> **Razorpay AI Buildathon — Track 03: AI Revenue Recovery**

REVORA is an intelligent fintech solution engineered to close the loop on payment failures — detecting revenue at risk, diagnosing root causes, predicting recovery likelihood, and executing bounded, policy-safe recovery interventions to maximize recovered merchant revenue.

---

## 📌 Current Status: Phase 1 — Payment Intelligence Foundation

> [!IMPORTANT]
> **Phase 1 Scope**: This phase focuses exclusively on establishing a production-grade payment data foundation, failure taxonomy, synthetic dataset generator, data validation pipeline, and reproducible train/val/test splits.
>
> **Disclaimer**: All payment data in this project is 100% synthetic and generated deterministically for simulation and benchmark purposes. No real customer or payment card information is used.

---

## 🚀 Current Capabilities (Phase 1)

* **Synthetic Data Generator**: Configurable, reproducible payment transaction synthesis (`--rows 20000 --seed 42`).
* **Realistic Failure Taxonomy**: 10 failure categories classifying transient failures, bank declines, user authentication issues, and fraud blocks.
* **Data Leakage Prevention**: Strict separation of pre-recovery features from post-outcome target fields (`recovered`, `recovery_probability_target`).
* **Automated Data Validation**: Checks for missing values, duplicate transaction IDs, numerical bounds, taxonomy compliance, and leakage detection.
* **Stratified Dataset Splitting**: Reproducible 70% Train / 15% Validation / 15% Test split with zero transaction overlap.
* **Exploratory Data Analysis (EDA)**: Interactive Jupyter notebook inspecting failure distributions, risk correlations, and recovery rates.
* **Automated Test Suite**: Full `pytest` coverage for dataset generation, validation checks, and split isolation.

---

## 🔮 Future Architecture (Phases 2 & 3)

```text
┌────────────────┐     ┌──────────────────────┐     ┌──────────────────────┐
│ Payment Events │ ──> │ Root Cause Analysis │ ──> │ Recovery Prediction  │
└────────────────┘     └──────────────────────┘     └──────────────────────┘
                                                               │
                                                               v
┌────────────────┐     ┌──────────────────────┐     ┌──────────────────────┐
│Revenue Recovered│ <── │      Audit Trail     │ <── │  AI Recovery Agent   │
└────────────────┘     └──────────────────────┘     └──────────────────────┘
                                                               ^
                                                               │
                                                    ┌──────────────────────┐
                                                    │ Policy/Guardrail Engine│
                                                    └──────────────────────┘
```

---

## 🛠️ Quickstart Guide

### 1. Prerequisites & Installation

Clone the repository and install dependencies using Python 3.11+:

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Generate Synthetic Dataset

To generate the default 20,000 transaction dataset with random seed 42:

```bash
python scripts/generate_dataset.py --rows 20000 --seed 42
```

To generate a smaller sample dataset (1,000 transactions):

```bash
python scripts/generate_dataset.py --rows 1000 --seed 42 --output-dir data/sample
```

Outputs generated:
* `data/raw/transactions.csv` (20,000 raw transactions)
* `data/processed/train.csv` (14,000 rows — 70%)
* `data/processed/val.csv` (3,000 rows — 15%)
* `data/processed/test.csv` (3,000 rows — 15%)

### 3. Run Automated Tests

Run unit tests via `pytest`:

```bash
pytest -v
```

---

## 📂 Repository Structure

```text
revora/
├── README.md                           # Project documentation & quickstart
├── requirements.txt                    # Project Python dependencies
├── .gitignore                          # Git exclusions
├── .env.example                        # Environment variables template
├── config/
│   └── dataset_config.yaml             # Synthetic generator & validation config
├── data/
│   ├── raw/                            # Generated raw datasets
│   ├── processed/                      # Stratified train/val/test CSVs
│   └── sample/                         # Sample dataset output
├── src/
│   ├── __init__.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── generator.py                # Synthetic payment data generator
│   │   ├── validation.py               # Data validation pipeline
│   │   ├── preprocessing.py            # Minimal data preprocessor
│   │   └── split.py                    # Stratified train/val/test splitter
│   └── utils/
│       ├── __init__.py
│       └── logging_utils.py            # Logging configuration
├── notebooks/
│   └── 01_data_exploration.ipynb       # Jupyter notebook for Phase 1 EDA
├── scripts/
│   └── generate_dataset.py             # Dataset generation CLI tool
├── tests/
│   ├── __init__.py
│   ├── test_generator.py               # Unit tests for generator
│   ├── test_validation.py              # Unit tests for validator
│   └── test_split.py                   # Unit tests for splitter
└── docs/
    ├── data_dictionary.md              # Complete dataset schema specification
    ├── failure_taxonomy.md             # Failure category classifications & rules
    └── phase1.md                       # Phase 1 foundation technical summary
```

---

## 🔒 Test Set Protection Protocol

The test set (`data/processed/test.csv`) is held out and protected. It **must not** be used for:
* Feature selection or feature engineering
* Recovery threshold selection
* Model selection or hyperparameter tuning
* Recovery policy/guardrail design

It is strictly reserved for unbiased final evaluation in future phases.
