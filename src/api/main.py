"""
Main FastAPI Application Entrypoint for REVORA Phase 4.1 Production API.
"""

from datetime import datetime, timezone
from fastapi import FastAPI, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from src.api.schemas import HealthResponse
from src.api.routes import (
    predict_router,
    decide_router,
    simulate_router,
    audit_router,
    metrics_router,
)


def create_app() -> FastAPI:
    """Factory function to build and configure the REVORA FastAPI application."""
    app = FastAPI(
        title="REVORA - Autonomous Payment Recovery & Policy Engine API",
        description=(
            "Production REST API for REVORA (Phase 4.1). "
            "Exposes frozen Phase 2 ML prediction, Phase 3 decision policy engine, "
            "financial Expected Recovery Value (ERV) math, and cryptographic SHA-256 audit trail verification."
        ),
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # Configure CORS for local development & frontend demo
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Custom exception handler for request validation errors
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "Unprocessable Entity",
                "message": "Malformed request payload or invalid parameters.",
                "details": exc.errors(),
            },
        )

    # Custom exception handler for general HTTP exceptions
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal Server Error",
                "message": "An internal server error occurred while processing the request.",
            },
        )

    # Health Check Endpoint
    @app.get(
        "/health",
        response_model=HealthResponse,
        status_code=status.HTTP_200_OK,
        tags=["Health"],
        summary="Service Health Check",
        description="Returns API status, version, phase, and current UTC timestamp.",
    )
    def health_check() -> HealthResponse:
        return HealthResponse(
            status="ok",
            version="1.0.0",
            phase="Phase 4.1 — Production FastAPI API Layer",
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    # Include route modules
    app.include_router(predict_router)
    app.include_router(decide_router)
    app.include_router(simulate_router)
    app.include_router(audit_router)
    app.include_router(metrics_router)

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.main:app", host="127.0.0.1", port=8000, reload=True)
