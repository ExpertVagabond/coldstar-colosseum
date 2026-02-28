# Base Batches 003 — Startup Track Application
## Coldstar: Air-Gapped Cold Wallet for Base

> Copy/paste these fields into the Devfolio form at:
> https://base-batches-startup-track-3.devfolio.co/

---

### Project Name
Coldstar

### Tagline
Air-gapped cold signing for Base — private keys never touch the network.

### Project Description / What are you building?
Coldstar is an air-gapped cold wallet purpose-built for Base. Private keys are generated and stored on a permanently offline device. Transactions are built on an online machine, transferred via QR code to the offline signer, signed in secure memory, and returned via QR for broadcast — the private key never touches a networked device at any point.

The signing core is written in Rust with memory-locked buffers (mlock), Argon2id key derivation, AES-256-GCM encrypted containers, and automatic zeroization. The wallet interface is a Python TUI supporting Base Mainnet and Sepolia testnet, with full EIP-1559 transaction building, ERC-20 token support, and a QR-based air-gap transfer protocol.

Coldstar originally launched as a Solana cold wallet and has been extended to support Base with native secp256k1 ECDSA signing. The same security model — encrypted containers, Rust signer, QR air-gap — now works across both chains.

### Problem it solves
Hardware wallets are the standard for cold storage, but they have fundamental limitations:
- **Closed source** — Ledger's firmware is proprietary; users trust the company, not the code
- **USB/Bluetooth attack surface** — hardware wallets connect to online devices, creating a side-channel attack vector
- **Supply chain risk** — physical devices can be intercepted and tampered with before delivery
- **No Base-specific tooling** — existing cold storage solutions treat Base as an afterthought

Coldstar eliminates these vectors with a true air gap. The signing device is a standard computer running offline — no USB, no Bluetooth, no wireless. Transaction data crosses the gap only as QR codes (optical, unidirectional, human-inspectable). The entire stack is open source and auditable.

For Base specifically, there is no dedicated air-gapped signing tool. MetaMask, Rabby, and even Ledger treat Base as just another EVM chain with no chain-specific optimizations. Coldstar is built for Base from the ground up.

### Technologies Used
- Rust (secure signer: k256, sha3, argon2, aes-gcm, memsec, zeroize)
- Python (CLI: rich, eth-account, web3.py)
- secp256k1 ECDSA (EIP-1559 Type 2 transactions)
- QR code air-gap transfer protocol
- Base L2 (Chain ID 8453 / 84532 Sepolia)

### Links
- **GitHub:** https://github.com/ExpertVagabond/coldstar-colosseum
- **Website:** https://coldstar.dev
- **Base Landing Page:** https://coldstar.dev/base
- **Demo Video:** [TODO: Record and upload to YouTube]

### Video Demo
[TODO: Record 2-3 min screen recording showing:]
1. Create a Base wallet (keygen + encrypted container)
2. Build an unsigned ETH transfer on Sepolia
3. QR air-gap transfer to offline device
4. Sign with Rust signer
5. Broadcast to Base Sepolia

---

## Team Information

### Team Lead
**Matthew Karsten**
- GitHub: [@ExpertVagabond](https://github.com/ExpertVagabond)
- Twitter/X: [@expertvagabond](https://twitter.com/expertvagabond)
- Email: MatthewKarstenConnects@gmail.com
- Role: Solo founder, Purple Squirrel Media LLC

### Company / Organization
Purple Squirrel Media LLC

### Stage
Pre-launch (working product, not yet publicly released)

### Prior Funding
$0 (bootstrapped, qualifies for <$250k requirement)

### How did you hear about Base Batches?
Email from Devfolio

---

## 500-Word Light Paper

### Coldstar: Air-Gapped Cold Signing for Base

**The Problem**

Self-custody on Base today means browser extensions (MetaMask, Rabby) or hardware wallets (Ledger, Trezor). Browser wallets expose private keys in browser memory — a single malicious extension can drain funds. Hardware wallets are better but still connect via USB or Bluetooth, creating electronic side channels. Ledger's closed-source firmware and 2023 recovery service controversy highlighted that users are trusting a company, not verifying security.

For institutional and high-value holders on Base, there is no open-source, air-gapped cold signing solution. This gap is especially problematic as Base grows — over $10B TVL, 100M+ transactions, and increasing institutional interest through Coinbase.

**The Solution**

Coldstar implements true air-gapped cold signing for Base. The architecture separates concerns across two devices:

*Online device (hot):* Builds unsigned EIP-1559 transactions, fetches gas prices and nonces from Base RPC, displays QR codes for transfer.

*Offline device (cold):* Stores encrypted private keys, receives unsigned transactions via QR scan, signs with the Rust secure signer, outputs signed transactions as QR codes.

The signing core is written in Rust for memory safety guarantees. Private keys are stored in AES-256-GCM encrypted containers with Argon2id key derivation (64MB memory cost, 3 iterations). During signing, keys exist only in mlock'd memory pages that are automatically zeroized after use. The secp256k1 implementation uses the k256 crate with constant-time operations to prevent timing attacks.

The QR-based air-gap protocol is deliberately simple: JSON-serialized transaction data encoded as QR codes. This is human-inspectable — users can verify exactly what data crosses the air gap. No USB, no Bluetooth, no NFC, no wireless of any kind.

**Why Base**

Base is the fastest-growing L2 with deep Coinbase integration, making it a natural target for institutional adoption. As onchain treasury management grows, the demand for cold signing infrastructure that matches the security standards of traditional finance will increase. Coldstar provides this without requiring specialized hardware — any two computers, one kept permanently offline, become a cold signing setup.

**Architecture**

The stack is ~18,000 lines across Python and Rust:
- **Rust signer** (1,890 lines): secp256k1 ECDSA, encrypted containers, memory-locked buffers, FFI bindings for Python interop
- **Python CLI** (1,431 lines): EVM wallet management, Base network interaction, EIP-1559 transaction building, QR transfer protocol
- **Chain-agnostic encryption**: Same Argon2id + AES-256-GCM layer encrypts both Ed25519 (Solana) and secp256k1 (Base) keys

**Traction & Roadmap**

Coldstar launched as a Solana cold wallet and was accepted into the Colosseum hackathon. The Base port adds native secp256k1 signing, EIP-1559 transaction support, and Base-specific RPC integration. Near-term roadmap includes Aerodrome DEX integration for air-gapped swaps, ERC-20/ERC-721 token management, and multisig support via Safe contracts.

**Team**

Solo founder (Matthew Karsten, Purple Squirrel Media). Background in travel media and web3 development. Contributor to Solana ecosystem tooling including SolMail MCP and ordinals-mcp.

---

## Submission Checklist
- [ ] Devfolio account created
- [ ] Apply at https://base-batches-startup-track-3.devfolio.co/
- [ ] Paste project info from above
- [ ] Upload demo video to YouTube and add link
- [ ] Add GitHub repo link
- [ ] Add coldstar.dev/base link
- [ ] Submit before March 9, 2026
