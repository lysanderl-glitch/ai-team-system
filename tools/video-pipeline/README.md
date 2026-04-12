# Video Tutorial Pipeline

Automated pipeline for producing video tutorials. Records HTML animations with Playwright, generates AI narration with Edge TTS, and composes the final video with FFmpeg.

## Architecture

```
scenes.json (config)
    |
    v
video-gen.py (unified CLI)
    |
    ├── [1] Edge TTS narration → output/narration/*.mp3
    ├── [2] Template injection → output/generated-animation.html
    ├── [3] Playwright recording → output/recording.webm
    └── [4] FFmpeg composition → output/final.mp4
```

Two layers:
- **CLI layer**: `video-gen.py` — cross-platform Python entry point
- **Skill layer**: `/video-tutorial` — Synapse Skill that generates scenes.json from source docs

## Dependencies

| Tool | Version | Install |
|------|---------|---------|
| Python | >= 3.10 | https://python.org/ |
| Node.js | >= 18 | https://nodejs.org/ |
| FFmpeg | >= 5.0 | `winget install FFmpeg` / `brew install ffmpeg` / `apt install ffmpeg` |
| Playwright | (auto-installed) | `npm install playwright` |
| edge-tts | (auto-installed) | `pip install edge-tts` |

## Directory Structure

```
tools/video-pipeline/
├── README.md                    # This file
├── video-gen.py                 # Unified CLI entry point (Python)
├── scenes-schema.json           # JSON Schema for scenes config
├── record.mjs                   # Playwright HTML animation recorder
├── generate-narration.py        # Edge TTS narration generator (standalone)
├── compose.sh                   # FFmpeg composition (bash, legacy)
├── build.sh                     # One-click pipeline (bash, legacy)
├── narration-text.json          # Legacy narration data (SPE-specific)
├── templates/
│   └── terminal-tutorial.html   # Generic HTML animation template
├── examples/
│   └── spe-tutorial.json        # SPE tutorial scenes config
└── output/                      # Generated output
    ├── narration/               # Per-scene audio files
    ├── generated-animation.html # Template with injected scenes data
    ├── recording.webm           # Raw Playwright recording
    └── *.mp4                    # Final composed video
```

## Quick Start

### Using video-gen.py (recommended)

```bash
cd tools/video-pipeline

# Full pipeline from a scenes config
python video-gen.py --config examples/spe-tutorial.json

# With custom output path
python video-gen.py --config examples/spe-tutorial.json --output output/my-video.mp4

# Override voice and rate
python video-gen.py --config examples/spe-tutorial.json --voice zh-CN-XiaoyiNeural --rate "+5%"

# Skip steps for incremental builds
python video-gen.py --config examples/spe-tutorial.json --skip-narration --skip-record
python video-gen.py --config examples/spe-tutorial.json --skip-narration  # re-record only
python video-gen.py --config examples/spe-tutorial.json --skip-record     # re-narrate only

# Add background music
python video-gen.py --config examples/spe-tutorial.json --bgm music.mp3 --bgm-volume 0.08
```

### Using the legacy bash pipeline

```bash
cd tools/video-pipeline
bash build.sh
```

## video-gen.py Options

```
Options:
  --config PATH         Path to scenes.json config file (required)
  --output PATH         Output MP4 path (default: output/<title>.mp4)
  --voice NAME          TTS voice override
  --rate RATE           TTS rate override (e.g. "+10%")
  --bgm PATH           Background music file
  --bgm-volume FLOAT   BGM volume 0.0-1.0 (default: 0.08)
  --skip-narration      Skip TTS generation (use existing audio)
  --skip-record         Skip Playwright recording (use existing .webm)
  --skip-compose        Skip FFmpeg composition
```

## Scenes Config Format

The scenes config is a JSON file following `scenes-schema.json`. Key structure:

```json
{
  "meta": {
    "title": "Tutorial Title",
    "resolution": [1920, 1080],
    "voice": "zh-CN-YunxiNeural",
    "voice_rate": "+10%",
    "template": "terminal-tutorial.html",
    "brand": {
      "accent_color": "#14b8a6",
      "company": "Company Name"
    }
  },
  "scenes": [
    {
      "id": "scene_1",
      "type": "hook",
      "title": "Title",
      "chaos_items": ["item1", "item2"],
      "hook_cards": ["/cmd1", "/cmd2"],
      "narration": "TTS text for this scene"
    },
    {
      "id": "scene_2",
      "type": "terminal-demo",
      "progress_label": "/cmd1",
      "commands": [
        {
          "input": "/cmd1 arg",
          "output": ["line 1", "line 2"],
          "clear_before": false,
          "delay_after": 2000
        }
      ],
      "sidebar": {
        "type": "info-card",
        "title": "Card Title",
        "content": "<p>HTML content</p>"
      },
      "narration": "TTS text"
    },
    {
      "id": "scene_end",
      "type": "cta",
      "arch_layers": [...],
      "cta_lines": ["line1", "line2"],
      "brand_title": "Product Name",
      "narration": "TTS text"
    }
  ]
}
```

### Scene Types

| Type | Description | Key Fields |
|------|-------------|------------|
| `hook` | Opening hook with chaos-to-order transition | `chaos_items`, `hook_cards`, `title` |
| `terminal-demo` | Terminal command demonstration | `commands`, `sidebar`, `progress_label` |
| `cta` | Closing call-to-action | `arch_layers`, `cta_lines`, `brand_title` |
| `info-screen` | Static information display | `sidebar`, `subtitle` |

### Sidebar Types

| Type | Description |
|------|-------------|
| `info-card` | Free-form HTML card |
| `flow-steps` | Numbered step sequence |
| `color-legend` | Color swatch legend |
| `pdca` | PDCA cycle diagram |
| `diagram` | Generic data diagram |

### HTML Source Resolution

The config can specify HTML in three ways (checked in order):

1. **`meta.html_source`** — Direct path to a pre-built HTML file
2. **`meta.template`** — Template name in `templates/` (scenes data injected automatically)
3. **Default** — Uses `templates/terminal-tutorial.html`

## Creating a New Tutorial

1. **Create scenes config**: Copy `examples/spe-tutorial.json` and modify scenes
2. **Use the /video-tutorial Skill**: Run `/video-tutorial "Topic" --source path/to/doc.html` to auto-generate scenes.json from documentation
3. **Run the pipeline**: `python video-gen.py --config your-scenes.json`

## Individual Components

### record.mjs

```bash
# With named arguments (recommended)
node record.mjs --html path/to/animation.html --output output/recording.webm --width 1920 --height 1080

# Legacy positional argument
node record.mjs path/to/animation.html
```

### generate-narration.py (standalone)

```bash
python generate-narration.py
python generate-narration.py --voice zh-CN-XiaoyiNeural
python generate-narration.py --list-voices
```

## TTS Voice Options

Popular Chinese voices via Edge TTS:

| Voice | Gender | Style |
|-------|--------|-------|
| `zh-CN-YunxiNeural` | Male | Professional, tech-friendly (default) |
| `zh-CN-XiaoyiNeural` | Female | Warm, friendly |
| `zh-CN-YunyangNeural` | Male | News anchor, authoritative |
| `zh-CN-XiaoxiaoNeural` | Female | Young, energetic |

Run `python generate-narration.py --list-voices` for the full list.

## HTML Template Requirements

Custom HTML animations must set a completion signal for the recorder:

```javascript
// When animation finishes:
document.body.setAttribute('data-animation-complete', 'true');
```

Without this attribute, the recorder waits up to 5 minutes then saves whatever was captured.

## Troubleshooting

**FFmpeg not found**: `video-gen.py` auto-searches common install locations. If still not found, ensure FFmpeg is in your PATH.

**Playwright browser not installed**: Run `npx playwright install chromium`.

**Edge TTS timeout**: Check internet connection. Edge TTS requires network access to Microsoft's TTS service.

**Recording is blank**: Ensure the HTML file loads correctly in a browser. Check file path and asset accessibility.

**Video/audio out of sync**: Adjust scene `duration` values in the config, or narration pacing via `voice_rate`.

**Windows path issues**: `video-gen.py` uses `pathlib` throughout for cross-platform compatibility.
