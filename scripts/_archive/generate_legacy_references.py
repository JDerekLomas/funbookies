#!/usr/bin/env python3
"""Generate reference images for legacy books."""

import sys
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

# Legacy books needing references
LEGACY_BOOKS = {
    "dog_pink": {
        "title": "No, No, Dog!",
        "character": "A cute fluffy brown dog with floppy ears, big round eyes, and a pink tongue often sticking out",
        "style": "Playful 2-color riso print style with brown and fluorescent orange, bold black outlines",
        "scenes": [
            "Dog sitting innocently, tongue out, tail wagging",
            "Dog jumping on couch, cushions flying",
            "Dog digging in garden, dirt everywhere",
            "Dog splashing in mud puddle joyfully",
            "Dog running with toilet paper trailing",
            "Dog chewing a shoe, guilty look",
            "Child hugging the messy dog lovingly",
            "Dog sleeping peacefully, tired out",
            "Dog's face close-up, big puppy eyes"
        ]
    },
    "elephant_red": {
        "title": "Stomp! Stomp! Elephant",
        "character": "A big friendly gray elephant with large floppy ears, kind eyes, and a long trunk",
        "style": "Bold children's book illustration, warm red and orange accents, expressive character",
        "scenes": [
            "Elephant standing tall and proud",
            "Elephant stomping with big feet, dust clouds",
            "Elephant spraying water with trunk",
            "Elephant eating leaves happily",
            "Elephant walking through savanna",
            "Elephant trumpeting with trunk raised",
            "Elephant playing with other animals",
            "Elephant resting under a tree",
            "Elephant's friendly face close-up"
        ]
    },
    "mouse_gold": {
        "title": "Mouse in the House",
        "character": "A tiny cute brown mouse with big round ears, whiskers, and a long thin tail",
        "style": "Warm golden tones, cozy indoor scenes, soft watercolor style",
        "scenes": [
            "Mouse peeking out of a hole in the wall",
            "Mouse finding cheese, eyes wide with joy",
            "Mouse tiptoeing across the floor",
            "Mouse hiding from a cat shadow",
            "Mouse running quickly, legs blurring",
            "Mouse in a cozy nest made of fabric scraps",
            "Mouse nibbling on a crumb",
            "Mouse exploring kitchen shelves",
            "Mouse's cute face close-up with whiskers"
        ]
    },
    "castle": {
        "title": "Rats in the Castle",
        "character": "Cute cartoon rats with gray fur, pink ears and noses, long tails, mischievous expressions",
        "style": "Medieval fantasy style, stone castle interiors, warm torchlight, playful atmosphere",
        "scenes": [
            "Castle exterior with rats peeking from windows",
            "Rats scurrying through castle corridor",
            "Rat wearing a tiny crown, playing king",
            "Rats having a feast in the kitchen",
            "Rat sliding down a banister",
            "Rats hiding behind a suit of armor",
            "Rat reading a tiny book by candlelight",
            "Group of rats having an adventure",
            "Friendly rat face close-up"
        ]
    },
    "volcano": {
        "title": "Gus and the Volcano",
        "character": "Gus - a cheerful adventurous child/creature with bright curious eyes, explorer outfit",
        "style": "Vibrant adventure style, dramatic volcano oranges and reds, energetic compositions",
        "scenes": [
            "Gus standing before a smoking volcano",
            "Gus sitting on a rock, looking at the hill",
            "Gus climbing up the volcano slope",
            "Gus reaching the crater rim, arms raised",
            "Bright red lava bubbling in the crater",
            "Gus running away from rising lava",
            "Volcano erupting with steam and sparks",
            "Gus safe on his rock, looking proud",
            "Gus celebrating his adventure"
        ]
    }
}


def download_image(url: str, output_path: Path) -> bool:
    """Download image from URL."""
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(url, output_path)
        print(f"    Saved: {output_path.name}")
        return True
    except Exception as e:
        print(f"    Error: {e}")
        return False


def generate_reference(slug: str, book_info: dict, config) -> bool:
    """Generate a 9-panel reference sheet for a book."""
    output_path = REFS_DIR / f"{slug}_reference.png"

    if output_path.exists():
        print(f"  {slug}: Reference already exists, skipping")
        return True

    print(f"\n  Generating reference for: {book_info['title']}")

    # Build the prompt
    scenes_text = "\n".join([f"Panel {i+1}: {scene}" for i, scene in enumerate(book_info["scenes"])])

    prompt = f"""A 9-panel character and style reference sheet for a children's picture book.

TITLE: {book_info['title']}

MAIN CHARACTER:
{book_info['character']}

ART STYLE:
{book_info['style']}

9 PANELS (3x3 grid):
{scenes_text}

Each panel shows a different moment or expression. Consistent character design across all panels. Child-friendly, engaging illustrations.

IMPORTANT: No text or words in any panel. Focus on visual storytelling."""

    body = {
        "prompt": prompt,
        "size": "1024*1024",
        "n": 1
    }

    with APIClient(config) as client:
        result = create_and_poll_task(
            client=client,
            endpoint_path="/vendors/google/v1/nano-banana-pro/generation",
            request_body=body,
            result_key="images",
            interval=5.0,
            max_wait=300.0,
            verbose=True
        )

        if result.results:
            return download_image(result.results[0], output_path)
        else:
            print(f"    Failed: {result.error}")
            return False


def main():
    print("="*60)
    print("GENERATING LEGACY BOOK REFERENCES")
    print("="*60)

    config = load_config()
    print(f"API: {config.site}")

    REFS_DIR.mkdir(parents=True, exist_ok=True)

    success = 0
    for slug, info in LEGACY_BOOKS.items():
        if generate_reference(slug, info, config):
            success += 1

    print("\n" + "="*60)
    print(f"COMPLETE: Generated {success}/{len(LEGACY_BOOKS)} references")
    print("="*60)


if __name__ == "__main__":
    main()
