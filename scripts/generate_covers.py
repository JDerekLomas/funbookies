#!/usr/bin/env python3
"""Generate book covers using reference images for style consistency.

Saves generation metadata to book JSON:
- cover_metadata.generated_at: ISO timestamp
- cover_metadata.model: model used
- cover_metadata.used_reference: whether reference was used
- cover_metadata.reference_version: which reference version
"""

import sys
import os
import base64
import json
import urllib.request
from pathlib import Path
from datetime import datetime

# Add the skill directory to path
SKILL_DIR = Path("/Users/dereklomas/.claude/plugins/cache/mulerouter-skills/mulerouter-skills/1.0.0/skills/mulerouter-skills")
sys.path.insert(0, str(SKILL_DIR))

from dotenv import load_dotenv
load_dotenv(SKILL_DIR / ".env")

from core import APIClient, load_config, create_and_poll_task

BOOKS_DIR = Path("/Users/dereklomas/lilbookies/public/books")
COVERS_DIR = Path("/Users/dereklomas/lilbookies/public/images/covers")
REFS_DIR = BOOKS_DIR / "references"


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
        print(f"  Downloaded to {output_path}")
        return True
    except Exception as e:
        print(f"  Error downloading: {e}")
        return False


def get_cover_prompt(book_path: Path) -> str:
    """Extract cover scene description from book JSON.

    IMPORTANT: Prompts explicitly exclude text/titles - covers should be
    pure illustrations. Text overlays are added by the reader UI.
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

    # Build prompt WITHOUT any text/title instructions
    return f"""Children's book cover illustration. {scene}

Style: Soft watercolor illustration, warm colors, cute whimsical style for young children aged 4-7.

IMPORTANT: Do NOT include any text, titles, words, or letters in the image. Pure illustration only."""


def find_reference_image(slug: str) -> tuple[Path | None, str | None]:
    """Find the reference image for a book, checking versioned files.

    Returns: (path, version) or (None, None) if not found
    """
    versions = ["_v4", "_v3", "_v2", ""]
    for version in versions:
        suffix = f"_reference{version}.png"
        path = REFS_DIR / f"{slug}{suffix}"
        if path.exists():
            version_str = version.replace("_", "") if version else "v1"
            return path, version_str
    return None, None


def generate_cover(slug: str, config) -> bool:
    """Generate cover for a book using its reference image."""

    ref_path, ref_version = find_reference_image(slug)
    book_path = BOOKS_DIR / f"{slug}.json"
    output_path = COVERS_DIR / f"{slug}.png"

    if not ref_path:
        print(f"  No reference image found for {slug}")
        return False

    if not book_path.exists():
        print(f"  No book JSON found at {book_path}")
        return False

    print(f"  Using reference: {ref_version}")

    # Get prompt from book
    prompt = get_cover_prompt(book_path)
    print(f"  Prompt: {prompt[:100]}...")

    # Convert reference to base64
    ref_uri = image_to_base64_uri(ref_path)

    model = "wan2.6-image"

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
            endpoint_path=f"/vendors/alibaba/v1/{model}/generation",
            request_body=body,
            result_key="images",
            interval=5.0,
            max_wait=300.0,
            verbose=True
        )

        if result.results:
            url = result.results[0]
            print(f"  Generated: {url}")

            if download_image(url, output_path):
                # Save metadata to book JSON
                with open(book_path) as f:
                    book = json.load(f)

                book["cover_metadata"] = {
                    "generated_at": datetime.now().isoformat(),
                    "model": model,
                    "used_reference": True,
                    "reference_version": ref_version,
                    "prompt": prompt
                }

                with open(book_path, 'w') as f:
                    json.dump(book, f, indent=2)

                print(f"  Metadata saved to book JSON")
                return True
            return False
        else:
            print(f"  Failed: {result.error}")
            return False


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate book covers")
    parser.add_argument("--book", help="Single book slug to generate")
    parser.add_argument("--all", action="store_true", help="Generate for all books with references")
    args = parser.parse_args()

    if args.book:
        # Single book mode
        slugs = [args.book]
        # Check reference exists
        ref_path, _ = find_reference_image(args.book)
        if not ref_path:
            print(f"No reference image found for: {args.book}")
            return
    elif args.all:
        # Find all books with reference images
        refs = list(REFS_DIR.glob("*_reference*.png"))
        slugs = list(set(r.stem.split("_reference")[0] for r in refs))
    else:
        print("Usage: python generate_covers.py --book SLUG")
        print("       python generate_covers.py --all")
        return

    print(f"Generating covers for {len(slugs)} books:")
    for s in slugs:
        print(f"  - {s}")

    # Load config
    config = load_config()
    print(f"\nUsing API: {config.site}")

    # Ensure output dir exists
    COVERS_DIR.mkdir(parents=True, exist_ok=True)

    # Generate covers
    success = 0
    for slug in slugs:
        print(f"\n[{slug}]")
        if generate_cover(slug, config):
            success += 1

    print(f"\n\nDone! Generated {success}/{len(slugs)} covers.")


if __name__ == "__main__":
    main()
