#!/usr/bin/env python3
"""
Master script to generate all images for a book.

Pipeline:
1. Generate v3-style reference (9-panel with spatial layout)
2. Generate cover image
3. Generate title page (page 3)
4. Generate all story pages

Usage:
    python generate_book_complete.py <slug>
    python generate_book_complete.py <slug> --ref-only
    python generate_book_complete.py <slug> --pages-only
    python generate_book_complete.py --all
    python generate_book_complete.py --status
"""

import sys
import argparse
import base64
import json
import urllib.request
import time
from pathlib import Path
from dataclasses import dataclass

SKILL_DIR = Path("/Users/dereklomas/.claude/plugins/cache/mulerouter-skills/mulerouter-skills/1.0.0/skills/mulerouter-skills")
sys.path.insert(0, str(SKILL_DIR))

from dotenv import load_dotenv
load_dotenv(SKILL_DIR / ".env")

from core import APIClient, load_config, create_and_poll_task

# Paths
BOOKS_DIR = Path("/Users/dereklomas/lilbookies/public/books")
REFS_DIR = BOOKS_DIR / "references"
PAGES_DIR = BOOKS_DIR / "images"
COVERS_DIR = Path("/Users/dereklomas/lilbookies/public/images/covers")

# Band style templates
BAND_STYLES = {
    "A": {
        "base": "Simple bold shapes, soft pastel watercolor, minimal detail, toddler-friendly",
        "mood": "gentle, comforting, bright, simple"
    },
    "B": {
        "base": "Playful watercolor illustration, expressive characters, vibrant warm colors",
        "mood": "energetic, fun, adventurous, friendly"
    },
    "C": {
        "base": "Rich watercolor illustration, detailed characters and settings, dynamic compositions",
        "mood": "exciting, imaginative, engaging, detailed"
    },
    "D": {
        "base": "Sophisticated watercolor illustration, atmospheric lighting, nuanced details",
        "mood": "atmospheric, immersive, evocative, complex"
    }
}


@dataclass
class BookInfo:
    slug: str
    title: str
    band: str
    pages: list
    style: dict = None

    @property
    def story_pages(self):
        return [p for p in self.pages if p.get("type") == "story" and p.get("scene")]

    @property
    def cover_page(self):
        for p in self.pages:
            if p.get("type") == "cover":
                return p
        return None

    @property
    def title_page(self):
        for p in self.pages:
            if p.get("type") == "title":
                return p
        return None


def load_book(slug: str) -> BookInfo:
    """Load book data from JSON."""
    path = BOOKS_DIR / f"{slug}.json"
    if not path.exists():
        return None

    with open(path) as f:
        data = json.load(f)

    band = data.get("band", data.get("level", "B")[0])

    return BookInfo(
        slug=slug,
        title=data.get("title", slug),
        band=band,
        pages=data.get("pages", []),
        style=data.get("style")
    )


def image_to_base64_uri(path: Path) -> str:
    """Convert image to base64 data URI."""
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return f"data:image/png;base64,{b64}"


def download_image(url: str, output_path: Path) -> bool:
    """Download image from URL."""
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(url, output_path)
        return True
    except Exception as e:
        print(f"      Download error: {e}")
        return False


def extract_characters_and_setting(book: BookInfo) -> tuple[str, str]:
    """Extract character and setting info from scenes."""
    all_scenes = " ".join([p.get("scene", "") for p in book.pages if p.get("scene")])

    # Simple extraction - could be enhanced with LLM
    characters = []
    settings = []

    # Common character patterns
    if "girl" in all_scenes.lower() or "she" in all_scenes.lower():
        characters.append("Young girl protagonist")
    if "boy" in all_scenes.lower() or "he" in all_scenes.lower():
        characters.append("Young boy protagonist")
    if "mother" in all_scenes.lower() or "mom" in all_scenes.lower():
        characters.append("Mother figure")
    if "father" in all_scenes.lower() or "dad" in all_scenes.lower():
        characters.append("Father figure")
    if "grandmother" in all_scenes.lower() or "grandma" in all_scenes.lower():
        characters.append("Grandmother")
    if "cat" in all_scenes.lower():
        characters.append("Cat")
    if "dog" in all_scenes.lower() or "pup" in all_scenes.lower():
        characters.append("Dog/puppy")

    return ", ".join(characters) if characters else "Main character", all_scenes[:200]


