#!/usr/bin/env python3
"""Batch panel experiment: Generate 9-panel page images in single generations.

Instead of generating pages individually, generate them as 9-panel grids:
- Image 1: Reference sheet (9 panels: characters, objects, settings)
- Image 2: Pages 1-9 as a single 9-panel image (using Image 1 as ref)
- Image 3: Pages 10-18 as a single 9-panel image (using Image 1 + Image 2 as refs)

Benefits:
- Much cheaper: 1 image per 9 pages instead of 9 images
- Better consistency: Model sees all 9 scenes in context
- Progressive refs: Later batches reference earlier ones

Usage:
    python batch_panel_experiment.py flicker-the-firefly --dry-run
    python batch_panel_experiment.py flicker-the-firefly
"""

import os
import json
import time
import urllib.request
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / ".env")
load_dotenv(PROJECT_ROOT / ".env.local")

from fal_client import ImageClient, MODELS

BOOKS_DIR = PROJECT_ROOT / "public" / "books"
REFS_DIR = BOOKS_DIR / "references"
EXPERIMENTS_DIR = PROJECT_ROOT / "experiments"

PANELS_PER_IMAGE = 9  # 3x3 grid


def get_book_style(book: dict) -> str:
    """Get style description from book."""
    story_bible = book.get("story_bible", {})
    art_dir = book.get("art_direction", {})
    if story_bible.get("visual_style"):
        return story_bible["visual_style"]
    elif art_dir.get("style"):
        return art_dir["style"]
    return "children's book illustration, simple shapes, bold outlines"


def get_character_block(book: dict) -> str:
    """Extract character descriptions."""
    characters = book.get("characters", {})
    if not characters:
        characters = book.get("character", {})

    lines = []
    for key, data in characters.items():
        if isinstance(data, dict) and key not in ["names", "style_notes"]:
            if data.get("visual_shorthand"):
                lines.append(f"- {data['visual_shorthand']}")
    return "\n".join(lines)


def find_reference_image(slug: str) -> Path | None:
    """Find existing reference image."""
    for suffix in ["_v4", "_v3", "_v2", ""]:
        path = REFS_DIR / f"{slug}_reference{suffix}.png"
        if path.exists():
            return path
    return None


