# FairScore Integration Documentation

```
╔═══════════════════════════════════════════════════════════════╗
║  COLDSTAR × FAIRSCORE                                         ║
║  Reputation-Gated Cold Wallet Security                        ║
║                                                                ║
║  "B - Love U 3000"                                            ║
╚═══════════════════════════════════════════════════════════════╝
```

## Overview

**FairScore** is a reputation scoring system for Solana wallets by FairScale. It provides a 0-100 score with tier classifications (bronze/silver/gold/platinum), behavioral badges, and feature breakdowns. Coldstar maps these to a 1-5 internal tier system for transaction gating without compromising air-gap security.

**Live API:** `GET https://api2.fairscale.xyz/score?wallet=<address>` (auth via `fairkey` header)

### Why FairScore?

Traditional cold wallets are secure but blind. They protect your private keys but offer no context about the addresses you're transacting with. FairScore bridges this gap by providing reputation intelligence **before** transactions cross the air-gap boundary.

### Air-Gap Architecture Compatibility

FairScore checks occur on the **online device** during transaction preparation:

1. User initiates a transfer on the online device
2. FairScore API queries happen before QR code generation
3. Reputation tier determines if transaction can proceed
4. Only approved transactions generate QR codes
5. Air-gap device signs without needing external data
6. Signed transaction returns to online device for broadcast

This preserves complete air-gap isolation while adding reputation awareness.

---

## How It Works

### Transaction Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│  ONLINE DEVICE (Hot Wallet / Coldstar Dashboard)                │
│                                                                   │
│  1. User initiates transfer                                      │
│     └─> Enter recipient address                                 │
│     └─> Enter amount                                            │
│                                                                   │
│  2. Address Validation                                           │
│     └─> Valid Solana address? ──NO──> Error                     │
│              │                                                    │
│             YES                                                   │
│              │                                                    │
│  3. FairScore API Query                                          │
│     └─> GET /score?wallet={address}                             │
│              │                                                    │
│              ├─> Tier 1 (UNTRUSTED) ──> HARD BLOCK              │
│              │   └─> Error message, transaction cancelled        │
│              │                                                    │
│              ├─> Tier 2 (LOW TRUST) ──> SOFT WARNING            │
│              │   └─> User confirmation required                  │
│              │   └─> Amount limit: 10 SOL                        │
│              │                                                    │
│              └─> Tier 3-5 (TRUSTED+) ──> ALLOW                  │
│                  └─> Proceed with tiered limits                  │
│                                                                   │
│  4. Create Unsigned Transaction                                  │
│     └─> Serialize transaction data                              │
│     └─> Generate QR code                                         │
│                                                                   │
│  5. Display QR Code                                              │
└───────────────────────────┬─────────────────────────────────────┘
                             │
                    [QR CODE TRANSFER]
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  AIR-GAP DEVICE (Cold Wallet / Never Online)                    │
│                                                                   │
│  6. Scan QR Code                                                 │
│     └─> Parse unsigned transaction                              │
│                                                                   │
│  7. Review & Sign                                                │
│     └─> Display transaction details                             │
│     └─> User confirms and signs with private key                │
│     └─> Generate signed transaction QR code                     │
│                                                                   │
│  8. Display Signed QR Code                                       │
└───────────────────────────┬─────────────────────────────────────┘
                             │
                    [QR CODE TRANSFER]
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  ONLINE DEVICE (Returns to Hot Wallet)                           │
│                                                                   │
│  9. Scan Signed QR Code                                          │
│     └─> Parse signed transaction                                │
│                                                                   │
│  10. Broadcast to Solana Network                                 │
│      └─> Transaction confirmed                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Tier Definitions

FairScale returns a 0-100 score and string tier (bronze/silver/gold/platinum). Coldstar maps these to an internal 1-5 system for transaction gating:

