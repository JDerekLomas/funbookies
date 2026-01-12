#!/usr/bin/env python3
"""Generate page images for Band C books using reference-based style transfer."""

import sys
import os
import base64
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
PAGES_DIR = BOOKS_DIR / "images"

# Band C books that need page generation
BAND_C_BOOKS = [
    "c1_knight_quest",
    "c2_magic_city",
    "c4_robot_pilot",
    "c5_treehouse_mystery",
    "c6_biggest_race",
    "c7_hopeless_garden",
    "c8_impossible_invention",
]

# Style descriptions for Band C (Early Fluent readers)
BAND_C_STYLE = "Rich detailed watercolor illustration, dynamic compositions, engaging scenes, expressive characters"

# Book-specific style notes
BOOK_STYLES = {
    "c1_knight_quest": "Medieval fantasy style, warm golden lighting, stone castles, mystical forests, noble knights",
    "c2_magic_city": "Magical urban fantasy, crystal towers, glowing bridges, vibrant colors, whimsical architecture",
    "c4_robot_pilot": "Retro sci-fi style, friendly robots, cockpits and control panels, chrome and sky blue, adventure feel",
    "c5_treehouse_mystery": "Cozy adventure style, wooden treehouses, forest settings, warm afternoon light, curious children",
    "c6_biggest_race": "Dynamic sports illustration, motion and energy, competitive spirit, bright action colors",
    "c7_hopeless_garden": "Whimsical garden style, overgrown plants, determined characters, green and earth tones, hope",
    "c8_impossible_invention": "Steampunk-lite style, gears and gadgets, inventor's workshop, brass and copper tones, creativity",
}


def image_to_base64_uri(path: Path) -> str:
    """Convert image file to data URI."""
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return f"data:image/png;base64,{b64}"


def download_image(url: str, output_path: Path) -> bool:
    """Download image from URL."""
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(url, output_path)
        print(f"      Saved: {output_path.name}")
        return True
    except Exception as e:
        print(f"      Error: {e}")
        return False


def get_book_info(slug: str) -> dict:
    """Load book JSON."""
    book_path = BOOKS_DIR / f"{slug}.json"
    with open(book_path) as f:
        return json.load(f)


def get_reference_path(slug: str) -> Path:
    """Find reference image for book (prefer v2 if exists)."""
    v2_path = REFS_DIR / f"{slug}_reference_v2.png"
    v1_path = REFS_DIR / f"{slug}_reference.png"

    if v2_path.exists():
        return v2_path
    elif v1_path.exists():
        return v1_path
    else:
        return None


def generate_page(slug: str, page_num: int, scene: str, ref_path: Path, config) -> bool:
    """Generate a single page using reference image."""

    output_path = PAGES_DIR / f"{slug}_page{str(page_num).zfill(2)}.png"

    # Skip if already exists
    if output_path.exists():
        print(f"    Page {page_num}: Already exists, skipping")
        return True

    print(f"    Page {page_num}: Generating...")

    ref_uri = image_to_base64_uri(ref_path)
    book_style = BOOK_STYLES.get(slug, BAND_C_STYLE)

    prompt = f"""Create ONE SINGLE children's book illustration (not a grid, not multiple panels).

Scene: {scene}

Style: {book_style}
Base style: {BAND_C_STYLE}

Use the reference image to match the art style, colors, and character designs. The reference shows the visual style guide for this book.

OUTPUT: One single illustration filling the entire frame.
IMPORTANT: Do NOT include any text, words, or letters. Pure illustration only."""

    body = {
        "prompt": prompt,
        "images": [ref_uri],
        "size": "1024*1024",
        "n": 1
    }

    with APIClient(config) as client:
        result = create_and_poll_task(
            client=client,
            endpoint_path="/vendors/alibaba/v1/wan2.6-image/generation",
            request_body=body,
            result_key="images",
            interval=5.0,
            max_wait=300.0,
            verbose=False  # Less verbose for batch processing
        )

        if result.results:
            return download_image(result.results[0], output_path)
        else:
            print(f"      Failed: {result.error}")
            return False


def generate_book_pages(slug: str, config) -> int:
    """Generate all pages for one book."""
    print(f"\n{'='*60}")
    print(f"GENERATING: {slug}")
    print('='*60)

    book = get_book_info(slug)
    print(f"Title: {book.get('title')}")

    ref_path = get_reference_path(slug)
    if not ref_path:
        print(f"  ERROR: No reference image found for {slug}")
        return 0

    print(f"Reference: {ref_path.name}")

    # Get pages with scene descriptions
    pages_to_generate = [
        p for p in book.get("pages", [])
        if p.get("scene") or p.get("image_prompt")
    ]

    print(f"Pages to generate: {len(pages_to_generate)}")

    success = 0
    for page in pages_to_generate:
        page_num = page.get("page", 0)
        scene = page.get("scene") or page.get("image_prompt", "")
        if scene and generate_page(slug, page_num, scene, ref_path, config):
            success += 1

    print(f"\n  Completed: {success}/{len(pages_to_generate)} pages for {slug}")
    return success


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate Band C book pages")
    parser.add_argument("--book", type=str, help="Generate specific book only (e.g., c1_knight_quest)")
    parser.add_argument("--all", action="store_true", help="Generate all Band C books")
    args = parser.parse_args()

    # Determine which books to generate
    if args.book:
        books_to_generate = [args.book]
    elif args.all:
        books_to_generate = BAND_C_BOOKS
    else:
        print("Specify --book <slug> or --all")
        print(f"Available: {', '.join(BAND_C_BOOKS)}")
        return

    print("="*60)
    print("BAND C PAGE GENERATION")
    print("="*60)
    print(f"Books: {', '.join(books_to_generate)}")

    config = load_config()
    print(f"API: {config.site}")

    PAGES_DIR.mkdir(parents=True, exist_ok=True)

    total = 0
    for slug in books_to_generate:
        book_path = BOOKS_DIR / f"{slug}.json"
        if not book_path.exists():
            print(f"\nSkipping {slug}: Book not found")
            continue
        total += generate_book_pages(slug, config)

    print("\n" + "="*60)
    print("GENERATION COMPLETE")
    print("="*60)
    print(f"Total pages generated: {total}")


if __name__ == "__main__":
    main()
