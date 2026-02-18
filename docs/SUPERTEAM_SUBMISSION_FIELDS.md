# Fairathon Submission -- Copy-Paste Guide

> Open https://superteam.fun/earn/listing/fairathon/ and paste these into each field.
>
> **Deadline:** March 1, 2026
> **Winner Announcement:** March 15, 2026
> **Prize:** 5,000 USDC (futarchy vote by FAIR token holders on top 6 finalists -> top 3 -> winner)
> **Bonus:** 3 months free FairScale Pro API access ($500/month value) for top 6 finalists
> **Legends.fun:** Top 10 leaderboard earns DePitch Academy Pass + 50% FairScale Pro discount

---

## Field 1: Live Platform URL
*(Required — "A working, public link to your live platform URL")*

```
https://coldstar.dev/colosseum
```

---

## Field 2: GitHub Repository
*(Required — "Repository pushed to FairScale's GitHub organization with README and setup instructions")*

```
https://github.com/ExpertVagabond/coldstar-colosseum
```

**NOTE:** The listing says the repo must be "pushed to FairScale's GitHub organization." Check if FairScale has a GitHub org you need to fork into (e.g., github.com/fairscale-xyz/coldstar-colosseum). If so, fork the repo there first and submit that URL instead. If unclear, ask in their Telegram support channel before submitting.

---

## Field 3: Demo Video
*(Required — "YouTube/Loom, maximum 5 minutes")*

```
[TO BE ADDED — Record 5-min Loom/YouTube first]
```

**Recording checklist for the demo video:**
1. Show the Coldstar CLI launching (main.py TUI menu)
2. Walk through a FairScore reputation lookup (menu option F)
3. Demo a Tier 1 HARD BLOCK — attempt to send to a low-reputation address
4. Demo a Tier 2 SOFT WARNING with confirmation prompt
5. Demo a Tier 3+ GREEN LIGHT clean send flow
6. Show Jupiter swap with deployer address screening
7. Show the vault dashboard with reputation badges
8. Briefly show the air-gap QR code flow (create unsigned TX -> sign offline -> broadcast)
9. End with GitHub repo + coldstar.dev/colosseum link

---

## Field 4: Pitch Deck / Business Documentation
*(Required — "Business viability materials")*

```
https://expertvagabond.github.io/coldstar-colosseum/docs/pitch-deck.html
```

Alternative: Upload a PDF directly if the form supports file upload.

**Business viability talking points to cover in the deck:**
- **Problem:** Cold wallets are secure but blind — no reputation context on recipients
- **Target Audience:** Solana power users, DAOs managing treasuries, AI agent operators
- **Revenue Model:** Freemium CLI (free) + Premium API tier for institutional users + DAO treasury management fees
- **User Acquisition:** Solana developer community -> crypto security forums -> hardware wallet users
  - First 100: Colosseum hackathon community + FairScale ecosystem
  - First 1,000: X/Twitter launch campaign + Solana Discord seeding
  - First 10,000: Integration partnerships with Jupiter, Squads, Meteora
- **Demand Evidence:** Only cold wallet on any chain with on-chain reputation gating

---

## Field 5: Project's X/Twitter Account
*(Required — "Include tweets and threads plus traction evidence like user testimonials, analytics screenshots")*

```
https://x.com/buildcoldstar
```

**What to include alongside this URL:**
- Link to the launch tweet thread (see docs/LAUNCH_TWEETS.md for draft)
- Screenshots of tweet engagement metrics
- Any retweets/quotes from Solana ecosystem accounts

---

## Field 6: Tweet/Thread Link
*(If the form has a separate field for specific tweets/threads)*

```
[TO BE ADDED — Post the launch thread from docs/LAUNCH_TWEETS.md first, then paste link here]
```

---

## Field 7: Team Information
*(Required — "Names, roles, contact details, and relevant prior experience")*

```
@buildcoldstar — Solo Founder & Full-Stack Developer

GitHub: @ExpertVagabond
Twitter/X: @buildcoldstar
Email: MatthewKarstenConnects@gmail.com
Built Coldstar as a solo developer during the 10-day Colosseum Agent Hackathon sprint (Project #62, submitted as Agent #127). Deep Solana ecosystem experience building with Jupiter, Pyth, Anchor, SPL tokens, and MCP agent integrations. Polyglot developer shipping production code in Python, TypeScript, Rust, Ruby, and Go. Track record of rapid execution — Coldstar went from zero to live deployment with FairScore integration, Jupiter swaps, Pyth price feeds, QR-code air-gap signing, and a Rich TUI dashboard in under two weeks.
```

