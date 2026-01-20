# Image Generation Workflow

An idealized abstraction of how book images are created.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CONTENT LAYER                                      │
│                                                                             │
│   ┌─────────────┐                                                           │
│   │  Book JSON  │  Source of truth for all content                         │
│   │             │                                                           │
│   │  - title    │                                                           │
│   │  - level    │                                                           │
│   │  - pages[]  │──┐                                                        │
│   │    - text   │  │                                                        │
│   │    - scene  │  │  Scene descriptions drive image generation            │
│   │             │  │                                                        │
│   └─────────────┘  │                                                        │
│                    ▼                                                        │
└────────────────────┼────────────────────────────────────────────────────────┘
                     │
                     │
┌────────────────────┼────────────────────────────────────────────────────────┐
│                    │         STYLE LAYER                                    │
│                    ▼                                                        │
│   ┌─────────────────────────────────┐                                       │
│   │     Style Template Selection    │                                       │
│   │                                 │                                       │
│   │  Band A → Simple, pastel       │                                       │
│   │  Band B → Playful, vibrant     │                                       │
│   │  Band C → Rich, detailed       │                                       │
│   │  Band D → Sophisticated        │                                       │
│   │                                 │                                       │
│   │  + Book-specific overrides     │                                       │
│   │    (sci-fi, coastal, garden)   │                                       │
│   └────────────────┬────────────────┘                                       │
│                    │                                                        │
│                    ▼                                                        │
│   ┌─────────────────────────────────┐                                       │
│   │   Individual Reference Images   │  ← TEXT-TO-IMAGE                     │
│   │   (multiple separate images)    │    (nano-banana-pro)                 │
│   │                                 │                                       │
│   │  CHARACTER REFS:                │    Per character:                    │
│   │  ┌─────┐ ┌─────┐ ┌─────┐       │    - Front view                      │
│   │  │front│ │side │ │expr │       │    - Side view                       │
│   │  └─────┘ └─────┘ └─────┘       │    - Expressions                     │
│   │                                 │                                       │
│   │  ENVIRONMENT REFS:              │    Settings:                         │
│   │  ┌─────┐ ┌─────┐               │    - Day scene                       │
│   │  │ day │ │night│               │    - Night scene                     │
│   │  └─────┘ └─────┘               │                                       │
│   │                                 │                                       │
│   │  STYLE REF:                     │    Style palette:                    │
│   │  ┌─────┐                        │    - Colors, textures, mood          │
│   │  │style│                        │                                       │
│   │  └─────┘                        │                                       │
│   │                                 │                                       │
│   └────────────────┬────────────────┘                                       │
│                    │                                                        │
│                    │  3 refs selected per page for consistency              │
│                    ▼                                                        │
└────────────────────┼────────────────────────────────────────────────────────┘
                     │
                     │
┌────────────────────┼────────────────────────────────────────────────────────┐
│                    │         IMAGE LAYER                                    │
│                    │                                                        │
│         ┌──────────┴──────────┐                                             │
│         │                     │                                             │
│         ▼                     ▼                                             │
│   ┌───────────┐         ┌───────────┐                                       │
│   │   Cover   │         │   Pages   │                                       │
│   │   Image   │         │  Images   │                                       │
│   └─────┬─────┘         └─────┬─────┘                                       │
│         │                     │                                             │
│         │  IMAGE-TO-IMAGE     │  IMAGE-TO-IMAGE                             │
│         │  (wan2.6-image)     │  (wan2.6-image)                             │
│         │                     │                                             │
│         │  Inputs:            │  Inputs:                                    │
│         │  - 3 refs (char,    │  - 3 refs (char, env, style)                │
│         │    env, style)      │  - Page scene prompt                        │
│         │  - Cover scene      │  - "NO TEXT"                                │
│         │  - "NO TEXT"        │                                             │
│         │                     │                                             │
│         │  Output:            │  Output:                                    │
│         │  Pure illustration  │  Pure illustration                          │
│         │  (no title baked)   │  (no text baked)                            │
│         │                     │                                             │
│         ▼                     ▼                                             │
│   ┌───────────┐         ┌───────────┐                                       │
│   │  /images/ │         │  /books/  │                                       │
│   │  covers/  │         │  images/  │                                       │
│   │  {slug}.  │         │  {slug}_  │                                       │
│   │  png      │         │  page{N}. │                                       │
│   │           │         │  png      │                                       │
│   └─────┬─────┘         └─────┬─────┘                                       │
│         │                     │                                             │
└─────────┼─────────────────────┼─────────────────────────────────────────────┘
          │                     │
          │                     │
