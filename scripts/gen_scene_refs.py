#!/usr/bin/env python3
"""Generate scene-split reference images for a book using I2I from base.

Run from the mulerouter-skills directory:
cd ~/.claude/plugins/cache/mulerouter-skills/mulerouter-skills/1.0.0/skills/mulerouter-skills
uv run python /path/to/gen_scene_refs.py mud-pup-fun
"""

import sys
import os
import json
import base64
import urllib.request
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path("/Users/dereklomas/lilbookies")
REFS_DIR = PROJECT_ROOT / "public/books/references"

# Import from current directory (should be mulerouter-skills)
from dotenv import load_dotenv
load_dotenv()

from core.config import load_config
from core.client import APIClient
from core.task import create_and_poll_task


def generate_scene_refs(slug: str, base_path: Path, book_info: dict):
    """Generate scenes_part1 and scenes_part2 using I2I from base reference."""

    config = load_config()
    multi_dir = REFS_DIR / f"{slug}_multi"

    # Load base image as base64
    print(f"Loading base reference: {base_path}")
    with open(base_path, "rb") as f:
        base64_img = base64.b64encode(f.read()).decode("utf-8")
    print(f"Base64 length: {len(base64_img)} chars")

    # Get scenes from book
    scenes = []
    for page in book_info.get("pages", []):
        if page.get("type") == "story" and page.get("scene"):
            scenes.append(page["scene"])

    mid = len(scenes) // 2
    part1_scenes = scenes[:mid]
    part2_scenes = scenes[mid:]

    print(f"Book has {len(scenes)} scenes")
    print(f"Part 1: scenes 1-{mid}")
    print(f"Part 2: scenes {mid+1}-{len(scenes)}")

    # Build prompts
    part1_prompt = f"""9-PANEL SCENES REFERENCE - PART 1 (First Half of Story)

Using the style from the reference image, create a 3x3 grid showing scenes from the FIRST HALF of the story.

Row 1:
[1] {part1_scenes[0] if len(part1_scenes) > 0 else "Opening scene"}
[2] {part1_scenes[1] if len(part1_scenes) > 1 else "Scene 2"}
[3] {part1_scenes[2] if len(part1_scenes) > 2 else "Scene 3"}

Row 2:
[4] {part1_scenes[3] if len(part1_scenes) > 3 else "Scene 4"}
[5] {part1_scenes[4] if len(part1_scenes) > 4 else "Scene 5"}
[6] {part1_scenes[5] if len(part1_scenes) > 5 else "Scene 6"}

Row 3 - Key moments from first half:
[7] Establishing shot of main setting
[8] Character interaction moment
[9] Transition scene leading to second half

STYLE: Match the watercolor style from the reference image exactly.
Warm cheerful colors, soft edges, child-friendly art.
NO TEXT, NO WORDS, NO LETTERS anywhere."""

    part2_prompt = f"""9-PANEL SCENES REFERENCE - PART 2 (Second Half of Story)

Using the style from the reference image, create a 3x3 grid showing scenes from the SECOND HALF of the story.

Row 1:
[1] {part2_scenes[0] if len(part2_scenes) > 0 else "Scene 7"}
[2] {part2_scenes[1] if len(part2_scenes) > 1 else "Scene 8"}
[3] {part2_scenes[2] if len(part2_scenes) > 2 else "Scene 9"}

Row 2:
[4] {part2_scenes[3] if len(part2_scenes) > 3 else "Scene 10"}
[5] {part2_scenes[4] if len(part2_scenes) > 4 else "Scene 11"}
[6] {part2_scenes[5] if len(part2_scenes) > 5 else "Scene 12"}

Row 3 - Key moments from second half:
[7] Climax scene
[8] Resolution moment
[9] Final happy ending

STYLE: Match the watercolor style from the reference image exactly.
Warm cheerful colors, soft edges, child-friendly art.
NO TEXT, NO WORDS, NO LETTERS anywhere."""

    results = {}

    with APIClient(config) as client:
        for part_name, prompt in [("scenes_part1", part1_prompt), ("scenes_part2", part2_prompt)]:
            print(f"\n{'='*60}")
            print(f"Generating {part_name}...")
            print(f"Prompt preview: {prompt[:200]}...")

            body = {
                "prompt": prompt,
                "images": [f"data:image/png;base64,{base64_img}"],
                "size": "1024*1024",
                "n": 1
            }

            result = create_and_poll_task(
                client=client,
                endpoint_path="/vendors/alibaba/v1/wan2.6-image/generation",
                request_body=body,
                result_key="images",
                interval=5.0,
                max_wait=300.0,
                verbose=True
            )

            if result.results:
                url = result.results[0]
                output_path = multi_dir / f"{slug}_{part_name}.png"
                print(f"Downloading to {output_path}...")
                urllib.request.urlretrieve(url, output_path)
                print(f"Saved: {output_path.name}")
                results[part_name] = {
                    "path": str(output_path.relative_to(REFS_DIR.parent.parent)),
                    "prompt": prompt,
                    "model": "wan2.6-image",
                    "reference": "base",
                    "generated_at": datetime.now().isoformat()
                }
            else:
                print(f"Failed: {result.error}")

    return results


if __name__ == "__main__":
    slug = sys.argv[1] if len(sys.argv) > 1 else "mud-pup-fun"

    book_path = PROJECT_ROOT / f"public/books/{slug}.json"
    base_path = REFS_DIR / f"{slug}_multi/{slug}_base.png"

    if not book_path.exists():
        print(f"Book not found: {book_path}")
        sys.exit(1)

    if not base_path.exists():
        print(f"Base reference not found: {base_path}")
        print("Generate base reference first with nano-banana-pro")
        sys.exit(1)

    with open(book_path) as f:
        book_info = json.load(f)

    print(f"Generating scene references for: {book_info.get('title', slug)}")
    results = generate_scene_refs(slug, base_path, book_info)

    print(f"\n{'='*60}")
    print(f"Generated {len(results)} scene references")
    for name, data in results.items():
        print(f"  - {name}: {data['path']}")
