# TokenTon26 — AI Track Submission ($8,500 Prize Pool)

> Apply at: https://superteam.fun/earn/listing/tokenton26-ai-track-dollar8500-prize-pool/
> Sponsor: DeAura Capital Group
> Build Phase: February 16 – March 19, 2026
> Winner Announcement: April 2, 2026
> Contact: Telegram @tokenton26

---

## ⚠️ IMPORTANT: Requirements to Address Before Submitting

**Token launch requirement:** Must launch token via DeAura platform
**Volume requirement:** Minimum $200,000 trading volume
**Build deadline:** March 19, 2026 (10 days from today)

### Decision Point

These are significant requirements. Options:
1. **Launch a utility token** for the AI agent swarm (e.g., $SWARM or $CLAW) on DeAura — but $200K volume in <10 days is aggressive
2. **Leverage existing tokens** — $PAW (OpenPaw) already graduated from pump.fun bonding curve, or one of the 10 OpenSeeker agent tokens. Check if DeAura accepts existing tokens or requires new launch on their platform specifically.
3. **Skip this bounty** and focus on Solana Foundation grant + Superteam talent profile (no token requirement)

**Recommendation:** Contact @tokenton26 on Telegram to clarify whether existing tokens qualify or if a new DeAura launch is mandatory. If mandatory new launch required, the $200K volume threshold may be unrealistic in 10 days without significant capital.

---

## Project Name

PSM Neural Swarm — Full-Stack AI Agent Infrastructure for Solana

## Tagline

10 autonomous agents, 200+ tools, pure Rust ML core, air-gapped signing — AI agents that do real things on Solana.

## Live Demo URL

[TO BE ADDED — Deploy a unified dashboard or use existing coldstar.dev + openseeker.pages.dev]

## GitHub Repository

https://github.com/ExpertVagabond (Multiple repos — link to primary showcase repo)

## DeAura Token Launch Link

[TO BE ADDED — Requires DeAura platform token launch]

---

## Project Description

PSM Neural Swarm is a full-stack AI agent infrastructure for Solana, built across 35+ repositories by a solo developer. It combines autonomous multi-agent orchestration, pure Rust machine learning, on-chain program deployment, and air-gapped security into a unified system where AI agents analyze, decide, and execute real Solana transactions.

### The Architecture

**Layer 1: Agent Orchestration**
- **OpenClaw Swarm** — 10 registered agents with tiered model fallbacks (Anthropic Opus → Gemini Flash → Ollama local). Includes specialized agents for software development (6-agent plan/build/test/review cycle), crypto trading (Bankr-powered DeFi across 5 chains), self-healing workflows (antfarm-medic), and gateway relay.
- **Swarm-Rust** — Pure Rust agent fleet (6-crate workspace: core, llm, agents, tools, gateway, cli). Axum HTTP gateway, SQLite memory persistence, TOML-configurable agents.
- **OODA Loop** — Autonomous coding orchestrator with inner loop (code + test + retry) and outer loop (review + fix task generation). Proven convergence in 1 cycle with qwen2.5-coder:14b.

**Layer 2: Neural Intelligence (Pure Rust ML — Zero Unsafe)**
- **PSM Neural Core** — 9-crate workspace, 76 tests, zero unsafe blocks:
  - **Neural MCP Router** — Routes across 10 MCP servers (75 tools, 5 domains) with 9/10 accuracy, self-learning via Micro-LoRA
  - **HNSW vector search** — Pure Rust, cosine/euclidean/dot similarity
  - **GNN** with attention + GRU + LayerNorm
  - **Micro-LoRA** (rank 1-2) + **EWC++** (online continual learning)
  - **PreSignAnalyzer** — Autoencoder anomaly detection for Solana transaction signing
  - **OraclePipeline** — LSTM prediction to Anchor instruction data (49-byte payload for on-chain oracle)
  - **Wallet Profiling** — 16-dim behavioral embeddings, anomaly scoring
  - **WASM target** — 668KB release binary, deployable to Cloudflare Workers edge

