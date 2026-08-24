# REVORA — Phase 2: Recovery Prediction Engine

## Executive Summary

Phase 2 implements the **Recovery Prediction Engine** for **REVORA (AI-Powered Payment Revenue Recovery)**.

Building on the Phase 1 Payment Intelligence Foundation, Phase 2 trains, evaluates, and persists machine learning models to predict the probability that a failed payment transaction can be successfully recovered ($P(\text{recovered} = 1)$).

---

## 1. Model Architecture & Pipeline Design

```text
Input Transaction (FAILED)
  │
  ├──> Feature Pipeline (StandardScaler + OneHotEncoder on pre-recovery signals)
  │
  ├──> Baseline Model (Logistic Regression)
  │
  ├──> Primary Advanced Model (XGBoost Classifier)
  │
  ├──> Model Evaluator (Statistical Metrics + Monetized Net Recovery Optimizer)
  │
  └──> Safety-Aware Guardrail Engine & Threshold Filter (tau*)
```

### Primary Models
1. **Baseline Model**: Logistic Regression (`LogisticRegression(C=1.0, solver='lbfgs')`). Provides a simple linear baseline.
2. **Primary Advanced Model**: XGBoost Classifier (`XGBClassifier(n_estimators=150, max_depth=4, learning_rate=0.05)`). Captures non-linear feature interactions and risk patterns.

---

## 2. Leak-Free Feature Engineering

To guarantee zero data leakage, feature engineering operates exclusively on pre-recovery attributes:

* **Predictive Numerical Features**: `amount`, `customer_payment_success_rate`, `customer_previous_transactions`, `customer_previous_failures`, `days_since_last_successful_payment`, `ip_risk_score`, `merchant_risk_score`.
* **Engineered Pre-Recovery Features**: `recent_failure_ratio = customer_previous_failures / (customer_previous_transactions + 1)`.
* **Predictive Categorical Features**: `payment_method`, `payment_gateway`, `card_type`, `merchant_category`, `device_type`, `failure_code`, `avs_result`, `cvv_result`, `authentication_result`, `bank_response_code`, `gateway_response_code`, `is_retryable`.

> [!IMPORTANT]
> All scalers and one-hot encoders are fitted **strictly on the training split (`data/processed/train.csv`)**. Post-outcome fields (`recovered`, `recovery_probability_target`) are strictly excluded from input features.

---

## 3. Revenue & Monetary Metrics Definitions

The evaluator implements exact monetary revenue formulas based on realized outcomes:

### A. Core Revenue Variables
- **Actual Recovered Amount**: $\text{actual\_recovered\_amount}_i = \text{amount}_i \text{ if } \text{recovered}_i == 1 \text{ else } 0$
- **Revenue at Risk**: Total monetary value of all failed transactions:
  $$ R_{\text{risk}} = \sum_{i \in \text{Failed}} \text{amount}_i $$
- **Actual Recoverable Revenue**: Total monetary value of inherently recoverable failed transactions:
  $$ R_{\text{act\_rec}} = \sum_{i \in \text{Failed}, \text{recovered}_i=1} \text{amount}_i $$
- **Expected Recoverable Revenue**: Sum of expected values using model probabilities:
  $$ R_{\text{exp\_rec}} = \sum_{i \in \text{Failed}} \left( \text{amount}_i \times \hat{P}_i \right) $$
- **Gross Revenue Recovered by Interventions**:
  $$ \text{Gross Recovered} = \sum_{i \in \text{Selected Interventions}} \text{actual\_recovered\_amount}_i $$
- **Retry / Intervention Cost**: Total cost of executing automated interventions:
  $$ \text{Retry Cost} = \text{Total Selected Interventions} \times c_{\text{retry\_fee}} $$
- **Net Revenue Recovered (Net Recovery Value)**:
  $$ \text{Net Recovery Value} = \text{Gross Revenue Recovered} - \text{Retry Cost} $$

### B. Distinct Rate Metrics
1. **Intervention Recovery Rate**: Accuracy rate within selected interventions:
   $$ \text{Intervention Recovery Rate} = \frac{\text{Recovered Transactions in Interventions}}{\text{Total Selected Interventions}} $$
2. **Intervention Rate**: Fraction of failed transactions selected for intervention:
   $$ \text{Intervention Rate} = \frac{\text{Total Selected Interventions}}{\text{Total Failed Transactions}} $$
3. **Overall Recovery Yield**: Fraction of total failed transactions successfully recovered via interventions:
   $$ \text{Overall Recovery Yield} = \frac{\text{Recovered Transactions in Interventions}}{\text{Total Failed Transactions}} $$

---

## 4. Safety-Aware Guardrail & Threshold Optimization

### Threshold Grid Search
The evaluator scans candidate decision thresholds $\tau \in [0.05, 0.95]$ on the validation set (`data/processed/val.csv`). A transaction $i$ is selected for intervention if:
$$ \hat{P}_i \ge \tau \quad \text{AND} \quad \text{is\_retryable}_i == \text{True} $$

### Safety Policy Guardrails
* **Non-Retryable Category Override**: Non-retryable failure codes (`FRAUD_RISK_BLOCK`, `EXPIRED_CARD`, `INVALID_PAYMENT_DETAILS`, `BANK_DECLINED`, `AUTHENTICATION_FAILURE`) are **strictly blocked** from intervention regardless of probability score.
* **Configurable Constraints**: `max_intervention_rate` (cap on transaction volume), `max_retry_cost` (budget cap).

---

## 5. Test Set Protection Protocol

The held-out test set (`data/processed/test.csv`) is strictly locked during all feature engineering, model selection, hyperparameter tuning, and threshold optimization. It is evaluated **strictly once** using `scripts/evaluate_model.py` after freezing all development decisions.

---

## 6. Assumptions & Limitations

1. **Static Retry Cost**: Retry execution cost is modeled as a fixed cost per attempt (default INR 10.0 or $0.50).
2. **Simulated Ground Truth**: Model targets rely on Phase 1 synthetic probability distributions. Downstream deployment in Phase 3 will ingest real production logs.
