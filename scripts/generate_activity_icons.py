#!/usr/bin/env python3
"""
Generate missing activity icons for FunBookies.

Style: Flat, minimal illustrated icons matching existing FunBookies style
- Cream/off-white background (#FAF8F5)
- Sage green as primary color (#9FC7AA)
- Simple, centered, clear shapes
- Some with wooden block textures
"""

import json
import subprocess
import sys
import requests
from pathlib import Path
from time import sleep

# Base directory for MuleRouter skill
MULEROUTER_DIR = Path.home() / ".claude/plugins/cache/mulerouter-skills/mulerouter-skills/1.0.0/skills/mulerouter-skills"
OUTPUT_DIR = Path(__file__).parent.parent / "public" / "images" / "icons"

# Style description to prepend to all prompts
STYLE_PREFIX = """Flat minimalist icon for a children's educational app.
Cream/off-white background color (#FAF8F5).
Sage green (#9FC7AA) as the main icon color.
Simple, clean, centered illustration.
No text. Square format.
Style similar to modern educational app icons like Khan Academy Kids.
"""

NEGATIVE_PROMPT = "text, words, letters, labels, watermark, signature, photo, realistic, complex, busy, cluttered"

# Icons to generate with their descriptions
ICONS = {
    "icon-chop-it-up": "A pair of scissors cutting a word block into segments. Green scissors cutting wooden letter blocks.",

    "icon-letter-drill": "Letter 'A' wooden block with practice arrows around it suggesting repetition/drilling. Educational practice icon.",

    "icon-read-aloud": "An open book with gentle sound waves coming from it. Book reading out loud icon.",

    "icon-say-the-sound": "Simple stylized lips/mouth shape with a speech bubble containing a sound wave. Speaking phonics icon.",

    "icon-sound-boxes": "Three connected rectangular boxes in a row like Elkonin boxes. Sound segmentation boxes.",

    "icon-voice-blend": "Three blocks merging together with arrows pointing inward, showing blending. Sounds combining icon.",

    "icon-word-chains": "Chain links made of wooden blocks, showing transformation. Connected blocks in a chain.",

    "icon-first-sounds": "Letter 'A' block next to a small apple icon, with an arrow connecting them. Beginning sounds concept.",

    "icon-guided-lesson": "Open book with a friendly pointing hand/finger guiding. Guided reading lesson icon.",

    "icon-letter-match": "Two matching letter 'A' blocks side by side with a checkmark. Matching pairs icon.",

    "icon-letter-sounds": "Single letter block with small speaker/sound waves beside it. Letter-sound correspondence.",

    "icon-rhyme-time": "Two wooden word blocks with matching patterns highlighted. Rhyming concept.",

    "icon-syllable-clap": "Two hands clapping with small dots/beats between them. Syllable counting through clapping.",
}


def generate_icon(name: str, description: str) -> bool:
    """Generate a single icon using MuleRouter."""
    full_prompt = f"{STYLE_PREFIX}\n\nIcon concept: {description}"
    output_path = OUTPUT_DIR / f"{name}.png"

    print(f"  Generating {name}...")
    print(f"    Prompt: {description[:60]}...")

    # Use MuleRouter text-to-image with JSON output
    cmd = [
        "uv", "run", "python",
        str(MULEROUTER_DIR / "models/alibaba/wan2.6-t2i/generation.py"),
        "--prompt", full_prompt,
        "--negative-prompt", NEGATIVE_PROMPT,
        "--size", "1024*1024",
        "--n", "1",  # Only generate 1 image
        "--json",
        "--quiet"
    ]

    try:
        result = subprocess.run(
            cmd,
            cwd=str(MULEROUTER_DIR),
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )

        if result.returncode != 0:
            print(f"    FAILED: {result.stderr[:200] if result.stderr else 'Unknown error'}")
            return False

        # Parse JSON output to get image URL
        try:
            data = json.loads(result.stdout)
            if data.get("results"):
                image_url = data["results"][0]
                print(f"    Downloading from {image_url[:50]}...")

                # Download the image
                response = requests.get(image_url, timeout=60)
                if response.status_code == 200:
                    with open(output_path, 'wb') as f:
                        f.write(response.content)
                    print(f"    OK - saved to {output_path}")
                    return True
                else:
                    print(f"    FAILED to download: HTTP {response.status_code}")
                    return False
            else:
                print(f"    FAILED: No results in response")
                print(f"    Response: {result.stdout[:200]}")
                return False
        except json.JSONDecodeError as e:
            print(f"    FAILED to parse JSON: {e}")
            print(f"    Output: {result.stdout[:200]}")
            return False

    except subprocess.TimeoutExpired:
        print(f"    TIMEOUT after 5 minutes")
        return False
    except Exception as e:
        print(f"    ERROR: {e}")
        return False


def main():
    print("=" * 60)
    print("GENERATING ACTIVITY ICONS FOR FUNBOOKIES")
    print("=" * 60)
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Icons to generate: {len(ICONS)}")
    print()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    success = 0
    failed = 0

    for name, description in ICONS.items():
        output_path = OUTPUT_DIR / f"{name}.png"
        if output_path.exists():
            print(f"  Skipping {name} (already exists)")
            success += 1
            continue

        if generate_icon(name, description):
            success += 1
        else:
            failed += 1

        # Small delay between requests
        sleep(1)

    print()
    print("=" * 60)
    print(f"DONE: {success} generated, {failed} failed")
    print("=" * 60)


if __name__ == "__main__":
    main()