**Layer 3: On-Chain Execution**
- **15 Solana Programs** (14 Anchor) — Token Vesting, Escrow, Staking Pool, DAO Voting, Reputation, Orderbook, NFT Mint, Price Feed, Treasury Vault, Multi-sig, and more
- **Coldstar DAO** — veToken governance with epoch rewards, sub-DAO delegation, deployed on devnet
- **Jupiter integration** — DEX swaps with optimal routing
- **Pyth integration** — Real-time price feeds

**Layer 4: Security**
- **Coldstar air-gapped signing** — Rust secure signer, ~100μs plaintext exposure, memory-locked buffers, auto-zeroization
- **ZK proof pipeline** — Schnorr NIZK ownership proofs (Ristretto255), Pedersen range proofs (bit decomposition + CDS OR-proofs), policy compliance proofs, HMAC-SHA256 envelope integrity — no trusted setup, 108 tests
- **PreSign anomaly detection** — Neural autoencoder flags suspicious transactions before signing

**Layer 5: MCP Tool Ecosystem (14+ Servers, 200+ Tools)**

| Server | Tools | Domain |
|--------|-------|--------|
| coldstar-mcp | 13 | Solana/Base wallet, DeFi, reputation |
| solmail-mcp | ~10 | Physical mail via SOL payments |
| cpanel-mcp | 47 | Web infrastructure |
| shopify-mcp | 36 | E-commerce |
| fulfil-mcp | 29 | Fulfillment/ERP |
| ai-music | 8 | Music generation + voice cloning |
| rvc-webui | 12 | Voice model training |
| kino | 8 | Video analysis + audio fingerprinting |
| + 6 more | ~37 | Various domains |

### What Makes This AI — Not Just Automation

1. **Autonomous decision-making:** Agents analyze on-chain state, generate strategies, and execute without human intervention. The OODA Loop proves convergence — tasks complete in 1 cycle.
2. **Self-learning:** Neural MCP Router improves routing accuracy via Micro-LoRA after each interaction. EWC++ prevents catastrophic forgetting.
3. **Predictive capability:** LSTM oracle pipeline generates price predictions formatted as Anchor instruction data for on-chain consumption.
4. **Anomaly detection:** PreSignAnalyzer uses autoencoder reconstruction error + Welford statistics to flag suspicious transactions — the AI catches what rules miss.
5. **Multi-agent coordination:** 10 agents communicate, delegate, and self-heal. The antfarm-medic agent monitors workflow health and restarts failed agents.

---

## AI Architecture Documentation

### Inference Pipeline

```
User/Agent Request
    ↓
Neural MCP Router (semantic embedding → tool selection, 9/10 accuracy)
    ↓
Selected MCP Server (1 of 14, 200+ tools)
    ↓
Tool Execution (on-chain query, DeFi operation, content generation)
    ↓
Result Analysis (GNN attention scoring, anomaly detection)
    ↓
Action Decision (execute / escalate / block)
    ↓
If Solana transaction:
    PreSignAnalyzer (autoencoder anomaly check)
    → Transaction creation
    → [Air-gap QR transfer if high-value]
    → Rust signer (~100μs)
    → Broadcast
```

### Safety Systems

1. **ZK proof verification:** Schnorr ownership + range proofs verified before signing
2. **Anomaly detection:** Neural autoencoder flags out-of-distribution transactions
3. **Policy enforcement:** Transfer limits and allowlists enforced via ZK policy proofs
4. **Air-gap isolation:** High-value transactions require physical human intervention via QR code transfer
5. **Memory-locked signing:** Keys exist in RAM for ~100μs in mlock'd buffers, auto-zeroized
6. **Tiered model fallback:** If primary AI (Opus) is unavailable, agents fall back gracefully (Flash → local Ollama) rather than failing

### Token Utility

[TO BE DEFINED — Depends on DeAura token launch decision]

Potential utility angles:
- **Agent compute credits** — Token required to access swarm compute resources
- **Proof staking** — Stake tokens to unlock higher ZK proof tiers
- **MCP tool access** — Premium tool tiers gated by token holdings
- **DAO governance** — Vote on swarm configuration, model selection, tool additions

---

## Demo Video Script

[TO BE RECORDED — 5 minute Loom/YouTube]

