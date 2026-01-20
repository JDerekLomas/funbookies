#!/usr/bin/env python3
"""Batch experiment: Compare I2I models on a full book.

Generates all pages for a book using multiple models to compare:
- Quality of style transfer
- Character consistency
- Cost per book
- Generation time

Results are saved to experiments/{book_slug}/{timestamp}/ with:
- images/{model_name}/page_XX.png
- results.json with metrics
- comparison.html for visual review

Usage:
    # Compare default models on a book
    python batch_experiment.py flicker-the-firefly

    # Specify models to compare
    python batch_experiment.py flicker-the-firefly --models wan2.6-image,flux-kontext-pro,gemini-3-pro

    # Only generate specific pages
    python batch_experiment.py flicker-the-firefly --pages 1,2,3

    # Dry run to see what would be generated
    python batch_experiment.py flicker-the-firefly --dry-run
"""

import os
import sys
import json
import time
import urllib.request
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Optional

from dotenv import load_dotenv

# Load environment
PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / ".env")
load_dotenv(PROJECT_ROOT / ".env.local")

from fal_client import ImageClient, MODELS, GenerationResult

BOOKS_DIR = PROJECT_ROOT / "public" / "books"
REFS_DIR = BOOKS_DIR / "references"
EXPERIMENTS_DIR = PROJECT_ROOT / "experiments"

# Default models to compare (best I2I options)
DEFAULT_MODELS = [
    "wan2.6-image",       # $0.03 - Current workflow
    "flux-dev-i2i",       # $0.03/MP - Strength control
    "flux-kontext-pro",   # $0.04 - Natural language
    "gemini-2.5-flash",   # $0.039 - Fast
    "z-image-turbo",      # $0.005/MP - Budget
]

# Premium models (more expensive, run separately)
PREMIUM_MODELS = [
    "flux-kontext-max",   # $0.08 - Best quality
    "gemini-3-pro",       # $0.15 - 14 refs
]


@dataclass
class PageResult:
    """Result for a single page generation."""
    page_num: int
    model: str
    success: bool
    url: Optional[str] = None
    local_path: Optional[str] = None
    error: Optional[str] = None
    generation_time: Optional[float] = None
    cost: Optional[float] = None


@dataclass
class ExperimentResult:
    """Complete experiment results."""
    book_slug: str
    timestamp: str
    reference_image: Optional[str]
    models_tested: list[str]
    pages_generated: int
    total_images: int
    total_cost: float
    total_time: float
    results_by_model: dict  # model -> list of PageResult
    errors: list[str]


def find_reference_image(slug: str) -> tuple[Path | None, str | None]:
    """Find reference image for a book."""
    versions = ["_v4", "_v3", "_v2", ""]
    for version in versions:
        suffix = f"_reference{version}.png"
        path = REFS_DIR / f"{slug}{suffix}"
        if path.exists():
            version_str = version.replace("_", "") if version else "v1"
            return path, version_str
    return None, None


def get_character_block(book: dict) -> str:
    """Extract character descriptions for prompts."""
    characters = book.get("characters", {})
    if not characters:
        characters = book.get("character", {})

    char_lines = []
    for key, char_data in characters.items():
        if isinstance(char_data, dict) and key not in ["names", "style_notes"]:
            if char_data.get("visual_shorthand"):
                char_lines.append(char_data["visual_shorthand"])

    return "\n".join(char_lines)


def build_page_prompt(book: dict, page: dict) -> str:
    """Build prompt for a page."""
    scene = page.get("scene", "")
    if not scene:
        return ""

    # Get style
    story_bible = book.get("story_bible", {})
    art_dir = book.get("art_direction", {})
    if story_bible.get("visual_style"):
        style = story_bible["visual_style"]
    elif art_dir.get("style"):
        style = art_dir["style"]
    else:
        style = "children's book illustration, simple shapes, bold outlines"

    # Get characters
    char_block = get_character_block(book)

    if char_block:
        prompt = f"""{scene}

CHARACTERS (draw EXACTLY as described):
{char_block}

STYLE: {style}

NO TEXT, NO WORDS, NO LETTERS in the image."""
    else:
        prompt = f"""{scene}

STYLE: {style}

NO TEXT, NO WORDS, NO LETTERS in the image."""

    return prompt


def download_image(url: str, output_path: Path) -> bool:
    """Download image from URL."""
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(url, output_path)
        return True
    except Exception as e:
        print(f"    Download error: {e}")
        return False


