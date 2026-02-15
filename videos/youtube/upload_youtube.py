#!/usr/bin/env python3
"""Upload Coldstar demo videos to YouTube.

Setup:
  1. Go to https://console.cloud.google.com/apis/library/youtube.googleapis.com
  2. Enable "YouTube Data API v3" for your project
  3. Go to Credentials → Create Credentials → OAuth 2.0 Client ID
     - Application type: Desktop app
     - Download the JSON file
  4. Save it as: ~/Desktop/coldstar-videos/client_secrets.json
  5. Run: python3 ~/Desktop/coldstar-videos/upload_youtube.py
     - First run opens browser for OAuth consent
     - Token is cached in youtube_token.json for future runs

Usage:
  python3 upload_youtube.py              # Upload all 4 videos
  python3 upload_youtube.py --dry-run    # Preview metadata without uploading
  python3 upload_youtube.py --video 1    # Upload only video #1
"""

import os
import sys
import json
import argparse
import http.client
import httplib2
from pathlib import Path

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
SCRIPT_DIR = Path(__file__).parent
VIDEOS_DIR = SCRIPT_DIR.parent  # videos/ directory (one level up)
CLIENT_SECRETS = SCRIPT_DIR / "client_secrets.json"
TOKEN_FILE = SCRIPT_DIR / "youtube_token.json"

# ── Video metadata ──────────────────────────────────────────────────

VIDEOS = [
    {
        "file": "coldstar-demo-final.mp4",
        "title": "Coldstar: $10 Air-Gapped Solana Cold Wallet | Demo",
        "description": """Coldstar turns any $10 USB drive into a hardware-grade cold wallet for Solana.

🔐 Air-gapped key generation & transaction signing
💱 Jupiter DEX token swaps
📊 Pyth Network real-time price feeds
🏛️ On-chain DAO governance
🤖 Agent-friendly API

Your private key never touches the network.

🔗 Try it: https://coldstar.dev/colosseum
📦 Source: https://github.com/ExpertVagabond/coldstar-colosseum
🏆 Colosseum Agent Hackathon 2026

Built by @buildcoldstar | Purple Squirrel Media | coldstar.dev

#Solana #ColdWallet #AirGapped #Crypto #Security #Hackathon #Colosseum #DeFi #Jupiter #Web3""",
        "tags": ["Solana", "cold wallet", "air-gapped", "crypto security", "USB wallet",
                 "hardware wallet", "Coldstar", "Jupiter DEX", "Pyth Network", "DeFi",
                 "DAO", "hackathon", "Colosseum", "web3", "blockchain"],
        "category": "28",  # Science & Technology
        "privacy": "public",
    },
    {
        "file": "coldstar-square-final.mp4",
        "title": "Coldstar: Air-Gapped Solana Vault — $10 USB Cold Wallet",
        "description": """Square format demo of Coldstar — the $10 air-gapped Solana cold wallet.

Any USB drive becomes a hardware-grade cold wallet. Air-gapped signing, Jupiter DEX swaps, Pyth prices, DAO governance.

🔗 https://coldstar.dev/colosseum
📦 https://github.com/ExpertVagabond/coldstar-colosseum
🏆 Colosseum Agent Hackathon 2026

#Solana #ColdWallet #AirGapped #Crypto #Coldstar #DeFi""",
        "tags": ["Solana", "cold wallet", "air-gapped", "Coldstar", "crypto",
                 "USB wallet", "DeFi", "hackathon", "Colosseum"],
        "category": "28",
        "privacy": "public",
    },
    {
        "file": "coldstar-vertical-final.mp4",
        "title": "Hardware wallets cost $200. Coldstar costs $10. #Solana #Shorts",
        "description": """$200 hardware wallet vs $10 Coldstar.

Any USB drive → cold wallet. Store keys, sign offline, swap on Jupiter, confirmed on Solana.

Your private key NEVER touches the network.

🔗 https://coldstar.dev/colosseum
🏆 Colosseum Agent Hackathon 2026

#Shorts #Solana #ColdWallet #Crypto #Coldstar""",
        "tags": ["Shorts", "Solana", "cold wallet", "Coldstar", "crypto",
                 "hardware wallet", "air-gapped", "USB"],
        "category": "28",
        "privacy": "public",
    },
    {
        "file": "coldstar-explainer-final.mp4",
        "title": "How Air-Gapped Signing Works | Coldstar Explainer",
        "description": """Step-by-step explainer of how Coldstar's air-gapped signing keeps your Solana keys safe.

1️⃣ Generate keys offline on USB
2️⃣ Create transaction online
3️⃣ Sign completely offline (air gap)
4️⃣ Broadcast signed tx to Solana

Private key never leaves the USB drive.

🔗 https://coldstar.dev/colosseum
📦 https://github.com/ExpertVagabond/coldstar-colosseum
🏆 Colosseum Agent Hackathon 2026

#Solana #AirGapped #ColdWallet #Security #Coldstar #Crypto""",
        "tags": ["Solana", "air-gapped", "cold wallet", "explainer", "Coldstar",
                 "crypto security", "signing", "hackathon", "Colosseum"],
        "category": "28",
        "privacy": "public",
    },
    {
        "file": "coldstar-fairscore-demo-v2.mp4",
        "title": "Coldstar x FairScore: Reputation-Gated Cold Wallet | Demo",
        "description": """See how FairScore reputation screening works inside Coldstar's air-gapped cold wallet.

Every transaction is checked against FairScale's reputation API before crossing the air gap:
🔴 Bronze tier = HARD BLOCK (known scammers)
🟡 Silver tier = WARNING (low reputation)
🟢 Gold+ = PROCEED (trusted addresses)

Your private key never touches the network. But now your wallet knows who you're sending to.

🔗 https://coldstar.dev/colosseum
📦 https://github.com/ExpertVagabond/coldstar-colosseum
🏆 Colosseum Agent Hackathon 2026 — Project #62

#Solana #FairScore #ColdWallet #AirGapped #Crypto #Security #Reputation""",
        "tags": ["Solana", "FairScore", "cold wallet", "air-gapped", "Coldstar",
                 "reputation", "crypto security", "hackathon", "Colosseum", "FairScale"],
        "category": "28",
        "privacy": "public",
    },
]


