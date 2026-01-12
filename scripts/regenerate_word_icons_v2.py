#!/usr/bin/env python3
"""Regenerate specific word icons - round 2."""

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
GRIDS_DIR = OUTPUT_DIR / "grids-redo2"

# Very specific hints for tricky words
WORDS_V2 = {
    'bit': 'small piece of cookie with bite taken out',
    'got': 'happy child who just got a gift',
    'snap': 'hand snapping fingers with snap lines',
    'skip': 'girl skipping rope',
    'fell': 'person who fell down on ground',
    'slip': 'person slipping on wet floor sign',
    'chin': 'cartoon face pointing at chin',
    'thin': 'very thin stick figure person',
    'this': 'finger pointing down at something',
    'that': 'finger pointing away at something',
    'with': 'two friends standing together',
    'then': 'clock showing before and after',
    'them': 'group of three people',
    'game': 'colorful board game with dice',
    'name': 'hello my name is badge sticker',
    'came': 'person arriving through door',
    'far': 'tiny house far away in distance',
    'card': 'birthday card with heart',
    'for': 'gift box with for you tag',
    'dark': 'dark night scene with moon and stars',
    'turn': 'curved arrow turning right',
    'out': 'door with exit arrow pointing out',
    'show': 'magician showing magic trick',
    'soon': 'clock with arrow pointing forward',
    'down': 'red arrow pointing down',
    'brown': 'cute brown teddy bear',
    'play': 'kids playing on playground swing',
    'tail': 'happy dog with wagging tail',
    'make': 'hands making clay pottery',
    'wing': 'colorful butterfly wing',
    'wish': 'child blowing birthday candles making wish',
    'kiss': 'red lipstick kiss mark',
    'miss': 'arrow missing target bullseye',
    'full': 'full glass of orange juice',
    'tell': 'person whispering secret to friend',
    'will': 'superhero flexing strong muscles',
    'pull': 'child pulling wagon',
    'tall': 'tall giraffe next to short mouse',
    'big': 'big elephant',
    'pit': 'peach with pit seed showing',
    'hit': 'baseball bat hitting ball',
    'mop': 'mop and bucket cleaning',
    'well': 'stone water well with bucket',
    'day': 'bright sun in blue sky daytime',
    'stay': 'dog sitting and staying obediently',
    'loud': 'megaphone with sound waves',
    'moon': 'crescent moon with stars at night',
    'join': 'two puzzle pieces connecting together',
}

WORDS_TO_REDO = list(WORDS_V2.keys())


def download_image(url: str, output_path: Path) -> bool:
    try:
        urllib.request.urlretrieve(url, output_path)
        return True
    except Exception as e:
        print(f"    Error downloading: {e}")
        return False


def is_content_pixel(r, g, b):
    is_cream = r > 230 and g > 220 and b > 200 and abs(r-g) < 30 and abs(g-b) < 30
    return not is_cream


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


def extract_and_center(img, target_size=300, padding=30):
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

    content_rgba = content.convert('RGBA')
    pixels = content_rgba.load()
    for y in range(ch):
        for x in range(cw):
            r, g, b, a = pixels[x, y]
            is_bg = r > 230 and g > 220 and b > 200 and abs(r-g) < 30 and abs(g-b) < 30
            if is_bg:
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
        centered = extract_and_center(cell, target_size=300, padding=30)

        output_path = OUTPUT_DIR / f"{word}.png"
        centered.save(output_path)
        saved += 1
        print(f"    {word}.png")

    return saved


def generate_grid(batch_num: int, words: list, config) -> bool:
    grid_path = GRIDS_DIR / f"redo2_grid_{batch_num:02d}.png"

    panels = []
    for i, word in enumerate(words[:9]):
        hint = WORDS_V2.get(word, word)
        panels.append(f"Panel {i+1}: {hint}")

    while len(panels) < 9:
        panels.append(f"Panel {len(panels)+1}: cute rainbow")

    prompt = f"""Create a 3x3 grid image with 9 simple cartoon icons for children.

The 9 icons (row by row, left to right):
{chr(10).join(panels)}

CRITICAL RULES:
1. Each icon must be COMPLETE - nothing cut off at edges
2. Each icon should be SMALL and CENTERED with lots of padding around it
3. Plain cream/off-white background (#FFF8E7) - NO decorative borders
4. Simple kawaii style with bold black outlines
5. Bright cheerful colors
6. ABSOLUTELY NO TEXT OR LETTERS in any icon
7. Each icon clearly recognizable and distinct"""

    print(f"  Generating grid {batch_num}: {words[:9]}")

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
            print(f"  Downloaded grid")
            if download_image(url, grid_path):
                saved = split_grid_image(grid_path, words)
                print(f"  Split into {saved} icons")
                return True
        else:
            print(f"  Failed: {result.error}")

    return False


def main():
    print(f"Regenerating {len(WORDS_TO_REDO)} icons (round 2)\n")

    config = load_config()
    GRIDS_DIR.mkdir(parents=True, exist_ok=True)

    num_batches = (len(WORDS_TO_REDO) + 8) // 9
    print(f"Will generate {num_batches} grids\n")

    success = 0
    for batch_num in range(num_batches):
        start = batch_num * 9
        batch_words = WORDS_TO_REDO[start:start+9]

        print(f"\n[Grid {batch_num+1}/{num_batches}]")
        if generate_grid(batch_num + 1, batch_words, config):
            success += 1

        if batch_num < num_batches - 1:
            sleep(2)

    print(f"\n\nDone! Generated {success}/{num_batches} grids.")


if __name__ == "__main__":
    main()
