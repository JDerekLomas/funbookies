#!/usr/bin/env python3
"""Generate page images for a book.

Supports two providers:
- fal.ai (default): $0.03/image for wan2.6 I2I, $0.15 for nano-banana-pro
- mulerouter: ~$0.10-0.15/image for wan2.6, $0.15 for nano-banana-pro

Uses reference images for style consistency when available.

Saves generation metadata for each image including:
- generated_at: ISO timestamp
- model: model used for generation
- provider: fal or mulerouter
- used_reference: whether style transfer was used
- reference_version: which reference image version was used (if applicable)
"""

import sys
import os
import json
import time
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
from fal_client import FalClient

# Import shared utilities
from image_utils import (
    BOOKS_DIR, REFS_DIR, IMAGES_DIR,
    image_to_base64_uri, find_reference_image, find_best_references, get_character_block
)
from image_log import log_image_generation


def validate_scene(scene: str, page_num: int) -> list:
    """Check scene description for common problems. Returns list of warnings."""
    warnings = []

    if not scene:
        warnings.append(f"Page {page_num}: No scene description")
        return warnings

    if scene.startswith("Illustration for:"):
        warnings.append(f"Page {page_num}: PLACEHOLDER scene - run generate_scene_descriptions.py first")

    if len(scene) < 80:
        warnings.append(f"Page {page_num}: Scene too short ({len(scene)} chars)")

    # Check for negations (these cause the model to generate the unwanted thing)
    negation_words = ["no ", "not ", "without ", "don't ", "doesn't ", "isn't ", "never "]
    scene_lower = scene.lower()
    for neg in negation_words:
        if neg in scene_lower and "no text" not in scene_lower[scene_lower.find(neg):scene_lower.find(neg)+20]:
            warnings.append(f"Page {page_num}: Contains '{neg.strip()}' - models generate what you mention even when negated")

    return warnings


def build_image_prompt(book: dict, page: dict, for_fal: bool = True) -> str:
    """Build a complete image prompt with anti-grid composition instructions.

    CRITICAL: This function adds the necessary instructions to prevent
    the model from generating 9-panel grids (which it will do if it
    sees the 9-panel reference without explicit single-image instructions).
    """

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

    # CRITICAL: Add single-scene prefix to prevent grid output
    # The reference image is a 9-panel grid, and without this instruction
    # the model will generate grids instead of single scenes.
    single_scene_prefix = "Single scene illustration: "

    # Add fal.ai style reference instruction if using reference
    style_ref = "Generate an image using the style of image 1.\n\n" if for_fal else ""

    # CRITICAL: Composition instruction to prevent grid layout
    composition = """
COMPOSITION: One cohesive illustration filling the entire canvas.
Full-bleed image with the scene filling edge to edge."""

    # Build prompt with all required elements
    if char_block:
        prompt = f"""{style_ref}{single_scene_prefix}{scene}

CHARACTERS (draw EXACTLY as described - these features are KEY for identification):
{char_block}
{composition}

STYLE: {style}

CRITICAL: NO TEXT, NO WORDS, NO LETTERS anywhere in the image. Pure illustration only."""
    else:
        prompt = f"""{style_ref}{single_scene_prefix}{scene}
{composition}

STYLE: {style}

CRITICAL: NO TEXT, NO WORDS, NO LETTERS anywhere in the image. Pure illustration only."""

    return prompt


