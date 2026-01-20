#!/usr/bin/env python3
"""Multi-reference experiment: Compare single 9-panel vs multiple dedicated refs.

Tests whether splitting references improves character consistency:

Strategy A (Current): Single 9-panel composite
Strategy B (Split): 3 separate refs (character, environment, style)
Strategy C (Dedicated): Individual refs per element (for gemini-3-pro)

Usage:
    # Run experiment on a book
    python multi_ref_experiment.py flicker-the-firefly

    # Dry run to see what would be generated
    python multi_ref_experiment.py flicker-the-firefly --dry-run

    # Generate new reference images for a book
    python multi_ref_experiment.py flicker-the-firefly --generate-refs
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

PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / ".env")
load_dotenv(PROJECT_ROOT / ".env.local")

from fal_client import ImageClient, MODELS, GenerationResult

BOOKS_DIR = PROJECT_ROOT / "public" / "books"
REFS_DIR = BOOKS_DIR / "references"
EXPERIMENTS_DIR = PROJECT_ROOT / "experiments"


@dataclass
class RefStrategy:
    """Reference image strategy configuration."""
    name: str
    description: str
    model: str
    ref_types: list[str]  # Types of refs to use


# Define strategies to test
STRATEGIES = {
    "single-9panel": RefStrategy(
        name="single-9panel",
        description="Current: Single 9-panel composite",
        model="wan2.6-image",
        ref_types=["composite"],
    ),
    "split-3ref": RefStrategy(
        name="split-3ref",
        description="Split: Character + Environment + Style (wan2.6)",
        model="wan2.6-image",
        ref_types=["character", "environment", "style"],
    ),
    "dedicated-gemini": RefStrategy(
        name="dedicated-gemini",
        description="Dedicated: Multiple individual refs (gemini-3-pro)",
        model="gemini-3-pro",
        ref_types=["character_front", "character_side", "character_expression",
                   "environment_1", "environment_2", "style_palette"],
    ),
}


def get_book_characters(book: dict) -> dict:
    """Extract character info from book."""
    characters = book.get("characters", {})
    if not characters:
        characters = book.get("character", {})
    return {k: v for k, v in characters.items()
            if isinstance(v, dict) and k not in ["names", "style_notes"]}


def get_book_style(book: dict) -> str:
    """Get style description from book."""
    story_bible = book.get("story_bible", {})
    art_dir = book.get("art_direction", {})

    if story_bible.get("visual_style"):
        return story_bible["visual_style"]
    elif art_dir.get("style"):
        return art_dir["style"]
    return "children's book illustration, simple shapes, bold outlines"


def generate_character_ref(client: ImageClient, book: dict, char_name: str, char_data: dict,
                           view: str = "front", output_path: Path = None) -> Optional[str]:
    """Generate a dedicated character reference image."""
    style = get_book_style(book)

    # Build character description
    if char_data.get("visual_shorthand"):
        char_desc = char_data["visual_shorthand"]
    else:
        parts = []
        if char_data.get("species"):
            parts.append(char_data["species"])
        if char_data.get("appearance", {}).get("body"):
            parts.append(char_data["appearance"]["body"])
        char_desc = " ".join(parts) if parts else char_name

    view_prompts = {
        "front": f"Character reference sheet: {char_name}, {char_desc}. Front view, standing pose, full body visible. White/neutral background. {style}",
        "side": f"Character reference sheet: {char_name}, {char_desc}. Side profile view, full body visible. White/neutral background. {style}",
        "expression": f"Character expression sheet: {char_name}, {char_desc}. 4 head shots showing: happy, sad, surprised, determined. White background. {style}",
        "poses": f"Character pose sheet: {char_name}, {char_desc}. 4 different action poses. White background. {style}",
    }

    prompt = view_prompts.get(view, view_prompts["front"])
    prompt += "\n\nNO TEXT, NO WORDS, NO LABELS."

    print(f"  Generating {char_name} ({view})...")
    result = client.generate_image(prompt, model="nano-banana-pro", verbose=True)

    if result.success and output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(result.url, output_path)
        print(f"    Saved: {output_path.name}")
        return str(output_path)

    return result.url if result.success else None


def generate_environment_ref(client: ImageClient, book: dict, env_type: str,
                             output_path: Path = None) -> Optional[str]:
    """Generate environment/setting reference."""
    style = get_book_style(book)
    title = book.get("title", "")

    # Get setting hints from book
    story_bible = book.get("story_bible", {})
    settings = story_bible.get("settings", [])
    setting_desc = ", ".join(settings[:3]) if settings else "natural outdoor setting"

    prompts = {
        "day": f"Environment reference for '{title}': {setting_desc}. Daytime, warm lighting. Wide establishing shot, no characters. {style}",
        "night": f"Environment reference for '{title}': {setting_desc}. Nighttime, moonlit. Wide establishing shot, no characters. {style}",
        "interior": f"Interior environment reference for '{title}': cozy indoor setting matching the story. Wide shot, no characters. {style}",
    }

    prompt = prompts.get(env_type, prompts["day"])
    prompt += "\n\nNO TEXT, NO WORDS, NO LABELS."

    print(f"  Generating environment ({env_type})...")
    result = client.generate_image(prompt, model="nano-banana-pro", verbose=True)

    if result.success and output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(result.url, output_path)
        print(f"    Saved: {output_path.name}")
        return str(output_path)

    return result.url if result.success else None


def generate_style_ref(client: ImageClient, book: dict, output_path: Path = None) -> Optional[str]:
    """Generate a pure style/palette reference."""
    style = get_book_style(book)

    prompt = f"""Style reference sheet with 9 squares showing:
