# Book Reference Skill

Generate a 9-panel style reference sheet for consistent character, object, and setting design.

## When to Use

Use this skill when:
- A book has scene descriptions and needs a style reference
- Regenerating a reference sheet with improvements
- The existing reference is causing content contamination

## Usage

```
/book-reference <slug>
```

Examples:
- `/book-reference b2-if-i-could-only-be-a-red-tractor`
- `/book-reference c1-the-knights-quest`

## How It Works

### 1. Load Book Data

Read the book from `/public/books/{slug}.json` and extract:
- `reference_prompt` - The 9-panel prompt (if exists)
- `characters` - Character descriptions
- `setting_context` - Cultural/geographic context
- Key objects from the story

### 2. Design Reference Structure

The reference should show **STYLE VOCABULARY**, not story scenes:

```
Row 1 - CHARACTER DESIGN:
[1] Front view with full outfit
[2] Expression studies (3 small faces)
[3] Character in motion

Row 2 - KEY OBJECTS:
[4] Main object 1 (e.g., red tractor)
[5] Main object 2 (e.g., airplane)
[6] Props together (e.g., toy versions)

Row 3 - SETTING:
[7] Exterior (e.g., farmhouse)
[8] Landscape (e.g., countryside)
[9] Interior (e.g., cozy room)
```

**Why this structure?**
- Separates visual elements from narrative
- Prevents content contamination (airplane won't appear in tractor scenes)
- Establishes consistent character design
- Defines the color palette and style

### 3. Generate Reference Prompt

If `reference_prompt` doesn't exist, create it:

```
9-PANEL STYLE REFERENCE SHEET for children's book illustration

FOCUS: Character design, setting elements, and color palette. NOT story scenes.

Row 1 - CHARACTER DESIGN:
[1] {Character} front view: {full description}, standing pose, cream background
[2] {Character} expressions: Same {character type} showing three expressions -
    {emotion1}, {emotion2}, {emotion3}
[3] {Character} in motion: Same {character type} {action}, {details}

Row 2 - KEY OBJECTS:
[4] {Object1}: {detailed description}, {style notes}
[5] {Object2}: {detailed description}, {style notes}
[6] {Objects together}: {toy/miniature versions on surface}

Row 3 - {SETTING_NAME} SETTING:
[7] {Exterior}: {cultural-specific building description}
[8] {Landscape}: {geographic-specific landscape description}
[9] {Interior}: {room description with lighting}

STYLE: Warm soft watercolor illustration throughout all panels. Muted earthy
palette: sage green, terracotta orange, warm cream, soft gold, dusty blue.
Soft painterly edges with no hard black outlines. Gentle natural lighting.
Friendly rounded shapes suitable for young children.

LAYOUT: 3x3 grid with thin white borders between panels. Each panel clearly separated.

CRITICAL: NO TEXT, NO WORDS, NO LETTERS, NO NUMBERS anywhere in the image.
Pure visual reference only.
```

### 4. Generate Image with Nano-Banana-Pro

Use the MuleRouter skill to generate the reference:

```bash
cd /path/to/mulerouter-skills
uv run python models/google/nano-banana-pro/generation.py \
  --prompt '{reference_prompt}' \
  --aspect-ratio '1:1' \
  --resolution '2K'
```

### 5. Download and Save

Save the generated image to:
```
/public/books/references/{slug}_reference.png
```

If regenerating, save as `_reference_v2.png`, `_v3.png`, etc.

### 6. Checkpoint

After generating, show the user:
1. The reference image
2. Ask: "Does the character look consistent? Are the objects and settings correct? Ready to generate page images?"

## Reference Quality Checklist

- [ ] Character is consistent across all 3 character panels
- [ ] Character matches the description (age, hair, clothing)
- [ ] Objects are clearly depicted and child-friendly
- [ ] Setting matches cultural context
- [ ] Color palette is warm and cohesive
- [ ] No text or letters anywhere
- [ ] 9 distinct panels visible

## Common Issues

### Content Contamination
**Problem:** Story scenes in reference bleed into all page images
**Solution:** Use character/object/setting structure, NOT story scenes

### Inconsistent Character
**Problem:** Character looks different across panels
**Solution:** Include detailed identifiers in each panel description

### Wrong Setting
**Problem:** Generic "farmhouse" instead of cultural-specific
**Solution:** Use setting_context ("Estonian wooden farmhouse with steep shingled roof")

## File Locations

| File | Path |
|------|------|
| Reference | `/public/books/references/{slug}_reference.png` |
| Versioned | `/public/books/references/{slug}_reference_v2.png` |
