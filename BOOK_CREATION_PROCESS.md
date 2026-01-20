# Book Creation Process

A comprehensive guide to creating FunBookies books correctly. Follow this process to avoid common mistakes.

## Overview

```
Story Seed → Story Text → Scene Descriptions → Reference Image → Page Images → Deploy
                ↓              ↓                    ↓               ↓
           CHECKPOINT 1   CHECKPOINT 2         CHECKPOINT 3    CHECKPOINT 4
```

**CRITICAL RULE:** Never proceed past a checkpoint without human review.

---

## Three Ways to Create Books

### 1. Web Wizard (Recommended for humans)
```
https://funbookies.com/wizard/
```
Step-by-step UI with built-in validation. Data saved to Supabase after each phase.

### 2. Claude Code Web (AI-assisted)
```
https://claude.ai/code
```
Connect your GitHub repo, then either:
- Use browser automation to run the wizard
- Call APIs directly via curl
- Ask Claude to generate and review each phase

**Example prompt for Claude Code Web:**
```
Create a B2 level book about a cat who finds a lost mitten.
Use the wizard at funbookies.com/wizard/ to generate it,
reviewing each phase before proceeding.
```

### 3. CLI/Python Scripts (Batch generation)
```bash
python scripts/generate_story.py --level B2 --concept "cat finds mitten"
python scripts/generate_scene_descriptions.py cat-and-the-mitten
python scripts/generate_references.py --book cat-and-the-mitten
python scripts/generate_page_images.py cat-and-the-mitten
```

---

## API Endpoints (for Claude Code Web / programmatic access)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/generate-story` | POST | Generate story from concept |
| `/api/generate-scenes` | POST | Generate scene descriptions (Sonnet) |
| `/api/validate-book` | POST | Validate book for image generation |
| `/api/generate-image` | POST | Generate single image |
| `/api/save-book` | POST | Save book to Supabase |
| `/api/check-status` | GET | Poll async image generation |

**Example: Generate story via API**
```bash
curl -X POST https://funbookies.com/api/generate-story \
  -H "Content-Type: application/json" \
  -d '{"level": "B2", "concept": "cat finds mitten", "setting": "snowy backyard"}'
```

---

## Phase 1: Story Generation

### Input
- Level specification (B1, B4, B6, etc.)
- Story seed (setting, anchor, mode)
- Pipeline config (A-F)

### Output
- Story text with page breaks
- `book.json` with text fields populated

### Checkpoint 1: Story Review
Before proceeding, verify:
- [ ] Text matches target phonics level
- [ ] Decodability meets level requirements
- [ ] Heart/sight words are appropriate
- [ ] Each page has a clear visual moment
- [ ] Story has emotional arc

---

## Phase 2: Scene Description Generation

### The Problem This Solves
Bad: `"Illustration for: The pig sat in mud..."`
Good: `"Plump pink pig with floppy ears splashing joyfully in brown mud puddle, mud droplets flying, wooden fence and sunny farm field behind. Warm watercolor style."`

### Scene Description Requirements

Every scene MUST include:

1. **WHO** - Character with visual identifiers
   - Age, size, physical features
   - Hair color/style, skin tone
   - Clothing with colors
   - Expression/emotion

2. **WHERE** - Setting with specificity
   - Location details
   - Time of day/weather
   - Cultural context if relevant

3. **WHAT** - Action matching page text
   - Verb describing what's happening
   - Body position/gesture
   - Interaction with environment

4. **COMPOSITION** - Framing
   - Shot type: wide, medium, close, detail
   - "Single scene illustration" (prevents grids)
   - "Full-bleed, scene fills entire canvas"

5. **STYLE** - Art direction
   - "Warm watercolor style" or specific reference
   - "NO TEXT anywhere in image"

### Scene Description Template

```
[Shot type] shot: [CHARACTER with visual details] [ACTION verb-ing] [in/at LOCATION].
[Additional scene elements]. [Mood/atmosphere]. [Style]. NO TEXT.
```

### Example

Page text: "Tim ran to the big pig. She sat and sat."

Bad scene:
```
Illustration for: Tim ran to the big pig. She sat and sat.
```

Good scene:
```
Medium shot: Tim, a round-faced boy (6-7) in denim overalls and straw sun hat,
running eagerly across dusty farm ground toward a plump pink pig with droopy ears.
The pig sits contentedly in a patch of shade by a wooden fence. Bright summer
sunlight, green grass, warm ochre dirt. Playful Eric Carle collage style with
bold shapes and textures. NO TEXT.
```

