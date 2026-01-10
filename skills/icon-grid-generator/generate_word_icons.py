#!/usr/bin/env python3
"""Generate simple icon images for Word Builder activity.

Generates 9 icons at a time in a 3x3 grid, then splits them into individual files.
This is much more efficient than generating 189 separate images.
"""

import sys
import re
import urllib.request
from pathlib import Path
from time import sleep
from PIL import Image
import io

# Add the skill directory to path
SKILL_DIR = Path("/Users/dereklomas/.claude/plugins/cache/mulerouter-skills/mulerouter-skills/1.0.0/skills/mulerouter-skills")
sys.path.insert(0, str(SKILL_DIR))

from dotenv import load_dotenv
load_dotenv(SKILL_DIR / ".env")

from core import APIClient, load_config, create_and_poll_task

OUTPUT_DIR = Path("/Users/dereklomas/lilbookies/public/activities/word-icons")
GRIDS_DIR = OUTPUT_DIR / "grids"


def extract_words_from_html():
    """Extract all unique words from word-builder.html."""
    html_path = Path("/Users/dereklomas/lilbookies/public/activities/word-builder.html")

    with open(html_path) as f:
        content = f.read()

    # Find all word entries: { word: 'cat', image: '...', hint: '...' }
    pattern = r"\{\s*word:\s*'([^']+)',\s*image:\s*'[^']*',\s*hint:\s*'([^']+)'"
    matches = re.findall(pattern, content)

    # Deduplicate while preserving order
    seen = set()
    words = []
    for word, hint in matches:
        if word not in seen:
            seen.add(word)
            words.append({"word": word, "hint": hint})

    return words


def download_image(url: str, output_path: Path) -> bool:
    """Download image from URL."""
    try:
        urllib.request.urlretrieve(url, output_path)
        return True
    except Exception as e:
        print(f"    Error downloading: {e}")
        return False


def is_content_pixel(r, g, b):
    """Check if pixel is part of content (not plain background)."""
    is_cream = r > 230 and g > 220 and b > 200 and abs(r-g) < 30 and abs(g-b) < 30
    return not is_cream


def find_largest_blob(img):
    """Find the largest connected component of content pixels."""
    from collections import deque

    if img.mode != 'RGB':
        img = img.convert('RGB')
    pixels = img.load()
    w, h = img.size

    visited = [[False]*h for _ in range(w)]
    largest_blob = []

    def bfs(start_x, start_y):
        blob = []
        queue = deque([(start_x, start_y)])
        while queue:
            x, y = queue.popleft()
            if x < 0 or x >= w or y < 0 or y >= h:
                continue
            if visited[x][y]:
                continue
            r, g, b = pixels[x, y]
            if not is_content_pixel(r, g, b):
                continue
            visited[x][y] = True
            blob.append((x, y))
            queue.extend([(x+1,y), (x-1,y), (x,y+1), (x,y-1)])
        return blob

    for y in range(h):
        for x in range(w):
            if not visited[x][y]:
                r, g, b = pixels[x, y]
                if is_content_pixel(r, g, b):
                    blob = bfs(x, y)
                    if len(blob) > len(largest_blob):
                        largest_blob = blob

    return largest_blob


