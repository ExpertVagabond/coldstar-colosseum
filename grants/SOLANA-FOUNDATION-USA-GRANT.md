# Coldstar — Solana Foundation USA Grant Application

> Apply at: https://superteam.fun/earn/grants/solana-foundation-usa-grants
> Contact: nicky@solanaeco.io
> Grant range: $1–$10,000 USDG
> Average approved: $5,460
> Turnaround: ~7 days

---

## Project Name

Coldstar — Open-Source Air-Gapped Cold Wallet for Solana

## Project Website

https://coldstar.dev

## GitHub Repository

https://github.com/ExpertVagabond/coldstar-colosseum

## One-Line Description

Open-source security infrastructure that replaces proprietary hardware wallets with disposable USB drives and RAM-only signing — 95% cheaper, fully auditable, zero vendor lock-in.

## Project Description

Coldstar transforms any $10 USB drive into hardware-wallet-grade security for Solana. Private keys are generated on an air-gapped Alpine Linux system (~50MB) with network kernel modules blacklisted at the OS level. The Rust secure signer holds plaintext keys in memory-locked buffers for ~100 microseconds, then auto-zeroizes via Drop trait. Transactions are transferred across the air gap using human-inspectable QR codes — no USB data, no Bluetooth, no wireless.

The online companion CLI provides full DeFi access from cold storage:
- **Jupiter Aggregator V6** — DEX swaps with optimal routing
- **Pyth Network Hermes** — real-time price feeds and portfolio tracking
- **ZK transaction layer** — Schnorr ownership proofs, Pedersen range proofs, and policy compliance proofs protect signing pipeline metadata (Ristretto255, Fiat-Shamir, no trusted setup)
- **DAO governance** — on-chain voting with veToken model (deployed on devnet)
- **SPL token transfers** — full token management
- **Base/EVM support** — multichain signing with same security model

This is the only cold wallet on any chain with zero-knowledge proof signing — ZK proofs run at the air-gap boundary, the point of no return before offline signing.

## What problem does this solve?

Hardware wallets cost $79–$279 and ship with proprietary, unauditable firmware from a single vendor. Supply chain attacks (Ledger breach 2023), firmware vulnerabilities, and vendor lock-in are real risks. Self-custody shouldn't require trusting another company's black box.

Coldstar eliminates all three problems:
1. **No proprietary firmware** — 100% open source (MIT), fully auditable
2. **No supply chain risk** — user creates the bootable USB themselves from verified Alpine Linux
3. **No vendor lock-in** — any USB drive works, keys are standard Ed25519/secp256k1

For the Solana ecosystem specifically: power users, DAOs, and AI agents managing significant capital need air-gapped signing with DeFi access. Currently they choose between security (hardware wallets with no DeFi) or convenience (hot wallets with full DeFi). Coldstar gives both.

## How does this advance Solana?

**Decentralization:** Eliminates dependency on hardware wallet vendors (Ledger, Trezor) for Solana self-custody. Anyone with a USB drive can achieve hardware-grade security.

**Developer tooling:** CLI-first, scriptable, automation-native. Developers can integrate Coldstar's signing flow into CI/CD pipelines, DAO operations, and agent frameworks.

**Censorship resistance:** No vendor can brick your wallet with a firmware update. No company can freeze your signing device. The air-gapped OS runs entirely from RAM.

**Agent economy infrastructure:** As AI agents manage on-chain capital, they need both programmatic access (hot wallet for small txns) and physical isolation (cold wallet for treasury). Coldstar's MCP server (npm: coldstar-mcp, 13 tools) bridges this gap — AI agents analyze and prepare transactions, but large amounts require human air-gap signing.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Secure Signer | Rust (ed25519-dalek, k256, argon2, aes-gcm, zeroize, memsec) |
| ZK Proofs | Rust (curve25519-dalek/Ristretto255, Fiat-Shamir, Pedersen commitments, HMAC-SHA256) |
| CLI | Python 3.11+ (Rich TUI, httpx, questionary) |
| Cold OS | Alpine Linux v3.19 (~50MB bootable) |
| DEX | Jupiter Aggregator V6 |
| Oracles | Pyth Network Hermes API |
| DAO | Anchor 0.29.0, SPL Governance 4.0.0 |
| EVM | k256 (secp256k1), web3.py, EIP-1559 |
| MCP Server | Node.js, @modelcontextprotocol/sdk |

