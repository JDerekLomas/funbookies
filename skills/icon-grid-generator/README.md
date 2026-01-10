# Icon Grid Generator Skill

Generate batches of icons efficiently using 3x3 grids, then extract and center each icon with transparent backgrounds.

## Overview

This skill generates icons by:
1. **Batch generation**: Create 9 icons per API call in a 3x3 grid (9x cheaper than individual calls)
2. **Smart extraction**: Use blob detection to isolate each icon from grid borders
3. **Visual centering**: Center icons by visual weight, not just bounding box
4. **Transparent backgrounds**: Remove background colors for clean PNGs
5. **Review UI**: HTML interface for quality control with thumbs-down rejection

## Cost Efficiency

| Approach | API Calls for 189 icons | Relative Cost |
|----------|------------------------|---------------|
| Individual | 189 calls | 100% |
| 3x3 Grids | 21 calls | ~11% |

## Pipeline

```
[Word List] → [Generate 3x3 Grids] → [Split Cells] → [Blob Detection] → [Visual Center] → [Transparent BG] → [Review UI]
```

## Key Algorithms

### 1. Blob Detection (Connected Component Analysis)

Finds the largest connected region of non-background pixels. This isolates the main icon content and ignores any border artifacts from the grid.

```python
def find_largest_blob(img):
    """BFS to find largest connected component of content pixels."""
    visited = [[False]*h for _ in range(w)]
    largest_blob = []

    def bfs(start_x, start_y):
        blob = []
        queue = deque([(start_x, start_y)])
        while queue:
            x, y = queue.popleft()
            if visited[x][y] or not is_content_pixel(pixels[x, y]):
                continue
            visited[x][y] = True
            blob.append((x, y))
            queue.extend([(x+1,y), (x-1,y), (x,y+1), (x,y-1)])
        return blob

    # Find all blobs, keep largest
    for y in range(h):
        for x in range(w):
            if not visited[x][y] and is_content_pixel(pixels[x, y]):
                blob = bfs(x, y)
                if len(blob) > len(largest_blob):
                    largest_blob = blob
    return largest_blob
```

### 2. Visual Center (Weighted by Color Difference)

Centers icons by their visual weight rather than geometric center. Better for asymmetric shapes (e.g., a cat with a tail).

```python
def get_visual_center(img, blob):
    """Center weighted by color difference from background."""
    bg_color = (250, 245, 230)  # Cream background
    sum_x, sum_y, sum_weight = 0, 0, 0

    for x, y in blob:
        r, g, b = pixels[x, y]
        # Weight = how different from background
        diff = abs(r - bg_color[0]) + abs(g - bg_color[1]) + abs(b - bg_color[2])
        sum_x += x * diff
        sum_y += y * diff
        sum_weight += diff

    return sum_x / sum_weight, sum_y / sum_weight
```

### 3. Transparent Background

Replace background-colored pixels with alpha=0:

```python
def make_transparent(img):
    content_rgba = img.convert('RGBA')
    pixels = content_rgba.load()
    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            # Detect cream/white background
            is_bg = r > 230 and g > 220 and b > 200 and abs(r-g) < 30
            if is_bg:
                pixels[x, y] = (r, g, b, 0)  # Transparent
    return content_rgba
```

## Prompt Engineering

### Grid Generation Prompt Template

```
9 cute cartoon icons arranged in a 3x3 layout on a plain cream background.

Icons (left to right, top to bottom):
Panel 1: [detailed description]
Panel 2: [detailed description]
...

STYLE:
- Simple kawaii/emoji style icons
- Bold black outlines
- Bright flat colors
- Each icon FULLY VISIBLE and CENTERED (not cut off!)
- Plain solid cream (#FFF8E7) background

CRITICAL:
- Each icon must be COMPLETE - nothing cropped at edges
- NO borders, frames, or lines
- NO text or letters
- Leave padding around each icon
```

### Tips for Better Results

1. **Be specific**: "red car driving" not just "car"
2. **Describe the scene**: "tall giraffe next to short mouse" for "tall"
3. **Avoid abstract words**: Skip words like "this", "that", "with" - hard to visualize
4. **Add context**: "arrow missing target bullseye" for "miss"

## Review UI

Simple HTML page for quality control:
- Displays all icons in a grid
- Click to toggle 👎 rejection
- Filter: All / Approved / Rejected
- Export rejected list for regeneration
- Persists to localStorage

## Iterative Review Process

The most effective workflow is iterative refinement through multiple review rounds:

### Round 1: Initial Generation
- Generate all icons in 3x3 grids with basic prompts
- Review all icons, reject ones with issues (cutoff, wrong concept, bad transparency)
- Export rejected list

### Round 2-N: Targeted Regeneration
For each round, improve prompts based on observed issues:

| Issue | Solution |
|-------|----------|
| Icons cut off at edges | Request smaller icons (40-50% of cell), more padding |
| Poor transparency | Use WHITE background instead of cream, adjust detection thresholds |
| Wrong concept | Use more specific hints with concrete objects |
| Abstract words (this, that, then) | Use people/hands doing the action instead of symbols |
| Action words (skip, fell, show) | Include a person/character performing the action |

### Prompt Evolution Example

**Round 1** (too vague):
```
Panel 1: skip
```

**Round 2** (object-focused):
```
Panel 1: jump rope with handles
```

**Round 3** (with actor):
```
Panel 1: happy girl skipping with pigtails
```

### Key Learnings

1. **Actions need actors**: Words like "skip", "fell", "show" work better with people/characters doing the action rather than abstract symbols

2. **Concrete beats abstract**: "brown teddy bear" works; "brown color" doesn't

3. **Size matters**: Requesting smaller icons (40-50% of cell) prevents cutoff issues

4. **Background color**: Pure WHITE (#FFFFFF) is easier to make transparent than cream/beige

5. **Iterate quickly**: Multiple small batches with targeted fixes beats one large generation

### Typical Iteration Counts

| Category | Rounds to Approval |
|----------|-------------------|
| Simple nouns (cat, dog, sun) | 1 |
| Action words (run, jump, skip) | 2-3 |
| Abstract words (this, that, for) | 3-4 |
| Compound concepts (show, will) | 3-4 |

## File Structure

```
word-icons/
├── *.png              # Individual icons (300x300, transparent)
├── grids/             # Source grid images
├── review.html        # QA interface
└── review/            # Test samples
```

## Usage

```bash
# Generate all icons
python scripts/generate_word_icons.py

# Regenerate specific icons
python scripts/regenerate_word_icons.py

# Open review UI
open public/activities/word-icons/review.html
```

## Dependencies

- PIL/Pillow for image processing
- MuleRouter API for image generation (wan2.6-t2i)