def generate_image_fal(
    prompt: str,
    slug: str,
    page_num: int,
    fal_client: FalClient,
    use_reference: bool = True
) -> dict | None:
    """Generate an image using fal.ai.

    Automatically uses multi-ref strategy (3 refs) if available,
    falls back to single ref, then to T2I if no references found.

    Returns: dict with 'url', 'local_path', and 'metadata' or None on failure
    """
    print(f"  Generating page {page_num} via fal.ai...")

    model = "nano-banana-pro"
    ref_paths = []
    ref_strategy = "none"
    cost = "$0.15"

    if use_reference:
        ref_paths, ref_strategy = find_best_references(slug)
        if ref_paths:
            num_refs = len(ref_paths)
            print(f"    Using {num_refs} reference(s): {ref_strategy}")
            model = "wan2.6-image"
            cost = "$0.03"
        else:
            print(f"    No references found, using T2I")

    # Generate based on model type
    if model == "wan2.6-image" and ref_paths:
        result = fal_client.generate_with_reference(
            prompt=prompt,
            reference_images=ref_paths,  # Now supports 1-3 references
            model=model,
            size="1024x1024",
            verbose=True,
        )
    else:
        # Remove fal.ai style reference prefix for T2I
        clean_prompt = prompt.replace("Generate an image using the style of image 1.\n\n", "")
        result = fal_client.generate_image(
            prompt=clean_prompt,
            model=model,
            size="square_hd",
            verbose=True,
        )

    if result.success:
        print(f"    Generated: {result.url[:60]}...")

        # Save image locally
        image_dir = IMAGES_DIR / slug
        image_dir.mkdir(parents=True, exist_ok=True)
        local_path = image_dir / f"page{page_num:02d}.png"

        try:
            urllib.request.urlretrieve(result.url, local_path)
            print(f"    Saved: {local_path.name}")

            # Log successful generation
            log_image_generation(
                model=model,
                prompt=prompt,
                parameters={"size": "1024x1024", "reference_strategy": ref_strategy, "num_refs": len(ref_paths)},
                source="generate_page_images.py",
                book_slug=slug,
                page=page_num,
                cost=0.03 if model == "wan2.6-image" else 0.15,
                status="completed",
                result_url=result.url,
                reference_images=[str(p) for p in ref_paths] if ref_paths else [],
            )

            # Path format for reader: "images/{slug}/page{nn}.png"
            return {
                "url": result.url,
                "image_path": f"images/{slug}/page{page_num:02d}.png",
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "model": model,
                    "provider": "fal.ai",
                    "used_reference": bool(ref_paths and use_reference),
                    "reference_strategy": ref_strategy if (ref_paths and use_reference) else None,
                    "num_references": len(ref_paths) if ref_paths else 0,
                    "cost": cost,
                }
            }
        except Exception as e:
            print(f"    Download error: {e}")
            log_image_generation(
                model=model,
                prompt=prompt,
                parameters={"size": "1024x1024"},
                source="generate_page_images.py",
                book_slug=slug,
                page=page_num,
                status="failed",
                error=f"Download error: {e}",
                reference_images=[str(p) for p in ref_paths] if ref_paths else [],
            )
            return None
    else:
        print(f"    Failed: {result.error}")
        log_image_generation(
            model=model,
            prompt=prompt,
            parameters={"size": "1024x1024"},
            source="generate_page_images.py",
            book_slug=slug,
            page=page_num,
            status="failed",
            error=result.error,
            reference_images=[str(p) for p in ref_paths] if ref_paths else [],
        )
        return None


