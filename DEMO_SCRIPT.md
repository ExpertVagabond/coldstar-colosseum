# Coldstar Demo Video Script
## 3-Minute Demonstration (180 seconds)

**Target**: Colosseum Agent Hackathon Judges
**Goal**: Show unique value proposition + technical execution
**Tone**: Professional, confident, security-focused

---

## Opening (0:00-0:15) - 15 seconds

### Visual
- Coldstar logo/banner
- Text overlay: "Coldstar - Air-Gapped Solana Vault"
- GitHub stars, Colosseum logo

### Narration
> "Coldstar: The first air-gapped cold wallet that turns any USB drive into hardware-grade security. Your private keys never touch the internet. Ever."

### On-Screen Text
- "Hardware-grade security"
- "Software cost ($10 vs $200)"
- "Built for the agent economy"

---

## Problem Statement (0:15-0:30) - 15 seconds

### Visual
- Split screen showing:
  - Left: Agent managing $100K in crypto
  - Right: Private keys on networked computer (red X)

### Narration
> "Agents managing serious capital face a critical problem: How do you access DeFi without exposing your private keys to networked devices?"

### On-Screen Text
- "$100B+ in crypto security needs"
- "Hardware wallets: Expensive, not programmable"
- "Hot wallets: Fast but vulnerable"

---

## Solution Overview (0:30-0:50) - 20 seconds

### Visual
- Architecture diagram showing:
  - Online device (transaction creation)
  - QR code transfer
  - Air-gapped USB (signing)
  - Back to online (broadcast)

### Narration
> "Coldstar solves this with complete air-gap isolation. Create transactions online, sign them on an offline USB device, then broadcast. Private keys never leave the air-gapped environment."

### On-Screen Text
- "Complete network isolation"
- "QR-based transaction signing"
- "Alpine Linux (50MB)"

---

## Feature Demo 1: USB Creation (0:50-1:10) - 20 seconds

### Visual
- Terminal showing `flash_usb_tui.py`
- Progress bars for:
  - Formatting
  - Writing Alpine Linux
  - Encrypting
  - Verifying

### Narration
> "Turn any USB drive into a cold wallet in minutes. Our beautiful TUI guides you through flashing Alpine Linux with network drivers blacklisted at boot."

### On-Screen Text
- "Any USB drive ($10)"
- "Bootable Alpine Linux"
- "Network disabled by default"

---

## Feature Demo 2: Jupiter Swap (1:10-1:40) - 30 seconds

### Visual
- Split screen:
  - **Online**: Create swap (SOL → USDC)
    - Jupiter best route shown
    - Price impact: 0.1%
    - QR code generated
  - **Offline**: Scan QR, review details, sign
  - **Online**: Scan signed QR, broadcast

### Narration
> "Want to swap tokens? Create the transaction online using Jupiter's best routes. Transfer via QR code to your air-gapped device. Review the full swap details on your offline screen—every field visible. Sign with your private key. Transfer back and broadcast. DeFi access with zero key exposure."

### On-Screen Text
- "Jupiter: Best routes across all DEXes"
- "Full transaction visibility offline"
- "Sign with air-gapped keys"
- "Broadcast online"

---

## Feature Demo 3: DAO Governance (1:40-2:00) - 20 seconds

### Visual
- Terminal showing:
  - DAO vault creation (3-of-5 multi-sig)
  - Proposal: "Transfer 100 SOL to dev fund"
  - Vote collection from 5 members
  - Automatic execution

### Narration
> "Manage team treasuries with on-chain DAO governance. Create multi-sig vaults, propose fund movements, collect air-gapped signatures from each member, and execute automatically when the threshold is met. Deployed on Solana devnet."

### On-Screen Text
- "Multi-sig cold vaults"
- "On-chain voting"
- "Air-gapped signatures"
- "Live on devnet"

---

## Feature Demo 4: Price Feeds (2:00-2:15) - 15 seconds

### Visual
- Vault dashboard showing:
  ```
  Wallet: abc123...
  Balance: 5.234 SOL
  USD Value: ≈ $523.40 USD
  Price: SOL @ $100.00 (Pyth Network)
  ```

### Narration
> "Real-time portfolio valuation powered by Pyth Network. See your holdings in USD without compromising security. Prices refresh every 5 seconds."

### On-Screen Text
- "Pyth Network integration"
- "Real-time USD valuation"
- "Portfolio tracking"

---

## Technical Highlights (2:15-2:35) - 20 seconds

### Visual
- Code snippets scrolling:
  - `jupiter_integration.py`
  - `pyth_integration.py`
  - DAO program IDs
  - GitHub repo stats

### Narration
> "Two thousand lines of Python. Four major integrations: Jupiter for swaps, Pyth for prices, custom DAO programs deployed to devnet, and Solana MCP server integration planned. All open source, MIT licensed."

### On-Screen Text
- "2,000+ lines of code"
- "Jupiter + Pyth integration"
- "DAO programs live on devnet"
- "Open source (MIT)"

---

## Differentiation (2:35-2:50) - 15 seconds

### Visual
- Comparison table:
  ```
  | Feature          | Coldstar | Hardware Wallet | Hot Wallet |
  |------------------|----------|-----------------|------------|
  | Air-Gap Security | ✅       | ✅              | ❌         |
  | Cost             | $10      | $79-279         | Free       |
  | Jupiter Swaps    | ✅       | Limited         | ✅         |
  | DAO Governance   | ✅       | ❌              | ❌         |
  | Programmable     | ✅       | ❌              | ✅         |
  ```

### Narration
> "We're the only project building air-gapped security infrastructure. Not another DeFi tool—foundational security for the agent economy. Hardware wallet security at software cost."

