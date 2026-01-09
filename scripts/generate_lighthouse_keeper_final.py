#!/usr/bin/env python3
"""Generate all Lighthouse Keeper pages with spatial consistency."""

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
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return f"data:image/png;base64,{b64}"


def download_image(url: str, output_path: Path) -> bool:
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(url, output_path)
        return True
    except Exception as e:
        print(f"      Error: {e}")
        return False


def generate_page(page_num: int, scene: str, page_type: str, ref_uri: str, prev_scenes: list, config) -> Path | None:
    """Generate a single page with concise prompt."""

    if page_type == "cover":
        output_path = COVERS_DIR / "d1-the-lighthouse-keeper.png"
    else:
        output_path = PAGES_DIR / f"d1-the-lighthouse-keeper_page{str(page_num).zfill(2)}.png"

    # Concise prompt under 2000 chars
    prev_context = ""
    if prev_scenes and len(prev_scenes) <= 2:
        prev_context = f"\nPrevious: {prev_scenes[-1][:60]}"

    prompt = f"""ONE illustration for children's book. No grid.

Scene: {scene}

Style: Coastal watercolor, atmospheric, muted blues and sunset oranges.

GEOGRAPHY (consistent): Lighthouse on cliff, cottage below-left, stone path connects them.

Characters from reference:
- Maya: girl, brown hair, orange shirt, blue overalls
- Grandmother: gray bun, purple dress, rocking chair
- Mr. Chen: captain hat, blue coat
{prev_context}
Reference = style guide. Match characters exactly. Maintain spatial layout for exteriors.

NO text/words. Single illustration only."""

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
            if download_image(result.results[0], output_path):
                return output_path
        else:
            print(f"      Failed: {result.error}")

    return None


def main():
    print("=" * 60)
    print("THE LIGHTHOUSE KEEPER - Final Generation")
    print("=" * 60)

    # Load book
    with open(BOOKS_DIR / "d1-the-lighthouse-keeper.json") as f:
        book = json.load(f)

    # Use v3 reference (with spatial layout)
    ref_path = REFS_DIR / "d1-the-lighthouse-keeper_reference_v3.png"
    print(f"Reference: {ref_path.name}")
    ref_uri = image_to_base64_uri(ref_path)

    # Get all pages with scenes
    pages = [p for p in book["pages"] if p.get("scene")]
    print(f"Pages to generate: {len(pages)}")

    config = load_config()

    prev_scenes = []
    generated = []

    for page in pages:
        page_num = page["page"]
        scene = page["scene"]
        page_type = page.get("type", "story")

        print(f"\n[PAGE {page_num}] {scene[:50]}...")

        result = generate_page(
            page_num=page_num,
            scene=scene,
            page_type=page_type,
            ref_uri=ref_uri,
            prev_scenes=prev_scenes,
            config=config
        )

        if result:
            print(f"    ✓ {result.name}")
            generated.append(result)
            prev_scenes.append(scene)
        else:
            print(f"    ✗ Failed")

    print("\n" + "=" * 60)
    print(f"COMPLETE: {len(generated)}/{len(pages)} pages")
    print("=" * 60)


if __name__ == "__main__":
    main()