┌─────────┼─────────────────────┼─────────────────────────────────────────────┐
│         │   PRESENTATION LAYER│                                             │
│         │                     │                                             │
│         ▼                     ▼                                             │
│   ┌─────────────────────────────────┐                                       │
│   │           Reader UI             │                                       │
│   │                                 │                                       │
│   │  ┌─────────────────────────┐    │                                       │
│   │  │                         │    │                                       │
│   │  │    [Cover Image]        │    │   Image from filesystem               │
│   │  │                         │    │                                       │
│   │  │  ┌───────────────────┐  │    │                                       │
│   │  │  │   "BOOK TITLE"    │  │    │   Text overlay from JSON              │
│   │  │  └───────────────────┘  │    │   (rendered by UI, not in image)      │
│   │  │                         │    │                                       │
│   │  └─────────────────────────┘    │                                       │
│   │                                 │                                       │
│   │  Benefits of separation:        │                                       │
│   │  - Consistent typography        │                                       │
│   │  - Easy title changes           │                                       │
│   │  - Localization possible        │                                       │
│   │  - Cleaner illustrations        │                                       │
│   └─────────────────────────────────┘                                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## The Pipeline

```
Book XML (generate_book_xml.py)
    │
    ├──► Story + Scenes ──► Book JSON (xml_to_book_json.py)
    │                              │
    │                              ├──► Add character data (visual_shorthand)
    │                              │
    │                              ▼
    │                       ┌─────────────────────────────────────┐
    │                       │  Individual Refs (multi_ref_exp.py) │
    │                       │  --generate-refs                    │
    │                       │                                     │
    │                       │  ┌──────────┐ ┌──────────┐         │
    │                       │  │ char_*   │ │ env_*    │         │
    │                       │  │ front    │ │ day      │         │
    │                       │  │ side     │ │ night    │         │
    │                       │  │ expr     │ └──────────┘         │
    │                       │  └──────────┘ ┌──────────┐         │
    │                       │               │ style_   │         │
    │                       │               │ palette  │         │
    │                       │               └──────────┘         │
    │                       └─────────────────┬───────────────────┘
    │                                         │
    │                                         │ Select 3 refs per page
    │                                         ▼
    ├──► Cover Scene ────────────────────────►├──► Cover (I2I, wan2.6)
    │                                         │
    └──► Page Scenes ────────────────────────►└──► Pages (I2I, wan2.6)
```

## Key Principles

### 1. Separation of Content and Presentation
- **Content** (text, titles) lives in JSON
- **Images** are pure illustrations
- **UI** composes them together at runtime

### 2. Style Consistency via Multi-Ref
- Individual reference images per book (character, environment, style)
- 3 refs selected per page using split-3ref strategy
- Character refs ensure visual consistency across pages
- Environment refs maintain setting coherence
- Style ref locks color palette and mood

### 3. No Baked Text
- Images contain NO text, titles, or words
- Text is overlaid by the reader UI
- Allows typography consistency and easy updates

### 4. Level-Appropriate Styles

| Band | Base Style | Mood |
|------|------------|------|
| A | Simple bold shapes, soft watercolor, very minimal detail, warm pastel colors, toddler-friendly | Gentle, comforting, bright |
| B | Playful watercolor, expressive characters, vibrant colors, child-friendly art style | Energetic, fun, adventurous |
| C | Rich watercolor, more detailed characters/settings, dynamic compositions | Exciting, imaginative, engaging |
| D | Sophisticated style, detailed environments, nuanced lighting, chapter book aesthetic | Atmospheric, immersive, evocative |

**Book-Specific Overrides** (in `generate_references.py`):
- `d1-the-lighthouse-keeper`: Coastal watercolor, muted blues, sunset oranges
- `d2-the-hidden-garden`: Lush botanical, secret garden aesthetic
- `d4-signals-from-kepler`: Science fiction, deep space blues/purples
- `c1_knight_quest`: Medieval fantasy, castle/forest settings
- See script for 30+ additional book-specific styles

## File Structure

