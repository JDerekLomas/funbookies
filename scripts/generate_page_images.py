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

import sys
import json
import time
import base64
import urllib.request
from pathlib import Path
from datetime import datetime

# Add MuleRouter skills to path
SKILL_DIR = Path("/Users/dereklomas/.claude/plugins/cache/mulerouter-skills/mulerouter-skills/1.0.0/skills/mulerouter-skills")
sys.path.insert(0, str(SKILL_DIR))

from dotenv import load_dotenv
load_dotenv(SKILL_DIR / ".env")

from core import APIClient, load_config, create_and_poll_task

BOOKS_DIR = Path("/Users/dereklomas/lilbookies/public/books")
REFS_DIR = BOOKS_DIR / "references"
IMAGES_DIR = BOOKS_DIR / "images"


def image_to_base64_uri(path: Path) -> str:
    """Convert image file to data URI."""
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    ext = path.suffix.lower()
    mime = "image/png" if ext == ".png" else "image/jpeg"
    return f"data:{mime};base64,{b64}"


def get_character_block(book: dict) -> str:
    """Extract a consistent character description block.

    Uses visual_shorthand from characters field for concise, consistent descriptions.
    Falls back to building from appearance fields if shorthand not available.
    """
    # Try new schema first (characters plural)
    characters = book.get("characters", {})

    # Fall back to old schema (character singular)
    if not characters:
        characters = book.get("character", {})

    char_lines = []
    for key, char_data in characters.items():
        if isinstance(char_data, dict) and key not in ["names", "style_notes"]:
            # Prefer visual_shorthand if available (new schema)
            if char_data.get("visual_shorthand"):
                char_lines.append(char_data["visual_shorthand"])
            elif char_data.get("appearance"):
                # Build from appearance (new schema)
                app = char_data["appearance"]
                name = char_data.get("name", key.capitalize())
                parts = [f"{name}:"]
                if app.get("body"):
                    parts.append(app["body"])
                if app.get("fur_color"):
                    parts.append(f"with {app['fur_color']} fur")
                if app.get("distinguishing_mark"):
                    parts.append(f"- {app['distinguishing_mark']} (KEY FEATURE)")
                if app.get("ears"):
                    parts.append(f"- {app['ears']}")
                if app.get("tail"):
                    parts.append(f"- {app['tail']}")
                if app.get("posture"):
                    parts.append(f"- {app['posture']}")
                char_lines.append(" ".join(parts))
            else:
                # Old schema fallback
                name = key.capitalize()
                species = char_data.get("species", "")
                color = char_data.get("color", "")
                body = char_data.get("body", "")
                distinguishing = char_data.get("distinguishing_feature", "")

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

    # Get art style - priority: story_bible.visual_style > art_direction.style > default
    story_bible = book.get("story_bible", {})
    art_dir = book.get("art_direction", {})

    if story_bible.get("visual_style"):
        style = story_bible["visual_style"]
    elif art_dir.get("style"):
        style = art_dir["style"]
    else:
        style = "children's book illustration, simple shapes, bold outlines"

    # Get character block for consistency
    char_block = get_character_block(book)

    # Build prompt with character block only if we have characters
    if char_block:
        prompt = f"""{scene}

CHARACTERS (draw EXACTLY as described - these features are KEY for identification):
{char_block}

STYLE: {style}

IMPORTANT: NO TEXT, NO WORDS, NO LETTERS in the image. Visual storytelling only."""
    else:
        prompt = f"""{scene}

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


def generate_image(prompt: str, slug: str, page_num: int, config, use_reference: bool = False) -> dict | None:
    """Generate an image using nano-banana-pro or wan2.6-image with reference.

    Returns: dict with 'url', 'local_path', and 'metadata' or None on failure
    """

    print(f"  Generating page {page_num}...")

    model = "nano-banana-pro"
    ref_path, ref_version = None, None

    if use_reference:
        ref_path, ref_version = find_reference_image(slug)
        if ref_path:
            print(f"    Using reference: {ref_version}")
            model = "wan2.6-image"
        else:
            print(f"    No reference found, using T2I")

    # Build request body based on model type
    if model == "wan2.6-image" and ref_path:
        # Image-to-image with reference
        ref_uri = image_to_base64_uri(Path(ref_path))
        body = {
            "prompt": prompt,
            "images": [ref_uri],
            "size": "1024*1024",
            "n": 1
        }
        endpoint_path = "/vendors/alibaba/v1/wan2.6-image/generation"
    else:
        # Text-to-image
        body = {
            "prompt": prompt,
            "size": "1024*1024",
            "n": 1
        }
        endpoint_path = "/vendors/google/v1/nano-banana-pro/generation"

    # Generate using MuleRouter API directly
    with APIClient(config) as client:
        result = create_and_poll_task(
            client=client,
            endpoint_path=endpoint_path,
            request_body=body,
            result_key="images",
            interval=5.0,
            max_wait=300.0,
            verbose=True
        )

        if result.results:
            url = result.results[0]
            print(f"    Generated: {url[:60]}...")

            # Save image locally
            image_dir = IMAGES_DIR / slug
            image_dir.mkdir(parents=True, exist_ok=True)
            local_path = image_dir / f"page{page_num:02d}.png"

            try:
                urllib.request.urlretrieve(url, local_path)
                print(f"    Saved: {local_path.name}")

                # Path format for reader: "images/{slug}/page{nn}.png"
                return {
                    "url": url,
                    "image_path": f"images/{slug}/page{page_num:02d}.png",
                    "metadata": {
                        "generated_at": datetime.now().isoformat(),
                        "model": model,
                        "used_reference": bool(ref_path and use_reference),
                        "reference_version": ref_version if (ref_path and use_reference) else None,
                    }
                }
            except Exception as e:
                print(f"    Download error: {e}")
                return None
        else:
            print(f"    Failed: {result.error}")
            return None


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

    # Load MuleRouter config
    config = load_config()
    print(f"Using API: {config.site}\n")

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
        result = generate_image(prompt, args.slug, page_num, config, use_reference=args.use_reference)

        if result:
            page["image"] = result["image_path"]
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
