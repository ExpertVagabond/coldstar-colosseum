# Privacy Policy

**Coldstar — Air-Gapped Solana Cold Wallet**
Last updated: February 15, 2026
Operated by: Purple Squirrel Media LLC

---

## Overview

Coldstar is open-source, self-custody wallet software that runs entirely on your local device. We do not operate servers, collect user data, or require account creation. Your private keys are generated and stored locally — they never leave your device.

This policy explains what data flows occur when you use Coldstar and what third-party services are contacted.

---

## What We Do NOT Collect

- **Private keys** — Generated and encrypted locally. Never transmitted.
- **Passwords** — Used only in local memory for decryption. Never stored in plaintext, never transmitted.
- **Personal information** — No names, emails, phone numbers, or identifiers.
- **Analytics or telemetry** — Coldstar does not phone home. No usage tracking, no crash reporting.
- **IP addresses** — We do not operate servers that could log your IP.

---

## Data That Leaves Your Device

When you use Coldstar's online features (on the online device, not the air-gapped USB), the following network requests are made:

### Solana RPC

- **What:** Your wallet's public address is sent to a Solana RPC endpoint to check balances, fetch blockhashes, and broadcast signed transactions.
- **Default endpoint:** `https://api.devnet.solana.com` (Solana Foundation)
- **Data sent:** Public wallet address, signed transactions.
- **Your control:** You can configure a custom RPC URL.

### FairScore Reputation Check (FairScale API)

- **What:** Before transactions cross the air gap, Coldstar queries the FairScale API to check the recipient wallet's reputation score.
- **Endpoint:** `https://api2.fairscale.xyz`
- **Data sent:** Recipient's public wallet address.
- **Your control:** FairScore checks occur only when you initiate a transaction. No background polling.
- **Third-party policy:** [FairScale](https://fairscale.xyz)

### Jupiter DEX (Token Swaps)

- **What:** When you use the swap feature, Coldstar queries Jupiter's aggregator for price quotes and swap routes.
- **Endpoint:** Jupiter Aggregator V6 API
- **Data sent:** Token mint addresses, amounts, your public wallet address.
- **Your control:** Only triggered when you explicitly request a swap.
- **Third-party policy:** [Jupiter](https://jup.ag)

### Pyth Network (Price Feeds)

- **What:** Coldstar fetches real-time token prices from Pyth's Hermes API for display in the portfolio dashboard.
- **Endpoint:** `https://hermes.pyth.network`
- **Data sent:** Token price feed IDs (not your wallet address).
- **Your control:** Only triggered when you view the dashboard or initiate a swap.
- **Third-party policy:** [Pyth Network](https://pyth.network)

### Infrastructure Fee

- **What:** A 1% infrastructure fee is included in transactions, sent to the Coldstar project wallet.
- **Address:** `Cak1aAwxM2jTdu7AtdaHbqAc3Dfafts7KdsHNrtXN5rT`
- **Transparency:** This is visible in the transaction before you sign it. You can inspect the transaction data before approving.

---

## Air-Gapped Device

The air-gapped USB device running Coldstar's offline signer:

- **Has no network access.** Alpine Linux with network interfaces blacklisted.
- **Makes zero network requests.** All data transfer happens via QR codes or USB file transfer.
- **Stores only:** Your encrypted keypair, unsigned/signed transaction files.

---

## Blockchain Transparency

Solana is a public blockchain. Once a transaction is broadcast:

- Your wallet address, transaction amounts, and recipient addresses are **permanently public** on the Solana ledger.
- Anyone can view your transaction history using a block explorer.
- This is inherent to all public blockchains and is not something Coldstar can change.

---

## Local Data Storage

Coldstar stores the following on your USB drive and/or local filesystem:

| Data | Location | Encrypted |
|------|----------|-----------|
| Wallet keypair | USB `/wallet/keypair.json` | Yes (Rust AES-256 + Argon2) |
| Public key | USB `/wallet/pubkey.txt` | No (public by nature) |
| Unsigned transactions | USB `/inbox/` | No |
| Signed transactions | USB `/outbox/` | No |
| Backups | USB `/backups/` | Optional (user choice) |
| Configuration | Local `config.py` | No |

---

## Open Source

Coldstar is MIT-licensed open-source software. You can audit every line of code:

- **Repository:** [github.com/ExpertVagabond/coldstar-colosseum](https://github.com/ExpertVagabond/coldstar-colosseum)
- **Rust signer source:** `secure_signer/src/`
- **All network calls:** `src/network.py`, `src/fairscore_integration.py`, `src/jupiter_integration.py`, `src/pyth_integration.py`

---

## Children

Coldstar is not directed at children under 13. We do not knowingly collect data from minors (we do not collect data from anyone).

---

## Changes

This policy may be updated as Coldstar evolves. Changes will be committed to the repository with full git history. The "Last updated" date at the top reflects the most recent revision.

---

## Contact

For privacy questions, open an issue on [GitHub](https://github.com/ExpertVagabond/coldstar-colosseum/issues) or reach us at [@buildcoldstar](https://x.com/buildcoldstar).