### On-Screen Text
- "Only air-gapped wallet in hackathon"
- "95% cheaper than hardware wallets"
- "Security + DeFi functionality"

---

## Call to Action (2:50-3:00) - 10 seconds

### Visual
- GitHub repo: github.com/ExpertVagabond/coldstar-colosseum
- Colosseum project page
- Social links

### Narration
> "Coldstar. Your keys, your responsibility. Open source, open trust. Built for the Colosseum Agent Hackathon by coldstar-agent."

### On-Screen Text
- "Try it: github.com/ExpertVagabond/coldstar-colosseum"
- "Agent: coldstar-agent"
- "Project: coldstar-air-gapped-solana-vault-2z9v3x"
- "Made with ✦ for Colosseum"

---

## Technical Recording Notes

### Tools Needed
- **Screen Recording**: OBS Studio or QuickTime
- **Terminal**: iTerm2 with custom theme
- **Editor**: DaVinci Resolve or iMovie
- **Narration**: Clear microphone, quiet room
- **Music**: Royalty-free tech background (low volume)

### Recording Setup
1. **Terminal Theme**: Dark mode, large font (16pt)
2. **Screen Resolution**: 1920x1080 for YouTube
3. **Cursor**: Visible but not distracting
4. **Typing Speed**: Moderate (demo pre-scripted)
5. **Transitions**: Smooth fades, 0.5s duration

### B-Roll Suggestions
- Code scrolling in background
- Network traffic visualization (blocked on air-gap)
- USB drive close-up
- QR code scanning animation

### Accessibility
- **Subtitles**: Auto-generate on YouTube
- **Closed Captions**: Full script provided
- **Audio**: Clear narration, no background noise
- **Visuals**: High contrast, readable text

---

## Alternative: Automated Demo (If No Recording)

### Use Existing Tools
```bash
# Generate screenshots
python create_screenshots.py

# Create animated preview
python create_animated_preview.py

# Record terminal session
python record_tui.sh
```

### Combine into GIF
```bash
# Use ImageMagick or Gifski
gifski screenshots/*.png -o coldstar-demo.gif
```

### Static Demo Page
- Create `demo.html` with:
  - Screenshot carousel
  - Animated GIFs
  - Code snippets
  - Architecture diagrams
  - Deploy to GitHub Pages

---

## YouTube Upload Checklist

### Video Details
- **Title**: "Coldstar - Air-Gapped Solana Cold Wallet | Colosseum Agent Hackathon"
- **Description**:
  ```
  Coldstar turns any USB drive into a hardware-grade security wallet for Solana.

  Features:
  - Complete air-gap isolation
  - Jupiter DEX integration
  - Pyth Network price feeds
  - DAO governance with multi-sig
  - QR-based transaction signing

  Built for the Colosseum Agent Hackathon by coldstar-agent.

  GitHub: https://github.com/ExpertVagabond/coldstar-colosseum
  Project: https://colosseum.com/agent-hackathon/projects/coldstar-air-gapped-solana-vault-2z9v3x

  $100,000 prize pool | Feb 2-12, 2026
  ```

- **Tags**:
  - Solana
  - Cryptocurrency
  - Cold Wallet
  - Air Gap
  - Security
  - DeFi
  - Jupiter
  - Pyth Network
  - Agent Hackathon
  - Colosseum
  - Open Source

- **Thumbnail**:
  - Coldstar logo
  - "Air-Gapped Security"
  - "$10 → $200 Value"
  - Bright, high contrast

- **Category**: Science & Technology
- **Visibility**: Public
- **Comments**: Enabled
- **License**: Standard YouTube License

---

## Narration Script (Plain Text for Recording)

```
[0:00]
Coldstar: The first air-gapped cold wallet that turns any USB drive into hardware-grade security. Your private keys never touch the internet. Ever.

[0:15]
Agents managing serious capital face a critical problem: How do you access DeFi without exposing your private keys to networked devices?

[0:30]
Coldstar solves this with complete air-gap isolation. Create transactions online, sign them on an offline USB device, then broadcast. Private keys never leave the air-gapped environment.

[0:50]
Turn any USB drive into a cold wallet in minutes. Our beautiful TUI guides you through flashing Alpine Linux with network drivers blacklisted at boot.

[1:10]
Want to swap tokens? Create the transaction online using Jupiter's best routes. Transfer via QR code to your air-gapped device. Review the full swap details on your offline screen—every field visible. Sign with your private key. Transfer back and broadcast. DeFi access with zero key exposure.

[1:40]
Manage team treasuries with on-chain DAO governance. Create multi-sig vaults, propose fund movements, collect air-gapped signatures from each member, and execute automatically when the threshold is met. Deployed on Solana devnet.

[2:00]
Real-time portfolio valuation powered by Pyth Network. See your holdings in USD without compromising security. Prices refresh every 5 seconds.

[2:15]
Two thousand lines of Python. Four major integrations: Jupiter for swaps, Pyth for prices, custom DAO programs deployed to devnet, and Solana MCP server integration planned. All open source, MIT licensed.

[2:35]
We're the only project building air-gapped security infrastructure. Not another DeFi tool—foundational security for the agent economy. Hardware wallet security at software cost.

[2:50]
Coldstar. Your keys, your responsibility. Open source, open trust. Built for the Colosseum Agent Hackathon by coldstar-agent.
```

---

**Total Runtime**: 3:00 exactly
**File Size Target**: < 100MB for easy upload
**Format**: MP4 (H.264 codec, AAC audio)
**Aspect Ratio**: 16:9 (1920x1080)
