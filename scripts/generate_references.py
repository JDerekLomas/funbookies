#!/usr/bin/env python3
"""Generate 9-panel reference images for books based on their content."""

import sys
import os
import json
import urllib.request
from pathlib import Path

SKILL_DIR = Path("/Users/dereklomas/.claude/plugins/cache/mulerouter-skills/mulerouter-skills/1.0.0/skills/mulerouter-skills")
sys.path.insert(0, str(SKILL_DIR))

from dotenv import load_dotenv
load_dotenv(SKILL_DIR / ".env")

from core import APIClient, load_config, create_and_poll_task

BOOKS_DIR = Path("/Users/dereklomas/lilbookies/public/books")
REFS_DIR = BOOKS_DIR / "references"

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

# Book-specific style overrides for unique themes
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


def get_book_info(slug: str) -> dict:
    """Load book JSON and extract key info."""
    book_path = BOOKS_DIR / f"{slug}.json"
    if not book_path.exists():
        return None

    with open(book_path) as f:
        book = json.load(f)

    # Get sample scenes
    scenes = [p.get("scene", p.get("text", "")) for p in book.get("pages", []) if p.get("scene") or p.get("text")][:9]

    return {
        "title": book.get("title", slug),
        "level": book.get("level", "B1"),
        "band": book.get("band", book.get("level", "B")[0]),
        "skill": book.get("skill") or book.get("targetPhonics", ""),
        "summary": book.get("summary", ""),
        "scenes": scenes
    }


def build_reference_prompt(slug: str, book_info: dict) -> str:
    """Build a prompt for generating a 9-panel reference image."""

    band = book_info["band"]
    style_template = STYLE_TEMPLATES.get(band, STYLE_TEMPLATES["B"])

    # Check for book-specific style override
    book_style = BOOK_STYLES.get(slug, style_template["base"])

    # Extract key visual elements from scenes
    scenes = book_info["scenes"][:9]

    # Build panel descriptions
    panel_descriptions = []
    for i, scene in enumerate(scenes[:9]):
        # Truncate long scenes
        if len(scene) > 100:
            scene = scene[:100] + "..."
        panel_descriptions.append(f"Panel {i+1}: {scene}")

    # Pad to 9 panels if needed
    while len(panel_descriptions) < 9:
        panel_descriptions.append(f"Panel {len(panel_descriptions)+1}: Character or setting detail from {book_info['title']}")

    prompt = f"""A 9-panel reference sheet for children's book "{book_info['title']}".
Style: {book_style}
Mood: {style_template['mood']}

The 9 panels arranged in a 3x3 grid showing:
{chr(10).join(panel_descriptions[:9])}

Consistent art style across all panels, suitable for children's picture book illustration. Each panel is a square vignette showing a key moment or character."""

    return prompt


def generate_reference(slug: str, config) -> bool:
    """Generate a 9-panel reference image for a book."""

    book_info = get_book_info(slug)
    if not book_info:
        print(f"  Book not found: {slug}")
        return False

    output_path = REFS_DIR / f"{slug}_reference.png"

    prompt = build_reference_prompt(slug, book_info)
    print(f"  Title: {book_info['title']}")
    print(f"  Band: {book_info['band']}")
    print(f"  Prompt preview: {prompt[:200]}...")

    # Use text-to-image for reference generation
    body = {
        "prompt": prompt,
        "size": "1024*1024",
        "n": 1
    }

    with APIClient(config) as client:
        result = create_and_poll_task(
            client=client,
            endpoint_path="/vendors/alibaba/v1/wan2.6-t2i/generation",
            request_body=body,
            result_key="images",
            interval=5.0,
            max_wait=300.0,
            verbose=True
        )

        if result.results:
            url = result.results[0]
            print(f"  Generated: {url}")
            try:
                urllib.request.urlretrieve(url, output_path)
                print(f"  Saved to: {output_path}")
                return True
            except Exception as e:
                print(f"  Download error: {e}")
                return False
        else:
            print(f"  Failed: {result.error}")
            return False


def main():
    # Books missing reference images
    missing = [
        # Band A
        "a1-i-sit", "a2-i-see-it",
        # Band B
        "b2-pup-in-the-mud", "b3-jump-at-camp", "b6-kate-and-the-lake", "b8-the-owl-and-the-boy",
        # Band C
        "c2_magic_city", "c4_robot_pilot", "c6_biggest_race", "c7_hopeless_garden", "c8_impossible_invention",
        # Band D
        "d1-the-lighthouse-keeper", "d2-the-hidden-garden", "d3-the-architects-secret",
        "d4-signals-from-kepler", "d5-the-winter-of-words", "d6-the-bridge-between",
    ]

    # Filter to only existing books
    existing = [s for s in missing if (BOOKS_DIR / f"{s}.json").exists()]

    print(f"Generating reference images for {len(existing)} books:")
    for s in existing:
        print(f"  - {s}")

    config = load_config()
    print(f"\nUsing API: {config.site}")

    REFS_DIR.mkdir(parents=True, exist_ok=True)

    success = 0
    for slug in existing:
        print(f"\n[{slug}]")
        if generate_reference(slug, config):
            success += 1

    print(f"\n\nDone! Generated {success}/{len(existing)} reference images.")


if __name__ == "__main__":
    main()