---

## Field 8: FairScore Integration Description
*(Required — "Brief description of FairScore integration and why it matters")*

```
Coldstar integrates FairScore as a CORE GATING MECHANISM for every outbound transaction — not a badge or afterthought. Every transfer queries the FairScale API (GET /score?wallet=<address> with fairkey auth header) BEFORE the transaction can cross the air gap for offline signing.

WHY IT MATTERS: Cold wallets protect private keys but are completely blind to who you're sending to. Once a transaction crosses the air gap and gets signed offline, it's irreversible. FairScore at the air-gap checkpoint is uniquely impactful — it's the last line of defense before an irrevocable signature.

6 INTEGRATION POINTS:

1. TRANSACTION GATING (Primary): Bronze tier (FairScore <20) = HARD BLOCK, transaction rejected before QR code generation. Silver tier (20-39) = SOFT WARNING requiring explicit user confirmation. Gold/Platinum/Diamond = green light. This runs on every outbound transfer in create_unsigned_transaction().

2. DYNAMIC TRANSFER LIMITS: Transfer caps scale with recipient reputation tier — Bronze: 0 SOL (blocked), Silver: 10 SOL, Gold: 100 SOL, Platinum: 500 SOL, Diamond: unlimited. Enforced at transaction preparation.

3. DAO GOVERNANCE WEIGHTING: Multi-sig proposal vote weight is influenced by voter's FairScore tier. Tier 5 gets 2x multiplier, Tier 1 cannot vote. Prevents Sybil attacks on governance.

4. JUPITER SWAP SCREENING: Token deployer/contract addresses checked for reputation before creating swap transactions. Low-tier token contracts trigger warnings to protect against honeypot tokens and rug pulls.

5. VAULT DASHBOARD BADGES: Reputation tier badges displayed alongside portfolio balances in the Rich TUI dashboard. Color-coded (red/yellow/green/cyan/magenta) with score and tier info for all displayed addresses.

6. MCP AGENT GATES: AI agents get transaction autonomy proportional to their FairScore — Tier 3+ can execute, Tier 1-2 blocked. Prevents compromised agents from sending to malicious addresses.

IMPLEMENTATION:
- src/fairscore_integration.py — FairScoreClient class (341 lines): API client, tier mapping, risk assessment, transaction blocking, transfer limits, reputation badges, tier legend display
- config.py — FAIRSCORE_API_URL, FAIRSCORE_API_KEY, FAIRSCORE_ENABLED, FAIRSCORE_MIN_TIER configuration
- main.py — 7 integration points: wallet status display, create_unsigned_transaction() gating, check_fairscore_reputation() lookup, cleanup
- docs/fairscale-openapi.yaml — Full OpenAPI 3.0 spec for /score, /fairScore, /walletScore endpoints

TECHNICAL DETAILS:
- Real FairScale API at https://api2.fairscale.xyz with fairkey header authentication
- Maps API string tiers (bronze/silver/gold/platinum) to internal 1-5 numeric system
- Score-based fallback when string tier is missing (0-19=Tier1, 20-39=Tier2, 40-59=Tier3, 60-79=Tier4, 80-100=Tier5)
- 5-minute TTL response cache to minimize API calls while keeping data fresh
- Graceful degradation: when API is unreachable, falls back to configurable default tier (default: Tier 3)
- Air-gap device NEVER contacts FairScore — all checks happen on the online device before QR code generation, preserving complete offline isolation

This is the ONLY cold wallet on Solana (or any chain) that integrates on-chain reputation into the transaction signing flow.
```

---

## Field 9: User Count / Traction Evidence
*(Required — "Active marketing, user testimonials, waitlists, partnerships, user metrics")*

```
Coldstar launched as Colosseum Agent Hackathon Project #62 (submitted as Agent #127) and is live at coldstar.dev. The project has a public GitHub repository at github.com/ExpertVagabond/coldstar-colosseum.

As a cold wallet CLI tool targeting security-conscious Solana users, traction is measured in code quality, ecosystem integration depth, and community engagement rather than traditional DAU metrics:

- 1,400+ lines of production Python across 13 source modules
- 5 protocol integrations: Jupiter (swaps), Pyth (price feeds), FairScale (reputation), Squads (multi-sig), Meteora (liquidity)
- Full air-gap signing flow with QR code transfer between online and offline devices
- Rich TUI dashboard with real-time portfolio, price feeds, and reputation badges
- OpenAPI 3.0 documentation for FairScale API integration
- Active on X/Twitter: @buildcoldstar with Solana ecosystem engagement

User acquisition strategy: Solana developer community first (hackathon exposure) -> crypto security forums and cold wallet communities -> institutional DAO treasury managers needing reputation-gated signing.
```

