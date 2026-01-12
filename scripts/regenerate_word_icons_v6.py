#!/usr/bin/env python3
"""Regenerate specific word icons - round 6. People and hands."""

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
GRIDS_DIR = OUTPUT_DIR / "grids-redo6"

# People and hands for action words
WORDS_V6 = {
    'snap': 'cartoon hand snapping fingers with sparks',
    'skip': 'happy girl skipping with pigtails',
    'fell': 'boy who fell down sitting on ground',
    'this': 'hand pointing finger down',
    'that': 'hand pointing finger to the side',
    'then': 'person looking at clock on wall',
    'out': 'child climbing out of cardboard box',
    'show': 'child doing show and tell with teddy bear',
    'brown': 'girl holding brown teddy bear',
    'will': 'strong boy flexing arm muscles',
    'day': 'child playing outside in sunshine',
    'for': 'child giving wrapped gift to friend',
    'mop': 'person mopping floor with mop',
}

WORDS_TO_REDO = list(WORDS_V6.keys())


def download_image(url: str, output_path: Path) -> bool:
    try:
        urllib.request.urlretrieve(url, output_path)
        return True
    except Exception as e:
        print(f"    Error downloading: {e}")
        return False


def is_content_pixel(r, g, b):
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


def extract_and_center(img, target_size=300, padding=40):
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

    content_rgba = content.convert('RGBA')
    pixels = content_rgba.load()
    for y in range(ch):
        for x in range(cw):
            r, g, b, a = pixels[x, y]
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
        centered = extract_and_center(cell, target_size=300, padding=40)

        output_path = OUTPUT_DIR / f"{word}.png"
        centered.save(output_path)
        saved += 1
        print(f"    {word}.png")

    return saved


def generate_grid(batch_num: int, words: list, config) -> bool:
    grid_path = GRIDS_DIR / f"redo6_grid_{batch_num:02d}.png"

    panels = []
    for i, word in enumerate(words[:9]):
        hint = WORDS_V6.get(word, word)
        panels.append(f"Panel {i+1}: {hint}")

    while len(panels) < 9:
        panels.append(f"Panel {len(panels)+1}: cute star")

    prompt = f"""9 cute cartoon characters/hands in a 3x3 grid on pure WHITE background.

The 9 icons:
{chr(10).join(panels)}

STYLE:
- Pure WHITE background only
- Each icon SMALL (40% of cell) and CENTERED
- Kawaii chibi style characters with big heads
- Bold black outlines, bright colors
- NO text or letters
- Nothing cut off - full body/hand visible
- NO borders or frames"""

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
    print(f"Regenerating {len(WORDS_TO_REDO)} icons (round 6)\n")

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