### NEVER Include in Scene Descriptions

1. **Negations** - Don't say what ISN'T there
   - Bad: "no ball", "without the tractor", "not raining"
   - Why: Models attend to concepts even when negated. "No ball" activates "ball"
   - Good: Only describe what IS there

2. **Future story elements** - Don't mention things that appear later
   - Track when elements first appear
   - Exclude future elements from earlier pages

3. **Abstract/mood words without visuals**
   - Bad: "dreamy atmosphere", "magical feeling", "sense of wonder"
   - Good: "soft golden light", "sparkles floating in air", "child's eyes wide"

4. **Grid/panel references**
   - Bad: "not a grid", "single image not panels"
   - Good: "One cohesive illustration filling the entire canvas"

### Emotional → Physical Translation

**CRITICAL:** Never use mood words in scene descriptions. Translate emotions to physical manifestations:

| Emotion | Physical Description |
|---------|---------------------|
| Scared/Panicked | Eyes wide open, mouth agape, eyebrows raised high, body leaning back |
| Happy/Joyful | Wide smile showing teeth, eyes crinkled, cheeks raised |
| Sad/Worried | Downturned mouth, eyebrows furrowed inward, shoulders slumped |
| Surprised | Mouth O-shaped, eyebrows raised, hands up near face |
| Determined | Jaw set, eyes focused, chin up, chest out, stepping confidently |
| Tired/Exhausted | Drooping eyelids, slouched posture, yawning |
| Stuck in mud | Body buried up to [specific point], only [parts] visible above surface |
| Running away | Legs extended mid-stride, arms pumping, body leaning forward |

**Why:** Image models don't understand emotions—they understand visual features. "Scared" means nothing; "eyes wide, mouth agape" is renderable.

### Checkpoint 2: Scene Description Review

Before proceeding to image generation:
- [ ] Every story page has a scene description
- [ ] Each scene follows WHO/WHERE/WHAT/COMPOSITION/STYLE format
- [ ] No negations anywhere
- [ ] No future story elements mentioned
- [ ] Character descriptions match reference prompt
- [ ] "NO TEXT" included in every scene

---

## Phase 3: Reference Image Generation

### Purpose
The 9-panel reference sheet establishes:
- Character design consistency
- Color palette
- Art style
- Key objects/props
- Setting elements

### Reference Sheet Structure
```
[1] Character front   [2] Expressions      [3] Character action
[4] Secondary char    [5] Key prop/object  [6] KEY MOMENT (center)
[7] Setting element   [8] Setting element  [9] Resolution/together
```

### Reference Prompt Requirements
- Focus on STYLE VOCABULARY, not story scenes
- Panel 6 (center) has highest style influence
- Include "NO TEXT, NO WORDS, NO LETTERS"
- Specify art style explicitly

### Model
Use `nano-banana-pro` (text-to-image) for references.

### Checkpoint 3: Reference Image Review

Before generating page images:
- [ ] Character is consistent across panels
- [ ] Style matches the intended mood
- [ ] Color palette is cohesive
- [ ] No unwanted text/words in image
- [ ] Key props/objects are present

---

## Phase 4: Page Image Generation

### The Critical Settings

Every page image prompt MUST include:

```
PROMPT PREFIX (add to every scene):
"Single scene illustration: "

PROMPT SUFFIX (add to every scene):
"
COMPOSITION: One cohesive illustration filling the entire canvas.
Full-bleed image with the scene filling edge to edge.
Style: [Match reference - watercolor/collage/etc].
NO TEXT, NO WORDS, NO LETTERS anywhere in image."
```

### Image Generation Parameters

| Parameter | Value | Why |
|-----------|-------|-----|
| Model | wan2.6-image | I2I style transfer |
| Reference | {slug}_reference.png | Style consistency |
| Size | 1280x960 (pages), 1280x1280 (cover) | Reader layout |

### Building the Final Prompt

```python
def build_page_prompt(scene_description: str, book: dict) -> str:
    """Build complete prompt for page image generation."""

    # Get character block from story_bible
    char_block = get_character_block(book)

    # Get style from reference prompt or art_direction
    style = extract_style(book)

    prompt = f"""Single scene illustration: {scene_description}

CHARACTERS (draw EXACTLY as described - these features are KEY):
{char_block}

COMPOSITION: One cohesive illustration filling the entire canvas.
Full-bleed image with the scene filling edge to edge.

STYLE: {style}

CRITICAL: NO TEXT, NO WORDS, NO LETTERS anywhere. Pure illustration only."""

    return prompt
```

