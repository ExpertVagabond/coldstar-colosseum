# 💎 Coldstar - Air-Gapped Solana Vault

<p align="center">
  <img src="https://img.shields.io/badge/Solana-14F195?style=for-the-badge&logo=solana&logoColor=white" alt="Solana"/>
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="MIT License"/>
  <img src="https://img.shields.io/badge/Security-Air--Gapped-red?style=for-the-badge" alt="Air-Gapped"/>
  <img src="https://img.shields.io/badge/FairScore-Reputation_Gating-ff00ff?style=for-the-badge" alt="FairScore"/>
</p>

<p align="center">
  <strong>Hardware-grade security meets reputation intelligence. FairScore-gated transactions on Solana.</strong>
</p>

<p align="center">
  <a href="#-features">Features</a> •
  <a href="#-fairscore-integration">FairScore</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-demo">Demo</a> •
  <a href="#-colosseum-hackathon">Hackathon</a>
</p>

---

## 🎯 What is Coldstar?

**Coldstar** turns any **$10 USB drive** into a **$200 hardware wallet** with complete air-gap isolation for Solana.

**The Problem**: Agents managing serious capital need both security AND DeFi access. Hardware wallets are expensive and not programmable. Hot wallets are fast but vulnerable.

**The Solution**: Air-gapped cold wallet + online DeFi integration = best of both worlds.

```
Create transactions online → Sign on air-gapped USB → Broadcast
                           ↓
              Private keys NEVER touch the network
```

---

## 🛡️ FairScore Integration

**Coldstar is the only cold wallet that checks counterparty reputation before every transaction.**

