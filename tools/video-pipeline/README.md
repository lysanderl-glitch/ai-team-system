# SPE Video Tutorial Pipeline

Automated pipeline for producing the SPE (Synapse Personal Engine) video tutorial. Records HTML animations with Playwright, generates AI narration with Edge TTS, and composes the final video with FFmpeg.

## Dependencies

| Tool | Version | Install |
|------|---------|---------|
| Node.js | >= 18 | https://nodejs.org/ |
| Python | >= 3.9 | https://python.org/ |
| FFmpeg | >= 5.0 | `winget install FFmpeg` / `brew install ffmpeg` / `apt install ffmpeg` |
| Playwright | (auto-installed) | `npm install playwright` |
| edge-tts | (auto-installed) | `pip install edge-tts` |

## Directory Structure

```
tools/video-pipeline/
├── README.md                 # This file
├── build.sh                  # One-click pipeline runner
├── record.mjs                # Playwright HTML animation recorder
├── generate-narration.py     # Edge TTS narration generator
├── compose.sh                # FFmpeg video composition
├── narration-text.json       # Scene narration text data
└── output/                   # Generated output
    ├── narration/            # Per-scene audio files
    │   ├── scene_1_hook.mp3
    │   ├── scene_2_capture_intro.mp3
    │   └── ...
    ├── narration-combined.mp3
    ├── recording.webm        # Raw Playwright recording
    └── spe-tutorial-mvp.mp4  # Final composed video
```

## Quick Start

Run the full pipeline with one command:

```bash
cd tools/video-pipeline
bash build.sh
```

This will:
1. Check and install dependencies (Playwright, edge-tts)
2. Generate TTS narration for all scenes
3. Record the HTML animation via headless Chromium
4. Compose the final MP4 video

## Individual Steps

### Generate Narration Only

```bash
python generate-narration.py

# With a different voice
python generate-narration.py --voice zh-CN-XiaoyiNeural

# List available Chinese voices
python generate-narration.py --list-voices
```

### Record Animation Only

```bash
node record.mjs

# With a custom HTML file
node record.mjs path/to/animation.html
```

### Compose Video Only

```bash
bash compose.sh

# With background music
bash compose.sh --bgm path/to/music.mp3 --bgm-volume 0.08
```

## Build Options

```bash
bash build.sh [OPTIONS]

Options:
  --bgm PATH          Add background music
  --bgm-volume N      BGM volume (0.0-1.0, default: 0.08)
  --skip-deps          Skip dependency installation
  --skip-record        Skip Playwright recording
  --skip-narration     Skip TTS generation
  --html PATH          Custom HTML animation file
  --voice NAME         Override TTS voice
  --help               Show usage
```

## Modifying Content

### Change narration text

Edit `narration-text.json`, then rebuild:

```bash
bash build.sh --skip-record
```

### Change voice

```bash
bash build.sh --voice zh-CN-XiaoyiNeural --skip-record
```

### Change animation

Edit the HTML file at `obs/03-process-knowledge/spe-video-animation.html`, then:

```bash
bash build.sh --skip-narration
```

### Recompose with background music

```bash
bash build.sh --skip-deps --skip-record --skip-narration --bgm music.mp3
```

## Animation HTML Requirements

The HTML animation file must set a completion signal for the recorder to detect:

```javascript
// When animation finishes:
document.body.setAttribute('data-animation-complete', 'true');
```

Without this attribute, the recorder will wait up to 5 minutes then save whatever was captured.

## TTS Voice Options

Popular Chinese voices via Edge TTS:

| Voice | Gender | Style |
|-------|--------|-------|
| `zh-CN-YunxiNeural` | Male | Professional, tech-friendly (default) |
| `zh-CN-XiaoyiNeural` | Female | Warm, friendly |
| `zh-CN-YunyangNeural` | Male | News anchor, authoritative |
| `zh-CN-XiaoxiaoNeural` | Female | Young, energetic |

Run `python generate-narration.py --list-voices` for the full list.

## Troubleshooting

**FFmpeg not found**: Ensure FFmpeg is in your PATH. On Windows with Git Bash, you may need to add it manually.

**Playwright browser not installed**: Run `npx playwright install chromium`.

**Edge TTS timeout**: Check your internet connection. Edge TTS requires network access to Microsoft's TTS service.

**Recording is blank**: Ensure the HTML file loads correctly in a browser. Check the file path and that all assets are accessible.

**Video/audio out of sync**: The `compose.sh` script uses `-shortest` to match the shorter of video/audio. Adjust animation timing or narration pacing in `narration-text.json` to better align them.
