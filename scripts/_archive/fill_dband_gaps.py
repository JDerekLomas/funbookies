#!/usr/bin/env python3
"""Fill missing page images for D-band books."""

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

D_BAND_BOOKS = [
    "d2-the-hidden-garden",
    "d3-the-architects-secret",
    "d4-signals-from-kepler",
    "d5-the-winter-of-words",
    "d6-the-bridge-between",
]


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


def get_reference_path(slug: str) -> Path:
    """Find reference image for book."""
    for suffix in ["_reference_v2.png", "_reference.png"]:
        path = REFS_DIR / f"{slug}{suffix}"
        if path.exists():
            return path
    return None


def get_missing_pages(slug: str) -> list:
    """Get list of pages that need images."""
    book_path = BOOKS_DIR / f"{slug}.json"
    with open(book_path) as f:
        book = json.load(f)

    missing = []
    for page in book.get("pages", []):
        if not page.get("scene"):
            continue

        page_num = page.get("page")
        image_path = PAGES_DIR / f"{slug}_page{str(page_num).zfill(2)}.png"

        if not image_path.exists():
            missing.append({
                "page": page_num,
                "scene": page.get("scene"),
                "text": page.get("text", "")
            })

    return missing


def generate_page(slug: str, page_info: dict, ref_path: Path, config) -> bool:
    """Generate a single page image."""
    page_num = page_info["page"]
    output_path = PAGES_DIR / f"{slug}_page{str(page_num).zfill(2)}.png"

    if output_path.exists():
        return True

    print(f"    Page {page_num}: Generating...")

    ref_uri = image_to_base64_uri(ref_path)

    prompt = f"""Create ONE SINGLE children's book illustration (not a grid, not multiple panels).

Scene: {page_info['scene']}

Text on this page: "{page_info['text']}"

Use the reference image to match the art style, colors, and character designs. This is for an advanced children's chapter book (Band D - ages 8-10).

Style: Rich detailed watercolor illustration, dynamic compositions, engaging scenes.

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
            verbose=False
        )

        if result.results:
            return download_image(result.results[0], output_path)
        else:
            print(f"      Failed: {result.error}")
            return False


def fill_book_gaps(slug: str, config) -> int:
    """Fill missing pages for one book."""
    print(f"\n{'='*50}")
    print(f"FILLING GAPS: {slug}")
    print("="*50)

    ref_path = get_reference_path(slug)
    if not ref_path:
        print(f"  ERROR: No reference image found")
        return 0

    missing = get_missing_pages(slug)
    print(f"  Missing pages: {len(missing)}")

    if not missing:
        print(f"  All pages complete!")
        return 0

    success = 0
    for page_info in missing:
        if generate_page(slug, page_info, ref_path, config):
            success += 1

    print(f"  Generated: {success}/{len(missing)} pages")
    return success


def main():
    print("="*60)
    print("FILLING D-BAND PAGE GAPS")
    print("="*60)

    config = load_config()
    print(f"API: {config.site}")

    PAGES_DIR.mkdir(parents=True, exist_ok=True)

    total = 0
    for slug in D_BAND_BOOKS:
        total += fill_book_gaps(slug, config)

    print("\n" + "="*60)
    print(f"COMPLETE: Generated {total} pages")
    print("="*60)


if __name__ == "__main__":
    main()
