@echo off
TITLE REVORA Autonomous Payment Failure Recovery System Launcher

echo ================================================================================
echo 🚀 LAUNCHING REVORA PRODUCTION SYSTEM & WEB DASHBOARD
echo ================================================================================

cd /d "%~dp0\.."

:: 1. Start FastAPI REST Backend
echo [1/2] Starting FastAPI REST Backend Service (http://127.0.0.1:8000)...
start "REVORA FastAPI Backend" cmd /k ".venv\Scripts\python.exe -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000"

timeout /t 3 /nobreak > NUL

:: 2. Start React + Vite Frontend
echo [2/2] Starting React + Vite Web Dashboard (http://localhost:5173)...
start "REVORA Vite Frontend" cmd /k "cd frontend && npm run dev"

timeout /t 3 /nobreak > NUL

echo ================================================================================
echo ✅ REVORA SYSTEM IS ONLINE!
echo    - API Backend:   http://127.0.0.1:8000
echo    - OpenAPI Docs:  http://127.0.0.1:8000/docs
echo    - Dashboard UI:  http://localhost:5173
echo ================================================================================

start http://localhost:5173
