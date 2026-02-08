#!/usr/bin/env python3
"""Build Coldstar x FairScore demo video with voiceover and background music."""
import subprocess
import os
import json
import time

VIDEO_DIR = os.path.dirname(os.path.abspath(__file__))
SLIDES_DIR = os.path.join(VIDEO_DIR, "slides")
AUDIO_DIR = os.path.join(VIDEO_DIR, "audio")
OUTPUT = os.path.join(VIDEO_DIR, "coldstar-fairscore-demo.mp4")

# Each slide: (title, body_lines, voiceover_text, duration_secs, bg_color, accent_color)
SLIDES = [
    # Slide 1: Title (10s)
    (
        "COLDSTAR × FAIRSCORE",
        [
            "",
            "Reputation-Gated Air-Gapped Cold Wallet",
            "for Solana",
            "",
            "Built by Matthew Karsten",
            "@expertvagabond | Purple Squirrel Media",
        ],
        "Coldstar is the first and only air-gapped Solana cold wallet with built-in reputation scoring. Every transaction is checked against FairScale's FairScore API before it crosses the air gap.",
        12,
        "#0a0a0a",
        "#ff00ff",
    ),
    # Slide 2: The Problem (12s)
    (
        "THE PROBLEM",
        [
            "",
            "Cold wallets provide the best physical security.",
            "",
            "But they are BLIND to counterparty risk.",
            "",
            "You can air-gap sign a transaction",
            "to a SCAM ADDRESS and lose everything.",
            "",
            "$1.2B hardware wallet market",
            "has ZERO reputation layer.",
        ],
        "Cold wallets give you the best physical security in crypto. But they're completely blind to who you're sending to. You can carefully sign a transaction on your air-gapped device, only to send funds to a scam address. Once signed and broadcast, the funds are gone forever. The entire 1.2 billion dollar hardware wallet market has zero reputation intelligence.",
        15,
        "#0a0a0a",
        "#ff4444",
    ),
    # Slide 3: The Solution (12s)
    (
        "THE SOLUTION: FAIRSCORE GATING",
        [
            "",
            "FairScore (0-100) checked BEFORE every transaction",
            "",
            "  BRONZE (0-19):    HARD BLOCK",
            "  SILVER (20-39):   SOFT WARNING",
            "  GOLD (40-59):     PROCEED",
            "  PLATINUM (60-79): PROCEED",
            "  DIAMOND (80+):    UNLIMITED",
            "",
            "All checks happen BEFORE the point of no return.",
        ],
        "Coldstar integrates FairScale's FairScore as a core gating mechanism. Before any transaction crosses the air gap for offline signing, the recipient's reputation score is checked. Bronze tier addresses, with scores below 20, are hard blocked. The transaction simply cannot be created. Silver tier gets a soft warning requiring explicit confirmation. Gold and above get the green light. This all happens before the point of no return.",
        17,
        "#0a0a0a",
        "#00ff88",
    ),
    # Slide 4: Architecture (10s)
    (
        "ARCHITECTURE",
        [
            "",
            "ONLINE DEVICE              AIR-GAPPED USB",
            "+------------------+  QR  +------------------+",
            "| FairScore API    | ---> | Alpine Linux     |",
            "| Jupiter DEX      |      | Ed25519 Signing  |",
            "| Pyth Oracles     | <--- | Key Storage      |",
            "| Rich TUI         |  QR  | Offline Only     |",
            "+------------------+      +------------------+",
            "         |",
            "    Solana Mainnet",
        ],
        "Here's the architecture. The online device handles all FairScore API calls, Jupiter swaps, and Pyth price feeds. Transactions are transferred via QR code to the air-gapped USB device running Alpine Linux. The offline device signs with Ed25519 and returns the signature via QR. FairScore metadata is embedded in the QR payload so users can verify reputation on the offline screen before signing.",
        14,
        "#0a0a0a",
        "#58d1eb",
    ),
    # Slide 5: Live API Demo (12s)
    (
        "LIVE API: JUPITER WALLET",
        [
            "",
            "GET /score?wallet=JUPyiwrYJFsk...ZNsDvCN",
            "",
            '  "fairscore": 34.2,',
            '  "tier": "silver",',
            '  "badges": [',
            '    "LST Staker",',
            '    "SOL Maxi",',
            '    "No Instant Dumps"',
            "  ]",
            "",
            "Action: WARNING - Confirm to proceed",
        ],
        "Here's a real API response from FairScale. The Jupiter aggregator wallet scores 34.2 out of 100, placing it in the Silver tier. It has three badges: LST Staker, SOL Maxi, and No Instant Dumps. In Coldstar, this triggers a soft warning. The user sees the score, badges, and must explicitly confirm before the transaction is created.",
        14,
        "#0a0a0a",
        "#ffaa00",
    ),
    # Slide 6: Bronze BLOCK (10s)
    (
        "DEMO: BRONZE BLOCK",
        [
            "",
            "+-------- FairScore Reputation --------+",
            "|  Address:     5xGh...Tf8Y             |",
            "|  Reputation:  !!! UNTRUSTED           |",
            "|  Tier:        Bronze (1/5)            |",
            "|  FairScore:   12.3/100                |",
            "|  TX Limit:    BLOCKED                 |",
            "+---------------------------------------+",
            "",
            "  TRANSACTION BLOCKED",
            "  Cannot send to bronze-tier wallet",
        ],
        "When you try to send to a bronze-tier wallet, Coldstar hard blocks the transaction. The rich terminal UI shows the address, its untrusted status, the bronze tier, and the score of 12.3 out of 100. The transaction cannot proceed. You physically cannot send funds to a known scam address. This is the core value proposition.",
        13,
        "#0a0a0a",
        "#ff4444",
    ),
    # Slide 7: 6 Integration Points (12s)
    (
        "6 INTEGRATION POINTS",
        [
            "",
            "1. Transaction Gating    - Block/warn before air-gap",
            "2. Dynamic Limits        - Reputation-scaled amounts",
            "3. DAO Governance         - Vote weight by FairScore",
            "4. Jupiter Screening     - Token contract reputation",
            "5. Dashboard Badges      - Reputation in portfolio",
            "6. MCP Agent Gates       - Autonomy by reputation",
            "",
            "FairScore is NOT decorative.",
            "It is a CORE GATING MECHANISM.",
        ],
        "Coldstar has six distinct FairScore integration points. Transaction gating blocks or warns before the air gap. Dynamic transfer limits scale with reputation. DAO governance weights votes by FairScore. Jupiter swap screening checks token contracts. The vault dashboard shows reputation badges. And MCP agent gates create an autonomy gradient for AI agents. FairScore is not a decorative badge. It's a core gating mechanism that determines whether transactions can proceed.",
        16,
        "#0a0a0a",
        "#7B2FBE",
    ),
    # Slide 8: Business Model (10s)
    (
        "BUSINESS MODEL",
        [
            "",
            "  Coldstar Pro:       $9.99/mo",
            "    Advanced analytics, higher limits",
            "",
            "  Enterprise/DAO:     $99/mo",
            "    Multi-wallet, compliance reporting",
            "",
            "  USB Hardware Kits:  $29.99",
            "    Pre-configured, plug-and-play",
            "",
            "  Path to $10K MRR within 12 months",
        ],
        "The business model has three revenue streams. Coldstar Pro at $9.99 per month for advanced analytics and higher limits. Enterprise and DAO plans at $99 per month for multi-wallet management and compliance. And pre-configured USB hardware kits at $29.99 each. We're targeting $10K monthly recurring revenue within 12 months.",
        12,
        "#0a0a0a",
        "#98e024",
    ),
    # Slide 9: Traction (10s)
    (
        "TRACTION & TEAM",
        [
            "",
            "  Colosseum Agent Hackathon - Project #62",
            "  Recognized by Superteam Earn",
            "  Live at coldstar.dev",
            "  2,500+ lines shipped",
            "  DAO programs on devnet",
            "",
            "  Matthew Karsten - Solo Founder",
            "  1,800+ commits across projects",
            "  Purple Squirrel Media LLC",
            "  Built and shipped in 10-day sprint",
        ],
        "Coldstar was built for the Colosseum Agent Hackathon as Project #62 and was recognized by Superteam Earn. The platform is live at coldstar.dev with over 2,500 lines of production Python and DAO programs deployed on Solana devnet. I'm Matthew Karsten, solo founder at Purple Squirrel Media. Over 1,800 commits across projects. Built and shipped Coldstar in a 10-day sprint.",
        13,
        "#0a0a0a",
        "#58d1eb",
    ),
    # Slide 10: CTA (8s)
    (
        "TRY COLDSTAR",
        [
            "",
            "  Live:   coldstar.dev/colosseum",
            "",
            "  GitHub: ExpertVagabond/coldstar-colosseum",
            "",
            "  Twitter: @expertvagabond",
            "",
            "",
            '"The future of cold storage is intelligent."',
            "",
            "  FairScale Fairathon 2026",
        ],
        "Try Coldstar today at coldstar.dev. The code is open source on GitHub. Follow at expert vagabond on X. The future of cold storage is intelligent. Thank you.",
        10,
        "#0a0a0a",
        "#ff00ff",
    ),
]


