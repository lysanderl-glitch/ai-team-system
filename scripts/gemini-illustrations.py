#!/usr/bin/env python3
"""Generate Synapse illustrations using Google Imagen 4.0 API."""

from google import genai
from google.genai import types
from pathlib import Path
import os
import time

API_KEY = os.environ.get("GEMINI_API_KEY", "")
OUTPUT_DIR = Path(__file__).parent.parent / "lysander-bond-rebuild" / "public" / "illustrations"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

client = genai.Client(api_key=API_KEY)

STYLE = "Flat business illustration, modern cartoon style like Notion and Slack brand illustrations. Color palette: Gold, Deep Blue, Cyan, Dark Navy, white and light gray. Characters are cute chibi Q-style with big heads, small bodies, big expressive eyes, simple happy faces. No outlines, flat color blocks. Clean simple gradient background. Professional yet warm and friendly feel. No text or words in the image."

SCENES = [
    ("scene-1-team", f"{STYLE} A wide panoramic illustration of an AI company team hierarchy. At the top center stands a confident leader figure in gold amber clothing on a small platform, he is the president. Below him a blue-suited AI CEO figure acts as a bridge with glowing golden connection lines spreading outward to teams. Around the CEO arranged in a semi-circle are multiple team clusters: left group of 4 gold-toned advisors one holds a chart another a telescope, center-left group of 7 cyan figures as delivery team, center-right group of 5 blue figures as tech team with laptops, right group of 4 dark blue figures as operations team with gears. Background has faint neural network synapse connection lines. Collaborative futuristic atmosphere. Wide 16:9 composition."),

    ("scene-2-review", f"{STYLE} Five cartoon expert characters sitting around a modern round glass table in a bright meeting room. Each expert holds a golden score card. Top center: a dark blue suited strategist wearing glasses holding a chart. Left: a gold-outfitted advisor holding a balance scale. Right: a cyan-dressed analyst looking through a small telescope. Bottom-left: a purple-hoodie developer with a laptop. Bottom-right: an orange-blazered marketer holding a growth chart. In the center of the table is a glowing document with a big green checkmark. Above the scene floats a golden badge with five stars. The mood is collaborative and decisive with warm lighting."),

    ("scene-3-dispatch", f"{STYLE} A dynamic energetic scene of work being delegated. In the center a blue-suited CEO character stands at a futuristic holographic command center desk. Colorful task cards float in the air around him. Golden cards fly toward a think tank group on the left who are analyzing. Cyan cards fly toward developers on the right who are typing on laptops. Blue cards fly toward an operations team with gears. A character with a clipboard stands nearby checking items off a list. Each team member catches their card enthusiastically with happy expressions. Background has subtle grid pattern. The mood is energetic organized and fun."),

    ("scene-4-pipeline", f"{STYLE} A horizontal timeline pipeline illustration with 4 connected stages flowing left to right with arrows between them. Stage 1 on far left in golden tones: a cute small robot character waking up at sunrise checking a task list clipboard. Stage 2 in cyan tones: an agent character with a big magnifying glass scanning floating news article cards, some cards have green checkmarks others have red X marks. Stage 3 in blue tones: multiple small expert characters around a mini table scoring items with number cards, approved items moving onto a conveyor belt. Stage 4 in golden tones: an HR character with a giant checklist auditing small agent characters standing in a line, score bars floating above them. A clock runs along the top showing time progression from morning to evening."),

    ("scene-5-audit", f"{STYLE} A humorous but professional scene of an AI agent character going through a health check examination. On the left a nervous looking small cartoon character stands on a medical style examination platform looking worried. Next to the character floats a big holographic radar spider chart showing capability scores with some areas highlighted in red and others in green. In the center the HR Director character wearing gold outfit has a stern but fair expression and holds a clipboard marking checks and crosses. On the right a cyan-dressed Capability Architect character points at the low scoring areas on the radar chart with a pointer. Above the scene a progress bar shows transformation from red 64 to bright green 94. Behind them a few other agent characters wait in a queue, some looking confident others nervous."),

    ("scene-6-harness", f"{STYLE} A conceptual educational illustration showing the Harness Engineering framework concept. In the center is a large glowing friendly AI brain character. On the left side golden colored guardrails and guide pathways point toward the brain with floating icons of a document, a decision tree diagram, and team profile cards, these represent Guides or feedforward control. On the right side cyan colored monitoring sensors and scanner eyes point outward from the brain with floating icons of a magnifying glass, a quality checklist, and a score card, these represent Sensors or feedback control. Flowing neural connection lines create a beautiful circular feedback loop connecting the guides and sensors around the brain. The whole composition feels like an elegant protective framework. Illuminating conceptual mood."),

    ("scene-7-cta", f"{STYLE} A warm inviting business partnership scene. On the left a professional CTO character in business attire reaches out with a warm friendly expression and open hand. On the right an AI CEO character in a sharp blue suit reaches to shake hands with a confident welcoming smile. Between them a glowing golden bridge or pathway connects them with small floating icons along it: a lightbulb representing ideas, colorful building blocks representing implementation, and a graduation cap representing training. Behind the CTO on the left side is a messy chaotic background with tangled lines and confused small characters representing disorganized AI. Behind the AI CEO on the right side is a neat beautifully organized system with orderly teams clean connections and green checkmarks. The visual contrast tells the story of transformation from chaos to order."),
]


def generate(name, prompt):
    print(f"  {name}...", end=" ", flush=True)
    try:
        r = client.models.generate_images(
            model="imagen-4.0-generate-001",
            prompt=prompt,
            config=types.GenerateImagesConfig(number_of_images=1, aspect_ratio="16:9"),
        )
        if r.generated_images:
            out = OUTPUT_DIR / f"{name}.png"
            out.write_bytes(r.generated_images[0].image.image_bytes)
            kb = out.stat().st_size // 1024
            print(f"OK ({kb}KB)")
            return True
        print("No image")
        return False
    except Exception as e:
        print(f"Error: {str(e)[:120]}")
        return False


def main():
    print(f"=== Synapse Illustrations (Imagen 4.0) ===\n")
    ok = 0
    for name, prompt in SCENES:
        if generate(name, prompt):
            ok += 1
        time.sleep(3)
    print(f"\n=== {ok}/{len(SCENES)} generated ===")


if __name__ == "__main__":
    main()