- Color palette swatches (primary colors used in the book)
- Brush stroke samples
- Texture examples
- Lighting mood samples

Style: {style}

Abstract art elements only. NO characters, NO objects, NO scenes.
NO TEXT, NO WORDS, NO LABELS."""

    print(f"  Generating style palette...")
    result = client.generate_image(prompt, model="nano-banana-pro", verbose=True)

    if result.success and output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(result.url, output_path)
        print(f"    Saved: {output_path.name}")
        return str(output_path)

    return result.url if result.success else None


def generate_all_refs(book_slug: str, dry_run: bool = False) -> dict:
    """Generate all reference images for multi-ref strategies."""
    book_path = BOOKS_DIR / f"{book_slug}.json"
    if not book_path.exists():
        raise FileNotFoundError(f"Book not found: {book_slug}")

    with open(book_path) as f:
        book = json.load(f)

    refs_output_dir = REFS_DIR / f"{book_slug}_multi"
    refs_output_dir.mkdir(parents=True, exist_ok=True)

    characters = get_book_characters(book)

    print(f"\n{'='*60}")
    print(f"GENERATING MULTI-REF SET: {book_slug}")
    print(f"{'='*60}")
    print(f"Characters: {list(characters.keys())}")
    print(f"Output: {refs_output_dir}")

    if dry_run:
        print("\n[DRY RUN - showing what would be generated]")
        print("\nCharacter refs:")
        for name in characters:
            print(f"  - {name}_front.png")
            print(f"  - {name}_side.png")
            print(f"  - {name}_expressions.png")
        print("\nEnvironment refs:")
        print("  - environment_day.png")
        print("  - environment_night.png")
        print("\nStyle refs:")
        print("  - style_palette.png")
        return {}

    client = ImageClient()
    generated = {}

    # Generate character refs
    for char_name, char_data in characters.items():
        safe_name = char_name.lower().replace(" ", "_")

        for view in ["front", "side", "expression"]:
            output_path = refs_output_dir / f"char_{safe_name}_{view}.png"
            url = generate_character_ref(client, book, char_name, char_data, view, output_path)
            if url:
                generated[f"char_{safe_name}_{view}"] = str(output_path)
            time.sleep(2)

    # Generate environment refs
    for env_type in ["day", "night"]:
        output_path = refs_output_dir / f"env_{env_type}.png"
        url = generate_environment_ref(client, book, env_type, output_path)
        if url:
            generated[f"env_{env_type}"] = str(output_path)
        time.sleep(2)

    # Generate style ref
    output_path = refs_output_dir / "style_palette.png"
    url = generate_style_ref(client, book, output_path)
    if url:
        generated["style_palette"] = str(output_path)

    # Save manifest
    manifest = {
        "book_slug": book_slug,
        "generated_at": datetime.now().isoformat(),
        "references": generated,
    }
    manifest_path = refs_output_dir / "manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"\n{'='*60}")
    print(f"Generated {len(generated)} reference images")
    print(f"Manifest: {manifest_path}")
    print(f"{'='*60}")

    return generated


def load_refs_for_strategy(book_slug: str, strategy: RefStrategy) -> list[Path]:
    """Load reference images for a strategy."""
    refs = []

    if strategy.name == "single-9panel":
        # Use existing composite reference
        for suffix in ["_v4", "_v3", "_v2", ""]:
            path = REFS_DIR / f"{book_slug}_reference{suffix}.png"
            if path.exists():
                refs.append(path)
                break
    else:
        # Use multi-ref set
        multi_dir = REFS_DIR / f"{book_slug}_multi"
        if not multi_dir.exists():
            print(f"Warning: Multi-ref directory not found: {multi_dir}")
            print(f"Run with --generate-refs first")
            return refs

        # Load based on ref_types
        for ref_type in strategy.ref_types:
            if ref_type == "character":
                # Get first character front view
                for f in multi_dir.glob("char_*_front.png"):
                    refs.append(f)
                    break
            elif ref_type == "character_front":
                for f in multi_dir.glob("char_*_front.png"):
                    refs.append(f)
            elif ref_type == "character_side":
                for f in multi_dir.glob("char_*_side.png"):
                    refs.append(f)
            elif ref_type == "character_expression":
                for f in multi_dir.glob("char_*_expression.png"):
                    refs.append(f)
            elif ref_type == "environment":
                path = multi_dir / "env_day.png"
                if path.exists():
                    refs.append(path)
            elif ref_type.startswith("environment_"):
                env_type = ref_type.split("_")[1]
                path = multi_dir / f"env_{env_type}.png"
                if path.exists():
                    refs.append(path)
            elif ref_type in ["style", "style_palette"]:
                path = multi_dir / "style_palette.png"
                if path.exists():
                    refs.append(path)

    return refs


def build_prompt_for_strategy(book: dict, page: dict, strategy: RefStrategy, ref_count: int) -> str:
    """Build prompt appropriate for the strategy."""
    scene = page.get("scene", "")
    style = get_book_style(book)

    # Get character block
    characters = get_book_characters(book)
    char_lines = []
    for name, data in characters.items():
        if data.get("visual_shorthand"):
            char_lines.append(f"- {name}: {data['visual_shorthand']}")
    char_block = "\n".join(char_lines)

    if strategy.name == "single-9panel":
        # Current approach
        prompt = f"""Generate using style of image 1.

