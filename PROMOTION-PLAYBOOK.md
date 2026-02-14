# Coldstar Promotion Playbook — Feb 8, 2026

**Deadline: Feb 12, 2026 12PM EST (4 days left)**

---

## STATUS DASHBOARD

- [x] Colosseum submission (Project #62, Agent #127)
- [x] SolMail submission (Project #47, Agent #100)
- [x] Demo videos (4 finals in videos/)
- [x] Grant applications (DD.xyz + FairScale PDFs in grants/)
- [x] Social media copy (SOCIAL_MEDIA_COPY.md, LAUNCH_TWEETS.md)
- [x] Forum post draft (COLOSSEUM_FORUM_POST.md)
- [x] Twitter account (@buildcoldstar)
- [ ] **Claim codes linked** — CRITICAL, do this FIRST
- [ ] **YouTube videos uploaded** — needs GCP client_secrets.json
- [ ] **Twitter threads posted** — from @buildcoldstar + @expertvagabond
- [ ] **Colosseum forum post** — paste from docs/COLOSSEUM_FORUM_POST.md
- [ ] **FairScale submission** — superteam.fun/earn/listing/fairathon/ (deadline March 1)
- [ ] **DD.xyz grant submitted** — find submission portal
- [ ] **Upvotes solicited** — share vote link widely

---

## STEP 1: LINK CLAIM CODES (5 min, do NOW)

Both claim codes need your X account + Solana wallet linked to receive prizes.

**Coldstar (Agent #127):**
https://colosseum.com/agent-hackathon/claim/781a3cf1-2f7c-429f-8d79-d004fe5f7734

**SolMail (Agent #100):**
https://colosseum.com/agent-hackathon/claim/af36e272-b1ba-4ea9-8279-377796213f4b

Action: Open both URLs in browser, sign in with X, connect Solana wallet.

---

## STEP 2: YOUTUBE UPLOAD (15 min)

### Setup (one-time):
1. Go to https://console.cloud.google.com/apis/library/youtube.googleapis.com
2. Enable "YouTube Data API v3"
3. Go to Credentials → Create OAuth 2.0 Client ID (Desktop app)
4. Download JSON → save as: `$VS/projects/coldstar/videos/youtube/client_secrets.json`

### Upload:
```bash
cd /Volumes/Virtual\ Server/projects/coldstar/videos/youtube/
pip install google-auth google-auth-oauthlib google-api-python-client
python3 upload_youtube.py  # Opens browser for OAuth, then uploads all 4
```

### Videos to upload:
1. coldstar-demo-final.mp4 (7.8 MB) — "Coldstar: $10 Air-Gapped Solana Cold Wallet | Demo"
2. coldstar-square-final.mp4 (5.9 MB) — "Coldstar: Air-Gapped Solana Vault — $10 USB Cold Wallet"
3. coldstar-vertical-final.mp4 (2.4 MB) — "Hardware wallets cost $200. Coldstar costs $10. #Shorts"
4. coldstar-explainer-final.mp4 (1.0 MB) — "How Air-Gapped Signing Works | Coldstar Explainer"
5. coldstar-fairscore-demo-v2.mp4 (7.4 MB) — needs metadata added to upload script

---

## STEP 3: POST TWITTER THREADS (10 min)

### Thread 1 — @buildcoldstar (project account)
Use the 5-tweet thread from SOCIAL_MEDIA_COPY.md:
1. Problem: AI agents + $100K treasuries
2. Solution: $10 USB → hardware-grade
3. Technical: devnet programs, Jupiter, Pyth
4. Positioning: only air-gapped security infra
5. CTA: vote link

### Thread 2 — @expertvagabond (personal account)
Post a personal endorsement:

> Built something for the @Colosseum Agent Hackathon.
>
> Coldstar: air-gapped Solana cold wallet. Any $10 USB drive.
>
> FairScore reputation gates every transaction before it crosses the air gap. Known scammers get hard-blocked. Trusted addresses get green-lit.
>
> Demo: https://coldstar.dev/colosseum
> Vote: [project link]
>
> @buildcoldstar #Solana #Colosseum

### Thread 3 — @buildcoldstar FairScore launch thread
Use the 10-tweet thread from docs/LAUNCH_TWEETS.md

### Vote link to include:
https://colosseum.com/agent-hackathon/projects/coldstar-air-gapped-solana-vault-2z9v3x?from=leaderboard

---

## STEP 4: COLOSSEUM FORUM POST (5 min)

1. Go to https://colosseum.com/agent-hackathon/forum
2. Create new post
3. Copy content from: `$VS/projects/coldstar/docs/COLOSSEUM_FORUM_POST.md`
4. Also post a shorter one for SolMail (Project #47)

---

## STEP 5: FAIRSCALE SUBMISSION (15 min, deadline March 1)

Portal: https://superteam.fun/earn/listing/fairathon/

Requirements:
- [x] Working link: https://coldstar.dev/colosseum
- [x] GitHub repo with README: ExpertVagabond/coldstar-colosseum
- [ ] Demo video (YouTube link — do Step 2 first)
- [x] Pitch deck: docs in project
- [ ] Traction evidence (Twitter, analytics)
- [x] Team info: Matthew Karsten, Purple Squirrel Media
- [x] FairScore integration description: docs/FAIRSCORE_INTEGRATION.md

Prize: 5,000 USDC + 3 months free FairScale Pro API
Contact: @zkishann on Telegram

---

## STEP 6: DD.XYZ GRANT (research needed)

Application PDF ready at: grants/COLDSTAR-DD-XYZ-GRANT-APPLICATION.pdf
Need to find DD.xyz submission portal. Check:
- https://dd.xyz
- Webacy partnership/grants page
- Direct email to DD.xyz team

---

## STEP 7: DAILY ENGAGEMENT (ongoing until Feb 12)

### Feb 8 (today):
- Link claim codes
- Post first Twitter thread
- Submit forum post

### Feb 9-10:
- Upload YouTube videos
- Post FairScore thread
- Engage with other hackathon projects (vote for them, comment)
- Share in Solana Discord

### Feb 11:
- "Last 24 hours!" reminder tweet
- Final push for votes

### Feb 12 (deadline day):
- Morning: final CTA tweet
- Submit FairScale (separate deadline March 1, but good to have early)

---

## KEY LINKS

| Resource | URL |
|----------|-----|
| Coldstar live | https://coldstar.dev/colosseum |
| Coldstar GitHub | https://github.com/ExpertVagabond/coldstar-colosseum |
| Coldstar vote | https://colosseum.com/agent-hackathon/projects/coldstar-air-gapped-solana-vault-2z9v3x?from=leaderboard |
| Coldstar claim | https://colosseum.com/agent-hackathon/claim/781a3cf1-2f7c-429f-8d79-d004fe5f7734 |
| SolMail claim | https://colosseum.com/agent-hackathon/claim/af36e272-b1ba-4ea9-8279-377796213f4b |
| @buildcoldstar | https://x.com/buildcoldstar |
| @expertvagabond | https://x.com/expertvagabond |
| FairScale submit | https://superteam.fun/earn/listing/fairathon/ |
| Pitch deck | https://expertvagabond.github.io/coldstar-colosseum/docs/pitch-deck.html |
| FairScore docs | https://expertvagabond.github.io/coldstar-colosseum/docs/FAIRSCORE_INTEGRATION.md |
