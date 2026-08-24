"""
Unified One-Click Launcher for REVORA Phase 4.3 Production Demo System.

Launches FastAPI REST Service (port 8000) and Vite Web Dashboard (port 5173).
"""

import sys
import time
import subprocess
import webbrowser
from pathlib import Path


def main():
    root_dir = Path(__file__).resolve().parent.parent
    frontend_dir = root_dir / "frontend"

    print("=" * 80)
    print("🚀 LAUNCHING REVORA PHASE 4 DEMO SYSTEM")
    print("=" * 80)

    # Step 1: Start FastAPI REST Backend
    print("[1/2] Starting FastAPI Backend Service (http://127.0.0.1:8000)...")
    backend_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "src.api.main:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=root_dir,
    )

    time.sleep(2.0)

    # Step 2: Start Vite React Frontend
    print("[2/2] Starting React + Vite Frontend Dashboard (http://localhost:5173)...")
    frontend_proc = subprocess.Popen(
        ["npm.cmd" if sys.platform == "win32" else "npm", "run", "dev"],
        cwd=frontend_dir,
    )

    time.sleep(2.5)

    print("\n" + "=" * 80)
    print("✅ REVORA DEMO SYSTEM IS ONLINE!")
    print("   - API Service:   http://127.0.0.1:8000")
    print("   - OpenAPI Docs:  http://127.0.0.1:8000/docs")
    print("   - Dashboard UI:  http://localhost:5173")
    print("=" * 80)

    try:
        webbrowser.open("http://localhost:5173")
        backend_proc.wait()
    except KeyboardInterrupt:
        print("\nShutting down REVORA demo servers...")
        backend_proc.terminate()
        frontend_proc.terminate()


if __name__ == "__main__":
    main()
