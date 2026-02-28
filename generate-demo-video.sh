#!/bin/bash
# Generate Coldstar for Base demo video from voiceover + animated slides
# Requires: ffmpeg, the voiceover WAV from generate-coldstar-base.py

set -e

AUDIO_DIR="/Volumes/Virtual Server/projects/coldstar/demo-audio"
VIDEO_DIR="/Volumes/Virtual Server/projects/coldstar/demo-video"
VOICEOVER="$AUDIO_DIR/coldstar-base-voiceover.wav"
OUTPUT="$VIDEO_DIR/coldstar-base-demo.mp4"

mkdir -p "$VIDEO_DIR/frames"

# Check voiceover exists
if [ ! -f "$VOICEOVER" ]; then
    echo "ERROR: Voiceover not found at $VOICEOVER"
    echo "Run generate-coldstar-base.py first."
    exit 1
fi

# Get total duration
TOTAL_DURATION=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$VOICEOVER")
echo "Voiceover duration: ${TOTAL_DURATION}s"

# Get individual segment durations for timing
declare -a SEG_DURATIONS
declare -a SEG_NAMES
for f in "$AUDIO_DIR"/s0*.wav; do
    name=$(basename "$f" .wav)
    dur=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$f")
    SEG_NAMES+=("$name")
    SEG_DURATIONS+=("$dur")
    echo "  $name: ${dur}s"
done

# ── Generate title card frames as SVGs → PNGs using ffmpeg drawtext ──

# Colors
BG="#000000"
BASE_BLUE="#0052FF"
WHITE="#ffffff"
GRAY="#8a8a9a"
GREEN="#00D26A"

# Slide content mapped to segments
# Format: "TITLE|SUBTITLE|DETAIL"
declare -a SLIDES
SLIDES=(
    "COLDSTAR|Air-Gapped Cold Wallet|Now on Base"
    "THE PROBLEM|Browser wallets expose keys in memory|Hardware wallets still connect over USB"
    "TRUE AIR GAP|No USB · No Bluetooth · No WiFi|QR codes are the only bridge"
    "HOW IT WORKS|Build → QR → Sign Offline → QR → Broadcast|4 steps · Zero network exposure"
    "RUST SECURE SIGNER|mlock · Argon2id · AES-256-GCM · Zeroize|Keys exist only in locked memory pages"
    "BUILT FOR BASE|secp256k1 ECDSA · EIP-1559 Type 2|Base Mainnet + Sepolia Testnet"
    "MULTICHAIN|Solana (Ed25519) + Base (secp256k1)|Same encryption layer · Same air gap"
    "OPEN SOURCE|18,000 lines · Fully auditable|Don't trust us · Verify"
    "coldstar.dev|Cold Signing for Base|github.com/ExpertVagabond/coldstar-colosseum"
)

# Calculate cumulative start times (with 0.8s gap between segments)
declare -a START_TIMES
CUMULATIVE=0
GAP=0.8
for i in "${!SEG_DURATIONS[@]}"; do
    START_TIMES+=("$CUMULATIVE")
    dur="${SEG_DURATIONS[$i]}"
    CUMULATIVE=$(echo "$CUMULATIVE + $dur + $GAP" | bc)
done

echo ""
echo "Building video with ffmpeg complex filter..."

# Build the ffmpeg filter for animated text overlays
# We create a base black video, then overlay text for each segment

# First, create base video with the audio
# Use drawtext filter chain for each slide

# Build filter_complex string
FILTER=""

# Base: black background at 1920x1080
FILTER+="color=c=black:s=1920x1080:d=${TOTAL_DURATION}:r=30[base];"

# For each segment, we add text overlays with fade in/out
for i in "${!SLIDES[@]}"; do
    IFS='|' read -r TITLE SUBTITLE DETAIL <<< "${SLIDES[$i]}"
    start="${START_TIMES[$i]}"
    dur="${SEG_DURATIONS[$i]}"

    # Fade in over 0.5s, hold, fade out over 0.3s
    fade_in="0.4"
    fade_out="0.3"

    # Alpha expression: fade in, hold, fade out
    # enable between start and start+dur
    enable="between(t,${start},${start}+${dur})"
    alpha_expr="if(lt(t-${start},${fade_in}),(t-${start})/${fade_in},if(gt(t-${start},${dur}-${fade_out}),(${dur}-(t-${start}))/${fade_out},1))"

    if [ $i -eq 0 ]; then
        prev="base"
    else
        prev="v${i}"
    fi
    next="v$((i+1))"

    # Title (large, white or blue for first/last)
    if [ $i -eq 0 ] || [ $i -eq 8 ]; then
        title_color="${BASE_BLUE}"
        title_size=72
    else
        title_color="${WHITE}"
        title_size=64
    fi

    # Escape colons in text for ffmpeg
    TITLE_ESC=$(echo "$TITLE" | sed "s/:/\\\\:/g")
    SUBTITLE_ESC=$(echo "$SUBTITLE" | sed "s/:/\\\\:/g" | sed "s/·/•/g")
    DETAIL_ESC=$(echo "$DETAIL" | sed "s/:/\\\\:/g" | sed "s/·/•/g")

    # Draw title
    FILTER+="[${prev}]drawtext=text='${TITLE_ESC}':fontsize=${title_size}:fontcolor=${title_color}@%{eif\\:${alpha_expr}\\:d\\:2}:x=(w-text_w)/2:y=(h-text_h)/2-80:enable='${enable}'[t${i}a];"

    # Draw subtitle
    FILTER+="[t${i}a]drawtext=text='${SUBTITLE_ESC}':fontsize=28:fontcolor=${GRAY}@%{eif\\:${alpha_expr}\\:d\\:2}:x=(w-text_w)/2:y=(h-text_h)/2+20:enable='${enable}'[t${i}b];"

    # Draw detail line
    FILTER+="[t${i}b]drawtext=text='${DETAIL_ESC}':fontsize=24:fontcolor=${GREEN}@%{eif\\:${alpha_expr}\\:d\\:2}:x=(w-text_w)/2:y=(h-text_h)/2+70:enable='${enable}'[${next}];"

