# REVORA — Phase 3: Recovery Decision & Policy Engine

## Executive Summary

Phase 3 implements the **Recovery Decision & Policy Engine** for **REVORA (AI-Powered Payment Revenue Recovery)**.

Building on the Phase 1 Payment Intelligence Foundation and Phase 2 Recovery Prediction Engine, Phase 3 transforms machine learning recovery probabilities ($P(\text{recovered} = 1)$) into **safe, deterministic, explainable, cost-bounded, and policy-governed recovery intervention decisions**.

---

## 1. Architectural Pipeline Design

```text
Input Transaction (FAILED)
  │
  ├──> Frozen Phase 2 Recovery Prediction (Prob = P_rec)
  │
  ├──> Failure Category Diagnosis (Classifier)
  │
  ├──> Deterministic Safety Guardrails Filter (Hard Rules)
  │
  ├──> Multi-Signal Risk Classification Engine (LOW / MEDIUM / HIGH / CRITICAL)
  │
  ├──> Expected Recovery Value (ERV) & Cost Calculator
  │
  ├──> Decision-Policy Matrix Action Matcher
  │
  ├──> Explainable Decision Builder (Human-Readable Reason)
  │
  └──> Immutable Audit Trail System (SHA-256 Hash Chained JSONL)
```

---

## 2. Bounded Intervention Taxonomy

Phase 3 selects among 7 bounded recovery intervention actions:

1. **`RETRY`**: Immediate automated gateway retry for transient infrastructure failures with high recovery potential.
2. **`DELAY_AND_RETRY`**: Scheduled off-peak or pay-day retry window for insufficient funds.
3. **`RETRY_WITH_CAUTION`**: Cautionary retry for network/unclassified errors under moderate risk.
4. **`CUSTOMER_ACTION_REQUIRED`**: Proactive customer nudge (SMS/WhatsApp) to re-authenticate or update payment credentials.
5. **`ESCALATE`**: High-value transaction escalation to merchant desk or VIP customer support.
6. **`BLOCK`**: Strict security and fraud risk block.
7. **`NO_ACTION`**: Skip recovery when expected recovery value is non-positive or below optimal threshold.

---

## 3. Decision-Policy Matrix

Every decision is strictly governed by the following deterministic policy matrix:

| Failure Category | Retryable | Risk Level | ML Prob ($P$) | Net ERV Condition | Selected Intervention | Active Policy Rule |
| :--- | :---: | :---: | :---: | :---: | :--- | :--- |
| `FRAUD_RISK_BLOCK` | False | `CRITICAL` / `HIGH` | Any | Any | **`BLOCK`** | `RULE_FRAUD_HARD_BLOCK` |
| `EXPIRED_CARD` | False | `MEDIUM` / `HIGH` | Any | Any | **`CUSTOMER_ACTION_REQUIRED`** | `RULE_NON_RETRYABLE_CODE` |
| `INVALID_PAYMENT_DETAILS` | False | `MEDIUM` / `HIGH` | Any | Any | **`CUSTOMER_ACTION_REQUIRED`** | `RULE_NON_RETRYABLE_CODE` |
| `AUTHENTICATION_FAILURE` | False | `MEDIUM` | Any | Amount $\ge$ ₹10,000 | **`ESCALATE`** | High-value auth failure |
| `AUTHENTICATION_FAILURE` | False | `MEDIUM` | Any | Amount $<$ ₹10,000 | **`CUSTOMER_ACTION_REQUIRED`** | `RULE_NON_RETRYABLE_CODE` |
| `BANK_DECLINED` | False | `HIGH` | $P < \tau^*$ | Any | **`NO_ACTION`** | Non-retryable bank decline |
| `BANK_DECLINED` | False | `HIGH` | $P \ge \tau^*$ | Amount $\ge$ ₹5,000 | **`ESCALATE`** | Manual bank inquiry |
| `INSUFFICIENT_FUNDS` | True | `MEDIUM` | $P \ge \tau^*$ | Net ERV $>$ ₹5.00 | **`DELAY_AND_RETRY`** | Off-peak pay-day retry window |
| `INSUFFICIENT_FUNDS` | True | `MEDIUM` | $P < \tau^*$ | Any | **`CUSTOMER_ACTION_REQUIRED`** | Low funds recovery score |
| `TEMPORARY_GATEWAY_FAILURE`| True | `LOW` / `MEDIUM` | $P \ge \tau^*$ | Net ERV $>$ ₹5.00 | **`RETRY`** | Immediate automated retry |
| `NETWORK_ERROR` | True | `LOW` | $P \ge 0.50$ | Net ERV $>$ ₹5.00 | **`RETRY`** | High prob network error |
| `NETWORK_ERROR` | True | `MEDIUM` | $\tau^* \le P < 0.50$ | Net ERV $>$ ₹5.00 | **`RETRY_WITH_CAUTION`** | Medium prob network error |
| `UNKNOWN_FAILURE` | True | `MEDIUM` | $P \ge \tau^*$ | Net ERV $>$ ₹5.00 | **`RETRY_WITH_CAUTION`** | Unclassified retry with caution |
| *Any Category* | Any | `CRITICAL` | Any | Any | **`BLOCK`** | `RULE_CRITICAL_RISK_BLOCK` |

---

## 4. Expected Recovery Value (ERV) & Financial Formulas

1. **Gross Expected Recovery Value**:
   $$ \text{Gross ERV} = \text{amount} \times \hat{P}_{\text{recovery}} $$
2. **Intervention Cost Structure**:
   - `RETRY`: ₹10.00
   - `DELAY_AND_RETRY`: ₹12.00
   - `RETRY_WITH_CAUTION`: ₹15.00
   - `CUSTOMER_ACTION_REQUIRED`: ₹5.00
   - `ESCALATE`: ₹25.00
   - `BLOCK` / `NO_ACTION`: ₹0.00
3. **Customer Friction Penalty**:
   $$ \text{Cost}_{\text{friction}} = \min\left( 2.0 \times (1 + \text{customer\_previous\_failures}) \times 1.5, 50.0 \right) $$
4. **Net Expected Recovery Value**:
   $$ \text{Net ERV} = \text{Gross ERV} - \text{Intervention Cost} - \text{Cost}_{\text{friction}} $$

---

## 5. Cryptographic Audit Trail System

Every decision event is recorded in `data/audit/audit_trail.jsonl` with sequence locking and SHA-256 hash chaining:

$$ H_0 = \text{SHA256}(\text{"REVORA_PHASE3_GENESIS"}) $$
$$ H_i = \text{SHA256}\left( H_{i-1} \parallel \text{CanonicalJSON}(R_i) \right) $$

Verification script `src/audit/verifier.py` validates chain integrity and flags any data tampering or missing log lines.
