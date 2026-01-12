#!/usr/bin/env python3
"""Regenerate book covers WITHOUT any text baked in.

Uses wan2.6-image with reference images and very explicit no-text instructions.
"""

import sys
import os
import base64
import json
import urllib.request
from pathlib import Path

# Add the skill directory to path
SKILL_DIR = Path("/Users/dereklomas/.claude/plugins/cache/mulerouter-skills/mulerouter-skills/1.0.0/skills/mulerouter-skills")
sys.path.insert(0, str(SKILL_DIR))

from dotenv import load_dotenv
load_dotenv(SKILL_DIR / ".env")

from core import APIClient, load_config, create_and_poll_task

BOOKS_DIR = Path("/Users/dereklomas/lilbookies/public/books")
COVERS_DIR = Path("/Users/dereklomas/lilbookies/public/images/covers")
REFS_DIR = BOOKS_DIR / "references"

# Covers that need regeneration (have text baked in)
COVERS_WITH_TEXT = [
    "a0-look",
    "a1-i-sit",
    "a2-i-see-it",
    "a3-the-cat-is-here",
    "a4-sam-and-the-hat",
    "b1-sam-and-the-cat",
    "b2-pup-in-the-mud",
    "b3-jump-at-camp",
    "b4-frog-and-crab",
    "b5-the-ship-in-the-shell",
    "b6-kate-and-the-lake",
    "b7-the-rain-and-the-snow",
    "b8-the-owl-and-the-boy",
    "b9-a-star-at-the-farm",
    "c1_knight_quest",
    "c2_magic_city",
    "c3_kitten_adventure",
    "c4_robot_pilot",
    "c5_treehouse_mystery",
    "c6_biggest_race",
    "c7_hopeless_garden",
    "c8_impossible_invention",
    "d2-the-hidden-garden",
    "d3-the-architects-secret",
    "d4-signals-from-kepler",
    "d5-the-winter-of-words",
    "d6-the-bridge-between",
    "pig_mud",
    "jungle_v2",
    "sol_stone_orange",
    "fern_gust_orange",
    "pig_yellow",
    "snail_blue",
    "fox_purple",
    "owl_green",
    "puppy_silver",
]


def image_to_base64_uri(path: Path) -> str:
    """Convert image file to data URI."""
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    ext = path.suffix.lower()
    mime = "image/png" if ext == ".png" else "image/jpeg"
    return f"data:{mime};base64,{b64}"


def download_image(url: str, output_path: Path) -> bool:
    """Download image from URL."""
    try:
        urllib.request.urlretrieve(url, output_path)
        print(f"  ✓ Downloaded to {output_path.name}")
        return True
    except Exception as e:
        print(f"  ✗ Error downloading: {e}")
        return False


def get_cover_prompt(book_path: Path) -> str:
    """Extract cover scene description from book JSON.

    Uses VERY explicit no-text instructions.
    """
    with open(book_path) as f:
        book = json.load(f)

    # Find cover page scene description
    scene = ""
    for page in book.get("pages", []):
        if page.get("type") == "cover" or page.get("page") == 1:
            scene = page.get("scene", "")
            break

    if not scene:
        scene = book.get("summary", "A charming scene")

    # Remove any mention of title/text from scene description
    scene_clean = scene.replace("title", "").replace("text", "").replace("words", "")

    # Build prompt with VERY explicit no-text instructions
    return f"""Children's book cover illustration showing: {scene_clean}

Art style: Soft watercolor illustration with warm colors. Cute, whimsical style appropriate for young children ages 4-7. Charming character designs with expressive faces.

CRITICAL REQUIREMENTS:
- This is a PURE ILLUSTRATION with NO TEXT whatsoever
- Do NOT include any title, words, letters, numbers, or writing
- Do NOT include any text overlays, banners, or labels
- The image should be ONLY artwork - no typography of any kind
- Leave space at the top for a title to be added digitally later
- Focus on the characters and scene, not on any text elements"""


def find_reference(slug: str) -> Path | None:
    """Find reference image for a book (handles _v2, _v3 variants)."""
    # Try exact match first
    ref = REFS_DIR / f"{slug}_reference.png"
    if ref.exists():
        return ref

    # Try versioned variants
    for v in ["_v3", "_v2"]:
        ref = REFS_DIR / f"{slug}_reference{v}.png"
        if ref.exists():
            return ref

    return None


def generate_cover(slug: str, config) -> bool:
    """Generate cover for a book using its reference image."""

    ref_path = find_reference(slug)
    book_path = BOOKS_DIR / f"{slug}.json"
    output_path = COVERS_DIR / f"{slug}.png"

    if not ref_path:
        print(f"  ⚠ No reference image found")
        return False

    if not book_path.exists():
        print(f"  ⚠ No book JSON found")
        return False

    # Get prompt from book
    prompt = get_cover_prompt(book_path)
    print(f"  Scene: {prompt[50:120]}...")

    # Convert reference to base64
    ref_uri = image_to_base64_uri(ref_path)

    # Build request
    body = {
        "prompt": prompt,
        "images": [ref_uri],
        "size": "1024*1024",
        "n": 1
    }

    # Call API
    with APIClient(config) as client:
        result = create_and_poll_task(
            client=client,
            endpoint_path="/vendors/alibaba/v1/wan2.6-image/generation",
            request_body=body,
            result_key="images",
            interval=5.0,
            max_wait=300.0,
            verbose=False
        )

        if result.results:
            url = result.results[0]
            return download_image(url, output_path)
        else:
            print(f"  ✗ Failed: {result.error}")
            return False


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--slug", help="Regenerate specific cover only")
    parser.add_argument("--dry-run", action="store_true", help="Just list what would be regenerated")
    args = parser.parse_args()

    # Determine which covers to regenerate
    if args.slug:
        slugs = [args.slug]
    else:
        slugs = COVERS_WITH_TEXT

    print(f"Regenerating {len(slugs)} covers WITHOUT text:\n")

    if args.dry_run:
        for s in slugs:
            ref = find_reference(s)
            status = "✓ has ref" if ref else "✗ no ref"
            print(f"  {s}: {status}")
        return

    # Load config
    config = load_config()
    print(f"Using API: {config.site}\n")

    # Ensure output dir exists
    COVERS_DIR.mkdir(parents=True, exist_ok=True)

    # Generate covers
    success = 0
    failed = []

    for i, slug in enumerate(slugs):
        print(f"[{i+1}/{len(slugs)}] {slug}")
        if generate_cover(slug, config):
            success += 1
        else:
            failed.append(slug)
        print()

    print(f"\n{'='*50}")
    print(f"Done! Generated {success}/{len(slugs)} covers.")

    if failed:
        print(f"\nFailed ({len(failed)}):")
        for s in failed:
            print(f"  - {s}")


if __name__ == "__main__":
    main()
