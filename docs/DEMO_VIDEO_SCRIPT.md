# Coldstar Demo Video Recording Script

**Duration:** 5 minutes maximum
**Tool:** Loom or QuickTime screen recording
**Audience:** Colosseum Agent Hackathon judges
**Focus:** FairScore reputation integration (this is what differentiates the entry)

---

## Pre-Recording Setup (Do This Before You Hit Record)

### Terminal Setup
- Use iTerm2 or Terminal.app with a dark theme
- Font size: **16pt minimum** (Loom compresses, small text becomes unreadable)
- Terminal width: **120 columns**, height: **40 rows**
- Clear scrollback: `Cmd+K`

### Screen Settings
- Resolution: 1920x1080 (if Retina, set Loom to capture at 1080p)
- Hide desktop icons, close all other apps
- Disable notifications: `System Settings > Focus > Do Not Disturb`
- Hide the macOS Dock: `Cmd+Option+D`

### Environment Prep
```bash
cd /Volumes/Virtual\ Server/projects/coldstar
export FAIRSCORE_API_URL="https://fairscale-test.purplesquirrelnetworks.workers.dev"
```

The proxy URL above bypasses the ISP block on api2.fairscale.xyz. Set it every time or the FairScore API calls will fail/timeout.

### Test Addresses to Have Ready (Copy These to Clipboard Manager)
Paste these into a text file or clipboard manager so you can quickly paste during recording:

```
# Well-known Solana addresses for FairScore lookups:
# Use your own wallet or any known devnet address.
# The FairScore API returns different tiers for different wallets.
# If the API is unreachable, the TUI gracefully degrades with a warning.
```

### Dry Run
Run through the entire script once without recording. Confirm:
- [ ] `python main.py` launches without errors
- [ ] FairScore lookup returns a result (or a clean warning if API is down)
- [ ] `python vault_dashboard_tui.py` renders properly at your terminal size
- [ ] You have at least one Solana address ready to paste

---

## THE RECORDING

---

### SCENE 1: Introduction (0:00 - 0:30)

**WHAT TO DO:**
1. Have the terminal open at the project directory, cursor blinking
2. Start recording (Loom: click Record, QuickTime: Cmd+Shift+5)
3. Wait 2 seconds of silence (gives you a clean edit point)

**WHAT TO SAY:**

> "Hey, I'm Matthew. This is Coldstar -- an air-gapped Solana cold wallet that turns any USB drive into hardware-grade security. Today I want to show you the feature that makes Coldstar different from every other wallet project: FairScore reputation integration. Before you send crypto to anyone, Coldstar checks the recipient's on-chain reputation and blocks transfers to known bad actors. Let me show you how it works."

**WHAT TO TYPE:**
```bash
python main.py
```

**WHAT SHOULD BE ON SCREEN:**
- The big ASCII "SOLANA" banner appears
- Status line shows `Network: https://api.devnet.solana.com`
- Connection status shows `Connected` (green) or `Offline` (yellow)
- The "NO USB DEVICE DETECTED" menu appears (this is expected and fine)

**TIP:** You do NOT need a USB plugged in for this demo. The wallet menu can be shown without one. If a USB with a wallet is available, even better -- but the key features work from the menu system regardless.

---

### SCENE 2: Show the Wallet Menu (0:30 - 1:00)

**WHAT TO SAY:**

> "Here's the main TUI. Coldstar is a full-featured cold wallet -- you can create wallets, send SOL, sign transactions offline, swap on Jupiter, and more. But let me draw your attention to option F: Check FairScore Reputation. This is the integration with FairScale's on-chain reputation API."

**WHAT TO DO:**
- If the "NO USB DEVICE DETECTED" screen is showing, you need a wallet loaded to see the full menu. Two options:
  - **Option A (USB available):** Mount a USB with a wallet on it (option 2)
  - **Option B (no USB):** Exit (`0`), then demonstrate FairScore by running the vault dashboard instead (skip to Scene 4 and come back)

If you have the full wallet menu visible, slowly scroll through the options with your cursor so judges can read them. Pause on these:
```
2. Send SOL (Create Unsigned Transaction)
J. Jupiter Swap (Create Unsigned Swap)
F. Check FairScore Reputation
```

**WHAT TO SAY (continuing):**