def authenticate():
    """Handle OAuth 2.0 flow, return YouTube API service."""
    creds = None

    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CLIENT_SECRETS.exists():
                print(f"\n❌ Missing: {CLIENT_SECRETS}")
                print("\nSetup instructions:")
                print("  1. Go to https://console.cloud.google.com/apis/credentials")
                print("  2. Create OAuth 2.0 Client ID (Desktop app)")
                print("  3. Download JSON → save as client_secrets.json in this folder")
                sys.exit(1)

            flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRETS), SCOPES)
            creds = flow.run_local_server(port=8080)

        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
        print("✅ Auth token saved")

    return build("youtube", "v3", credentials=creds)


def upload_video(youtube, video_meta: dict, dry_run: bool = False):
    """Upload a single video to YouTube."""
    filepath = VIDEOS_DIR / video_meta["file"]

    if not filepath.exists():
        print(f"❌ File not found: {filepath}")
        return None

    size_mb = filepath.stat().st_size / (1024 * 1024)
    print(f"\n{'[DRY RUN] ' if dry_run else ''}📹 {video_meta['file']} ({size_mb:.1f} MB)")
    print(f"   Title: {video_meta['title']}")
    print(f"   Privacy: {video_meta['privacy']}")
    print(f"   Tags: {', '.join(video_meta['tags'][:5])}...")

    if dry_run:
        return "dry-run"

    body = {
        "snippet": {
            "title": video_meta["title"],
            "description": video_meta["description"],
            "tags": video_meta["tags"],
            "categoryId": video_meta["category"],
        },
        "status": {
            "privacyStatus": video_meta["privacy"],
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(
        str(filepath),
        mimetype="video/mp4",
        resumable=True,
        chunksize=1024 * 1024,  # 1MB chunks
    )

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media,
    )

    print("   Uploading", end="", flush=True)
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            pct = int(status.progress() * 100)
            print(f"\r   Uploading... {pct}%", end="", flush=True)

    video_id = response["id"]
    url = f"https://youtu.be/{video_id}"
    print(f"\r   ✅ Uploaded: {url}")
    return url


def main():
    parser = argparse.ArgumentParser(description="Upload Coldstar videos to YouTube")
    parser.add_argument("--dry-run", action="store_true", help="Preview without uploading")
    parser.add_argument("--video", type=int, help="Upload only video N (1-4)")
    args = parser.parse_args()

    if args.dry_run:
        print("🔍 DRY RUN — previewing metadata only\n")
        for i, v in enumerate(VIDEOS, 1):
            upload_video(None, v, dry_run=True)
        return

    youtube = authenticate()
    print("✅ Authenticated with YouTube API\n")

    videos_to_upload = VIDEOS
    if args.video:
        if 1 <= args.video <= len(VIDEOS):
            videos_to_upload = [VIDEOS[args.video - 1]]
        else:
            print(f"❌ Invalid video number. Use 1-{len(VIDEOS)}")
            sys.exit(1)

    results = []
    for v in videos_to_upload:
        url = upload_video(youtube, v)
        if url:
            results.append({"file": v["file"], "title": v["title"], "url": url})

    if results:
        print("\n" + "=" * 60)
        print("📋 Upload Summary:")
        for r in results:
            print(f"   {r['title']}")
            print(f"   → {r['url']}\n")

        # Save results
        results_file = SCRIPT_DIR / "upload_results.json"
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to {results_file}")


if __name__ == "__main__":
    main()
