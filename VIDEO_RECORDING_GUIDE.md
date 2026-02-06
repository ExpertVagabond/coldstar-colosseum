# Coldstar Demo Video - Recording Guide

## 📋 Pre-Recording Checklist

### Equipment Setup:
- [ ] **Screen recording software** installed (OBS Studio, QuickTime, or ScreenFlow)
- [ ] **Microphone** tested (built-in or external)
- [ ] **Quiet environment** (no background noise)
- [ ] **Terminal setup** (iTerm2/Terminal with dark theme, 16pt font)
- [ ] **Screen resolution** set to 1920x1080
- [ ] **Do Not Disturb** enabled (no notifications)

### Software Preparation:
- [ ] Coldstar CLI ready (`cd coldstar && python main.py`)
- [ ] Demo transactions prepared (test data)
- [ ] Browser tabs open: GitHub, demo site, Solana Explorer
- [ ] DEMO_SCRIPT.md open in second monitor/window

### Recording Settings:
- [ ] **Frame rate**: 30 FPS minimum
- [ ] **Audio quality**: 128 kbps or higher
- [ ] **Format**: MP4 (H.264 codec)
- [ ] **Aspect ratio**: 16:9

---

## 🎬 Recording Steps (Follow DEMO_SCRIPT.md)

### Scene-by-Scene Timing:

**Total Duration: 3:00 (180 seconds)**

1. **Opening (0:00-0:15)** - 15 seconds
   - Show Coldstar logo
   - Text overlay: "Coldstar - Air-Gapped Solana Vault"
   - Quick stats flash

2. **Problem Statement (0:15-0:30)** - 15 seconds
   - Split screen or slide showing the challenge
   - Narrate the agent treasury problem

3. **Solution Overview (0:30-0:50)** - 20 seconds
   - Architecture diagram
   - Show the air-gap workflow

4. **USB Creation Demo (0:50-1:10)** - 20 seconds
   - Terminal: flash_usb_tui.py
   - Show progress bars, completion

5. **Jupiter Swap Demo (1:10-1:40)** - 30 seconds
   - MOST IMPORTANT SECTION
   - Show: Create swap online → QR → Sign offline → Broadcast
   - Use screen recording of actual CLI

6. **DAO Governance Demo (1:40-2:00)** - 20 seconds
   - Show multi-sig vault
   - Proposal creation
   - Link to Solana Explorer

7. **Price Feeds Demo (2:00-2:15)** - 15 seconds
   - Vault dashboard
   - USD portfolio valuation

8. **Technical Highlights (2:15-2:35)** - 20 seconds
   - Code snippets scrolling
   - GitHub repo
   - Stats overlay

9. **Differentiation (2:35-2:50)** - 15 seconds
   - Comparison table
   - "Only air-gapped wallet" emphasis

10. **Call to Action (2:50-3:00)** - 10 seconds
    - GitHub repo URL
    - Colosseum project page
    - Social links

---

## 🎤 Narration Tips:

### Voice Recording:
- **Pace**: Moderate (not too fast)
- **Tone**: Professional but enthusiastic
- **Enunciation**: Clear pronunciation of technical terms
- **Pauses**: Brief pauses between sections

### Script Reading:
- Read through 3 times BEFORE recording
- Mark breathing points in script
- Record in segments (can edit together later)
- Option: Record narration separately, overlay on video

### Common Mistakes to Avoid:
- ❌ Speaking too fast (slow down!)
- ❌ Monotone delivery (show enthusiasm!)
- ❌ "Um", "uh", filler words (pause instead)
- ❌ Background noise (test audio first)

---

## 🎥 Recording Options:

### Option 1: All-in-One Recording
**Tools**: OBS Studio
**Method**: Record screen + narration simultaneously
**Pros**: Faster, natural flow
**Cons**: Harder to fix mistakes

### Option 2: Separate Recording + Editing
**Tools**: QuickTime (screen) + Audacity (audio) + iMovie (editing)
**Method**: Record screen footage, record narration separately, combine
**Pros**: Better quality, easier to fix
**Cons**: More time-consuming

### Option 3: Automated Alternative (If No Time)
**Tools**: Screenshots + Online video maker
**Method**: Use our generated screenshots + text overlays
**Pros**: No narration needed
**Cons**: Less engaging

---

## 📝 OBS Studio Setup (Recommended):

### Scene Configuration:

**Scene 1: Full Screen**
- Source: Display Capture (1920x1080)
- Audio: Microphone

**Scene 2: Terminal Focus**
- Source: Window Capture (Terminal)
- Background: Blurred or dark
- Audio: Microphone

**Scene 3: Browser Demo**
- Source: Window Capture (Chrome/Firefox)
- Audio: Microphone

### Recording Settings:
```
Output Mode: Simple
Video Bitrate: 2500 Kbps
Encoder: Software (x264)
Audio Bitrate: 160 Kbps
Recording Format: MP4
Recording Quality: High Quality, Medium File Size
```

