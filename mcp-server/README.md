# Coldstar MCP Server

Secure signing infrastructure for AI agents on Solana. FairScore reputation gating prevents rogue agents from draining wallets.

## The Problem

AI agents are getting access to crypto wallets for payments, DeFi, and autonomous trading. But an agent can be tricked -- prompt injection, compromised tool calls, or hallucinated addresses can cause it to send funds to a scam wallet. There is no guardrail between "agent decides to send" and "funds are gone."

## The Solution

Coldstar MCP intercepts every outbound transaction and checks the recipient's on-chain reputation via FairScore. Low-reputation wallets are blocked. Medium-reputation wallets trigger warnings. Only verified, high-reputation addresses pass through cleanly.

**The `validate_transaction` tool is the kill switch.** Any AI agent using Coldstar will automatically refuse to send funds to wallets with Bronze-tier reputation -- even if the agent itself has been compromised.

## 8 Tools

| Tool | Description |
|------|-------------|
| `check_reputation` | Check FairScore reputation of any Solana wallet (score 0-100, tier, badges) |
| `get_token_price` | Real-time token prices via Pyth Network oracle |
| `get_swap_quote` | Jupiter DEX swap quotes with best routes across all Solana DEXes |
| `check_wallet_balance` | SOL and SPL token balances for any wallet |
| `validate_transaction` | **Pre-flight safety check** -- reputation gate before any transfer |
| `list_supported_tokens` | All supported tokens with mint addresses |
| `get_portfolio` | Full portfolio with USD values (balances + Pyth prices) |
| `estimate_swap_cost` | Total swap cost analysis including price impact and fees |

## Install

```bash
npm install -g coldstar-mcp
```

Or run directly:

```bash
npx coldstar-mcp
```

## Configure

### Claude Desktop / Claude Code

Add to your MCP settings:

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

### Cursor / Windsurf / Other MCP Clients

Same configuration format -- just add the `coldstar` entry to your MCP config.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SOLANA_RPC_URL` | `https://api.mainnet-beta.solana.com` | Solana RPC endpoint |
| `FAIRSCORE_API_URL` | `https://api2.fairscale.xyz` | FairScale API base URL |
| `FAIRSCORE_API_KEY` | (empty) | Optional FairScale API key |

## Security Model

### Reputation Gating

Every outbound transfer is gated by FairScore reputation tiers:

| Tier | Score | Action | Transfer Limit |
|------|-------|--------|----------------|
| Bronze | 0-19 | **BLOCK** | Blocked |
| Silver | 20-39 | **WARN** | 10 SOL max |
| Gold | 40-59 | Allow | 100 SOL max |
| Platinum | 60-79 | Allow | 500 SOL max |
| Diamond | 80-100 | Allow | Unlimited |

### How It Protects Agents

1. **Agent receives instruction** to send 50 SOL to an address
2. **Agent calls `validate_transaction`** with the recipient address
3. **Coldstar checks FairScore** -- recipient has a score of 12 (Bronze)
4. **Transaction is BLOCKED** -- agent receives clear "not allowed" response
5. **Agent refuses the transaction** and reports the issue

The agent never needs to understand scam detection. Coldstar handles it at the infrastructure layer.

### What Coldstar Does NOT Do

- It does **not** hold private keys (that is the air-gapped USB wallet)
- It does **not** sign transactions (signing is offline)
- It does **not** broadcast transactions (that is the user's choice)
- It **only** provides read operations and safety checks

This is a read-only security layer. The worst case if Coldstar is compromised is that it returns incorrect reputation data -- it can never move funds.

## Example Usage

### Validate Before Sending

```
Agent: I need to send 5 SOL to 7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU

> validate_transaction(recipient="7xKXtg...", amount=5, token="SOL")

Result: {
  "allowed": false,
  "tier": "Bronze",
  "fairscore": 8.5,
  "warnings": ["BLOCKED: Recipient has Bronze reputation (score: 8.5). Transaction denied."],
  "recommendation": "Transaction should be rejected"
}

Agent: I cannot complete this transfer. The recipient wallet has a Bronze reputation
score of 8.5/100 which indicates high risk. The transaction has been blocked by
Coldstar's reputation gating system.
```

### Check Portfolio

```
> get_portfolio(wallet_address="YourWa11etAddressHere...")

Result: {
  "total_value_usd": 1523.41,
  "holdings": [
    { "symbol": "SOL", "amount": 10.5, "price_usd": 130.25, "value_usd": 1367.63 },
    { "symbol": "USDC", "amount": 155.78, "price_usd": 1.0, "value_usd": 155.78 }
  ]
}
```

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
    |
    v
Coldstar Air-Gapped Wallet (offline signing)
```

## Target Integration Partners

- **Phantom** -- Wallet-level reputation gating
- **Backpack** -- Agent-aware wallet security
- **Coinbase** -- Institutional agent custody
- **Anthropic** -- Agent safety infrastructure
- **OpenAI** -- Agent payment guardrails
- **Stripe** -- Crypto payment validation

## License

MIT
