#!/usr/bin/env python3
"""Generate page images for a book using MuleRouter API.

Uses nano-banana-pro with consistent character descriptions in every prompt
to maintain visual coherence across the book.
"""

import json
import time
import requests
from pathlib import Path

BOOKS_DIR = Path("/Users/dereklomas/lilbookies/public/books")
API_URL = "https://funbookies.com/api"


def get_character_block(book: dict) -> str:
    """Extract a consistent character description block."""
    characters = book.get("character", {})

    char_lines = []
    for key, value in characters.items():
        if isinstance(value, dict) and key not in ["names", "style_notes"]:
            name = key.capitalize()
            species = value.get("species", "")
            color = value.get("color", "")
            body = value.get("body", "")
            distinguishing = value.get("distinguishing_feature", "")

            parts = []
            if species:
                parts.append(species)
            if color:
                parts.append(f"({color})")
            if body:
                parts.append(body)
            if distinguishing:
                parts.append(f"- {distinguishing}")

            if parts:
                char_lines.append(f"{name}: {' '.join(parts)}")

    return "\n".join(char_lines)


def build_image_prompt(book: dict, page: dict) -> str:
    """Build a simple, focused image prompt."""

    scene = page.get("scene", "")
    if not scene:
        return ""

    # Get art style
    art_dir = book.get("art_direction", {})
    style = art_dir.get("style", "children's book illustration, simple shapes, bold outlines")

    # Get character block for consistency
    char_block = get_character_block(book)

    # Build simple prompt
    prompt = f"""{scene}

CHARACTERS (draw exactly as described):
{char_block}

STYLE: {style}

IMPORTANT: NO TEXT, NO WORDS, NO LETTERS in the image. Visual storytelling only."""

    return prompt


def generate_image(prompt: str, slug: str, page_num: int) -> str:
    """Generate an image using nano-banana-pro."""

    print(f"  Generating page {page_num}...")

    # Submit generation request - use nano-banana-pro for consistency
    response = requests.post(f"{API_URL}/generate-image", json={
        "prompt": prompt,
        "model": "nano-banana-pro",
        "slug": slug,
        "page": page_num
    })

    result = response.json()

    if not result.get("success"):
        print(f"    Error: {result.get('error')}")
        return None

    if result.get("pending"):
        task_id = result["taskId"]
        endpoint = result["statusEndpoint"]
        print(f"    Task: {task_id[:8]}...")

        # Poll for completion
        for i in range(60):  # Max 5 minutes
            time.sleep(5)
            try:
                status_resp = requests.get(f"{API_URL}/check-status", params={
                    "taskId": task_id,
                    "endpoint": endpoint
                }, timeout=30)
                status = status_resp.json()

                if status.get("completed"):
                    print(f"    Done!")
                    return status["url"]

                if not status.get("success"):
                    print(f"    Error: {status.get('error')}")
                    return None

                print(f"    Polling... ({i+1})")
            except Exception as e:
                print(f"    Network error, retrying... ({e})")
                time.sleep(5)

        print("    Timeout!")
        return None

    # Immediate result
    return result.get("url")


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("slug", help="Book slug to process")
    parser.add_argument("--pages", help="Comma-separated page numbers (default: all)")
    parser.add_argument("--dry-run", action="store_true", help="Show prompts only")
    parser.add_argument("--force", action="store_true", help="Regenerate even if image exists")
    args = parser.parse_args()

    book_file = BOOKS_DIR / f"{args.slug}.json"
    if not book_file.exists():
        print(f"Book not found: {args.slug}")
        return

    with open(book_file) as f:
        book = json.load(f)

    pages = book.get("pages", [])

    # Filter pages if specified
    if args.pages:
        page_nums = [int(p) for p in args.pages.split(",")]
        pages = [p for p in pages if p["page"] in page_nums]

    print(f"Processing {len(pages)} pages for {args.slug}\n")

    # Show character block for reference
    char_block = get_character_block(book)
    print(f"Character consistency block:\n{char_block}\n")
    print("-" * 50)

    updated = 0
    for page in pages:
        page_num = page["page"]
        scene = page.get("scene", "")

        # Skip pages without scenes
        if not scene:
            print(f"Page {page_num}: Skipping (no scene)")
            continue

        # Skip if already has image (unless --force)
        if page.get("image") and not args.force:
            print(f"Page {page_num}: Already has image")
            continue

        # Build prompt
        prompt = build_image_prompt(book, page)
        page["image_prompt"] = prompt

        if args.dry_run:
            print(f"\n=== Page {page_num} ===")
            print(prompt)
            print()
            continue

        # Generate image
        image_url = generate_image(prompt, args.slug, page_num)

        if image_url:
            page["image"] = image_url
            updated += 1

            # Save after each successful generation
            with open(book_file, 'w') as f:
                json.dump(book, f, indent=2)

        time.sleep(2)  # Rate limiting

    if not args.dry_run:
        print(f"\nDone! Generated {updated} images.")


if __name__ == "__main__":
    main()
