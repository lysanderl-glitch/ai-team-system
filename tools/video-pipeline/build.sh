#!/bin/bash
# =============================================================================
# SPE Video Tutorial - One-Click Build Pipeline
#
# Runs the complete video production pipeline:
#   1. Install dependencies
#   2. Generate TTS narration audio
#   3. Record HTML animation via Playwright
#   4. Compose final video with FFmpeg
#
# Usage:
#   bash build.sh [--bgm path/to/bgm.mp3] [--skip-deps] [--skip-record]
#
# Options:
#   --bgm PATH       Add background music to the final video
#   --bgm-volume N   Background music volume (0.0-1.0, default: 0.08)
#   --skip-deps      Skip dependency installation
#   --skip-record    Skip recording (use existing recording.webm)
#   --skip-narration Skip narration generation (use existing audio)
#   --html PATH      Custom path to HTML animation file
#   --voice NAME     Override TTS voice (default: zh-CN-YunxiNeural)
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --- Defaults ---
SKIP_DEPS=false
SKIP_RECORD=false
SKIP_NARRATION=false
BGM_ARG=""
HTML_ARG=""
VOICE_ARG=""

# --- Parse Arguments ---
while [[ $# -gt 0 ]]; do
  case $1 in
    --bgm)
      BGM_ARG="--bgm $2"
      shift 2
      ;;
    --bgm-volume)
      BGM_ARG="${BGM_ARG} --bgm-volume $2"
      shift 2
      ;;
    --skip-deps)
      SKIP_DEPS=true
      shift
      ;;
    --skip-record)
      SKIP_RECORD=true
      shift
      ;;
    --skip-narration)
      SKIP_NARRATION=true
      shift
      ;;
    --html)
      HTML_ARG="$2"
      shift 2
      ;;
    --voice)
      VOICE_ARG="--voice $2"
      shift 2
      ;;
    --help|-h)
      head -n 20 "$0" | tail -n +2 | sed 's/^# //' | sed 's/^#//'
      exit 0
      ;;
    *)
      echo "Unknown option: $1 (use --help for usage)"
      exit 1
      ;;
  esac
done

echo "============================================="
echo "  SPE Video Tutorial Pipeline"
echo "============================================="
echo ""
echo "Working directory: ${SCRIPT_DIR}"
echo ""

# Track timing
START_TIME=$(date +%s)

# =============================================
# Step 1: Install dependencies
# =============================================
echo "--- [1/4] Dependencies ---"

if [[ "${SKIP_DEPS}" == true ]]; then
  echo "  Skipped (--skip-deps)"
else
  echo "  Checking Node.js..."
  if command -v node &> /dev/null; then
    echo "    Node.js $(node --version) found"
  else
    echo "    ERROR: Node.js not found. Install from https://nodejs.org/"
    exit 1
  fi

  echo "  Checking Python..."
  if command -v python &> /dev/null; then
    PYTHON_CMD="python"
  elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
  else
    echo "    ERROR: Python not found. Install from https://python.org/"
    exit 1
  fi
  echo "    Python: $($PYTHON_CMD --version)"

  echo "  Checking FFmpeg..."
  if command -v ffmpeg &> /dev/null; then
    echo "    FFmpeg found"
  else
    echo "    ERROR: FFmpeg not found."
    echo "    Install: winget install FFmpeg (Windows) / brew install ffmpeg (macOS)"
    exit 1
  fi

  echo "  Installing npm packages..."
  cd "${SCRIPT_DIR}"
  if [[ ! -d "node_modules" ]] || [[ ! -d "node_modules/playwright" ]]; then
    npm init -y > /dev/null 2>&1 || true
    npm install playwright > /dev/null 2>&1
    npx playwright install chromium > /dev/null 2>&1
    echo "    Playwright installed"
  else
    echo "    Playwright already installed"
  fi

  echo "  Installing Python packages..."
  $PYTHON_CMD -m pip install edge-tts --quiet 2>/dev/null || \
    pip install edge-tts --quiet 2>/dev/null
  echo "    edge-tts installed"
fi
echo ""

# Determine python command for later use
if command -v python &> /dev/null; then
  PYTHON_CMD="python"
elif command -v python3 &> /dev/null; then
  PYTHON_CMD="python3"
fi

# =============================================
# Step 2: Generate TTS narration
# =============================================
echo "--- [2/4] Generating TTS Narration ---"

if [[ "${SKIP_NARRATION}" == true ]]; then
  echo "  Skipped (--skip-narration)"
else
  cd "${SCRIPT_DIR}"
  $PYTHON_CMD generate-narration.py ${VOICE_ARG}
fi
echo ""

# =============================================
# Step 3: Record HTML animation
# =============================================
echo "--- [3/4] Recording HTML Animation ---"

if [[ "${SKIP_RECORD}" == true ]]; then
  echo "  Skipped (--skip-record)"
  if [[ ! -f "${SCRIPT_DIR}/output/recording.webm" ]]; then
    echo "  WARNING: No existing recording found at output/recording.webm"
    echo "  The compose step will fail without a recording."
  fi
else
  cd "${SCRIPT_DIR}"
  node record.mjs ${HTML_ARG}
fi
echo ""

# =============================================
# Step 4: Compose final video
# =============================================
echo "--- [4/4] Composing Final Video ---"

cd "${SCRIPT_DIR}"
bash compose.sh ${BGM_ARG}
echo ""

# =============================================
# Done
# =============================================
END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))

echo "============================================="
echo "  Pipeline Complete!"
echo "============================================="
echo ""
echo "  Output: ${SCRIPT_DIR}/output/spe-tutorial-mvp.mp4"
echo "  Time:   ${ELAPSED} seconds"
echo ""
echo "  To replay with different settings:"
echo "    bash build.sh --skip-deps --skip-record  (recompose only)"
echo "    bash build.sh --bgm music.mp3            (add background music)"
echo "    bash build.sh --voice zh-CN-XiaoyiNeural (change voice)"
echo ""
