#!/usr/bin/env python3
"""
Fix inconsistent icons - regenerate with strict style matching.

Reference style (from icon-assessment, icon-books, icon-blend-it):
- Plain cream background (#FAF8F5) filling entire image
- Single sage green color (#9FC7AA) for the icon
- NO borders, NO frames, NO cards, NO rounded rectangles
- Icon fills about 60-70% of the canvas
- Simple, flat, clean design
"""

import json
import subprocess
import requests
from pathlib import Path
from time import sleep

MULEROUTER_DIR = Path.home() / ".claude/plugins/cache/mulerouter-skills/mulerouter-skills/1.0.0/skills/mulerouter-skills"
OUTPUT_DIR = Path(__file__).parent.parent / "public" / "images" / "icons"

# Very strict style prompt
STYLE = """Simple flat icon on plain solid cream background (#FAF8F5).
Single color only: sage green (#9FC7AA).
NO borders. NO frames. NO cards. NO rounded rectangles around the icon.
The icon should fill about 60-70% of the image, centered.
Minimalist, clean, like a professional app icon.
Plain background with NO patterns, NO gradients, NO shadows.
Only ONE shade of green - do not use multiple greens."""

NEGATIVE = "border, frame, card, rounded rectangle, box, container, multiple colors, gradient, shadow, 3D, pattern, texture, multiple shades of green, dark green, light green variation, photo, realistic, text, words"

# Icons to fix with their descriptions
ICONS_TO_FIX = {
    "icon-target": "Simple target/bullseye with concentric circles and an arrow. Centered, clean.",

    "icon-star": "Simple five-pointed star shape. Just a star, no background shape.",

    "icon-game": "Game controller silhouette. Should be larger, filling more of the canvas.",

    "icon-chart": "Bar chart with 4 bars increasing in height and upward arrow. Larger, filling canvas.",

    "icon-syllable-clap": "Two hands clapping with small dots between them. Single green color only.",

    "icon-letter-match": "Two letter A shapes side by side with small checkmark. Single green color only.",
}


def generate_icon(name: str, description: str) -> bool:
    """Generate icon with strict style."""
    full_prompt = f"{STYLE}\n\nIcon: {description}"
    output_path = OUTPUT_DIR / f"{name}.png"
    backup_path = OUTPUT_DIR / "backup" / f"{name}_v2.png"

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
        "--negative-prompt", NEGATIVE,
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
        print("FAILED - no results")
        return False

    except Exception as e:
        print(f"ERROR: {e}")
        return False


def main():
    print("=" * 50)
    print("FIXING INCONSISTENT ICONS")
    print("=" * 50)
    print(f"Icons to fix: {len(ICONS_TO_FIX)}")
    print()

    success = 0
    for name, description in ICONS_TO_FIX.items():
        if generate_icon(name, description):
            success += 1
        sleep(1)

    print()
    print(f"Done: {success}/{len(ICONS_TO_FIX)} fixed")
    print("Old versions in /backup/")


if __name__ == "__main__":
    main()
