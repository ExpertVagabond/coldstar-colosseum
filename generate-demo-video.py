#!/usr/bin/env python3
"""Generate Coldstar for Base demo video using actual brand assets.

Uses promo images, logos, TUI screenshots as slide backgrounds
with text overlays synced to voiceover audio.
"""

import os
import subprocess
import shutil
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

AUDIO_DIR = "/Volumes/Virtual Server/projects/coldstar/demo-audio"
VIDEO_DIR = "/Volumes/Virtual Server/projects/coldstar/demo-video"
FRAMES_DIR = os.path.join(VIDEO_DIR, "frames")
ASSETS = "/Volumes/Virtual Server/projects/coldstar"
OUTPUT = os.path.join(VIDEO_DIR, "coldstar-base-demo.mp4")

W, H = 1920, 1080
FPS = 30

os.makedirs(FRAMES_DIR, exist_ok=True)

SEGMENTS = [
    "s01-intro", "s02-problem", "s03-airgap", "s04-how-it-works",
    "s05-rust-signer", "s06-base-native", "s07-multichain",
    "s08-open-source", "s09-cta",
]

# (title, subtitle, detail, background_image_path)
SLIDES = [
    ("COLDSTAR", "Air-Gapped Cold Wallet", "Now on Base",
     f"{ASSETS}/promo/hero-image.png"),
    ("THE PROBLEM", "Browser wallets expose keys in memory", "Hardware wallets still connect over USB",
     None),
    ("TRUE AIR GAP", "No USB · No Bluetooth · No WiFi", "QR codes are the only bridge",
     f"{ASSETS}/promo/architecture-flow.png"),
    ("HOW IT WORKS", "Build > QR > Sign Offline > QR > Broadcast", "4 steps · Zero network exposure",
     f"{ASSETS}/screenshots/tui/tui-architecture.png"),
    ("RUST SECURE SIGNER", "mlock · Argon2id · AES-256-GCM · Zeroize", "Keys exist only in locked memory pages",
     f"{ASSETS}/screenshots/tui/tui-features.png"),
    ("BUILT FOR BASE", "secp256k1 ECDSA · EIP-1559 Type 2", "Base Mainnet + Sepolia Testnet",
     None),
    ("MULTICHAIN", "Solana (Ed25519) + Base (secp256k1)", "Same encryption layer · Same air gap",
     f"{ASSETS}/social-preview.png"),
    ("OPEN SOURCE", "18,000 lines · Fully auditable", "Don't trust us · Verify",
     f"{ASSETS}/screenshots/tui/tui-home.png"),
    ("coldstar.dev", "Cold Signing for Base", "github.com/ExpertVagabond/coldstar-colosseum",
     f"{ASSETS}/promo/hero-image.png"),
]

LOGO_PATH = f"{ASSETS}/assets/coldstar-logo.png"
ICON_PATH = f"{ASSETS}/assets/coldstar-icon.png"

GAP = 0.8

# Colors
BASE_BLUE = (0, 82, 255)
WHITE = (255, 255, 255)
GRAY = (138, 138, 154)
GREEN = (0, 210, 106)
BG = (0, 0, 0)
OVERLAY_COLOR = (0, 0, 8)


def get_duration(filepath):
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", filepath],
        capture_output=True, text=True,
    )
    return float(result.stdout.strip())


def get_font(size, bold=False):
    paths = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/HelveticaNeue.ttc",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ]
    for fp in paths:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                continue
    return ImageFont.load_default()


def load_and_fit(img_path, target_w, target_h):
    """Load image and cover-fit to target dimensions."""
    img = Image.open(img_path).convert("RGB")
    iw, ih = img.size
    scale = max(target_w / iw, target_h / ih)
    new_w, new_h = int(iw * scale), int(ih * scale)
    img = img.resize((new_w, new_h), Image.LANCZOS)
    # Center crop
    left = (new_w - target_w) // 2
    top = (new_h - target_h) // 2
    return img.crop((left, top, left + target_w, top + target_h))


