#!/usr/bin/env python3
"""
video-gen.py — Unified CLI entry point for the Video Tutorial Pipeline.

Reads a scenes.json config, generates TTS narration, records HTML animation
via Playwright, and composes the final MP4 with FFmpeg.

Cross-platform: Windows / macOS / Linux.

Usage:
    python video-gen.py --config scenes.json --output output/my-video.mp4
    python video-gen.py --config scenes.json --voice zh-CN-XiaoyiNeural --rate "+5%"
    python video-gen.py --config scenes.json --skip-narration --skip-record

Dependencies:
    pip install edge-tts
    npm install playwright && npx playwright install chromium
    FFmpeg installed (auto-discovered)
"""

import argparse
import asyncio
import base64
import json
import os
import platform
import shutil
import subprocess
import sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = SCRIPT_DIR / "templates"
DEFAULT_OUTPUT_DIR = SCRIPT_DIR / "output"

DEFAULT_VOICE = "zh-CN-YunxiNeural"
DEFAULT_RATE = "+10%"
DEFAULT_VOLUME = "+0%"
DEFAULT_RESOLUTION = (1920, 1080)

# ---------------------------------------------------------------------------
# FFmpeg auto-discovery
# ---------------------------------------------------------------------------

def find_ffmpeg() -> str | None:
    """Search for ffmpeg binary in PATH and common install locations."""
    # 1) shutil.which checks PATH
    found = shutil.which("ffmpeg")
    if found:
        return found

    # 2) Platform-specific common locations
    candidates: list[Path] = []

    if platform.system() == "Windows":
        candidates += [
            Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "WinGet" / "Links" / "ffmpeg.exe",
            Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "FFmpeg" / "bin" / "ffmpeg.exe",
            Path(os.environ.get("ProgramFiles(x86)", "C:/Program Files (x86)")) / "FFmpeg" / "bin" / "ffmpeg.exe",
            Path("C:/ffmpeg/bin/ffmpeg.exe"),
            Path(os.environ.get("USERPROFILE", "")) / "scoop" / "shims" / "ffmpeg.exe",
        ]
        # Also check chocolatey
        choco = Path(os.environ.get("ChocolateyInstall", "C:/ProgramData/chocolatey"))
        candidates.append(choco / "bin" / "ffmpeg.exe")
        # Check WinGet Packages directories (glob for versioned package paths)
        winget_pkgs = Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "WinGet" / "Packages"
        if winget_pkgs.is_dir():
            for pkg_dir in winget_pkgs.iterdir():
                if "FFmpeg" in pkg_dir.name:
                    for bin_path in pkg_dir.rglob("ffmpeg.exe"):
                        candidates.append(bin_path)
    elif platform.system() == "Darwin":
        candidates += [
            Path("/opt/homebrew/bin/ffmpeg"),
            Path("/usr/local/bin/ffmpeg"),
        ]
    else:
        candidates += [
            Path("/usr/bin/ffmpeg"),
            Path("/usr/local/bin/ffmpeg"),
            Path("/snap/bin/ffmpeg"),
        ]

    for c in candidates:
        if c.is_file():
            return str(c)

    return None


def find_node() -> str | None:
    """Find node binary."""
    found = shutil.which("node")
    if found:
        return found
    if platform.system() == "Windows":
        for p in [
            Path(os.environ.get("ProgramFiles", "")) / "nodejs" / "node.exe",
            Path(os.environ.get("LOCALAPPDATA", "")) / "fnm_multishells" / "node.exe",
        ]:
            if p.is_file():
                return str(p)
    return None


# ---------------------------------------------------------------------------
# TTS Narration Generation
# ---------------------------------------------------------------------------