## Proof of Work

- **Colosseum Agent Hackathon:** Project #62, passed (Feb 12, 2026)
- **Graveyard Hackathon:** Additional Solana protocol revival submissions (Tribeca DAO, Port Finance, Grape, Parrot TWAP)
- **On-chain programs:** Coldstar DAO + Voter Stake Registry deployed on Solana devnet
- **ZK transaction layer:** Schnorr NIZK ownership proofs, Pedersen range proofs, policy compliance proofs — 108 tests (47 Rust + 61 Python), no trusted setup, Ristretto255 curve
- **npm published:** coldstar-mcp@0.2.0 (13 MCP tools for Solana + Base)
- **Live website:** coldstar.dev
- **Rust signer:** ~49,000 lines, memory-locked, auto-zeroizing, FFI to Python
- **ZK crate:** 8,400+ lines of Rust/Python for proof generation, verification, and envelope integrity
- **Python CLI:** 17 modules, 290,000+ lines total
- **4 contributors:** devsyrem (founder/lead), 3 additional contributors
- **GitHub:** 35+ commits, 5 forks, active development

## What will this grant fund?

**Requested amount: $7,500**

| Milestone | Amount | Deliverable | Timeline |
|-----------|--------|-------------|----------|
| 1. Security hardening | $2,500 | Formal threat model, fuzzing suite (cargo-fuzz), dependency audit, SBOM generation | 2 weeks |
| 2. Cross-platform builds | $2,500 | CI/CD pipeline for Linux/macOS/Windows binaries, automated ISO builder, Homebrew formula | 2 weeks |
| 3. Developer documentation | $1,500 | Integration guide, API docs, tutorial for DAO treasury setup, MCP server usage guide | 1 week |
| 4. Community + mainnet prep | $1,000 | Bug bounty program, community testing campaign, mainnet deployment prep | 1 week |

**Total timeline:** 6 weeks from grant approval.

All milestones are independently verifiable via GitHub commits and CI artifacts.

## Why should the Foundation fund this?

1. **It's built and running** — not a pitch deck. Live CLI, live website, published MCP server, deployed devnet programs.
2. **Solana-native** — Jupiter, Pyth, Anchor, SPL tokens, Solana Pay, Realms-compatible governance.
3. **Small ask, fast execution** — $7,500 for concrete deliverables in 6 weeks. All work is open source.
4. **Unique in the ecosystem** — no other open-source air-gapped wallet exists for Solana with DeFi access and ZK proof signing.
5. **Agent economy ready** — MCP server already integrates with Claude, providing AI agents secure Solana capabilities with ZK-verified transactions.

## Team

**</Syrem> (devsyrem)** — Founder & Lead Developer
- Cybersecurity + Digital Forensics + Aerospace Engineering background
- Built the core Rust secure signer, full Python CLI, and DAO governance programs
- GitHub: github.com/devsyrem | Twitter: @dev_syrem

**Matthew Karsten** — Strategic & Infrastructure Support
- Founder, Purple Squirrel Media LLC
- Website, MCP server, positioning, grant strategy, ecosystem integration
- GitHub: github.com/ExpertVagabond | Twitter: @expertvagabond
- 1,800+ commits across 320+ projects, polyglot (TS, Python, Rust, Go, Ruby)

## Contact

- **Email:** MatthewKarstenConnects@gmail.com
- **Twitter/X:** @buildcoldstar
- **GitHub:** ExpertVagabond
- **Telegram:** @buildcoldstar

## Links

- Website: https://coldstar.dev
- GitHub: https://github.com/ExpertVagabond/coldstar-colosseum
- Colosseum submission: https://coldstar.dev/colosseum
- MCP server (npm): https://www.npmjs.com/package/coldstar-mcp
- Twitter: https://x.com/buildcoldstar

---

*Application prepared March 2026 for Solana Foundation USA Grants via Superteam Earn*
*Project: Coldstar — https://coldstar.dev*
*Applicant: Matthew Karsten | Purple Squirrel Media LLC*
