# Book Images Skill

Generate page images for a FunBookies book using style transfer from the reference sheet.

## When to Use

Use this skill when:
- A book has scenes and a reference, ready for page images
- Regenerating specific pages that didn't turn out well
- Regenerating all images with improved prompts

## Usage

```
/book-images <slug> [options]
```

Options:
- `--all` - Generate all pages (cover + story pages + end)
- `--cover` - Only generate cover image
- `--pages 3,5,7` - Only generate specific story pages
- `--end` - Only generate end page

Examples:
- `/book-images b2-if-i-could-only-be-a-red-tractor --all`
- `/book-images b2-if-i-could-only-be-a-red-tractor --pages 2,5`
- `/book-images c1-the-knights-quest --cover`

## How It Works

### 1. Load Book Data

Read the book from `/public/books/{slug}.json` and extract:
- `pages` - All pages with scene descriptions
- `story_elements` - When elements first appear (for negative prompts)
- Reference image URL from `/public/books/references/{slug}_reference.png`

### 2. Compute Negative Prompts

Use `story_elements` to prevent future elements from appearing:

```python
story_elements = {
    "airplane": 5,      # First appears on story_page 5
    "farmhouse": 9,     # First appears on story_page 9
    "clouds": 8
}

def get_negative_prompt(story_page):
    base = "text, words, letters, writing, watermark"
    exclusions = []

    for element, intro_page in story_elements.items():
        if story_page < intro_page:
            exclusions.append(element)

    if exclusions:
        return f"{base}, {', '.join(exclusions)}"
    return base

# Page 3: "text, words, letters, writing, watermark, airplane, farmhouse, clouds"
# Page 6: "text, words, letters, writing, watermark, farmhouse, clouds"
# Page 10: "text, words, letters, writing, watermark"
```

### 3. Generate Images with Wan2.6-Image

For each page, use image-to-image generation:

```bash
cd /path/to/mulerouter-skills
uv run python models/alibaba/wan2.6-image/generation.py \
  --prompt '{scene_description}' \
  --images '["https://...reference.png"]' \
  --negative-prompt '{computed_negative_prompt}' \
  --size '1280*960' \
  --n 1
```

**Image sizes:**
- Cover: `1280*1280` (square)
- Story pages: `1280*960` (landscape, fits 80/20 layout)
- End page: `1280*960`

### 4. Parallel Generation

Generate multiple pages in parallel for speed (4 at a time):

```bash
# Pages 1-4 in parallel
uv run python ... --prompt '{page1_scene}' & \
uv run python ... --prompt '{page2_scene}' & \
uv run python ... --prompt '{page3_scene}' & \
uv run python ... --prompt '{page4_scene}' & \
wait
```

### 5. Download Images

Save generated images to:
```
/public/images/covers/{slug}.png          # Cover
/public/books/images/{slug}_page{NN}.png  # Pages (01, 02, etc.)
```

### 6. Checkpoint

After generating, show the user:
1. Sample of generated images (cover + 2-3 key pages)
2. Ask: "Do the images match the text? Any pages need regeneration?"

## Image Generation Rules

### DO:
- Use the reference image for every generation
- Compute negative prompts based on story progression
- Include standard negative prompt base (text, watermark, etc.)
- Generate in parallel for speed (4 at a time max)
- Use consistent sizes (1280x960 for pages)

### DON'T:
- Skip the negative prompt
- Regenerate the reference when regenerating pages
- Use different aspect ratios for pages
- Generate more than 4 in parallel (API limits)

## Regenerating Specific Pages

When user says "page 5 has an airplane but shouldn't":

1. Check `story_elements` - when does airplane first appear?
2. If page 5 is before airplane intro, add "airplane, flying" to negative prompt
3. Regenerate just page 5:

```bash
/book-images b2-if-i-could-only-be-a-red-tractor --pages 5
```

## Common Issues

### Content Contamination
**Problem:** Airplane appears in tractor-only pages
**Cause:** Missing negative prompt or reference showing story scenes
**Solution:**
1. Check `story_elements` is correct
2. Verify negative prompt includes "airplane"
3. If reference is contaminating, regenerate with `/book-reference`

### Style Inconsistency
**Problem:** Pages look different from each other
**Cause:** Not using reference image
**Solution:** Ensure reference URL is passed to every generation

### Wrong Scene
**Problem:** Image doesn't match page text
**Cause:** Scene description is wrong
**Solution:** Use `/book-scenes` to rewrite, then regenerate

## File Locations

| Type | Path |
|------|------|
| Reference | `/public/books/references/{slug}_reference.png` |
| Cover | `/public/images/covers/{slug}.png` |
| Pages | `/public/books/images/{slug}_page{NN}.png` |

## Generation Summary

After completion, output:

```
Generated images for: b2-if-i-could-only-be-a-red-tractor

Cover: ✓
Pages: 01 ✓, 02 ✓, 03 ✓, 04 ✓, 05 ✓, 06 ✓, 07 ✓, 08 ✓, 09 ✓, 10 ✓
End: ✓

Total: 12 images
Time: ~3 minutes

Review at: /reader.html?book=b2-if-i-could-only-be-a-red-tractor&mode=edit
```
