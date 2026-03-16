# Build-A-Bear Hackathon | Main Track

**Organizer:** Ranger (Presto Labs)
**Type:** 4-week online hackathon — vault strategies on Solana
**Window:** Mar 9 – Apr 6, 2026
**Submissions Deadline:** Apr 6, 23:59 UTC
**Results:** Apr 14

## What We're Building

Production-ready vault strategy deployed on Ranger Earn. Options:
- Basis trades
- Delta-neutral
- RWA
- AI-driven
- Anything novel

**Coldstar angle:** Air-gapped signing + vault strategy = secure automated yield without hot wallet risk.

## Prize Pool

### Main Track
| Place | Prize |
|-------|-------|
| 1st | Up to $500,000 vault seeding |
| 2nd | Up to $300,000 vault seeding |
| 3rd | Up to $200,000 vault seeding |

### Drift Side Track (separate submission)
| Place | Prize |
|-------|-------|
| 1st | $100,000 vault seeding |
| 2nd | $60,000 vault seeding |
| 3rd | $40,000 vault seeding |

### Sponsor Prizes (Main Track Top 3)
- $15,000 audit credits — Adevar Labs
- 3 months free MPC wallet infra — Cobo
- $10,000 AWS Credits (9 total: 3 Main, 3 Drift, 3 Honorable)

### All Participants
- 1 month free Helius Dev Plan
- Free Cobo Web3 wallet testing accounts

## Eligibility Requirements

- **Minimum APY:** 10%
- **Vault Base Asset:** USDC
- **Tenor:** 3-month lock, rolling (reassessed quarterly)

### Disqualifying Yield Sources
- Ponzi-like yield-bearing stables (circular dependencies → death spirals)
- Junior tranche / insurance pool designs (e.g. RLP, jrUSDe — principal loss risk)
- DEX LP vaults (e.g. JLP, HLP, LLP — impermanent loss risk)
- High-leverage looping (health rate < 1.05 on non-hardcoded oracle assets)

## Submission Requirements (all via Earn page)

1. **Demo/Pitch Video** (max 3 min) — strategy, edge, how it runs on Ranger Earn
2. **Strategy Documentation** — thesis, mechanics, risk management (drawdown, sizing, rebalancing)
3. **Code Repository** — open-source preferred; if private, add @jakeyvee on GitHub
4. **On-chain Verification** — wallet/vault address used during build window (verified via Solscan)
5. **CEX Strategy Verification** (if applicable) — trade history CSV + read-only API key

Live performance preferred, backtested results accepted.

## Judging Criteria

1. **Strategy Quality & Edge** — genuine alpha, differentiated approach
2. **Risk Management** — drawdown limits, liquidation protection, position sizing, rebalancing
3. **Technical Implementation** — code quality, adaptor integration, vault architecture, security
4. **Production Viability** — realistic deployment, scalability, operational complexity
5. **Novelty & Innovation** — new primitives, creative protocol combos, ecosystem contribution

## Timeline

| Date | Event |
|------|-------|
| Mar 9 | Kickoff |
| Mar 9 – Apr 6 | Build Window |
| Mar 11 | Workshop 1: Launch & Operate Your Ranger Vault |
| Mar 13 | Workshop 2: Compose with Ranger Vaults via CPI / Custom Adaptors |
| Mar 16 | Workshop 3: Drift Perps and Vaults |
| Mar 17 | Workshop 4: Cobo MPC Wallet Infra (TBC — check TG) |
| Apr 6 23:59 UTC | Submissions Deadline |
| Apr 7–11 | Judging |
| Apr 14 | Results |

## Workshop Links

- **Workshop 1** (Mar 11, 3-4pm UTC): zoom.us/j/81469827696 — Passcode: 566337
- **Workshop 2** (Mar 13, 3-4pm UTC): zoom.us/j/87277759766 — Passcode: 501493
- **Workshop 3** (Mar 16, 3-4pm UTC): zoom.us/j/89451647662 — Passcode: 209390
- **Workshop 4** (Mar 17, TBC): Check Telegram

## Resources

- Ranger Earn Docs
- Ranger Hackathon Telegram
- Drift Docs
- Cobo Docs