def generate_reference(book: BookInfo, config) -> Path:
    """Generate v3-style reference image."""
    output_path = REFS_DIR / f"{book.slug}_reference_v3.png"

    if output_path.exists():
        print(f"    Reference already exists: {output_path.name}")
        return output_path

    print(f"    Generating reference...")

    band_style = BAND_STYLES.get(book.band, BAND_STYLES["B"])
    characters, setting_hint = extract_characters_and_setting(book)

    # Get first 9 scenes for panels
    scenes = [p.get("scene", "")[:80] for p in book.pages if p.get("scene")][:9]
    while len(scenes) < 9:
        scenes.append(f"Scene from {book.title}")

    prompt = f"""A 9-panel reference sheet for children's book illustration, arranged in 3x3 grid.

STYLE: {band_style['base']}
MOOD: {band_style['mood']}

PANEL LAYOUT:
Panel 1 (top-left): WIDE ESTABLISHING SHOT - Show the main setting/location with spatial layout
Panel 2 (top-center): MAIN CHARACTER - Full figure character design
Panel 3 (top-right): SECONDARY CHARACTER or supporting character design
Panel 4 (middle-left): KEY LOCATION exterior view
Panel 5 (middle-center): KEY LOCATION alternate view or interior
Panel 6 (middle-right): Another important setting
Panel 7 (bottom-left): Scene: {scenes[0]}
Panel 8 (bottom-center): Scene: {scenes[1]}
Panel 9 (bottom-right): MOOD/PALETTE - Key lighting, weather, or emotional tone

Book: "{book.title}"
Characters: {characters}

Each panel is a square vignette. Consistent art style across all panels. White borders between panels.

CRITICAL: NO text, words, letters, or writing of any kind. Pure illustration only."""

    body = {
        "prompt": prompt,
        "aspect_ratio": "1:1",
        "resolution": "2K"
    }

    with APIClient(config) as client:
        result = create_and_poll_task(
            client=client,
            endpoint_path="/vendors/google/v1/nano-banana-pro/generation",
            request_body=body,
            result_key="images",
            interval=5.0,
            max_wait=300.0,
            verbose=False
        )

        if result.results:
            if download_image(result.results[0], output_path):
                print(f"    ✓ Reference saved: {output_path.name}")
                return output_path
        else:
            print(f"    ✗ Reference failed: {result.error}")

    return None


# Shot type specific prompt templates
SHOT_PROMPTS = {
    "wide": """ONE wide establishing shot for children's book. No grid, no panels.

Scene: {scene}

Style: {style}

IMPORTANT: Match the EXACT spatial layout from Panel 1 of the reference (top-left).
Keep all geography consistent - building positions, distances, landscape features.
Characters should match those in Panels 2-3 of the reference.

CRITICAL: NO text, words, or letters. Single illustration only.""",

    "medium": """ONE medium shot for children's book. No grid, no panels.

Scene: {scene}

Style: {style}

Focus on the character(s) from waist up or full figure with some environment context.
Match character designs from Panels 2-3 of the reference image.
Background can be simplified or slightly blurred.

CRITICAL: NO text, words, or letters. Single illustration only.""",

    "close": """ONE close-up shot for children's book. No grid, no panels.

Scene: {scene}

Style: {style}

Focus tightly on face, hands, or key details. Minimal or no background.
Match character features from Panels 2-3 of the reference.
Capture emotion and expression clearly.

CRITICAL: NO text, words, or letters. Single illustration only.""",

    "interior": """ONE interior scene for children's book. No grid, no panels.

Scene: {scene}

Style: {style}

Match interior settings from Panels 4-6 of the reference if applicable.
Focus on the indoor environment and character within it.
Consistent lighting and architectural details.

CRITICAL: NO text, words, or letters. Single illustration only."""
}