---

## Field 10: Analytics Screenshots
*(If the form requests visual evidence of traction)*

```
[TO BE ADDED — Capture and upload the following:]
1. GitHub repository insights (traffic, clones, stars)
2. coldstar.dev analytics (page views, unique visitors)
3. Tweet engagement metrics from launch thread
4. Any Colosseum hackathon upvote/view counts
```

---

## Field 11: Legends.fun Product Page URL
*(Required -- "Product page URL with demo video and founder's card, using invite code FAIRAT")*

```
[TO BE ADDED -- Create product listing at https://legends.fun first]
```

**Steps to create:**
1. Visit https://legends.fun
2. Connect Solana wallet
3. Use invite code: FAIRAT
4. Create product page:
   - Name: Coldstar
   - Description: The only air-gapped Solana cold wallet with FairScore reputation gating. Every transaction is checked against on-chain reputation before crossing the air gap for offline signing.
   - Demo video: Link to YouTube upload
   - Category: Security / Wallet / DeFi Infrastructure
5. Create founder's card with @buildcoldstar profile
6. Share and engage for leaderboard ranking

**Why this matters:** Top 10 leaderboard = DePitch Academy Pass + 50% FairScale Pro discount. This is separate from the $5K USDC prize but increases visibility with judges.

---

## Field 12: Telegram Contact Link
*(Required -- "Telegram contact link")*

```
https://t.me/buildcoldstar
```

**NOTE:** Ensure @buildcoldstar is registered on Telegram. If not, create the account or use an existing handle. This is how judges and FairScale team will reach out directly.

---

## Pre-Submission Checklist

**Critical Path (must complete before March 1):**
- [ ] **FairScale API key** obtained from https://sales.fairscale.xyz/ and tested with real API calls
- [ ] **Legends.fun product page** created with invite code FAIRAT, demo video, and founder's card
- [ ] **Demo video** uploaded to YouTube (existing videos in videos/ dir, or record fresh using script in grants/COLDSTAR-FAIRSCALE-SUBMISSION.md Section 7)
- [ ] **Launch tweet thread** posted from @buildcoldstar (draft ready in docs/LAUNCH_TWEETS.md)
- [ ] **Telegram contact** set up as @buildcoldstar on Telegram
- [ ] **FairScale GitHub org** -- confirm with team in Telegram (https://t.me/+XF23ay9aY1AzYzlk or DM https://t.me/zkishann) whether repo must be forked into their org

**Important but not blocking:**
- [ ] **Analytics screenshots** captured after tweet thread gets engagement
- [ ] **Pitch deck** finalized (docs/pitch-deck.html exists, review for completeness)
- [ ] **Join FairScale Telegram** community for visibility: https://t.me/+XF23ay9aY1AzYzlk
- [ ] All form fields above filled in with final URLs
- [ ] Final review of all fields before clicking Submit

---

## Judging Criteria Reference

| Criterion | Weight | Coldstar Strength | Action Needed |
|-----------|--------|-------------------|---------------|
| FairScore Integration | 30% | 6 integration points, core gating mechanism at air-gap boundary | READY -- verify with real API key |
| Technical Quality | 25% | Production Python (341-line module), Rich TUI, OpenAPI spec, graceful degradation | READY |
| Traction & Users | 20% | Hackathon launch, public repo, live site | POST tweet thread, create Legends.fun page |
| Business Viability | 15% | Clear problem/solution, revenue path, competitive analysis | Review pitch deck |
| Team Quality | 10% | Solo full-stack dev, 10-day build sprint, polyglot stack | READY |

**Priority order for remaining work:**
1. Get FairScale API key (blocks testing)
2. Post tweet thread from @buildcoldstar (builds traction)
3. Create Legends.fun listing with FAIRAT code (required field)
4. Upload demo video to YouTube (required field)
5. Set up Telegram contact (required field)
6. Capture analytics screenshots (evidence of traction)
7. Confirm GitHub org requirement with FairScale team