def generate_image_mulerouter(
    prompt: str,
    slug: str,
    page_num: int,
    config,
    use_reference: bool = True
) -> dict | None:
    """Generate an image using MuleRouter API (fallback).

    Returns: dict with 'url', 'local_path', and 'metadata' or None on failure
    """
    sys.path.insert(0, str(SKILL_DIR))
    load_dotenv(SKILL_DIR / ".env")
    from core import APIClient, create_and_poll_task

    print(f"  Generating page {page_num} via MuleRouter...")

    model = "nano-banana-pro"
    ref_path, ref_version = None, None

    if use_reference:
        ref_path, ref_version = find_reference_image(slug)
        if ref_path:
            print(f"    Using reference: {ref_version}")
            model = "wan2.6-image"
        else:
            print(f"    No reference found, using T2I")

    # Clean prompt (remove fal.ai-specific prefix)
    clean_prompt = prompt.replace("Generate an image using the style of image 1.\n\n", "")

    # Build request body based on model type
    if model == "wan2.6-image" and ref_path:
        # Image-to-image with reference
        ref_uri = image_to_base64_uri(Path(ref_path))
        body = {
            "prompt": clean_prompt,
            "images": [ref_uri],
            "size": "1024*1024",
            "n": 1
        }
        endpoint_path = "/vendors/alibaba/v1/wan2.6-image/generation"
    else:
        # Text-to-image
        body = {
            "prompt": clean_prompt,
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

                # Log successful generation
                log_image_generation(
                    model=model,
                    prompt=prompt,
                    parameters={"size": "1024x1024", "reference_version": ref_version},
                    source="generate_page_images.py",
                    book_slug=slug,
                    page=page_num,
                    cost=0.03 if model == "wan2.6-image" else 0.15,
                    status="completed",
                    result_url=url,
                    reference_images=[str(ref_path)] if ref_path else [],
                )

                # Path format for reader: "images/{slug}/page{nn}.png"
                return {
                    "url": url,
                    "image_path": f"images/{slug}/page{page_num:02d}.png",
                    "metadata": {
                        "generated_at": datetime.now().isoformat(),
                        "model": model,
                        "provider": "mulerouter",
                        "used_reference": bool(ref_path and use_reference),
                        "reference_version": ref_version if (ref_path and use_reference) else None,
                    }
                }
            except Exception as e:
                print(f"    Download error: {e}")
                log_image_generation(
                    model=model,
                    prompt=prompt,
                    parameters={"size": "1024x1024"},
                    source="generate_page_images.py",
                    book_slug=slug,
                    page=page_num,
                    status="failed",
                    error=f"Download error: {e}",
                    reference_images=[str(ref_path)] if ref_path else [],
                )
                return None
        else:
            print(f"    Failed: {result.error}")
            log_image_generation(
                model=model,
                prompt=prompt,
                parameters={"size": "1024x1024"},
                source="generate_page_images.py",
                book_slug=slug,
                page=page_num,
                status="failed",
                error=result.error,
                reference_images=[str(ref_path)] if ref_path else [],
            )
            return None


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("slug", help="Book slug to process")
    parser.add_argument("--pages", help="Comma-separated page numbers (default: all)")
    parser.add_argument("--dry-run", action="store_true", help="Show prompts only")
    parser.add_argument("--force", action="store_true", help="Regenerate even if image exists")
    parser.add_argument("--use-reference", action="store_true", default=True,
                        help="Use I2I with reference sheet (default: True)")
    parser.add_argument("--no-reference", action="store_true",
                        help="Use T2I without reference (nano-banana-pro)")
    parser.add_argument("--provider", choices=["fal", "mulerouter"], default="fal",
                        help="API provider (default: fal - cheaper for I2I)")
    args = parser.parse_args()

    book_file = BOOKS_DIR / f"{args.slug}.json"
    if not book_file.exists():
        print(f"Book not found: {args.slug}")
        return

    with open(book_file) as f:
        book = json.load(f)

    pages = book.get("pages", [])

    # Validate scenes before generating images
    print(f"\n{'='*50}")
    print("PRE-FLIGHT VALIDATION")
    print(f"{'='*50}")

    all_warnings = []
    # Process both story and end pages
    story_pages = [p for p in pages if p.get("type") == "story"]
    end_pages = [p for p in pages if p.get("type") == "end"]
    imageable_pages = story_pages + end_pages

    for page in imageable_pages:
        scene = page.get("scene", "")
        pnum = page.get("page", "?")
        warnings = validate_scene(scene, pnum)
        all_warnings.extend(warnings)

    if all_warnings:
        print(f"\n⚠️  WARNINGS ({len(all_warnings)}):")
        for w in all_warnings:
            print(f"   • {w}")

        # Check for critical errors (placeholder scenes)
        placeholder_count = sum(1 for w in all_warnings if "PLACEHOLDER" in w)
        if placeholder_count > 0:
            print(f"\n❌ {placeholder_count} pages have placeholder scenes!")
            print("   Run: python scripts/generate_scene_descriptions.py", args.slug)
            print("   Then re-run this script.")
            if not args.force:
                print("\n   Use --force to generate anyway (not recommended)")
                return
            else:
                print("\n   --force specified, proceeding anyway...")
    else:
        print("✅ All scenes validated")

    print(f"{'='*50}\n")

    # Filter pages if specified
    if args.pages:
        page_nums = [int(p) for p in args.pages.split(",")]
        pages = [p for p in pages if p["page"] in page_nums]

    print(f"Processing {len(pages)} pages for {args.slug}")
    print(f"Provider: {args.provider}")

    use_reference = args.use_reference and not args.no_reference

    # Estimate costs - check for best available references
    ref_paths, ref_strategy = find_best_references(args.slug)
    if use_reference and ref_paths:
        cost_per_image = 0.03 if args.provider == "fal" else 0.12
        print(f"Mode: Image-to-image ({ref_strategy}, {len(ref_paths)} ref(s))")
    else:
        cost_per_image = 0.15
        print(f"Mode: Text-to-image (nano-banana-pro)")

    pages_to_generate = [p for p in pages if p.get("scene") and (args.force or not p.get("image"))]
    print(f"Pages to generate: {len(pages_to_generate)}")
    print(f"Estimated cost: ${len(pages_to_generate) * cost_per_image:.2f}\n")

    # Initialize client
    if args.provider == "fal":
        try:
            client = FalClient()
            print(f"API key: {client.fal_key[:8]}...")
        except ValueError as e:
            print(f"Error: {e}")
            return
    else:
        sys.path.insert(0, str(SKILL_DIR))
        load_dotenv(SKILL_DIR / ".env")
        from core import load_config
        client = load_config()
        print(f"API: {client.site}")

    # Show character block for reference
    char_block = get_character_block(book)
    if char_block:
        print(f"\nCharacter consistency block:\n{char_block}")
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
        prompt = build_image_prompt(book, page, for_fal=(args.provider == "fal" and use_reference))
        page["image_prompt"] = prompt

        if args.dry_run:
            print(f"\n=== Page {page_num} ===")
            print(prompt)
            print()
            continue

        # Generate image with metadata
        if args.provider == "fal":
            result = generate_image_fal(prompt, args.slug, page_num, client, use_reference=use_reference)
        else:
            result = generate_image_mulerouter(prompt, args.slug, page_num, client, use_reference=use_reference)

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
        if args.provider == "fal":
            actual_cost = updated * (0.03 if use_reference and ref_paths else 0.15)
            print(f"Total cost: ~${actual_cost:.2f}")


if __name__ == "__main__":
    main()
