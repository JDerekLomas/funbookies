#!/usr/bin/env python3
"""Generate all images for Pip and the Well book."""

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

BOOK_SLUG = "pip_well_orange"


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
        print(f"  Saved: {output_path}")
        return True
    except Exception as e:
        print(f"  Error downloading: {e}")
        return False


def get_book_info() -> dict:
    """Load the book JSON."""
    book_path = BOOKS_DIR / f"{BOOK_SLUG}.json"
    with open(book_path) as f:
        return json.load(f)


def generate_reference(config) -> bool:
    """Generate 9-panel reference sheet with correct Pip character design."""

    output_path = REFS_DIR / f"{BOOK_SLUG}_reference_v2.png"

    book = get_book_info()
    char = book["character"]
    art = book["art_direction"]
    palette = art["palette"]

    prompt = f"""A 9-panel character and style reference sheet for a children's picture book.

MAIN CHARACTER - PIP THE TOAD:
{char['style_notes']}
- Species: {char['pip']['species']}
- Body color: {char['pip']['color']}
- Eyes: {char['pip']['eyes']}
- Distinguishing feature: {char['pip']['distinguishing_feature']}
- Body: {char['pip']['body']}
- Expression: {char['pip']['expression_default']}

ART STYLE: {art['style']}
Influences: {', '.join(art['influences'])}
Mood: {art['mood']}

COLOR PALETTE:
- Pip body: {palette['pip_body']} (teal-green)
- Pip belly: {palette['pip_belly']} (cream)
- Pip blue spot: {palette['pip_spot']}
- Well stone: {palette['well_stone']} (gray)
- Well dark: {palette['well_dark']}
- Water: {palette['water_blue']} and {palette['water_deep']}
- Grass: {palette['grass_green']}
- Sky/Background: {palette['sky_blue']} and {palette['background_soft']}

9 PANELS (3x3 grid):
Panel 1: Pip sitting alone, looking peaceful but slightly wistful - full body view
Panel 2: Pip hopping joyfully - motion pose
Panel 3: Pip with surprised/wondering expression - close-up face
Panel 4: Pip shouting with mouth wide open - expressive pose
Panel 5: Pip looking happy and wet with water droplets
Panel 6: Pip with eyes closed, serene smile - peaceful expression
Panel 7: The stone well - circular, weathered gray stones, dark opening
Panel 8: Water splashing with blue droplets and white highlights
Panel 9: Sunset scene with well, warm orange-pink sky

CRITICAL: Pip is a TOAD (small amphibian), NOT a human child. Round body, no neck, stubby legs, large expressive eyes with blue highlights. Simple cartoon style with bold black outlines and flat colors. Mo Willems expressiveness meets Jon Klassen stillness.

NO TEXT OR WORDS IN ANY PANEL."""

    print("Generating reference sheet...")
    print(f"Prompt length: {len(prompt)} chars")

    body = {
        "prompt": prompt,
        "size": "1024*1024",
        "n": 1
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
            print(f"  Failed: {result.error}")
            return False


def generate_cover(config) -> bool:
    """Generate cover image using reference."""

    ref_path = REFS_DIR / f"{BOOK_SLUG}_reference_v2.png"
    if not ref_path.exists():
        ref_path = REFS_DIR / f"{BOOK_SLUG}_reference.png"

    if not ref_path.exists():
        print("  ERROR: No reference image found")
        return False

    output_path = COVERS_DIR / f"{BOOK_SLUG}.png"

    book = get_book_info()
    cover_page = next((p for p in book["pages"] if p.get("type") == "cover"), None)

    if not cover_page or not cover_page.get("image_prompt"):
        print("  ERROR: No cover prompt found")
        return False

    ref_uri = image_to_base64_uri(ref_path)

    prompt = f"""Create ONE SINGLE children's book cover illustration (not a grid).

{cover_page['image_prompt']}

Use the reference image for style consistency - match the art style, colors, and character design of Pip the toad.

OUTPUT: One single illustration filling the entire frame.
IMPORTANT: NO TEXT, NO TITLE, NO WORDS - pure illustration only."""

    print("Generating cover...")

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
            print(f"  Failed: {result.error}")
            return False


def generate_page(page_num: int, image_prompt: str, ref_path: Path, config, force: bool = False) -> bool:
    """Generate a single page image."""

    output_path = PAGES_DIR / f"{BOOK_SLUG}_page{str(page_num).zfill(2)}.png"

    # Skip if exists (unless force)
    if output_path.exists() and not force:
        print(f"  Page {page_num}: Already exists, skipping")
        return True

    ref_uri = image_to_base64_uri(ref_path)

    prompt = f"""Create ONE SINGLE children's book illustration (not a grid, not multiple panels).

{image_prompt}

Use the reference image for style consistency - match the art style, colors, and character design of Pip the toad.

OUTPUT: One single illustration filling the entire frame.
IMPORTANT: NO TEXT, NO WORDS - pure illustration only."""

    print(f"  Generating page {page_num}...")

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


def generate_all_pages(config) -> int:
    """Generate all page images."""

    ref_path = REFS_DIR / f"{BOOK_SLUG}_reference_v2.png"
    if not ref_path.exists():
        ref_path = REFS_DIR / f"{BOOK_SLUG}_reference.png"

    if not ref_path.exists():
        print("ERROR: No reference image found")
        return 0

    book = get_book_info()

    # Get pages with image prompts (skip wordlist page)
    pages_to_generate = [
        p for p in book["pages"]
        if p.get("image_prompt") and p.get("type") != "wordlist"
    ]

    print(f"\nGenerating {len(pages_to_generate)} page images...")

    success = 0
    for page in pages_to_generate:
        page_num = page["page"]
        if generate_page(page_num, page["image_prompt"], ref_path, config):
            success += 1

    return success


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate Pip and the Well images")
    parser.add_argument("--reference", action="store_true", help="Generate reference sheet only")
    parser.add_argument("--cover", action="store_true", help="Generate cover only")
    parser.add_argument("--pages", action="store_true", help="Generate pages only")
    parser.add_argument("--all", action="store_true", help="Generate everything")
    parser.add_argument("--force", action="store_true", help="Regenerate even if exists")
    args = parser.parse_args()

    # Default to --all if nothing specified
    if not any([args.reference, args.cover, args.pages, args.all]):
        args.all = True

    config = load_config()
    print(f"API: {config.site}")

    REFS_DIR.mkdir(parents=True, exist_ok=True)
    PAGES_DIR.mkdir(parents=True, exist_ok=True)
    COVERS_DIR.mkdir(parents=True, exist_ok=True)

    if args.reference or args.all:
        print("\n" + "="*60)
        print("STEP 1: REFERENCE SHEET")
        print("="*60)
        if generate_reference(config):
            print("Reference sheet generated successfully!")
        else:
            print("Failed to generate reference sheet")
            if args.all:
                print("Stopping - reference is needed for other images")
                return

    if args.cover or args.all:
        print("\n" + "="*60)
        print("STEP 2: COVER IMAGE")
        print("="*60)
        if generate_cover(config):
            print("Cover generated successfully!")
        else:
            print("Failed to generate cover")

    if args.pages or args.all:
        print("\n" + "="*60)
        print("STEP 3: PAGE IMAGES")
        print("="*60)
        count = generate_all_pages(config)
        print(f"\nGenerated {count} page images")

    print("\n" + "="*60)
    print("GENERATION COMPLETE")
    print("="*60)
    print(f"\nView at: https://funbookies.com/reader.html?book={BOOK_SLUG}")


if __name__ == "__main__":
    main()
