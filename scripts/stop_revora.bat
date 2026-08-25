@echo off
TITLE REVORA System Shutdown Script

echo ================================================================================
echo 🛑 SHUTTING DOWN REVORA DEVELOPMENT PROCESSES
echo ================================================================================

echo Stopping uvicorn FastAPI backend server processes...
taskkill /FI "WINDOWTITLE eq REVORA FastAPI Backend*" /F /T > NUL 2>&1

echo Stopping Vite React frontend server processes...
taskkill /FI "WINDOWTITLE eq REVORA Vite Frontend*" /F /T > NUL 2>&1

echo ================================================================================
echo ✅ REVORA PROCESSES STOPPED SAFELY.
echo ================================================================================
pause
