#!/usr/bin/env python3
"""Regenerate specific word icons with improved prompts."""

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
GRIDS_DIR = OUTPUT_DIR / "grids-redo"

# Better hints for tricky words
BETTER_HINTS = {
    'bat': 'baseball bat or flying bat animal',
    'bed': 'cozy bed with pillow and blanket',
    'fox': 'orange fox with bushy tail',
    'net': 'fishing net or butterfly net',
    'mat': 'welcome mat or yoga mat',
    'sat': 'person sitting on chair',
    'hug': 'two people hugging',
    'hit': 'baseball player hitting ball',
    'sit': 'person sitting down',
    'trip': 'person with suitcase traveling',
    'snap': 'fingers snapping',
    'skip': 'child skipping happily',
    'step': 'footstep or stair step',
    'fell': 'person falling down',
    'wall': 'brick wall',
    'slip': 'person slipping on banana peel',
    'chin': 'face showing chin',
    'chop': 'chef chopping vegetables',
    'math': 'chalkboard with 1+2=3',
    'game': 'board game or video game controller',
    'hike': 'person hiking with backpack in mountains',
    'car': 'red car driving',
    'star': 'yellow star shape',
    'jar': 'glass jar with lid',
    'barn': 'red barn on farm',
    'card': 'greeting card or playing card',
    'park': 'playground in park with trees',
    'dark': 'dark night sky with moon',
    'turn': 'arrow turning or person turning around',
    'day': 'bright sunny day',
    'feet': 'pair of feet',
    'stay': 'dog staying sitting',
    'snow': 'snowflakes falling',
    'loud': 'speaker with sound waves',
    'join': 'puzzle pieces joining together',
    'toy': 'teddy bear toy',
    'joy': 'happy jumping person',
    'show': 'person showing something proudly',
    'town': 'small town with houses',
    'brown': 'brown teddy bear',
    'play': 'children playing',
    'say': 'person talking with speech bubble',
    'tail': 'dog wagging tail',
    'see': 'eye looking',
    'hope': 'person looking up at rainbow',
    'like': 'thumbs up',
    'bike': 'bicycle',
    'time': 'clock showing time',
    'dime': 'silver coin',
    'make': 'hands making crafts',
    'wing': 'bird wing',
    'chip': 'potato chip snack',
    'shut': 'closed door',
    'wish': 'child blowing dandelion',
    'kiss': 'lips or heart',
    'miss': 'person missing target with arrow',
    'tell': 'person telling story',
    'well': 'water well with bucket',
    'sell': 'person at shop selling',
    'hill': 'green grassy hill',
    'fill': 'glass being filled with water',
    'will': 'strong person flexing (willpower)',
    'pull': 'person pulling rope',
    'fall': 'autumn leaves falling',
    'fun': 'kids having fun on playground',
    'run': 'person running fast',
    'mop': 'mop cleaning floor',
    'hop': 'bunny hopping',
    'ran': 'person who just ran (motion lines)',
    'can': 'tin can',
    'rat': 'gray rat',
    'pot': 'cooking pot',
    'sun': 'bright yellow sun with rays',
    'dog': 'happy dog with tongue out',
}

# Words to regenerate
WORDS_TO_REDO = list(BETTER_HINTS.keys())


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
    grid_path = GRIDS_DIR / f"redo_grid_{batch_num:02d}.png"

    panels = []
    for i, word in enumerate(words[:9]):
        hint = BETTER_HINTS.get(word, word)
        panels.append(f"Panel {i+1}: {hint}")

    while len(panels) < 9:
        panels.append(f"Panel {len(panels)+1}: decorative star pattern")

    prompt = f"""9 cute cartoon icons arranged in a 3x3 layout on a plain cream background.

Icons (left to right, top to bottom):
{chr(10).join(panels)}

STYLE:
- Simple kawaii/emoji style icons
- Bold black outlines
- Bright flat colors
- Each icon FULLY VISIBLE and CENTERED in its area (not cut off!)
- Plain solid cream (#FFF8E7) background everywhere

CRITICAL:
- Each icon must be COMPLETE and not cropped or cut off at edges
- NO borders, frames, or lines of any kind
- NO text or letters anywhere
- Icons should be small enough to fit fully within each cell
- Leave padding around each icon"""

    print(f"  Generating grid {batch_num} with words: {words[:9]}")

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
                print(f"  Split into {saved} individual icons")
                return True
        else:
            print(f"  Failed: {result.error}")

    return False


def main():
    print(f"Regenerating {len(WORDS_TO_REDO)} icons\n")

    config = load_config()
    print(f"Using API: {config.site}\n")

    GRIDS_DIR.mkdir(parents=True, exist_ok=True)

    # Calculate batches
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
