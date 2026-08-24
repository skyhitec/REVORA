"""
API Routes Package for REVORA Phase 4.1.
"""

from src.api.routes.predict import router as predict_router
from src.api.routes.decide import router as decide_router
from src.api.routes.simulate import router as simulate_router
from src.api.routes.audit import router as audit_router
from src.api.routes.metrics import router as metrics_router

__all__ = [
    "predict_router",
    "decide_router",
    "simulate_router",
    "audit_router",
    "metrics_router",
]
