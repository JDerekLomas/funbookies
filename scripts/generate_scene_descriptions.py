#!/usr/bin/env python3
"""Generate proper scene descriptions for a book.

Transforms placeholder scenes like "Illustration for: [text]..."
into proper visual descriptions with WHO/WHERE/WHAT/STYLE.

Uses Claude to generate descriptions based on:
- Page text
- Story context
- Character definitions from reference_prompt
- Art style guidance
"""

import json
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / ".env")

BOOKS_DIR = PROJECT_ROOT / "public" / "books"

# Anthropic client
try:
    import anthropic
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
except ImportError:
    print("Please install anthropic: pip install anthropic")
    sys.exit(1)


SCENE_GENERATION_PROMPT = """You are an expert at writing image prompts for children's book illustrations.

Given a page of text from a children's book, write a detailed scene description for image generation.

## BOOK CONTEXT
Title: {title}
Level: {level}
Setting: {setting}
Art Style: {style}

## CHARACTER REFERENCE (from reference sheet prompt)
{character_info}

## RULES FOR SCENE DESCRIPTIONS

1. **WHO** - Character with visual identifiers
   - Use EXACT details from character reference
   - Include: age, hair, clothing, expression
   - Example: "Tim, a round-faced boy (6-7) in denim overalls and straw sun hat"

2. **WHERE** - Setting with specificity
   - Ground the scene in a real place
   - Include lighting/weather if relevant
   - Example: "dusty farm yard under bright summer sun"

3. **WHAT** - Action matching the text
   - Use active verbs (running, sitting, looking)
   - Show the emotional state through body language
   - Example: "running eagerly toward the pig"

4. **COMPOSITION**
   - Start with shot type: "Wide shot:", "Medium shot:", "Close-up:"
   - Add: "One cohesive illustration filling the entire canvas"

5. **STYLE**
   - End with style instruction matching the book
   - Always end with: "NO TEXT anywhere in image."

## CRITICAL: NEVER USE NEGATIONS

WRONG: "no ball", "without the tractor", "not raining", "no other characters"
RIGHT: Only describe what IS in the scene, never what isn't.

If you write "no X", the model will generate X. Only describe what you want to see.

## EXAMPLE

Page text: "Tim ran to the big pig. She sat and sat."

Good scene description:
```
Medium shot: Tim, a round-faced boy (6-7) in denim overalls and straw sun hat, running eagerly across dusty farm ground toward a plump pink pig with droopy ears. The pig sits contentedly in a patch of shade by a wooden fence. Bright summer sunlight, warm ochre dirt, green grass in background. One cohesive illustration filling the entire canvas. Eric Carle inspired collage style with bold shapes and layered textures. NO TEXT anywhere in image.
```

## YOUR TASK

Write a scene description for this page:

PAGE {page_num} TEXT:
{page_text}

PREVIOUS PAGE CONTEXT (for continuity):
{prev_context}

Output ONLY the scene description, nothing else. No quotes, no explanation."""


def extract_character_info(reference_prompt: str) -> str:
    """Extract character information from reference prompt."""
    if not reference_prompt:
        return "No character reference available"

    # Find Row 1 section (characters) and extract
    lines = reference_prompt.split('\n')
    char_lines = []
    in_row1 = False

    for line in lines:
        if 'Row 1' in line or '[1]' in line:
            in_row1 = True
        elif 'Row 2' in line:
            in_row1 = False
        if in_row1:
            char_lines.append(line)

    if char_lines:
        return '\n'.join(char_lines)

    # Fallback: return first 500 chars
    return reference_prompt[:500]


def extract_style(reference_prompt: str, book: dict) -> str:
    """Extract art style from reference prompt or book."""
    # Try to find STYLE: line in reference prompt
    if reference_prompt:
        for line in reference_prompt.split('\n'):
            if line.strip().startswith('STYLE:'):
                return line.replace('STYLE:', '').strip()

    # Fallback to art_direction
    art_dir = book.get('art_direction', {})
    if art_dir.get('style'):
        return art_dir['style']

    # Default
    return "Warm, friendly children's book illustration style"


def generate_scene_for_page(
    page: dict,
    book: dict,
    prev_context: str = ""
) -> str:
    """Generate a scene description for a single page."""

    title = book.get('title', 'Untitled')
    level = book.get('level', 'Unknown')
    setting = book.get('setting_context', book.get('summary', ''))
    reference_prompt = book.get('reference_prompt', '')

    character_info = extract_character_info(reference_prompt)
    style = extract_style(reference_prompt, book)

    page_text = page.get('text', '')
    page_num = page.get('story_page', page.get('page', '?'))

    prompt = SCENE_GENERATION_PROMPT.format(
        title=title,
        level=level,
        setting=setting,
        style=style,
        character_info=character_info,
        page_num=page_num,
        page_text=page_text,
        prev_context=prev_context or "First page of story"
    )

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.content[0].text.strip()


def generate_scenes_for_book(slug: str, dry_run: bool = False, force: bool = False) -> bool:
    """Generate scene descriptions for all story pages in a book."""

    book_path = BOOKS_DIR / f"{slug}.json"
    if not book_path.exists():
        print(f"Book not found: {book_path}")
        return False

    with open(book_path) as f:
        book = json.load(f)

    story_pages = [p for p in book.get("pages", []) if p.get("type") == "story"]

    print(f"\n{'='*60}")
    print(f"GENERATING SCENES: {book.get('title', slug)}")
    print(f"{'='*60}")
    print(f"Story pages: {len(story_pages)}")

    # Check which pages need scenes
    pages_to_update = []
    for page in story_pages:
        scene = page.get("scene", "")
        needs_update = (
            not scene or
            scene.startswith("Illustration for:") or
            len(scene) < 80
        )
        if needs_update or force:
            pages_to_update.append(page)

    if not pages_to_update:
        print("\n✅ All pages already have proper scene descriptions")
        return True

    print(f"Pages to update: {len(pages_to_update)}")

    if dry_run:
        print("\n[DRY RUN] Would update these pages:")
        for p in pages_to_update:
            print(f"  - Page {p.get('page')} (story {p.get('story_page')}): {p.get('text', '')[:50]}...")
        return True

    # Generate scenes
    prev_context = ""
    updated = 0

    for page in story_pages:
        pnum = page.get('page')
        story_pnum = page.get('story_page')
        text = page.get('text', '')

        if page in pages_to_update:
            print(f"\n[{story_pnum}/{len(story_pages)}] Generating scene for page {pnum}...")
            print(f"   Text: {text[:60]}...")

            try:
                scene = generate_scene_for_page(page, book, prev_context)
                page['scene'] = scene
                updated += 1
                print(f"   ✓ Generated ({len(scene)} chars)")
                print(f"   Preview: {scene[:100]}...")
            except Exception as e:
                print(f"   ✗ Error: {e}")

        # Update context for next page
        prev_context = f"Page {story_pnum}: {text[:100]}"

    # Save updated book
    if updated > 0:
        with open(book_path, 'w') as f:
            json.dump(book, f, indent=2)
        print(f"\n✅ Updated {updated} scene descriptions")
        print(f"   Saved to: {book_path}")
    else:
        print("\n⚠️  No scenes were updated")

    return True


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate scene descriptions for a book")
    parser.add_argument("slug", help="Book slug")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be updated")
    parser.add_argument("--force", action="store_true", help="Regenerate all scenes even if they exist")
    args = parser.parse_args()

    success = generate_scenes_for_book(args.slug, dry_run=args.dry_run, force=args.force)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
