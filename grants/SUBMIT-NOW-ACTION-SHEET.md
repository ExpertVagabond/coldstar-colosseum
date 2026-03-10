# SUBMIT NOW — Action Sheet (March 9, 2026)

Do these in order. Each section has exact copy-paste text.

---

## STEP 1: Superteam Talent Profile (5 min)

**URL:** https://talent.superteam.fun/join

### Fields — copy-paste ready:

**Name:** Matthew Karsten

**Email:** MatthewKarstenConnects@gmail.com

**Twitter/X:** https://x.com/expertvagabond

**GitHub:** https://github.com/ExpertVagabond

**Website/Portfolio:** https://coldstar.dev

**Location:** United States

**Bio / About:**
```
Full-stack Solana infrastructure builder. Founder of Purple Squirrel Media. Shipping production security tooling, MCP servers, DAO governance, and AI agent frameworks across TypeScript, Python, Rust, and Go.

Key proof of work:
- Coldstar: Air-gapped cold wallet with FairScore reputation gating (Colosseum #62, passed)
- SolMail: Physical mail via SOL payments (Colosseum #47, passed)
- 15 deployed Solana programs (Anchor), 14 MCP servers (200+ tools)
- PSM Neural Core: Pure Rust ML stack (9 crates, 76 tests, zero unsafe)
- 4 Graveyard Hackathon submissions (Tribeca DAO, Port Finance, Grape, Parrot TWAP)
- 1,800+ commits, 320+ repos, 6,800+ Claude Code sessions
```

**Skills:** Rust, TypeScript, Python, Solana, Anchor, React Native, MCP Protocol, DeFi, DAO Governance, Security, AI Agents, CLI Tools

**What are you looking for?** Bounties, grants, and ecosystem roles — security infrastructure, AI agent tooling, developer SDKs, DeFi protocol work

**Availability:** Open to full-time, contract, bounties, and grants

---

## STEP 2: Solana Foundation USA Grant (10 min)

**URL:** https://superteam.fun/earn/grants/solana-foundation-usa-grants

### Fields — copy-paste ready:

**Project Name:** Coldstar — Open-Source Air-Gapped Cold Wallet for Solana

**Project URL:** https://coldstar.dev

**GitHub:** https://github.com/ExpertVagabond/coldstar-colosseum

**Grant Amount Requested:** $7,500

**One-line description:**
```
Open-source security infrastructure that replaces proprietary hardware wallets with disposable USB drives and RAM-only Rust signing — 95% cheaper, fully auditable, zero vendor lock-in.
```

**Project description / What are you building?**
```
Coldstar transforms any $10 USB drive into hardware-wallet-grade security for Solana. Private keys live on an air-gapped Alpine Linux system with network drivers blacklisted at the kernel level. The Rust secure signer holds plaintext in memory-locked buffers for ~100 microseconds, then auto-zeroizes.

Full DeFi from cold storage: Jupiter V6 swaps, Pyth price feeds, ZK proof transaction layer (Schnorr ownership, Pedersen range proofs, policy compliance — Ristretto255, no trusted setup), DAO governance with veToken model, SPL token management. Transactions cross the air gap via QR codes — no USB data, no Bluetooth, no wireless.

This is the only cold wallet on any chain with zero-knowledge proof signing. ZK proofs run at the air-gap boundary — the point of no return before offline signing. 108 tests across the ZK layer (47 Rust + 61 Python).

Live and running: coldstar.dev, npm published MCP server (coldstar-mcp@0.2.0, 13 tools), DAO programs on devnet, Colosseum Agent Hackathon Project #62 (passed Feb 12, 2026).
```

**How does this advance Solana? / Why should the Foundation fund this?**
```
Decentralization: Eliminates dependency on hardware wallet vendors for Solana self-custody. Any USB drive works.

Developer tooling: CLI-first, scriptable, automation-native. Integrates into CI/CD, DAO ops, and agent frameworks.

Censorship resistance: No vendor can brick your wallet with a firmware update. Air-gapped OS runs entirely from RAM.

Agent economy infrastructure: MCP server (npm: coldstar-mcp) gives AI agents secure Solana capabilities with reputation gates. Agents analyze and prepare transactions, but large amounts require human air-gap signing.

This is built and running, not a pitch deck. $7,500 for concrete deliverables in 6 weeks, all open source.
```

**What will the grant fund? / Milestones:**
```
Milestone 1 ($2,500, 2 weeks): Security hardening — formal threat model, cargo-fuzz fuzzing suite, dependency audit, SBOM generation

Milestone 2 ($2,500, 2 weeks): Cross-platform builds — CI/CD for Linux/macOS/Windows binaries, automated ISO builder, Homebrew formula

Milestone 3 ($1,500, 1 week): Developer documentation — integration guide, API docs, DAO treasury setup tutorial, MCP server usage guide

Milestone 4 ($1,000, 1 week): Community + mainnet prep — bug bounty program, community testing, mainnet deployment preparation

Total: 6 weeks from grant approval. All milestones independently verifiable via GitHub.
```

**Proof of work / Team:**
```
Team:
- </Syrem> (devsyrem) — Founder & Lead Dev. Cybersecurity + Aerospace Engineering. Built the Rust signer, Python CLI, DAO programs. GitHub: devsyrem
- Matthew Karsten — Infrastructure & Strategy. Purple Squirrel Media. Website, MCP server, grants, ecosystem integration. GitHub: ExpertVagabond

Proof of work:
- Colosseum Agent Hackathon: Project #62, passed (Feb 12, 2026)
- 4 Graveyard Hackathon submissions (revived abandoned Solana protocols)
- Rust signer: ~49K lines, memory-locked, auto-zeroizing
- ZK transaction layer: Schnorr NIZK, Pedersen range proofs, 108 tests, Ristretto255
- npm: coldstar-mcp@0.2.0 (13 tools)
- DAO programs deployed on Solana devnet
- 35+ commits, 5 forks, 4 contributors
```

**Contact:** MatthewKarstenConnects@gmail.com

**Twitter:** https://x.com/buildcoldstar

**Telegram:** @buildcoldstar

---

## STEP 3: Telegram Message to @tokenton26 (2 min)

**Open Telegram → search @tokenton26 → send:**

```
Hey! I'm interested in the TokenTon26 AI Track ($8,500 bounty).

Quick question on the token launch requirement: I have existing Solana tokens already live (including $PAW which graduated from pump.fun bonding curve). Do these qualify, or does the submission specifically require a new token launch on the DeAura platform?

Also clarifying: is the $200K minimum trading volume measured from the token's lifetime or within the hackathon build phase specifically?

I'm building AI agent infrastructure for Solana — 10-agent swarm, pure Rust ML core, 14 MCP servers with 200+ tools, air-gapped signing with neural anomaly detection. Would love to submit if the token requirements work.

Thanks!
— Matthew (@buildcoldstar / @expertvagabond)
```

---

## STEP 4: Re-auth MCP Servers (2 min)

1. Open https://claude.ai in browser
2. Settings → Integrations (or Connectors)
3. Find **Gmail** → Re-authorize → complete Google OAuth
4. Find **Google Calendar** → Re-authorize → complete Google OAuth
5. Restart Claude Code — both servers should connect

---

## Done! Total time: ~20 minutes.

### What happens next:
- **Solana Foundation grant:** Decision in ~7 days via email
- **TokenTon26:** Depends on @tokenton26's response about token requirement
- **Superteam Talent:** They review and may schedule a 15-min chat
- **MCP Servers:** Should reconnect immediately after re-auth
