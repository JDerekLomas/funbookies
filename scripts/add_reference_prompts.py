#!/usr/bin/env python3
"""Add reference_prompt field to book JSONs (backfill from generation logic)."""

import json
from pathlib import Path

BOOKS_DIR = Path("/Users/dereklomas/lilbookies/public/books")

# Style templates based on reading level/band
STYLE_TEMPLATES = {
    "A": {
        "base": "Simple bold shapes, soft watercolor, very minimal detail, warm pastel colors, toddler-friendly illustration",
        "mood": "gentle, comforting, bright"
    },
    "B": {
        "base": "Playful watercolor illustration, expressive characters, vibrant colors, child-friendly art style",
        "mood": "energetic, fun, adventurous"
    },
    "C": {
        "base": "Rich watercolor illustration, more detailed characters and settings, dynamic compositions",
        "mood": "exciting, imaginative, engaging"
    },
    "D": {
        "base": "Sophisticated illustration style, detailed environments, nuanced lighting, chapter book aesthetic",
        "mood": "atmospheric, immersive, evocative"
    }
}

# Book-specific style overrides
BOOK_STYLES = {
    "d1-the-lighthouse-keeper": "Coastal watercolor style, muted blues and warm sunset oranges, vintage seaside aesthetic, atmospheric lighting",
    "d2-the-hidden-garden": "Lush botanical illustration, secret garden aesthetic, dappled sunlight, rich greens and flower colors",
    "d3-the-architects-secret": "Architectural illustration style, warm browns and golds, mysterious shadows, historical building details",
    "d4-signals-from-kepler": "Science fiction illustration, deep space blues and purples, glowing technology, starfield backgrounds",
    "d5-the-winter-of-words": "Cozy winter illustration, soft whites and warm indoor lighting, snowy landscapes, bookish atmosphere",
    "d6-the-bridge-between": "Dreamlike illustration, soft gradients, bridge and connection imagery, ethereal lighting",
    "c1_knight_quest": "Medieval fantasy illustration, castle and forest settings, noble knights, warm golden lighting",
    "c2_magic_city": "Magical urban illustration, floating buildings, sparkles and wonder, vibrant fantasy colors",
    "c4_robot_pilot": "Retro sci-fi illustration, friendly robots, cockpit views, chrome and sky blue palette",
    "c6_biggest_race": "Dynamic sports illustration, motion blur effects, competitive energy, bright action colors",
    "c7_hopeless_garden": "Whimsical garden illustration, overgrown plants, determined characters, green and earth tones",
    "c8_impossible_invention": "Steampunk-lite illustration, gears and gadgets, inventor's workshop, brass and copper tones",
}


def build_reference_prompt(slug: str, book: dict) -> str:
    """Build a prompt for generating a 9-panel reference image."""

    band = book.get("band", book.get("level", "B")[0])
    title = book.get("title", slug)
    style_template = STYLE_TEMPLATES.get(band, STYLE_TEMPLATES["B"])

    # Check for book-specific style override
    book_style = BOOK_STYLES.get(slug, style_template["base"])

    # Extract scenes from pages
    scenes = []
    for p in book.get("pages", []):
        scene = p.get("scene") or p.get("text", "")
        if scene:
            scenes.append(scene)
    scenes = scenes[:9]

    # Build panel descriptions
    panel_descriptions = []
    for i, scene in enumerate(scenes[:9]):
        if len(scene) > 100:
            scene = scene[:100] + "..."
        panel_descriptions.append(f"Panel {i+1}: {scene}")

    # Pad to 9 panels if needed
    while len(panel_descriptions) < 9:
        panel_descriptions.append(f"Panel {len(panel_descriptions)+1}: Character or setting detail from {title}")

    prompt = f"""A 9-panel reference sheet for children's book illustration style.
Style: {book_style}
Mood: {style_template['mood']}

The 9 panels arranged in a 3x3 grid showing:
{chr(10).join(panel_descriptions[:9])}

Consistent art style across all panels, suitable for children's picture book illustration. Each panel is a square vignette showing a key moment or character.

IMPORTANT: Minimize text in panels. Focus on visual style, characters, colors, and mood. No title text."""

    return prompt


def main():
    book_files = list(BOOKS_DIR.glob("*.json"))
    book_files = [f for f in book_files if f.name != "manifest.json"]

    print(f"Adding reference_prompt to {len(book_files)} books...\n")

    updated = 0
    for book_file in sorted(book_files):
        slug = book_file.stem

        with open(book_file) as f:
            book = json.load(f)

        # Generate the reference prompt
        ref_prompt = build_reference_prompt(slug, book)

        # Add to book data
        book["reference_prompt"] = ref_prompt

        # Write back
        with open(book_file, 'w') as f:
            json.dump(book, f, indent=2)

        print(f"[{slug}] Added reference_prompt")
        updated += 1

    print(f"\nDone! Updated {updated} books.")


if __name__ == "__main__":
    main()
