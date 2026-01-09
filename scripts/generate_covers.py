#!/usr/bin/env python3
"""Generate book covers using reference images for style consistency."""

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


def generate_cover(slug: str, config) -> bool:
    """Generate cover for a book using its reference image."""

    ref_path = REFS_DIR / f"{slug}_reference.png"
    book_path = BOOKS_DIR / f"{slug}.json"
    output_path = COVERS_DIR / f"{slug}.png"

    if not ref_path.exists():
        print(f"  No reference image found at {ref_path}")
        return False

    if not book_path.exists():
        print(f"  No book JSON found at {book_path}")
        return False

    # Get prompt from book
    prompt = get_cover_prompt(book_path)
    print(f"  Prompt: {prompt[:100]}...")

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
            verbose=True
        )

        if result.results:
            url = result.results[0]
            print(f"  Generated: {url}")
            return download_image(url, output_path)
        else:
            print(f"  Failed: {result.error}")
            return False


def main():
    # Find books with reference images
    refs = list(REFS_DIR.glob("*_reference.png"))
    slugs = [r.stem.replace("_reference", "") for r in refs]

    print(f"Found {len(slugs)} books with reference images:")
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
