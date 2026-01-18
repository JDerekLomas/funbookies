#!/usr/bin/env python3
"""Validate book is ready for image generation.

Checks:
- Book JSON exists
- Reference image exists
- All story pages have scene descriptions
- Scene descriptions are not placeholders
- No negations in scene descriptions
- Character definitions exist
"""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
BOOKS_DIR = PROJECT_ROOT / "public" / "books"
REFS_DIR = BOOKS_DIR / "references"


def validate_book(slug: str) -> bool:
    book_path = BOOKS_DIR / f"{slug}.json"
    ref_path = REFS_DIR / f"{slug}_reference.png"

    errors = []
    warnings = []

    # Check files exist
    if not book_path.exists():
        errors.append(f"Book JSON not found: {book_path}")
        print(f"\n❌ Book JSON not found: {book_path}")
        return False

    if not ref_path.exists():
        errors.append(f"Reference image not found: {ref_path}")

    with open(book_path) as f:
        book = json.load(f)

    story_pages = [p for p in book.get("pages", []) if p.get("type") == "story"]

    # Check each story page
    for page in story_pages:
        pnum = page.get("page", "?")
        story_pnum = page.get("story_page", "?")
        scene = page.get("scene", "")
        text = page.get("text", "")[:50]

        # Check for placeholder scenes
        if scene.startswith("Illustration for:"):
            errors.append(f"Page {pnum} (story {story_pnum}): PLACEHOLDER scene - '{scene[:60]}...'")
            continue

        if not scene:
            errors.append(f"Page {pnum} (story {story_pnum}): Missing scene description")
            continue

        # Check for negations (these make the model generate the unwanted thing)
        negation_patterns = [
            ("no ", "Negation 'no'"),
            ("not ", "Negation 'not'"),
            ("without ", "Negation 'without'"),
            ("don't ", "Negation 'don't'"),
            ("doesn't ", "Negation 'doesn't'"),
            ("isn't ", "Negation 'isn't'"),
            ("aren't ", "Negation 'aren't'"),
            ("never ", "Negation 'never'"),
            ("not a grid", "Anti-pattern: 'not a grid' - say 'single illustration' instead"),
            ("no text", ""),  # This one is OK - we want it
        ]

        scene_lower = scene.lower()
        for pattern, msg in negation_patterns:
            if pattern in scene_lower and pattern != "no text":
                if msg:  # Skip "no text" which is intentional
                    warnings.append(f"Page {pnum}: {msg} - models generate what you mention even when negated")

        # Check for composition instructions
        composition_phrases = [
            "single scene",
            "single illustration",
            "one cohesive",
            "full-bleed",
            "fills the canvas",
            "filling the entire"
        ]
        has_composition = any(phrase in scene_lower for phrase in composition_phrases)
        if not has_composition:
            warnings.append(f"Page {pnum}: Missing composition instruction (add 'Single scene illustration' or 'One cohesive illustration')")

        # Check for NO TEXT instruction
        if "no text" not in scene_lower:
            warnings.append(f"Page {pnum}: Missing 'NO TEXT' instruction")

        # Check scene length (good scenes are detailed)
        if len(scene) < 80:
            warnings.append(f"Page {pnum}: Scene very short ({len(scene)} chars) - probably needs more detail")
        elif len(scene) < 150:
            warnings.append(f"Page {pnum}: Scene short ({len(scene)} chars) - consider adding WHO/WHERE/WHAT details")

    # Check for character definitions
    has_characters = (
        book.get("characters") or
        book.get("story_bible", {}).get("characters") or
        "Row 1" in book.get("reference_prompt", "")  # Reference prompt has character details
    )
    if not has_characters:
        warnings.append("No character definitions found in book - add to 'characters' or 'story_bible'")

    # Report
    print(f"\n{'='*60}")
    print(f"VALIDATION: {slug}")
    print(f"{'='*60}")
    print(f"Story pages: {len(story_pages)}")

    if errors:
        print(f"\n❌ ERRORS ({len(errors)}) - MUST FIX:")
        for e in errors:
            print(f"   • {e}")

    if warnings:
        print(f"\n⚠️  WARNINGS ({len(warnings)}) - SHOULD FIX:")
        for w in warnings:
            print(f"   • {w}")

    if not errors and not warnings:
        print("\n✅ Book is ready for image generation!")
        return True
    elif not errors:
        print("\n⚠️  Book has warnings - review before generating images")
        print("   Run with --force to proceed anyway")
        return True
    else:
        print("\n❌ Book has errors - FIX THESE before generating images")
        print("\nTo fix placeholder scenes, run:")
        print(f"   python scripts/generate_scene_descriptions.py {slug}")
        return False


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Validate book for image generation")
    parser.add_argument("slug", help="Book slug to validate")
    parser.add_argument("--force", action="store_true", help="Return success even with warnings")
    args = parser.parse_args()

    success = validate_book(args.slug)

    if not success and not args.force:
        sys.exit(1)


if __name__ == "__main__":
    main()
