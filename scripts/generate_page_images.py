#!/usr/bin/env python3
"""Generate page images for a book using MuleRouter API.

Uses nano-banana-pro with consistent character descriptions in every prompt
to maintain visual coherence across the book.

Saves generation metadata for each image including:
- generated_at: ISO timestamp
- model: model used for generation
- used_reference: whether style transfer was used
- reference_version: which reference image version was used (if applicable)
"""

import json
import time
import requests
from pathlib import Path
from datetime import datetime

BOOKS_DIR = Path("/Users/dereklomas/lilbookies/public/books")
REFS_DIR = BOOKS_DIR / "references"
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


def find_reference_image(slug: str) -> tuple[str | None, str | None]:
    """Find the reference image for a book, checking versioned files.

    Returns: (path, version) or (None, None) if not found
    """
    versions = ["_v4", "_v3", "_v2", ""]
    for version in versions:
        suffix = f"_reference{version}.png"
        path = REFS_DIR / f"{slug}{suffix}"
        if path.exists():
            version_str = version.replace("_", "") if version else "v1"
            return str(path), version_str
    return None, None


def generate_image(prompt: str, slug: str, page_num: int, use_reference: bool = False) -> dict | None:
    """Generate an image using nano-banana-pro.

    Returns: dict with 'url' and 'metadata' or None on failure
    """

    print(f"  Generating page {page_num}...")

    model = "nano-banana-pro"
    ref_path, ref_version = None, None

    if use_reference:
        ref_path, ref_version = find_reference_image(slug)
        if ref_path:
            print(f"    Using reference: {ref_version}")
            model = "wan2.6-image"  # Use I2I model with reference
        else:
            print(f"    No reference found, using T2I")

    # Submit generation request
    payload = {
        "prompt": prompt,
        "model": model,
        "slug": slug,
        "page": page_num
    }

    # Add reference for I2I if available
    if ref_path and use_reference:
        payload["reference_image"] = f"/books/references/{slug}_reference{('_' + ref_version) if ref_version != 'v1' else ''}.png"

    response = requests.post(f"{API_URL}/generate-image", json=payload)
    result = response.json()

    if not result.get("success"):
        print(f"    Error: {result.get('error')}")
        return None

    image_url = None

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
                    image_url = status["url"]
                    break

                if not status.get("success"):
                    print(f"    Error: {status.get('error')}")
                    return None

                print(f"    Polling... ({i+1})")
            except Exception as e:
                print(f"    Network error, retrying... ({e})")
                time.sleep(5)
        else:
            print("    Timeout!")
            return None
    else:
        # Immediate result
        image_url = result.get("url")

    if not image_url:
        return None

    # Return URL with metadata
    return {
        "url": image_url,
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "model": model,
            "used_reference": bool(ref_path and use_reference),
            "reference_version": ref_version if (ref_path and use_reference) else None,
        }
    }


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("slug", help="Book slug to process")
    parser.add_argument("--pages", help="Comma-separated page numbers (default: all)")
    parser.add_argument("--dry-run", action="store_true", help="Show prompts only")
    parser.add_argument("--force", action="store_true", help="Regenerate even if image exists")
    parser.add_argument("--use-reference", action="store_true", help="Use I2I with reference sheet")
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

    # Check for reference image
    ref_path, ref_version = find_reference_image(args.slug)
    if ref_path:
        print(f"Reference image found: {ref_version}")
    else:
        print("No reference image found")

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

        # Generate image with metadata
        result = generate_image(prompt, args.slug, page_num, use_reference=args.use_reference)

        if result:
            page["image"] = result["url"]
            page["generation_metadata"] = result["metadata"]
            updated += 1

            # Save after each successful generation
            with open(book_file, 'w') as f:
                json.dump(book, f, indent=2)

        time.sleep(2)  # Rate limiting

    if not args.dry_run:
        print(f"\nDone! Generated {updated} images.")


if __name__ == "__main__":
    main()