```
public/
├── books/
│   ├── {slug}.json              # Book content
│   ├── references/
│   │   ├── {slug}_reference.png # Legacy 9-panel (deprecated)
│   │   └── {slug}_multi/        # Individual refs (preferred)
│   │       ├── char_{name}_front.png
│   │       ├── char_{name}_side.png
│   │       ├── char_{name}_expression.png
│   │       ├── env_day.png
│   │       ├── env_night.png
│   │       ├── style_palette.png
│   │       └── manifest.json
│   └── images/
│       └── {slug}/
│           └── page{NN}.png     # Page illustrations
│
└── images/
    └── covers/
        └── {slug}.png           # Cover illustrations
```

## Models Used

| Step | Model | Type | Why |
|------|-------|------|-----|
| Individual Refs | `nano-banana-pro` | Text-to-Image | High quality character/env refs |
| Covers | `wan2.6-image` | Image-to-Image | 3 refs for style transfer |
| Pages | `wan2.6-image` | Image-to-Image | 3 refs for style transfer |

### Available I2I Models (via fal.ai)

| Model | Price | Max Refs | Best For |
|-------|-------|----------|----------|
| `wan2.6-image` | $0.03/img | 3 | Budget style transfer |
| `flux-dev-i2i` | $0.03/MP | 1 | Strength control |
| `flux-kontext-pro` | $0.04/img | 1 | Natural language edits |
| `flux-kontext-max` | $0.08/img | 3 | Premium quality |
| `gemini-2.5-flash` | $0.039/img | 3 | Fast, good quality |
| `gemini-3-pro` | $0.15/img | **14** | Best character consistency |
| `z-image-turbo` | $0.005/MP | 1 | Bulk budget generation |

**Recommendation:**
- Use `wan2.6-image` for most pages (80% cheaper than alternatives)
- Use `gemini-3-pro` when character consistency is critical (complex multi-character scenes)
- Use `z-image-turbo` for draft/preview generation

### Model Selection Rationale

**High-Quality T2I for References** (`nano-banana-pro` or `gpt-image-1`):
- Reference sheets are the foundation - quality matters most here
- Better prompt adherence for complex 9-panel layouts
- Cleaner character designs that propagate to all derived images
- Worth the extra cost since each reference generates many covers/pages
- **One image = 9 panels** (3x3 grid in single generation)

**Image-to-Image (`wan2.6-image`)** for covers/pages:
- Reference sheet provides style consistency
- Scene description provides content
- Model transfers style from reference to new scene
- Faster and cheaper for high-volume page generation

### API Endpoints

```
Reference (preferred): /vendors/google/v1/nano-banana-pro/generation
Reference (alt):       OpenAI gpt-image-1 / DALL-E
Covers:                /vendors/alibaba/v1/wan2.6-image/generation
Pages:                 /vendors/alibaba/v1/wan2.6-image/generation
```

### Quality vs Speed Tradeoff

```
                    Quality
                       ▲
                       │
   gpt-image-1  ●      │
   nano-banana  ●      │      ← Use for REFERENCE SHEETS
                       │        (1 per book, high impact)
                       │
      wan2.6    ●      │      ← Use for COVERS/PAGES
                       │        (many per book, need speed)
                       │
                       └──────────────────────► Speed/Cost
```

## Generation Commands

```bash
# Step 1: Generate book XML with story and scenes
python scripts/generate_book_xml.py \
  --level B1 \
  --concept "Story concept" \
  --setting "Setting description" \
  --title "Book Title" \
  --output /tmp/book.xml

# Step 2: Convert XML to JSON
python scripts/xml_to_book_json.py /tmp/book.xml

# Step 3: Add character data to JSON (manual step)
# Edit public/books/{slug}.json to add characters with visual_shorthand

# Step 4: Generate individual reference images
python scripts/multi_ref_experiment.py {slug} --generate-refs

# Step 5: Generate pages using split-3ref strategy
python scripts/multi_ref_experiment.py {slug} --strategies split-3ref

# Alternative: Generate all pages at once
python scripts/multi_ref_experiment.py {slug} --strategies split-3ref --pages all
```

## Prompt Writing Best Practices

### Single Image Output (Critical for I2I)

When using image-to-image with a 9-panel reference sheet, models often copy the grid layout into outputs. **Strongly emphasize single-image composition:**