def create_slide_image(idx, title, body_lines, bg_color, accent_color):
    """Create a 1920x1080 slide image using ImageMagick."""
    out_path = os.path.join(SLIDES_DIR, f"slide_{idx:02d}.png")

    # Build the body text
    body_text = "\n".join(body_lines)

    # Create gradient background
    cmd = [
        "magick",
        "-size", "1920x1080",
        f"xc:{bg_color}",
        # Add subtle gradient overlay
        "(", "-size", "1920x1080",
        "gradient:transparent-#111111",
        "-rotate", "180",
        ")",
        "-composite",
        # Title text
        "-font", "Courier-Bold",
        "-pointsize", "72",
        "-fill", accent_color,
        "-gravity", "North",
        "-annotate", "+0+80", title,
        # Body text
        "-font", "Courier",
        "-pointsize", "38",
        "-fill", "#cccccc",
        "-gravity", "NorthWest",
        "-annotate", "+120+220", body_text,
        # Bottom branding
        "-font", "Courier",
        "-pointsize", "24",
        "-fill", "#444444",
        "-gravity", "South",
        "-annotate", "+0+30", "coldstar.dev | @expertvagabond | FairScale Fairathon 2026",
        out_path,
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return out_path


def generate_voiceover(idx, text, duration):
    """Generate voiceover audio using macOS say command."""
    aiff_path = os.path.join(AUDIO_DIR, f"vo_{idx:02d}.aiff")
    wav_path = os.path.join(AUDIO_DIR, f"vo_{idx:02d}.wav")

    # Use Samantha voice (natural US English)
    # Adjust rate to fit duration: ~150 wpm baseline
    word_count = len(text.split())
    target_wpm = max(140, min(200, (word_count / (duration - 1)) * 60))
    rate = int(target_wpm * 1.1)  # say rate is slightly different from wpm

    subprocess.run(
        ["say", "-v", "Samantha", "-r", str(rate), "-o", aiff_path, text],
        check=True,
        capture_output=True,
    )

    # Convert to wav
    subprocess.run(
        ["ffmpeg", "-y", "-i", aiff_path, "-ar", "44100", "-ac", "1", wav_path],
        check=True,
        capture_output=True,
    )
    os.remove(aiff_path)
    return wav_path


def generate_background_music(total_duration):
    """Generate subtle ambient background music using ffmpeg tone generators."""
    music_path = os.path.join(AUDIO_DIR, "bgm.wav")

    # Simple ambient drone: two sine waves mixed quietly
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i",
        f"sine=frequency=110:duration={total_duration}",
        "-f", "lavfi", "-i",
        f"sine=frequency=165:duration={total_duration}",
        "-filter_complex",
        "[0]volume=0.025[a];"
        "[1]volume=0.015[b];"
        "[a][b]amix=inputs=2:duration=longest,"
        "lowpass=f=600,highpass=f=80,"
        f"afade=t=in:st=0:d=3,afade=t=out:st={total_duration-3}:d=3[out]",
        "-map", "[out]",
        "-ar", "44100", "-ac", "1",
        music_path,
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return music_path


def build_video():
    """Assemble all slides + audio into final video."""
    print("=== Coldstar x FairScore Demo Video Builder ===\n")

    # Step 1: Create slide images
    print("1/4 Creating slide images...")
    slide_paths = []
    for i, (title, body, _, _, bg, accent) in enumerate(SLIDES):
        path = create_slide_image(i, title, body, bg, accent)
        slide_paths.append(path)
        print(f"  Slide {i+1}/{len(SLIDES)}: {title}")

    # Step 2: Generate voiceovers
    print("\n2/4 Generating voiceovers...")
    vo_paths = []
    for i, (_, _, vo_text, duration, _, _) in enumerate(SLIDES):
        path = generate_voiceover(i, vo_text, duration)
        vo_paths.append(path)
        print(f"  VO {i+1}/{len(SLIDES)}: {len(vo_text)} chars")

    # Step 3: Generate background music
    total_duration = sum(s[3] for s in SLIDES)
    print(f"\n3/4 Generating background music ({total_duration}s)...")
    bgm_path = generate_background_music(total_duration)
    print(f"  BGM: {bgm_path}")

    # Step 4: Combine into video
    print("\n4/4 Assembling final video...")

    # Create concat file for slides with durations
    concat_path = os.path.join(VIDEO_DIR, "concat.txt")
    with open(concat_path, "w") as f:
        for i, (_, _, _, duration, _, _) in enumerate(SLIDES):
            f.write(f"file 'slides/slide_{i:02d}.png'\n")
            f.write(f"duration {duration}\n")
        # Need to repeat last frame for concat demuxer
        f.write(f"file 'slides/slide_{len(SLIDES)-1:02d}.png'\n")

    # Concatenate all voiceover audio with padding to match slide durations
    vo_concat_path = os.path.join(AUDIO_DIR, "vo_all.wav")

    # Build complex filter for audio concatenation with silence padding
    filter_parts = []
    input_args = []
    for i, (_, _, _, duration, _, _) in enumerate(SLIDES):
        input_args.extend(["-i", vo_paths[i]])
        # Pad each VO to exactly the slide duration
        filter_parts.append(f"[{i}]apad=whole_dur={duration}[a{i}]")

    concat_labels = "".join(f"[a{i}]" for i in range(len(SLIDES)))
    filter_parts.append(f"{concat_labels}concat=n={len(SLIDES)}:v=0:a=1[voall]")

    filter_str = ";".join(filter_parts)

    cmd = (
        ["ffmpeg", "-y"]
        + input_args
        + ["-filter_complex", filter_str, "-map", "[voall]", "-ar", "44100", "-ac", "1", vo_concat_path]
    )
    subprocess.run(cmd, check=True, capture_output=True)

    # Final assembly: slides + voiceover + bgm
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", concat_path,  # slide images
        "-i", vo_concat_path,  # voiceover
        "-i", bgm_path,  # background music
        "-filter_complex",
        "[1][2]amix=inputs=2:duration=first:dropout_transition=3[audio]",
        "-map", "0:v",
        "-map", "[audio]",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "23",
        "-pix_fmt", "yuv420p",
        "-r", "30",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        OUTPUT,
    ]
    subprocess.run(cmd, check=True, capture_output=True)

    # Cleanup
    os.remove(concat_path)

    duration_check = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", OUTPUT],
        capture_output=True, text=True,
    )
    final_duration = float(duration_check.stdout.strip())

    print(f"\n=== DONE ===")
    print(f"Output: {OUTPUT}")
    print(f"Duration: {final_duration:.1f}s ({final_duration/60:.1f} min)")
    print(f"Size: {os.path.getsize(OUTPUT) / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    build_video()
