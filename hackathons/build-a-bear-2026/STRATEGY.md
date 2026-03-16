# Coldstar x Build-A-Bear — Strategy Notes

## Implementation Repo
**$VS/projects/coldstar-bear-hackathon/** — full codebase, 2,690 lines, 24 tests passing

## Strategy: Coldstar Aegis — Bidirectional Delta-Neutral Funding Harvester

### How It Works
- **Positive funding** (longs pay shorts): Long jitoSOL + short SOL-PERP → earn funding + LST staking + basis
- **Negative funding** (shorts pay longs): Hold USDC + long SOL-PERP → earn funding + USDC lending
- Strategy flips direction automatically based on funding rate regime
- All transactions signed via Coldstar air-gapped signer

### Backtest Results (90-day, $100K TVL)
- **55% annualized APY** (10% min required)
- **0.09% max drawdown** (5% limit)
- **15.94 Sharpe ratio**
- 56% time positive mode, 14% negative, 30% idle

## Progress

- [x] Define vault strategy — Bidirectional delta-neutral funding harvester
- [x] Implement strategy logic (strategy.ts, 484 lines)
- [x] Implement rebalancer (rebalancer.ts, 597 lines)
- [x] Drift + Pyth + Jupiter integration (drift-client.ts, 523 lines)
- [x] Ranger Earn vault adaptor (vault-adaptor.ts, 220 lines)
- [x] Coldstar signing interface (coldstar-signer.ts, 302 lines)
- [x] Backtest engine (backtest.ts, 390 lines)
- [x] Live monitor dashboard (monitor.ts, 174 lines)
- [x] Vault deployment script (deploy-vault.ts)
- [x] Unit tests (24/24 passing)
- [x] Write strategy documentation
- [ ] Deploy vault on Ranger Earn
- [ ] Run live during build window (Mar 9 – Apr 6)
- [ ] Record 3-min demo video
- [ ] Submit via Superteam Earn by Apr 6

## Key Constraints
- Base asset: USDC
- Min APY: 10%
- 3-month rolling lock
- No LP vaults, no circular yield stables, no junior tranches, no high-leverage looping
