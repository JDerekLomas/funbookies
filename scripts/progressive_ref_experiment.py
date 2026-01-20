#!/usr/bin/env python3
"""Progressive reference experiment: Build consistency through batched page composites.

Strategy:
1. Generate style/character reference sheet (9 panels) - like current
2. Generate pages 1-9 as individual images using ref sheet
3. Composite pages 1-9 into a single 9-panel image
4. Generate pages 10-18 using ref sheet + pages 1-9 composite
5. Composite pages 10-18, use both for pages 19+

This leverages wan2.6's 3-ref or gemini's 14-ref capability for
progressive consistency - later pages can "see" earlier pages.

Usage:
    # Full book with progressive refs (wan2.6, 3 refs)
    python progressive_ref_experiment.py flicker-the-firefly

    # Use gemini-3-pro for more refs
    python progressive_ref_experiment.py flicker-the-firefly --model gemini-3-pro

    # Dry run
    python progressive_ref_experiment.py flicker-the-firefly --dry-run
"""

import os
import sys
import json
import time
import urllib.request
from pathlib import Path
from datetime import datetime
from PIL import Image
from io import BytesIO

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / ".env")
load_dotenv(PROJECT_ROOT / ".env.local")

from fal_client import ImageClient, MODELS

BOOKS_DIR = PROJECT_ROOT / "public" / "books"
REFS_DIR = BOOKS_DIR / "references"
IMAGES_DIR = BOOKS_DIR / "images"
EXPERIMENTS_DIR = PROJECT_ROOT / "experiments"

BATCH_SIZE = 9  # Pages per composite (3x3 grid)


def find_reference_image(slug: str) -> Path | None:
    """Find the reference image for a book."""
    for suffix in ["_v4", "_v3", "_v2", ""]:
        path = REFS_DIR / f"{slug}_reference{suffix}.png"
        if path.exists():
            return path
    return None


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


def create_composite_image(image_paths: list[Path], output_path: Path, grid_size: int = 3) -> bool:
    """Create a 3x3 composite from individual images.

    Args:
        image_paths: List of up to 9 image paths
        output_path: Where to save the composite
        grid_size: Grid dimension (3 for 3x3)

    Returns:
        True if successful
    """
    try:
        # Load images
        images = []
        for path in image_paths[:grid_size * grid_size]:
            if path.exists():
                images.append(Image.open(path))

        if not images:
            print(f"  No images to composite")
            return False

        # Get dimensions from first image
        img_width, img_height = images[0].size

        # Create composite canvas
        composite_width = img_width * grid_size
        composite_height = img_height * grid_size
        composite = Image.new('RGB', (composite_width, composite_height), (255, 255, 255))

        # Paste images into grid
        for idx, img in enumerate(images):
            row = idx // grid_size
            col = idx % grid_size
            x = col * img_width
            y = row * img_height

            # Resize if needed
            if img.size != (img_width, img_height):
                img = img.resize((img_width, img_height), Image.Resampling.LANCZOS)

            composite.paste(img, (x, y))

        # Save
        output_path.parent.mkdir(parents=True, exist_ok=True)
        composite.save(output_path, 'PNG')
        print(f"  Created composite: {output_path.name} ({len(images)} images)")
        return True

    except Exception as e:
        print(f"  Composite error: {e}")
        return False


def download_image(url: str, path: Path) -> bool:
    """Download image from URL."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(url, path)
        return True
    except Exception as e:
        print(f"    Download error: {e}")
        return False


def build_prompt(book: dict, page: dict, batch_num: int, refs_description: str) -> str:
    """Build prompt with reference context."""
    scene = page.get("scene", "")
    style = get_book_style(book)
    char_block = get_character_block(book)

    prompt = f"""Generate using the style from Image 1 (reference sheet).
{refs_description}

SCENE: {scene}

CHARACTERS (draw EXACTLY as shown in references):
{char_block}

STYLE: {style}

