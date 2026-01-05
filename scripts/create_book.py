#!/usr/bin/env python3
"""
FunBookies Complete Book Creation Pipeline

This script orchestrates the full workflow:
1. Generate story text with Claude
2. Generate images with NanoBanana/MuleRouter
3. Evaluate quality
4. Output ready-to-use book

Usage:
    python create_book.py --level 2 --character rat --theme "finding jam in a kitchen"
"""

import asyncio
import argparse
import json
from pathlib import Path
from datetime import datetime

from book_generator import BookGenerator, BookSpec, CHARACTERS, LEVELS
from image_generator import BookImageGenerator
from quality_evaluator import QualityEvaluator


async def create_complete_book(
    level: int,
    character_type: str,
    theme: str,
    title: str = None,
    custom_words: list = None,
    style_preset: str = "classic",
    project_root: str = ".",
    generate_images: bool = True,
    evaluate: bool = True,
    image_concurrency: int = 2
) -> dict:
    """
    Create a complete book from scratch.

    Returns a summary dict with paths and evaluation results.
    """
    project_root = Path(project_root)
    results = {
        "started_at": datetime.now().isoformat(),
        "spec": {
            "level": level,
            "character": character_type,
            "theme": theme,
            "style": style_preset
        }
    }

    print("\n" + "="*60)
    print("FUNBOOKIES BOOK CREATION PIPELINE")
    print("="*60)

    # Step 1: Generate Story
    print("\n[1/4] Generating story with Claude...")
    print(f"  Level: {level} ({LEVELS[level]['name']})")
    print(f"  Character: {character_type}")
    print(f"  Theme: {theme}")

    spec = BookSpec(
        level=level,
        character_type=character_type,
        theme=theme,
        title=title,
        custom_words=custom_words or [],
        style_preset=style_preset
    )

    book_gen = BookGenerator(str(project_root))
    book = book_gen.create_full_book(spec)
    book_path = book_gen.save_book(book)

    results["book_slug"] = book.slug
    results["book_path"] = str(book_path)
    results["title"] = book.title
    results["pages_count"] = len(book.pages)

    print(f"  Generated: {book.title}")
    print(f"  Saved to: {book_path}")

    # Step 2: Generate Images
    if generate_images:
        print("\n[2/4] Generating images with NanoBanana...")
        print(f"  Style: {style_preset}")
        print(f"  Character: {book.character_description}")

        img_gen = BookImageGenerator(str(project_root))

        img_results = await img_gen.generate_book_images(
            book.slug,
            style_preset=style_preset,
            character_desc=book.character_description,
            concurrency=image_concurrency
        )

        results["images"] = {
            "total": img_results["total"],
            "successful": img_results["successful"],
            "failed": img_results["failed"]
        }

        print(f"  Generated: {img_results['successful']}/{img_results['total']} images")

        if img_results["failed"] > 0:
            print("  Failed pages:")
            for r in img_results["results"]:
                if not r["success"]:
                    print(f"    - {r['page_id']}: {r['error']}")
    else:
        print("\n[2/4] Skipping image generation (--no-images)")
        results["images"] = {"skipped": True}

    # Step 3: Evaluate Quality
    if evaluate:
        print("\n[3/4] Evaluating book quality...")

        evaluator = QualityEvaluator(str(project_root))
        evaluation = evaluator.evaluate_book(
            book.slug,
            evaluate_images=generate_images,
            evaluate_text=True,
            sample_images=5
        )
        eval_path = evaluator.save_evaluation(evaluation)

        results["evaluation"] = {
            "overall_score": evaluation.overall_score,
            "image_score": evaluation.overall_image_score,
            "text_score": evaluation.overall_text_score,
            "summary": evaluation.summary,
            "recommendations": evaluation.recommendations,
            "path": str(eval_path)
        }

        print(f"  {evaluation.summary}")
        if evaluation.recommendations:
            print("  Recommendations:")
            for rec in evaluation.recommendations:
                print(f"    - {rec}")
    else:
        print("\n[3/4] Skipping evaluation (--no-eval)")
        results["evaluation"] = {"skipped": True}

    # Step 4: Summary
    print("\n[4/4] Complete!")
    print("="*60)

    results["completed_at"] = datetime.now().isoformat()

    # Save pipeline results
    results_dir = project_root / "pipeline_runs"
    results_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_path = results_dir / f"{book.slug}_{timestamp}.json"

    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nBook created: {book.title}")
    print(f"  JSON: {book_path}")
    print(f"  Images: public/books/{book.slug}_images/")
    print(f"  Pipeline log: {results_path}")

    if evaluate and results.get("evaluation", {}).get("overall_score"):
        score = results["evaluation"]["overall_score"]
        if score >= 4.0:
            print(f"\n  Quality: GOOD ({score}/5.0)")
        elif score >= 3.0:
            print(f"\n  Quality: ACCEPTABLE ({score}/5.0)")
        else:
            print(f"\n  Quality: NEEDS WORK ({score}/5.0)")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Create a complete FunBookies leveled reader"
    )
    parser.add_argument(
        "--level", type=int, required=True,
        help=f"Reading level (0-{len(LEVELS)-1})"
    )
    parser.add_argument(
        "--character", required=True,
        choices=list(CHARACTERS.keys()),
        help="Main character type"
    )
    parser.add_argument(
        "--theme", required=True,
        help="Story theme/premise (e.g., 'finding treasure in a cave')"
    )
    parser.add_argument(
        "--title",
        help="Optional title (will be generated if not provided)"
    )
    parser.add_argument(
        "--words",
        help="Comma-separated custom words to include"
    )
    parser.add_argument(
        "--style", default="classic",
        choices=["classic", "adventure", "nature", "silly", "cozy"],
        help="Art style preset"
    )
    parser.add_argument(
        "--no-images", action="store_true",
        help="Skip image generation"
    )
    parser.add_argument(
        "--no-eval", action="store_true",
        help="Skip quality evaluation"
    )
    parser.add_argument(
        "--concurrency", type=int, default=2,
        help="Image generation concurrency"
    )
    parser.add_argument(
        "--project-root", default=".",
        help="Project root directory"
    )

    args = parser.parse_args()

    custom_words = []
    if args.words:
        custom_words = [w.strip() for w in args.words.split(",")]

    asyncio.run(create_complete_book(
        level=args.level,
        character_type=args.character,
        theme=args.theme,
        title=args.title,
        custom_words=custom_words,
        style_preset=args.style,
        project_root=args.project_root,
        generate_images=not args.no_images,
        evaluate=not args.no_eval,
        image_concurrency=args.concurrency
    ))


if __name__ == "__main__":
    main()