> "Notice that FairScore is baked into two places: the standalone lookup tool at option F, and also directly into the transaction flow when you try to send SOL. Let's start with the standalone lookup."

---

### SCENE 3: FairScore Reputation Lookup (1:00 - 2:15)

**WHAT TO DO:**
1. Select option `F` (Check FairScore Reputation)
2. When prompted for a wallet address, paste a Solana address

**WHAT TO TYPE:**
- Select `F. Check FairScore Reputation` from the menu
- Paste a Solana wallet address when prompted

**WHAT SHOULD BE ON SCREEN:**
The FairScore reputation panel appears with:
```
+------ FairScore Reputation ------+
| Address:    4xp...Tf8Y           |
| Reputation: [+] TRUSTED         |
| Tier:       Gold (3/5)           |
| FairScore:  52.3/100             |
| TX Limit:   100 SOL max          |
| Status:     Verified wallet ...  |
+----------------------------------+
```

**WHAT TO SAY:**

> "I just pasted a wallet address, and Coldstar queried the FairScale API in real time. This wallet came back as Gold tier -- a trusted wallet with a FairScore of about 52 out of 100. The transaction limit for this tier is 100 SOL. Let me show you the full tier legend."

**WHAT TO DO:**
- When asked "Show FairScore tier legend?", select "Yes, show tier explanations"

**WHAT SHOULD BE ON SCREEN:**
The tier legend table appears:

```
FairScore Reputation Tiers
Tier | API Tier | Label      | Score | Action | TX Limit  | Description
1    | bronze   | UNTRUSTED  | 0-19  | BLOCK  | BLOCKED   | High-risk wallet
2    | silver   | LOW TRUST  | 20-39 | WARN   | 10 SOL    | New or unverified
3    | gold     | TRUSTED    | 40-59 | ALLOW  | 100 SOL   | Verified wallet
4    | platinum | HIGH TRUST | 60-79 | ALLOW  | 500 SOL   | Established wallet
5    | diamond  | EXCELLENT  | 80-100| ALLOW  | Unlimited | Top-tier reputation
```

**WHAT TO SAY:**

> "Here's the full tier system. Five tiers from bronze to diamond. Bronze wallets -- known bad actors, sybil accounts -- are completely blocked. You literally cannot create a transaction to them. Silver wallets get a warning and a 10 SOL cap. Gold and above are allowed with increasing limits. Diamond tier is unlimited. This is all enforced at the transaction creation level, not just a visual indicator."

**TIMING NOTE:** Spend about 10 seconds letting the table sit on screen. Judges will want to read it.

---

### SCENE 4: Transaction Gating in Action (2:15 - 3:30)

**WHAT TO SAY:**

> "Now let me show you what happens when FairScore gates an actual transaction. I'll try to send SOL to different addresses and you'll see how the wallet responds based on reputation."

**WHAT TO DO:**
1. Return to the wallet menu
2. Select option `2. Send SOL (Create Unsigned Transaction)`
3. Enter a wallet address

**WHAT SHOULD BE ON SCREEN:**
After entering the recipient address, the FairScore check runs automatically:

```
---- FAIRSCORE REPUTATION CHECK ----
Checking reputation for 4xpR...Tf8Y...

+------ FairScore Reputation ------+
| Address:    4xpR...Tf8Y          |
| Reputation: !!! UNTRUSTED        |
| Tier:       Bronze (1/5)         |
| FairScore:  8.2/100              |
| TX Limit:   BLOCKED              |
+----------------------------------+

ERROR: TRANSACTION BLOCKED
Recipient has UNTRUSTED reputation (FairScore: 8.2, Tier: bronze) - transaction blocked
Coldstar will not create transactions to untrusted wallets.
```

**WHAT TO SAY:**

> "Watch this. I entered a recipient address and before I could even type an amount, Coldstar checked the FairScore API. This address came back as bronze tier -- untrusted. The transaction is completely blocked. I can't proceed. The wallet won't even let me create the unsigned transaction. This protects users from sending funds to known scam wallets."

**WHAT TO DO (second attempt):**
1. Go back to `Send SOL` again
2. This time enter a silver-tier address (if available) or describe the flow

**WHAT TO SAY:**