done

# Remove trailing semicolon, map final output
LAST_V="v${#SLIDES[@]}"
FILTER="${FILTER%;}"

echo "$FILTER" > "$VIDEO_DIR/filter.txt"

# Use a simpler approach: generate individual slide videos and concatenate

echo "Generating individual slide videos..."

for i in "${!SLIDES[@]}"; do
    IFS='|' read -r TITLE SUBTITLE DETAIL <<< "${SLIDES[$i]}"
    dur="${SEG_DURATIONS[$i]}"
    seg_audio="$AUDIO_DIR/${SEG_NAMES[$i]}.wav"
    slide_video="$VIDEO_DIR/frames/slide_${i}.mp4"

    # Add gap duration to segment
    if [ $i -lt $((${#SLIDES[@]}-1)) ]; then
        total_dur=$(echo "$dur + $GAP" | bc)
    else
        total_dur="$dur"
    fi

    # Escape special chars for drawtext
    TITLE_ESC=$(echo "$TITLE" | sed "s/:/\\\\:/g" | sed "s/'/\\\\'/g")
    SUBTITLE_ESC=$(echo "$SUBTITLE" | sed "s/:/\\\\:/g" | sed "s/'/\\\\'/g" | sed "s/·/*/g")
    DETAIL_ESC=$(echo "$DETAIL" | sed "s/:/\\\\:/g" | sed "s/'/\\\\'/g" | sed "s/·/*/g")

    # Title styling
    if [ $i -eq 0 ] || [ $i -eq 8 ]; then
        TCOLOR="0052FF"
        TSIZE=72
    else
        TCOLOR="ffffff"
        TSIZE=60
    fi

    echo "  Slide $i: $TITLE (${total_dur}s)"

    # Generate video with text overlay and audio
    ffmpeg -y \
        -f lavfi -i "color=c=black:s=1920x1080:d=${total_dur}:r=30" \
        -i "$seg_audio" \
        -filter_complex "\
[0:v]drawtext=text='${TITLE_ESC}':\
fontsize=${TSIZE}:fontcolor=0x${TCOLOR}:\
x=(w-text_w)/2:y=(h/2)-80:\
alpha='if(lt(t,0.5),t/0.5,if(gt(t,${total_dur}-0.4),(${total_dur}-t)/0.4,1))',\
drawtext=text='${SUBTITLE_ESC}':\
fontsize=26:fontcolor=0x8a8a9a:\
x=(w-text_w)/2:y=(h/2)+20:\
alpha='if(lt(t,0.7),t/0.7,if(gt(t,${total_dur}-0.4),(${total_dur}-t)/0.4,1))',\
drawtext=text='${DETAIL_ESC}':\
fontsize=22:fontcolor=0x00D26A:\
x=(w-text_w)/2:y=(h/2)+70:\
alpha='if(lt(t,0.9),t/0.9,if(gt(t,${total_dur}-0.4),(${total_dur}-t)/0.4,1))'\
[v]" \
        -map "[v]" -map 1:a \
        -c:v libx264 -preset fast -crf 23 -pix_fmt yuv420p \
        -c:a aac -b:a 192k \
        -shortest \
        "$slide_video" \
        2>/dev/null
done

# Concatenate all slides
echo ""
echo "Concatenating slides..."
CONCAT_FILE="$VIDEO_DIR/concat.txt"
> "$CONCAT_FILE"
for i in "${!SLIDES[@]}"; do
    echo "file 'frames/slide_${i}.mp4'" >> "$CONCAT_FILE"
done

ffmpeg -y -f concat -safe 0 \
    -i "$CONCAT_FILE" \
    -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p \
    -c:a aac -b:a 192k \
    "$OUTPUT" \
    2>/dev/null

# Get final duration
FINAL_DUR=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$OUTPUT")
MINS=$(echo "$FINAL_DUR / 60" | bc)
SECS=$(echo "$FINAL_DUR % 60 / 1" | bc)

echo ""
echo "========================================="
echo "  VIDEO COMPLETE"
echo "  Output: $OUTPUT"
echo "  Duration: ${MINS}:$(printf '%02d' $SECS)"
echo "========================================="

# Copy to Desktop
cp "$OUTPUT" ~/Desktop/coldstar-base-demo.mp4
echo "  Copied to ~/Desktop/coldstar-base-demo.mp4"
