#!/usr/bin/env python3
"""Generate comprehensive reference_prompt for book JSONs.

Extracts character details, art direction, color palette, and story summary
to create rich prompts for 9-panel reference sheet generation.
"""

import json
from pathlib import Path

BOOKS_DIR = Path("/Users/dereklomas/lilbookies/public/books")


def build_reference_prompt(slug: str, book: dict) -> str:
    """Build a comprehensive prompt for generating a 9-panel reference image."""

    title = book.get("title", slug)
    theme = book.get("theme", "")
    summary = book.get("summary", "")

    # Extract character information
    characters = book.get("character", {})
    character_descriptions = []

    # Handle different character field structures
    if isinstance(characters, dict):
        names = characters.get("names", [])
        style_notes = characters.get("style_notes", "")

        # Look for individual character details
        for key, value in characters.items():
            if isinstance(value, dict) and key not in ["names"]:
                char_name = key.capitalize()
                species = value.get("species", "")
                color = value.get("color", "")
                body = value.get("body", "")
                distinguishing = value.get("distinguishing_feature", "")
                appearance = value.get("appearance", "")
                expression = value.get("expression_default", "")

                parts = [f"{char_name}:"]
                if species:
                    parts.append(species)
                if color:
                    parts.append(f"({color})")
                if body:
                    parts.append(body)
                if distinguishing:
                    parts.append(f"Distinguishing feature: {distinguishing}")
                if appearance:
                    parts.append(appearance)
                if expression:
                    parts.append(f"Expression: {expression}")

                if len(parts) > 1:
                    character_descriptions.append(" ".join(parts))

    # Extract art direction
    art_dir = book.get("art_direction", {})
    style = art_dir.get("style", "")
    mood = art_dir.get("mood", "")
    influences = art_dir.get("influences", [])
    must_include = art_dir.get("must_include", "")
    avoid = art_dir.get("avoid", "")

    # Extract color palette
    palette = art_dir.get("palette", {})
    color_list = []
    for color_name, color_value in palette.items():
        # Format: "grass_green (#81C784)" -> "grass green: #81C784"
        name_formatted = color_name.replace("_", " ")
        color_list.append(f"{name_formatted}: {color_value}")

    # Build the comprehensive prompt
    sections = []

    # Title and theme
    sections.append(f"9-PANEL REFERENCE SHEET for \"{title}\"")

    if theme:
        sections.append(f"\nSTORY THEME: {theme}")

    if summary:
        sections.append(f"\nSUMMARY: {summary}")

    # Characters
    if character_descriptions:
        sections.append("\nCHARACTERS:")
        for desc in character_descriptions:
            sections.append(f"- {desc}")

    if style_notes := characters.get("style_notes", ""):
        sections.append(f"\nCHARACTER STYLE NOTES: {style_notes}")

    # Art direction
    if style:
        sections.append(f"\nART STYLE: {style}")

    if mood:
        sections.append(f"\nMOOD: {mood}")

    if influences:
        sections.append(f"\nINFLUENCES: {', '.join(influences)}")

    # Color palette
    if color_list:
        sections.append(f"\nCOLOR PALETTE: {', '.join(color_list[:8])}")  # Limit to 8 colors

    # Key scenes from pages
    scenes = []
    for p in book.get("pages", []):
        scene = p.get("scene") or p.get("text", "")
        if scene and len(scene) > 10:
            scenes.append(scene[:80] + "..." if len(scene) > 80 else scene)

    if scenes[:6]:
        sections.append("\nKEY SCENES TO SHOW:")
        for i, scene in enumerate(scenes[:6], 1):
            sections.append(f"  Panel {i}: {scene}")

    # Technical requirements
    sections.append("\nTECHNICAL REQUIREMENTS:")
    sections.append("- 9 panels in 3x3 grid")
    sections.append("- Consistent style across all panels")
    sections.append("- Square vignettes showing characters, settings, key moments")

    if must_include:
        sections.append(f"- {must_include}")

    if avoid:
        sections.append(f"- AVOID: {avoid}")

    sections.append("- NO TEXT, WORDS, OR LETTERS in the image")

    return "\n".join(sections)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--slug", help="Update specific book only")
    parser.add_argument("--preview", action="store_true", help="Preview prompt without saving")
    args = parser.parse_args()

    book_files = list(BOOKS_DIR.glob("*.json"))
    book_files = [f for f in book_files if f.name != "manifest.json"]

    if args.slug:
        book_files = [f for f in book_files if f.stem == args.slug]
        if not book_files:
            print(f"Book not found: {args.slug}")
            return

    print(f"Generating reference_prompt for {len(book_files)} books...\n")

    updated = 0
    for book_file in sorted(book_files):
        slug = book_file.stem

        with open(book_file) as f:
            book = json.load(f)

        # Generate the reference prompt
        ref_prompt = build_reference_prompt(slug, book)

        if args.preview:
            print(f"=== {slug} ===")
            print(ref_prompt)
            print("\n" + "="*60 + "\n")
            continue

        # Add to book data
        book["reference_prompt"] = ref_prompt

        # Write back
        with open(book_file, 'w') as f:
            json.dump(book, f, indent=2)

        print(f"[{slug}] Updated reference_prompt")
        updated += 1

    if not args.preview:
        print(f"\nDone! Updated {updated} books.")


if __name__ == "__main__":
    main()