**Add to EVERY page/cover prompt:**
```
COMPOSITION: One cohesive illustration filling the entire canvas.
Full-bleed image with the scene filling edge to edge.
```

**Example page prompt:**
```
A small hermit crab discovers a glowing white shell in a tide pool at dawn.

Style: Match the reference image - soft watercolor, rounded shapes,
warm dawn palette.

COMPOSITION: Single full-bleed illustration, scene fills the entire canvas.
```

**Why this happens:** The I2I model attends to structural elements in the reference image. A 3x3 grid becomes a strong compositional prior. Emphasizing "full-bleed" and "fills entire canvas" helps override this.

---

### Never Mention Unwanted Concepts

Text-to-image models attend to concepts even when negated. Saying "no ball" makes the model MORE likely to generate a ball - the word "ball" activates that concept regardless of negation.

**The rule: If you don't want it, don't mention it at all.**

**Bad (mentions unwanted concept):**
- "Child playing, no ball" → will likely include a ball
- "Nature is alive even without rain" → will likely show rain
- "Clear sky with no clouds" → will likely show clouds
- "Single image, not a grid" → may still create a grid

**Good (describes only what you want):**
- "Child playing with a kite"
- "Dry dirt trail under overcast gray sky"
- "Clear blue sky"
- "One cohesive illustration filling the entire canvas"

**Note:** Our models do not support a `negative_prompt` parameter. The only solution is to describe what IS there, never what isn't.

### Examples

| What You Want | Bad Prompt | Good Prompt |
|---------------|------------|-------------|
| Dry weather | "No rain" | "Dry overcast day, gray clouds" |
| Single scene | "Not a grid" | "One illustration filling the frame" |
| Empty hands | "No ball in hands" | "Hands at sides" |
| Calm water | "No waves" | "Still, glassy water" |

## Reference Image Content Contamination

**Problem:** When using image-to-image (wan2.6-image) with a 9-panel reference sheet, the model doesn't just copy style—it also bleeds content from the reference into outputs.

Example: If the reference shows airplanes in panels 5-7, airplane elements may appear in pages that should only show tractors.

**Solutions:**

### Option 1: Panel Extraction
Extract relevant panels and use only those for each scene:
```python
# For tractor scenes (pages 1-5), use only panels 1-4 from reference
# For airplane scenes (pages 6-10), use only panels 5-7 from reference
reference_panel = extract_panel(reference_image, panel_number)
```

### Option 2: Style-Only Reference
Create a reference image that captures ONLY style elements:
- Color palette swatches
- Brush texture samples
- Character face studies (no story context)
- No narrative scenes that could contaminate

### Option 3: Text-to-Image for All Pages
Use nano-banana-pro (text-to-image) for every page with detailed style description:
```
"[Scene description]. Warm watercolor style with soft edges, muted earthy
palette (sage green, terracotta, warm cream), friendly rounded character
shapes, gentle natural lighting."
```

## Story Progression-Aware Negative Prompts

Compute negative prompts dynamically based on what appears LATER in the story:

```python
def get_negative_prompt(page_number, story_elements):
    """
    Exclude story elements that haven't been introduced yet.
    """
    negative = ["text", "words", "letters", "watermark"]

    for element, intro_page in story_elements.items():
        if page_number < intro_page:
            negative.append(element)

    return ", ".join(negative)

# Example usage:
story_elements = {
    "airplane": 6,      # Airplane first appears on page 6
    "flying": 6,
    "clouds": 6,
    "farmhouse": 10     # Farmhouse first appears on page 10
}

# For page 3: "text, words, letters, watermark, airplane, flying, clouds, farmhouse"
# For page 7: "text, words, letters, watermark, farmhouse"
```

## Scene Description Quality Checklist

Before generating, verify each scene description has:

- [ ] **CHARACTER** with visual identifiers (age, hair, clothing)
- [ ] **SETTING** with cultural specificity (not generic "farmhouse")
- [ ] **ACTION** that matches the page text exactly
- [ ] **CONTEXT** with only elements relevant to THIS page
- [ ] **STYLE** instruction at the end
- [ ] **NO** abstract/mood language ("dreamy", "magical feeling")
- [ ] **NO** negations ("no airplane", "without the tractor")
- [ ] **NO** future story references ("about to imagine")

## Prompt Enhancement Pipeline

For complex books or problematic pages, use `prompt_enhancer.py`:

