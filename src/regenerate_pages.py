#!/usr/bin/env python3
"""Regenerate specific pages for a v2 book.

Usage:
    python src/regenerate_pages.py volcano 4 5 6 8 10 11 12 13 14 17 18
"""

import json
import os
import sys
import subprocess
from pathlib import Path

# Paths
SKILL_DIR = Path("/Users/dereklomas/mulerouter-skills-dev/skills/mulerouter-skills")
BOOKS_DIR = Path("web/books")
IMAGES_DIR = Path("web/books/images_v2")

# Riso style suffix
RISO_STYLE = """
Style: Simple flat cartoon illustration designed for Risograph printing.
Bold black outlines. Flat color fills only - NO gradients, NO shading, NO textures.
High contrast. Large solid color areas. Minimal background details.
2-3 spot colors maximum. Exaggerated expressions. Clean vector-like shapes.
NO TEXT IN IMAGE. Child-friendly."""

# Character definitions - UPDATED to prevent spikes
CHARACTERS = {
    "volcano": """
CHARACTER - Gus (cute cartoon salamander, see reference):
- Big round head with HUGE round eyes (black with white highlight dots)
- Small cute smile, tiny round nose
- Body is ORANGE with YELLOW belly
- SMOOTH rounded body - absolutely NO SPIKES, NO RIDGES, NO FINS on back
- Curly spiral tail (always visible)
- EXACTLY 4 short stubby limbs (2 arms, 2 legs) - NEVER 3 arms or 5 limbs
- Bold black outlines, flat solid colors, simple cartoon style
- Proportions: big head, small cute body - like the reference image
- Expression: always cute and friendly, never scary""",

    "castle": """
CHARACTERS - Rita and Rico the Rats:
RITA: Small rat, solid PINK body, big eager eyes, tiny ears, thin tail.
DISTINCTIVE FEATURE: RED BOW on head (must be visible in every image).

RICO: Small rat, solid BLUE-GRAY body, worried eyes, tiny ears, thin tail.
DISTINCTIVE FEATURE: BLUE BANDANA around neck (must be visible in every image).""",

    "jungle": """
CHARACTERS - Zee and Pip:
ZEE: Small round sloth with shaggy GREEN fur. Gentle sleepy eyes, tiny black nose.
DISTINCTIVE FEATURE: Long curved CLAWS (must be visible in every image).

PIP: Small round BLUE bird with big eager eyes, tiny beak.
DISTINCTIVE FEATURE: Tall CREST on head that shows emotion."""
}

COLOR_PALETTES = {
    "volcano": "COLORS: Black (outlines) + Fluorescent Orange (Gus, lava) + Yellow (highlights, belly)",
    "castle": "COLORS: Black (outlines, castle) + Fluorescent Pink (Rita, jam) + Blue (Rico, shadows)",
    "jungle": "COLORS: Black (outlines, trunks) + Green (Zee, leaves) + Risofederal Blue (Pip, sky)"
}


def generate_image(prompt: str, output_name: str, book_key: str) -> bool:
    """Generate a single Riso-style image."""
    character_def = CHARACTERS.get(book_key, "")
    color_palette = COLOR_PALETTES.get(book_key, "")

    full_prompt = f"{character_def}\n\n{color_palette}\n\nSCENE: {prompt}\n\n{RISO_STYLE}"

    output_path = IMAGES_DIR / output_name

    print(f"\n{'='*60}")
    print(f"Generating: {output_name}")
    print(f"{'='*60}")

    env = os.environ.copy()
    env["MULEROUTER_SITE"] = "mulerouter"
    env["MULEROUTER_API_KEY"] = os.environ.get(
        "MULEROUTER_API_KEY",
        "sk-mr-2dfbbdfe5bbd2e24235960b2d4f5b45bf1b59a087bc2524ff35c6c70a2657436"
    )

    cmd = [
        "uv", "run", "python",
        "models/alibaba/wan2.6-t2i/generation.py",
        "--prompt", full_prompt,
        "--n", "1",
        "--size", "1536*1024"
    ]

    try:
        result = subprocess.run(
            cmd,
            cwd=SKILL_DIR,
            env=env,
            capture_output=True,
            text=True,
            timeout=180
        )

        output = result.stdout + result.stderr
        for line in output.split("\n"):
            if "result_00.png" in line or "mule-router-assets" in line:
                parts = line.split()
                for part in parts:
                    if part.startswith("http"):
                        url = part
                        import requests
                        resp = requests.get(url, timeout=60)
                        with open(output_path, "wb") as f:
                            f.write(resp.content)
                        print(f"OK Saved: {output_path}")
                        return True

        print(f"X No image URL found")
        return False

    except subprocess.TimeoutExpired:
        print(f"X Timeout")
        return False
    except Exception as e:
        print(f"X Error: {e}")
        return False


def main():
    if len(sys.argv) < 3:
        print("Usage: python src/regenerate_pages.py <book> <page1> <page2> ...")
        print("Example: python src/regenerate_pages.py volcano 4 5 6 8")
        sys.exit(1)

    book_key = sys.argv[1].lower()
    pages_to_regen = [int(p) for p in sys.argv[2:]]

    json_path = BOOKS_DIR / f"{book_key}_v2.json"

    if not json_path.exists():
        print(f"ERROR: {json_path} not found")
        sys.exit(1)

    with open(json_path) as f:
        book = json.load(f)

    print("="*60)
    print(f"REGENERATING: {book['title']}")
    print(f"Pages: {pages_to_regen}")
    print("="*60)

    results = []

    for page in book.get("pages", []):
        page_num = page.get("page", 0)

        if page_num not in pages_to_regen:
            continue

        page_type = page.get("type", "story")
        if page_type == "wordlist":
            continue

        image_prompt = page.get("image_prompt", "")
        if not image_prompt:
            continue

        filename = f"{book_key}_v2_page{page_num:02d}.png"

        riso_notes = page.get("riso_notes", "")
        if riso_notes:
            image_prompt = f"{image_prompt}\n\nRISO COLOR NOTES: {riso_notes}"

        success = generate_image(image_prompt, filename, book_key)
        results.append((page_num, filename, success))

    print("\n" + "="*60)
    print(f"SUMMARY")
    print("="*60)
    success_count = sum(1 for _, _, s in results if s)
    print(f"Regenerated: {success_count}/{len(results)}")
    for page_num, filename, success in results:
        status = "OK" if success else "X"
        print(f"  {status} Page {page_num}: {filename}")


if __name__ == "__main__":
    main()