Every outbound transfer is gated by [FairScale's FairScore API](https://fairscale.xyz) — a real-time reputation score (0-100) for any Solana wallet.

| Recipient Tier | FairScore | Action | Transfer Limit |
|---------------|-----------|--------|----------------|
| 🔴 Bronze | 0-19 | **HARD BLOCK** | Blocked |
| 🟡 Silver | 20-39 | **SOFT WARNING** | 10 SOL max |
| 🟢 Gold | 40-59 | Proceed | 100 SOL max |
| 🔵 Platinum | 60-79 | Proceed | 500 SOL max |
| 🟣 Diamond | 80-100 | Proceed | Unlimited |

**6 Integration Points:**
1. **Transaction Gating** — Block/warn before air-gap crossing
2. **Dynamic Transfer Limits** — Reputation-scaled amounts
3. **DAO Governance** — Vote weight by FairScore
4. **Jupiter Swap Screening** — Token contract reputation
5. **Vault Dashboard** — Reputation badges in portfolio view
6. **MCP Agent Gates** — Autonomy gradient for AI agents

> *"The last checkpoint before the point of no return."*

**Live API Example (Jupiter Wallet):**
```
FairScore: 34.2/100 | Tier: Silver | Badges: LST Staker, SOL Maxi
Action: ⚠️ WARNING — Confirm to proceed
```

📖 [Full Integration Documentation →](docs/FAIRSCORE_INTEGRATION.md)

---

## ✨ Features

### 🔐 Air-Gap Security
- **Private keys generated offline** on air-gapped device
- **Alpine Linux** with network drivers blacklisted at boot
- **USB cold wallet** - any drive becomes hardware-grade security
- **QR code signing** - transfer transactions without file copying

### 💱 DeFi Integration
- **Jupiter DEX** - Best routes across all Solana DEXes
- **Pyth Network** - Real-time price feeds and USD portfolio valuation
- **SPL Tokens** - Support for SOL, USDC, USDT, BONK, JUP, RAY
- **Air-gapped swaps** - Create swap online, sign offline, broadcast

### 🛡️ Reputation Gating (FairScore)
- **FairScale API** - Real-time wallet reputation scoring (0-100)
- **Transaction blocking** - Bronze tier addresses hard-blocked
- **Soft warnings** - Silver tier requires explicit confirmation
- **Dynamic limits** - Transfer caps scaled by counterparty reputation
- **Badge display** - LST Staker, SOL Maxi, Early Adopter badges shown

### 🏛️ DAO Governance
- **Multi-sig vaults** - M-of-N signatures for fund movements
- **On-chain voting** - Proposal creation and execution
- **Air-gapped approval** - Each member signs with cold wallet
- **Deployed on devnet** - Live DAO programs ready to use

### 🎨 Beautiful Interface
- **Modern TUI** - Rich terminal interface with progress bars
- **Vault dashboard** - Portfolio tracking with real-time prices
- **USB flashing tool** - Guided setup with visual feedback
- **Companion PWA** - Mobile-friendly web app for online operations

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/ExpertVagabond/coldstar-colosseum
cd coldstar-colosseum

# Install dependencies
pip install -r local_requirements.txt

# Run the CLI
python main.py
```

### Create Your First Cold Wallet

```bash
# 1. Flash USB drive (requires root)
sudo python flash_usb_tui.py

# 2. Boot from USB on air-gapped device
#    Private key generated offline

# 3. Use Coldstar CLI for operations
python main.py
```

---

## 🏗️ Architecture

### Air-Gapped Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                    ONLINE DEVICE                            │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Coldstar CLI                                       │    │
│  │  • Check balance (Solana RPC)                      │    │
│  │  • Get prices (Pyth Network)                       │    │
│  │  • Create unsigned transactions                    │    │
│  │  • Query Jupiter routes                            │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                              │
                    QR Code / USB Transfer
                              │
┌─────────────────────────────────────────────────────────────┐
│                  OFFLINE DEVICE (Air-Gapped)                │
│  ┌────────────────────────────────────────────────────┐    │
│  │  USB Cold Wallet (Alpine Linux)                    │    │
│  │  • Private key storage (encrypted)                 │    │
│  │  • Transaction signing                             │    │
│  │  • User verification screen                        │    │
│  │  • ZERO network access                             │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Layer | Technology |
|-------|------------|
| **OS** | Alpine Linux (minimal, <50MB) |
| **Language** | Python 3.11+ |
| **UI** | Rich (beautiful terminal UI) |
| **Blockchain** | Solders (Solana Rust SDK bindings) |
| **DEX** | Jupiter Aggregator API |
| **Oracles** | Pyth Network Hermes API |
| **Reputation** | FairScale FairScore API |
| **Programs** | Anchor (DAO governance) |

---

## 📊 Comparison

| Feature | Coldstar | Hardware Wallet | Hot Wallet |
|---------|----------|-----------------|------------|
| **Air-Gap Security** | ✅ Yes | ✅ Yes | ❌ No |
| **Cost** | $10 | $79-279 | Free |
| **Open Source** | ✅ Yes | ❌ No | Varies |
| **DAO Governance** | ✅ Yes | ❌ No | ❌ No |
| **Jupiter Swaps** | ✅ Yes | Limited | ✅ Yes |
| **Pyth Prices** | ✅ Yes | ❌ No | ✅ Yes |
| **Reputation Gating** | ✅ FairScore | ❌ No | ❌ No |
| **Programmable** | ✅ Yes | ❌ No | ✅ Yes |
| **Agent-Friendly** | ✅ Yes | ❌ No | ⚠️ Risky |

**Result**: 95% cheaper than hardware wallets with more features

---

## 🎬 Demo

### 📸 Screenshots

**Live TUI Gallery:** [View All Screenshots →](./screenshots/index.html)

<table>
  <tr>
    <td width="50%">
      <img src="https://expertvagabond.github.io/coldstar-colosseum/screenshots/flash_usb_preview.html" alt="USB Flashing Interface" />
      <p align="center"><strong>USB Flashing Interface</strong></p>
    </td>
    <td width="50%">
      <img src="https://expertvagabond.github.io/coldstar-colosseum/screenshots/vault_dashboard_preview.html" alt="Vault Dashboard" />
      <p align="center"><strong>Portfolio Dashboard</strong></p>
    </td>
  </tr>
</table>

**Interactive Demos:**
- 🎥 [Animated USB Flashing](https://expertvagabond.github.io/coldstar-colosseum/screenshots/flash_usb_animated.html) - Watch the full flashing process (20s)
- 📊 [Vault Dashboard](https://expertvagabond.github.io/coldstar-colosseum/screenshots/vault_dashboard_preview.html) - Portfolio management interface

### Jupiter Swap (Air-Gapped)

```bash
# Online device: Create swap
python main.py
> J. Jupiter Swap
> From: SOL
> To: USDC
> Amount: 1.0
# → Creates unsigned transaction

# Transfer to air-gapped USB via QR code

# Offline device: Review and sign
coldstar sign-transaction
# → Full swap details visible
# → Sign with private key

# Transfer back and broadcast
python main.py
> 4. Broadcast Signed Transaction
# → Swap executed!
```

### Portfolio Dashboard

```
╔══════════════════════════════════════════════════════════╗
║                    WALLET STATUS                         ║
╠══════════════════════════════════════════════════════════╣
║  Address:  abc123...xyz789                               ║
║  Balance:  5.2341 SOL                                    ║
║  USD Value: ≈ $523.41 USD (SOL @ $100.00)               ║
║  Source:   Pyth Network (live)                           ║
╚══════════════════════════════════════════════════════════╝
```

---

## 🏆 Colosseum Agent Hackathon

**Built for**: [Colosseum Agent Hackathon](https://colosseum.com/agent-hackathon)
**Agent**: coldstar-final (ID: 127)
**Prize Pool**: $100,000 USDC
**Dates**: Feb 2-12, 2026

### Why Coldstar Wins

1. **Unique Category** - Only air-gapped wallet in hackathon
2. **Complete Solution** - Works end-to-end with beautiful UX
3. **Real Problem** - Agents managing billions need secure key storage
4. **DeFi Integration** - Not just secure storage, full functionality
5. **Open Source** - Community can audit and contribute

### Deployed Infrastructure

**DAO Programs on Devnet**:
- Coldstar DAO: `Ue6Z2MBm7DxR5QTAYRRNsdXc7KBRgASQabA7DJYXeat`
- Voter Stake Registry: `2ueu2H3tN8U3SWNsQPogd3dWhjnNBXH5AqiZ1H47ViZx`

[View on Solana Explorer →](https://explorer.solana.com/address/Ue6Z2MBm7DxR5QTAYRRNsdXc7KBRgASQabA7DJYXeat?cluster=devnet)

---

## 📚 Documentation

- **[Demo Walkthrough](DEMO_WALKTHROUGH.md)** - Complete product demonstration
- **[TUI Guide](TUI_GUIDE.md)** - Terminal UI documentation
- **[Deployed Programs](DEPLOYED_PROGRAMS.md)** - DAO contracts on devnet
- **[MCP Integration](MCP_INTEGRATION.md)** - Hot+cold wallet architecture
- **[Hackathon Strategy](HACKATHON_STRATEGY.md)** - Competition analysis
- **[Submission Checklist](SUBMISSION_CHECKLIST.md)** - Final preparation
- **[Technical Whitepaper](whitepaper.md)** - Deep dive

---

## 🛠️ Development

### Project Structure

```
coldstar-colosseum/
├── main.py                    # Main CLI (1300+ lines)
├── src/
│   ├── jupiter_integration.py # DEX swap integration
│   ├── pyth_integration.py    # Price feed integration
│   ├── fairscore_integration.py # FairScore reputation gating
│   ├── wallet.py              # Keypair management
│   ├── transaction.py         # TX creation/signing
│   ├── network.py             # Solana RPC client
│   ├── usb.py                 # USB device management
│   └── ui.py                  # Beautiful TUI components
├── flash_usb_tui.py           # USB flashing interface
├── vault_dashboard_tui.py     # Portfolio dashboard
├── companion-app/             # PWA for online operations
└── mcp-server/                # Solana MCP integration
```

### Build from Source

```bash
# Install dependencies
pip install rich questionary solana solders pynacl httpx aiofiles base58 qrcode textual

# Or use project file
pip install -e .

# Run tests
python test_transaction.py

# Build ISO (for USB flashing)
python flash_usb.py
```

---

## 🔒 Security Model

### Threat Model

**Adversary**: Nation-state level (NSA, FSB)
**Assumptions**: Online device is compromised
**Guarantee**: Private keys remain secure

### Attack Surface Analysis

| Attack | Vulnerability | Mitigation |
|--------|---------------|------------|
| Private Key Exposure | ❌ IMPOSSIBLE | Air-gapped |
| Transaction Tampering | ✅ DETECTED | Signature fails |
| Balance Spoofing | ⚠️ POSSIBLE | Verify on explorer |
| Denial of Service | ⚠️ POSSIBLE | Multiple RPCs |

### Security Features

- ✅ Network drivers blacklisted at OS level
- ✅ Transaction review on offline screen
- ✅ User verification before signing
- ✅ Encrypted USB storage
- ✅ Open source code (community audit)

---

## 🌟 Use Cases

### 1. Agent Treasury Management
**Problem**: Agents managing $100K+ in crypto assets
**Solution**: DAO-governed cold vault with air-gapped signing
**Security**: Private keys never on networked servers

### 2. High-Value Individual Holdings
**Problem**: Don't want to spend $200 on hardware wallet
**Solution**: $10 USB drive + Coldstar = same security
**Savings**: 95% cost reduction

### 3. Team Multi-Sig Wallets
**Problem**: Need M-of-N signatures for fund movements
**Solution**: Each member uses Coldstar for offline signing
**Benefit**: Complete audit trail on-chain

### 4. DeFi Access from Cold Storage
**Problem**: Want to swap tokens but keep keys offline
**Solution**: Create swap on online device, sign offline
**Result**: DeFi functionality + hardware-level security

---

## 🤝 Integration Partners

Coldstar integrates with:
- **FairScale** - Wallet reputation scoring and transaction gating
- **Jupiter** - DEX aggregation for best swap routes
- **Pyth Network** - Real-time price feeds
- **Solana MCP Server** - Hot wallet operations
- **SAID Protocol** - Agent identity verification
- **AgentVault** - Agent economy escrow

---

## 📈 Roadmap

### Phase 1: Core Features ✅
- [x] Air-gapped USB wallet creation
- [x] QR code transaction signing
- [x] Jupiter DEX integration
- [x] Pyth price feeds
- [x] DAO governance programs
- [x] FairScore reputation gating

### Phase 2: Enhanced Security (In Progress)
- [ ] Hardware key import/export (BIP39)
- [ ] Multi-device multi-sig
- [ ] Encrypted USB backup
- [ ] Yubikey 2FA integration

### Phase 3: Agent Ecosystem (Planned)
- [ ] REST API for agent integration
- [ ] Webhook notifications
- [ ] Scheduled transactions
- [ ] Auto-rebalancing with governance

### Phase 4: Enterprise (Future)
- [ ] Corporate treasury management
- [ ] Compliance reporting
- [ ] Custom approval workflows
- [ ] HSM integration

---

## 🙏 Contributing

We welcome contributions! Here's how:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open a Pull Request

**Security Issues**: Email security@coldstar.dev (or open a private issue)

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

---

## 🔗 Links

- **GitHub**: [ExpertVagabond/coldstar-colosseum](https://github.com/ExpertVagabond/coldstar-colosseum)
- **Hackathon Project**: [coldstar-air-gapped-solana-vault-2z9v3x](https://colosseum.com/agent-hackathon/projects/coldstar-air-gapped-solana-vault-2z9v3x)
- **Forum**: Search "coldstar-agent"
- **DAO Explorer**: [Solana Explorer](https://explorer.solana.com/address/Ue6Z2MBm7DxR5QTAYRRNsdXc7KBRgASQabA7DJYXeat?cluster=devnet)

---

## 💬 Community

**X**: [@buildcoldstar](https://x.com/buildcoldstar) | STIE Member
**STIE Member** | [chainlabs.uno](https://chainlabs.uno)
**Hackathons**: Colosseum Agent Hackathon (Project #62) + FairScale Fairathon

<p align="center">
  <strong>Your keys, your responsibility. Open source, open trust.</strong>
  <br><br>
  Made with ✦ for the Solana Agent Economy
</p>

---

## 🎯 Quick Links

| Resource | Link |
|----------|------|
| **Demo Page** | [Live Demo Site](https://expertvagabond.github.io/coldstar-colosseum/) |
| **Screenshots** | [TUI Gallery](./screenshots/index.html) |
| **FairScore Docs** | [Integration Guide](docs/FAIRSCORE_INTEGRATION.md) |
| **Documentation** | [/docs](./DEMO_WALKTHROUGH.md) |
| **Forum Posts** | [Coldstar Introduction](https://colosseum.com/agent-hackathon/) |
| **DAO Programs** | [Devnet Explorer](https://explorer.solana.com/?cluster=devnet) |

---

**Star ⭐ this repo if you find it useful!**