### Pre-Flight Checklist

Before running batch image generation:

```bash
# Run validation script
python scripts/validate_book_for_images.py {slug}
```

Validation checks:
- [ ] Book JSON exists
- [ ] Reference image exists
- [ ] All story pages have scene descriptions
- [ ] Scene descriptions are not placeholders ("Illustration for:")
- [ ] Scene descriptions include character details
- [ ] Scene descriptions include composition instructions
- [ ] No negations in scene descriptions
- [ ] story_bible or characters field populated

### Optional: Prompt Enhancement Pipeline

For higher-quality prompts, use the enhancement script:

```bash
python scripts/prompt_enhancer.py {slug} --pages 11,12,13
```

The pipeline:
1. **Story Context Analysis** - Determines narrative act (setup/conflict/climax/resolution)
2. **Character Presence Logic** - Identifies who MUST and MUST NOT be in scene
3. **Emotional → Physical Translation** - Converts mood words to visual descriptions
4. **LLM Review & Scoring** - Validates prompt quality before generation

**Review Scoring Criteria:**

| Score | Quality | Action |
|-------|---------|--------|
| 9-10 | Perfect - physically specific, correct characters, clear composition | Generate |
| 7-8 | Good - minor improvements but should generate correctly | Generate |
| 5-6 | Acceptable - some vagueness but main elements clear | Caution |
| 3-4 | Problematic - likely wrong characters or emotions | Fix first |
| 1-2 | Fail - will definitely generate incorrectly | Must fix |

**Common Issues Detected:**
- Wrong characters present (character should be alone)
- Emotional words without physical translation
- Vague positioning ("in the scene" vs specific placement)
- Missing key character identifiers
- Ambiguous scale or size relationships
- Story continuity errors

### Checkpoint 4: Image Review

After generation, review in edit mode:
```
https://funbookies.com/reader.html?book={slug}&mode=edit
```

Check for:
- [ ] No grid/panel layouts (should be single images)
- [ ] Characters match reference design
- [ ] No unwanted text in images
- [ ] Style consistent across pages
- [ ] No content contamination from future pages
- [ ] Actions match page text

---

## Common Mistakes and How to Avoid Them

### Mistake 1: Lazy Scene Descriptions
**Symptom:** Images don't match story, random content
**Cause:** Scene is just "Illustration for: [text]..."
**Prevention:** Checkpoint 2 - validate all scenes before image gen

### Mistake 2: Grid/Panel Output
**Symptom:** Page images come out as 9-panel grids
**Cause:** Reference is 9-panel, style transfer copies layout
**Prevention:**
- Add "Single scene illustration:" prefix
- Add "One cohesive illustration filling entire canvas"
- Never say "not a grid" (activates "grid")

### Mistake 3: Content Contamination
**Symptom:** Airplane appears before it should in story
**Cause:** Reference shows airplane, or negative prompt missing
**Prevention:**
- Track `story_elements` with first appearance page
- Compute exclusions dynamically
- Keep reference focused on style, not story scenes

### Mistake 4: Text in Images
**Symptom:** Generated images have words/letters
**Cause:** Missing "NO TEXT" instruction
**Prevention:** Add "NO TEXT, NO WORDS, NO LETTERS" to every prompt

### Mistake 5: Inconsistent Characters
**Symptom:** Character looks different on each page
**Cause:** Missing character consistency block in prompts
**Prevention:**
- Include character visual details in every prompt
- Reference the same reference image for all pages
- Use explicit "draw EXACTLY as described" language

---

## Quick Reference: Prompt Anatomy

```
┌─────────────────────────────────────────────────────────────┐
│ Single scene illustration: [SCENE DESCRIPTION]              │ ← Prefix
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ [WHO]: Tim, round-faced boy (6-7), denim overalls,         │
│        straw sun hat, eager expression                      │
│                                                             │
│ [WHAT]: running across dusty farm ground                    │
│                                                             │
│ [WHERE]: toward plump pink pig by wooden fence,            │
│          bright summer sunlight, green grass                │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ CHARACTERS (draw EXACTLY as described):                     │ ← Character block
│ - Tim: round-faced boy, denim overalls, straw hat          │
│ - Pig: plump pink, droopy ears, expressive eyes            │
├─────────────────────────────────────────────────────────────┤
│ COMPOSITION: One cohesive illustration filling entire       │ ← Anti-grid
│ canvas. Full-bleed image, scene fills edge to edge.        │
├─────────────────────────────────────────────────────────────┤
│ STYLE: Eric Carle collage, bold shapes, warm palette       │ ← Style match
├─────────────────────────────────────────────────────────────┤
│ CRITICAL: NO TEXT, NO WORDS, NO LETTERS anywhere.          │ ← No text
└─────────────────────────────────────────────────────────────┘
```