| Internal | API Tier | Score Range | Label | Action | Default Limit | Description |
|----------|----------|-------------|-------|--------|---------------|-------------|
| **1** | bronze | 0-19 | UNTRUSTED | **BLOCK** | 0 SOL | Low-reputation wallet. Transaction is immediately rejected. |
| **2** | silver | 20-39 | LOW TRUST | **WARN** | 10 SOL | New or unverified wallet. User must explicitly confirm to proceed. |
| **3** | gold | 40-59 | TRUSTED | **ALLOW** | 100 SOL | Established wallet with positive history. Standard operations permitted. |
| **4** | platinum | 60-79 | HIGH TRUST | **ALLOW** | 500 SOL | Verified protocol or high-reputation user. Elevated transfer limits. |
| **5** | (80+) | 80-100 | EXCELLENT | **ALLOW** | Unlimited | Top-tier reputation. No limits. |

**Live API Example (Jupiter wallet):**
```json
{
  "wallet": "JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN",
  "fairscore": 34.2,
  "tier": "silver",
  "badges": [
    {"id": "lst_staker", "label": "LST Staker", "tier": "gold"},
    {"id": "sol_maxi", "label": "SOL Maxi", "tier": "gold"},
    {"id": "no_dumper", "label": "No Instant Dumps", "tier": "silver"}
  ]
}
```

### Tier Color Coding in CLI

```python
TIER_COLORS = {
    1: "\033[91m",  # Bright Red
    2: "\033[93m",  # Bright Yellow
    3: "\033[92m",  # Bright Green
    4: "\033[96m",  # Bright Cyan
    5: "\033[95m",  # Bright Magenta
}
```

---

## Integration Points

FairScore is integrated across **6 major touch points** in Coldstar:

### 1. Transaction Gating (Primary)

**Location:** `src/fairscore_integration.py` → `should_block_transaction()`

- Called before every outgoing transfer
- Tier 1 addresses are hard-blocked
- Tier 2 addresses trigger confirmation prompts
- Tier 3-5 addresses proceed with tiered limits

**Code Example:**
```python
tier = fairscore.get_tier(recipient_address)
if tier == 1:
    raise TransactionBlockedError("Recipient address flagged as UNTRUSTED")
elif tier == 2 and amount > 10_000_000:  # 10 SOL in lamports
    if not confirm_risky_transaction(recipient_address, amount):
        raise UserCancelledError()
```

### 2. Dynamic Transfer Limits

**Location:** `src/fairscore_integration.py` → `get_transfer_limit()`

- Returns SOL limits based on tier
- Enforced at transaction preparation
- User-configurable overrides in config

**Default Limits:**
```python
TIER_LIMITS = {
    1: 0,           # 0 SOL (blocked)
    2: 10,          # 10 SOL (warning)
    3: 100,         # 100 SOL (standard)
    4: 500,         # 500 SOL (high trust)
    5: float('inf') # Unlimited (excellent)
}
```

### 3. DAO Vote Weighting

**Location:** `coldstar/dao/vote_manager.py`

- FairScore tier influences governance voting power
- Tier 5 addresses get 2x weight
- Tier 1 addresses cannot vote
- Prevents Sybil attacks on governance

**Implementation:**
```python
def calculate_vote_weight(address: str, token_balance: float) -> float:
    tier = fairscore.get_tier(address)
    if tier == 1:
        return 0  # No voting rights
    elif tier == 5:
        return token_balance * 2.0  # 2x multiplier
    else:
        return token_balance  # Standard weight
```

### 4. Jupiter Swap Screening

**Location:** `coldstar/integrations/jupiter.py`

- Pre-screens token contract addresses before swaps
- Warns on low-tier token contracts
- Protects against honeypot tokens and rug pulls

**Flow:**
```python
token_tier = fairscore.get_tier(token_mint_address)
if token_tier <= 2:
    display_warning(f"Token contract has LOW TRUST rating (Tier {token_tier})")
    if not user_confirms():
        return  # Cancel swap
```

### 5. Portfolio Dashboard

**Location:** `coldstar/ui/dashboard.py`

- Displays reputation badges next to all addresses
- Visual indicators (color + tier number)
- Hover tooltips with full reputation data

**Badge Format:**
```
Address: 8xK...9pQ [🟢 Tier 3 - TRUSTED]
Address: 3mN...7fW [🔴 Tier 1 - UNTRUSTED - BLOCKED]
```

