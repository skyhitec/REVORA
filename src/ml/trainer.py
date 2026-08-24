"""
Primary Advanced XGBoost Model Trainer for REVORA Phase 2

Implements XGBoost classifier training, probability estimation, and feature importance.
"""

from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
from xgboost import XGBClassifier
import shap

from src.utils.logging_utils import get_logger

logger = get_logger(__name__)


class XGBoostRecoveryModel:
    """Primary Advanced XGBoost Classifier for recovery prediction."""

    def __init__(
        self,
        n_estimators: int = 150,
        max_depth: int = 4,
        learning_rate: float = 0.05,
        subsample: float = 0.8,
        colsample_bytree: float = 0.8,
        random_state: int = 42,
    ) -> None:
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.learning_rate = learning_rate
        self.subsample = subsample
        self.colsample_bytree = colsample_bytree
        self.random_state = random_state

        self.model = XGBClassifier(
            n_estimators=self.n_estimators,
            max_depth=self.max_depth,
            learning_rate=self.learning_rate,
            subsample=self.subsample,
            colsample_bytree=self.colsample_bytree,
            random_state=self.random_state,
            eval_metric="logloss",
        )
        self.is_fitted = False

    def fit(self, X: np.ndarray, y: np.ndarray, eval_set: Optional[List] = None) -> "XGBoostRecoveryModel":
        """Fits XGBoost model on feature matrix X and target y."""
        logger.info("Training Primary Advanced XGBoost model on %d samples...", X.shape[0])
        self.model.fit(X, y, eval_set=eval_set, verbose=False)
        self.is_fitted = True
        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Returns predicted probability of recovery (class 1)."""
        if not self.is_fitted:
            raise RuntimeError("XGBoostRecoveryModel must be fitted before predicting!")
        return self.model.predict_proba(X)[:, 1]

    def predict(self, X: np.ndarray, threshold: float = 0.5) -> np.ndarray:
        """Returns binary prediction flags given threshold."""
        probs = self.predict_proba(X)
        return (probs >= threshold).astype(int)

    def get_feature_importances(self, feature_names: List[str]) -> pd.DataFrame:
        """Returns sorted DataFrame of feature importances."""
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted to compute feature importances!")
        importances = self.model.feature_importances_
        fi_df = pd.DataFrame({"feature": feature_names, "importance": importances})
        return fi_df.sort_values(by="importance", ascending=False).reset_index(drop=True)

    def get_shap_explainer_and_values(self, X: np.ndarray):
        """Computes Tree SHAP explainer and SHAP values for model interpretability."""
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before computing SHAP values!")
        explainer = shap.TreeExplainer(self.model)
        shap_values = explainer.shap_values(X)
        return explainer, shap_values
