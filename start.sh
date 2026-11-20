#!/usr/bin/env bash
# OmniSEO Studio - Portable Launcher for macOS & Linux

set -e

echo "========================================================"
echo "  OmniSEO Studio - Portable Web Audit & Ranking Engine"
echo "========================================================"
echo ""

# 1. Check Python
if command -v python3 &>/dev/null; then
    PYTHON_CMD=python3
elif command -v python &>/dev/null; then
    PYTHON_CMD=python
else
    echo "[ERROR] Python 3 was not found on your system!"
    echo "Please install Python 3.9+ from https://www.python.org/downloads/"
    exit 1
fi

echo "[OK] Python detected: $($PYTHON_CMD --version)"
echo ""

# 2. Check / Install dependencies
echo "[*] Checking dependencies..."
$PYTHON_CMD -m pip install -r requirements.txt --quiet --disable-pip-version-check

echo "[OK] Dependencies ready."
echo ""
echo "========================================================"
echo "  Launching server on http://localhost:8000"
echo "  Press Ctrl+C to stop the server."
echo "========================================================"
echo ""

# 3. Auto-open browser
if command -v xdg-open &>/dev/null; then
    (sleep 2 && xdg-open http://localhost:8000) &
elif command -v open &>/dev/null; then
    (sleep 2 && open http://localhost:8000) &
fi

# 4. Start Server
$PYTHON_CMD run.py