async def generate_narration(scenes: list[dict], voice: str, rate: str, volume: str, output_dir: Path) -> list[Path]:
    """Generate TTS audio for each scene using edge-tts."""
    try:
        import edge_tts
    except ImportError:
        print("ERROR: edge-tts not installed. Run: pip install edge-tts")
        sys.exit(1)

    narration_dir = output_dir / "narration"
    narration_dir.mkdir(parents=True, exist_ok=True)

    output_files: list[Path] = []

    for i, scene in enumerate(scenes, 1):
        narration_text = scene.get("narration", "")
        if not narration_text:
            print(f"  [{i}/{len(scenes)}] {scene.get('id', f'scene_{i}')} — no narration, skipping")
            continue

        scene_id = scene.get("id", f"scene_{i}")
        out_path = narration_dir / f"{scene_id}.mp3"

        print(f"  [{i}/{len(scenes)}] {scene_id}")
        print(f"    Text: {narration_text[:60]}...")

        communicate = edge_tts.Communicate(
            text=narration_text,
            voice=voice,
            rate=rate,
            volume=volume,
        )
        await communicate.save(str(out_path))

        if out_path.exists() and out_path.stat().st_size > 0:
            size_kb = out_path.stat().st_size / 1024
            print(f"    Saved: {out_path.name} ({size_kb:.1f} KB)")
        else:
            print(f"    WARNING: Output file is empty or missing: {out_path}")

        output_files.append(out_path)

    # Write filelist.txt for FFmpeg concatenation
    filelist_path = narration_dir / "filelist.txt"
    with open(filelist_path, "w", encoding="utf-8") as f:
        for fp in output_files:
            f.write(f"file '{fp.name}'\n")

    print(f"  FFmpeg file list: {filelist_path}")
    return output_files


# ---------------------------------------------------------------------------
# HTML Template Injection
# ---------------------------------------------------------------------------

