# REVORA Failure Taxonomy Documentation

> [!NOTE]
> Disclaimer: These failure classifications are synthetic categories designed for the REVORA prototype. They do not represent Razorpay's internal proprietary classification schema.

---

## Overview

In payment revenue recovery, understanding **why** a transaction failed is the critical first step before choosing an automated recovery intervention. Failures fall along a spectrum from **transient operational glitches** (high recovery likelihood via smart retry) to **hard customer/fraud declines** (zero recovery likelihood via simple retry, requiring user notification or instrument fallback).

---

## Taxonomy Classifications

### 1. `SUCCESS`
* **Meaning**: Transaction completed without errors.
* **Example Scenario**: Customer enters valid card credentials, 3DS authentication succeeds, and the issuing bank approves the debit.
* **Retryable?**: No (Not applicable).
* **Expected Recovery Behavior**: Target is `NaN` (Not Applicable).
* **Why it matters to REVORA**: Establishes baseline transaction population and normal behavior metrics.

---

### 2. `TEMPORARY_GATEWAY_FAILURE`
* **Meaning**: Transient infrastructure failure, rate-limiting, or temporary service degradation at the payment gateway level.
* **Example Scenario**: Razorpay or issuing bank gateway returns HTTP 504 Gateway Timeout during peak flash sale traffic.
* **Retryable?**: **Yes (High priority for automatic retry)**.
* **Expected Recovery Behavior**: High recovery rate (~70% - 85%) if retried within a short exponential backoff window (15s to 5 mins).
* **Why it matters to REVORA**: Represents low-hanging fruit where automated smart retries recover revenue without customer friction.

---

### 3. `NETWORK_ERROR`
* **Meaning**: TCP socket timeout or packet loss during communication between merchant server, payment gateway, and acquiring bank.
* **Example Scenario**: Mobile network drops connection right as 3DS redirect payload is posted to bank server.
* **Retryable?**: **Yes (High priority)**.
* **Expected Recovery Behavior**: High recovery rate (~65% - 80%) upon immediate or short-delay automated retry.
* **Why it matters to REVORA**: High recovery probability; requires checking idempotency keys before retrying to prevent double debiting.

---

### 4. `INSUFFICIENT_FUNDS`
* **Meaning**: Customer's bank account or credit line does not have sufficient balance to cover the transaction amount.
* **Example Scenario**: A recurring monthly subscription billing attempt fails because salary has not yet been credited to the account.
* **Retryable?**: **Conditionally Yes**.
* **Expected Recovery Behavior**: Moderate recovery rate (~35% - 50%). Immediate retry fails; recovery improves significantly when retried on salary credit dates (e.g. 1st or 30th of the month) or via WhatsApp payment link reminder.
* **Why it matters to REVORA**: Demonstrates the need for **optimal timing intelligence** rather than naive immediate retries.

---

### 5. `BANK_DECLINED`
* **Meaning**: Generic non-specific hard decline returned by customer's issuing bank (`Do Not Honor`).
* **Example Scenario**: Bank internal risk algorithms decline an international transaction or block suspicious velocity.
* **Retryable?**: **No (Not immediately retryable)**.
* **Expected Recovery Behavior**: Low recovery rate (~15% - 25%). Retrying immediately will repeatedly fail.
* **Why it matters to REVORA**: Prevents wasting gateway API costs and damaging merchant risk scores by suppressing automated retries.

---

### 6. `AUTHENTICATION_FAILURE`
* **Meaning**: Customer failed 3DS authentication, entered incorrect OTP, or abandoned the OTP modal window.
* **Example Scenario**: User receives SMS OTP late, inputs expired code, or closes checkout browser window.
* **Retryable?**: **No (Requires customer action)**.
* **Expected Recovery Behavior**: Moderate recovery rate (~25% - 40%) only if customer is nudged via SMS/WhatsApp checkout recovery link to complete 3DS.
* **Why it matters to REVORA**: Triggers customer-facing recovery interventions (e.g. 1-click checkout recovery link) rather than backend automated retries.

---

### 7. `FRAUD_RISK_BLOCK`
* **Meaning**: Risk engine or fraud prevention module flagged transaction due to suspicious IP, stolen card signals, or high anomaly score.
* **Example Scenario**: IP geolocation mismatch, high velocity card testing attempt, or blacklisted BIN range.
* **Retryable?**: **No (Strictly non-retryable)**.
* **Expected Recovery Behavior**: Very low recovery rate (<5%).
* **Why it matters to REVORA**: Guardrail enforcement — safety policy must strictly block automated retries on fraud blocks to prevent card testing attacks.

---

### 8. `EXPIRED_CARD`
* **Meaning**: Payment instrument card expiration date is in the past.
* **Example Scenario**: Customer's saved card vaulted in 2023 expired in July 2026.
* **Retryable?**: **No (Non-retryable without instrument update)**.
* **Expected Recovery Behavior**: Low recovery rate (~10%) unless merchant updates card metadata via Network Tokenization / Account Updater.
* **Why it matters to REVORA**: Identifies cases where recovery intervention must prompt customer to update card details or select UPI.

---

### 9. `INVALID_PAYMENT_DETAILS`
* **Meaning**: Card number, CVV, expiry date, or UPI VPA entered incorrectly.
* **Example Scenario**: Customer mistypes card number or provides malformed UPI ID (`user@invalidbank`).
* **Retryable?**: **No**.
* **Expected Recovery Behavior**: Low recovery rate (~8%).
* **Why it matters to REVORA**: Backend retries are futile; requires inline checkout validation nudge.

---

### 10. `UNKNOWN_FAILURE`
* **Meaning**: Ambiguous or unclassified error response from upstream gateway or bank.
* **Example Scenario**: Gateway returns non-standard HTTP 500 error code with unparseable payload.
* **Retryable?**: **Conditionally Yes**.
* **Expected Recovery Behavior**: Moderate recovery rate (~35% - 45%).
* **Why it matters to REVORA**: Demonstrates real-world edge cases where AI agents must handle ambiguous signals safely.
