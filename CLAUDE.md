# Coldstar — Air-gapped cold wallet for Solana and Base

## Stack
- **Python 3.10+** — CLI, TUI (Textual/Rich), wallet logic, QR signing
- **Rust (2021)** — `secure_signer/` crate for memory-locked Ed25519 + secp256k1 signing
- **Key deps:** solana, solders, pynacl, web3, eth-account, textual, questionary, qrcode, httpx
- **Rust deps:** ed25519-dalek, k256, zeroize, memsec, aes-gcm, argon2

## Key Commands
```bash
make install          # Create venv + install Python deps
make run              # Run Coldstar CLI (main.py)
make test             # Run Python tests (pytest or test_transaction.py)
make lint             # Syntax check main.py + config.py
make build-signer     # Build Rust secure signer (release)
make test-signer      # Run Rust tests
make lint-signer      # Clippy + fmt check
make clean            # Remove .venv + cargo artifacts
```

## Project Structure
```
coldstar.py / main.py    — CLI entry points
coldstar_tui.py          — Textual TUI interface
config.py                — Runtime configuration
src/
  wallet.py              — Solana wallet management
  transaction.py         — Solana transaction building
  evm_wallet.py          — Base/EVM wallet
  evm_transaction.py     — EVM transaction building
  fairscore_integration.py — Reputation-gated transfers
  jupiter_integration.py — Jupiter DEX integration
  qr_transfer.py         — QR code air-gap transfer
  usb.py                 — USB drive flash/mount
  ui.py                  — Rich UI helpers
  zk/                    — Zero-knowledge proof modules
secure_signer/           — Rust crate (cdylib + staticlib)
  src/                   — Ed25519/secp256k1 signing, AES-256-GCM encryption
tests/                   — Policy, roundtrip, ZK, and transaction tests
mcp-server/              — MCP server for Claude Code integration
companion-app/           — Mobile companion app
grants/                  — Grant applications
```

## Environment
- No env vars required for basic operation (keys stay on USB)
- Solana RPC URL can be configured; defaults to mainnet-beta
- Venv: `.venv/` (auto-created by `make install`)

## Architecture
- Air-gapped: create transactions online, sign on offline USB, broadcast
- FairScore reputation gating blocks low-reputation recipients
- Rust signer provides memory-locked key handling via FFI (cdylib)
- Multi-chain: Solana (Ed25519) + Base/EVM (secp256k1)

## Repo Layout
- 4 related repos: coldstar-colosseum, coldstar-companion, coldstar-mcp, coldstar-site
- Homepage: https://coldstar.dev
- Bundle ID: app.replit.northcatch (companion app shares NorthCatch infra)
