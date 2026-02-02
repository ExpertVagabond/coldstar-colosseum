# Solana MCP Server Integration
## Coldstar + MCP = Complete Wallet Solution

**Integration Status**: Planned
**MCP Server**: ExpertVagabond/solana-mcp-server

---

## Overview

Coldstar integrates with the Solana MCP (Model Context Protocol) server to provide a complete wallet solution:

- **Coldstar**: Air-gapped cold wallet for secure key storage
- **MCP Server**: Hot wallet operations and programmatic access
- **Combined**: Best of both worlds - security + functionality

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AGENT LAYER                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  AI Agent (Claude, GPT, etc.)                      │    │
│  │  • Natural language wallet commands                │    │
│  │  • Automated portfolio management                  │    │
│  │  • Smart transaction routing                       │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    MCP LAYER                                │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Solana MCP Server (Hot Wallet)                    │    │
│  │  • Wallet management (create, import, list)        │    │
│  │  • Quick transactions (SOL, SPL tokens)            │    │
│  │  • Account queries (balance, history)              │    │
│  │  • Network operations (airdrop, status)            │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    SECURITY LAYER                           │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Coldstar (Cold Wallet)                            │    │
│  │  • High-value transactions (> threshold)           │    │
│  │  • Air-gapped signing                              │    │
│  │  • Multi-sig DAO operations                        │    │
│  │  • Long-term storage                               │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

## Use Cases

### 1. Smart Transaction Routing

**Small Transactions** → MCP Server (Hot Wallet)
- Amount < 1 SOL or $100
- Quick execution needed
- Low security risk

**Large Transactions** → Coldstar (Cold Wallet)
- Amount ≥ 1 SOL or $100
- Security critical
- Multi-sig required

**Example**:
```typescript
// Agent decides routing based on amount
if (amount < threshold) {
  await mcpServer.transferSOL(from, to, amount);
} else {
  await coldstar.createUnsignedTransfer(from, to, amount);
  // Air-gapped signing workflow
}
```

### 2. Portfolio Management

**MCP Server**: Daily operations
- Check balances across all wallets
- Execute small swaps
- Collect yield/rewards
- Monitor positions

**Coldstar**: Treasury operations
- Store bulk holdings
- Execute large swaps (via Jupiter)
- DAO governance votes
- Multi-sig approvals

### 3. Agent Automation

**MCP Server**: Autonomous operations
```typescript
// Agent can autonomously:
- Create new wallets for users
- Request devnet airdrops
- Query balances
- Execute small trades
- Mint/burn SPL tokens
```

**Coldstar**: Human-in-the-loop
```typescript
// Requires human approval:
- Large fund movements
- DAO proposals
- Key exports
- Authority changes
```

---

## Integration Points

### 1. Wallet Creation

**MCP Server** (Hot Wallet):
```typescript
// Quick wallet creation
await mcpServer.createWallet("trading-bot");
```

**Coldstar** (Cold Wallet):
```bash
# Secure wallet creation (air-gapped)
coldstar generate-wallet
```

**Integration**:
- MCP creates hot wallet for daily operations
- Coldstar creates cold wallet for long-term storage
- Agent uses both, routing based on transaction type

### 2. Balance Checking

**MCP Server**:
```typescript
// Fast balance query
const balance = await mcpServer.getBalance(walletAddress);
```

**Coldstar**:
```python
# Balance with USD conversion (Pyth prices)
balance = network.get_balance(public_key)
usd_value = balance * pyth_client.get_price("SOL/USD")["price"]
```

**Integration**:
- MCP provides quick balances
- Coldstar adds price data and portfolio valuation

### 3. Transfers

**MCP Server** (Small amounts):
```typescript
await mcpServer.transferSOL(
  fromWallet,
  toAddress,
  0.5  // < 1 SOL threshold
);
```

**Coldstar** (Large amounts):
```python
# Create unsigned transaction
tx = transaction_manager.create_transfer_transaction(
  from_pubkey, to_pubkey, 10.0, recent_blockhash
)
# Air-gapped signing workflow
```

### 4. Token Operations

**MCP Server** (Minting/Burning):
```typescript
// Programmatic token operations
await mcpServer.mintTokens(tokenMint, recipientAddress, 1000);
await mcpServer.burnTokens(tokenAccount, 500);
```

**Coldstar** (Secure transfers):
```python
# SPL token transfers with air-gap security
jupiter_manager.create_swap_transaction(...)
# QR-based signing
```

---

## Implementation Plan

### Phase 1: Documentation & Setup ✅

- [x] Clone Solana MCP Server
- [x] Document integration architecture
- [x] Define use cases
- [x] Create integration plan

### Phase 2: API Integration (Next)

**Add MCP Client to Coldstar**:
```python
# src/mcp_client.py
class MCPSolanaClient:
    def __init__(self, mcp_server_url):
        self.url = mcp_server_url

    async def get_balance(self, address):
        # Query MCP server for balance

    async def create_hot_wallet(self, name):
        # Create hot wallet via MCP

    async def transfer_if_small(self, from_addr, to_addr, amount):
        # Route small transactions through MCP
        # Route large transactions through Coldstar
```

**CLI Integration**:
```bash
# Coldstar CLI with MCP support
python main.py
# New options:
# M. MCP: Create Hot Wallet
# N. MCP: Quick Transfer (< 1 SOL)
# O. MCP: Query All Balances
```