### 6. MCP Agent Transaction Gates

**Location:** `coldstar/mcp/server.py`

- AI agents must pass FairScore checks before executing transfers
- Prevents compromised agents from sending to malicious addresses
- Agent-initiated transactions use stricter thresholds (Tier 3+ required)

**Agent Policy:**
```python
if fairscore.get_tier(destination) < 3:
    raise AgentSecurityError(
        "Agent transactions require Tier 3+ destination addresses"
    )
```

---

## Setup

### API Key Configuration

FairScore requires an API key from FairScale. Get one at https://sales.fairscale.xyz/

**Option 1: Environment Variable (Recommended)**
```bash
export FAIRSCORE_API_KEY="zpka_your_key_here"
```

**Option 2: Configuration File**

Edit `config.py`:
```python
FAIRSCORE_API_URL = "https://api2.fairscale.xyz"
FAIRSCORE_API_KEY = ""  # Set via env FAIRSCORE_API_KEY or here
FAIRSCORE_ENABLED = True
FAIRSCORE_MIN_TIER = 2  # Minimum tier to allow transactions without warning
```

**API Endpoints Available:**
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/score?wallet=` | GET | Full response: tier, badges, features, score |
| `/fairScore?wallet=` | GET | Lightweight: just the combined score |
| `/walletScore?wallet=` | GET | Wallet-only score (excludes social) |

All endpoints require the `fairkey` header for authentication.

### Enable/Disable

FairScore can be toggled without removing API keys:

```python
FAIRSCORE_ENABLED = True  # Set to False to disable all checks
```

When disabled, all transactions proceed as if Tier 5 (no gating).

### Fallback Behavior

If FairScore API is unreachable:
- Tier 3 (TRUSTED) is assumed by default
- User is notified of offline reputation service
- Configurable via `FAIRSCORE_FALLBACK_TIER` (default: 3)

---

## Usage

### Manual Address Lookup

From the main menu:

```
Coldstar Main Menu
==================
[S] Send SOL
[R] Receive SOL
[J] Jupiter Swap
[D] DAO Operations
[F] FairScore Lookup  <-- Manual reputation check
[Q] Quit

Select option: F
Enter Solana address to check: 8xK7JhYZ...9pQ3mN

╔═══════════════════════════════════════════════════════════╗
║  FAIRSCORE REPUTATION REPORT                              ║
╠═══════════════════════════════════════════════════════════╣
║  Address:  8xK7JhYZ...9pQ3mN                             ║
║  Tier:     🟢 3 - TRUSTED                                 ║
║  Limit:    100 SOL per transaction                        ║
║                                                            ║
║  History:                                                  ║
║    • 1,247 successful transactions                        ║
║    • 0 reported scams                                     ║
║    • Active for 8 months                                  ║
║                                                            ║
║  Notes:                                                    ║
║    Standard trusted address. No red flags detected.       ║
╚═══════════════════════════════════════════════════════════╝
```

### Automatic Checks on Send

When sending SOL:

```
Send SOL
========
Recipient address: 3mN4fW...7rT8pL
Amount (SOL): 5.5

Checking recipient reputation...

⚠️  WARNING: LOW TRUST ADDRESS DETECTED
╔═══════════════════════════════════════════════════════════╗
║  Tier: 🟡 2 - LOW TRUST                                   ║
║  Reason: New address, minimal on-chain activity           ║
║  Transaction limit: 10 SOL                                ║
╚═══════════════════════════════════════════════════════════╝

Your transaction (5.5 SOL) is within limits but risky.

Continue anyway? [y/N]:
```

### Tier 1 Block Example

```
Send SOL
========
Recipient address: 2kM9nF...3vB6xP
Amount (SOL): 1.0

Checking recipient reputation...

🚫 TRANSACTION BLOCKED
╔═══════════════════════════════════════════════════════════╗
║  Tier: 🔴 1 - UNTRUSTED                                   ║
║  Reason: Address flagged for suspicious activity          ║
║                                                            ║
║  This address has been reported for:                      ║
║    • Phishing attempts                                    ║
║    • Fake token airdrops                                  ║
║    • Multiple user reports                                ║
║                                                            ║
║  Transaction CANNOT proceed.                              ║
╚═══════════════════════════════════════════════════════════╝