def build_9panel_page_prompt(book: dict, pages: list[dict], batch_num: int, total_batches: int) -> str:
    """Build prompt for a 9-panel page image.

    Each panel shows one page's scene, arranged in a 3x3 grid.
    """
    style = get_book_style(book)
    char_block = get_character_block(book)

    # Build panel descriptions
    panel_descs = []
    for i, page in enumerate(pages):
        panel_num = i + 1
        row = (i // 3) + 1
        col = (i % 3) + 1
        scene = page.get("scene", "")
        # Truncate long scenes
        if len(scene) > 150:
            scene = scene[:147] + "..."
        panel_descs.append(f"Panel {panel_num} (row {row}, col {col}): {scene}")

    panels_text = "\n".join(panel_descs)

    # Reference instruction based on batch
    if batch_num == 1:
        ref_instruction = "Use the style and characters from Image 1 (reference sheet)."
    else:
        ref_instruction = f"""Use the style and characters from Image 1 (reference sheet).
Match character appearances EXACTLY to how they appear in Image 2 (previous pages)."""

    prompt = f"""Create a 3x3 grid image with 9 panels. Each panel is a separate scene from a children's book.

{ref_instruction}

PANELS:
{panels_text}

CHARACTERS (draw EXACTLY the same in every panel):
{char_block}

STYLE: {style}

LAYOUT: 3 rows × 3 columns, clear panel borders, each panel is a complete scene.
NO TEXT, NO WORDS, NO NUMBERS in any panel."""

    return prompt


def download_image(url: str, path: Path) -> bool:
    """Download image from URL."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(url, path)
        return True
    except Exception as e:
        print(f"  Download error: {e}")
        return False


def run_experiment(
    book_slug: str,
    model: str = "wan2.6-image",
    dry_run: bool = False,
) -> dict:
    """Generate book pages as 9-panel batch images."""

    book_path = BOOKS_DIR / f"{book_slug}.json"
    if not book_path.exists():
        raise FileNotFoundError(f"Book not found: {book_slug}")

    with open(book_path) as f:
        book = json.load(f)

    # Get pages with scenes
    pages = [p for p in book.get("pages", []) if p.get("scene")]

    # Find reference sheet
    ref_path = find_reference_image(book_slug)
    if not ref_path:
        raise FileNotFoundError(f"No reference image for {book_slug}")

    # Calculate batches
    num_batches = (len(pages) + PANELS_PER_IMAGE - 1) // PANELS_PER_IMAGE

    # Setup output
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    experiment_dir = EXPERIMENTS_DIR / "batch_panels" / book_slug / timestamp

    model_config = MODELS.get(model)
    cost_per_image = model_config.price if model_config else 0.03

    print(f"\n{'='*60}")
    print(f"9-PANEL BATCH GENERATION: {book_slug}")
    print(f"{'='*60}")
    print(f"Model: {model}")
    print(f"Total pages: {len(pages)}")
    print(f"Batches needed: {num_batches} (9 pages each)")
    print(f"Reference: {ref_path.name}")
    print(f"Output: {experiment_dir}")
    print(f"\nCost estimate: {num_batches} × ${cost_per_image:.2f} = ${num_batches * cost_per_image:.2f}")
    print(f"(vs ${len(pages) * cost_per_image:.2f} for individual pages)")

    if dry_run:
        print(f"\n[DRY RUN]")
        for batch_num in range(1, num_batches + 1):
            start_idx = (batch_num - 1) * PANELS_PER_IMAGE
            end_idx = min(start_idx + PANELS_PER_IMAGE, len(pages))
            batch_pages = pages[start_idx:end_idx]

            print(f"\n--- Batch {batch_num}/{num_batches} ---")
            print(f"Pages: {[p['page'] for p in batch_pages]}")

            refs = ["reference_sheet"]
            if batch_num > 1:
                refs.append(f"batch_{batch_num-1}_panels.png")
            print(f"References: {refs}")

            prompt = build_9panel_page_prompt(book, batch_pages, batch_num, num_batches)
            print(f"\nPrompt preview:\n{prompt[:500]}...")
        return {}

    # Initialize
    experiment_dir.mkdir(parents=True, exist_ok=True)
    client = ImageClient()

    results = {
        "book_slug": book_slug,
        "model": model,
        "timestamp": timestamp,
        "total_pages": len(pages),
        "batches": [],
    }

    generated_panels = []  # Paths to generated panel images
    total_cost = 0
    total_time = 0

    for batch_num in range(1, num_batches + 1):
        start_idx = (batch_num - 1) * PANELS_PER_IMAGE
        end_idx = min(start_idx + PANELS_PER_IMAGE, len(pages))
        batch_pages = pages[start_idx:end_idx]

        print(f"\n{'─'*40}")
        print(f"BATCH {batch_num}/{num_batches}: Pages {[p['page'] for p in batch_pages]}")
        print(f"{'─'*40}")

        # Build references list
        refs = [ref_path]
        if generated_panels:
            # Add previous batch as reference (up to model's max)
            max_refs = model_config.max_refs if model_config else 3
            for prev_panel in generated_panels[-(max_refs-1):]:
                refs.append(prev_panel)

        print(f"  Using {len(refs)} reference(s)")

        # Build prompt
        prompt = build_9panel_page_prompt(book, batch_pages, batch_num, num_batches)

        # Generate
        print(f"  Generating 9-panel image...", end=" ", flush=True)
        start = time.time()

        result = client.generate_with_reference(
            prompt=prompt,
            reference_images=refs,
            model=model,
            verbose=False,
        )

        gen_time = time.time() - start

        if result.success:
            output_path = experiment_dir / f"batch_{batch_num:02d}_pages_{batch_pages[0]['page']:02d}-{batch_pages[-1]['page']:02d}.png"
            if download_image(result.url, output_path):
                print(f"OK ({gen_time:.1f}s, ${result.cost or 0:.3f})")
                generated_panels.append(output_path)
                total_cost += result.cost or 0

                results["batches"].append({
                    "batch_num": batch_num,
                    "pages": [p["page"] for p in batch_pages],
                    "refs_used": len(refs),
                    "path": str(output_path),
                    "time": gen_time,
                    "cost": result.cost,
                    "success": True,
                })
            else:
                print("DOWNLOAD FAILED")
                results["batches"].append({
                    "batch_num": batch_num,
                    "pages": [p["page"] for p in batch_pages],
                    "success": False,
                    "error": "Download failed",
                })
        else:
            print(f"FAILED: {result.error}")
            results["batches"].append({
                "batch_num": batch_num,
                "pages": [p["page"] for p in batch_pages],
                "success": False,
                "error": result.error,
            })

        total_time += gen_time
        time.sleep(1)

    # Save results
    results["total_cost"] = total_cost
    results["total_time"] = total_time
    results["images_generated"] = len(generated_panels)

    results_path = experiment_dir / "results.json"
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n{'='*60}")
    print(f"COMPLETE")
    print(f"{'='*60}")
    print(f"Batches: {len(generated_panels)}/{num_batches}")
    print(f"Total cost: ${total_cost:.2f}")
    print(f"Total time: {total_time:.1f}s")
    print(f"\nResults: {results_path}")
    print(f"\nView images:")
    for p in generated_panels:
        print(f"  open {p}")

    return results


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Generate 9-panel batch page images")
    parser.add_argument("book_slug", help="Book to process")
    parser.add_argument("--model", default="wan2.6-image", help="Model (default: wan2.6-image)")
    parser.add_argument("--dry-run", action="store_true", help="Preview without generating")

    args = parser.parse_args()

    run_experiment(
        book_slug=args.book_slug,
        model=args.model,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
