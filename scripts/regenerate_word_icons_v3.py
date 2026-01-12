#!/usr/bin/env python3
"""Regenerate specific word icons - round 3. Better transparency + no cutoff."""

import sys
import urllib.request
from pathlib import Path
from time import sleep
from PIL import Image
from collections import deque

SKILL_DIR = Path("/Users/dereklomas/.claude/plugins/cache/mulerouter-skills/mulerouter-skills/1.0.0/skills/mulerouter-skills")
sys.path.insert(0, str(SKILL_DIR))

from dotenv import load_dotenv
load_dotenv(SKILL_DIR / ".env")

from core import APIClient, load_config, create_and_poll_task

OUTPUT_DIR = Path("/Users/dereklomas/lilbookies/public/activities/word-icons")
GRIDS_DIR = OUTPUT_DIR / "grids-redo3"

# Very specific hints
WORDS_V3 = {
    'got': 'child receiving gift box happily',
    'snap': 'hand with fingers snapping sparkles',
    'skip': 'happy girl skipping with jump rope',
    'fell': 'cartoon person fallen on ground',
    'thin': 'very skinny stick figure',
    'this': 'hand pointing down here',
    'that': 'hand pointing over there',
    'then': 'number 1 then number 2 sequence',
    'them': 'group of three smiling people',
    'far': 'tiny house far in distance',
    'for': 'wrapped gift with bow',
    'out': 'open door with arrow going out',
    'show': 'magician with magic wand',
    'soon': 'hourglass timer',
    'brown': 'brown chocolate bar',
    'play': 'children on playground slide',
    'tail': 'cute dog showing fluffy tail',
    'wish': 'shooting star',
    'miss': 'dart missing dartboard',
    'will': 'flexing arm muscle',
    'pull': 'person pulling rope tug of war',
    'tall': 'tall giraffe',
    'big': 'big friendly elephant',
    'mop': 'mop with bucket',
    'stay': 'dog sitting staying',
    'moon': 'yellow crescent moon',
    'join': 'two puzzle pieces connecting',
    'pit': 'cherry with pit visible',
    'hit': 'baseball bat hitting ball',
    'bit': 'apple with bite mark',
    'loud': 'red megaphone with sound waves',
    'doll': 'cute rag doll toy',
    'drop': 'water droplet falling',
    'cat': 'cute orange cat face',
    'clap': 'two hands clapping',
    'well': 'stone wishing well with bucket',
    'king': 'golden crown',
    'ring': 'diamond ring jewelry',
    'bath': 'bathtub with bubbles',
    'path': 'winding forest path',
    'cake': 'birthday cake with candles',
    'sing': 'person singing with music notes',
    'mule': 'gray donkey mule',
    'day': 'bright yellow sun',
    'town': 'small town houses',
}

WORDS_TO_REDO = list(WORDS_V3.keys())


def download_image(url: str, output_path: Path) -> bool:
    try:
        urllib.request.urlretrieve(url, output_path)
        return True
    except Exception as e:
        print(f"    Error downloading: {e}")
        return False


def is_content_pixel(r, g, b):
    """More aggressive background detection."""
    # Cream/beige/white backgrounds
    is_light = r > 220 and g > 210 and b > 190
    is_neutral = abs(r - g) < 40 and abs(g - b) < 40
    is_bg = is_light and is_neutral
    return not is_bg


def find_largest_blob(img):
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
            if x < 0 or x >= w or y < 0 or y >= h or visited[x][y]:
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


def extract_and_center(img, target_size=300, padding=35):
    """Extract with better transparency."""
    blob = find_largest_blob(img)
    if not blob:
        return img

    xs = [p[0] for p in blob]
    ys = [p[1] for p in blob]

    w, h = img.size
    margin = 10
    left = max(0, min(xs) - margin)
    top = max(0, min(ys) - margin)
    right = min(w, max(xs) + margin)
    bottom = min(h, max(ys) + margin)

    content = img.crop((left, top, right, bottom))
    cw, ch = content.size

    # Convert to RGBA with better transparency detection
    content_rgba = content.convert('RGBA')
    pixels = content_rgba.load()
    for y in range(ch):
        for x in range(cw):
            r, g, b, a = pixels[x, y]
            # More aggressive: any light neutral color becomes transparent
            is_light = r > 220 and g > 210 and b > 190
            is_neutral = abs(r - g) < 40 and abs(g - b) < 40
            if is_light and is_neutral:
                pixels[x, y] = (r, g, b, 0)

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

    new_img = Image.new('RGBA', (target_size, target_size), (0, 0, 0, 0))
    target_center = target_size // 2
    paste_x = int(target_center - vc_x)
    paste_y = int(target_center - vc_y)
    new_img.paste(content_rgba, (paste_x, paste_y), content_rgba)

    return new_img


def split_grid_image(grid_path: Path, words: list) -> int:
    img = Image.open(grid_path)
    w, h = img.size
    cell_w, cell_h = w // 3, h // 3

    saved = 0
    for i, word in enumerate(words[:9]):
        row, col = i // 3, i % 3
        left = col * cell_w
        top = row * cell_h
        right = left + cell_w
        bottom = top + cell_h

        cell = img.crop((left, top, right, bottom))
        centered = extract_and_center(cell, target_size=300, padding=35)

        output_path = OUTPUT_DIR / f"{word}.png"
        centered.save(output_path)
        saved += 1
        print(f"    {word}.png")

    return saved


def generate_grid(batch_num: int, words: list, config) -> bool:
    grid_path = GRIDS_DIR / f"redo3_grid_{batch_num:02d}.png"

    panels = []
    for i, word in enumerate(words[:9]):
        hint = WORDS_V3.get(word, word)
        panels.append(f"Panel {i+1}: {hint}")

    while len(panels) < 9:
        panels.append(f"Panel {len(panels)+1}: cute rainbow")

    prompt = f"""Draw a 3x3 grid with 9 small cartoon icons on a plain WHITE background.

Icons (row by row):
{chr(10).join(panels)}

REQUIREMENTS:
- Pure WHITE background (#FFFFFF) - no cream, no beige, no texture
- Each icon must be SMALL (about 60% of cell size) and perfectly CENTERED
- Leave generous white space/padding around each icon
- Simple kawaii style with bold black outlines
- Bright solid colors
- NO text, labels, or letters anywhere
- Each icon must be COMPLETE - absolutely nothing cut off at edges
- NO decorative borders or frames"""

    print(f"  Grid {batch_num}: {words[:9]}")

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
            print(f"  Downloaded")
            if download_image(url, grid_path):
                saved = split_grid_image(grid_path, words)
                print(f"  Split: {saved} icons")
                return True
        else:
            print(f"  Failed: {result.error}")

    return False


def main():
    print(f"Regenerating {len(WORDS_TO_REDO)} icons (round 3)\n")

    config = load_config()
    GRIDS_DIR.mkdir(parents=True, exist_ok=True)

    num_batches = (len(WORDS_TO_REDO) + 8) // 9
    print(f"Generating {num_batches} grids\n")

    success = 0
    for batch_num in range(num_batches):
        start = batch_num * 9
        batch_words = WORDS_TO_REDO[start:start+9]

        print(f"\n[Grid {batch_num+1}/{num_batches}]")
        if generate_grid(batch_num + 1, batch_words, config):
            success += 1

        if batch_num < num_batches - 1:
            sleep(2)

    print(f"\n\nDone! {success}/{num_batches} grids.")


if __name__ == "__main__":
    main()