```bash
python scripts/prompt_enhancer.py {slug} --pages 11,12,13
```

### Pipeline Stages

1. **Story Context Analysis**
   - Determines narrative act (setup 0-25%, conflict 25-60%, climax 60-85%, resolution 85-100%)
   - Gets emotional beat from story_bible
   - Extracts previous/next page context

2. **Character Presence Logic**
   - Extracts all characters from book
   - Determines who MUST be in scene (from page text)
   - Determines who MUST NOT be in scene (exclusion list)
   - Adds explicit "DO NOT INCLUDE" instructions

3. **Emotional → Physical Translation**
   - Converts mood words to visual descriptions
   - "scared" → "eyes wide open, mouth agape, eyebrows raised"
   - "happy" → "wide smile showing teeth, eyes crinkled, cheeks raised"

4. **LLM Review & Scoring**
   - Validates prompt quality (1-10 scale)
   - Detects common issues
   - Suggests fixes for low scores (<7)

### Output Format

```json
{
  "enhanced_prompt": "Full physical prompt",
  "characters_included": ["Name1", "Name2"],
  "characters_excluded": ["Name3"],
  "physical_descriptions": ["detail 1", "detail 2"],
  "recommended_panels": [1, 5],
  "review_score": 8,
  "issues": []
}
```

## Character Consistency Techniques

For books with recurring characters, maintaining visual consistency is critical. Different models offer varying capabilities.

### Model Comparison for Character Consistency

| Model | Max Refs | Best For |
|-------|----------|----------|
| `gemini-3-pro` | 14 | Multi-character books, complex scenes |
| `wan2.6-image` | 3 | Simple style transfer, single character |
| `flux-kontext-max` | 3 | Natural language edits |
| `gemini-2.5-flash` | 3 | Budget option with good consistency |

### Multi-Reference Strategy (Gemini 3 Pro)

Gemini 3 Pro / Nano Banana Pro supports up to **14 reference images** with role-based assignments:

```
Recommended allocation:
├── Images 1-5:  Character references (poses, expressions, angles)
├── Images 6-8:  Object/prop references (recurring items)
├── Images 9-11: Environment references (settings)
└── Images 12-14: Style references (color palette, mood)
```

### Prompting for Character Consistency

**1. Reference-Based Prompting:**
```
Draw [CHARACTER NAME] EXACTLY as shown in Image 1.
[Character] has [DISTINCTIVE FEATURES - be specific].
The character MUST have [KEY FEATURE] in every frame.
```

**2. Visual Shorthand in Book JSON:**
```json
{
  "characters": {
    "flicker": {
      "name": "Flicker",
      "visual_shorthand": "tiny golden-green firefly with bright amber glow, friendly expression",
      "distinctive_features": ["amber light (KEY)", "tiny size fits in palm", "translucent wings"]
    }
  }
}
```

**3. Layered Prompt Structure:**
```
SCENE: [What's happening in this page]

CHARACTERS (CRITICAL - draw EXACTLY as described):
- Flicker: tiny golden-green firefly with amber glow | MUST HAVE: amber light, tiny size

STYLE: warm watercolor, soft edges, children's book

CONSTRAINTS: No text, maintain character proportions from reference
```

### Identity Anchoring Technique

For maximum consistency across pages:

1. **Create a character reference sheet** with:
   - Front view, 3/4 view, profile
   - Key expressions (happy, sad, surprised)
   - Size reference (next to common objects)

2. **Use explicit size relationships:**
   - "Flicker is tiny, fits in a child's palm"
   - "The mouse is small enough to sit on a leaf"

3. **Reference previous pages:**
   - "Character appears exactly as in page 3"

### Batch Experiment for Model Comparison

Use `batch_experiment.py` to compare model output across a full book:

```bash
# Compare default models
python scripts/batch_experiment.py flicker-the-firefly

# Include premium models
python scripts/batch_experiment.py flicker-the-firefly --include-premium

# Test specific pages
python scripts/batch_experiment.py flicker-the-firefly --pages 1,5,10

# Dry run to preview
python scripts/batch_experiment.py flicker-the-firefly --dry-run
```

Results are saved to `experiments/{book}/{timestamp}/` with:
- Side-by-side comparison HTML
- Per-model cost breakdown
- Generation timing data

### Character Consistency Helper

Use the helper function in `fal_client.py`:

