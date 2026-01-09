#!/usr/bin/env python3
"""Test the full generation workflow: reference → pages.

Uses nano-banana for high-quality reference sheets,
then wan2.6-image for page generation.
"""

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
COVERS_DIR = Path("/Users/dereklomas/lilbookies/public/images/covers")

# Test books - one from each band
TEST_BOOKS = ["a0-look", "b2-pup-in-the-mud", "c1_knight_quest"]


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


def build_reference_prompt(book: dict) -> str:
    """Build prompt for 9-panel reference sheet."""
    title = book.get("title", "Book")
    band = book.get("band", "B")

    # Get first 9 scenes
    scenes = []
    for page in book.get("pages", []):
        scene = page.get("scene", "")
        if scene:
            scenes.append(scene[:80])
        if len(scenes) >= 9:
            break

    # Pad if needed
    while len(scenes) < 9:
        scenes.append(f"Scene from {title}")

    # Style by band
    styles = {
        "A": "Simple bold shapes, soft pastel watercolor, minimal detail, toddler-friendly",
        "B": "Playful watercolor, expressive characters, vibrant warm colors",
        "C": "Rich detailed watercolor, dynamic compositions, engaging scenes",
        "D": "Sophisticated illustration, atmospheric lighting, nuanced details"
    }
    style = styles.get(band, styles["B"])

    panels = "\n".join([f"Panel {i+1}: {s}" for i, s in enumerate(scenes)])

    return f"""A 9-panel reference sheet for children's book illustration, arranged in a 3x3 grid.

Style: {style}

The panels show:
{panels}

Each panel is a square vignette with consistent art style. Warm, friendly watercolor illustration suitable for children aged 4-7.

IMPORTANT: Do NOT include any text, words, or letters. Pure illustration only. White borders between panels."""


def generate_reference_nano(slug: str, book: dict, config) -> bool:
    """Generate reference using nano-banana (high quality)."""
    print(f"\n  [REFERENCE] Using nano-banana-pro...")

    prompt = build_reference_prompt(book)
    output_path = REFS_DIR / f"{slug}_reference_v2.png"

    body = {
        "prompt": prompt,
        "aspect_ratio": "1:1",
        "resolution": "2K"
    }

    with APIClient(config) as client:
        result = create_and_poll_task(
            client=client,
            endpoint_path="/vendors/google/v1/nano-banana-pro/generation",
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


def generate_page(slug: str, page_num: int, scene: str, ref_path: Path, config) -> bool:
    """Generate a single page using reference image."""
    print(f"\n  [PAGE {page_num}] {scene[:50]}...")

    output_path = PAGES_DIR / f"{slug}_page{str(page_num).zfill(2)}.png"

    ref_uri = image_to_base64_uri(ref_path)

    prompt = f"""Children's book illustration. {scene}

Match the style, colors, and character designs from the reference image exactly.
Warm watercolor style, friendly and inviting.

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


def test_book(slug: str, config):
    """Test full workflow for one book."""
    print(f"\n{'='*60}")
    print(f"TESTING: {slug}")
    print('='*60)

    book = get_book_info(slug)
    print(f"Title: {book.get('title')}")
    print(f"Band: {book.get('band', '?')}")

    # Step 1: Generate reference with nano-banana
    if not generate_reference_nano(slug, book, config):
        print("  FAILED to generate reference")
        return

    ref_path = REFS_DIR / f"{slug}_reference_v2.png"

    # Step 2: Generate first 3 story pages
    story_pages = [p for p in book.get("pages", []) if p.get("scene") and p.get("type") != "cover"][:3]

    for i, page in enumerate(story_pages):
        page_num = page.get("page", i + 2)
        scene = page.get("scene", "")
        if scene:
            generate_page(slug, page_num, scene, ref_path, config)

    print(f"\n  DONE: {slug}")


def main():
    print("="*60)
    print("TESTING IMAGE GENERATION WORKFLOW")
    print("="*60)
    print("\nReference: nano-banana-pro (high quality)")
    print("Pages: wan2.6-image (style transfer)")
    print(f"\nTest books: {', '.join(TEST_BOOKS)}")

    config = load_config()
    print(f"API: {config.site}")

    REFS_DIR.mkdir(parents=True, exist_ok=True)
    PAGES_DIR.mkdir(parents=True, exist_ok=True)

    for slug in TEST_BOOKS:
        test_book(slug, config)

    print("\n" + "="*60)
    print("WORKFLOW TEST COMPLETE")
    print("="*60)
    print(f"\nGenerated files:")
    print(f"  References: {REFS_DIR}/*_reference_v2.png")
    print(f"  Pages: {PAGES_DIR}/*_page*.png")


if __name__ == "__main__":
    main()
