#!/usr/bin/env python3
"""
SPE Video Tutorial - AI TTS Narration Generator

Uses Microsoft Edge TTS (free, high-quality neural voices) to generate
narration audio for each scene defined in narration-text.json.

Usage:
    python generate-narration.py [--voice VOICE] [--rate RATE] [--json PATH]

Dependencies:
    pip install edge-tts

Recommended voices:
    - zh-CN-YunxiNeural    (male, professional, good for tech tutorials)
    - zh-CN-XiaoyiNeural   (female, warm, good for guides)
    - zh-CN-YunyangNeural  (male, news anchor style)
"""

import asyncio
import json
import os
import sys
import argparse
from pathlib import Path

try:
    import edge_tts
except ImportError:
    print("ERROR: edge-tts not installed. Run: pip install edge-tts")
    sys.exit(1)


# Paths
SCRIPT_DIR = Path(__file__).parent
DEFAULT_JSON = SCRIPT_DIR / "narration-text.json"
OUTPUT_DIR = SCRIPT_DIR / "output" / "narration"


async def generate_scene_audio(
    scene: dict,
    voice: str,
    rate: str,
    volume: str,
    output_dir: Path,
) -> Path:
    """Generate TTS audio for a single scene."""
    scene_id = scene["id"]
    text = scene["narration"]
    output_path = output_dir / f"{scene_id}.mp3"

    print(f"  Generating: {scene_id}")
    print(f"    Text: {text[:60]}...")

    communicate = edge_tts.Communicate(
        text=text,
        voice=voice,
        rate=rate,
        volume=volume,
    )

    await communicate.save(str(output_path))

    # Verify the file was created and has content
    if output_path.exists() and output_path.stat().st_size > 0:
        size_kb = output_path.stat().st_size / 1024
        print(f"    Saved: {output_path.name} ({size_kb:.1f} KB)")
    else:
        print(f"    WARNING: Output file is empty or missing: {output_path}")

    return output_path


async def generate_all(json_path: Path, voice_override: str = None, rate_override: str = None):
    """Generate narration audio for all scenes."""
    # Load narration config
    if not json_path.exists():
        print(f"ERROR: Narration JSON not found: {json_path}")
        sys.exit(1)

    with open(json_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    voice = voice_override or config.get("voice", "zh-CN-YunxiNeural")
    rate = rate_override or config.get("rate", "+10%")
    volume = config.get("volume", "+0%")
    scenes = config.get("scenes", [])

    if not scenes:
        print("ERROR: No scenes found in narration JSON.")
        sys.exit(1)

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("=== SPE Narration Generator ===")
    print(f"Voice:   {voice}")
    print(f"Rate:    {rate}")
    print(f"Volume:  {volume}")
    print(f"Scenes:  {len(scenes)}")
    print(f"Output:  {OUTPUT_DIR}")
    print("")

    # Generate audio for each scene
    output_files = []
    for i, scene in enumerate(scenes, 1):
        print(f"[{i}/{len(scenes)}] {scene.get('title', scene['id'])}")
        output_path = await generate_scene_audio(scene, voice, rate, volume, OUTPUT_DIR)
        output_files.append(output_path)
        print("")

    # Generate a file list for FFmpeg concatenation
    filelist_path = OUTPUT_DIR / "filelist.txt"
    with open(filelist_path, "w", encoding="utf-8") as f:
        for fp in output_files:
            # Use forward slashes and relative paths for cross-platform FFmpeg compatibility
            rel = fp.name
            f.write(f"file '{rel}'\n")

    print(f"FFmpeg file list: {filelist_path}")
    print("")

    # Also generate a combined narration using concat
    print("Generating combined narration track...")
    combined_path = OUTPUT_DIR.parent / "narration-combined.mp3"

    # We'll let compose.sh handle the actual concatenation via FFmpeg
    # Just output the file list here
    print(f"  (Use compose.sh to concatenate via FFmpeg)")
    print("")

    print("=== Narration Generation Complete ===")
    print(f"Individual files: {OUTPUT_DIR}")
    print(f"File list:        {filelist_path}")

    return output_files


def main():
    parser = argparse.ArgumentParser(description="SPE Video Tutorial - TTS Narration Generator")
    parser.add_argument(
        "--json",
        type=str,
        default=str(DEFAULT_JSON),
        help=f"Path to narration JSON file (default: {DEFAULT_JSON})",
    )
    parser.add_argument(
        "--voice",
        type=str,
        default=None,
        help="TTS voice name (default: from JSON config or zh-CN-YunxiNeural)",
    )
    parser.add_argument(
        "--rate",
        type=str,
        default=None,
        help="Speech rate adjustment (default: from JSON config or +10%%)",
    )
    parser.add_argument(
        "--list-voices",
        action="store_true",
        help="List available Chinese voices and exit",
    )
    args = parser.parse_args()

    if args.list_voices:
        asyncio.run(list_chinese_voices())
        return

    json_path = Path(args.json)
    asyncio.run(generate_all(json_path, args.voice, args.rate))


async def list_chinese_voices():
    """List available Chinese TTS voices."""
    print("Available Chinese voices:")
    print("-" * 60)
    voices = await edge_tts.list_voices()
    zh_voices = [v for v in voices if v["Locale"].startswith("zh-")]
    for v in zh_voices:
        gender = v.get("Gender", "Unknown")
        name = v["ShortName"]
        locale = v["Locale"]
        print(f"  {name:<30} {locale:<10} {gender}")
    print("-" * 60)
    print(f"Total: {len(zh_voices)} Chinese voices")


if __name__ == "__main__":
    main()
