#!/usr/bin/env python3
"""Generate book covers using reference images for style consistency.

Supports two providers:
- fal.ai (default): $0.03/image for wan2.6 - 80% cheaper!
- mulerouter: $0.10-0.15/image for wan2.6

Saves generation metadata to book JSON:
- cover_metadata.generated_at: ISO timestamp
- cover_metadata.model: model used
- cover_metadata.provider: fal or mulerouter
- cover_metadata.used_reference: whether reference was used
- cover_metadata.reference_version: which reference version
"""

import sys
import os
import json
import urllib.request
from pathlib import Path
from datetime import datetime

# Setup paths relative to project root
from dotenv import load_dotenv
PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / ".env")
load_dotenv(PROJECT_ROOT / ".env.local")

# For MuleRouter fallback - configurable via env var
SKILL_DIR = Path(os.getenv("MULEROUTER_SKILL_DIR", str(Path.home() / ".claude/plugins/cache/mulerouter-skills/mulerouter-skills/1.0.0/skills/mulerouter-skills")))

# Import fal client
from fal_client import FalClient, GenerationResult

# Import shared utilities
from image_utils import (
    BOOKS_DIR, COVERS_DIR, REFS_DIR,
    image_to_base64_uri, find_reference_image, get_character_block
)
from image_log import log_image_generation


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

    # Get art style from story_bible if available
    story_bible = book.get("story_bible", {})
    if story_bible.get("visual_style"):
        style = story_bible["visual_style"]
    else:
        style = "Soft watercolor illustration, warm colors, cute whimsical style for young children aged 4-7"

    # Get character block
    char_block = get_character_block(book)

    # Build prompt WITHOUT any text/title instructions
    # For fal.ai wan2.6, we add "using style of image 1" to trigger style transfer
    if char_block:
        return f"""Generate an image using the style of image 1.

Children's book cover illustration. {scene}

CHARACTERS (draw EXACTLY as described):
{char_block}

Style: {style}

IMPORTANT: Do NOT include any text, titles, words, or letters in the image. Pure illustration only."""
    else:
        return f"""Generate an image using the style of image 1.

Children's book cover illustration. {scene}

Style: {style}

IMPORTANT: Do NOT include any text, titles, words, or letters in the image. Pure illustration only."""


def generate_cover_fal(slug: str, fal_client: FalClient) -> bool:
    """Generate cover using fal.ai (default, cheaper)."""

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

    model = "wan2.6-image"

    # Generate using fal.ai
    result = fal_client.generate_with_reference(
        prompt=prompt,
        reference_images=[ref_path],
        model=model,
        size="1024x1024",
        verbose=True,
    )

    if result.success:
        print(f"  Generated: {result.url[:60]}...")

        if download_image(result.url, output_path):
            # Save metadata to book JSON
            with open(book_path) as f:
                book = json.load(f)

            book["cover_metadata"] = {
                "generated_at": datetime.now().isoformat(),
                "model": model,
                "provider": "fal.ai",
                "used_reference": True,
                "reference_version": ref_version,
                "prompt": prompt,
                "cost": "$0.03",  # wan2.6 I2I price
            }

            with open(book_path, 'w') as f:
                json.dump(book, f, indent=2)

            print(f"  Metadata saved to book JSON")
            return True
        return False
    else:
        print(f"  Failed: {result.error}")
        return False


def generate_cover_mulerouter(slug: str, config) -> bool:
    """Generate cover using MuleRouter (fallback)."""

    # Import MuleRouter modules
    sys.path.insert(0, str(SKILL_DIR))
    load_dotenv(SKILL_DIR / ".env")
    from core import APIClient, create_and_poll_task

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

    # Get prompt from book (strip fal.ai-specific prefix)
    prompt = get_cover_prompt(book_path)
    prompt = prompt.replace("Generate an image using the style of image 1.\n\n", "")
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
                    "provider": "mulerouter",
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
    parser.add_argument("--provider", choices=["fal", "mulerouter"], default="fal",
                        help="API provider (default: fal - 80%% cheaper)")
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
        print("")
        print("Options:")
        print("  --provider fal        Use fal.ai (default, $0.03/image)")
        print("  --provider mulerouter Use MuleRouter (~$0.10-0.15/image)")
        return

    print(f"Generating covers for {len(slugs)} books:")
    for s in slugs:
        print(f"  - {s}")

    print(f"\nUsing provider: {args.provider}")
    if args.provider == "fal":
        print("  Cost: $0.03 per image (wan2.6 I2I)")
        print(f"  Estimated total: ${len(slugs) * 0.03:.2f}")
    else:
        print("  Cost: ~$0.10-0.15 per image")
        print(f"  Estimated total: ${len(slugs) * 0.12:.2f}")

    # Initialize client based on provider
    if args.provider == "fal":
        try:
            client = FalClient()
            print(f"  API key: {client.fal_key[:8]}...")
        except ValueError as e:
            print(f"\nError: {e}")
            return
    else:
        sys.path.insert(0, str(SKILL_DIR))
        load_dotenv(SKILL_DIR / ".env")
        from core import load_config
        client = load_config()
        print(f"  API: {client.site}")

    # Ensure output dir exists
    COVERS_DIR.mkdir(parents=True, exist_ok=True)

    # Generate covers
    success = 0
    for slug in slugs:
        print(f"\n[{slug}]")
        if args.provider == "fal":
            if generate_cover_fal(slug, client):
                success += 1
        else:
            if generate_cover_mulerouter(slug, client):
                success += 1

    print(f"\n\nDone! Generated {success}/{len(slugs)} covers.")
    if args.provider == "fal":
        print(f"Total cost: ~${success * 0.03:.2f}")


if __name__ == "__main__":
    main()