1. **0:00-0:30** — Introduction: "This is PSM Neural Swarm — 10 AI agents, 200+ tools, pure Rust ML, all on Solana"
2. **0:30-1:30** — Show OpenClaw gateway launching, agents registering, model fallback tiers
3. **1:30-2:30** — Demo Neural MCP Router: natural language query → automatic tool selection → Solana balance check + Jupiter swap quote
4. **2:30-3:30** — Show PreSignAnalyzer catching a suspicious transaction (anomaly score spike), then ZK policy proof blocking an out-of-bounds transfer
5. **3:30-4:30** — Demo air-gapped signing flow: transaction built online → QR code → signed offline → broadcast
6. **4:30-5:00** — Show WASM deployment (668KB), on-chain programs on devnet, wrap up with GitHub links

---

## Pitch: Launch Strategy

### Phase 1: Developer Adoption (Weeks 1-4)
- Open-source all agent configurations and MCP server setup guides
- Publish Neural MCP Router as standalone crate on crates.io
- Create "build your own Solana AI agent" tutorial series
- Target: 50 GitHub stars, 10 forks, 5 active contributors

### Phase 2: Agent Economy (Weeks 5-8)
- Deploy agent compute marketplace on devnet
- Enable token-gated MCP tool access
- Launch community bounties for new MCP server integrations
- Target: 100 agents registered, 1,000 daily tool invocations

### Phase 3: Mainnet + Security Audit (Weeks 9-12)
- Security audit of Rust signer and DAO programs (Hacken review from 1st place prize)
- Mainnet deployment of governance contracts
- Agent reputation system live on mainnet
- Target: Production-ready infrastructure for Solana AI agents

---

## Judging Criteria Alignment

### AI Integration & Intelligence ✅
- Neural MCP Router with self-learning (Micro-LoRA)
- PreSign anomaly detection (autoencoder)
- LSTM oracle pipeline for price prediction
- Wallet behavioral profiling (16-dim embeddings)
- GNN with attention for graph-structured data
- All pure Rust, zero unsafe — not wrapper code around OpenAI

### Execution & Technical Quality ✅
- 35+ repositories, all functional
- 15 deployed Solana programs
- 9-crate Rust ML workspace with 76 tests
- npm-published MCP server (coldstar-mcp@0.2.0)
- Colosseum hackathon passed (Project #62)
- WASM compilation to 668KB

### Product Experience & User Value ✅
- Rich terminal TUI with real-time portfolio, price feeds, reputation badges
- One-command agent swarm startup
- Natural language → on-chain action via Neural MCP Router
- Air-gapped signing provides actual security, not theater

### Safety & Guardrails ✅
- ZK proof pipeline (Schnorr, Pedersen, policy proofs)
- Neural anomaly detection on every transaction
- Agent autonomy gradient (capability scales with reputation)
- Physical air-gap for high-value operations
- Memory-locked, auto-zeroizing Rust signer

### Launch Readiness ✅
- Already running, not a prototype
- npm published, devnet deployed, website live
- Clear 12-week roadmap from developer tools → agent economy → mainnet
- Hacken security review (from 1st place prize) provides audit path

---

## Team

**Matthew Karsten** — Founder & Solo Developer
- Purple Squirrel Media LLC
- 1,800+ commits, 320+ projects, 6,800+ Claude Code sessions
- Polyglot: TypeScript, Python, Rust, Go, Ruby
- Colosseum Agent Hackathon: 2 projects passed (#62 Coldstar, #47 SolMail)
- Graveyard Hackathon: 4 submissions (Tribeca DAO, Port Finance, Grape, Parrot TWAP)
- GitHub: github.com/ExpertVagabond
- Twitter: @expertvagabond / @squirrel_eth / @buildcoldstar

## Contact

- **Email:** MatthewKarstenConnects@gmail.com
- **Telegram:** @buildcoldstar
- **Twitter/X:** @buildcoldstar
- **GitHub:** ExpertVagabond

---

*Submission prepared March 2026 for TokenTon26 AI Track via Superteam Earn*
*Sponsor: DeAura Capital Group*
*Prize Pool: $8,500 (1st: $3,000 + $2,500 Hacken review + Bonk Advisory + Buildifi)*