### Hotkeys (Set These):
- Start Recording: F9
- Stop Recording: F10
- Pause Recording: F11
- Screenshot: F12

---

## ✂️ Post-Recording Editing:

### Minimal Editing Checklist:
- [ ] Trim dead air at start/end
- [ ] Remove long pauses or mistakes
- [ ] Add text overlays for key stats
- [ ] Add logo at beginning/end
- [ ] Fade in/out for transitions
- [ ] Check audio levels (normalize if needed)

### Text Overlays to Add:
- Opening: "Coldstar - Air-Gapped Solana Vault"
- Throughout: Feature highlights
- End: "GitHub: github.com/ExpertVagabond/coldstar-colosseum"
- End: "Demo: coldstar.dev/colosseum"
- End: "Built for Colosseum Agent Hackathon"

### Free Editing Tools:
- **iMovie** (macOS) - Simple, built-in
- **DaVinci Resolve** (Free) - Professional grade
- **Shotcut** (Free, cross-platform) - Good middle ground

---

## 📤 YouTube Upload Checklist:

### Video Details:
**Title**:
```
Coldstar - Air-Gapped Solana Cold Wallet | Colosseum Agent Hackathon Demo
```

**Description**:
```
Coldstar: The only air-gapped cold wallet built for the Solana agent economy.

🔐 FEATURES:
• Complete network isolation (air-gapped security)
• Jupiter DEX integration (air-gapped swaps)
• Pyth Network price feeds (real-time USD valuation)
• DAO governance with multi-sig vaults
• QR-based transaction signing
• Hardware-grade security at software cost ($10 USB)

💻 TECHNICAL:
• 2 DAO programs deployed on Solana devnet
• 2,500+ lines of production Python code
• Beautiful TUI with Rich library
• Full integration with Solana ecosystem

🔗 LINKS:
Demo: https://coldstar.dev/colosseum
GitHub: https://github.com/ExpertVagabond/coldstar-colosseum
Hackathon Project: https://colosseum.com/agent-hackathon/projects/coldstar-air-gapped-solana-vault-2z9v3x

Built for the Colosseum Agent Hackathon (Feb 2-12, 2026)
Prize Pool: $100,000 USDC

📊 PROGRAM IDs (Devnet):
Coldstar DAO: Ue6Z2MBm7DxR5QTAYRRNsdXc7KBRgASQabA7DJYXeat
Voter Registry: 2ueu2H3tN8U3SWNsQPogd3dWhjnNBXH5AqiZ1H47ViZx

#Solana #ColdWallet #Security #AgentEconomy #Web3 #Colosseum
```

**Tags** (Max 500 chars):
```
Solana, Cold Wallet, Cryptocurrency, Security, Air Gap, DeFi, Jupiter, Pyth Network, DAO, Multi-sig, Agent Economy, Web3, Blockchain, Open Source, Colosseum, Hackathon, Python, TUI, Hardware Wallet
```

**Thumbnail Suggestions**:
- Coldstar logo + "Air-Gapped Security"
- "$10 → $200 Value" text
- "Colosseum Hackathon" badge
- Bright colors (blue/gold) for visibility

**Category**: Science & Technology
**Visibility**: Public
**License**: Standard YouTube License
**Comments**: Enabled
**Age Restriction**: No

### After Upload:
- [ ] Add video to "Colosseum Hackathon" playlist
- [ ] Add end screen with links (GitHub, demo site)
- [ ] Add chapters/timestamps in description
- [ ] Pin comment with upvote link
- [ ] Share on Twitter/X immediately

---

## ⏱️ Timeline Estimate:

- **Preparation**: 30-45 minutes
- **Recording**: 45-60 minutes (multiple takes)
- **Editing**: 30-45 minutes
- **Uploading**: 10-15 minutes
- **Total**: 2-3 hours

---

## 🆘 Troubleshooting:

**Problem**: Audio is too quiet
**Solution**: Increase mic gain, or normalize audio in post

**Problem**: Video file too large (>2GB)
**Solution**: Re-export with lower bitrate (1500 Kbps)

**Problem**: Terminal text hard to read
**Solution**: Increase font size to 18-20pt, use high contrast theme

**Problem**: Recording stutters/lags
**Solution**: Close other apps, lower recording quality slightly

**Problem**: Don't have time for video
**Solution**: Use our screenshot gallery as "visual demo" and focus on written documentation

---

## ✅ Final Quality Check:

Before uploading, verify:
- [ ] Audio is clear and understandable
- [ ] All text overlays are readable
- [ ] Video length is 3:00 or under
- [ ] No personal information visible
- [ ] GitHub and demo URLs are correct
- [ ] Video exports at 1920x1080
- [ ] File size under 2GB

---

**Remember**: A good 3-minute demo is better than a rushed 5-minute demo. Quality over quantity!

Good luck! 🎬🚀