```python
from fal_client import build_character_consistent_prompt, ImageClient

prompt = build_character_consistent_prompt(
    scene="Flicker flies over the moonlit pond",
    characters={
        "Flicker": {
            "visual_shorthand": "tiny golden-green firefly with bright amber glow",
            "distinctive_features": ["amber light (KEY)", "tiny size", "friendly expression"],
        }
    },
    style="warm watercolor, soft edges, children's book",
    reference_assignments={"Flicker": 1}  # Image 1 is Flicker's reference
)

client = ImageClient()
result = client.generate_with_reference(
    prompt=prompt,
    reference_images=["ref_flicker_front.png", "ref_flicker_side.png", "ref_style.png"],
    model="gemini-3-pro",
)
```

## Reference Image Strategies

### Current: Single 9-Panel Reference Sheet

The **production workflow** uses a single 9-panel reference sheet per book:

```
┌─────────────────────────────────────────┐
│  [1] Char     [2] Char     [3] Char    │
│      Front        Expr         Action   │
├─────────────────────────────────────────┤
│  [4] Char2/   [5] **HERO** [6] Setting │
│      Prop         SHOT                  │
├─────────────────────────────────────────┤
│  [7] Setting  [8] Setting  [9] Together│
│      Day          Night                 │
└─────────────────────────────────────────┘
```

**Pros:** Simple, one generation per book, proven workflow
**Cons:** Content contamination (story elements bleed into pages), limited style control

**Scripts:**
- `generate_references.py` - Creates 9-panel sheets
- `generate_page_images.py` - Uses single reference for all pages

**Storage:** `public/books/references/{slug}_reference.png`

---

### Target: Multi-Reference Strategy (3 refs)

Models like `wan2.6-image` support up to **3 reference images**. This enables specialized references:

```
Reference 1: CHARACTER SHEET
┌─────────────────────────────┐
│ [Front] [Side] [3/4 view]  │
│ [Happy] [Sad]  [Surprised] │
│ [Action1] [Action2] [Size] │
└─────────────────────────────┘

Reference 2: SETTINGS SHEET
┌─────────────────────────────┐
│ [Day exterior] [Night]     │
│ [Interior 1]   [Interior 2]│
│ [Weather]      [Mood]      │
└─────────────────────────────┘

Reference 3: STYLE SHEET
┌─────────────────────────────┐
│ Color palette swatches     │
│ Texture samples            │
│ Lighting examples          │
└─────────────────────────────┘
```

**Pros:** No content contamination, better character consistency, fine-grained control
**Cons:** 3x reference generation cost, more complex workflow

**Scripts (planned):**
- `generate_references.py --strategy multi` - Creates 3 specialized sheets
- `generate_page_images.py --refs 3` - Uses all 3 references

**Storage:** `public/books/references/{slug}_multi/`
- `{slug}_characters.png`
- `{slug}_settings.png`
- `{slug}_style.png`

---

### Premium: 14-Reference Strategy (Gemini 3 Pro)

For books requiring maximum consistency (complex multi-character stories), `gemini-3-pro` supports **14 reference images**:

```
Images 1-5:   Individual character images (not sheets)
              - char1_front.png, char1_side.png, char1_happy.png
              - char2_front.png, char2_side.png

Images 6-8:   Key objects/props
              - prop_ball.png, prop_hat.png, prop_wagon.png

Images 9-11:  Environment references
              - env_backyard.png, env_bedroom.png, env_kitchen.png

Images 12-14: Style references
              - style_palette.png, style_texture.png, style_lighting.png
```

**Cost:** $0.15/page (vs $0.03 for wan2.6-image)
**Use when:** Multi-character books, critical consistency needs

---

### Reference Type Templates

#### Character Sheet Prompt
```
9-PANEL CHARACTER REFERENCE for [Name]:

Row 1 - Views:
[1] [Name] front view, full body, arms at sides, neutral expression
[2] [Name] side profile, walking pose
[3] [Name] 3/4 view, slight smile

Row 2 - Expressions:
[4] [Name] happy, wide smile, eyes crinkled
[5] [Name] sad, downturned mouth, drooping posture
[6] [Name] surprised, eyes wide, mouth O-shaped

Row 3 - Actions:
[7] [Name] running, legs mid-stride
[8] [Name] sitting, relaxed pose
[9] [Name] with [key prop], size reference

CRITICAL: Same character in ALL panels. Consistent [distinctive features].
Style: [art style]. NO TEXT anywhere.
```

