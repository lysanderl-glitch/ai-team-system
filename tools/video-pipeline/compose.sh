#!/bin/bash
# =============================================================================
# SPE Video Tutorial - FFmpeg Composition Script
#
# Combines Playwright-recorded video with TTS narration audio into final MP4.
#
# Usage:
#   bash compose.sh [--bgm path/to/bgm.mp3] [--bgm-volume 0.1]
#
# Prerequisites:
#   - FFmpeg installed and available in PATH
#   - Recording exists at: output/recording.webm
#   - Narration files exist at: output/narration/*.mp3
# =============================================================================

set -euo pipefail

# --- Configuration ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="${SCRIPT_DIR}/output"
NARRATION_DIR="${OUTPUT_DIR}/narration"

RECORDING="${OUTPUT_DIR}/recording.webm"
NARRATION_FILELIST="${NARRATION_DIR}/filelist.txt"
NARRATION_COMBINED="${OUTPUT_DIR}/narration-combined.mp3"
VIDEO_H264="${OUTPUT_DIR}/video-h264.mp4"
FINAL_OUTPUT="${OUTPUT_DIR}/spe-tutorial-mvp.mp4"

BGM_PATH=""
BGM_VOLUME="0.08"

# --- Parse Arguments ---
while [[ $# -gt 0 ]]; do
  case $1 in
    --bgm)
      BGM_PATH="$2"
      shift 2
      ;;
    --bgm-volume)
      BGM_VOLUME="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: bash compose.sh [--bgm path/to/bgm.mp3] [--bgm-volume 0.1]"
      exit 1
      ;;
  esac
done

# --- Checks ---
echo "=== SPE Video Composition ==="
echo ""

# Check FFmpeg
if ! command -v ffmpeg &> /dev/null; then
  echo "ERROR: FFmpeg not found in PATH."
  echo "Install FFmpeg: https://ffmpeg.org/download.html"
  echo "  Windows: winget install FFmpeg"
  echo "  macOS:   brew install ffmpeg"
  echo "  Linux:   sudo apt install ffmpeg"
  exit 1
fi

echo "FFmpeg version: $(ffmpeg -version | head -n 1)"
echo ""

# Check recording
if [[ ! -f "${RECORDING}" ]]; then
  echo "ERROR: Recording not found: ${RECORDING}"
  echo "Run record.mjs first: node record.mjs"
  exit 1
fi

# Check narration files
if [[ ! -f "${NARRATION_FILELIST}" ]]; then
  echo "ERROR: Narration file list not found: ${NARRATION_FILELIST}"
  echo "Run generate-narration.py first: python generate-narration.py"
  exit 1
fi

echo "Input recording: ${RECORDING}"
echo "Narration files: ${NARRATION_DIR}"
echo "Output:          ${FINAL_OUTPUT}"
echo ""

# --- Step 1: Concatenate narration audio ---
echo "[1/4] Concatenating narration audio..."

# Add 0.5s silence between scenes for natural pacing
# First, generate a short silence file
SILENCE="${OUTPUT_DIR}/silence_500ms.mp3"
ffmpeg -y -f lavfi -i anullsrc=r=44100:cl=mono -t 0.5 -q:a 9 "${SILENCE}" 2>/dev/null

# Build a new filelist with silence gaps
FILELIST_WITH_GAPS="${OUTPUT_DIR}/filelist-with-gaps.txt"
> "${FILELIST_WITH_GAPS}"

FIRST=true
while IFS= read -r line; do
  # Skip empty lines
  [[ -z "${line}" ]] && continue

  # Extract the filename from the line (format: file 'filename.mp3')
  FNAME=$(echo "${line}" | sed "s/file '//;s/'//")

  if [[ "${FIRST}" == true ]]; then
    FIRST=false
  else
    # Add silence between scenes
    echo "file '$(basename "${SILENCE}")'" >> "${FILELIST_WITH_GAPS}"
  fi

  echo "file 'narration/${FNAME}'" >> "${FILELIST_WITH_GAPS}"
