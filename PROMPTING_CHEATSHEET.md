# Prompting Cheat Sheet

Quick reference for all FunBookies prompting knowledge. For details, see linked docs.

---

## Quick Index

| Doc | Focus | When to Use |
|-----|-------|-------------|
| [BOOK_CREATION_PROCESS.md](BOOK_CREATION_PROCESS.md) | 4-checkpoint workflow | Starting a new book |
| [STORY_CONTENT_GUIDE.md](STORY_CONTENT_GUIDE.md) | Narrative principles | Writing story text |
| [STORY_RUBRIC.md](STORY_RUBRIC.md) | Quality checklist | Reviewing story quality |
| [IMAGE_GENERATION_WORKFLOW.md](IMAGE_GENERATION_WORKFLOW.md) | Multi-ref architecture | Understanding the pipeline |
| [REFERENCE_IMAGE_PROMPTS.md](REFERENCE_IMAGE_PROMPTS.md) | 9-panel templates, **metaprompts** | Creating reference sheets |
| [BOOK_GENERATION_GUIDE.md](BOOK_GENERATION_GUIDE.md) | Conversational workflow | Step-by-step generation |

---

## Metaprompt System

Reference prompts are generated from a **metaprompt template** + **story data**:

```
Metaprompt: "Create a 3x3 grid for {title}: CHARACTER: {name} - {description}..."
     +
Story Data: {title: "Spot Finds Sun", name: "Spot", description: "fluffy gray cat..."}
     =
Generated: "Create a 3x3 grid for Spot Finds Sun: CHARACTER: Spot - fluffy gray cat..."
```

**Placeholders:** `{title}`, `{name}`, `{NAME}`, `{description}`, `{traits}`, `{setting}`

**Data extraction:** Character details auto-extracted from scene descriptions.