{scene}

CHARACTERS (draw EXACTLY as described):
{char_block}

STYLE: {style}

NO TEXT, NO WORDS, NO LETTERS."""

    elif strategy.name == "split-3ref":
        # Reference specific images
        prompt = f"""{scene}

CHARACTERS (draw EXACTLY as shown in Image 1):
{char_block}

ENVIRONMENT: Match the setting style from Image 2.
COLOR PALETTE: Use colors from Image 3.

STYLE: {style}

NO TEXT, NO WORDS, NO LETTERS."""

    else:  # dedicated-gemini
        # More detailed reference assignments
        ref_assignments = []
        for i in range(1, min(ref_count + 1, 7)):
            if i <= 3:
                ref_assignments.append(f"Image {i}: Character reference")
            elif i <= 5:
                ref_assignments.append(f"Image {i}: Environment reference")
            else:
                ref_assignments.append(f"Image {i}: Style/palette reference")

        prompt = f"""{scene}

REFERENCE IMAGES:
{chr(10).join(ref_assignments)}

CHARACTERS (MUST match reference images exactly):
{char_block}

Draw characters EXACTLY as shown in Images 1-3.
Use environment style from Images 4-5.
Apply color palette from Image 6.

STYLE: {style}

NO TEXT, NO WORDS, NO LETTERS."""

    return prompt


def run_comparison(book_slug: str, strategies: list[str], page_nums: list[int] = None,
                   dry_run: bool = False) -> dict:
    """Run comparison experiment across strategies."""
    book_path = BOOKS_DIR / f"{book_slug}.json"
    if not book_path.exists():
        raise FileNotFoundError(f"Book not found: {book_slug}")

    with open(book_path) as f:
        book = json.load(f)

    pages = [p for p in book.get("pages", []) if p.get("scene")]
    if page_nums:
        pages = [p for p in pages if p["page"] in page_nums]

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    experiment_dir = EXPERIMENTS_DIR / "multi_ref" / book_slug / timestamp
    experiment_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"MULTI-REF COMPARISON: {book_slug}")
    print(f"{'='*60}")
    print(f"Strategies: {strategies}")
    print(f"Pages: {len(pages)}")
    print(f"Output: {experiment_dir}")

    if dry_run:
        print("\n[DRY RUN]")
        for strat_name in strategies:
            strat = STRATEGIES[strat_name]
            refs = load_refs_for_strategy(book_slug, strat)
            print(f"\n{strat_name}:")
            print(f"  Model: {strat.model}")
            print(f"  Refs: {[r.name for r in refs]}")

            if pages:
                prompt = build_prompt_for_strategy(book, pages[0], strat, len(refs))
                print(f"  Sample prompt:\n{prompt[:300]}...")
        return {}

    client = ImageClient()
    results = {}

    for strat_name in strategies:
        strat = STRATEGIES[strat_name]
        print(f"\n[{strat_name}] {strat.description}")

        refs = load_refs_for_strategy(book_slug, strat)
        if not refs:
            print(f"  Skipping - no refs found")
            continue

        print(f"  Using {len(refs)} refs: {[r.name for r in refs]}")

        strat_dir = experiment_dir / strat_name
        strat_dir.mkdir(parents=True, exist_ok=True)

        strat_results = []

        for page in pages:
            page_num = page["page"]
            prompt = build_prompt_for_strategy(book, page, strat, len(refs))

            print(f"  Page {page_num}...", end=" ", flush=True)

            start = time.time()
            result = client.generate_with_reference(
                prompt=prompt,
                reference_images=refs,
                model=strat.model,
                verbose=False,
            )
            gen_time = time.time() - start

            if result.success:
                local_path = strat_dir / f"page_{page_num:02d}.png"
                urllib.request.urlretrieve(result.url, local_path)
                print(f"OK ({gen_time:.1f}s, ${result.cost or 0:.3f})")

                strat_results.append({
                    "page": page_num,
                    "success": True,
                    "path": str(local_path),
                    "time": gen_time,
                    "cost": result.cost,
                })
            else:
                print(f"FAILED: {result.error}")
                strat_results.append({
                    "page": page_num,
                    "success": False,
                    "error": result.error,
                })

            time.sleep(1)

        results[strat_name] = {
            "strategy": asdict(strat) if hasattr(strat, '__dataclass_fields__') else {
                "name": strat.name, "description": strat.description,
                "model": strat.model, "ref_types": strat.ref_types
            },
            "refs_used": [str(r) for r in refs],
            "results": strat_results,
        }

    # Save results
    results_path = experiment_dir / "results.json"
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)

    # Generate comparison HTML
    html_path = generate_comparison_html(experiment_dir, book_slug, results)

    print(f"\n{'='*60}")
    print(f"EXPERIMENT COMPLETE")
    print(f"Results: {results_path}")
    print(f"Comparison: {html_path}")
    print(f"\nOpen: open {html_path}")

    return results


def generate_comparison_html(experiment_dir: Path, book_slug: str, results: dict) -> Path:
    """Generate HTML comparison page."""
    strategies = list(results.keys())

    # Get all page numbers
    all_pages = set()
    for strat_data in results.values():
        for r in strat_data.get("results", []):
            all_pages.add(r["page"])
    all_pages = sorted(all_pages)

    # Build table
    headers = "".join(f"<th>{s}</th>" for s in strategies)

    rows = []
    for page_num in all_pages:
        cells = [f"<td><strong>Page {page_num}</strong></td>"]
        for strat in strategies:
            strat_results = results[strat].get("results", [])
            page_result = next((r for r in strat_results if r["page"] == page_num), None)

            if page_result and page_result.get("success"):
                img_name = f"page_{page_num:02d}.png"
                cells.append(f'<td><img src="{strat}/{img_name}" loading="lazy"></td>')
            else:
                error = page_result.get("error", "Not run") if page_result else "Not run"
                cells.append(f'<td class="error">{error}</td>')
        rows.append(f"<tr>{''.join(cells)}</tr>")

    # Cost summary
    cost_rows = []
    for strat in strategies:
        strat_data = results[strat]
        strat_results = strat_data.get("results", [])
        total_cost = sum(r.get("cost", 0) or 0 for r in strat_results)
        success = sum(1 for r in strat_results if r.get("success"))
        model = strat_data.get("strategy", {}).get("model", "?")
        cost_rows.append(f"<tr><td>{strat}</td><td>{model}</td><td>{success}/{len(strat_results)}</td><td>${total_cost:.2f}</td></tr>")

    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Multi-Ref Experiment: {book_slug}</title>
    <style>
        body {{ font-family: -apple-system, sans-serif; margin: 20px; background: #f5f5f5; }}
        h1 {{ color: #333; }}
        .meta {{ background: #fff; padding: 15px; border-radius: 8px; margin-bottom: 20px; }}
        table {{ border-collapse: collapse; width: 100%; background: #fff; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: center; }}
        th {{ background: #4a90a4; color: white; position: sticky; top: 0; }}
        img {{ max-width: 250px; height: auto; border-radius: 4px; }}
        .error {{ color: #c00; font-size: 0.8em; }}
        .summary {{ margin-top: 30px; }}
        .summary table {{ width: auto; }}
        .strategy-info {{ background: #e8f4f8; padding: 10px; margin: 10px 0; border-radius: 4px; }}
    </style>
</head>
<body>
    <h1>Multi-Reference Experiment: {book_slug}</h1>

    <div class="meta">
        <h3>Strategies Tested</h3>
        {"".join(f'<div class="strategy-info"><strong>{s}:</strong> {results[s].get("strategy", {}).get("description", "")}<br>Refs: {len(results[s].get("refs_used", []))}</div>' for s in strategies)}
    </div>

    <h2>Visual Comparison</h2>
    <table>
        <thead><tr><th>Page</th>{headers}</tr></thead>
        <tbody>{''.join(rows)}</tbody>
    </table>

    <div class="summary">
        <h2>Cost Summary</h2>
        <table>
            <thead><tr><th>Strategy</th><th>Model</th><th>Success</th><th>Cost</th></tr></thead>
            <tbody>{''.join(cost_rows)}</tbody>
        </table>
    </div>
</body>
</html>"""

    html_path = experiment_dir / "comparison.html"
    with open(html_path, "w") as f:
        f.write(html)

    return html_path


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Multi-reference image experiment")
    parser.add_argument("book_slug", nargs="?", help="Book to test")
    parser.add_argument("--generate-refs", action="store_true",
                        help="Generate multi-ref image set for the book")
    parser.add_argument("--strategies", default="single-9panel,split-3ref",
                        help=f"Strategies to compare (default: single-9panel,split-3ref). Available: {','.join(STRATEGIES.keys())}")
    parser.add_argument("--pages", help="Comma-separated page numbers (default: 1,5,10)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be generated")
    parser.add_argument("--list-strategies", action="store_true", help="List available strategies")

    args = parser.parse_args()

    if args.list_strategies:
        print("Available strategies:")
        for name, strat in STRATEGIES.items():
            print(f"\n  {name}:")
            print(f"    {strat.description}")
            print(f"    Model: {strat.model}")
            print(f"    Ref types: {strat.ref_types}")
        return

    if not args.book_slug:
        parser.error("book_slug required (or use --list-strategies)")

    if args.generate_refs:
        generate_all_refs(args.book_slug, dry_run=args.dry_run)
        return

    # Parse strategies
    strategies = [s.strip() for s in args.strategies.split(",")]
    for s in strategies:
        if s not in STRATEGIES:
            print(f"Unknown strategy: {s}")
            print(f"Available: {list(STRATEGIES.keys())}")
            return

    # Parse pages (default to a sample)
    page_nums = [1, 5, 10]
    if args.pages:
        page_nums = [int(p.strip()) for p in args.pages.split(",")]

    run_comparison(
        book_slug=args.book_slug,
        strategies=strategies,
        page_nums=page_nums,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
