#!/usr/bin/env python3
"""Generate Coldstar for Base demo video.

Creates animated title card slides synced with voiceover audio.
Uses Pillow for frame rendering + ffmpeg for video composition.
"""

import os
import subprocess
import shutil
from PIL import Image, ImageDraw, ImageFont

AUDIO_DIR = "/Volumes/Virtual Server/projects/coldstar/demo-audio"
VIDEO_DIR = "/Volumes/Virtual Server/projects/coldstar/demo-video"
FRAMES_DIR = os.path.join(VIDEO_DIR, "frames")
OUTPUT = os.path.join(VIDEO_DIR, "coldstar-base-demo.mp4")

W, H = 1920, 1080
FPS = 30

os.makedirs(FRAMES_DIR, exist_ok=True)

SEGMENTS = [
    "s01-intro", "s02-problem", "s03-airgap", "s04-how-it-works",
    "s05-rust-signer", "s06-base-native", "s07-multichain",
    "s08-open-source", "s09-cta",
]

SLIDES = [
    ("COLDSTAR", "Air-Gapped Cold Wallet", "Now on Base"),
    ("THE PROBLEM", "Browser wallets expose keys in memory", "Hardware wallets still connect over USB"),
    ("TRUE AIR GAP", "No USB · No Bluetooth · No WiFi", "QR codes are the only bridge"),
    ("HOW IT WORKS", "Build → QR → Sign Offline → QR → Broadcast", "4 steps · Zero network exposure"),
    ("RUST SECURE SIGNER", "mlock · Argon2id · AES-256-GCM · Zeroize", "Keys exist only in locked memory pages"),
    ("BUILT FOR BASE", "secp256k1 ECDSA · EIP-1559 Type 2", "Base Mainnet + Sepolia Testnet"),
    ("MULTICHAIN", "Solana (Ed25519) + Base (secp256k1)", "Same encryption layer · Same air gap"),
    ("OPEN SOURCE", "18,000 lines · Fully auditable", "Don't trust us · Verify"),
    ("coldstar.dev", "Cold Signing for Base", "github.com/ExpertVagabond/coldstar-colosseum"),
]

GAP = 0.8

# Colors
BG = (0, 0, 0)
BASE_BLUE = (0, 82, 255)
WHITE = (255, 255, 255)
GRAY = (138, 138, 154)
GREEN = (0, 210, 106)
DARK_BLUE_GLOW = (0, 20, 60)


def get_duration(filepath):
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", filepath],
        capture_output=True, text=True,
    )
    return float(result.stdout.strip())


def get_font(size, bold=False):
    """Try to load a nice font, fall back to default."""
    font_paths = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/SFNSMono.ttf",
        "/Library/Fonts/SF-Pro-Display-Bold.otf",
        "/Library/Fonts/SF-Pro-Display-Regular.otf",
        "/System/Library/Fonts/HelveticaNeue.ttc",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                continue
    return ImageFont.load_default()