def _convert_screenshot_images_to_base64(scenes_data: dict, config_dir: Path) -> None:
    """For screenshot-demo and training-slide scenes, convert image references to inline base64 data URIs.

    This keeps the generated HTML self-contained (single-file).
    Modifies scenes_data in place.
    """
    for scene in scenes_data.get("scenes", []):
        scene_type = scene.get("type", "")

        # --- screenshot-demo: converts screenshots[].image_path ---
        if scene_type == "screenshot-demo":
            for ss in scene.get("screenshots", []):
                if "image_path" not in ss:
                    continue
                raw = ss["image_path"]
                img_path = Path(raw).resolve() if Path(raw).is_absolute() else (config_dir / raw).resolve()
                if not img_path.is_file():
                    print(f"  WARNING: Screenshot image not found: {img_path}")
                    continue
                with open(img_path, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode()
                ext = img_path.suffix.lstrip(".").lower()
                mime_map = {"jpg": "jpeg", "svg": "svg+xml"}
                mime_ext = mime_map.get(ext, ext)
                ss["image_base64"] = f"data:image/{mime_ext};base64,{b64}"
                size_kb = len(b64) * 3 / 4 / 1024
                print(f"  Embedded screenshot: {ss['image_path']} ({size_kb:.0f} KB)")

        # --- training-slide: converts scene.screenshot ---
        elif scene_type == "training-slide":
            if "screenshot" not in scene:
                continue
            raw = scene["screenshot"]
            img_path = Path(raw).resolve() if Path(raw).is_absolute() else (config_dir / raw).resolve()
            if not img_path.is_file():
                print(f"  WARNING: Screenshot image not found: {img_path}")
                continue
            with open(img_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            ext = img_path.suffix.lstrip(".").lower()
            mime_map = {"jpg": "jpeg", "svg": "svg+xml"}
            mime_ext = mime_map.get(ext, ext)
            scene["image_base64"] = f"data:image/{mime_ext};base64,{b64}"
            size_kb = len(b64) * 3 / 4 / 1024
            print(f"  Embedded screenshot: {scene['screenshot']} ({size_kb:.0f} KB)")


def inject_scenes_into_template(template_path: Path, scenes_data: dict, output_html: Path, config_dir: Path | None = None) -> Path:
    """Read template HTML, inject scenes JSON, write to output_html."""
    # Convert screenshot image paths to base64 before injection
    if config_dir:
        _convert_screenshot_images_to_base64(scenes_data, config_dir)

    template_text = template_path.read_text(encoding="utf-8")

    # Replace the placeholder with actual data
    # Template uses: const SCENES_CONFIG = /*SCENES_DATA*/null;
    # We must replace "/*SCENES_DATA*/null" (including the fallback null) to avoid
    # generating invalid JS like "{ ... }null;"
    json_str = json.dumps(scenes_data, ensure_ascii=False, indent=2)
    if "/*SCENES_DATA*/null" in template_text:
        injected = template_text.replace("/*SCENES_DATA*/null", json_str, 1)
    else:
        injected = template_text.replace("/*SCENES_DATA*/", json_str, 1)

    output_html.parent.mkdir(parents=True, exist_ok=True)
    output_html.write_text(injected, encoding="utf-8")
    print(f"  Injected scenes into template -> {output_html}")
    return output_html


# ---------------------------------------------------------------------------
# Playwright Recording
# ---------------------------------------------------------------------------

def run_playwright_record(html_path: Path, output_dir: Path, node_bin: str, resolution: tuple[int, int]) -> Path:
    """Call record.mjs via Node.js subprocess."""
    record_script = SCRIPT_DIR / "record.mjs"
    if not record_script.exists():
        print(f"ERROR: record.mjs not found at {record_script}")
        sys.exit(1)

    output_webm = output_dir / "recording.webm"

    cmd = [
        node_bin,
        str(record_script),
        "--html", str(html_path),
        "--output", str(output_webm),
        "--width", str(resolution[0]),
        "--height", str(resolution[1]),
    ]

    print(f"  Command: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=str(SCRIPT_DIR))

    if result.returncode != 0:
        print(f"ERROR: Playwright recording failed with exit code {result.returncode}")
        sys.exit(1)

    if not output_webm.exists():
        print(f"ERROR: Recording not found at {output_webm}")
        sys.exit(1)

    print(f"  Recording saved: {output_webm}")
    return output_webm


# ---------------------------------------------------------------------------
# FFmpeg Composition (replaces compose.sh)
# ---------------------------------------------------------------------------

def run_ffmpeg(args: list[str], ffmpeg_bin: str, description: str = "") -> subprocess.CompletedProcess:
    """Run an ffmpeg command, printing the description."""
    cmd = [ffmpeg_bin] + args
    if description:
        print(f"  {description}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  FFmpeg stderr:\n{result.stderr[-500:]}")
    return result


def compose_video(
    recording: Path,
    narration_dir: Path,
    output_path: Path,
    ffmpeg_bin: str,
    bgm_path: Path | None = None,
    bgm_volume: float = 0.08,
) -> Path:
    """Compose final MP4 from recording + narration audio."""
    output_dir = output_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    narration_filelist = narration_dir / "filelist.txt"
    if not narration_filelist.exists():
        print(f"ERROR: Narration filelist not found: {narration_filelist}")
        sys.exit(1)

    # --- Step 1: Concatenate narration with silence gaps ---
    print("  [compose 1/4] Concatenating narration audio...")

    silence_path = output_dir / "silence_500ms.mp3"
    run_ffmpeg(
        ["-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", "0.5", "-q:a", "9", str(silence_path)],
        ffmpeg_bin,
        "Generating 500ms silence...",
    )

    # Build filelist with gaps
    filelist_with_gaps = output_dir / "filelist-with-gaps.txt"
    lines = narration_filelist.read_text(encoding="utf-8").strip().splitlines()

    with open(filelist_with_gaps, "w", encoding="utf-8") as f:
        first = True
        for line in lines:
            if not line.strip():
                continue
            # Extract filename from "file 'name.mp3'"
            fname = line.replace("file '", "").replace("'", "").strip()
            if not first:
                # Relative path from output_dir to silence
                f.write(f"file '{silence_path.name}'\n")
            first = False
            # narration files are in narration/ subdir relative to output_dir
            f.write(f"file 'narration/{fname}'\n")

    narration_combined = output_dir / "narration-combined.mp3"
    result = run_ffmpeg(
        ["-y", "-f", "concat", "-safe", "0", "-i", str(filelist_with_gaps),
         "-c:a", "libmp3lame", "-q:a", "2", str(narration_combined)],
        ffmpeg_bin,
        "Concatenating narration tracks...",
    )
    if result.returncode != 0:
        print("ERROR: Failed to concatenate narration audio.")
        sys.exit(1)
    print(f"  Combined narration: {narration_combined}")

    # --- Step 2: Convert WebM to H.264 ---
    print("  [compose 2/4] Converting WebM to H.264 MP4...")
    video_h264 = output_dir / "video-h264.mp4"
    result = run_ffmpeg(
        ["-y", "-i", str(recording),
         "-c:v", "libx264", "-preset", "medium", "-crf", "18",
         "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an",
         str(video_h264)],
        ffmpeg_bin,
        "Encoding H.264...",
    )
    if result.returncode != 0:
        print("ERROR: Failed to convert video to H.264.")
        sys.exit(1)
    print(f"  H.264 video: {video_h264}")

    # --- Step 3: Merge video + audio ---
    print("  [compose 3/4] Merging video and narration...")

    if bgm_path and bgm_path.is_file():
        print(f"  Background music: {bgm_path} (volume: {bgm_volume})")
        result = run_ffmpeg(
            ["-y",
             "-i", str(video_h264),
             "-i", str(narration_combined),
             "-i", str(bgm_path),
             "-filter_complex",
             f"[1:a]aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo[narration];"
             f"[2:a]aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo,volume={bgm_volume}[bgm];"
             f"[narration][bgm]amix=inputs=2:duration=first:dropout_transition=3[audio_out]",
             "-map", "0:v", "-map", "[audio_out]",
             "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
             "-shortest",
             str(output_path)],
            ffmpeg_bin,
            "Mixing narration + BGM...",
        )
    else:
        if bgm_path:
            print(f"  WARNING: BGM file not found: {bgm_path}")
        result = run_ffmpeg(
            ["-y",
             "-i", str(video_h264),
             "-i", str(narration_combined),
             "-map", "0:v", "-map", "1:a",
             "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
             "-shortest",
             str(output_path)],
            ffmpeg_bin,
            "Merging video + narration...",
        )

    if result.returncode != 0:
        print("ERROR: Failed to merge video and audio.")
        sys.exit(1)

    # --- Step 4: Verify + cleanup ---
    print("  [compose 4/4] Verifying output...")
    if output_path.exists():
        size_mb = output_path.stat().st_size / (1024 * 1024)
        print(f"  Final video: {output_path} ({size_mb:.1f} MB)")
    else:
        print("ERROR: Final output was not created.")
        sys.exit(1)

    # Cleanup intermediate files
    for tmp in [silence_path, filelist_with_gaps, video_h264]:
        if tmp.exists():
            tmp.unlink()
    print("  Cleaned up intermediate files.")

    return output_path


# ---------------------------------------------------------------------------
# Main Pipeline
# ---------------------------------------------------------------------------

def load_config(config_path: Path) -> dict:
    """Load and validate scenes config JSON."""
    if not config_path.exists():
        print(f"ERROR: Config file not found: {config_path}")
        sys.exit(1)
    with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if "scenes" not in data:
        print("ERROR: Config JSON must contain a 'scenes' array.")
        sys.exit(1)
    return data


def resolve_html_source(config: dict, config_path: Path) -> Path:
    """Determine which HTML file to record.

    Priority:
    1. config.meta.html_source (relative to config file)
    2. config.meta.template + scenes injection
    3. Default template (terminal-tutorial.html)
    """
    meta = config.get("meta", {})

    # Direct HTML source
    html_source = meta.get("html_source")
    if html_source:
        p = (config_path.parent / html_source).resolve()
        if p.exists():
            return p
        # Try relative to project root
        p = (SCRIPT_DIR / ".." / ".." / html_source).resolve()
        if p.exists():
            return p
        print(f"ERROR: html_source not found: {html_source}")
        sys.exit(1)

    # Template injection
    template_name = meta.get("template", "terminal-tutorial.html")
    template_path = TEMPLATE_DIR / template_name
    if not template_path.exists():
        print(f"ERROR: Template not found: {template_path}")
        sys.exit(1)

    output_html = DEFAULT_OUTPUT_DIR / "generated-animation.html"
    return inject_scenes_into_template(template_path, config, output_html, config_dir=config_path.parent)


def main():
    parser = argparse.ArgumentParser(
        description="Video Tutorial Pipeline — unified CLI entry point",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python video-gen.py --config scenes.json
  python video-gen.py --config scenes.json --output output/my-video.mp4
  python video-gen.py --config scenes.json --voice zh-CN-XiaoyiNeural --rate "+5%"
  python video-gen.py --config scenes.json --skip-narration --skip-record
        """,
    )
    parser.add_argument("--config", required=True, help="Path to scenes.json config file")
    parser.add_argument("--output", default=None, help="Output MP4 path (default: output/<title>.mp4)")
    parser.add_argument("--voice", default=None, help="TTS voice override")
    parser.add_argument("--rate", default=None, help="TTS rate override (e.g. '+10%%')")
    parser.add_argument("--bgm", default=None, help="Background music file path")
    parser.add_argument("--bgm-volume", type=float, default=0.08, help="BGM volume 0.0-1.0 (default: 0.08)")
    parser.add_argument("--skip-narration", action="store_true", help="Skip TTS narration generation")
    parser.add_argument("--skip-record", action="store_true", help="Skip Playwright recording")
    parser.add_argument("--skip-compose", action="store_true", help="Skip FFmpeg composition")
    args = parser.parse_args()

    print("=" * 50)
    print("  Video Tutorial Pipeline")
    print("=" * 50)
    print()

    # --- Load config ---
    config_path = Path(args.config).resolve()
    config = load_config(config_path)
    meta = config.get("meta", {})
    scenes = config["scenes"]

    title = meta.get("title", "tutorial")
    resolution = tuple(meta.get("resolution", list(DEFAULT_RESOLUTION)))
    voice = args.voice or meta.get("voice", DEFAULT_VOICE)
    rate = args.rate or meta.get("voice_rate", DEFAULT_RATE)
    volume = meta.get("voice_volume", DEFAULT_VOLUME)

    output_dir = DEFAULT_OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = Path(args.output).resolve() if args.output else output_dir / f"{title.replace(' ', '-').lower()}.mp4"

    print(f"  Config:     {config_path}")
    print(f"  Title:      {title}")
    print(f"  Scenes:     {len(scenes)}")
    print(f"  Resolution: {resolution[0]}x{resolution[1]}")
    print(f"  Voice:      {voice}")
    print(f"  Rate:       {rate}")
    print(f"  Output:     {output_path}")
    print()

    # --- Check dependencies ---
    print("[0/3] Checking dependencies...")

    ffmpeg_bin = find_ffmpeg()
    if not ffmpeg_bin and not args.skip_compose:
        print("ERROR: FFmpeg not found.")
        print("  Install: winget install FFmpeg (Windows) / brew install ffmpeg (macOS) / apt install ffmpeg (Linux)")
        sys.exit(1)
    if ffmpeg_bin:
        print(f"  FFmpeg: {ffmpeg_bin}")

    node_bin = find_node()
    if not node_bin and not args.skip_record:
        print("ERROR: Node.js not found.")
        print("  Install from https://nodejs.org/")
        sys.exit(1)
    if node_bin:
        print(f"  Node.js: {node_bin}")

    print()

    # --- Step 1: Generate narration ---
    print("[1/3] Generating TTS narration...")
    if args.skip_narration:
        print("  Skipped (--skip-narration)")
    else:
        asyncio.run(generate_narration(scenes, voice, rate, volume, output_dir))
    print()

    # --- Step 2: Record HTML animation ---
    print("[2/3] Recording HTML animation...")
    recording_path = output_dir / "recording.webm"

    if args.skip_record:
        print("  Skipped (--skip-record)")
        if not recording_path.exists():
            print("  WARNING: No existing recording at output/recording.webm")
    else:
        html_path = resolve_html_source(config, config_path)
        print(f"  HTML source: {html_path}")
        recording_path = run_playwright_record(html_path, output_dir, node_bin, resolution)
    print()

    # --- Step 3: Compose final video ---
    print("[3/3] Composing final video...")
    if args.skip_compose:
        print("  Skipped (--skip-compose)")
    else:
        narration_dir = output_dir / "narration"
        bgm = Path(args.bgm).resolve() if args.bgm else None
        compose_video(recording_path, narration_dir, output_path, ffmpeg_bin, bgm, args.bgm_volume)
    print()

    # --- Done ---
    print("=" * 50)
    print("  Pipeline Complete!")
    print("=" * 50)
    print()
    print(f"  Output: {output_path}")
    print()


if __name__ == "__main__":
    main()
