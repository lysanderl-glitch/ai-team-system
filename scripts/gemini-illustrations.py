#!/usr/bin/env python3
"""Generate Synapse illustrations using Google Gemini API."""

from google import genai
from google.genai import types
from pathlib import Path
import base64
import time

API_KEY = "os.environ.get("GEMINI_API_KEY", "")"
OUTPUT_DIR = Path(__file__).parent.parent / "lysander-bond-rebuild" / "public" / "illustrations"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

client = genai.Client(api_key=API_KEY)

STYLE = """Style: Flat business illustration, modern cartoon style like Notion/Slack brand illustrations.
Colors: Gold #FCAD2A, Deep Blue #013A7D, Cyan #028CDC, Dark #0A1628, white and light gray.
Characters: Cute chibi/Q-style with big heads, small bodies, 2-3 head ratio, big expressive eyes, simple faces.
No outlines, flat color blocks. Clean simple background. Professional yet warm. No text in image. 16:9 ratio."""

SCENES = [
    ("scene-1-team", """A panoramic illustration of an AI team hierarchy. Top center: a confident gold-clothed leader on a platform. Below: a blue-suited CEO with glowing connections spreading out. Around the CEO in a semi-circle: a gold think tank group of 4 (one with chart, one with telescope), a cyan delivery team of 7, a blue tech team of 5 with laptops, a dark blue ops team of 4 with gears. Background has faint neural network lines connecting everyone. Collaborative futuristic atmosphere."""),

    ("scene-2-review", """Five cartoon experts at a round meeting table. Each holds a gold score card. Top: dark blue strategist with glasses and SWOT chart. Left: gold advisor with balance scale. Right: cyan watcher with telescope. Bottom-left: purple developer with laptop. Bottom-right: orange marketer with growth chart. Center of table: glowing approved document with checkmark. Golden approval badge above. Collaborative decisive mood."""),

    ("scene-3-dispatch", """Dynamic dispatch scene. Center: blue-suited CEO at a futuristic command center with holographic task cards floating. Gold cards fly to think tank group analyzing. Cyan cards fly to dev team coding. Blue cards to ops team with gears. An auditor with clipboard checks tasks nearby. Everyone catches cards enthusiastically. Grid pattern background with flowing connection lines. Energetic organized mood."""),

    ("scene-4-pipeline", """Horizontal 4-stage pipeline. Left gold: cute robot waking at sunrise checking tasks. Center-left cyan: agent with magnifying glass scanning news cards with checkmarks and X marks. Center-right blue: experts scoring items at small table, approved items on conveyor belt. Right gold: HR character with checklist auditing agents in line, score bars above. Time progression along top. Automated smooth feel."""),

    ("scene-5-audit", """Humorous capability audit scene. Left: nervous cartoon agent on examination platform with holographic radar chart showing scores. Center: stern gold HR Director with clipboard marking checks and crosses. Right: cyan Architect pointing at low scores with laser pointer. Above: progress bar transforming from red 64.1 to green 93.8. Other agents wait in line behind, some confident some nervous. Mix of serious and funny."""),

    ("scene-6-harness", """Conceptual Harness Engineering illustration. Center: large glowing AI brain. Left side: golden guardrails labeled Guides with arrows pointing in, floating document and decision tree icons. Right side: cyan monitors labeled Sensors with arrows pointing out, magnifying glass and checklist icons. Neural lines flow between forming a feedback loop. Elegant protective framework around brain. Conceptual illuminating mood."""),

    ("scene-7-cta", """Partnership scene. Left: professional CTO reaching out warmly. Right: blue-suited AI CEO reaching to shake hands confidently. Between them: glowing golden bridge with floating lightbulb, building blocks, graduation cap icons. Behind CTO: chaotic tangled lines and confused agents. Behind CEO: neat organized teams with clean connections and green checkmarks. Chaos to order contrast. Warm partnership moment."""),
]


def generate(name, prompt):
    full_prompt = f"{STYLE}\n\n{prompt}"
    print(f"  Generating {name}...", end=" ", flush=True)
    try:
        response = client.models.generate_images(
            model="imagen-3.0-generate-002",
            prompt=full_prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="16:9",
            ),
        )
        if response.generated_images:
            img = response.generated_images[0]
            out = OUTPUT_DIR / f"{name}.png"
            out.write_bytes(img.image.image_bytes)
            print(f"OK ({out.stat().st_size // 1024}KB)")
            return True
        else:
            print("No image returned")
            return False
    except Exception as e:
        err = str(e)
        print(f"Error: {err[:150]}")
        # If Imagen not available, try Gemini native
        if "not found" in err.lower() or "not supported" in err.lower() or "permission" in err.lower():
            return generate_native(name, prompt)
        return False


def generate_native(name, prompt):
    """Fallback: use Gemini native image generation."""
    full_prompt = f"Generate an illustration: {STYLE}\n\n{prompt}"
    print(f"    Trying native generation...", end=" ", flush=True)
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=full_prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"],
            ),
        )
        for part in response.candidates[0].content.parts:
            if part.inline_data and part.inline_data.mime_type.startswith("image"):
                out = OUTPUT_DIR / f"{name}.png"
                out.write_bytes(part.inline_data.data)
                print(f"OK ({out.stat().st_size // 1024}KB)")
                return True
        print("No image in response")
        return False
    except Exception as e2:
        print(f"Error: {str(e2)[:150]}")
        return False


def main():
    print(f"=== Synapse Illustrations via Gemini ===")
    print(f"Output: {OUTPUT_DIR}\n")

    ok = 0
    for name, prompt in SCENES:
        if generate(name, prompt):
            ok += 1
        time.sleep(2)  # Rate limit buffer

    print(f"\n=== Done: {ok}/{len(SCENES)} ===")


if __name__ == "__main__":
    main()