done < "${NARRATION_FILELIST}"

# Concatenate using FFmpeg
ffmpeg -y -f concat -safe 0 -i "${FILELIST_WITH_GAPS}" \
  -c:a libmp3lame -q:a 2 \
  "${NARRATION_COMBINED}" 2>/dev/null

if [[ -f "${NARRATION_COMBINED}" ]]; then
  DURATION=$(ffmpeg -i "${NARRATION_COMBINED}" 2>&1 | grep "Duration" | awk '{print $2}' | tr -d ',')
  echo "  Combined narration: ${NARRATION_COMBINED} (${DURATION})"
else
  echo "  ERROR: Failed to create combined narration."
  exit 1
fi
echo ""

# --- Step 2: Convert WebM to H.264 MP4 ---
echo "[2/4] Converting WebM to H.264 MP4..."

ffmpeg -y -i "${RECORDING}" \
  -c:v libx264 \
  -preset medium \
  -crf 18 \
  -pix_fmt yuv420p \
  -movflags +faststart \
  -an \
  "${VIDEO_H264}" 2>/dev/null

if [[ -f "${VIDEO_H264}" ]]; then
  VID_DURATION=$(ffmpeg -i "${VIDEO_H264}" 2>&1 | grep "Duration" | awk '{print $2}' | tr -d ',')
  echo "  H.264 video: ${VIDEO_H264} (${VID_DURATION})"
else
  echo "  ERROR: Failed to convert video."
  exit 1
fi
echo ""

# --- Step 3: Merge video + audio ---
echo "[3/4] Merging video and narration..."

if [[ -n "${BGM_PATH}" && -f "${BGM_PATH}" ]]; then
  # With background music: mix narration + BGM, then merge with video
  echo "  Background music: ${BGM_PATH} (volume: ${BGM_VOLUME})"

  ffmpeg -y \
    -i "${VIDEO_H264}" \
    -i "${NARRATION_COMBINED}" \
    -i "${BGM_PATH}" \
    -filter_complex " \
      [1:a]aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo[narration]; \
      [2:a]aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo,volume=${BGM_VOLUME}[bgm]; \
      [narration][bgm]amix=inputs=2:duration=first:dropout_transition=3[audio_out] \
    " \
    -map 0:v \
    -map "[audio_out]" \
    -c:v copy \
    -c:a aac -b:a 192k \
    -shortest \
    "${FINAL_OUTPUT}" 2>/dev/null
else
  # Without background music: just merge narration with video
  echo "  No background music (use --bgm to add)"

  ffmpeg -y \
    -i "${VIDEO_H264}" \
    -i "${NARRATION_COMBINED}" \
    -map 0:v \
    -map 1:a \
    -c:v copy \
    -c:a aac -b:a 192k \
    -shortest \
    "${FINAL_OUTPUT}" 2>/dev/null
fi

echo ""

# --- Step 4: Verify output ---
echo "[4/4] Verifying output..."

if [[ -f "${FINAL_OUTPUT}" ]]; then
  FINAL_SIZE=$(du -h "${FINAL_OUTPUT}" | cut -f1)
  FINAL_DURATION=$(ffmpeg -i "${FINAL_OUTPUT}" 2>&1 | grep "Duration" | awk '{print $2}' | tr -d ',')
  echo "  Final video:    ${FINAL_OUTPUT}"
  echo "  Duration:       ${FINAL_DURATION}"
  echo "  Size:           ${FINAL_SIZE}"
else
  echo "  ERROR: Final output was not created."
  exit 1
fi

echo ""

# --- Cleanup ---
echo "Cleaning up intermediate files..."
rm -f "${SILENCE}" "${FILELIST_WITH_GAPS}" "${VIDEO_H264}"
echo "  Kept: ${FINAL_OUTPUT}"
echo "  Kept: ${NARRATION_COMBINED}"
echo "  Kept: ${NARRATION_DIR}/*.mp3"

echo ""
echo "=== Composition Complete ==="
echo "Final output: ${FINAL_OUTPUT}"
