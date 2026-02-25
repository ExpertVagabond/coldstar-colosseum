# Coldstar — Air-gapped Solana cold wallet
# Usage: make [target]

VENV     := .venv
PYTHON   := $(VENV)/bin/python
PIP      := $(VENV)/bin/pip
SIGNER   := secure_signer

.PHONY: install build-signer run test clean lint help

## ── Python ──────────────────────────────────────────

install: $(VENV)/bin/activate  ## Install Python deps in venv
$(VENV)/bin/activate:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip -q
	$(PIP) install -r local_requirements.txt -q
	@echo "Installed. Activate: source $(VENV)/bin/activate"

run: install  ## Run Coldstar CLI
	$(PYTHON) main.py

test: install  ## Run tests
	$(PYTHON) -m pytest test_*.py -v 2>/dev/null || $(PYTHON) test_transaction.py

lint: install  ## Check Python style
	$(PYTHON) -m py_compile main.py config.py
	@echo "Syntax OK"

## ── Rust signer ─────────────────────────────────────

build-signer:  ## Build Rust secure signer (release)
	cd $(SIGNER) && cargo build --release
	@echo "Built: $(SIGNER)/target/release/libsolana_secure_signer.*"

test-signer:  ## Run Rust tests
	cd $(SIGNER) && cargo test

lint-signer:  ## Clippy + format check
	cd $(SIGNER) && cargo clippy -- -D warnings
	cd $(SIGNER) && cargo fmt -- --check

## ── Housekeeping ────────────────────────────────────

clean:  ## Remove build artifacts
	rm -rf $(VENV) __pycache__ src/__pycache__ *.pyc
	cd $(SIGNER) && cargo clean 2>/dev/null || true

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*##' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*##"}; {printf "  %-16s %s\n", $$1, $$2}'
