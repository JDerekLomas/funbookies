# Book Reference Skill

Generate individual reference images for consistent character, environment, and style design.

## When to Use

Use this skill when:
- A book has character and setting data, needs reference images
- Regenerating reference images with improvements
- Adding new characters or environments to an existing book

## Usage

```
/book-reference <slug>
```

Examples:
- `/book-reference the-big-pig`
- `/book-reference sled-run`

## How It Works

### 1. Load Book Data

Read the book from `/public/books/{slug}.json` and extract:
- `characters` - Character data with `visual_shorthand` and `distinctive_features`
- `setting_context` - Environment description
- `story_bible.visual_style` - Art style notes

Example character data:
```json
{
  "characters": {
    "tim": {
      "name": "Tim",
      "visual_shorthand": "young boy (5-6), round face, short brown hair, blue overalls, red t-shirt",
      "distinctive_features": ["round face", "short brown hair", "blue overalls", "red t-shirt"]
    },
    "pig": {
      "name": "The Big Pig",
      "visual_shorthand": "very large pink pig with floppy ears, friendly expression",
      "distinctive_features": ["very large size", "pink", "floppy ears"]
    }
  }
}
```

### 2. Individual Reference Structure

Generate separate reference images instead of a single 9-panel composite:

```
{slug}_multi/
├── Character References
│   ├── char_{name}_front.png      # Front view, full body, clear design
│   ├── char_{name}_side.png       # Side/3-quarter view, in action
│   └── char_{name}_expression.png # Expression studies (multiple faces)
│
├── Environment References
│   ├── env_day.png                # Daytime setting
│   └── env_night.png              # Nighttime setting (if needed)
│
└── Style Reference
    └── style_palette.png          # Color palette, style exemplar
```

**Why individual refs?**
- wan2.6-image supports up to 3 reference images per generation
- Allows selecting the most relevant refs per page
- Prevents grid artifacts from composite references
- More control over character/environment/style influence

### 3. Generate Reference Prompts

For each reference type, generate a specialized prompt:

**Character Front:**
```
Single character illustration on clean background:
{Character name}, {visual_shorthand}.
Standing in neutral pose, facing viewer, full body visible.
{art_style}
NO TEXT, NO WORDS, NO LETTERS anywhere.
```

**Character Side:**
```
Single character illustration on clean background:
{Character name}, {visual_shorthand}.
Three-quarter view, walking or in gentle motion.
{art_style}
NO TEXT, NO WORDS, NO LETTERS anywhere.
```

**Character Expression:**
```
Character expression studies:
{Character name}, {visual_shorthand}.
Four expressions in 2x2 grid: happy, surprised, sad, determined.
Same character in each, head/face only.
{art_style}
NO TEXT, NO WORDS, NO LETTERS anywhere.
```

**Environment Day:**
```
Environment illustration:
{setting_context} during daytime.
Establishing shot showing full environment, no characters.
Bright natural lighting, warm atmosphere.
{art_style}
NO TEXT, NO WORDS, NO LETTERS anywhere.
```

**Style Palette:**
```
Art style reference:
Color palette and style demonstration for children's book.
{art_style}
Show: color swatches, texture samples, sample object in style.
Clean presentation, no characters or specific story elements.
NO TEXT, NO WORDS, NO LETTERS anywhere.
```

### 4. Generate Images with Nano-Banana-Pro

Use the multi_ref_experiment.py script to generate all references:

```bash
cd /Users/dereklomas/lilbookies
uv run python scripts/multi_ref_experiment.py {slug} --generate-refs
```

This generates all character, environment, and style references based on book JSON data.

Or generate individually using MuleRouter:

```bash
cd ~/.claude/plugins/cache/mulerouter-skills/mulerouter-skills/1.0.0/skills/mulerouter-skills

uv run python models/google/nano-banana-pro/generation.py \
  --prompt '{reference_prompt}' \
  --aspect-ratio '1:1' \
  --resolution '2K'
```

### 5. Download and Save

Save generated images to:
```
/public/books/references/{slug}_multi/char_{name}_front.png
/public/books/references/{slug}_multi/char_{name}_side.png
/public/books/references/{slug}_multi/char_{name}_expression.png
/public/books/references/{slug}_multi/env_day.png
/public/books/references/{slug}_multi/env_night.png
/public/books/references/{slug}_multi/style_palette.png
```

### 6. Checkpoint

After generating, show the user:
1. All generated reference images
2. Ask: "Do the characters look consistent? Are environments correct? Ready to generate page images?"

## Reference Quality Checklist

### Character References
- [ ] Front view shows full body, clear features
- [ ] Side view is recognizably the same character
- [ ] Expressions show range while maintaining identity
- [ ] Clothing/colors match `visual_shorthand`
- [ ] Distinctive features are visible

### Environment References
- [ ] Setting matches `setting_context`
- [ ] Appropriate lighting (day/night)
- [ ] Child-friendly, warm atmosphere
- [ ] No characters or story elements

### Style Reference
- [ ] Color palette matches intended style
- [ ] Texture/brushwork is consistent
- [ ] No text or letters anywhere

## Common Issues

### Character Looks Different Between Refs
**Problem:** Front and side views don't match
**Solution:** Include full `visual_shorthand` in each prompt, emphasize key features

### Environment Too Specific
**Problem:** Environment ref shows specific story scene
**Solution:** Use "establishing shot" framing, exclude story-specific elements

### Wrong Art Style
**Problem:** Style doesn't match book's visual intent
**Solution:** Include detailed `art_style` in every prompt

## File Locations

| Type | Path |
|------|------|
| Character refs | `/public/books/references/{slug}_multi/char_{name}_*.png` |
| Environment refs | `/public/books/references/{slug}_multi/env_*.png` |
| Style ref | `/public/books/references/{slug}_multi/style_palette.png` |

## Generation Summary

After completion, output:

```
Generated references for: the-big-pig

Characters:
  tim: front ✓, side ✓, expression ✓
  pig: front ✓, side ✓, expression ✓

Environments:
  day ✓

Style:
  palette ✓

Total: 8 reference images
Location: /public/books/references/the-big-pig_multi/

Ready for: /book-images the-big-pig --all
```
