#!/usr/bin/env python3
"""Generate book images using story bible approach.

Simple, consistent prompts with the same style suffix on every image.
"""

import json
import time
import requests
from pathlib import Path

BOOKS_DIR = Path("/Users/dereklomas/lilbookies/public/books")
API_URL = "https://funbookies.com/api"

# The consistent style block - same for EVERY image
STYLE_BLOCK = """
STYLE: Simple flat illustration like Dick Bruna (Miffy) or Mo Willems.
- Thick black outlines around everything
- Flat solid colors, no gradients
- Simple round shapes
- Clean simple background (grass and sky)

CRITICAL: NO TEXT, NO WORDS, NO LETTERS anywhere in the image."""

# Character description - short and consistent
FERN_DESC = "Fern (a small round brown mouse with big ears, cream tummy, curly tail)"


def build_simple_prompt(page_num: int, text: str) -> str:
    """Build a simple, focused prompt for each page."""

    # Map page text to simple scene descriptions
    scenes = {
        1: f"COVER: {FERN_DESC} standing on a grassy hill with colorful leaves swirling around her in the wind. She looks happy and curious.",
        3: f"{FERN_DESC} sitting peacefully on green grass under a yellow sun. Blue sky. She looks content with eyes half-closed.",
        4: f"{FERN_DESC} looking surprised as the grass around her bends and sways. Motion lines show wind. Leaves starting to fly.",
        5: f"Close-up of {FERN_DESC} looking around confused, head tilted, wondering what made the wind.",
        6: f"{FERN_DESC} with an orange leaf stuck on her face! She looks startled. Wind motion lines around her.",
        7: f"{FERN_DESC} holding the leaf, looking around searching for something invisible.",
        8: f"{FERN_DESC} being puffed by wind from different directions. Her fur is ruffled. Motion lines everywhere.",
        9: f"{FERN_DESC} running across the grass, legs moving fast. Wind effects behind her.",
        10: f"Wide shot: {FERN_DESC} small in the frame, running across a big grassy hill. Leaves flying.",
        11: f"{FERN_DESC} spinning and tumbling, dizzy from the wind. Spiral motion lines. Leaves swirling.",
        12: f"{FERN_DESC} sitting on the grass looking dizzy. Spiral eyes or wobbly expression. Stars around head.",
        13: f"{FERN_DESC} sitting up, looking around with a questioning expression. Calm scene.",
        14: f"Quiet scene: {FERN_DESC} small on the grass. Everything still. No wind. Peaceful.",
        15: f"{FERN_DESC} with just a gentle breeze ruffling her fur softly. She notices something.",
        16: f"Close-up of {FERN_DESC} with a big happy grin. Eyes bright and joyful.",
        17: f"{FERN_DESC} pointing at the air with confidence, smiling. A gentle swirl of leaves nearby.",
        18: f"{FERN_DESC} playing joyfully with the wind. Leaves dancing around her. She's jumping or spinning happily.",
        19: f"{FERN_DESC} mid-jump with arms up, huge smile, having fun. Leaves and wind effects around her.",
        20: f"{FERN_DESC} sitting peacefully on the grass at sunset. Warm orange and pink sky. Content expression.",
        21: f"Close-up of {FERN_DESC} with a gentle, knowing smile. A soft breeze ruffles her fur.",
        22: f"{FERN_DESC} with eyes closed, peaceful smile, as a gentle wind swirls around her lovingly.",
        23: f"A gentle spiral of leaves and wind circling around {FERN_DESC} like a hug. She smiles.",
        24: f"FINAL: {FERN_DESC} on her hill at sunset. Warm colors. Peaceful. Leaves gently floating. Happy ending."
    }

    scene = scenes.get(page_num)
    if not scene:
        return None

    return f"{scene}\n{STYLE_BLOCK}"


def generate_image(prompt: str, slug: str, page_num: int) -> str:
    """Generate an image."""

    print(f"  Page {page_num}: Generating...")

    response = requests.post(f"{API_URL}/generate-image", json={
        "prompt": prompt,
        "model": "nano-banana-pro",
        "slug": slug,
        "page": page_num
    }, timeout=30)

    result = response.json()

    if not result.get("success"):
        print(f"    Error: {result.get('error')}")
        return None

    if result.get("pending"):
        task_id = result["taskId"]
        endpoint = result["statusEndpoint"]

        for i in range(40):
            time.sleep(5)
            try:
                status_resp = requests.get(f"{API_URL}/check-status", params={
                    "taskId": task_id,
                    "endpoint": endpoint
                }, timeout=30)
                status = status_resp.json()

                if status.get("completed"):
                    print(f"    Done!")
                    return status["url"]

                if not status.get("success") and status.get("error"):
                    print(f"    Error: {status.get('error')}")
                    return None

            except Exception as e:
                print(f"    Network error, retrying...")
                time.sleep(5)

        print("    Timeout!")
        return None

    return result.get("url")


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("slug", help="Book slug")
    parser.add_argument("--pages", help="Specific pages (comma-separated)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    book_file = BOOKS_DIR / f"{args.slug}.json"
    with open(book_file) as f:
        book = json.load(f)

    # Determine which pages to process
    if args.pages:
        page_nums = [int(p) for p in args.pages.split(",")]
    else:
        page_nums = [p["page"] for p in book["pages"]]

    print(f"Generating {len(page_nums)} pages for {args.slug}\n")

    generated = 0
    for page in book["pages"]:
        page_num = page["page"]

        if page_num not in page_nums:
            continue

        # Build prompt
        prompt = build_simple_prompt(page_num, page.get("text", ""))

        if not prompt:
            print(f"  Page {page_num}: Skipping (no scene defined)")
            continue

        if args.dry_run:
            print(f"\n=== Page {page_num} ===")
            print(prompt)
            continue

        # Generate
        url = generate_image(prompt, args.slug, page_num)

        if url:
            page["image"] = url
            page["image_prompt"] = prompt
            generated += 1

            # Save after each
            with open(book_file, 'w') as f:
                json.dump(book, f, indent=2)

        time.sleep(2)

    if not args.dry_run:
        print(f"\nDone! Generated {generated} images.")


if __name__ == "__main__":
    main()