CRITICAL: Match character appearance exactly to reference images.
NO TEXT, NO WORDS, NO LETTERS in the image."""

    return prompt


def run_progressive_generation(
    book_slug: str,
    model: str = "wan2.6-image",
    dry_run: bool = False,
    max_pages: int = None,
) -> dict:
    """Generate book pages with progressive reference building."""

    book_path = BOOKS_DIR / f"{book_slug}.json"
    if not book_path.exists():
        raise FileNotFoundError(f"Book not found: {book_slug}")

    with open(book_path) as f:
        book = json.load(f)

    # Get pages with scenes
    pages = [p for p in book.get("pages", []) if p.get("scene")]
    if max_pages:
        pages = pages[:max_pages]

    # Find style reference
    style_ref = find_reference_image(book_slug)
    if not style_ref:
        raise FileNotFoundError(f"No reference image found for {book_slug}")

    # Setup output
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    experiment_dir = EXPERIMENTS_DIR / "progressive" / book_slug / timestamp
    images_dir = experiment_dir / "images"
    composites_dir = experiment_dir / "composites"

    model_config = MODELS.get(model)
    max_refs = model_config.max_refs if model_config else 3

    print(f"\n{'='*60}")
    print(f"PROGRESSIVE REFERENCE GENERATION: {book_slug}")
    print(f"{'='*60}")
    print(f"Model: {model} (max {max_refs} refs)")
    print(f"Pages: {len(pages)}")
    print(f"Batch size: {BATCH_SIZE}")
    print(f"Style ref: {style_ref.name}")
    print(f"Output: {experiment_dir}")

    # Calculate batches
    num_batches = (len(pages) + BATCH_SIZE - 1) // BATCH_SIZE
    print(f"Batches: {num_batches}")

    # Estimate cost
    cost_per_image = model_config.price if model_config else 0.03
    estimated_cost = len(pages) * cost_per_image
    print(f"Estimated cost: ${estimated_cost:.2f}")

    if dry_run:
        print(f"\n[DRY RUN]")
        for batch_num in range(num_batches):
            start_idx = batch_num * BATCH_SIZE
            end_idx = min(start_idx + BATCH_SIZE, len(pages))
            batch_pages = pages[start_idx:end_idx]

            print(f"\nBatch {batch_num + 1}:")
            print(f"  Pages: {[p['page'] for p in batch_pages]}")

            refs = ["style_ref"]
            if batch_num >= 1:
                refs.append("composite_batch_1")
            if batch_num >= 2 and max_refs >= 3:
                refs.append("composite_batch_2")
            print(f"  References: {refs}")

            if batch_pages:
                prompt = build_prompt(book, batch_pages[0], batch_num,
                                     f"Using {len(refs)} reference images")
                print(f"  Sample prompt:\n    {prompt[:200]}...")
        return {}

    # Initialize
    client = ImageClient()
    images_dir.mkdir(parents=True, exist_ok=True)
    composites_dir.mkdir(parents=True, exist_ok=True)

    results = {
        "book_slug": book_slug,
        "model": model,
        "timestamp": timestamp,
        "batches": [],
    }

    composite_refs = []  # Build up as we go
    total_cost = 0
    total_time = 0

    for batch_num in range(num_batches):
        start_idx = batch_num * BATCH_SIZE
        end_idx = min(start_idx + BATCH_SIZE, len(pages))
        batch_pages = pages[start_idx:end_idx]

        print(f"\n{'─'*40}")
        print(f"BATCH {batch_num + 1}/{num_batches}: Pages {batch_pages[0]['page']}-{batch_pages[-1]['page']}")
        print(f"{'─'*40}")

        # Build reference list for this batch
        refs = [style_ref]
        refs_desc = "Image 1: Style/character reference sheet."

        for i, comp_ref in enumerate(composite_refs[:max_refs - 1]):
            refs.append(comp_ref)
            batch_start = i * BATCH_SIZE + 1
            batch_end = min((i + 1) * BATCH_SIZE, len(pages))
            refs_desc += f"\nImage {i + 2}: Pages {batch_start}-{batch_end} for character consistency."

        print(f"  Using {len(refs)} reference(s)")

        batch_results = []
        batch_image_paths = []

        for page in batch_pages:
            page_num = page["page"]
            prompt = build_prompt(book, page, batch_num, refs_desc)

            print(f"  Page {page_num}...", end=" ", flush=True)

            start = time.time()
            result = client.generate_with_reference(
                prompt=prompt,
                reference_images=refs,
                model=model,
                verbose=False,
            )
            gen_time = time.time() - start

            if result.success:
                local_path = images_dir / f"page_{page_num:02d}.png"
                if download_image(result.url, local_path):
                    print(f"OK ({gen_time:.1f}s, ${result.cost or 0:.3f})")
                    batch_image_paths.append(local_path)
                    batch_results.append({
                        "page": page_num,
                        "success": True,
                        "path": str(local_path),
                        "time": gen_time,
                        "cost": result.cost,
                    })
                    total_cost += result.cost or 0
                else:
                    print(f"DOWNLOAD FAILED")
                    batch_results.append({"page": page_num, "success": False, "error": "Download failed"})
            else:
                print(f"FAILED: {result.error}")
                batch_results.append({"page": page_num, "success": False, "error": result.error})

            total_time += gen_time
            time.sleep(1)

        # Create composite of this batch for future reference
        if batch_image_paths:
            composite_path = composites_dir / f"batch_{batch_num + 1:02d}_pages_{batch_pages[0]['page']:02d}-{batch_pages[-1]['page']:02d}.png"
            if create_composite_image(batch_image_paths, composite_path):
                composite_refs.append(composite_path)

        results["batches"].append({
            "batch_num": batch_num + 1,
            "pages": [p["page"] for p in batch_pages],
            "refs_used": len(refs),
            "results": batch_results,
            "composite": str(composite_path) if batch_image_paths else None,
        })

    # Save results
    results["total_cost"] = total_cost
    results["total_time"] = total_time
    results["total_images"] = sum(1 for b in results["batches"] for r in b["results"] if r.get("success"))

    results_path = experiment_dir / "results.json"
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)

    # Generate HTML
    html_path = generate_html(experiment_dir, results)

    print(f"\n{'='*60}")
    print(f"COMPLETE")
    print(f"{'='*60}")
    print(f"Total images: {results['total_images']}")
    print(f"Total cost: ${total_cost:.2f}")
    print(f"Total time: {total_time:.1f}s")
    print(f"\nResults: {results_path}")
    print(f"View: open {html_path}")

    return results


def generate_html(experiment_dir: Path, results: dict) -> Path:
    """Generate HTML viewer for results."""

    pages_html = ""
    for batch in results["batches"]:
        pages_html += f"<h3>Batch {batch['batch_num']} (using {batch['refs_used']} refs)</h3>"
        pages_html += "<div class='grid'>"
        for r in batch["results"]:
            if r.get("success"):
                img_name = Path(r["path"]).name
                pages_html += f'<div class="page"><img src="images/{img_name}"><p>Page {r["page"]}</p></div>'
            else:
                pages_html += f'<div class="page error"><p>Page {r["page"]}: {r.get("error", "Failed")}</p></div>'
        pages_html += "</div>"

        if batch.get("composite"):
            comp_name = Path(batch["composite"]).name
            pages_html += f'<div class="composite"><p>Composite (used as ref for next batch):</p><img src="composites/{comp_name}"></div>'

    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Progressive Ref: {results['book_slug']}</title>
    <style>
        body {{ font-family: -apple-system, sans-serif; margin: 20px; background: #f5f5f5; }}
        h1 {{ color: #333; }}
        .meta {{ background: #fff; padding: 15px; border-radius: 8px; margin-bottom: 20px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }}
        .page {{ background: #fff; padding: 10px; border-radius: 8px; text-align: center; }}
        .page img {{ max-width: 100%; border-radius: 4px; }}
        .page.error {{ background: #fee; color: #c00; }}
        .composite {{ background: #e8f4f8; padding: 15px; border-radius: 8px; margin: 20px 0; }}
        .composite img {{ max-width: 600px; border-radius: 4px; }}
    </style>
</head>
<body>
    <h1>Progressive Reference: {results['book_slug']}</h1>

    <div class="meta">
        <p><strong>Model:</strong> {results['model']}</p>
        <p><strong>Total Images:</strong> {results['total_images']}</p>
        <p><strong>Total Cost:</strong> ${results['total_cost']:.2f}</p>
        <p><strong>Total Time:</strong> {results['total_time']:.1f}s</p>
    </div>

    <h2>Generated Pages</h2>
    {pages_html}
</body>
</html>"""

    html_path = experiment_dir / "view.html"
    with open(html_path, "w") as f:
        f.write(html)

    return html_path


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Progressive reference generation")
    parser.add_argument("book_slug", help="Book to process")
    parser.add_argument("--model", default="wan2.6-image",
                        help="Model to use (default: wan2.6-image)")
    parser.add_argument("--max-pages", type=int, help="Limit pages to generate")
    parser.add_argument("--dry-run", action="store_true", help="Preview without generating")

    args = parser.parse_args()

    run_progressive_generation(
        book_slug=args.book_slug,
        model=args.model,
        max_pages=args.max_pages,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