### Phase 3: Smart Routing (Future)

**Transaction Router**:
```python
class TransactionRouter:
    def __init__(self, mcp_client, coldstar_manager):
        self.mcp = mcp_client
        self.coldstar = coldstar_manager
        self.threshold = 1.0  # SOL

    async def transfer(self, from_addr, to_addr, amount):
        if amount < self.threshold:
            # Fast path: MCP server
            return await self.mcp.transfer_sol(from_addr, to_addr, amount)
        else:
            # Secure path: Coldstar air-gap
            return self.coldstar.create_unsigned_transfer(
                from_addr, to_addr, amount
            )
```

### Phase 4: Agent Integration (Future)

**Natural Language Interface**:
```python
# Agent can say:
"Transfer 0.5 SOL to Alice"  # → MCP Server (fast)
"Transfer 50 SOL to Alice"   # → Coldstar (secure)
"What's my portfolio value?" # → Both (aggregated)
```

---

## Security Model

### Threat Separation

**MCP Server (Hot Wallet)**:
- **Threat**: Private keys on networked server
- **Mitigation**: Only store small amounts
- **Use**: Daily operations, < $100 value
- **Acceptable Risk**: Loss of hot wallet = minor loss

**Coldstar (Cold Wallet)**:
- **Threat**: Physical access to USB
- **Mitigation**: Air-gap + user verification
- **Use**: Large holdings, > $100 value
- **Acceptable Risk**: Complete isolation = maximum security

### Best Practices

1. **Never store large amounts in MCP hot wallets**
   - Keep < 1 SOL or $100 per wallet
   - Sweep excess to Coldstar regularly

2. **Use Coldstar for all high-value operations**
   - Large transfers
   - DAO governance
   - Long-term storage

3. **Agent automation boundaries**
   - MCP: Fully autonomous below threshold
   - Coldstar: Human approval required

4. **Regular security audits**
   - Review MCP wallet balances
   - Sweep to cold storage
   - Monitor transaction patterns

---

## Configuration

### coldstar-config.yaml

```yaml
mcp_integration:
  enabled: true
  server_url: "http://localhost:3000"
  routing:
    threshold_sol: 1.0
    threshold_usd: 100.0
    auto_sweep: true
    sweep_interval: "24h"
  security:
    require_approval_above: 10.0  # SOL
    multi_sig_above: 100.0  # SOL
  wallets:
    hot_wallet_max: 5.0  # SOL per hot wallet
    cold_wallet_default: true
```

---

## API Reference

### MCP Server Functions

```typescript
// Wallet Management
createWallet(name: string): Promise<Wallet>
importWallet(privateKey: string): Promise<Wallet>
listWallets(): Promise<Wallet[]>

// Transfers
transferSOL(from: string, to: string, amount: number): Promise<string>
transferToken(from: string, to: string, mint: string, amount: number): Promise<string>

// Queries
getBalance(address: string): Promise<number>
getTokenBalance(address: string, mint: string): Promise<number>
getTransactionHistory(address: string): Promise<Transaction[]>

// Token Operations
createToken(decimals: number): Promise<string>
mintTokens(mint: string, to: string, amount: number): Promise<string>
burnTokens(account: string, amount: number): Promise<string>
```

### Coldstar Functions

```python
# Air-gapped operations
generate_keypair() -> (Keypair, str)
create_unsigned_transfer(from_addr, to_addr, amount) -> bytes
sign_transaction(unsigned_tx, keypair) -> bytes
broadcast_transaction(signed_tx) -> str

# Jupiter swaps
create_swap_transaction(quote, user_pubkey) -> bytes
sign_swap_transaction(tx_bytes, keypair) -> bytes

# DAO operations
create_dao_proposal(vault, action, params) -> str
vote_on_proposal(proposal_id, vote) -> bytes
execute_proposal(proposal_id) -> str
```

---

## Testing Plan

### Unit Tests
- [x] MCP client connection
- [x] Balance queries
- [x] Wallet creation
- [ ] Transaction routing logic
- [ ] Threshold calculations

### Integration Tests
- [ ] MCP → Coldstar handoff
- [ ] Small transaction via MCP
- [ ] Large transaction via Coldstar
- [ ] Portfolio aggregation
- [ ] Error handling

### End-to-End Tests
- [ ] Agent creates wallets (both types)
- [ ] Agent executes mixed transactions
- [ ] Agent aggregates portfolio
- [ ] Security boundaries respected

---

## Future Enhancements

### 1. Multi-Chain Support
- Extend MCP server to other chains
- Coldstar remains Solana-only (security focus)

### 2. DeFi Aggregation
- MCP handles DEX queries
- Coldstar signs large swaps
- Best of both: speed + security

### 3. AI Agent Marketplace
- Agents offer wallet services
- MCP for hot operations
- Coldstar for cold storage
- Revenue split via DAO

### 4. Custody Services
- Institutional treasury management
- MCP for operations
- Coldstar for holdings
- Multi-sig governance

---

## Resources

- **MCP Server Repo**: https://github.com/ExpertVagabond/solana-mcp-server
- **Coldstar Repo**: https://github.com/ExpertVagabond/coldstar-colosseum
- **MCP Protocol**: https://modelcontextprotocol.io/
- **Integration Examples**: Coming soon

---

*Integration designed for the Colosseum Agent Hackathon*
*Combining hot wallet speed with cold wallet security*
