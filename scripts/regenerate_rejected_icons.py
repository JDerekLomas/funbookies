#!/usr/bin/env python3
"""
Regenerate rejected icons with corrected style.

Key fix: NO card container, NO border - just icon on plain cream background.
"""

import json
import subprocess
import requests
from pathlib import Path
from time import sleep

MULEROUTER_DIR = Path.home() / ".claude/plugins/cache/mulerouter-skills/mulerouter-skills/1.0.0/skills/mulerouter-skills"
OUTPUT_DIR = Path(__file__).parent.parent / "public" / "images" / "icons"

# Updated style - emphasize NO card container
STYLE_PREFIX = """Simple flat icon on a plain solid cream background (#FAF8F5).
The background must be completely plain with no borders, no frames, no rounded rectangles, no card containers.
Sage green (#9FC7AA) icon centered on the plain background.
Minimalist, clean illustration floating on the background.
No text, no faces, no 3D effects.
Style like a simple logo or glyph on a plain background.
"""

NEGATIVE_PROMPT = "card, frame, border, rounded rectangle, container, box around icon, app icon style, 3D, shadow, face, eyes, smile, text, words, photo, realistic, busy, colorful background"

# Icons that need regeneration with improved descriptions
ICONS = {
    "icon-books": "Simple stack of 2-3 flat books. Just books on plain background.",

    "icon-chart": "Simple bar chart with 4 bars increasing in height and an upward arrow. Growth chart icon.",

    "icon-first-sounds": "Letter A with a small arrow pointing to an apple shape. Beginning sound concept.",

    "icon-letter-sounds": "Letter block with sound waves coming from it. Letter making sound.",

    "icon-letter-match": "Two letter A shapes side by side with a small checkmark. Matching concept.",

    "icon-letter-drill": "Letter A with circular arrows around it showing repetition/practice.",

    "icon-guided-lesson": "Open book with a pointing finger/hand above it. No face, no smile.",

    "icon-game": "Simple game controller silhouette. Flat gamepad shape.",

    "icon-rhyme-time": "Two word blocks with wavy lines connecting them showing they rhyme.",

    "icon-target": "Simple target with concentric circles and an arrow hitting the center.",

    "icon-syllable-clap": "Two hands in clapping position with small dots between them.",
}


def generate_icon(name: str, description: str) -> bool:
    """Generate a single icon using MuleRouter."""
    full_prompt = f"{STYLE_PREFIX}\n\nIcon: {description}"
    output_path = OUTPUT_DIR / f"{name}.png"
    backup_path = OUTPUT_DIR / "backup" / f"{name}_old.png"

    # Backup existing
    if output_path.exists():
        backup_path.parent.mkdir(exist_ok=True)
        import shutil
        shutil.copy(output_path, backup_path)

    print(f"  {name}...", end=" ", flush=True)

    cmd = [
        "uv", "run", "python",
        str(MULEROUTER_DIR / "models/alibaba/wan2.6-t2i/generation.py"),
        "--prompt", full_prompt,
        "--negative-prompt", NEGATIVE_PROMPT,
        "--size", "1024*1024",
        "--n", "1",
        "--json",
        "--quiet"
    ]

    try:
        result = subprocess.run(
            cmd,
            cwd=str(MULEROUTER_DIR),
            capture_output=True,
            text=True,
            timeout=300
        )

        if result.returncode != 0:
            print(f"FAILED")
            return False

        data = json.loads(result.stdout)
        if data.get("results"):
            image_url = data["results"][0]
            response = requests.get(image_url, timeout=60)
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                print("OK")
                return True
        print("FAILED")
        return False

    except Exception as e:
        print(f"ERROR: {e}")
        return False


def main():
    print("=" * 50)
    print("REGENERATING REJECTED ICONS")
    print("=" * 50)
    print(f"Icons to regenerate: {len(ICONS)}")
    print()

    success = 0
    failed = 0

    for name, description in ICONS.items():
        if generate_icon(name, description):
            success += 1
        else:
            failed += 1
        sleep(1)

    print()
    print("=" * 50)
    print(f"Done: {success} regenerated, {failed} failed")
    print("Old versions backed up to /backup/")
    print("Refresh the review page to see new icons.")


if __name__ == "__main__":
    main()