def generate_page(book: BookInfo, page_num: int, scene: str, page_type: str,
                  ref_uri: str, config, shot_type: str = None) -> bool:
    """Generate a single page image."""

    if page_type == "cover":
        output_path = COVERS_DIR / f"{book.slug}.png"
    else:
        output_path = PAGES_DIR / f"{book.slug}_page{str(page_num).zfill(2)}.png"

    if output_path.exists():
        return True  # Skip existing

    band_style = BAND_STYLES.get(book.band, BAND_STYLES["B"])

    # Use shot-type specific prompt or default to medium
    shot = shot_type or "medium"
    prompt_template = SHOT_PROMPTS.get(shot, SHOT_PROMPTS["medium"])
    prompt = prompt_template.format(scene=scene, style=band_style['base'])

    body = {
        "prompt": prompt,
        "images": [ref_uri],
        "size": "1024*1024",
        "n": 1
    }

    with APIClient(config) as client:
        result = create_and_poll_task(
            client=client,
            endpoint_path="/vendors/alibaba/v1/wan2.6-image/generation",
            request_body=body,
            result_key="images",
            interval=5.0,
            max_wait=300.0,
            verbose=False
        )

        if result.results:
            return download_image(result.results[0], output_path)
        else:
            print(f"      Failed: {result.error}")
            return False


def generate_book(slug: str, ref_only: bool = False, pages_only: bool = False):
    """Generate all images for a book."""

    print(f"\n{'='*60}")
    print(f"GENERATING: {slug}")
    print('='*60)

    book = load_book(slug)
    if not book:
        print(f"  Book not found: {slug}")
        return False

    print(f"  Title: {book.title}")
    print(f"  Band: {book.band}")
    print(f"  Story pages: {len(book.story_pages)}")

    config = load_config()

    # Step 1: Generate reference
    if not pages_only:
        ref_path = generate_reference(book, config)
        if not ref_path:
            print("  ✗ Failed to generate reference")
            return False
        if ref_only:
            return True
    else:
        # Find existing reference
        for version in ["v3", "v2", ""]:
            suffix = f"_{version}" if version else ""
            ref_path = REFS_DIR / f"{slug}_reference{suffix}.png"
            if ref_path.exists():
                break
        if not ref_path.exists():
            print("  ✗ No reference found. Run without --pages-only first.")
            return False

    ref_uri = image_to_base64_uri(ref_path)
    print(f"  Using reference: {ref_path.name}")

    # Step 2: Generate cover
    if book.cover_page:
        print(f"\n  [COVER]")
        scene = book.cover_page.get("scene", f"Cover illustration for {book.title}")
        cover_shot = book.cover_page.get("shot_type", "wide")
        if generate_page(book, 1, scene, "cover", ref_uri, config, shot_type=cover_shot):
            print(f"    ✓ Cover")
        else:
            print(f"    ✗ Cover failed")

    # Step 3: Generate title page (page 3)
    if book.title_page:
        print(f"\n  [TITLE PAGE]")
        scene = f"Decorative title page illustration showing the main setting of {book.title}. No characters, peaceful establishing shot."
        if generate_page(book, 3, scene, "title", ref_uri, config, shot_type="wide"):
            print(f"    ✓ Title page")
        else:
            print(f"    ✗ Title page failed")

    # Step 4: Generate story pages
    print(f"\n  [STORY PAGES] {len(book.story_pages)} pages")
    success = 0
    for i, page in enumerate(book.story_pages):
        page_num = page.get("page", i + 4)
        scene = page.get("scene", "")
        shot_type = page.get("shot_type", "medium")

        output_path = PAGES_DIR / f"{slug}_page{str(page_num).zfill(2)}.png"
        if output_path.exists():
            success += 1
            continue

        print(f"    [{page_num}] ({shot_type}) {scene[:35]}...", end=" ", flush=True)
        if generate_page(book, page_num, scene, "story", ref_uri, config, shot_type=shot_type):
            print("✓")
            success += 1
        else:
            print("✗")

    print(f"\n  COMPLETE: {success}/{len(book.story_pages)} pages")
    return True