See [REFERENCE_IMAGE_PROMPTS.md](REFERENCE_IMAGE_PROMPTS.md#metaprompt-system) for details.

---

## The Golden Rules

### 1. Never Use Negations
```
BAD:  "no ball", "without tractor", "not raining", "no other characters"
GOOD: Only describe what IS there
```
**Why:** Models attend to concepts even when negated. "No ball" activates "ball".

### 2. Physical Over Emotional
```
BAD:  "scared", "happy", "worried"
GOOD: Physical manifestations (see translation table below)
```

### 3. Explicit Character Presence
```
BAD:  "Rex entering tunnel"
GOOD: "Rex entering tunnel ALONE. Rosie NOT in scene."
```

### 4. Single Scene Emphasis
```
ALWAYS ADD: "Single scene illustration:"
ALWAYS ADD: "One cohesive illustration filling the entire canvas"
NEVER SAY: "not a grid" (activates "grid")
```

### 5. NO TEXT in Every Prompt
```
ALWAYS END WITH: "NO TEXT, NO WORDS, NO LETTERS anywhere in image."
```

---

## Scene Description Framework (WHO/WHERE/WHAT/STATE)

```
[Shot type]: [WHO with visual details] [WHAT action verb-ing] [WHERE with specifics].
[STATE: character's current physical condition]. [Mood/atmosphere]. [Style]. NO TEXT.
```

**STATE tracking** - Always show current physical condition:
- wet? muddy? clean? tired? injured? happy?
- If they got muddy on page 4, they're STILL muddy on page 5 (unless cleaned)
- If they're in the bath, they'll be WET when they get out

**Example:**
```
Medium shot: Tim, a round-faced boy (6-7) in denim overalls and straw sun hat,
running eagerly across dusty farm ground toward a plump pink pig with droopy ears.
Tim's overalls are mud-splattered from page 3. The pig sits contentedly by a wooden
fence. Bright summer sunlight, warm ochre dirt. Eric Carle collage style. NO TEXT.
```

### Shot Types
| Shot | Use For |
|------|---------|
| Wide | Establishing location, multiple characters |
| Medium | Character interaction, main action |
| Close-up | Emotion, detail, dramatic moment |
| Detail | Props, hands, specific objects |

---

## Emotional → Physical Translation Table

Use in scene descriptions instead of mood words:

| Emotion | Physical Description |
|---------|---------------------|
| Scared/Panicked | Eyes wide open, mouth agape, eyebrows raised high, body leaning back |
| Happy/Joyful | Wide smile showing teeth, eyes crinkled, cheeks raised |
| Sad/Worried | Downturned mouth, eyebrows furrowed inward, shoulders slumped |
| Surprised | Mouth O-shaped, eyebrows raised, hands up near face |
| Determined | Jaw set, eyes focused, chin up, chest out |
| Tired | Drooping eyelids, slouched posture, yawning |
| Stuck in mud | Body buried up to [specific point], only [parts] visible above surface |
| Running away | Legs extended mid-stride, arms pumping, body leaning forward |

---

## Page Image Prompt Template

```python
# From generate_page_images.py
def build_image_prompt(book, page):
    return f"""Single scene illustration: {scene}

CHARACTERS (draw EXACTLY as described - these features are KEY):
{character_block}

COMPOSITION: One cohesive illustration filling the entire canvas.
Full-bleed image with the scene filling edge to edge.

STYLE: {style}

CRITICAL: NO TEXT, NO WORDS, NO LETTERS anywhere. Pure illustration only."""
```

---

## Reference Sheet Structure

```
[1] Character front   [2] Expressions      [3] Character action
[4] Secondary char    [5] KEY HERO SHOT    [6] Props/objects
[7] Setting element   [8] Setting element  [9] Resolution/together
```

**Panel 5 (center) has highest style influence.**

**TIMING:** Write reference prompt LAST, after completing all story pages. Base it on:
- Row 1: YOUR main character (front view, expressions, action pose) with exact visual details
- Row 2: Key objects/secondary characters from YOUR story, KEY MOMENT in center
- Row 3: The actual settings from YOUR story (e.g., backyard, bathroom)

---

## Style Templates by Band

| Band | Style | Mood |
|------|-------|------|
| A | Simple bold shapes, soft watercolor, very minimal detail, warm pastels | Gentle, comforting, bright |
| B | Playful watercolor, expressive characters, vibrant colors | Energetic, fun, adventurous |
| C | Rich watercolor, more detailed characters/settings, dynamic compositions | Exciting, imaginative, engaging |
| D | Sophisticated style, detailed environments, nuanced lighting | Atmospheric, immersive, evocative |

---

## Scene Continuity Rules

Scenes must flow like a movie. Track these across pages:

| What to Track | Rule | Example |
|---------------|------|---------|
| **Physical state** | Persists until changed | Muddy on p4 → still muddy on p5 |
| **Location** | Must show transition | Can't teleport without showing travel |
| **Time of day** | Progress logically | Morning → afternoon → evening |
| **Props** | Stay where placed | Ball in tunnel → still in tunnel until retrieved |
| **Clothing** | Consistent unless changed | Same outfit unless story shows change |
| **Wetness** | Bath = wet when out | Can't be dry immediately after bath |

**The Movie Test:** Could an animator draw continuous motion between your scenes? If there's a logic gap, fix it.

---

## Story Act Detection

Used by `prompt_enhancer.py` for context-aware prompts:

| Position | Act | Emotional Tendency |
|----------|-----|-------------------|
| 0-25% | Setup | Introduction, curiosity |
| 25-60% | Conflict | Struggle, attempts |
| 60-85% | Climax | Peak tension, breakthrough |
| 85-100% | Resolution | Relief, joy, satisfaction |

---

## Validation Checklist

Run before image generation:

```bash
python scripts/validate_book_for_images.py {slug}
```

Manual checks:
- [ ] No placeholder scenes ("Illustration for:")
- [ ] All scenes > 80 characters
- [ ] No negations (except "NO TEXT")
- [ ] Character details match reference prompt
- [ ] WHO/WHERE/WHAT/COMPOSITION/STYLE present
- [ ] "NO TEXT" in every scene

---

## Common Mistakes Quick Fixes

| Symptom | Cause | Fix |
|---------|-------|-----|
| Grid/panel output | Reference is 9-panel, no override | Add "Single scene illustration:" prefix |
| Wrong content appears | Content contamination from reference | Track story_elements, exclude future items |
| Text in images | Missing instruction | Add "NO TEXT, NO WORDS, NO LETTERS" |
| Character inconsistent | Missing character block | Include visual_shorthand in every prompt |
| Vague/wrong scene | Placeholder or too short | Run `generate_scene_descriptions.py` |
| Emotional mismatch | Mood words instead of physical | Use translation table |

---

## Story Prompt Rules (from generate_story.py)

### What Makes a Good Story
| Element | Description |
|---------|-------------|
| **CHARACTER WANT** | Wants something specific and clear |
| **OBSTACLE** | A real problem (not manufactured drama) |
| **TRY-FAIL** | Genuine attempt that fails for a logical reason |
| **RESOLUTION** | Satisfying and earned |
| **CAUSATION** | Each event causes the next (not random scenes) |

### Word Palette Philosophy
```
Treat word lists as INSPIRATION, not constraint.
If a phonics word doesn't fit naturally, DON'T USE IT.
```

### Vocabulary Substitutions
| Too Hard | Use Instead |
|----------|-------------|
| washes | gets, rubs |
| ready | set |
| beautiful | pretty, nice |
| because | so |

### Logic Errors to Avoid
```
BAD:  "He got wet in the sun." (sun doesn't make you wet)
BAD:  "Now Max is not wet." (after a bath? he'd be soaking wet!)
BAD:  "He is wet and red." (why red? makes no sense)

GOOD: "Max jumped in the mud. Mud splashed on his nose!" (cause → effect)
GOOD: "Mom dried Max with a towel. Now his fur was fluffy." (action → result)
```

### Continuity Check
Before each page, ask:
1. What state is the character in from the previous page?
2. What would logically happen next?
3. Does this follow from what just happened?

---

## Script Quick Reference

| Script | Purpose | Command |
|--------|---------|---------|
| `generate_story.py` | Create story + scenes | `python scripts/generate_story.py --level B2 --concept "..." --setting "..."` |
| `generate_scene_descriptions.py` | Fix placeholder scenes | `python scripts/generate_scene_descriptions.py {slug}` |
| `generate_references.py` | Create 9-panel reference | `python scripts/generate_references.py --book {slug}` |
| `generate_page_images.py` | Generate all pages | `python scripts/generate_page_images.py {slug}` |
| `prompt_enhancer.py` | Enhance + review prompts | `python scripts/prompt_enhancer.py {slug} --pages 11,12,13` |
| `validate_book_for_images.py` | Pre-flight validation | `python scripts/validate_book_for_images.py {slug}` |

---

## Review Score Criteria (from prompt_enhancer.py)

| Score | Quality | Action |
|-------|---------|--------|
| 9-10 | Perfect | Generate immediately |
| 7-8 | Good | Minor improvements possible |
| 5-6 | Acceptable | Proceed with caution |
| 3-4 | Problematic | Likely wrong characters/emotions |
| 1-2 | Fail | Will definitely generate incorrectly |

---

## Reference Image Strategies

| Strategy | # Refs | Model | Cost/Page | Best For |
|----------|--------|-------|-----------|----------|
| Single 9-panel | 1 | wan2.6-image | $0.03 | Simple books, proven workflow |
| Multi 3-ref | 3 | wan2.6-image | $0.03 | Better consistency, no contamination |
| Premium 14-ref | 14 | gemini-3-pro | $0.15 | Complex multi-character |

**3-Reference Strategy (cascade, $0.21 to generate):**
1. **Characters** - T2I, establishes the style ($0.15)
2. **Settings** - I2I from characters, no characters in panels ($0.03)
3. **Style** - I2I from characters, abstract only, no story content ($0.03)

See [IMAGE_GENERATION_WORKFLOW.md](IMAGE_GENERATION_WORKFLOW.md#reference-image-strategies) for templates.

---

## Cost Reference

| Model | Type | Cost | Max Refs | Use For |
|-------|------|------|----------|---------|
| nano-banana-pro | T2I | $0.15/img | 0 | Reference sheets, covers |
| wan2.6-image | I2I | $0.03/img | 3 | Pages with reference |
| gemini-2.5-flash | I2I | $0.039/img | 3 | Budget + quality |
| gemini-3-pro | I2I | $0.15/img | 14 | Complex multi-character |

---

## URLs

| Purpose | URL |
|---------|-----|
| Production | https://funbookies.com |
| Read mode | `https://funbookies.com/reader.html?book={slug}` |
| Edit mode | `https://funbookies.com/reader.html?book={slug}&mode=edit` |

---

*See individual docs for full details. This is a quick reference only.*