def lerp_color(c1, c2, t):
    """Linear interpolate between two colors."""
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def render_frame(slide_idx, alpha, frame_num):
    """Render a single frame as PIL Image."""
    title, subtitle, detail = SLIDES[slide_idx]

    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Subtle radial glow behind center
    glow_alpha = int(alpha * 40)
    for r in range(300, 0, -5):
        a = int(glow_alpha * (r / 300))
        color = (0, int(10 * alpha), int(40 * alpha))
        draw.ellipse(
            [W//2 - r, H//2 - r - 40, W//2 + r, H//2 + r - 40],
            fill=color,
        )

    # Accent line at top
    line_w = int(200 * alpha)
    if line_w > 0:
        draw.rectangle(
            [W//2 - line_w//2, H//2 - 130, W//2 + line_w//2, H//2 - 128],
            fill=tuple(int(c * alpha) for c in BASE_BLUE),
        )

    # Title
    is_accent = slide_idx == 0 or slide_idx == len(SLIDES) - 1
    title_color = BASE_BLUE if is_accent else WHITE
    title_size = 72 if is_accent else 60
    title_font = get_font(title_size, bold=True)

    faded_title = tuple(int(c * alpha) for c in title_color)
    bbox = draw.textbbox((0, 0), title, font=title_font)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, H // 2 - 80), title, fill=faded_title, font=title_font)

    # Subtitle
    sub_alpha = max(0, min(1, (alpha - 0.2) / 0.8)) if alpha < 1 else alpha
    sub_font = get_font(26)
    faded_sub = tuple(int(c * sub_alpha) for c in GRAY)
    bbox = draw.textbbox((0, 0), subtitle, font=sub_font)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, H // 2 + 20), subtitle, fill=faded_sub, font=sub_font)

    # Detail
    det_alpha = max(0, min(1, (alpha - 0.35) / 0.65)) if alpha < 1 else alpha
    det_font = get_font(22)
    faded_det = tuple(int(c * det_alpha) for c in GREEN)
    bbox = draw.textbbox((0, 0), detail, font=det_font)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, H // 2 + 70), detail, fill=faded_det, font=det_font)

    # Bottom accent line
    if line_w > 0:
        draw.rectangle(
            [W//2 - line_w//3, H//2 + 120, W//2 + line_w//3, H//2 + 122],
            fill=tuple(int(c * alpha * 0.5) for c in BASE_BLUE),
        )

    return img


def main():
    # Get durations
    durations = []
    for seg in SEGMENTS:
        path = os.path.join(AUDIO_DIR, f"{seg}.wav")
        dur = get_duration(path)
        durations.append(dur)
        print(f"  {seg}: {dur:.2f}s")

    total = sum(durations) + GAP * (len(durations) - 1)
    print(f"\nTotal: {total:.1f}s ({int(total//60)}:{int(total%60):02d})")

    # Generate each slide as a video
    slide_files = []
    for i, (seg, dur) in enumerate(zip(SEGMENTS, durations)):
        title = SLIDES[i][0]
        total_dur = dur + GAP if i < len(SEGMENTS) - 1 else dur
        total_frames = int(total_dur * FPS)

        slide_frames_dir = os.path.join(FRAMES_DIR, f"slide_{i:02d}")
        os.makedirs(slide_frames_dir, exist_ok=True)

        print(f"  Rendering slide {i}: {title} ({total_frames} frames)...", end=" ", flush=True)

        fade_in_frames = int(0.5 * FPS)
        fade_out_frames = int(0.4 * FPS)

        for f in range(total_frames):
            # Calculate alpha
            if f < fade_in_frames:
                alpha = f / fade_in_frames
            elif f > total_frames - fade_out_frames:
                alpha = (total_frames - f) / fade_out_frames
            else:
                alpha = 1.0

            alpha = max(0, min(1, alpha))
            img = render_frame(i, alpha, f)
            img.save(os.path.join(slide_frames_dir, f"frame_{f:05d}.png"))

        print("done")

        # Compose frames + audio into video
        audio_path = os.path.join(AUDIO_DIR, f"{seg}.wav")
        slide_path = os.path.join(VIDEO_DIR, f"slide_{i:02d}.mp4")
        slide_files.append(slide_path)

        cmd = [
            "ffmpeg", "-y",
            "-framerate", str(FPS),
            "-i", os.path.join(slide_frames_dir, "frame_%05d.png"),
            "-f", "lavfi", "-i", f"anullsrc=r=24000:cl=mono",
            "-i", audio_path,
            "-filter_complex",
            f"[1:a]atrim=0:{total_dur}[silence];[2:a][silence]concat=n=2:v=0:a=1[aout]",
            "-map", "0:v", "-map", "[aout]",
            "-c:v", "libx264", "-preset", "fast", "-crf", "23", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k",
            "-t", str(total_dur),
            slide_path,
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"    ffmpeg error: {result.stderr[-300:]}")
            # Try simpler approach without silence padding
            cmd_simple = [
                "ffmpeg", "-y",
                "-framerate", str(FPS),
                "-i", os.path.join(slide_frames_dir, "frame_%05d.png"),
                "-i", audio_path,
                "-c:v", "libx264", "-preset", "fast", "-crf", "23", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "192k",
                "-t", str(total_dur),
                slide_path,
            ]
            result = subprocess.run(cmd_simple, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"    FATAL: {result.stderr[-200:]}")
                return

        # Clean up frames
        shutil.rmtree(slide_frames_dir)

    # Concatenate all slides
    print("\nConcatenating slides...")
    concat_file = os.path.join(VIDEO_DIR, "concat.txt")
    with open(concat_file, "w") as f:
        for sf in slide_files:
            f.write(f"file '{sf}'\n")

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", concat_file,
        "-c", "copy",
        OUTPUT,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  Concat error: {result.stderr[-300:]}")
        return

    # Get final duration
    final_dur = get_duration(OUTPUT)
    mins = int(final_dur // 60)
    secs = int(final_dur % 60)

    print(f"\n{'='*45}")
    print(f"  VIDEO COMPLETE")
    print(f"  Output: {OUTPUT}")
    print(f"  Duration: {mins}:{secs:02d}")
    print(f"{'='*45}")

    # Copy to Desktop
    desktop = os.path.expanduser("~/Desktop/coldstar-base-demo.mp4")
    shutil.copy2(OUTPUT, desktop)
    print(f"  Copied to {desktop}")

    # Clean up individual slides
    for sf in slide_files:
        if os.path.exists(sf):
            os.remove(sf)
    print("  Cleaned up temp files")


if __name__ == "__main__":
    main()