#### Settings Sheet Prompt
```
9-PANEL SETTINGS REFERENCE for [Book Title]:

Row 1 - Exterior:
[1] [Main location] exterior, bright daylight
[2] Same location, golden hour sunset lighting
[3] Same location, blue hour/dusk

Row 2 - Interior:
[4] [Interior space 1] with warm lighting
[5] [Interior space 2] cozy atmosphere
[6] Detail shot of [key furniture/object]

Row 3 - Atmosphere:
[7] Weather: [sunny/cloudy/rainy] sky
[8] Nature elements: [trees/flowers/grass]
[9] Mood shot: [overall feeling of story]

Consistent color palette and art style across all panels.
Style: [art style]. NO TEXT anywhere.
```

#### Style Sheet Prompt
```
9-PANEL STYLE REFERENCE - Color and Texture:

Row 1 - Color Palette:
[1] Primary color swatch: [color name and hex]
[2] Secondary colors: [2-3 accent colors]
[3] Neutral tones: [background/shadow colors]

Row 2 - Textures:
[4] Brush stroke sample: [watercolor/gouache/etc]
[5] Character skin/fur texture close-up
[6] Background texture: [grass/sky/wood]

Row 3 - Lighting:
[7] Warm lighting example (golden, cozy)
[8] Cool lighting example (blue, calm)
[9] Dramatic lighting (contrast, shadow)

Abstract swatches and samples only. No characters or story elements.
Style: [art style]. NO TEXT anywhere.
```

---

### Choosing a Strategy

| Book Type | Recommended Strategy | Cost/Page | Quality |
|-----------|---------------------|-----------|---------|
| Simple (1 char, few settings) | Single 9-panel | $0.03 | Good |
| Standard (1-2 chars, varied settings) | Multi 3-ref | $0.03 | Better |
| Complex (3+ chars, critical consistency) | 14-ref Gemini | $0.15 | Best |

---

## Current Status

| Component | Status |
|-----------|--------|
| Book JSONs | 48 books with scene descriptions |
| Reference Images | 47 generated (single 9-panel) |
| Cover Images | 48 generated |
| Page Images | 2 books fully generated |
| Multi-ref support | Documented, scripts need update |

## Edit Mode & Image Versioning

The reader includes an edit mode for iterating on images directly in the browser.

### Accessing Edit Mode

```
https://funbookies.com/reader.html?book={slug}&mode=edit
```

Or click "Edit" in the top-right corner of the reader.

### Edit Mode Features

1. **Prompt Editor** - Edit image prompts for any page
2. **Reference Selection** - Choose between reference image versions (v1, v2, v3)
3. **Model Selection** - Choose generation model:
   - `wan2.6-image` - Image-to-image with reference (recommended)
   - `wan2.6-t2i` - Text-to-image only
   - `nano-banana-pro` - High-quality text-to-image
4. **Image Versioning** - Save multiple versions and switch between them

### Image Versioning System

Images are **automatically saved** to Vercel Blob immediately after generation (no hotlinking to MuleRouter):

```
Vercel Blob Storage:
books/{slug}/page01_v1.png
books/{slug}/page01_v2.png
books/{slug}/page01_v3.png
```

**Book JSON stores versions:**
```json
{
  "pages": [{
    "page": 1,
    "image": "https://blob.vercel-storage.com/books/slug/page01_v2.png",
    "image_versions": [
      { "url": "..._v1.png", "version": 1, "created_at": "..." },
      { "url": "..._v2.png", "version": 2, "created_at": "..." }
    ]
  }]
}
```

**Workflow:**
1. Navigate to a page in edit mode
2. Edit the prompt if needed
3. Click "Regenerate" to generate a new image
4. Image is **automatically downloaded** from MuleRouter and saved to Vercel Blob
5. The version appears in the "Page Image Versions" gallery
6. Click "Use as Current Image" to set it as the active page image
7. Click any version thumbnail to switch between versions

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `←` / `→` | Navigate pages (disabled when editing text) |
| `Esc` | Return to book list |

### Data Storage

| Data | Storage |
|------|---------|
| Book JSON (prompts, versions) | Supabase |
| Generated images | Vercel Blob |
| Static book files (fallback) | `/public/books/` |
