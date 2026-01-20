# Book Images Skill

Generate page images for a FunBookies book using multi-reference style transfer.

## When to Use

Use this skill when:
- A book has scenes and individual reference images, ready for page images
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
- `/book-images the-big-pig --all`
- `/book-images the-big-pig --pages 2,5,8`
- `/book-images the-big-pig --cover`

## How It Works

### 1. Load Book Data

Read the book from `/public/books/{slug}.json` and extract:
- `pages` - All pages with scene descriptions
- `characters` - Character data with `visual_shorthand`
- `story_elements` - When elements first appear (for negative prompts)

### 2. Load Reference Images

Individual reference images in `/public/books/references/{slug}_multi/`:

```
{slug}_multi/
├── char_{name}_front.png      # Character front view
├── char_{name}_side.png       # Character side view
├── char_{name}_expression.png # Character expressions
├── env_day.png                # Day environment
├── env_night.png              # Night environment (if needed)
└── style_palette.png          # Color palette & style
```

### 3. Select 3 References Per Page (split-3ref)

For each page, select the most relevant 3 references:

```python
def select_refs_for_page(page, characters, setting):
    refs = []

    # 1. Character reference (front view for main character in scene)
    main_char = detect_main_character(page['scene'])
    refs.append(f"char_{main_char}_front.png")

    # 2. Environment reference (day/night based on scene)
    if "night" in page['scene'].lower():
        refs.append("env_night.png")
    else:
        refs.append("env_day.png")

    # 3. Style reference (always include)
    refs.append("style_palette.png")

    return refs  # Returns 3 refs for wan2.6-image
```

### 4. Generate Images with Wan2.6-Image (3 refs)

For each page, use image-to-image generation with 3 reference images:

```bash
cd ~/.claude/plugins/cache/mulerouter-skills/mulerouter-skills/1.0.0/skills/mulerouter-skills

uv run python models/alibaba/wan2.6-image/generation.py \
  --prompt '{scene_description}' \
  --images '["https://.../char_tim_front.png", "https://.../env_day.png", "https://.../style_palette.png"]' \
  --negative-prompt 'text, words, letters, watermark, {story_exclusions}' \
  --size '1280*960' \
  --n 1
```

Or use the multi_ref_experiment.py script:

```bash
cd /Users/dereklomas/lilbookies
uv run python scripts/multi_ref_experiment.py {slug} \
  --strategies split-3ref \
  --pages 1,2,3,4,5,6,7,8,9,10,11,12
```

**Image sizes:**
- Cover: `1280*1280` (square)
- Story pages: `1280*960` (landscape, fits 80/20 layout)
- End page: `1280*960`

### 5. Compute Negative Prompts

Use `story_elements` to prevent future elements from appearing:

```python
story_elements = {
    "airplane": 5,      # First appears on story_page 5
    "farmhouse": 9,     # First appears on story_page 9
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
```

### 6. Parallel Generation

Generate multiple pages in parallel for speed (4 at a time):

```bash
# Pages 1-4 in parallel
uv run python ... --prompt '{page1_scene}' & \
uv run python ... --prompt '{page2_scene}' & \
uv run python ... --prompt '{page3_scene}' & \
uv run python ... --prompt '{page4_scene}' &
wait
```

### 7. Download Images

Save generated images to:
```
/public/images/covers/{slug}.png          # Cover
/public/books/images/{slug}/page{NN}.png  # Pages (01, 02, etc.)
```

### 8. Checkpoint

After generating, show the user:
1. Sample of generated images (cover + 2-3 key pages)
2. Ask: "Do the images match the text? Any pages need regeneration?"

## Image Generation Rules

### DO:
- Use 3 reference images per generation (character, environment, style)
- Compute negative prompts based on story progression
- Include standard negative prompt base (text, watermark, etc.)
- Generate in parallel for speed (4 at a time max)
- Use consistent sizes (1280x960 for pages)

### DON'T:
- Use more than 3 references (wan2.6 limit)
- Skip the negative prompt
- Use different aspect ratios for pages
- Generate more than 4 in parallel (API limits)

## Regenerating Specific Pages

When user says "page 5 has an airplane but shouldn't":

1. Check `story_elements` - when does airplane first appear?
2. If page 5 is before airplane intro, add "airplane, flying" to negative prompt
3. Regenerate just page 5:

```bash
uv run python scripts/multi_ref_experiment.py {slug} \
  --strategies split-3ref \
  --pages 5
```

## Common Issues

### Content Contamination
**Problem:** Airplane appears in tractor-only pages
**Cause:** Missing negative prompt
**Solution:**
1. Check `story_elements` is correct
2. Verify negative prompt includes "airplane"
3. Regenerate the page

### Style Inconsistency
**Problem:** Pages look different from each other
**Cause:** Different reference combinations or missing style_palette ref
**Solution:** Ensure style_palette.png is always included as one of the 3 refs

### Wrong Scene
**Problem:** Image doesn't match page text
**Cause:** Scene description is wrong
**Solution:** Update the scene in book JSON, then regenerate

### Character Looks Different
**Problem:** Character appearance varies between pages
**Cause:** Using different character refs or no character ref
**Solution:** Always include character front ref for pages featuring that character

## File Locations

| Type | Path |
|------|------|
| Character refs | `/public/books/references/{slug}_multi/char_{name}_*.png` |
| Environment refs | `/public/books/references/{slug}_multi/env_*.png` |
| Style ref | `/public/books/references/{slug}_multi/style_palette.png` |
| Cover | `/public/images/covers/{slug}.png` |
| Pages | `/public/books/images/{slug}/page{NN}.png` |

## Generation Summary

After completion, output:

```
Generated images for: the-big-pig

References used: char_tim_front, char_pig_front, env_day, style_palette
Strategy: split-3ref (3 refs per page)

Cover: ✓
Pages: 01 ✓, 02 ✓, 03 ✓, 04 ✓, 05 ✓, 06 ✓, 07 ✓, 08 ✓, 09 ✓, 10 ✓, 11 ✓, 12 ✓
End: ✓

Total: 14 images @ $0.03 each = $0.42
Cost breakdown: Character refs $0.03/ea, Env refs $0.03/ea, Pages $0.03/ea

Review at: /reader.html?book=the-big-pig&mode=edit
```
