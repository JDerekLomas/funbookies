#!/usr/bin/env python3
"""Generate page images for specified books using reference-based style transfer."""

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

# Books to generate pages for (one from each band)
BOOKS_TO_GENERATE = [
    "a1-i-sit",
    "b5-the-ship-in-the-shell",
    "c3_kitten_adventure",
    "d1-the-lighthouse-keeper",
]

# How many story pages to generate per book
PAGES_PER_BOOK = 5


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
        print(f"    Saved: {output_path.name}")
        return True
    except Exception as e:
        print(f"    Error: {e}")
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


def get_style_description(band: str) -> str:
    """Get style description based on reading band."""
    styles = {
        "A": "Simple bold shapes, soft pastel watercolor, minimal detail, toddler-friendly",
        "B": "Playful watercolor, expressive characters, vibrant warm colors",
        "C": "Rich detailed watercolor, dynamic compositions, engaging scenes",
        "D": "Sophisticated illustration, atmospheric lighting, nuanced details"
    }
    return styles.get(band, styles["B"])


def generate_page(slug: str, page_num: int, scene: str, ref_path: Path, band: str, config) -> bool:
    """Generate a single page using reference image."""
    print(f"\n  [PAGE {page_num}] {scene[:60]}...")

    output_path = PAGES_DIR / f"{slug}_page{str(page_num).zfill(2)}.png"

    # Skip if already exists
    if output_path.exists():
        print(f"    Already exists, skipping")
        return True

    ref_uri = image_to_base64_uri(ref_path)
    style = get_style_description(band)

    prompt = f"""Children's book illustration. {scene}

Style: {style}
Match the style, colors, and character designs from the reference image exactly.

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
            verbose=True
        )

        if result.results:
            return download_image(result.results[0], output_path)
        else:
            print(f"    Failed: {result.error}")
            return False


def generate_book_pages(slug: str, config):
    """Generate pages for one book."""
    print(f"\n{'='*60}")
    print(f"GENERATING: {slug}")
    print('='*60)

    book = get_book_info(slug)
    band = book.get("band", "B")
    print(f"Title: {book.get('title')}")
    print(f"Band: {band}")

    ref_path = get_reference_path(slug)
    if not ref_path:
        print(f"  ERROR: No reference image found for {slug}")
        return 0

    print(f"Reference: {ref_path.name}")

    # Get story pages with scenes
    story_pages = [
        p for p in book.get("pages", [])
        if p.get("type") == "story" and p.get("scene")
    ][:PAGES_PER_BOOK]

    print(f"Story pages to generate: {len(story_pages)}")

    success = 0
    for page in story_pages:
        page_num = page.get("page", page.get("story_page", 0))
        scene = page.get("scene", "")
        if scene and generate_page(slug, page_num, scene, ref_path, band, config):
            success += 1

    print(f"\n  Generated {success}/{len(story_pages)} pages for {slug}")
    return success


def main():
    print("="*60)
    print("GENERATING BOOK PAGES")
    print("="*60)
    print(f"\nBooks: {', '.join(BOOKS_TO_GENERATE)}")
    print(f"Pages per book: {PAGES_PER_BOOK}")

    config = load_config()
    print(f"API: {config.site}")

    PAGES_DIR.mkdir(parents=True, exist_ok=True)

    total = 0
    for slug in BOOKS_TO_GENERATE:
        total += generate_book_pages(slug, config)

    print("\n" + "="*60)
    print("GENERATION COMPLETE")
    print("="*60)
    print(f"\nTotal pages generated: {total}")
    print(f"Output: {PAGES_DIR}")


if __name__ == "__main__":
    main()
