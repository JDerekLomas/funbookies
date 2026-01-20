# Book Create Skill

Complete workflow for creating curriculum-aligned decodable readers with proper images.

## When to Use

Use `/book-create` when creating a new FunBookies book from scratch. This skill handles:
- Story generation with strict curriculum alignment (85%+ decodability)
- Scene descriptions with WHO/WHERE/WHAT/STYLE format
- Reference sheet generation
- Page image generation with anti-grid prompting
- Validation at each checkpoint

## Usage

```
/book-create --level <level> --concept "<idea>" --setting "<context>" [--title "<title>"]
```

Examples:
- `/book-create --level B1 --concept "A pig who loves mud" --setting "farm"`
- `/book-create --level B4 --concept "A sled race down a hill" --setting "snowy mountain"`
- `/book-create --level B7 --concept "Sailing on a sunny day" --setting "coastal bay"`

## The Four Checkpoints

**NEVER skip checkpoints. Get user approval before proceeding.**

### Checkpoint 1: Story Text (XML)

Generate story as XML with strict curriculum alignment.

#### 1.1 Load Level Constraints

Read `/public/data/level-specs.json` to get:
- `phonicsPatterns` - Extract decodable words
- `wordsPerSentence` - Text density limits
- `pages` - Expected page count
- `decodability` - Target percentage (usually 85%+)

#### 1.2 Build Approved Word List

For the target level, extract ALL words from:
```python
# From level-specs.json constraints.phonicsPatterns
"CVC short a: cat, hat, sat, man, can, bat, rat, map, nap"
→ ["cat", "hat", "sat", "man", "can", "bat", "rat", "map", "nap"]

# Include cumulative sight words
"Previous + my, see" → all previous levels' sight words + my, see
```

**For B-band books, include all words from previous B levels.**

#### 1.3 Generate Story

Write story using ONLY approved words. Output as XML:

```xml
<story>
  <page n="1">
    <text>The big pig sat in the mud.</text>
    <text>She sat and sat.</text>
  </page>
  <page n="2">
    <text>Tim ran to the pig.</text>
    <text>The pig did not zip.</text>
  </page>
</story>
```

#### 1.4 Validate Decodability

Calculate decodability BEFORE proceeding:

```
Total words: 87
Approved words: 74 (85%)
Unknown words: 13
Status: ✅ PASS (≥85%)

Unknown words: [list any words not in approved lists]
```

**If <85%, rewrite using only approved words. DO NOT PROCEED with failing decodability.**

#### 1.5 Checkpoint Output: Story Review Page

**CRITICAL: Show the complete story in a visual layout before proceeding.**

Generate an HTML review page that displays:
1. All story pages laid out in a grid
2. Reference images (character, environment, style)
3. Decodability score and unknown words
4. Page count verification

```html
<!-- Generate and serve via local HTTP server -->
<!-- User must approve story BEFORE any image generation -->
```

**Story Quality Checklist:**
- [ ] Every sentence serves the story (no filler)
- [ ] Genuine emotional arc (not forced)
- [ ] Characters feel real and relatable
- [ ] Natural dialogue (if any)
- [ ] Satisfying ending
- [ ] Appropriate length for level

**Common Problems to Avoid:**
- Too many unnecessary sentences
- Forced/fake emotional beats
- No soul or genuine interest
- Repetitive padding
- Abrupt or unsatisfying endings

Show user:
1. Visual story layout with all pages
2. Reference images alongside
3. Decodability score
4. Ask: **"Does this story feel genuine and engaging? Approve before generating images."**

**DO NOT proceed to image generation until user explicitly approves the story.**

---

### Checkpoint 2: Scene Descriptions

Generate concrete visual prompts for each page.

#### 2.1 Define Characters

Create detailed character definitions:

```
Tim: A round-faced boy (6-7) with brown hair, wearing denim overalls
and a straw sun hat. Freckles on cheeks. Brown work boots.

The Pig: A plump pink pig with droopy ears and a curly tail.
Black spot on left side. Friendly expression.
```

