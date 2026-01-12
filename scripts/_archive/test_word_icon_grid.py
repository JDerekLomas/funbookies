#!/usr/bin/env python3
"""Test generating a single word icon grid."""

import sys
import urllib.request
from pathlib import Path
from PIL import Image

SKILL_DIR = Path("/Users/dereklomas/.claude/plugins/cache/mulerouter-skills/mulerouter-skills/1.0.0/skills/mulerouter-skills")
sys.path.insert(0, str(SKILL_DIR))

from dotenv import load_dotenv
load_dotenv(SKILL_DIR / ".env")

from core import APIClient, load_config, create_and_poll_task

OUTPUT_DIR = Path("/Users/dereklomas/lilbookies/public/activities/word-icons/test")

# Test words
TEST_WORDS = [
    {"word": "cat", "hint": "furry pet that meows"},
    {"word": "dog", "hint": "pet that barks"},
    {"word": "sun", "hint": "bright in the sky"},
    {"word": "hat", "hint": "wear on your head"},
    {"word": "cup", "hint": "drink from it"},
    {"word": "bed", "hint": "sleep on it"},
    {"word": "pig", "hint": "pink farm animal"},
    {"word": "bus", "hint": "big yellow vehicle"},
    {"word": "fox", "hint": "orange animal"},
]


def download_image(url: str, output_path: Path) -> bool:
    try:
        urllib.request.urlretrieve(url, output_path)
        return True
    except Exception as e:
        print(f"Error downloading: {e}")
        return False


def get_content_bbox(img, bg_threshold=240):
    """Find bounding box of non-background content."""
    # Convert to RGB if needed
    if img.mode != 'RGB':
        img = img.convert('RGB')

    pixels = img.load()
    w, h = img.size

    min_x, min_y = w, h
    max_x, max_y = 0, 0

    for y in range(h):
        for x in range(w):
            r, g, b = pixels[x, y]
            # Check if pixel is NOT background (not light colored)
            if r < bg_threshold or g < bg_threshold or b < bg_threshold:
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)

    if max_x < min_x:  # No content found
        return None

    return (min_x, min_y, max_x + 1, max_y + 1)


def center_content(img, target_size=341, padding=20):
    """Center the content of an image."""
    # Get the bounding box of actual content
    bbox = get_content_bbox(img)
    if not bbox:
        return img

    # Crop to content
    content = img.crop(bbox)
    cw, ch = content.size

    # Calculate scale to fit in target with padding
    available = target_size - (padding * 2)
    scale = min(available / cw, available / ch)

    if scale < 1:
        # Need to shrink
        new_w = int(cw * scale)
        new_h = int(ch * scale)
        content = content.resize((new_w, new_h), Image.LANCZOS)
        cw, ch = new_w, new_h

    # Create new image with background color (sample from corner of original)
    bg_color = img.getpixel((5, 5))
    new_img = Image.new('RGB', (target_size, target_size), bg_color)

    # Center the content
    x = (target_size - cw) // 2
    y = (target_size - ch) // 2
    new_img.paste(content, (x, y))

    return new_img


def split_grid_image(grid_path: Path, words: list) -> int:
    """Split a 3x3 grid image into 9 individual icons."""
    img = Image.open(grid_path)
    w, h = img.size
    cell_w, cell_h = w // 3, h // 3

    print(f"Grid size: {w}x{h}, cell size: {cell_w}x{cell_h}")

    saved = 0
    for i, entry in enumerate(words[:9]):
        row, col = i // 3, i % 3
        left = col * cell_w
        top = row * cell_h
        right = left + cell_w
        bottom = top + cell_h

        cell = img.crop((left, top, right, bottom))

        # Center the content
        cell = center_content(cell, target_size=cell_w, padding=15)

        output_path = OUTPUT_DIR / f"{entry['word']}.png"
        cell.save(output_path)
        saved += 1
        print(f"  Saved: {entry['word']}.png (centered)")

    return saved


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Build panel descriptions
    panels = []
    for i, entry in enumerate(TEST_WORDS):
        panels.append(f"Panel {i+1}: A cute cartoon {entry['word']} ({entry['hint']})")

    prompt = f"""9 cute cartoon icons arranged in a 3x3 layout on a plain cream background.

Icons (left to right, top to bottom):
{chr(10).join(panels)}

STYLE:
- Simple kawaii/emoji style icons
- Bold black outlines
- Bright flat colors
- Each icon is small and centered in its area
- Plain solid cream (#FFF8E7) background everywhere

CRITICAL:
- NO borders, frames, or lines of any kind
- NO decorative elements between icons
- NO grid lines or separators
- Just 9 simple icons floating on a plain cream background
- Background must be completely plain and uniform
- NO text"""

    print("Generating test grid...")
    print(f"Prompt:\n{prompt}\n")

    config = load_config()

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
            print(f"Generated: {url}")
            grid_path = OUTPUT_DIR / "test_grid.png"
            if download_image(url, grid_path):
                print(f"Saved grid to: {grid_path}")
                print("\nSplitting grid...")
                saved = split_grid_image(grid_path, TEST_WORDS)
                print(f"\nSplit into {saved} individual icons")
                print(f"\nOpen to check: open {OUTPUT_DIR}")
        else:
            print(f"Failed: {result.error}")


if __name__ == "__main__":
    main()
