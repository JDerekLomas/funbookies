#!/usr/bin/env python3
"""
Generate additional UI icons for FunBookies.
"""

import json
import subprocess
import requests
from pathlib import Path
from time import sleep

MULEROUTER_DIR = Path.home() / ".claude/plugins/cache/mulerouter-skills/mulerouter-skills/1.0.0/skills/mulerouter-skills"
OUTPUT_DIR = Path(__file__).parent.parent / "public" / "images" / "icons"

STYLE_PREFIX = """Flat minimalist icon for a children's educational app.
Cream/off-white background color (#FAF8F5).
Sage green (#9FC7AA) as the main icon color.
Simple, clean, centered illustration.
No text. Square format.
"""

NEGATIVE_PROMPT = "text, words, letters, labels, watermark, signature, photo, realistic, complex, busy, cluttered"

ICONS = {
    "icon-books": "A small stack of 2-3 books, slightly angled. Library or reading collection icon.",
    "icon-game": "A game controller or joystick. Play/practice activities icon.",
    "icon-target": "A target with concentric circles and an arrow in the bullseye. Goal or achievement icon.",
    "icon-star": "A simple five-pointed star. Achievement or favorite icon.",
    "icon-sparkles": "Magic sparkles or stars scattered. Magic/AI generation icon.",
    "icon-chart": "A simple bar chart showing growth. Progress or statistics icon.",
}


def generate_icon(name: str, description: str) -> bool:
    """Generate a single icon using MuleRouter."""
    full_prompt = f"{STYLE_PREFIX}\n\nIcon concept: {description}"
    output_path = OUTPUT_DIR / f"{name}.png"

    print(f"  Generating {name}...")

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
            print(f"    FAILED: {result.stderr[:200] if result.stderr else 'Unknown error'}")
            return False

        data = json.loads(result.stdout)
        if data.get("results"):
            image_url = data["results"][0]
            response = requests.get(image_url, timeout=60)
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                print(f"    OK")
                return True
        print(f"    FAILED: No results")
        return False

    except Exception as e:
        print(f"    ERROR: {e}")
        return False


def main():
    print("Generating UI icons...")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for name, description in ICONS.items():
        output_path = OUTPUT_DIR / f"{name}.png"
        if output_path.exists():
            print(f"  Skipping {name} (exists)")
            continue
        generate_icon(name, description)
        sleep(1)

    print("Done!")


if __name__ == "__main__":
    main()
