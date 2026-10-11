#!/usr/bin/env bash
# Script per iniciar fàcilment l'aplicació ETF & Portfolio Backtester

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

if [ ! -d "venv" ]; then
    echo "⚙️ Creant entorn virtual de Python..."
    python3 -m venv venv
    ./venv/bin/pip install -r requirements.txt
fi

echo "🚀 Iniciant l'aplicació ETF Portfolio Tracker..."
./venv/bin/streamlit run app.py