#### 2.2 Scene Description Format

**Every scene MUST follow WHO/WHERE/WHAT/COMPOSITION/STYLE:**

```
Medium shot: Tim, a round-faced boy (6-7) in denim overalls and straw
sun hat, running eagerly across dusty farm ground toward a plump pink
pig with droopy ears. The pig sits contentedly in a patch of shade by
a wooden fence. Bright summer sunlight, warm ochre dirt, green grass
in background. One cohesive illustration filling the entire canvas.
Children's book style with bold shapes and warm colors. NO TEXT anywhere
in image.
```

**Required elements:**
| Element | Description | Example |
|---------|-------------|---------|
| Shot type | Wide/Medium/Close-up | "Medium shot:" |
| WHO | Character + identifiers | "Tim, a round-faced boy (6-7) in denim overalls" |
| WHERE | Setting + lighting | "dusty farm ground, bright summer sun" |
| WHAT | Action from text | "running toward the pig" |
| COMPOSITION | Anti-grid instruction | "One cohesive illustration filling entire canvas" |
| STYLE | Art direction | "Children's book style with bold shapes" |
| NO TEXT | Required suffix | "NO TEXT anywhere in image." |

#### 2.3 CRITICAL: No Negations

**WRONG:** "The pig is alone, no other animals around, without Tim"
**RIGHT:** "The pig sits contentedly in a muddy patch" (only describe what IS there)

Negations ("no", "not", "without", "never") cause models to generate the mentioned element.

#### 2.4 Output as XML

```xml
<scenes>
  <page n="1">
    <scene>Medium shot: Tim, a round-faced boy (6-7) in denim overalls and straw sun hat, standing by wooden fence looking at plump pink pig sitting in mud. Bright summer farmyard, red barn in background. One cohesive illustration filling entire canvas. Warm children's book style. NO TEXT anywhere in image.</scene>
    <image_prompt>Single scene illustration: Tim, a round-faced boy (6-7) in denim overalls and straw sun hat, standing by wooden fence looking at plump pink pig sitting in mud. The pig has droopy ears and a curly tail with a black spot on left side. Bright summer farmyard with dusty ground, red barn visible in background, blue sky with white clouds. One cohesive illustration filling the entire canvas. Warm friendly children's book illustration style with bold shapes, bright colors, and gentle outlines. CRITICAL: NO TEXT, NO WORDS, NO LETTERS anywhere in image.</image_prompt>
  </page>
</scenes>
```

#### 2.5 Checkpoint Output

Show user:
1. Table of all scenes with page text
2. Character definitions
3. Ask: "Do these scenes look concrete and visual? Ready to generate reference sheet?"

---

### Checkpoint 3: Reference Images

Generate individual reference images for characters, environments, and style.

#### 3.1 Add Character Data to Book JSON

Ensure book JSON has character data with `visual_shorthand`:

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

#### 3.2 Individual Reference Structure

Generate separate reference images (not a single 9-panel composite):

```
{slug}_multi/
├── Character References
│   ├── char_{name}_front.png      # Front view, full body
│   ├── char_{name}_side.png       # Side view, in motion
│   └── char_{name}_expression.png # Expression studies
│
├── Environment References
│   ├── env_day.png                # Daytime setting
│   └── env_night.png              # Nighttime (if needed)
│
└── Style Reference
    └── style_palette.png          # Color palette & style
```

**Why individual refs?**
- wan2.6-image supports up to 3 references per generation
- Select most relevant refs per page (character + env + style)
- No grid artifacts from composite references

#### 3.3 Generate Reference Images

Use multi_ref_experiment.py:

```bash
uv run python scripts/multi_ref_experiment.py <slug> --generate-refs
```

This generates all character/environment/style references based on book JSON.

Save to: `/public/books/references/{slug}_multi/`

#### 3.4 Checkpoint Output

Show user:
1. All generated reference images
2. Ask: "Do the characters look consistent? Environments correct? Ready for page images?"

---

### Checkpoint 4: Page Images

