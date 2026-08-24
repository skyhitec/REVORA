"""
Synthetic Payment Failure Event Generator for REVORA Phase 4.2.

Produces realistic payment failure transaction objects matching Phase 1/2 schemas.
"""

import uuid
import random
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List


FAILURE_TAXONOMY_SCENARIOS = [
    ("TEMPORARY_GATEWAY_FAILURE", True, 0.35),
    ("GATEWAY_TIMEOUT", True, 0.25),
    ("INSUFFICIENT_FUNDS", True, 0.15),
    ("EXPIRED_CARD", False, 0.08),
    ("INVALID_CREDENTIALS", False, 0.05),
    ("AUTHENTICATION_FAILURE", True, 0.05),
    ("BANK_DECLINED", True, 0.04),
    ("FRAUD_RISK_BLOCK", False, 0.02),
    ("CUSTOMER_VELOCITY_EXCEEDED", False, 0.01),
]

PAYMENT_METHODS = ["UPI", "CREDIT_CARD", "DEBIT_CARD", "NET_BANKING", "WALLET"]
PAYMENT_GATEWAYS = ["RAZORPAY", "CASHFREE", "PAYU", "BILLDESK"]
MERCHANT_CATEGORIES = ["ECOMMERCE", "TRAVEL", "GAMING", "UTILITIES", "EDTECH", "FINTECH"]
DEVICE_TYPES = ["MOBILE_ANDROID", "MOBILE_IOS", "DESKTOP_WEB", "MOBILE_WEB"]


class TransactionEventGenerator:
    """Generates synthetic transaction events with configurable distributions and seed control."""

    def __init__(self, seed: Optional[int] = None) -> None:
        self.rng = random.Random(seed) if seed is not None else random.Random()
        self.seed = seed

    def set_seed(self, seed: int) -> None:
        """Resets the internal RNG state for deterministic replay."""
        self.rng = random.Random(seed)
        self.seed = seed

    def generate_event(
        self,
        override_amount: Optional[float] = None,
        override_failure_code: Optional[str] = None,
        override_payment_method: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generates a single realistic transaction failure event.

        Returns:
            Dict containing full transaction attributes matching Phase 1/2 schema.
        """
        tx_id = f"tx_sim_{uuid.UUID(int=self.rng.getrandbits(128)).hex[:12]}"
        cust_id = f"cust_{self.rng.randint(1000, 9999)}"
        merch_id = f"merch_{self.rng.randint(100, 999)}"

        if override_failure_code:
            failure_code = override_failure_code
            is_retryable = failure_code not in [
                "EXPIRED_CARD", "INVALID_CREDENTIALS", "FRAUD_RISK_BLOCK",
                "CUSTOMER_VELOCITY_EXCEEDED", "SUCCESS"
            ]
        else:
            codes, retryable_flags, weights = zip(*FAILURE_TAXONOMY_SCENARIOS)
            selected_idx = self.rng.choices(range(len(codes)), weights=weights, k=1)[0]
            failure_code = codes[selected_idx]
            is_retryable = retryable_flags[selected_idx]

        payment_status = "FAILED"
        payment_method = override_payment_method or self.rng.choice(PAYMENT_METHODS)
        payment_gateway = self.rng.choice(PAYMENT_GATEWAYS)
        merchant_category = self.rng.choice(MERCHANT_CATEGORIES)
        device_type = self.rng.choice(DEVICE_TYPES)

        if override_amount:
            amount = round(override_amount, 2)
        else:
            r_val = self.rng.random()
            if r_val < 0.6:
                amount = round(self.rng.uniform(100.0, 2500.0), 2)
            elif r_val < 0.9:
                amount = round(self.rng.uniform(2500.0, 15000.0), 2)
            else:
                amount = round(self.rng.uniform(15000.0, 50000.0), 2)

        prev_txns = self.rng.randint(5, 30)
        if failure_code == "CUSTOMER_VELOCITY_EXCEEDED":
            prev_fails = 4
        else:
            prev_fails = self.rng.randint(0, 1)

        success_rate = round((prev_txns - prev_fails) / prev_txns, 4)
        days_since_success = round(self.rng.uniform(0.1, 10.0), 1)

        # Risk scores in [0.0, 1.0] standard scale
        if failure_code == "FRAUD_RISK_BLOCK":
            ip_risk_score = round(self.rng.uniform(0.85, 0.99), 3)
            merchant_risk_score = round(self.rng.uniform(0.50, 0.90), 3)
        else:
            ip_risk_score = round(self.rng.uniform(0.01, 0.15), 3)
            merchant_risk_score = round(self.rng.uniform(0.01, 0.15), 3)

        timestamp = datetime.now(timezone.utc).isoformat()

        return {
            "transaction_id": tx_id,
            "customer_id": cust_id,
            "merchant_id": merch_id,
            "amount": amount,
            "currency": "INR",
            "payment_method": payment_method,
            "payment_gateway": payment_gateway,
            "card_type": "CREDIT_CARD" if payment_method == "CREDIT_CARD" else None,
            "failure_code": failure_code,
            "payment_status": payment_status,
            "is_retryable": is_retryable,
            "customer_payment_success_rate": success_rate,
            "customer_previous_transactions": prev_txns,
            "customer_previous_failures": prev_fails,
            "days_since_last_successful_payment": days_since_success,
            "device_type": device_type,
            "merchant_category": merchant_category,
            "ip_risk_score": ip_risk_score,
            "merchant_risk_score": merchant_risk_score,
            "avs_result": "MATCH" if failure_code != "INVALID_CREDENTIALS" else "NO_MATCH",
            "cvv_result": "MATCH" if failure_code != "INVALID_CREDENTIALS" else "NO_MATCH",
            "authentication_result": "SUCCESS" if failure_code not in ["AUTHENTICATION_FAILURE", "FRAUD_RISK_BLOCK"] else "FAILED",
            "bank_response_code": "00" if failure_code in ["TEMPORARY_GATEWAY_FAILURE", "GATEWAY_TIMEOUT"] else "51",
            "gateway_response_code": failure_code,
            "timestamp": timestamp,
        }

    def generate_batch(self, count: int) -> List[Dict[str, Any]]:
        """Generates a batch of N transaction events."""
        return [self.generate_event() for _ in range(count)]