def draw_text_with_shadow(draw, xy, text, font, fill, shadow_color=(0, 0, 0), offset=2):
    """Draw text with a drop shadow for readability."""
    x, y = xy
    # Shadow
    for dx in range(-offset, offset + 1):
        for dy in range(-offset, offset + 1):
            draw.text((x + dx, y + dy), text, fill=shadow_color, font=font)
    # Main text
    draw.text(xy, text, fill=fill, font=font)


def centered_text(draw, y, text, font, fill, shadow=True):
    """Draw centered text at given y position."""
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    x = (W - tw) // 2
    if shadow:
        draw_text_with_shadow(draw, (x, y), text, font, fill)
    else:
        draw.text((x, y), text, fill=fill, font=font)


def render_frame(slide_idx, alpha, bg_cache):
    """Render a single video frame."""
    title, subtitle, detail, bg_path = SLIDES[slide_idx]

    # Background
    if bg_path and bg_path in bg_cache:
        img = bg_cache[bg_path].copy()
        # Darken background for text readability
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(0.3)
        # Add dark overlay
        overlay = Image.new("RGB", (W, H), OVERLAY_COLOR)
        img = Image.blend(img, overlay, 0.4)
    else:
        img = Image.new("RGB", (W, H), BG)
        # Subtle blue gradient glow for slides without background
        draw_temp = ImageDraw.Draw(img)
        for r in range(400, 0, -2):
            a = int(15 * (r / 400))
            color = (0, min(a, 12), min(a * 3, 45))
            draw_temp.ellipse(
                [W // 2 - r, H // 2 - r - 40, W // 2 + r, H // 2 + r - 40],
                fill=color,
            )

    draw = ImageDraw.Draw(img)

    # Logo watermark in top-left corner
    if hasattr(render_frame, '_logo') and render_frame._logo:
        logo = render_frame._logo.copy()
        # Fade logo with alpha
        logo_alpha = int(180 * alpha)
        logo_r, logo_g, logo_b, logo_a = logo.split()
        from PIL import ImageChops
        logo_a = logo_a.point(lambda p: min(p, logo_alpha))
        logo = Image.merge("RGBA", (logo_r, logo_g, logo_b, logo_a))
        img.paste(logo, (40, 30), logo)

    # Accent line above title
    line_w = int(200 * alpha)
    if line_w > 0:
        blue_faded = tuple(int(c * alpha) for c in BASE_BLUE)
        draw.rectangle(
            [W // 2 - line_w // 2, H // 2 - 140, W // 2 + line_w // 2, H // 2 - 138],
            fill=blue_faded,
        )

    # Title
    is_accent = slide_idx == 0 or slide_idx == len(SLIDES) - 1
    title_color = BASE_BLUE if is_accent else WHITE
    title_size = 72 if is_accent else 60
    title_font = get_font(title_size, bold=True)
    faded_title = tuple(int(c * alpha) for c in title_color)
    centered_text(draw, H // 2 - 90, title, title_font, faded_title)

    # Subtitle
    sub_alpha = max(0, min(1, (alpha - 0.15) / 0.85))
    sub_font = get_font(28)
    faded_sub = tuple(int(c * sub_alpha) for c in GRAY)
    centered_text(draw, H // 2 + 10, subtitle, sub_font, faded_sub)

    # Detail
    det_alpha = max(0, min(1, (alpha - 0.3) / 0.7))
    det_font = get_font(24)
    faded_det = tuple(int(c * det_alpha) for c in GREEN)
    centered_text(draw, H // 2 + 60, detail, det_font, faded_det)

    # Bottom accent line
    if line_w > 0:
        draw.rectangle(
            [W // 2 - line_w // 3, H // 2 + 110, W // 2 + line_w // 3, H // 2 + 112],
            fill=tuple(int(c * alpha * 0.5) for c in BASE_BLUE),
        )

    # "BASE" badge on first and last slide
    if (slide_idx == 0 or slide_idx == len(SLIDES) - 1) and alpha > 0.5:
        badge_font = get_font(16)
        badge_text = "BASE"
        badge_alpha = min(1, (alpha - 0.5) * 2)
        bbox = draw.textbbox((0, 0), badge_text, font=badge_font)
        bw = bbox[2] - bbox[0] + 20
        bh = bbox[3] - bbox[1] + 10
        bx = W // 2 - bw // 2
        by = H // 2 - 160
        badge_fill = tuple(int(c * badge_alpha) for c in BASE_BLUE)
        draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=4, fill=badge_fill)
        text_color = tuple(int(255 * badge_alpha) for _ in range(3))
        draw.text((bx + 10, by + 3), badge_text, fill=text_color, font=badge_font)

    return img


def main():
    # Pre-load backgrounds
    print("Loading brand assets...")
    bg_cache = {}
    for _, _, _, bg_path in SLIDES:
        if bg_path and bg_path not in bg_cache and os.path.exists(bg_path):
            print(f"  Loading {os.path.basename(bg_path)}...")
            bg_cache[bg_path] = load_and_fit(bg_path, W, H)

    # Pre-load logo
    if os.path.exists(LOGO_PATH):
        logo = Image.open(LOGO_PATH).convert("RGBA")
        # Resize to fit top corner (width ~200px)
        ratio = 200 / logo.width
        logo = logo.resize((200, int(logo.height * ratio)), Image.LANCZOS)
        render_frame._logo = logo
        print(f"  Logo loaded: {logo.size}")
    else:
        render_frame._logo = None

    # Get audio durations
    durations = []
    for seg in SEGMENTS:
        path = os.path.join(AUDIO_DIR, f"{seg}.wav")
        dur = get_duration(path)
        durations.append(dur)
        print(f"  {seg}: {dur:.2f}s")

    total = sum(durations) + GAP * (len(durations) - 1)
    print(f"\nTotal: {total:.1f}s ({int(total // 60)}:{int(total % 60):02d})")

    # Generate each slide as video
    slide_files = []
    for i, (seg, dur) in enumerate(zip(SEGMENTS, durations)):
        title = SLIDES[i][0]
        total_dur = dur + GAP if i < len(SEGMENTS) - 1 else dur
        total_frames = int(total_dur * FPS)

        slide_frames_dir = os.path.join(FRAMES_DIR, f"slide_{i:02d}")
        os.makedirs(slide_frames_dir, exist_ok=True)

        print(f"  Rendering slide {i}: {title} ({total_frames} frames)...", end=" ", flush=True)

        fade_in_frames = int(0.6 * FPS)
        fade_out_frames = int(0.5 * FPS)

        for f in range(total_frames):
            if f < fade_in_frames:
                alpha = f / fade_in_frames
            elif f > total_frames - fade_out_frames:
                alpha = (total_frames - f) / fade_out_frames
            else:
                alpha = 1.0
            alpha = max(0, min(1, alpha))

            img = render_frame(i, alpha, bg_cache)
            img.save(os.path.join(slide_frames_dir, f"frame_{f:05d}.png"))

        print("done")

        # Compose frames + audio
        audio_path = os.path.join(AUDIO_DIR, f"{seg}.wav")
        slide_path = os.path.join(VIDEO_DIR, f"slide_{i:02d}.mp4")
        slide_files.append(slide_path)

        cmd = [
            "ffmpeg", "-y",
            "-framerate", str(FPS),
            "-i", os.path.join(slide_frames_dir, "frame_%05d.png"),
            "-i", audio_path,
            "-c:v", "libx264", "-preset", "fast", "-crf", "23", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k",
            "-t", str(total_dur),
            slide_path,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"    ffmpeg error: {result.stderr[-200:]}")
            return

        # Clean up frames immediately
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

    final_dur = get_duration(OUTPUT)
    mins = int(final_dur // 60)
    secs = int(final_dur % 60)

    print(f"\n{'=' * 50}")
    print(f"  VIDEO COMPLETE")
    print(f"  Output: {OUTPUT}")
    print(f"  Duration: {mins}:{secs:02d}")
    print(f"{'=' * 50}")

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
