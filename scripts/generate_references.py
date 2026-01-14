#!/usr/bin/env python3
"""Generate 9-panel reference images for books based on their content.

Saves generation metadata to book JSON:
- reference_generated_at: ISO timestamp
- reference_model: model used
- reference_prompt: the prompt used
"""

import sys
import os
import json
import urllib.request
from pathlib import Path
from datetime import datetime

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

    # Get sample scenes (filter out None/empty)
    scenes = [p.get("scene") or p.get("text") or "" for p in book.get("pages", [])]
    scenes = [s for s in scenes if s][:9]

    # Extract visual style from story_bible if present
    story_bible = book.get("story_bible", {})
    visual_style = story_bible.get("visual_style", "")

    # Extract character descriptions for reference sheet
    characters = book.get("characters", {})
    character_blocks = []
    for char_key, char_data in characters.items():
        if isinstance(char_data, dict):
            # Use visual_shorthand if available, otherwise build from appearance
            shorthand = char_data.get("visual_shorthand", "")
            if shorthand:
                character_blocks.append(shorthand)
            elif char_data.get("appearance"):
                app = char_data["appearance"]
                name = char_data.get("name", char_key.capitalize())
                parts = [name + ":"]
                if app.get("body"):
                    parts.append(app["body"])
                if app.get("fur_color"):
                    parts.append(f"with {app['fur_color']} fur")
                if app.get("distinguishing_mark"):
                    parts.append(f"- {app['distinguishing_mark']} (key identifier)")
                if app.get("ears"):
                    parts.append(f"- {app['ears']}")
                if app.get("posture"):
                    parts.append(f"- {app['posture']}")
                character_blocks.append(" ".join(parts))

    return {
        "title": book.get("title", slug),
        "level": book.get("level", "B1"),
        "band": book.get("band", book.get("level", "B")[0]),
        "skill": book.get("skill") or book.get("targetPhonics", ""),
        "summary": book.get("summary", ""),
        "scenes": scenes,
        "visual_style": visual_style,
        "reference_prompt": book.get("reference_prompt", ""),  # Custom prompt if provided
        "character_blocks": character_blocks,  # For character consistency
    }


def build_reference_prompt(slug: str, book_info: dict) -> str:
    """Build a prompt for generating a 9-panel reference image."""

    band = book_info["band"]
    style_template = STYLE_TEMPLATES.get(band, STYLE_TEMPLATES["B"])

    # Priority for style: story_bible.visual_style > BOOK_STYLES > STYLE_TEMPLATES
    if book_info.get("visual_style"):
        book_style = book_info["visual_style"]
    else:
        book_style = BOOK_STYLES.get(slug, style_template["base"])

    # Build character section if we have character descriptions
    character_blocks = book_info.get("character_blocks", [])
    character_section = ""
    if character_blocks:
        character_section = f"""
CHARACTERS (draw EXACTLY as described - they must be visually distinct):

{chr(10).join(character_blocks)}
"""

    # Extract key visual elements from scenes
    scenes = book_info["scenes"][:9]

    # Build panel descriptions - first 3 panels for characters if we have them
    panel_descriptions = []

    if character_blocks:
        # Dedicate Row 1 to character studies
        num_chars = len(character_blocks)
        for i, char_block in enumerate(character_blocks[:3]):
            char_name = char_block.split(":")[0].strip()
            panel_descriptions.append(f"Panel {i+1}: {char_name} character study - full body, clear view of distinguishing features")
        if num_chars < 3:
            panel_descriptions.append(f"Panel 3: All characters together showing size/color contrast")

        # Remaining panels for scenes
        for i, scene in enumerate(scenes[:6]):
            if not scene:
                continue
            if len(scene) > 100:
                scene = scene[:100] + "..."
            panel_descriptions.append(f"Panel {len(panel_descriptions)+1}: {scene}")
    else:
        # No characters - use scenes for all panels
        for i, scene in enumerate(scenes[:9]):
            if not scene:
                continue
            if len(scene) > 100:
                scene = scene[:100] + "..."
            panel_descriptions.append(f"Panel {i+1}: {scene}")

    # Pad to 9 panels if needed
    while len(panel_descriptions) < 9:
        panel_descriptions.append(f"Panel {len(panel_descriptions)+1}: Setting or mood detail from {book_info['title']}")

    prompt = f"""9-PANEL REFERENCE SHEET for '{book_info['title']}'

Style: {book_style}
Mood: {style_template['mood']}
{character_section}
PANEL LAYOUT (3x3 grid):
{chr(10).join(panel_descriptions[:9])}

Consistent art style across all panels. Each panel is a square vignette.

CRITICAL: NO TEXT, NO WORDS, NO LETTERS anywhere in the image. Pure illustration only."""

    return prompt


