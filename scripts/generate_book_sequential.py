#!/usr/bin/env python3
"""Generate book pages sequentially, using reference + previous pages as context."""

import sys
import base64
import json
import urllib.request
from pathlib import Path

SKILL_DIR = Path("/Users/dereklomas/.claude/plugins/cache/mulerouter-skills/mulerouter-skills/1.0.0/skills/mulerouter-skills")
sys.path.insert(0, str(SKILL_DIR))

from dotenv import load_dotenv
load_dotenv(SKILL_DIR / ".env")

from core import APIClient, load_config, create_and_poll_task

BOOKS_DIR = Path("/Users/dereklomas/lilbookies/public/books")
REFS_DIR = BOOKS_DIR / "references"
PAGES_DIR = BOOKS_DIR / "images"
COVERS_DIR = Path("/Users/dereklomas/lilbookies/public/images/covers")


def image_to_base64_uri(path: Path) -> str:
    """Convert image file to data URI."""
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return f"data:image/png;base64,{b64}"


def download_image(url: str, output_path: Path) -> bool:
    """Download image from URL."""
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(url, output_path)
        print(f"      Saved: {output_path.name}")
        return True
    except Exception as e:
        print(f"      Error: {e}")
        return False


# Book-specific style and character details
BOOK_STYLES = {
    "d1-the-lighthouse-keeper": {
        "style": "Sophisticated coastal watercolor illustration, atmospheric lighting",
        "characters": """
- Maya: young girl (age 11) with brown windblown hair, wears orange/red shirt and blue overalls
- Grandmother: elderly woman with gray hair in a bun, kind wrinkled face, wears purple/lavender dress
- Mr. Chen: harbor master, middle-aged Asian man with captain's hat, friendly face
""",
        "setting": """
- Location: coastal New England, rocky cliffs
- Lighthouse: tall white lighthouse with red trim, weathered but beloved
- Cottage: small gray shingled cottage near the lighthouse
- Ocean: dramatic waves, moody skies
""",
        "palette": "Muted blues, warm sunset oranges, weathered whites, stormy grays"
    }
}


def generate_page_sequential(
    slug: str,
    page_num: int,
    scene: str,
    page_type: str,
    ref_path: Path,
    prev_page_path: Path | None,
    prev_scenes: list[str],
    book_style: dict,
    config
) -> Path | None:
    """Generate a page using reference + previous page context."""

    if page_type == "cover":
        output_path = COVERS_DIR / f"{slug}_v2.png"
    else:
        output_path = PAGES_DIR / f"{slug}_seq_page{str(page_num).zfill(2)}.png"

    print(f"\n  [PAGE {page_num}] {page_type.upper()}")
    print(f"    Scene: {scene[:60]}...")

    # Build image inputs: always include reference, optionally include previous page
    images = [image_to_base64_uri(ref_path)]

    if prev_page_path and prev_page_path.exists():
        images.append(image_to_base64_uri(prev_page_path))
        print(f"    Using previous page: {prev_page_path.name}")

    # Build context from previous scenes
    prev_context = ""
    if prev_scenes:
        recent = prev_scenes[-3:]  # Last 3 pages for context
        prev_context = "\n\nPrevious pages in sequence:\n" + "\n".join(
            f"  - Page {i}: {s[:80]}" for i, s in enumerate(recent, len(prev_scenes) - len(recent) + 1)
        )

    prompt = f"""Create ONE SINGLE children's book illustration (not a grid, not multiple panels).

PAGE TYPE: {page_type.upper()}
SCENE: {scene}

STYLE: {book_style['style']}
PALETTE: {book_style['palette']}

CHARACTERS:{book_style['characters']}

SETTING:{book_style['setting']}
{prev_context}

REFERENCE IMAGES:
- Image 1: 9-panel style guide showing character designs and color palette
{"- Image 2: The previous page in the story - maintain visual continuity" if len(images) > 1 else ""}

CRITICAL INSTRUCTIONS:
1. Create ONE SINGLE illustration filling the entire frame
2. Do NOT create a grid or multiple panels
3. Match the exact character designs from the reference
4. Maintain visual continuity with the previous page if provided
5. Do NOT include any text, words, or letters

OUTPUT: A single {page_type} illustration for a children's book."""

    body = {
        "prompt": prompt,
        "images": images,
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
            if download_image(result.results[0], output_path):
                return output_path
        else:
            print(f"      Failed: {result.error}")

    return None


def generate_book_sequential(slug: str, max_pages: int = None):
    """Generate all pages for a book sequentially with context."""

    print("=" * 60)
    print(f"SEQUENTIAL GENERATION: {slug}")
    print("=" * 60)

    # Load book
    book_path = BOOKS_DIR / f"{slug}.json"
    with open(book_path) as f:
        book = json.load(f)

    print(f"Title: {book['title']}")
    print(f"Band: {book.get('band', '?')}")

    # Get reference
    ref_path = REFS_DIR / f"{slug}_reference.png"
    if not ref_path.exists():
        ref_path = REFS_DIR / f"{slug}_reference_v2.png"
    if not ref_path.exists():
        print(f"ERROR: No reference found for {slug}")
        return

    print(f"Reference: {ref_path.name}")

    # Get book style
    book_style = BOOK_STYLES.get(slug, {
        "style": "Warm watercolor children's book illustration",
        "characters": "Characters as described in each scene",
        "setting": "Settings as described in each scene",
        "palette": "Warm, friendly colors suitable for children"
    })

    # Get pages to generate
    pages = [p for p in book["pages"] if p.get("scene")]
    if max_pages:
        pages = pages[:max_pages]

    print(f"Pages to generate: {len(pages)}")

    config = load_config()

    prev_page_path = None
    prev_scenes = []
    generated = []

    for page in pages:
        page_num = page.get("page", 0)
        scene = page.get("scene", "")
        page_type = page.get("type", "story")

        result_path = generate_page_sequential(
            slug=slug,
            page_num=page_num,
            scene=scene,
            page_type=page_type,
            ref_path=ref_path,
            prev_page_path=prev_page_path,
            prev_scenes=prev_scenes,
            book_style=book_style,
            config=config
        )

        if result_path:
            generated.append(result_path)
            prev_page_path = result_path
            prev_scenes.append(scene)

    print("\n" + "=" * 60)
    print(f"COMPLETE: Generated {len(generated)}/{len(pages)} pages")
    print("=" * 60)

    return generated


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("slug", help="Book slug to generate")
    parser.add_argument("--pages", type=int, default=5, help="Max pages to generate")
    args = parser.parse_args()

    generate_book_sequential(args.slug, args.pages)