Generate all story page images with multi-reference style transfer.

#### 4.1 Split-3ref Strategy

For each page, select 3 references:
1. **Character ref** - Front view of main character in scene
2. **Environment ref** - Day or night environment
3. **Style ref** - Color palette and style

```python
# Example ref selection for a page
refs = [
    "char_tim_front.png",    # Main character
    "env_day.png",           # Daytime farm
    "style_palette.png"      # Style consistency
]
```

wan2.6-image supports up to 3 references - this maximizes style transfer.

#### 4.2 Generate Images

Use multi_ref_experiment.py with split-3ref strategy:

```bash
uv run python scripts/multi_ref_experiment.py <slug> \
  --strategies split-3ref \
  --pages 1,2,3,4,5,6,7,8,9,10,11,12
```

Or generate all pages:
```bash
uv run python scripts/multi_ref_experiment.py <slug> --strategies split-3ref --all
```

Cost: ~$0.03 per page with wan2.6-image.

#### 4.3 Negative Prompts

Use story_elements to prevent contamination:

```bash
--negative-prompt "text, words, letters, watermark, {exclusions}"
```

Add elements that shouldn't appear yet (e.g., airplane before page 5).

#### 4.4 Checkpoint Output

Show user:
1. Sample images (cover + 2-3 story pages)
2. References used per page
3. Any failed generations
4. Ask: "Do images match the text? Any need regeneration?"

---

## File Locations

| Type | Path |
|------|------|
| Book JSON | `/public/books/{slug}.json` |
| Character refs | `/public/books/references/{slug}_multi/char_{name}_*.png` |
| Environment refs | `/public/books/references/{slug}_multi/env_*.png` |
| Style ref | `/public/books/references/{slug}_multi/style_palette.png` |
| Page Images | `/public/books/images/{slug}/page{NN}.png` |
| Cover | `/public/images/covers/{slug}.png` |

## Validation Commands

```bash
# Validate curriculum alignment
python scripts/generate_book_xml.py --level B1 --concept "..." --validate-only

# Validate scene descriptions
python scripts/validate_book_for_images.py <slug>

# Check decodability of existing book
python -c "
import json
# ... decodability check code
"
```

## Common Mistakes to Avoid

### 1. Lazy Scene Descriptions
**WRONG:** `"Illustration for: Tim ran to the pig."`
**RIGHT:** Full WHO/WHERE/WHAT/COMPOSITION/STYLE format

### 2. Missing Character Data
**WRONG:** No `characters` object with `visual_shorthand` in book JSON
**RIGHT:** Add detailed character data before generating refs

### 3. Using Negations in Prompts
**WRONG:** "The pig is alone, no tractor visible"
**RIGHT:** Only describe what IS in the scene

### 4. Skipping Decodability Check
**WRONG:** Generating images for a story with 50% decodability
**RIGHT:** Validate 85%+ decodability before any image generation

### 5. Words Not in Level Specs
**WRONG:** Using "mud", "hot", "step" in B1 (these are B2 patterns)
**RIGHT:** Only use words from level-specs.json for target level

### 6. Missing Style Reference
**WRONG:** Only using character refs (inconsistent colors/style)
**RIGHT:** Always include style_palette.png as one of the 3 refs

## Quick Reference: Phonics by Level

| Level | Focus | Example Words |
|-------|-------|---------------|
| B1 | CVC short a, i | cat, sat, big, pig, sit, hit |
| B2 | CVC short o, u, e | hot, mud, sun, run, bed, red |
| B3 | Final blends + FLOSS | and, best, jump, off, bell |
| B4 | Initial blends | sled, swim, trip, frog, stop |
| B5 | Digraphs | ship, chat, this, when, ring |
| B6 | Silent e (CVCe) | cake, like, home, cute |
| B7 | Vowel teams | rain, day, feet, boat, snow |

## Review URLs

After deployment:
- Read mode: `https://funbookies.com/reader.html?book={slug}`
- Edit mode: `https://funbookies.com/reader.html?book={slug}&mode=edit`
