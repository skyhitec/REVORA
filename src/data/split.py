"""
Train / Validation / Test Dataset Splitter for REVORA

Performs reproducible 70% / 15% / 15% stratified splitting of transactions.

PROTECTION RULE (Correction #4):
The held-out test set must NEVER be used for feature engineering, threshold
selection, model selection, hyperparameter tuning, or recovery-policy design.
It is strictly reserved for unbiased final evaluation in future phases.
"""

from typing import Dict, Tuple
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from src.utils.logging_utils import get_logger

logger = get_logger(__name__)


class DatasetSplitter:
    """Splits dataset into 70% train, 15% validation, and 15% test subsets with stratification."""

    def __init__(
        self,
        train_ratio: float = 0.70,
        val_ratio: float = 0.15,
        test_ratio: float = 0.15,
        seed: int = 42,
    ) -> None:
        """
        Initializes the splitter with ratios and seed.

        Args:
            train_ratio: Fraction for training set (default 0.70)
            val_ratio: Fraction for validation set (default 0.15)
            test_ratio: Fraction for test set (default 0.15)
            seed: Random seed for reproducibility
        """
        if not np.isclose(train_ratio + val_ratio + test_ratio, 1.0):
            raise ValueError(f"Ratios must sum to 1.0 (got {train_ratio + val_ratio + test_ratio})")

        self.train_ratio = train_ratio
        self.val_ratio = val_ratio
        self.test_ratio = test_ratio
        self.seed = seed

    def split(self, df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """
        Performs stratified train/val/test split on the dataset.

        Stratification accounts for both payment_status (SUCCESS vs FAILED)
        and recovery outcome (0 vs 1).

        Returns:
            Dict containing 'train', 'validation', and 'test' DataFrames.
        """
        logger.info(
            "Splitting %d transactions into ratios %.2f / %.2f / %.2f (seed=%d)...",
            len(df),
            self.train_ratio,
            self.val_ratio,
            self.test_ratio,
            self.seed,
        )

        # Create composite stratification key
        strat_key = []
        for _, row in df.iterrows():
            status = row["payment_status"]
            rec = row["recovered"]
            if status == "SUCCESS":
                strat_key.append("SUCCESS")
            elif pd.isna(rec):
                strat_key.append("FAILED_UNKNOWN")
            else:
                strat_key.append(f"FAILED_{int(rec)}")

        df_copy = df.copy()
        df_copy["_strat_key"] = strat_key

        # First split: train vs (val + test)
        temp_ratio = self.val_ratio + self.test_ratio
        train_df, temp_df = train_test_split(
            df_copy,
            test_size=temp_ratio,
            random_state=self.seed,
            stratify=df_copy["_strat_key"],
        )

        # Second split: val vs test (split temp_df 50/50 relative to val_ratio and test_ratio)
        val_relative_ratio = self.val_ratio / temp_ratio
        val_df, test_df = train_test_split(
            temp_df,
            test_size=(1.0 - val_relative_ratio),
            random_state=self.seed,
            stratify=temp_df["_strat_key"],
        )

        # Clean up temporary stratification column
        for d in [train_df, val_df, test_df]:
            d.drop(columns=["_strat_key"], inplace=True)

        # Verify zero transaction ID overlap
        train_ids = set(train_df["transaction_id"])
        val_ids = set(val_df["transaction_id"])
        test_ids = set(test_df["transaction_id"])

        assert len(train_ids.intersection(val_ids)) == 0, "Overlap detected between Train and Val splits!"
        assert len(train_ids.intersection(test_ids)) == 0, "Overlap detected between Train and Test splits!"
        assert len(val_ids.intersection(test_ids)) == 0, "Overlap detected between Val and Test splits!"

        logger.info(
            "Splitting complete: Train=%d (%.1f%%), Val=%d (%.1f%%), Test=%d (%.1f%%)",
            len(train_df),
            len(train_df) / len(df) * 100,
            len(val_df),
            len(val_df) / len(df) * 100,
            len(test_df),
            len(test_df) / len(df) * 100,
        )

        return {
            "train": train_df.reset_index(drop=True),
            "validation": val_df.reset_index(drop=True),
            "test": test_df.reset_index(drop=True),
        }