def get_all_books() -> list[str]:
    """Get list of all book slugs."""
    slugs = []
    for path in BOOKS_DIR.glob("*.json"):
        if path.stem != "manifest":
            slugs.append(path.stem)
    return sorted(slugs)


def get_incomplete_books() -> list[str]:
    """Get books that need page generation."""
    incomplete = []
    for slug in get_all_books():
        book = load_book(slug)
        if not book:
            continue

        # Count existing pages
        existing = len(list(PAGES_DIR.glob(f"{slug}_page*.png")))
        needed = len(book.story_pages)

        if existing < needed:
            incomplete.append(slug)

    return incomplete


def print_status():
    """Print status of all books."""
    print("\n" + "="*70)
    print("BOOK GENERATION STATUS")
    print("="*70)

    complete = []
    partial = []
    none = []

    for slug in get_all_books():
        book = load_book(slug)
        if not book:
            continue

        # Check reference
        ref = "-"
        for v in ["v3", "v2", ""]:
            suffix = f"_{v}" if v else ""
            if (REFS_DIR / f"{slug}_reference{suffix}.png").exists():
                ref = v if v else "v1"
                break

        # Check cover
        cover = "✓" if (COVERS_DIR / f"{slug}.png").exists() else "-"

        # Count pages
        existing = len(list(PAGES_DIR.glob(f"{slug}_page*.png")))
        needed = len(book.story_pages)

        status = {
            "slug": slug,
            "title": book.title[:25],
            "band": book.band,
            "ref": ref,
            "cover": cover,
            "pages": f"{existing}/{needed}"
        }

        if existing >= needed and needed > 0:
            complete.append(status)
        elif existing > 0:
            partial.append(status)
        else:
            none.append(status)

    print(f"\n✓ COMPLETE ({len(complete)} books):")
    for s in complete:
        print(f"  {s['slug']:<30} {s['pages']:>8}")

    print(f"\n◐ PARTIAL ({len(partial)} books):")
    for s in partial:
        print(f"  {s['slug']:<30} {s['pages']:>8}  (ref:{s['ref']})")

    print(f"\n✗ NO PAGES ({len(none)} books):")
    for s in none:
        print(f"  {s['slug']:<30} {s['pages']:>8}  (ref:{s['ref']})")

    total_needed = sum(int(s['pages'].split('/')[1]) - int(s['pages'].split('/')[0])
                       for s in partial + none if '/' in s['pages'])
    print(f"\n{'='*70}")
    print(f"TOTAL PAGES TO GENERATE: ~{total_needed}")
    print(f"ESTIMATED TIME: ~{total_needed * 0.5:.0f} minutes")
    print("="*70)


def main():
    parser = argparse.ArgumentParser(description="Generate book images")
    parser.add_argument("slug", nargs="?", help="Book slug to generate")
    parser.add_argument("--ref-only", action="store_true", help="Only generate reference")
    parser.add_argument("--pages-only", action="store_true", help="Only generate pages (requires existing ref)")
    parser.add_argument("--all", action="store_true", help="Generate all incomplete books")
    parser.add_argument("--status", action="store_true", help="Show status of all books")

    args = parser.parse_args()

    if args.status:
        print_status()
        return

    if args.all:
        incomplete = get_incomplete_books()
        print(f"Generating {len(incomplete)} incomplete books...")
        for slug in incomplete:
            generate_book(slug, args.ref_only, args.pages_only)
        return

    if not args.slug:
        parser.print_help()
        return

    generate_book(args.slug, args.ref_only, args.pages_only)


if __name__ == "__main__":
    main()
