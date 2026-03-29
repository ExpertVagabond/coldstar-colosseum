# :diamond_shape_with_a_dot_inside: Coldstar -- Air-Gapped Solana Vault

[![Colosseum #62](https://img.shields.io/badge/Colosseum-Project_%2362-8B5CF6?style=flat)](https://colosseum.com/agent-hackathon/projects/coldstar-air-gapped-solana-vault-2z9v3x)
[![Solana](https://img.shields.io/badge/Solana-14F195?logo=solana&logoColor=white)](https://solana.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub stars](https://img.shields.io/github/stars/ExpertVagabond/coldstar-colosseum)](https://github.com/ExpertVagabond/coldstar-colosseum/stargazers)
[![Whitepaper](https://img.shields.io/badge/Whitepaper-Hugging_Face-orange)](https://huggingface.co/purplesquirrelnetworks/coldstar-whitepaper)

**Programmable cold-signing infrastructure for Solana.** Any USB drive becomes an air-gapped cold wallet. Air-gapped signing, FairScore reputation gating, Jupiter DEX integration, and native RWA support — built for DAOs, traders, and developers who need hardware-grade security without a $200 device. By ChainLabs Technologies.

## Traction

- **107 wallets created**, 37 actively signing (35% retention)
- Partnerships: Superteam IE, Superteam UK, DeAura, Bonk Advisory, Jito
- Revenue: 1% transaction fee (capped at $10) + Jito staking tips + native RWA swaps

## The Problem

Hardware wallets cost $50–$300, suffer data breaches, and aren't programmable. This blocks DAOs, traders, and developers from using cold security in practice.

## The Solution

Air-gapped cold wallet + reputation-gated transactions + DeFi integration. Private keys never touch the network. Every outbound transfer is scored by FairScore before execution.

```
Create transaction online --> Sign on air-gapped USB --> Broadcast
                             Private keys NEVER touch the network
```

## Install

```bash
git clone https://github.com/ExpertVagabond/coldstar-colosseum
cd coldstar-colosseum
pip install -r local_requirements.txt
python main.py
```

### MCP Server (for AI agents)

```bash
npx coldstar-mcp
```

```json
{
  "mcpServers": {
    "coldstar": {
      "command": "npx",
      "args": ["-y", "coldstar-mcp"],
      "env": { "SOLANA_RPC_URL": "https://api.mainnet-beta.solana.com" }
    }
  }
}
```

**8 MCP tools**: `check_reputation`, `get_token_price`, `get_swap_quote`, `check_wallet_balance`, `validate_transaction`, `list_supported_tokens`, `get_portfolio`, `estimate_swap_cost`

## FairScore Reputation Gating

Every outbound transfer is gated by [FairScale's FairScore API](https://fairscale.xyz):

| Tier | Score | Action | Limit |
|------|-------|--------|-------|
| Bronze | 0-19 | **BLOCKED** | -- |
| Silver | 20-39 | Warning | 10 SOL |
| Gold | 40-59 | Proceed | 100 SOL |
| Platinum | 60-79 | Proceed | 500 SOL |
| Diamond | 80-100 | Proceed | Unlimited |

## Features

- **Air-Gap Security** -- Alpine Linux with network drivers blacklisted, QR code signing
- **DeFi Integration** -- Jupiter DEX routes, Pyth price feeds, SPL token support
- **Reputation Gating** -- FairScore blocks low-reputation recipients at infrastructure level
- **DAO Governance** -- Multi-sig vaults, on-chain voting, air-gapped approval
- **Beautiful TUI** -- Rich terminal UI with portfolio dashboard and USB flashing tool
- **Agent-Friendly** -- MCP server with 8 tools for autonomous wallet operations

## Architecture

```
ONLINE DEVICE                         OFFLINE DEVICE (Air-Gapped)
+--------------------------+          +---------------------------+
| Coldstar CLI             |   QR /   | USB Cold Wallet           |
| - Check balance (RPC)   |   USB    | - Private key storage     |
| - Get prices (Pyth)     | <------> | - Transaction signing     |
| - Create unsigned txs   |          | - ZERO network access     |
| - Query Jupiter routes  |          | - Alpine Linux (<50MB)    |
+--------------------------+          +---------------------------+
```

## Comparison

| Feature | Coldstar | Hardware Wallet | Hot Wallet |
|---------|----------|-----------------|------------|
| Air-Gap | Yes | Yes | No |
| Cost | $10 | $79-279 | Free |
| Open Source | Yes | No | Varies |
| DeFi / Jupiter | Yes | Limited | Yes |
| Reputation Gating | Yes | No | No |
| Agent-Friendly | Yes | No | Risky |
| DAO Governance | Yes | No | No |

## Tech Stack

| Layer | Technology |
|-------|-----------|
| OS | Alpine Linux (<50MB) |
| Language | Python 3.11+ |
| UI | Rich (terminal) |
| Blockchain | Solders (Solana Rust SDK) |
| DEX | Jupiter Aggregator |
| Oracles | Pyth Network |
| Reputation | FairScale FairScore API |
| DAO | Anchor Programs (devnet) |

## Deployed Infrastructure

- **Coldstar DAO**: [`Ue6Z2MBm...DJYXeat`](https://explorer.solana.com/address/Ue6Z2MBm7DxR5QTAYRRNsdXc7KBRgASQabA7DJYXeat?cluster=devnet)
- **Voter Stake Registry**: [`2ueu2H3t...47ViZx`](https://explorer.solana.com/address/2ueu2H3tN8U3SWNsQPogd3dWhjnNBXH5AqiZ1H47ViZx?cluster=devnet)

## Related Projects

- [solana-mcp-server-app](https://github.com/ExpertVagabond/solana-mcp-server-app) -- Solana wallet + DeFi MCP
- [solmail-mcp](https://github.com/ExpertVagabond/solmail-mcp) -- Physical mail via Solana payments
- [ordinals-mcp](https://github.com/ExpertVagabond/ordinals-mcp) -- Bitcoin Ordinals MCP server
- [cpanel-mcp](https://github.com/ExpertVagabond/cpanel-mcp) -- cPanel hosting MCP server

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes
4. Open a Pull Request

**Security Issues**: [Private advisory](https://github.com/ExpertVagabond/coldstar-colosseum/security/advisories/new)

## Links

- [Hackathon Project](https://colosseum.com/agent-hackathon/projects/coldstar-air-gapped-solana-vault-2z9v3x) | [Whitepaper](https://huggingface.co/purplesquirrelnetworks/coldstar-whitepaper) | [X: @buildcoldstar](https://x.com/buildcoldstar)

## License

MIT -- [ChainLabs Technologies](https://github.com/devsyrem)
