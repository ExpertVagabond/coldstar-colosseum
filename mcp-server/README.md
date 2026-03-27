# coldstar-mcp

[![npm version](https://img.shields.io/npm/v/coldstar-mcp)](https://www.npmjs.com/package/coldstar-mcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Node](https://img.shields.io/badge/Node-%3E%3D18-339933?logo=node.js)](https://nodejs.org)
[![Tools](https://img.shields.io/badge/tools-22-blue)](https://modelcontextprotocol.io)

**The only cold wallet MCP server.** 22 tools for air-gapped Solana and Base wallet operations -- reputation-gated transactions, institutional custody vaults, DEX quotes, price feeds, and cryptographic signature verification. Security-first, hardware-agnostic.

No competitor exists. Every other wallet MCP holds keys in memory. Coldstar is a read-only security layer that never touches private keys.

## Install

```bash
npx coldstar-mcp
```

Or install globally:

```bash
npm install -g coldstar-mcp
coldstar-mcp
```

## Configure

Add to your MCP config (`claude_desktop_config.json` or `~/.mcp.json`):

```json
{
  "mcpServers": {
    "coldstar": {
      "command": "npx",
      "args": ["-y", "coldstar-mcp"],
      "env": {
        "SOLANA_RPC_URL": "https://api.mainnet-beta.solana.com",
        "FAIRSCORE_API_KEY": ""
      }
    }
  }
}
```

## Tools (22)

### Solana (9)

| Tool | Description | Key Params |
|------|-------------|------------|
| `check_reputation` | FairScore reputation of any Solana wallet (0-100, tier, badges) | `address` |
| `get_token_price` | Real-time token prices via Pyth Network oracle | `token` |
| `get_swap_quote` | Jupiter DEX swap quotes with best routes | `inputToken`, `outputToken`, `amount` |
| `check_wallet_balance` | SOL and SPL token balances | `address` |
| `validate_transaction` | **Pre-flight safety check** -- reputation gate before any transfer | `recipient`, `amount`, `token` |
| `list_supported_tokens` | All supported tokens with mint addresses | -- |
| `get_portfolio` | Full portfolio with USD values (balances + Pyth prices) | `wallet_address` |
| `estimate_swap_cost` | Total swap cost analysis including price impact and fees | `inputToken`, `outputToken`, `amount` |
| `solana_get_fees` | Current network fees, slot height, and transaction cost estimates | -- |

### Base / EVM (5)

| Tool | Description | Key Params |
|------|-------------|------------|
| `base_check_balance` | ETH and ERC-20 balances on Base | `address` |
| `base_get_gas_price` | Current Base gas price | -- |
| `base_get_token_price` | Token prices on Base | `token` |
| `base_get_portfolio` | Full portfolio with USD values on Base | `address` |
| `base_list_tokens` | Supported Base tokens with contract addresses | -- |

### Institutional Custody (6)

| Tool | Description | Key Params |
|------|-------------|------------|
| `create_custody_request` | Create a withdrawal request from the vault | `amount`, `token`, `destination` |
| `list_pending_approvals` | List pending withdrawal requests | -- |
| `approve_custody_transfer` | Approve a pending request | `requestId` |
| `get_vault_status` | Vault health, compliance info, and balances | -- |
| `get_custody_audit_trail` | On-chain event history for the vault | -- |
| `validate_custody_transfer` | Pre-flight check before creating a custody request | `amount`, `token`, `destination` |

### Cryptographic Verification (2)

| Tool | Description | Key Params |
|------|-------------|------------|
| `verify_ed25519_signature` | Verify Ed25519 signatures -- independent check on signed transactions | `message`, `signature`, `publicKey` |
| `verify_webhook_hmac` | Verify HMAC-SHA256 webhook signatures (Shopify, GitHub, Stripe) | `payload`, `signature`, `secret` |

## Why This One?

- **Read-only security layer.** Coldstar never holds private keys, never signs transactions, never broadcasts. It only provides reputation checks, price data, and safety gates. The worst case if compromised is incorrect data -- it can never move funds.
- **Reputation-gated transactions.** Every outbound transfer is checked against FairScore. Bronze-tier wallets (score 0-19) are blocked. Even a compromised AI agent cannot send funds to a scam address.
- **Multichain + institutional custody.** Covers Solana and Base with 22 tools. Institutional vault operations (create/approve/audit withdrawals) are built in for permissioned stablecoin custody.

## Security Model

### Reputation Gating

| Tier | Score | Action | Transfer Limit |
|------|-------|--------|----------------|
| Bronze | 0-19 | **BLOCK** | Blocked |
| Silver | 20-39 | **WARN** | 10 SOL max |
| Gold | 40-59 | Allow | 100 SOL max |
| Platinum | 60-79 | Allow | 500 SOL max |
| Diamond | 80-100 | Allow | Unlimited |

### What Coldstar Does NOT Do

- Does **not** hold private keys (that is the air-gapped USB wallet)
- Does **not** sign transactions (signing is offline)
- Does **not** broadcast transactions (that is the user's choice)
- **Only** provides read operations and safety checks

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SOLANA_RPC_URL` | No | Solana RPC endpoint (default: mainnet) |
| `BASE_RPC_URL` | No | Base RPC endpoint (default: `https://mainnet.base.org`) |
| `FAIRSCORE_API_URL` | No | FairScale API base URL |
| `FAIRSCORE_API_KEY` | No | FairScale API key |

## Architecture

```
AI Agent (Claude, GPT, etc.)
    |
    v
Coldstar MCP Server (this package)
    |
    +---> FairScale API (reputation scoring)
    +---> Pyth Network (price oracles)
    +---> Jupiter Aggregator (DEX quotes)
    +---> Solana RPC (balances, token accounts)
    +---> Base RPC (EVM balances, gas)
    +---> Coldstar Vault Program (custody ops)
    |
    v
Coldstar Air-Gapped Wallet (offline signing)
```

## Development

```bash
git clone https://github.com/ExpertVagabond/coldstar.git
cd coldstar/mcp-server
npm install
node index.js
```

## License

MIT -- [Purple Squirrel Media](https://github.com/ExpertVagabond)
