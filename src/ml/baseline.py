"""
Baseline Logistic Regression Model for REVORA Phase 2

Serves as the benchmark linear model for payment recovery prediction.
"""

from typing import Dict, Any
import numpy as np
from sklearn.linear_model import LogisticRegression

from src.utils.logging_utils import get_logger

logger = get_logger(__name__)


class BaselineLogisticRegression:
    """Logistic Regression baseline classifier for recovery prediction."""

    def __init__(self, C: float = 1.0, random_state: int = 42) -> None:
        self.C = C
        self.random_state = random_state
        self.model = LogisticRegression(
            C=self.C,
            max_iter=1000,
            random_state=self.random_state,
            solver="lbfgs"
        )
        self.is_fitted = False

    def fit(self, X: np.ndarray, y: np.ndarray) -> "BaselineLogisticRegression":
        """Fits baseline logistic regression model on training feature matrix X and target y."""
        logger.info("Training Baseline Logistic Regression on %d samples (%d features)...", X.shape[0], X.shape[1])
        self.model.fit(X, y)
        self.is_fitted = True
        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Returns predicted probability of recovery (class 1)."""
        if not self.is_fitted:
            raise RuntimeError("BaselineLogisticRegression model must be fitted before predicting!")
        return self.model.predict_proba(X)[:, 1]

    def predict(self, X: np.ndarray, threshold: float = 0.5) -> np.ndarray:
        """Returns binary predictions based on decision threshold."""
        probs = self.predict_proba(X)
        return (probs >= threshold).astype(int)