---

## Validation Script

Create `scripts/validate_book_for_images.py`:

```python
#!/usr/bin/env python3
"""Validate book is ready for image generation."""

import json
import sys
from pathlib import Path

def validate_book(slug: str) -> bool:
    book_path = Path(f"public/books/{slug}.json")
    ref_path = Path(f"public/books/references/{slug}_reference.png")

    errors = []
    warnings = []

    # Check files exist
    if not book_path.exists():
        errors.append(f"Book JSON not found: {book_path}")
        return False

    if not ref_path.exists():
        errors.append(f"Reference image not found: {ref_path}")

    with open(book_path) as f:
        book = json.load(f)

    # Check each story page
    for page in book.get("pages", []):
        if page.get("type") != "story":
            continue

        pnum = page.get("page", "?")
        scene = page.get("scene", "")

        # Check for placeholder scenes
        if scene.startswith("Illustration for:"):
            errors.append(f"Page {pnum}: Placeholder scene description")

        if not scene:
            errors.append(f"Page {pnum}: Missing scene description")
            continue

        # Check for negations
        negation_words = ["no ", "not ", "without ", "don't ", "doesn't ", "isn't ", "aren't "]
        for neg in negation_words:
            if neg in scene.lower():
                warnings.append(f"Page {pnum}: Possible negation found: '{neg}'")

        # Check for required elements
        if "NO TEXT" not in scene.upper():
            warnings.append(f"Page {pnum}: Missing 'NO TEXT' instruction")

        # Check scene length (good scenes are detailed)
        if len(scene) < 100:
            warnings.append(f"Page {pnum}: Scene too short ({len(scene)} chars)")

    # Check for character definitions
    if not book.get("characters") and not book.get("story_bible", {}).get("characters"):
        warnings.append("No character definitions found")

    # Report
    print(f"\n{'='*60}")
    print(f"VALIDATION: {slug}")
    print(f"{'='*60}")

    if errors:
        print(f"\n❌ ERRORS ({len(errors)}):")
        for e in errors:
            print(f"   - {e}")

    if warnings:
        print(f"\n⚠️  WARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"   - {w}")

    if not errors and not warnings:
        print("\n✅ Book is ready for image generation")
        return True
    elif not errors:
        print("\n⚠️  Book has warnings but can proceed")
        return True
    else:
        print("\n❌ Book has errors - fix before generating images")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_book_for_images.py <slug>")
        sys.exit(1)

    success = validate_book(sys.argv[1])
    sys.exit(0 if success else 1)
```

---

## Process Automation

### Recommended Workflow

```bash
# 1. Generate story
python scripts/story_generator/run_book_experiment.py --seeds "b1_pig"

# 2. Generate scene descriptions (NEW - needs implementation)
python scripts/generate_scene_descriptions.py the-big-pig

# 3. CHECKPOINT: Review scenes
cat public/books/the-big-pig.json | jq '.pages[] | select(.type=="story") | {page, scene}'

# 4. Validate before images
python scripts/validate_book_for_images.py the-big-pig

# 5. Generate reference image
# (use mulerouter-skills nano-banana-pro)

# 6. CHECKPOINT: Review reference image
open public/books/references/the-big-pig_reference.png

# 7. Generate page images
python scripts/generate_page_images.py the-big-pig --provider mulerouter

# 8. CHECKPOINT: Review in browser
open "https://funbookies.com/reader.html?book=the-big-pig&mode=edit"
```

---

## Summary: The 4 Checkpoints

| # | Phase | What to Check | Who Reviews |
|---|-------|---------------|-------------|
| 1 | Story | Text quality, phonics, emotional arc | Human |
| 2 | Scenes | WHO/WHERE/WHAT/STYLE, no negations | Human + Script |
| 3 | Reference | Character consistency, style, no text | Human |
| 4 | Images | Single images, style match, no text | Human |

**NEVER skip checkpoints. The cost of regenerating 100+ bad images far exceeds the time to review.**
