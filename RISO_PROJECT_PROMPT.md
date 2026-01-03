# Funbookies Riso Picture Book Project

## Project Goal
Create decodable children's picture books (ages 5-7) designed for **Risograph printing**. Books should look like indie picture books, not educational materials. The phonics scaffolding should be invisible - kids grab these because they look fun.

## Print Partner
**Riso Pop** - Amsterdam risograph studio (https://www.risopop.com/)
- Get their specific specs before final output
- Typical: 2-3 spot colors, A5 or custom zine size, saddle-stitch binding

---

## Part 1: Story Framework

### Phonics Levels (Science of Reading aligned)

| Level | Name | Patterns | Max Words/Page | Target Age |
|-------|------|----------|----------------|------------|
| Yellow | CVC Only | cat, dog, run | 5 | 5-6 |
| Orange | CVC + Digraphs | sh, ch, th, ck | 7 | 6-7 |
| Red | + Blends | bl, cr, st, sp | 8 | 6-7 |
| Purple | + Magic E | make, like, home | 10 | 7-8 |

### Word Types
- **Decodable**: Words kids can sound out (big, run, hid, got, cat, hat, jam)
- **Sight words (Flash)**: Common words to memorize (the, to, a, is, it, we, go, said)
- **Heart words**: Irregular spellings to learn "by heart" (said, was, they)
- **Topic vocabulary**: 3-5 special words for the story topic (volcano, lava, castle)

### Story Structure (Mo Willems / Pete the Cat inspired)

**Character Design:**
- TWO characters with OPPOSING personalities (bold + cautious)
- Each has a CATCHPHRASE ("Let's go!" / "But wait!")
- Simple distinguishing features (red bow, blue bandana, curly tail)

**Emotional Arc (16-20 story pages):**
```
Pages 3-5:   Setup - introduce characters, show want
Pages 6-8:   Action - character pursues goal
Pages 9-10:  TURN - something changes (PAGE TURN SURPRISE)
Pages 11-14: Rising action - tension builds
Pages 15-16: Climax - biggest moment
Pages 17-18: Resolution - safe, happy, proud
```

**Writing Techniques:**
- Repetition with variation: "Run, Gus, run!" / "Run, run, run!"
- Sound effects: "HISS! PUFF! POP!" / "Dash! Rush! Run!"
- Catchphrase callbacks: Use character's phrase at key moments
- Pete the Cat resilience: "Did [Name] stop? No!"
- Short punchy sentences, one idea per page

---

## Part 2: Riso Art Direction

### Design Philosophy
**"Expressive Minimal"** - Mo Willems expressiveness meets Riso aesthetics.
Simple shapes, bold expression, limited spot colors.

### Riso Color Strategy

**2-3 ink approach per book:**
```
Layer 1: BLACK - All outlines, text, details
Layer 2: SPOT COLOR A - Main character color, warm elements
Layer 3: SPOT COLOR B - Secondary character, cool elements/accents
```

**Example palettes:**
- Gus Volcano: Black + Fluorescent Orange + Yellow
- Castle Rats: Black + Fluorescent Pink + Blue
- Jungle: Black + Green + Risofederal Blue

### Image Style for Riso

**DO:**
- Flat color fills (no gradients)
- Bold black outlines (will be separate layer)
- Simple geometric shapes
- High contrast
- Large areas of single color
- Exaggerated expressions
- Minimal backgrounds (saves ink, looks cleaner)

**DON'T:**
- Gradients or soft shading
- Complex textures
- Detailed backgrounds
- Small intricate details (Riso can't resolve)
- More than 3 colors per spread

### Character Design for Riso

Each character needs:
1. **Silhouette recognition** - identifiable as solid shape
2. **One distinguishing feature** in contrasting color
3. **Simple body** - oval/circle shapes, tube limbs
4. **Expressive face** - eyes do most of the work

**Example - Gus the Gecko:**
```
Body: Solid GREEN (spot color)
Outline: BLACK layer
Eyes: WHITE knocked out of green, BLACK pupils
Tail: Distinctive CURLY SPIRAL (recognition feature)
```

---

## Part 3: File Structure

### Project Organization
```
minibooks/
├── src/
│   ├── templates/           # Level-specific constraints
│   │   ├── level_orange.json
│   │   └── ...
│   ├── word_banks.json      # Approved words by phonics level
│   └── book_maker.py        # Story generation with constraints
├── web/books/
│   ├── [book_name].json     # Story data + prompts
│   ├── [book_name]_images/  # Generated PNGs
│   └── [book_name]_riso/    # Separated layers for print
│       ├── black/
│       ├── color_a/
│       └── color_b/
├── reference_images/        # Character/location refs
├── drafts/                  # HTML previews
└── docs/
    ├── art-direction.md
    └── reading-pedagogy-framework.md
```

### Book JSON Structure
```json
{
  "title": "Book Title",
  "level": "orange",
  "riso_colors": {
    "black": "outlines and details",
    "color_a": {"name": "Fluorescent Orange", "pantone": "804", "use": "Gus, lava, warm"},
    "color_b": {"name": "Yellow", "pantone": "Yellow", "use": "highlights, sun"}
  },
  "character": {
    "names": ["Gus"],
    "gus": {
      "species": "gecko",
      "riso_color": "color_a",
      "distinguishing_feature": "curly spiral tail",
      "expression_default": "curious, eyes wide",
      "catchphrase": "Wow! Wow! Wow!"
    }
  },
  "word_list": {
    "decodable": {"cvc": [...], "digraphs": [...]},
    "sight_words": {"flash": [...], "heart": [...]},
    "vocabulary": {"topic": [...], "character": [...]}
  },
  "pages": [
    {
      "page": 1,
      "type": "cover",
      "text": "Gus and the Volcano",
      "beat": "hook",
      "image_prompt": "...",
      "riso_notes": "Gus in ORANGE, volcano in BLACK outline with ORANGE lava glow"
    }
  ]
}
```

---

## Part 4: Image Generation Workflow

### Step 1: Generate Character References
Create reference sheets for each character showing:
- Front view
- Side profile
- Key expressions (happy, worried, excited)
- The distinguishing feature clearly visible

**Prompt template:**
```
Character reference sheet for [NAME] the [ANIMAL].
Simple flat cartoon style, bold black outlines, NO GRADIENTS.
[Description with distinguishing feature].
Show 3 poses on white background.
Designed for Risograph printing - flat colors only, high contrast.
NO TEXT IN IMAGE.
```

### Step 2: Generate Page Images
Use consistent style across all pages:

**Prompt structure:**
```
[SHOT TYPE]: [Scene description]

[Character] shown [position/pose]. [Distinguishing feature visible].
Expression: [specific emotion with details].

Background: [minimal/simple description].

Style: Simple flat cartoon, bold black outlines, flat color fills,
no gradients, no texture, high contrast, designed for Risograph
spot color separation. NO TEXT IN IMAGE.
```

**Shot types to use:**
- WIDE SHOT - establishing scenes, showing scale
- MEDIUM SHOT - action, interaction
- CLOSE-UP - emotions, catchphrase moments
- DYNAMIC/ACTION - chase scenes, movement

### Step 3: Riso Separation
Convert generated images to print-ready layers:

**Option A: Manual in Photoshop/GIMP**
1. Create grayscale layer for BLACK (outlines)
2. Create grayscale layer for each spot color
3. Export as separate PDFs

**Option B: Use separation tools**
- spectrolite.app
- risoseparator.tools
- colorlibrary.ch

**Output specs for Riso Pop:**
- 300 DPI minimum
- Grayscale PDFs per color
- Include registration marks
- Reduce solid areas to 85% opacity
- Add 3mm bleed if full-bleed pages

---

## Part 5: Example Stories

### Story 1: Gus and the Volcano (Orange Level)

**Premise:** Curious gecko Gus climbs a volcano, sees lava, has to run back to safety.
**Emotional arc:** curious → amazed → scared → relieved → proud
**Catchphrase:** "Wow! Wow! Wow!"
**Riso colors:** Black + Fluorescent Orange + Yellow

**Key beats:**
- p3: Gus sat on a rock (setup)
- p5: "I can go up!" (decision)
- p9: Red! Hot! Lava! (PAGE TURN REVEAL)
- p10: "Wow! Wow! Wow!" (catchphrase)
- p14: "Run!" said Gus (turn)
- p18: Did Gus stop? No! (resilience)
- p21: "Wow! Wow! Wow!" (callback)

### Story 2: Rats in the Castle (Orange Level)

**Premise:** Bold Rita and cautious Rico sneak into castle, find jam, escape a cat.
**Characters:** Rita (eager, red bow) + Rico (worried, blue bandana)
**Catchphrases:** "Let's go!" / "But wait!"
**Riso colors:** Black + Fluorescent Pink + Blue

**Key beats:**
- p5-6: Catchphrase contrast ("Let's go!" / "But wait!")
- p9-10: Jam discovery ("Jam! Jam! Jam!")
- p11: PAGE TURN - "But then... a cat!"
- p12: Rico's hero moment - "Run!" (role reversal)
- p14-15: Hiding (Rita in cup, Rico in hat - parallel)
- p20-21: Jam payoff with messy faces ("Yum! Yum! Yum!")

---

## Part 6: Validation Checklist

### Story Text
- [ ] Max words per page within level limit
- [ ] 80%+ words are decodable or sight words
- [ ] Character catchphrases used at key moments
- [ ] Page turn surprises on right-hand pages
- [ ] Repetition patterns for reading practice

### Images
- [ ] Character distinguishing features visible in every image
- [ ] Consistent character proportions across pages
- [ ] Expressions match story beats
- [ ] Flat colors only (no gradients)
- [ ] High contrast for Riso separation
- [ ] NO TEXT in images

### Riso Prep
- [ ] Max 3 colors per book
- [ ] Colors assigned to specific elements
- [ ] Large solid areas at 85% opacity
- [ ] Registration marks added
- [ ] Bleed included for full-bleed pages

---

## Quick Start Commands

```bash
# 1. Set up MuleRouter for image generation
export MULEROUTER_SITE="mulerouter"
export MULEROUTER_API_KEY="your-key"

# 2. Create new book
# - Write story JSON with prompts
# - Generate character references first
# - Generate page images with consistent style
# - Create HTML preview to review

# 3. Prepare for Riso
# - Separate into color layers
# - Export grayscale PDFs per ink
# - Send to Riso Pop with specs
```

---

## Resources

**Phonics:**
- Dolch sight word lists
- Science of Reading research

**Story Craft:**
- Mo Willems' Elephant & Piggie (character contrast, expression)
- Pete the Cat (resilience, repetition, catchphrases)
- Jon Klassen (deadpan humor, minimal backgrounds)

**Riso:**
- Riso Pop Amsterdam: https://www.risopop.com/
- RISOTTO print setup guide: https://risottostudio.com/pages/basic-print-setup
- Color library tester: https://colorlibrary.ch/

**Image Generation:**
- MuleRouter API for Wan2.5 text-to-image
- Use seed values for style consistency
