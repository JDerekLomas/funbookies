#!/usr/bin/env python3
"""Generate 9-panel reference images for books based on their content.

Supports two providers:
- fal.ai (default): $0.15/image for nano-banana-pro
- mulerouter: $0.15/image for nano-banana-pro

Both providers have the same pricing for nano-banana-pro T2I.
fal.ai is recommended for API consistency with other scripts.

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

# Setup paths relative to project root
from dotenv import load_dotenv
PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / ".env")
load_dotenv(PROJECT_ROOT / ".env.local")

# For MuleRouter fallback - configurable via env var
SKILL_DIR = Path(os.getenv("MULEROUTER_SKILL_DIR", str(Path.home() / ".claude/plugins/cache/mulerouter-skills/mulerouter-skills/1.0.0/skills/mulerouter-skills")))

# Import fal client
from fal_client import FalClient

# Import shared utilities
from image_utils import BOOKS_DIR, REFS_DIR, get_character_block

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

    # Build panel descriptions with CENTER (panel 5) as hero shot
    panel_descriptions = []

    if character_blocks:
        # Get character names for reference
        char_names = [cb.split(":")[0].strip() for cb in character_blocks[:2]]

        # Panel 1-2: Individual character studies
        for i, char_block in enumerate(character_blocks[:2]):
            char_name = char_block.split(":")[0].strip()
            panel_descriptions.append(f"Panel {i+1}: {char_name} alone - full body, distinguishing features clearly visible")

        # Panel 3-4: Settings from scenes
        for i, scene in enumerate(scenes[:2]):
            if scene:
                if len(scene) > 80:
                    scene = scene[:80] + "..."
                panel_descriptions.append(f"Panel {len(panel_descriptions)+1}: {scene}")
            else:
                panel_descriptions.append(f"Panel {len(panel_descriptions)+1}: Setting from {book_info['title']}")

        # Panel 5: CENTER HERO SHOT - all characters together
        if len(char_names) >= 2:
            panel_descriptions.append(f"Panel 5: **CENTER HERO SHOT** - {' and '.join(char_names)} TOGETHER, side by side, clear visual contrast between them. THE KEY IMAGE.")
        elif len(char_names) == 1:
            panel_descriptions.append(f"Panel 5: **CENTER HERO SHOT** - {char_names[0]} in heroic pose, all distinguishing features visible. THE KEY IMAGE.")
        else:
            panel_descriptions.append(f"Panel 5: **CENTER HERO SHOT** - Main character(s) together. THE KEY IMAGE.")

        # Panel 6: Another setting
        if len(scenes) > 2 and scenes[2]:
            scene = scenes[2][:80] + "..." if len(scenes[2]) > 80 else scenes[2]
            panel_descriptions.append(f"Panel 6: {scene}")
        else:
            panel_descriptions.append(f"Panel 6: Interior or location from {book_info['title']}")

        # Panel 7-9: Key moments from remaining scenes
        for i, scene in enumerate(scenes[3:6]):
            if scene:
                if len(scene) > 80:
                    scene = scene[:80] + "..."
                panel_descriptions.append(f"Panel {len(panel_descriptions)+1}: {scene}")

    else:
        # No characters - use scenes for all panels, but still emphasize panel 5
        for i, scene in enumerate(scenes[:4]):
            if scene:
                if len(scene) > 80:
                    scene = scene[:80] + "..."
                panel_descriptions.append(f"Panel {i+1}: {scene}")
            else:
                panel_descriptions.append(f"Panel {i+1}: Scene from {book_info['title']}")

        # Panel 5 still gets emphasis
        if len(scenes) > 4 and scenes[4]:
            panel_descriptions.append(f"Panel 5: **CENTER** - {scenes[4][:80]}...")
        else:
            panel_descriptions.append(f"Panel 5: **CENTER** - Key moment from {book_info['title']}")

        for i, scene in enumerate(scenes[5:9]):
            if scene:
                if len(scene) > 80:
                    scene = scene[:80] + "..."
                panel_descriptions.append(f"Panel {len(panel_descriptions)+1}: {scene}")

    # Pad to 9 panels if needed
    while len(panel_descriptions) < 9:
        panel_descriptions.append(f"Panel {len(panel_descriptions)+1}: Setting or mood detail")

    prompt = f"""9-PANEL REFERENCE SHEET for '{book_info['title']}'

Create a 3x3 grid. PANEL 5 (CENTER) is the HERO SHOT - most important!

Style: {book_style}
Mood: {style_template['mood']}
{character_section}
PANEL LAYOUT:
{chr(10).join(panel_descriptions[:9])}

Consistent art style across all panels. Each panel is a square vignette.

CRITICAL: NO TEXT, NO WORDS, NO LETTERS anywhere in the image. Pure illustration only."""

    return prompt


def generate_reference_fal(slug: str, fal_client: FalClient) -> bool:
    """Generate a 9-panel reference image using fal.ai."""

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

    model = "nano-banana-pro"

    # Generate using fal.ai
    result = fal_client.generate_image(
        prompt=prompt,
        model=model,
        size="square_hd",  # 1024x1024
        verbose=True,
    )

    if result.success:
        print(f"  Generated: {result.url[:60]}...")
        try:
            urllib.request.urlretrieve(result.url, output_path)
            print(f"  Saved to: {output_path}")

            # Save metadata to book JSON
            book_path = BOOKS_DIR / f"{slug}.json"
            with open(book_path) as f:
                book = json.load(f)

            book["reference_metadata"] = {
                "generated_at": datetime.now().isoformat(),
                "model": model,
                "provider": "fal.ai",
                "prompt": prompt,
                "output_path": str(output_path.relative_to(BOOKS_DIR.parent)),
                "cost": "$0.15",
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


def generate_reference_mulerouter(slug: str, config) -> bool:
    """Generate a 9-panel reference image using MuleRouter (fallback)."""

    sys.path.insert(0, str(SKILL_DIR))
    load_dotenv(SKILL_DIR / ".env")
    from core import APIClient, create_and_poll_task

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
                    "provider": "mulerouter",
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
    parser.add_argument("--provider", choices=["fal", "mulerouter"], default="fal",
                        help="API provider (default: fal)")
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
        print("")
        print("Options:")
        print("  --provider fal        Use fal.ai (default, $0.15/image)")
        print("  --provider mulerouter Use MuleRouter ($0.15/image)")
        print("  --force               Regenerate even if reference exists")
        return

    print(f"Generating reference images for {len(existing)} books:")
    for s in existing:
        print(f"  - {s}")

    print(f"\nUsing provider: {args.provider}")
    print(f"Cost: $0.15 per image (nano-banana-pro)")
    print(f"Estimated total: ${len(existing) * 0.15:.2f}")

    # Initialize client
    if args.provider == "fal":
        try:
            client = FalClient()
            print(f"API key: {client.fal_key[:8]}...")
        except ValueError as e:
            print(f"\nError: {e}")
            return
    else:
        sys.path.insert(0, str(SKILL_DIR))
        load_dotenv(SKILL_DIR / ".env")
        from core import load_config
        client = load_config()
        print(f"API: {client.site}")

    REFS_DIR.mkdir(parents=True, exist_ok=True)

    success = 0
    for slug in existing:
        print(f"\n[{slug}]")
        if args.provider == "fal":
            if generate_reference_fal(slug, client):
                success += 1
        else:
            if generate_reference_mulerouter(slug, client):
                success += 1

    print(f"\n\nDone! Generated {success}/{len(existing)} reference images.")
    print(f"Total cost: ~${success * 0.15:.2f}")


if __name__ == "__main__":
    main()
