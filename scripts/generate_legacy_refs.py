#!/usr/bin/env python3
"""Generate reference images for legacy books with minimal metadata."""

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

# Custom prompts for legacy books based on their titles
LEGACY_BOOK_STYLES = {
    "fern_gust_orange": {
        "title": "Fern and the Gust",
        "style": "Playful watercolor illustration, autumn colors, wind and leaves",
        "panels": [
            "A girl named Fern standing in a field with wind blowing her hair",
            "Autumn leaves swirling in a gust of wind",
            "Fern reaching for her hat blown by the wind",
            "Wind bending tall grass and flowers",
            "Fern laughing as leaves dance around her",
            "A colorful kite flying in a gusty sky",
            "Fern chasing leaves across a meadow",
            "Wind chimes tinkling in the breeze",
            "Fern hugging herself against a playful wind"
        ]
    },
    "jungle_v2": {
        "title": "Zee and the Jungle",
        "style": "Vibrant tropical illustration, lush greens, exotic animals",
        "panels": [
            "A curious child named Zee entering a dense jungle",
            "Colorful parrots perched in tropical trees",
            "A friendly monkey swinging on vines",
            "Zee crossing a wooden jungle bridge",
            "A jaguar resting on a tree branch",
            "Tropical flowers in bright colors",
            "Zee discovering a hidden waterfall",
            "Butterflies fluttering through jungle leaves",
            "Zee making friends with jungle animals"
        ]
    },
    "pig_mud": {
        "title": "Pig in the Mud",
        "style": "Playful farm illustration, muddy pig, warm earthy colors",
        "panels": [
            "A happy pink pig splashing in mud",
            "The pig rolling joyfully in a mud puddle",
            "Muddy pig footprints across a barnyard",
            "The pig covered in mud, grinning widely",
            "A farmer looking surprised at the muddy pig",
            "The pig shaking mud everywhere",
            "Clean pig after a bath, looking annoyed",
            "The pig sneaking back toward the mud",
            "Sunset over a peaceful farm with mud puddles"
        ]
    },
    "pip_well_orange": {
        "title": "Pip and the Well",
        "style": "Rustic village illustration, stone well, warm orange sunset tones",
        "panels": [
            "A small child named Pip peering into an old stone well",
            "A wooden bucket hanging from a well rope",
            "Pip dropping a coin into the well and making a wish",
            "The well in a cottage garden with flowers",
            "Pip listening for the splash at the bottom",
            "A frog sitting on the edge of the well",
            "Pip pulling up a bucket of water",
            "Sunset light reflecting off the well water",
            "Pip waving goodbye to the magical well"
        ]
    },
    "puppy_silver": {
        "title": "Puppy's Birthday",
        "style": "Festive celebration illustration, party decorations, silver and pastel colors",
        "panels": [
            "A fluffy puppy wearing a birthday hat",
            "Colorful birthday balloons and streamers",
            "A dog-bone shaped birthday cake with candles",
            "The puppy opening wrapped presents",
            "Party guests: other cute puppies and dogs",
            "The puppy playing with a new toy",
            "Birthday banner saying Happy Birthday",
            "The puppy blowing out candles on the cake",
            "Tired happy puppy after the party"
        ]
    },
    "sol_stone_orange": {
        "title": "Sol and the Stone",
        "style": "Desert adventure illustration, warm oranges and golds, mysterious stone",
        "panels": [
            "A child named Sol finding a glowing stone in the desert",
            "The magical stone shining with warm light",
            "Sol holding the stone up to examine it",
            "Desert landscape with cacti and sand dunes",
            "The stone casting beautiful shadows",
            "Sol showing the stone to a desert lizard friend",
            "Sunset colors reflecting off the stone",
            "Sol placing the stone in a special place",
            "The stone lighting up the night desert"
        ]
    },
    "pig_yellow": {
        "title": "Pig in Mud",
        "style": "Simple toddler-friendly illustration, happy pig, bright yellow sunshine",
        "panels": [
            "A cute pink pig looking at a mud puddle",
            "The pig jumping into the mud with a splash",
            "Mud splattering everywhere",
            "The pig's happy face covered in mud",
            "A bright yellow sun shining overhead",
            "The pig rolling on its back in the mud",
            "Farm animals watching the pig play",
            "The pig getting clean in a tub",
            "Happy clean pig under sunny sky"
        ]
    }
}


def generate_reference(slug: str, config) -> bool:
    """Generate a reference image for a legacy book."""

    if slug not in LEGACY_BOOK_STYLES:
        print(f"  No style defined for {slug}")
        return False

    book_info = LEGACY_BOOK_STYLES[slug]
    output_path = REFS_DIR / f"{slug}_reference.png"

    panel_text = "\n".join([f"Panel {i+1}: {p}" for i, p in enumerate(book_info["panels"])])

    prompt = f"""A 9-panel reference sheet for children's book illustration style.
Style: {book_info['style']}

The 9 panels arranged in a 3x3 grid showing:
{panel_text}

Consistent art style across all panels, suitable for children's picture book illustration. Warm, friendly, watercolor style.

IMPORTANT: Minimize text in panels. Focus on visual style, characters, colors, and mood. No title text."""

    print(f"  Title: {book_info['title']}")
    print(f"  Style: {book_info['style']}")

    body = {
        "prompt": prompt,
        "size": "1024*1024",
        "n": 1
    }

    with APIClient(config) as client:
        result = create_and_poll_task(
            client=client,
            endpoint_path="/vendors/alibaba/v1/wan2.6-t2i/generation",
            request_body=body,
            result_key="images",
            interval=5.0,
            max_wait=300.0,
            verbose=True
        )

        if result.results:
            url = result.results[0]
            print(f"  Generated: {url}")
            try:
                urllib.request.urlretrieve(url, output_path)
                print(f"  Saved to: {output_path}")
                return True
            except Exception as e:
                print(f"  Download error: {e}")
                return False
        else:
            print(f"  Failed: {result.error}")
            return False


def main():
    legacy_books = list(LEGACY_BOOK_STYLES.keys())

    print(f"Generating reference images for {len(legacy_books)} legacy books:")
    for s in legacy_books:
        print(f"  - {s}")

    config = load_config()
    print(f"\nUsing API: {config.site}")

    REFS_DIR.mkdir(parents=True, exist_ok=True)

    success = 0
    for slug in legacy_books:
        print(f"\n[{slug}]")
        if generate_reference(slug, config):
            success += 1

    print(f"\n\nDone! Generated {success}/{len(legacy_books)} reference images.")


if __name__ == "__main__":
    main()