> "Now if I try a silver-tier wallet -- a low trust address -- the behavior is different. Coldstar shows a warning and asks me to confirm. It says 'proceed with caution, this wallet has a low trust score.' I have to explicitly type PROCEED to continue. And even then, I'm capped at 10 SOL maximum."

**IF THE API IS DOWN:**

If the FairScale API is unreachable (even through the proxy), the output will be:

```
FairScore API unavailable: [connection error]
Offline mode - skipping FairScore reputation check
```

**WHAT TO SAY (if API is down):**

> "The FairScale API is currently unreachable from my network, so you can see the graceful degradation. The wallet warns you that the reputation check was skipped and continues in offline mode. In production, you'd get the full gating behavior I just described."

---

### SCENE 5: Vault Dashboard with Reputation Column (3:30 - 4:15)

**WHAT TO DO:**
1. Exit main.py (option `0`)
2. Launch the vault dashboard:

```bash
python vault_dashboard_tui.py
```

**WHAT SHOULD BE ON SCREEN:**
The three-panel Textual TUI appears:
- Left panel: **Portfolio** with tokens listed (SOL, USDC, BTC, RAY, XYZ, Unknown Token)
- Each token row has a **Rep** column showing reputation icons
- Middle panel: Token details
- Right panel: Send panel

**WHAT TO SAY:**

> "Here's the vault dashboard -- a full portfolio view built with Textual. Look at the rightmost column in the portfolio panel. Every token and associated wallet has a reputation indicator. Diamond-tier assets like SOL and USDC show the triple-star badge. Platinum shows double-plus. Gold shows a plus sign. And down at the bottom -- this XYZ token with the yellow warning icon, and this Unknown Token in red with triple exclamation marks. That's a bronze-tier untrusted asset. Coldstar is telling you at a glance: this token came from a suspicious source."

**WHAT TO DO:**
- Let the dashboard sit on screen for 5-8 seconds so judges can take it in
- Press `q` to exit

---

### SCENE 6: Code Walkthrough & Closing (4:15 - 5:00)

**WHAT TO SAY:**

> "Let me quickly show you the integration code."

**WHAT TO DO:**
Open the FairScore integration file in the terminal:

```bash
head -100 src/fairscore_integration.py
```

**WHAT SHOULD BE ON SCREEN:**
The first 100 lines of the file, showing:
- The API configuration
- The tier mapping (bronze through diamond)
- The tier definitions with actions (BLOCK, WARN, ALLOW)
- The transaction limits per tier

**WHAT TO SAY:**

> "The FairScore integration is about 340 lines of Python. It queries the FairScale API, maps their tier system to transaction policies, caches results for 5 minutes, and exposes three key methods: get the tier, check if a transaction should be blocked, and get the transfer limit. It's plugged into both the send flow and the dashboard. Every transaction goes through this gate before it's created."

**PAUSE for 3 seconds, then close:**

> "That's Coldstar. Air-gapped cold wallet security with built-in reputation gating. Your keys never touch the internet, and your funds never go to untrusted wallets. Open source on GitHub. Thanks for watching."

**WHAT TO DO:**
- Stop recording
- Wait 2 seconds before stopping (gives a clean edit point at the end)

---

## Post-Recording Checklist

- [ ] Trim the first and last 2 seconds of dead air (or leave them for polish)
- [ ] Watch the full recording at 1x speed -- is every screen readable?
- [ ] Check that terminal text is legible at 720p (Loom's default playback)
- [ ] If any FairScore lookups failed, add a text annotation: "API blocked by ISP -- see proxy workaround in README"
- [ ] Upload to Loom or YouTube
- [ ] Copy the share link to the Colosseum submission

## Recovery Plans

**If `python main.py` crashes on launch:**
```bash
pip install -r local_requirements.txt
python main.py
```

**If the FairScore API times out through the proxy:**
The demo still works. The graceful degradation IS a feature worth showing. Say: "Even when the reputation API is unreachable, Coldstar warns you and continues safely."

**If the vault dashboard won't render:**
```bash
pip install textual
python vault_dashboard_tui.py
```
If it still fails, skip Scene 5 and spend the extra 45 seconds on the code walkthrough instead.

**If you fumble a line:**
Keep going. You can trim pauses in Loom's editor. Do NOT restart the entire recording -- just pause, collect yourself, and re-say the line.
