#!/usr/bin/env python3
"""
generate-illustrations.py — 使用 Anthropic API 生成 Synapse 漫画插画
"""

import anthropic
import base64
import json
from pathlib import Path

API_KEY = "os.environ.get("ANTHROPIC_API_KEY", "")
OUTPUT_DIR = Path(__file__).parent.parent / "lysander-bond-rebuild" / "public" / "illustrations"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

STYLE_PREFIX = """Style: Flat business illustration, modern cartoon style similar to Notion/Slack brand illustrations.
Color palette: primarily Gold #FCAD2A, Deep Blue #013A7D, Cyan #028CDC, Dark #0A1628, with white and light gray accents.
Characters: Cute chibi/Q-style (big heads, small bodies, 2-3 head-to-body ratio), expressive eyes, no nose detail, simple but clear facial expressions.
Line style: No outlines or very thin outlines, filled with flat color blocks.
Background: Clean, simple gradient or solid color, not cluttered.
Overall feel: Professional yet warm, like corporate brand illustrations from tech companies.
No text in the image. Wide aspect ratio (16:9)."""

SCENES = [
    {
        "name": "scene-1-team",
        "prompt": """A wide panoramic illustration showing an AI team hierarchy.

At the top center stands a confident leader figure in gold/amber clothing on a subtle elevated platform. Below him, a blue-suited AI CEO figure acts as the bridge, with glowing connection lines spreading outward.

Around the CEO, arranged in a semi-circle, are multiple small team clusters:
- Left group (4 figures in gold tones): Think Tank / Advisory team, one holds a chart, another holds a telescope
- Center-left group (7 figures in cyan): Project delivery team with construction/IoT icons
- Center-right group (5 figures in blue): Tech/development team with laptop/code icons
- Right group (4 figures in dark blue): Operations team with gears/checklist icons

The background has subtle neural network / synapse connection lines in very low opacity, connecting all the teams. The overall composition should feel like a vibrant, organized ecosystem. The atmosphere is collaborative and futuristic."""
    },
    {
        "name": "scene-2-review",
        "prompt": """Five expert characters sitting around a modern round table in a meeting room.

Each expert has a distinct look and holds a golden score card showing 5 out of 5:
1. Top: Strategist - wears glasses, dark blue suit, holds a SWOT chart
2. Left: Decision Advisor - gold outfit, holds a balance scale
3. Right: Trend Watcher - cyan outfit, looks through a small telescope
4. Bottom-left: Developer - purple hoodie, has a laptop
5. Bottom-right: GTM Strategist - orange blazer, holds a growth chart

In the center of the table is a glowing document with a checkmark. Above the scene, a golden badge shows approval. The mood is collaborative and decisive."""
    },
    {
        "name": "scene-3-dispatch",
        "prompt": """A dynamic scene showing work being delegated from a CEO to multiple team members.

Center: An AI CEO figure in blue suit stands at a futuristic command center desk with holographic screens showing task cards floating around him.

Radiating outward, colorful task cards fly toward different team groups:
- Gold cards toward the think tank group who are analyzing
- Cyan cards toward the development team who are coding on laptops
- Blue cards toward the operations team working with gears
- A clipboard-holding auditor figure stands nearby checking off a list

Each receiving team member catches their task card with enthusiasm. The background has a subtle grid pattern and flowing connection lines. The mood is energetic and organized."""
    },
    {
        "name": "scene-4-pipeline",
        "prompt": """A horizontal timeline illustration showing four stages of a daily automation pipeline, connected by flowing arrows.

Stage 1 (left, gold tones): A small cute robot character waking up at sunrise, checking a task list.
Stage 2 (center-left, cyan): An agent character with magnifying glass scanning floating news cards, some with checkmarks some with X marks.
Stage 3 (center-right, blue): Multiple expert characters around a small table scoring items, with approved items moving to a conveyor belt.
Stage 4 (right, gold): An HR character with a giant checklist auditing small characters standing in a line, with score bars floating above.

A clock or time progression runs along the top. The overall feel is automated, smooth, and continuous like a well-oiled machine."""
    },
    {
        "name": "scene-5-audit",
        "prompt": """A humorous but professional scene showing an AI agent character going through a capability health check.

Left: A nervous-looking cartoon character stands on a medical examination platform, with a holographic radar/spider chart floating next to them showing various capability scores.

Center: An HR Director character in gold outfit with a stern but fair expression holds a clipboard with checkmarks and crosses.

Right: A Capability Architect character in cyan points at low-scoring areas on the radar chart with a laser pointer.

Above the scene, a progress bar transforms from red (64.1) to green (93.8). A few other characters wait in line behind, some confident, others nervous. The mood mixes seriousness and humor."""
    },
    {
        "name": "scene-6-harness",
        "prompt": """A conceptual illustration showing the Harness Engineering framework.

Center: A large glowing AI brain figure representing the Model.

Surrounding it like an elegant protective framework:
- Left side labeled Guides: golden guardrails and pathways with arrows pointing into the brain, with floating icons of a document, decision tree, and team cards.
- Right side labeled Sensors: cyan monitoring eyes and scanners with arrows pointing out from the brain, with icons of a magnifying glass, checklist, and score card.

Neural connection lines flow between guides and sensors forming a feedback loop around the brain. The overall mood is conceptual and illuminating, showing organized control without feeling restrictive."""
    },
    {
        "name": "scene-7-cta",
        "prompt": """A warm inviting scene of a business partnership moment.

Left: A professional CTO character in business attire reaching out with a warm expression.
Right: An AI CEO character in blue suit reaching to shake hands with a confident welcoming expression.

Between them, a glowing golden bridge connects them with small floating icons: a lightbulb, building blocks, and a graduation cap.

Behind the CTO: a subtle representation of chaotic AI setup with tangled lines and confused small characters.
Behind the AI CEO: a neat organized Synapse system with orderly teams and clean connections and green checkmarks.

The contrast between chaos and order is the visual story. The mood captures the moment before a great partnership begins."""
    },
]

def generate_image(client, scene):
    """Generate a single illustration using Claude API."""
    full_prompt = f"{STYLE_PREFIX}\n\n{scene['prompt']}"

    print(f"  Generating: {scene['name']}...")

    try:
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": f"Please generate an illustration based on this description:\n\n{full_prompt}"
                }
            ]
        )

        # Check for image content in response
        for block in message.content:
            if hasattr(block, 'type') and block.type == 'image':
                # Save the image
                img_data = base64.b64decode(block.source.data)
                output_path = OUTPUT_DIR / f"{scene['name']}.png"
                output_path.write_bytes(img_data)
                print(f"  ✅ Saved: {output_path} ({len(img_data) // 1024}KB)")
                return True
            elif hasattr(block, 'type') and block.type == 'text':
                # Claude might return text explaining it can't generate images
                if 'image' in block.text.lower() or 'generat' in block.text.lower():
                    print(f"  ⚠️ Response: {block.text[:200]}")

        print(f"  ❌ No image in response")
        return False

    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def main():
    client = anthropic.Anthropic(api_key=API_KEY)

    print(f"=== Synapse Illustration Generator ===")
    print(f"Output: {OUTPUT_DIR}")
    print(f"Scenes: {len(SCENES)}")
    print()

    success = 0
    for scene in SCENES:
        if generate_image(client, scene):
            success += 1

    print(f"\n=== Done: {success}/{len(SCENES)} generated ===")


if __name__ == "__main__":
    main()
