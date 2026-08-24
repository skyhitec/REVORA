"""
Synthetic Payment Data Generator for REVORA

Generates realistic, leak-free payment transactions with failure taxonomy
and synthetic ground-truth recovery targets.
"""

from datetime import datetime, timedelta
import os
from typing import Any, Dict, Optional
import numpy as np
import pandas as pd
import yaml
from faker import Faker

from src.utils.logging_utils import get_logger

logger = get_logger(__name__)


def sigmoid(x: np.ndarray) -> np.ndarray:
    """Computes standard logistic sigmoid function."""
    return 1.0 / (1.0 + np.exp(-np.clip(x, -15.0, 15.0)))


class PaymentDataGenerator:
    """Configurable synthetic payment transaction generator for REVORA."""

    def __init__(self, config_path: Optional[str] = None, seed: int = 42) -> None:
        """Initializes the generator with configuration and random seed."""
        self.seed = seed
        self.rng = np.random.RandomState(seed)
        self.faker = Faker()
        Faker.seed(seed)

        if config_path and os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f)
        else:
            self.config = self._default_config()

    def _default_config(self) -> Dict[str, Any]:
        """Provides fallback configuration if YAML is missing."""
        return {
            "dataset": {"seed": self.seed, "default_rows": 20000},
            "distributions": {
                "success_rate": 0.70,
                "currencies": {"INR": 0.85, "USD": 0.10, "EUR": 0.05},
                "payment_methods": {
                    "UPI": 0.50,
                    "CREDIT_CARD": 0.25,
                    "DEBIT_CARD": 0.15,
                    "NET_BANKING": 0.07,
                    "WALLET": 0.03,
                },
                "gateways": {
                    "RAZORPAY": 0.45,
                    "HDFC_PG": 0.20,
                    "ICICI_PG": 0.15,
                    "CASHFREE": 0.12,
                    "BILLDESK": 0.08,
                },
                "merchant_categories": {
                    "ECOMMERCE": 0.35,
                    "SAAS": 0.20,
                    "EDTECH": 0.15,
                    "GAMING": 0.15,
                    "FINANCIAL_SERVICES": 0.10,
                    "UTILITIES": 0.05,
                },
                "device_types": {
                    "MOBILE_ANDROID": 0.55,
                    "MOBILE_IOS": 0.25,
                    "DESKTOP_WINDOWS": 0.12,
                    "DESKTOP_MAC": 0.08,
                },
            },
            "taxonomy": {
                "SUCCESS": {
                    "is_retryable": False,
                    "base_recovery_prob": None,
                    "description": "Transaction completed successfully.",
                },
                "TEMPORARY_GATEWAY_FAILURE": {
                    "weight": 0.25,
                    "is_retryable": True,
                    "base_recovery_prob": 0.75,
                    "description": "Transient gateway downtime or rate limit.",
                },
                "NETWORK_ERROR": {
                    "weight": 0.20,
                    "is_retryable": True,
                    "base_recovery_prob": 0.70,
                    "description": "Network timeout between merchant, gateway, and bank.",
                },
                "INSUFFICIENT_FUNDS": {
                    "weight": 0.20,
                    "is_retryable": True,
                    "base_recovery_prob": 0.45,
                    "description": "Customer account balance insufficient at transaction time.",
                },
                "BANK_DECLINED": {
                    "weight": 0.12,
                    "is_retryable": False,
                    "base_recovery_prob": 0.20,
                    "description": "Issuing bank declined transaction without specific reason.",
                },
                "AUTHENTICATION_FAILURE": {
                    "weight": 0.08,
                    "is_retryable": False,
                    "base_recovery_prob": 0.30,
                    "description": "3DS / OTP verification failed or timed out.",
                },
                "FRAUD_RISK_BLOCK": {
                    "weight": 0.05,
                    "is_retryable": False,
                    "base_recovery_prob": 0.05,
                    "description": "Transaction flagged by risk engine or fraud rules.",
                },
                "EXPIRED_CARD": {
                    "weight": 0.04,
                    "is_retryable": False,
                    "base_recovery_prob": 0.10,
                    "description": "Card expiry date has passed.",
                },
                "INVALID_PAYMENT_DETAILS": {
                    "weight": 0.03,
                    "is_retryable": False,
                    "base_recovery_prob": 0.08,
                    "description": "Incorrect card number, CVV, or UPI ID.",
                },
                "UNKNOWN_FAILURE": {
                    "weight": 0.03,
                    "is_retryable": True,
                    "base_recovery_prob": 0.40,
                    "description": "Unclassified or ambiguous error response.",
                },
            },
        }

    def generate(self, num_rows: int = 20000) -> pd.DataFrame:
        """
        Generates synthetic payment transactions dataset.

        Args:
            num_rows: Number of transaction records to generate.

        Returns:
            pandas.DataFrame containing synthesized transactions adhering to schema.
        """
        logger.info("Generating %d synthetic payment transactions (seed=%d)...", num_rows, self.seed)

        # 1. Generate core customer and merchant pools for realistic repeat behavior
        num_customers = max(100, int(num_rows * 0.3))
        num_merchants = max(20, int(num_rows * 0.05))

        customer_pool = [f"cust_{i:06d}" for i in range(1, num_customers + 1)]
        merchant_pool = [f"merch_{i:04d}" for i in range(1, num_merchants + 1)]

        customer_ids = self.rng.choice(customer_pool, size=num_rows)
        merchant_ids = self.rng.choice(merchant_pool, size=num_rows)

        transaction_ids = [f"tx_{i:08d}" for i in range(1, num_rows + 1)]

        # 2. Payment details & distributions
        dist_cfg = self.config.get("distributions", {})

        currencies, curr_p = self._get_choices_and_probs(dist_cfg.get("currencies"))
        payment_methods, pm_p = self._get_choices_and_probs(dist_cfg.get("payment_methods"))
        gateways, gw_p = self._get_choices_and_probs(dist_cfg.get("gateways"))
        merch_cats, mc_p = self._get_choices_and_probs(dist_cfg.get("merchant_categories"))
        device_types, dev_p = self._get_choices_and_probs(dist_cfg.get("device_types"))

        gen_currencies = self.rng.choice(currencies, size=num_rows, p=curr_p)
        gen_payment_methods = self.rng.choice(payment_methods, size=num_rows, p=pm_p)
        gen_gateways = self.rng.choice(gateways, size=num_rows, p=gw_p)
        gen_merch_cats = self.rng.choice(merch_cats, size=num_rows, p=mc_p)
        gen_device_types = self.rng.choice(device_types, size=num_rows, p=dev_p)

        card_types_pool = ["VISA", "MASTERCARD", "RUPAY", "AMEX"]
        gen_card_types = []
        for pm in gen_payment_methods:
            if pm in ["CREDIT_CARD", "DEBIT_CARD"]:
                gen_card_types.append(self.rng.choice(card_types_pool, p=[0.45, 0.35, 0.15, 0.05]))
            else:
                gen_card_types.append("NA")

        # Amount generation (log-normal distribution for realistic transaction values)
        amounts = np.round(np.exp(self.rng.normal(loc=6.5, scale=1.2, size=num_rows)), 2)
        amounts = np.clip(amounts, 10.0, 250000.0)

        # Timestamps over the last 90 days
        base_time = datetime(2026, 8, 24, 12, 0, 0)
        time_offsets = self.rng.uniform(0, 90 * 86400, size=num_rows)
        timestamps = [(base_time - timedelta(seconds=sec)).strftime("%Y-%m-%d %H:%M:%S") for sec in time_offsets]

        # 3. Customer behavioral metrics
        cust_hist_success_rate = np.round(self.rng.beta(a=7, b=2, size=num_rows), 4)
        cust_prev_txns = self.rng.poisson(lam=12, size=num_rows)
        cust_prev_failures = np.array([
            self.rng.binomial(n=max(0, tx), p=max(0.01, 1.0 - sr))
            for tx, sr in zip(cust_prev_txns, cust_hist_success_rate)
        ])
        days_since_last_success = np.where(
            cust_prev_txns > 0,
            np.round(self.rng.exponential(scale=14.0, size=num_rows), 1),
            -1.0
        )
        days_since_last_success = np.clip(days_since_last_success, -1.0, 180.0)

        # 4. Device and Risk scores
        device_ids = [f"dev_{self.rng.randint(100000, 999999)}" for _ in range(num_rows)]
        ip_risk_scores = np.round(np.clip(self.rng.beta(a=1.5, b=8.0, size=num_rows) * 100.0, 0.0, 100.0), 2)
        merchant_risk_scores = np.round(np.clip(self.rng.beta(a=2.0, b=10.0, size=num_rows) * 100.0, 0.0, 100.0), 2)

        locations_pool = ["Mumbai, IN", "Bengaluru, IN", "Delhi, IN", "Hyderabad, IN", "Chennai, IN", "New York, US", "London, UK"]
        customer_locations = self.rng.choice(locations_pool, size=num_rows, p=[0.35, 0.25, 0.15, 0.10, 0.08, 0.04, 0.03])

        # 5. Payment Status & Failure Taxonomy Assignment
        taxonomy_cfg = self.config.get("taxonomy", {})
        overall_success_rate = float(dist_cfg.get("success_rate", 0.70))

        # Failure category weights among failed transactions
        failure_cats = [cat for cat in taxonomy_cfg.keys() if cat != "SUCCESS"]
        failure_weights = [float(taxonomy_cfg[cat].get("weight", 0.1)) for cat in failure_cats]
        failure_weights = np.array(failure_weights) / np.sum(failure_weights)

        payment_statuses = []
        failure_codes = []
        failure_reasons = []
        is_retryable_flags = []

        bank_response_codes = []
        gateway_response_codes = []
        avs_results = []
        cvv_results = []
        auth_results = []

        # Determine overall SUCCESS vs FAILED for each transaction
        is_success_mask = self.rng.uniform(size=num_rows) < overall_success_rate

        for i in range(num_rows):
            if is_success_mask[i]:
                payment_statuses.append("SUCCESS")
                failure_codes.append("NONE")
                failure_reasons.append("Transaction completed successfully.")
                is_retryable_flags.append(False)

                bank_response_codes.append("00_SUCCESS")
                gateway_response_codes.append("GATEWAY_200_OK")
                avs_results.append(self.rng.choice(["MATCH", "PARTIAL_MATCH"], p=[0.90, 0.10]))
                cvv_results.append("MATCH" if gen_payment_methods[i] in ["CREDIT_CARD", "DEBIT_CARD"] else "NOT_CHECKED")
                auth_results.append("SUCCESS")
            else:
                f_code = self.rng.choice(failure_cats, p=failure_weights)
                cat_info = taxonomy_cfg.get(f_code, {})

                payment_statuses.append("FAILED")
                failure_codes.append(f_code)
                failure_reasons.append(cat_info.get("description", "Payment failed."))
                is_retryable_flags.append(bool(cat_info.get("is_retryable", False)))

                # Assign security signals and response codes realistic to failure code
                if f_code == "TEMPORARY_GATEWAY_FAILURE":
                    bank_response_codes.append("91_TIMEOUT")
                    gateway_response_codes.append("GATEWAY_504_TIMEOUT")
                    avs_results.append("MATCH")
                    cvv_results.append("MATCH" if gen_payment_methods[i] in ["CREDIT_CARD", "DEBIT_CARD"] else "NOT_CHECKED")
                    auth_results.append("SUCCESS")
                elif f_code == "NETWORK_ERROR":
                    bank_response_codes.append("96_SYSTEM_ERROR")
                    gateway_response_codes.append("GATEWAY_500_INTERNAL_ERROR")
                    avs_results.append("MATCH")
                    cvv_results.append("MATCH" if gen_payment_methods[i] in ["CREDIT_CARD", "DEBIT_CARD"] else "NOT_CHECKED")
                    auth_results.append("SUCCESS")
                elif f_code == "INSUFFICIENT_FUNDS":
                    bank_response_codes.append("51_INSUFFICIENT_FUNDS")
                    gateway_response_codes.append("GATEWAY_400_DECLINED")
                    avs_results.append("MATCH")
                    cvv_results.append("MATCH" if gen_payment_methods[i] in ["CREDIT_CARD", "DEBIT_CARD"] else "NOT_CHECKED")
                    auth_results.append("SUCCESS")
                elif f_code == "BANK_DECLINED":
                    bank_response_codes.append("05_DO_NOT_HONOR")
                    gateway_response_codes.append("GATEWAY_400_DECLINED")
                    avs_results.append("PARTIAL_MATCH")
                    cvv_results.append("MATCH" if gen_payment_methods[i] in ["CREDIT_CARD", "DEBIT_CARD"] else "NOT_CHECKED")
                    auth_results.append("ATTEMPTED")
                elif f_code == "AUTHENTICATION_FAILURE":
                    bank_response_codes.append("65_AUTH_FAILED")
                    gateway_response_codes.append("GATEWAY_401_AUTH_FAILED")
                    avs_results.append("MATCH")
                    cvv_results.append("MATCH" if gen_payment_methods[i] in ["CREDIT_CARD", "DEBIT_CARD"] else "NOT_CHECKED")
                    auth_results.append("FAILED")
                elif f_code == "FRAUD_RISK_BLOCK":
                    bank_response_codes.append("59_SUSPECTED_FRAUD")
                    gateway_response_codes.append("GATEWAY_403_RISK_BLOCK")
                    avs_results.append("NO_MATCH")
                    cvv_results.append("NO_MATCH" if gen_payment_methods[i] in ["CREDIT_CARD", "DEBIT_CARD"] else "NOT_CHECKED")
                    auth_results.append("FAILED")
                elif f_code == "EXPIRED_CARD":
                    bank_response_codes.append("54_EXPIRED_CARD")
                    gateway_response_codes.append("GATEWAY_400_BAD_REQUEST")
                    avs_results.append("MATCH")
                    cvv_results.append("MATCH" if gen_payment_methods[i] in ["CREDIT_CARD", "DEBIT_CARD"] else "NOT_CHECKED")
                    auth_results.append("ATTEMPTED")
                elif f_code == "INVALID_PAYMENT_DETAILS":
                    bank_response_codes.append("14_INVALID_ACCOUNT")
                    gateway_response_codes.append("GATEWAY_400_BAD_REQUEST")
                    avs_results.append("NO_MATCH")
                    cvv_results.append("NO_MATCH" if gen_payment_methods[i] in ["CREDIT_CARD", "DEBIT_CARD"] else "NOT_CHECKED")
                    auth_results.append("FAILED")
                else:  # UNKNOWN_FAILURE
                    bank_response_codes.append("99_UNKNOWN")
                    gateway_response_codes.append("GATEWAY_500_UNKNOWN")
                    avs_results.append("NOT_SUPPORTED")
                    cvv_results.append("NOT_CHECKED")
                    auth_results.append("BYPASSED")

        # 6. Target Generation (RECOVERY TARGET ONLY FOR FAILED PAYMENTS)
        # Note per Correction #2: recovery_probability_target is a SYNTHETIC ground-truth
        # probability generated by the simulator, NOT an ML model prediction.
        # Note per Correction #1: For SUCCESS transactions, target values are np.nan.

        recovery_prob_targets = np.full(num_rows, np.nan, dtype=float)
        recovered_targets = np.full(num_rows, np.nan, dtype=float)

        # Logit offset per failure code
        failure_logit_offsets = {
            "TEMPORARY_GATEWAY_FAILURE": 1.25,
            "NETWORK_ERROR": 1.00,
            "INSUFFICIENT_FUNDS": 0.00,
            "UNKNOWN_FAILURE": -0.20,
            "AUTHENTICATION_FAILURE": -0.75,
            "BANK_DECLINED": -1.20,
            "EXPIRED_CARD": -2.00,
            "INVALID_PAYMENT_DETAILS": -2.20,
            "FRAUD_RISK_BLOCK": -3.00,
        }

        for i in range(num_rows):
            if payment_statuses[i] == "FAILED":
                f_code = failure_codes[i]
                base_logit = failure_logit_offsets.get(f_code, 0.0)

                # Realistic relationship terms:
                # + Higher customer historical success rate -> higher recovery prob
                # - Repeated recent failures -> lower recovery prob
                # - High IP risk -> lower recovery prob
                # - High merchant risk -> lower recovery prob
                cust_effect = 1.6 * (cust_hist_success_rate[i] - 0.7)
                fail_effect = -0.7 * min(1.0, cust_prev_failures[i] / 5.0)
                ip_effect = -1.2 * (ip_risk_scores[i] / 100.0)
                merch_effect = -0.5 * (merchant_risk_scores[i] / 100.0)

                # Add small gaussian noise to logit for realism
                noise = self.rng.normal(loc=0.0, scale=0.3)

                logit = base_logit + cust_effect + fail_effect + ip_effect + merch_effect + noise
                synth_prob = float(sigmoid(np.array([logit]))[0])
                synth_prob = round(float(np.clip(synth_prob, 0.001, 0.999)), 4)

                is_rec = 1 if self.rng.uniform() < synth_prob else 0

                recovery_prob_targets[i] = synth_prob
                recovered_targets[i] = float(is_rec)

        # Build DataFrame adhering strictly to schema order
        df = pd.DataFrame({
            "transaction_id": transaction_ids,
            "customer_id": customer_ids,
            "merchant_id": merchant_ids,
            "amount": amounts,
            "currency": gen_currencies,
            "payment_method": gen_payment_methods,
            "payment_gateway": gen_gateways,
            "card_type": gen_card_types,
            "transaction_timestamp": timestamps,
            "customer_payment_success_rate": cust_hist_success_rate,
            "customer_previous_transactions": cust_prev_txns,
            "customer_previous_failures": cust_prev_failures,
            "days_since_last_successful_payment": days_since_last_success,
            "device_type": gen_device_types,
            "device_id": device_ids,
            "ip_risk_score": ip_risk_scores,
            "customer_location": customer_locations,
            "merchant_category": gen_merch_cats,
            "merchant_risk_score": merchant_risk_scores,
            "avs_result": avs_results,
            "cvv_result": cvv_results,
            "authentication_result": auth_results,
            "bank_response_code": bank_response_codes,
            "gateway_response_code": gateway_response_codes,
            "payment_status": payment_statuses,
            "failure_code": failure_codes,
            "failure_reason": failure_reasons,
            "is_retryable": is_retryable_flags,
            "recovery_probability_target": recovery_prob_targets,
            "recovered": recovered_targets,
        })

        logger.info(
            "Successfully generated %d transactions (SUCCESS: %d, FAILED: %d)",
            len(df),
            (df["payment_status"] == "SUCCESS").sum(),
            (df["payment_status"] == "FAILED").sum(),
        )

        return df

    def _get_choices_and_probs(self, dist_dict: Optional[Dict[str, float]]):
        """Helper to extract normalized choices and probability vectors from config dict."""
        if not dist_dict:
            return ["DEFAULT"], [1.0]
        keys = list(dist_dict.keys())
        probs = np.array(list(dist_dict.values()), dtype=float)
        probs = probs / np.sum(probs)
        return keys, probs