def get_visual_center_of_blob(img, blob):
    """Get visual center weighted by color intensity within blob."""
    if img.mode != 'RGB':
        img = img.convert('RGB')
    pixels = img.load()

    bg_r, bg_g, bg_b = 250, 245, 230
    sum_x, sum_y, sum_weight = 0, 0, 0

    for x, y in blob:
        r, g, b = pixels[x, y]
        diff = abs(r - bg_r) + abs(g - bg_g) + abs(b - bg_b)
        sum_x += x * diff
        sum_y += y * diff
        sum_weight += diff

    if sum_weight == 0:
        xs = [p[0] for p in blob]
        ys = [p[1] for p in blob]
        return (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2

    return sum_x / sum_weight, sum_y / sum_weight


def extract_and_center(img, target_size=300, padding=30):
    """Find largest blob, extract it, center using visual center, transparent bg."""
    blob = find_largest_blob(img)

    if not blob:
        return img

    xs = [p[0] for p in blob]
    ys = [p[1] for p in blob]

    w, h = img.size
    margin = 8
    left = max(0, min(xs) - margin)
    top = max(0, min(ys) - margin)
    right = min(w, max(xs) + margin)
    bottom = min(h, max(ys) + margin)

    content = img.crop((left, top, right, bottom))
    cw, ch = content.size

    # Convert to RGBA and make background transparent
    content_rgba = content.convert('RGBA')
    pixels = content_rgba.load()
    for y in range(ch):
        for x in range(cw):
            r, g, b, a = pixels[x, y]
            is_bg = r > 230 and g > 220 and b > 200 and abs(r-g) < 30 and abs(g-b) < 30
            if is_bg:
                pixels[x, y] = (r, g, b, 0)

    # Get visual center relative to cropped image
    vc_x, vc_y = get_visual_center_of_blob(img, blob)
    vc_x -= left
    vc_y -= top

    available = target_size - (padding * 2)
    scale = min(available / cw, available / ch, 1.0)

    if scale < 1:
        new_w = int(cw * scale)
        new_h = int(ch * scale)
        content_rgba = content_rgba.resize((new_w, new_h), Image.LANCZOS)
        vc_x *= scale
        vc_y *= scale
        cw, ch = new_w, new_h

    # Transparent background
    new_img = Image.new('RGBA', (target_size, target_size), (0, 0, 0, 0))

    # Position so visual center is at target center
    target_center = target_size // 2
    paste_x = int(target_center - vc_x)
    paste_y = int(target_center - vc_y)

    new_img.paste(content_rgba, (paste_x, paste_y), content_rgba)

    return new_img


def split_grid_image(grid_path: Path, words: list) -> int:
    """Split a 3x3 grid image into 9 individual centered icons."""
    img = Image.open(grid_path)
    w, h = img.size
    cell_w, cell_h = w // 3, h // 3

    saved = 0
    for i, entry in enumerate(words[:9]):
        row, col = i // 3, i % 3
        left = col * cell_w
        top = row * cell_h
        right = left + cell_w
        bottom = top + cell_h

        cell = img.crop((left, top, right, bottom))
        centered = extract_and_center(cell, target_size=300, padding=30)

        output_path = OUTPUT_DIR / f"{entry['word']}.png"
        centered.save(output_path)
        saved += 1
        print(f"    {entry['word']}.png")

    return saved


def generate_grid(batch_num: int, words: list, config) -> bool:
    """Generate a 3x3 grid of 9 word icons."""

    grid_path = GRIDS_DIR / f"grid_{batch_num:02d}.png"

    # Build panel descriptions
    panels = []
    for i, entry in enumerate(words[:9]):
        panels.append(f"Panel {i+1}: {entry['word']} - {entry['hint']}")

    # Pad to 9 if needed
    while len(panels) < 9:
        panels.append(f"Panel {len(panels)+1}: decorative pattern")

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

    print(f"  Generating grid {batch_num} with words: {[w['word'] for w in words[:9]]}")

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
            print(f"  Downloaded grid: {url}")
            if download_image(url, grid_path):
                # Split into individual icons
                saved = split_grid_image(grid_path, words)
                print(f"  Split into {saved} individual icons")
                return True
        else:
            print(f"  Failed: {result.error}")

    return False


def main():
    # Extract words
    words = extract_words_from_html()
    print(f"Found {len(words)} unique words\n")

    # Load config
    config = load_config()
    print(f"Using API: {config.site}\n")

    # Ensure output dirs exist
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    GRIDS_DIR.mkdir(parents=True, exist_ok=True)

    # Check what already exists
    existing = set(p.stem for p in OUTPUT_DIR.glob("*.png"))
    remaining = [w for w in words if w["word"] not in existing]

    print(f"Already have {len(existing)} icons, {len(remaining)} remaining")

    if not remaining:
        print("All icons already generated!")
        return

    # Calculate batches (9 per grid)
    num_batches = (len(remaining) + 8) // 9
    print(f"Will generate {num_batches} grids (9 icons each)\n")

    # Generate grids
    success = 0
    for batch_num in range(num_batches):
        start = batch_num * 9
        batch_words = remaining[start:start+9]

        print(f"\n[Grid {batch_num+1}/{num_batches}]")
        if generate_grid(batch_num + 1, batch_words, config):
            success += 1

        # Delay between requests
        if batch_num < num_batches - 1:
            sleep(2)

    print(f"\n\nDone! Generated {success}/{num_batches} grids.")
    print(f"Total icons now: {len(list(OUTPUT_DIR.glob('*.png')))}")


if __name__ == "__main__":
    main()