Press any key to return to menu...
```

---

## API Reference

### FairScoreClient Methods

#### `get_tier(address: str) -> int`

Returns the reputation tier (1-5) for a given address.

**Parameters:**
- `address` (str): Base58-encoded Solana public key

**Returns:**
- `int`: Tier number (1-5)

**Raises:**
- `InvalidAddressError`: If address is not valid Solana format
- `APIError`: If FairScore service is unreachable

**Example:**
```python
from coldstar.core.fairscore_client import FairScoreClient

fairscore = FairScoreClient()
tier = fairscore.get_tier("8xK7JhYZ...9pQ3mN")
print(f"Address tier: {tier}")  # Output: Address tier: 3
```

---

#### `get_risk_assessment(address: str) -> dict`

Returns detailed risk analysis for an address.

**Parameters:**
- `address` (str): Base58-encoded Solana public key

**Returns:**
- `dict`: Risk assessment data structure

**Example Response:**
```python
{
    "address": "8xK7JhYZ...9pQ3mN",
    "tier": 3,
    "tier_label": "TRUSTED",
    "risk_score": 25,  # 0-100, lower is better
    "flags": [],
    "history": {
        "total_transactions": 1247,
        "reported_scams": 0,
        "age_days": 240
    },
    "recommendations": [
        "Standard trusted address",
        "No special precautions required"
    ]
}
```

---

#### `should_block_transaction(address: str, amount_lamports: int) -> tuple[bool, str]`

Determines if a transaction should be blocked based on reputation and amount.

**Parameters:**
- `address` (str): Recipient address
- `amount_lamports` (int): Transfer amount in lamports

**Returns:**
- `tuple[bool, str]`: (should_block, reason_message)

**Example:**
```python
blocked, reason = fairscore.should_block_transaction(
    "3mN4fW...7rT8pL",
    5_500_000_000  # 5.5 SOL
)

if blocked:
    print(f"Transaction blocked: {reason}")
else:
    print("Transaction approved")
```

---

#### `display_reputation_badge(address: str) -> str`

Returns a formatted string with color-coded reputation badge.

**Parameters:**
- `address` (str): Address to generate badge for

**Returns:**
- `str`: ANSI-colored badge string

**Example Output:**
```python
badge = fairscore.display_reputation_badge("8xK7JhYZ...9pQ3mN")
print(badge)
# Output: "\033[92m[🟢 Tier 3 - TRUSTED]\033[0m"
```

---

#### `get_transfer_limit(tier: int) -> float`

Returns the recommended transfer limit for a given tier.

**Parameters:**
- `tier` (int): Reputation tier (1-5)

**Returns:**
- `float`: Limit in SOL (or `float('inf')` for unlimited)

**Example:**
```python
limit = fairscore.get_transfer_limit(3)
print(f"Tier 3 limit: {limit} SOL")  # Output: Tier 3 limit: 100 SOL
```

---

## Security Considerations

### What FairScore Protects Against

1. **Sybil Attacks**: DAO voting protection via reputation weighting
2. **Phishing Addresses**: Known scam addresses hard-blocked
3. **Honeypot Tokens**: Jupiter swap screening flags risky contracts
4. **Agent Compromise**: MCP agents restricted to Tier 3+ destinations
5. **Social Engineering**: Warnings on new/suspicious addresses
6. **Rug Pulls**: Token contract reputation screening

### Limitations

FairScore is **not foolproof**. Users should still exercise caution:

1. **Compromised High-Tier Addresses**: A previously trusted address can be compromised. FairScore data may lag behind real-time events.

2. **Zero-Day Scams**: Brand new scam addresses start with Tier 2 (LOW TRUST), not Tier 1 (UNTRUSTED), until flagged.

3. **API Dependency**: FairScore requires network connectivity. Air-gap device never queries FairScore—only the online device does.

4. **False Positives**: Legitimate new addresses may be flagged as Tier 2 and require manual confirmation.

5. **User Override**: Users can disable FairScore or ignore warnings. No system can protect against determined user action.

### Air-Gap Compatibility

**Critical Security Guarantee:**

- Air-gap device **NEVER** communicates with FairScore API
- All reputation checks occur on online device **before** QR code generation
- Signed transactions contain no reputation data
- Air-gap device remains completely isolated

**Attack Surface:**

- FairScore API compromise could deliver false tier data
- MITIGATION: Use strict mode (`FAIRSCORE_STRICT_MODE = True`) to block Tier 2 as well
- MITIGATION: Cross-reference with on-chain data and community reports

---

## Troubleshooting

### Issue: "FairScore API Unreachable"

**Symptoms:**
```
⚠️  FairScore reputation service offline
Using fallback tier: 3 (TRUSTED)
Proceed with caution.
```

**Causes:**
- Network connectivity issues
- FairScore service downtime
- API key expired/invalid

**Solutions:**
1. Check internet connection on online device
2. Verify `FAIRSCORE_API_KEY` in config
3. Test API manually: `curl -H "Authorization: Bearer $FAIRSCORE_API_KEY" https://api.fairscore.io/v1/health`
4. Adjust `FAIRSCORE_FALLBACK_TIER` if needed (default: 3)

