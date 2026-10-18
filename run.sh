#!/usr/bin/env bash
set -e

# Resolve repository root directory
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

echo "===================================================================="
echo "              KDG v2 - Omni-Stack Local Orchestrator"
echo "===================================================================="

# 1. Resolve Python binary (Windows Git Bash vs Unix venv vs system)
PYTHON_BIN=""
if [ -f "$ROOT_DIR/.venv/Scripts/python.exe" ]; then
    PYTHON_BIN="$ROOT_DIR/.venv/Scripts/python.exe"
elif [ -f "$ROOT_DIR/.venv/bin/python" ]; then
    PYTHON_BIN="$ROOT_DIR/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_BIN="python"
else
    echo "[ERROR] Python environment not found! Please configure .venv or install Python."
    exit 1
fi

# 2. Check npm
if ! command -v npm >/dev/null 2>&1; then
    echo "[ERROR] npm is not found in PATH! Please install Node.js."
    exit 1
fi

# 3. Check frontend dependencies
if [ ! -d "$ROOT_DIR/frontend/node_modules" ]; then
    echo "[INFO] frontend/node_modules not found. Running npm install..."
    (cd "$ROOT_DIR/frontend" && npm install)
fi

# Cleanup handler on exit or interruption
cleanup() {
    echo ""
    echo "[INFO] Shutting down KDG services..."
    if [ -n "$BACKEND_PID" ]; then
        kill "$BACKEND_PID" 2>/dev/null || true
        if command -v taskkill >/dev/null 2>&1; then
            taskkill //F //T //PID "$BACKEND_PID" >/dev/null 2>&1 || true
        fi
    fi
    if [ -n "$FRONTEND_PID" ]; then
        kill "$FRONTEND_PID" 2>/dev/null || true
        if command -v taskkill >/dev/null 2>&1; then
            taskkill //F //T //PID "$FRONTEND_PID" >/dev/null 2>&1 || true
        fi
    fi
    wait 2>/dev/null || true
    echo "[INFO] All services successfully stopped."
}

trap cleanup INT TERM EXIT

echo "[1/2] Starting Backend service on http://127.0.0.1:8000 ..."
"$PYTHON_BIN" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload &
BACKEND_PID=$!

echo "[2/2] Starting Frontend Vite dev server on http://localhost:5173 ..."
(cd "$ROOT_DIR/frontend" && npm run dev) &
FRONTEND_PID=$!

echo ""
echo "===================================================================="
echo "  All services are active:"
echo "    - Backend API:  http://127.0.0.1:8000 (Docs: http://127.0.0.1:8000/docs)"
echo "    - Frontend App: http://localhost:5173"
echo "  Press Ctrl+C to terminate both services."
echo "===================================================================="
echo ""

wait $BACKEND_PID $FRONTEND_PID