def generate_comparison_html(experiment_dir: Path, result: ExperimentResult) -> Path:
    """Generate HTML comparison page."""
    html_path = experiment_dir / "comparison.html"

    # Build model comparison rows
    model_headers = "".join(f"<th>{m}</th>" for m in result.models_tested)

    rows = []
    for page_num in range(1, result.pages_generated + 1):
        cells = [f"<td><strong>Page {page_num}</strong></td>"]
        for model in result.models_tested:
            model_results = result.results_by_model.get(model, [])
            page_result = next((r for r in model_results if r["page_num"] == page_num), None)
            if page_result and page_result.get("local_path"):
                img_path = Path(page_result["local_path"]).name
                model_dir = model.replace("/", "_")
                cells.append(f'<td><img src="images/{model_dir}/{img_path}" loading="lazy"></td>')
            else:
                error = page_result.get("error", "Failed") if page_result else "Not run"
                cells.append(f'<td class="error">{error}</td>')
        rows.append(f"<tr>{''.join(cells)}</tr>")

    # Cost summary
    cost_rows = []
    for model in result.models_tested:
        model_results = result.results_by_model.get(model, [])
        total = sum(r.get("cost", 0) or 0 for r in model_results)
        success = sum(1 for r in model_results if r.get("success"))
        cost_rows.append(f"<tr><td>{model}</td><td>{success}/{len(model_results)}</td><td>${total:.2f}</td></tr>")

    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Experiment: {result.book_slug} - {result.timestamp}</title>
    <style>
        body {{ font-family: -apple-system, sans-serif; margin: 20px; background: #f5f5f5; }}
        h1 {{ color: #333; }}
        .meta {{ background: #fff; padding: 15px; border-radius: 8px; margin-bottom: 20px; }}
        table {{ border-collapse: collapse; width: 100%; background: #fff; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: center; }}
        th {{ background: #4a90a4; color: white; position: sticky; top: 0; }}
        img {{ max-width: 200px; height: auto; border-radius: 4px; }}
        .error {{ color: #c00; font-size: 0.8em; }}
        .summary {{ margin-top: 30px; }}
        .summary table {{ width: auto; }}
        .summary td, .summary th {{ padding: 10px 20px; }}
    </style>
</head>
<body>
    <h1>Model Comparison: {result.book_slug}</h1>

    <div class="meta">
        <p><strong>Timestamp:</strong> {result.timestamp}</p>
        <p><strong>Reference:</strong> {result.reference_image or 'None'}</p>
        <p><strong>Total Images:</strong> {result.total_images}</p>
        <p><strong>Total Cost:</strong> ${result.total_cost:.2f}</p>
        <p><strong>Total Time:</strong> {result.total_time:.1f}s</p>
    </div>

    <h2>Visual Comparison</h2>
    <table>
        <thead>
            <tr><th>Page</th>{model_headers}</tr>
        </thead>
        <tbody>
            {''.join(rows)}
        </tbody>
    </table>

    <div class="summary">
        <h2>Cost Summary</h2>
        <table>
            <thead><tr><th>Model</th><th>Success</th><th>Cost</th></tr></thead>
            <tbody>{''.join(cost_rows)}</tbody>
        </table>
    </div>
</body>
</html>"""

    with open(html_path, "w") as f:
        f.write(html)

    return html_path


def run_experiment(
    book_slug: str,
    models: list[str],
    page_nums: list[int] | None = None,
    dry_run: bool = False,
) -> ExperimentResult:
    """Run a full book experiment comparing multiple models."""

    # Load book
    book_path = BOOKS_DIR / f"{book_slug}.json"
    if not book_path.exists():
        raise FileNotFoundError(f"Book not found: {book_slug}")

    with open(book_path) as f:
        book = json.load(f)

    # Find reference image
    ref_path, ref_version = find_reference_image(book_slug)
    if not ref_path:
        print(f"Warning: No reference image found for {book_slug}")

    # Filter pages
    pages = book.get("pages", [])
    if page_nums:
        pages = [p for p in pages if p.get("page") in page_nums]
    # Only pages with scenes
    pages = [p for p in pages if p.get("scene")]

    # Setup experiment directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    experiment_dir = EXPERIMENTS_DIR / book_slug / timestamp
    experiment_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"BATCH EXPERIMENT: {book_slug}")
    print(f"{'='*60}")
    print(f"Timestamp: {timestamp}")
    print(f"Reference: {ref_version or 'None'}")
    print(f"Pages: {len(pages)}")
    print(f"Models: {', '.join(models)}")
    print(f"Output: {experiment_dir}")

    # Estimate cost
    total_estimated = 0
    for model in models:
        if model in MODELS:
            cost = MODELS[model].price * len(pages)
            total_estimated += cost
            print(f"  {model}: ~${cost:.2f}")
    print(f"Estimated total: ${total_estimated:.2f}")

    if dry_run:
        print("\n[DRY RUN - No images will be generated]")
        # Show prompts
        for page in pages[:3]:
            prompt = build_page_prompt(book, page)
            print(f"\nPage {page['page']}:")
            print(f"  {prompt[:200]}...")
        return None

    print(f"\n{'='*60}")

    # Initialize client
    client = ImageClient()

    # Run generations
    results_by_model = {}
    total_cost = 0
    total_time = 0
    total_images = 0
    errors = []

    for model in models:
        print(f"\n[{model}]")
        model_dir = experiment_dir / "images" / model.replace("/", "_")
        model_dir.mkdir(parents=True, exist_ok=True)

        model_results = []

        for page in pages:
            page_num = page["page"]
            prompt = build_page_prompt(book, page)

            if not prompt:
                continue

            print(f"  Page {page_num}...", end=" ", flush=True)

            # Generate
            start = time.time()
            if ref_path:
                result = client.generate_with_reference(
                    prompt=prompt,
                    reference_images=[ref_path],
                    model=model,
                    verbose=False,
                )
            else:
                result = client.generate_image(
                    prompt=prompt,
                    model=model,
                    verbose=False,
                )
            gen_time = time.time() - start

            # Download and save
            local_path = None
            if result.success:
                local_path = model_dir / f"page_{page_num:02d}.png"
                if download_image(result.url, local_path):
                    print(f"OK ({gen_time:.1f}s, ${result.cost or 0:.3f})")
                    total_images += 1
                else:
                    result = GenerationResult(error="Download failed", model=model)
                    print(f"DOWNLOAD FAILED")
            else:
                print(f"FAILED: {result.error}")
                errors.append(f"{model} page {page_num}: {result.error}")

            page_result = PageResult(
                page_num=page_num,
                model=model,
                success=result.success,
                url=result.url,
                local_path=str(local_path) if local_path else None,
                error=result.error,
                generation_time=gen_time,
                cost=result.cost,
            )
            model_results.append(asdict(page_result))

            if result.cost:
                total_cost += result.cost
            total_time += gen_time

            # Rate limiting
            time.sleep(1)

        results_by_model[model] = model_results

    # Build result
    experiment_result = ExperimentResult(
        book_slug=book_slug,
        timestamp=timestamp,
        reference_image=str(ref_path) if ref_path else None,
        models_tested=models,
        pages_generated=len(pages),
        total_images=total_images,
        total_cost=total_cost,
        total_time=total_time,
        results_by_model=results_by_model,
        errors=errors,
    )

    # Save results JSON
    results_path = experiment_dir / "results.json"
    with open(results_path, "w") as f:
        json.dump(asdict(experiment_result), f, indent=2)

    # Generate comparison HTML
    html_path = generate_comparison_html(experiment_dir, experiment_result)

    print(f"\n{'='*60}")
    print(f"EXPERIMENT COMPLETE")
    print(f"{'='*60}")
    print(f"Total images: {total_images}")
    print(f"Total cost: ${total_cost:.2f}")
    print(f"Total time: {total_time:.1f}s")
    print(f"Errors: {len(errors)}")
    print(f"\nResults: {results_path}")
    print(f"Comparison: {html_path}")
    print(f"\nOpen in browser:")
    print(f"  open {html_path}")

    return experiment_result


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Compare I2I models on a full book")
    parser.add_argument("book_slug", nargs="?", help="Book slug to process")
    parser.add_argument(
        "--models",
        help=f"Comma-separated models (default: {','.join(DEFAULT_MODELS)})",
        default=",".join(DEFAULT_MODELS),
    )
    parser.add_argument("--pages", help="Comma-separated page numbers (default: all)")
    parser.add_argument("--dry-run", action="store_true", help="Show prompts without generating")
    parser.add_argument("--include-premium", action="store_true", help="Include premium models")
    parser.add_argument("--list-models", action="store_true", help="List available models and exit")

    args = parser.parse_args()

    if args.list_models:
        print("Available I2I Models:")
        print("-" * 70)
        for name, cfg in MODELS.items():
            if cfg.supports_i2i:
                price_str = f"${cfg.price}/{cfg.price_unit}"
                print(f"  {name:25} {price_str:12} refs={cfg.max_refs}  {cfg.description}")
        return

    if not args.book_slug:
        parser.error("book_slug is required (or use --list-models)")

    # Parse models
    models = [m.strip() for m in args.models.split(",")]
    if args.include_premium:
        models.extend(PREMIUM_MODELS)

    # Validate models
    for model in models:
        if model not in MODELS:
            print(f"Unknown model: {model}")
            print(f"Available: {', '.join(MODELS.keys())}")
            return

    # Parse pages
    page_nums = None
    if args.pages:
        page_nums = [int(p.strip()) for p in args.pages.split(",")]

    # Run experiment
    run_experiment(
        book_slug=args.book_slug,
        models=models,
        page_nums=page_nums,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
