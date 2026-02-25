#!/bin/bash
# Coldstar — Air-gapped Solana cold wallet installer
set -e

MIN_PYTHON="3.10"
VENV_DIR=".venv"

# --- Check Python version ---
PYTHON=""
for cmd in python3 python; do
    if command -v "$cmd" &>/dev/null; then
        ver=$("$cmd" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null)
        if [ "$(printf '%s\n' "$MIN_PYTHON" "$ver" | sort -V | head -n1)" = "$MIN_PYTHON" ]; then
            PYTHON="$cmd"; break
        fi
    fi
done
if [ -z "$PYTHON" ]; then
    echo "Error: Python $MIN_PYTHON+ is required but not found." >&2; exit 1
fi
echo "Using $PYTHON ($($PYTHON --version))"

# --- Create venv and install deps ---
echo "Creating virtual environment in $VENV_DIR..."
$PYTHON -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"
pip install --upgrade pip -q
pip install -r local_requirements.txt -q
echo "Python dependencies installed."

# --- Build Rust signer (optional) ---
if command -v cargo &>/dev/null && [ -d "secure_signer" ]; then
    echo "Building Rust secure signer..."
    (cd secure_signer && cargo build --release)
    echo "Rust signer built."
else
    echo "Skipping Rust signer (cargo not found or secure_signer/ missing)."
fi

# --- Done ---
echo ""
echo "Coldstar installed successfully."
echo ""
echo "  Activate:  source $VENV_DIR/bin/activate"
echo "  Run:       python main.py"
echo "  Docs:      https://coldstar.dev"