---

### Issue: "All Addresses Show Tier 2"

**Symptoms:**
- Every address lookup returns Tier 2 (LOW TRUST)
- Even known good addresses are flagged

**Causes:**
- Using testnet addresses (reputation only on mainnet)
- FairScore account not activated
- API key missing permissions

**Solutions:**
1. Confirm you're on `mainnet-beta`: `solana config get`
2. Log into FairScore dashboard and verify account status
3. Regenerate API key with full permissions

---

### Issue: "Transaction Blocked Despite Tier 3"

**Symptoms:**
```
🚫 TRANSACTION BLOCKED
Tier: 🟢 3 - TRUSTED
Reason: Amount exceeds tier limit
```

**Causes:**
- Transfer amount exceeds tier's configured limit
- Custom limits set too low in config

**Solutions:**
1. Check configured limits: `TIER_LIMITS` in `config.py`
2. Split transaction into smaller amounts
3. Request recipient to build reputation (more on-chain activity)
4. Override limit (requires config change and restart)

---

### Issue: "Tier Lookup Takes Too Long"

**Symptoms:**
- 5+ second delays when entering recipient addresses
- Timeout errors on `get_tier()`

**Causes:**
- Slow network connection
- FairScore API rate limiting
- Large batch queries

**Solutions:**
1. Reduce API timeout: `FAIRSCORE_API_TIMEOUT = 3.0` (seconds)
2. Enable response caching: `FAIRSCORE_CACHE_ENABLED = True`
3. Upgrade FairScore API tier for higher rate limits
4. Pre-fetch tiers for known addresses in background

---

### Issue: "MCP Agent Cannot Send to Any Address"

**Symptoms:**
```
AgentSecurityError: Agent transactions require Tier 3+ destination addresses
```

**Causes:**
- Agent policy requires Tier 3+ by design
- Recipient address is Tier 1 or 2

**Solutions:**
1. This is **intentional behavior** for security
2. Use manual transaction flow for Tier 2 addresses
3. Wait for recipient to build reputation to Tier 3
4. Override agent policy (NOT recommended): `AGENT_MIN_TIER = 2` in config

---

## Support & Resources

- **FairScore Documentation**: https://docs.fairscore.io
- **Coldstar GitHub**: https://github.com/ExpertVagabond/coldstar-colosseum
- **Bug Reports**: https://github.com/ExpertVagabond/coldstar-colosseum/issues
- **Discord**: (Coming soon)

---

**Document Version:** 1.0
**Last Updated:** 2026-02-08
**Maintainer:** @buildcoldstar

```
╔═══════════════════════════════════════════════════════════════╗
║  "The most secure cold wallet is one that knows who it's     ║
║   talking to before the signature happens."                   ║
║                                                                ║
║  — Coldstar Team × Purple Squirrel Media                      ║
╚═══════════════════════════════════════════════════════════════╝
```
