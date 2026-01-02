#!/usr/bin/env python3
"""Generate Riso-style images for v2 books using Wan2.6 T2I.

Usage:
    python src/generate_riso_v2.py volcano    # Generate volcano_v2 images
    python src/generate_riso_v2.py castle     # Generate castle_v2 images
    python src/generate_riso_v2.py jungle     # Generate jungle_v2 images
    python src/generate_riso_v2.py all        # Generate all v2 images
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
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

# Riso style suffix - added to ALL prompts
RISO_STYLE = """
Style: Simple flat cartoon illustration designed for Risograph printing.
Bold black outlines. Flat color fills only - NO gradients, NO shading, NO textures.
High contrast. Large solid color areas. Minimal background details.
2-3 spot colors maximum. Exaggerated expressions. Clean vector-like shapes.
NO TEXT IN IMAGE. Child-friendly."""

# Book-specific character definitions
CHARACTERS = {
    "volcano": """
CHARACTER - Gus the Gecko:
- Small gecko with round head and big curious eyes
- Body is solid ORANGE (spot color)
- Yellow-green belly
- DISTINCTIVE FEATURE: Curly spiral tail (must be visible in every image)
- Four stubby legs with tiny toe pads
- Bold black outlines, flat colors only""",

    "castle": """
CHARACTERS - Rita and Rico the Rats:
RITA: Small rat, solid PINK body, big eager eyes, tiny ears, thin tail.
DISTINCTIVE FEATURE: RED BOW on head (must be visible in every image).
Personality: Bold, leaning forward, excited.

RICO: Small rat, solid BLUE-GRAY body, worried eyes, tiny ears, thin tail.
DISTINCTIVE FEATURE: BLUE BANDANA around neck (must be visible in every image).
Personality: Cautious, leaning back, one eyebrow raised.""",

    "jungle": """
CHARACTERS - Zee and Pip:
ZEE: Small round sloth with shaggy GREEN fur. Gentle sleepy eyes, tiny black nose.
DISTINCTIVE FEATURE: Long curved CLAWS (must be visible in every image).
Personality: Slow, calm, content, zen-like smile.

PIP: Small round BLUE bird with big eager eyes, tiny beak.
DISTINCTIVE FEATURE: Tall CREST on head that shows emotion.
Personality: Fast, excitable, always in motion."""
}

# Color palette reminders
COLOR_PALETTES = {
    "volcano": "COLORS: Black (outlines) + Fluorescent Orange (Gus, lava) + Yellow (highlights, belly)",
    "castle": "COLORS: Black (outlines, castle) + Fluorescent Pink (Rita, jam) + Blue (Rico, shadows)",
    "jungle": "COLORS: Black (outlines, trunks) + Green (Zee, leaves) + Risofederal Blue (Pip, sky)"
}


def generate_image(prompt: str, output_name: str, book_key: str) -> bool:
    """Generate a single Riso-style image."""
    # Build full prompt with character + style
    character_def = CHARACTERS.get(book_key, "")
    color_palette = COLOR_PALETTES.get(book_key, "")

    full_prompt = f"{character_def}\n\n{color_palette}\n\nSCENE: {prompt}\n\n{RISO_STYLE}"

    output_path = IMAGES_DIR / output_name

    print(f"\n{'='*60}")
    print(f"Generating: {output_name}")
    print(f"{'='*60}")

    # Run the skill
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
        "--size", "1536*1024"  # 3:2 landscape for print
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

        # Parse output for image URL
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
        if len(output) > 200:
            print(output[-200:])
        return False

    except subprocess.TimeoutExpired:
        print(f"X Timeout")
        return False
    except Exception as e:
        print(f"X Error: {e}")
        return False


def generate_book(book_key: str):
    """Generate all images for a v2 book."""
    json_path = BOOKS_DIR / f"{book_key}_v2.json"

    if not json_path.exists():
        print(f"ERROR: {json_path} not found")
        return

    with open(json_path) as f:
        book = json.load(f)

    print("="*60)
    print(f"GENERATING RISO V2: {book['title']}")
    print(f"Colors: {book.get('riso_colors', {})}")
    print("="*60)

    results = []

    for page in book.get("pages", []):
        page_num = page.get("page", 0)
        page_type = page.get("type", "story")

        # Skip wordlist pages (no image)
        if page_type == "wordlist":
            continue

        # Get the image prompt
        image_prompt = page.get("image_prompt", "")
        if not image_prompt:
            continue

        # Generate filename
        filename = f"{book_key}_v2_page{page_num:02d}.png"

        # Add riso notes to prompt if available
        riso_notes = page.get("riso_notes", "")
        if riso_notes:
            image_prompt = f"{image_prompt}\n\nRISO COLOR NOTES: {riso_notes}"

        success = generate_image(image_prompt, filename, book_key)
        results.append((filename, success))

    # Summary
    print("\n" + "="*60)
    print(f"SUMMARY: {book['title']}")
    print("="*60)
    success_count = sum(1 for _, s in results if s)
    print(f"Generated: {success_count}/{len(results)}")
    for filename, success in results:
        status = "OK" if success else "X"
        print(f"  {status} {filename}")

    return results


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python src/generate_riso_v2.py volcano")
        print("  python src/generate_riso_v2.py castle")
        print("  python src/generate_riso_v2.py jungle")
        print("  python src/generate_riso_v2.py all")
        sys.exit(1)

    arg = sys.argv[1].lower()

    if arg == "all":
        for book in ["volcano", "castle", "jungle"]:
            generate_book(book)
    elif arg in ["volcano", "castle", "jungle"]:
        generate_book(arg)
    else:
        print(f"Unknown book: {arg}")
        print("Options: volcano, castle, jungle, all")
        sys.exit(1)


if __name__ == "__main__":
    main()