def generate_reference(slug: str, config) -> bool:
    """Generate a 9-panel reference image for a book."""

    book_info = get_book_info(slug)
    if not book_info:
        print(f"  Book not found: {slug}")
        return False

    output_path = REFS_DIR / f"{slug}_reference.png"

    # Use custom reference_prompt from book JSON if provided, otherwise build one
    if book_info.get("reference_prompt"):
        prompt = book_info["reference_prompt"]
        print(f"  Using custom reference_prompt from book JSON")
    else:
        prompt = build_reference_prompt(slug, book_info)
        print(f"  Using auto-generated prompt")

    print(f"  Title: {book_info['title']}")
    print(f"  Band: {book_info['band']}")
    if book_info.get("visual_style"):
        print(f"  Style: {book_info['visual_style'][:60]}...")
    print(f"  Prompt preview: {prompt[:200]}...")

    # Use nano-banana-pro for highest quality reference sheets
    model = "nano-banana-pro"

    # Use text-to-image for reference generation
    body = {
        "prompt": prompt,
        "size": "1024*1024",
        "n": 1
    }

    with APIClient(config) as client:
        result = create_and_poll_task(
            client=client,
            endpoint_path=f"/vendors/google/v1/{model}/generation",
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

                # Save metadata to book JSON
                book_path = BOOKS_DIR / f"{slug}.json"
                with open(book_path) as f:
                    book = json.load(f)

                book["reference_metadata"] = {
                    "generated_at": datetime.now().isoformat(),
                    "model": model,
                    "prompt": prompt,
                    "output_path": str(output_path.relative_to(BOOKS_DIR.parent))
                }

                with open(book_path, 'w') as f:
                    json.dump(book, f, indent=2)

                print(f"  Metadata saved to book JSON")
                return True
            except Exception as e:
                print(f"  Download error: {e}")
                return False
        else:
            print(f"  Failed: {result.error}")
            return False


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate 9-panel reference images")
    parser.add_argument("--book", help="Single book slug to generate")
    parser.add_argument("--all-missing", action="store_true", help="Generate for all books missing references")
    parser.add_argument("--force", action="store_true", help="Regenerate even if reference exists")
    args = parser.parse_args()

    if args.book:
        # Single book mode
        existing = [args.book]
        if not (BOOKS_DIR / f"{args.book}.json").exists():
            print(f"Book not found: {args.book}")
            return
        # Check if reference exists and --force not set
        ref_exists = (REFS_DIR / f"{args.book}_reference.png").exists()
        if ref_exists and not args.force:
            print(f"Reference already exists for {args.book}. Use --force to regenerate.")
            return
    elif args.all_missing:
        # Find all books missing reference images
        all_books = [p.stem for p in BOOKS_DIR.glob("*.json") if p.stem != "manifest"]
        existing = [s for s in all_books if not (REFS_DIR / f"{s}_reference.png").exists()
                    and not (REFS_DIR / f"{s}_reference_v2.png").exists()
                    and not (REFS_DIR / f"{s}_reference_v3.png").exists()
                    and not (REFS_DIR / f"{s}_reference_v4.png").exists()]
    else:
        print("Usage: python generate_references.py --book SLUG")
        print("       python generate_references.py --all-missing")
        return

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
