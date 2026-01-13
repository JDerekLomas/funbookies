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
│   │    9-Panel Reference Sheet      │  ← TEXT-TO-IMAGE                     │
│   │    (1 image, 9 panels)          │    (nano-banana / gpt-image-1)       │
│   │                                 │                                       │
│   │  ┌───┬───┬───┐                  │    Prompt:                           │
│   │  │ 1 │ 2 │ 3 │  Characters      │    - Style description               │
│   │  ├───┼───┼───┤                  │    - 9 scene vignettes               │
│   │  │ 4 │ 5 │ 6 │  Objects/Props   │    - "No title text"                 │
│   │  ├───┼───┼───┤                  │                                       │
│   │  │ 7 │ 8 │ 9 │  Settings        │    Output: Single 1024x1024 image    │
│   │  └───┴───┴───┘                  │    containing all 9 panels           │
│   │                                 │                                       │
│   │  Captures: palette, character   │                                       │
│   │  design, mood, art style        │                                       │
│   └────────────────┬────────────────┘                                       │
│                    │                                                        │
│                    │  Reference image provides style consistency            │
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
│         │                     │                                             │
│         │  Inputs:            │  Inputs:                                    │
│         │  - Reference sheet  │  - Reference sheet                          │
│         │  - Cover scene      │  - Page scene                               │
│         │  - "NO TEXT"        │  - "NO TEXT"                                │
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
Book JSON
    │
    ├──► Scene Descriptions ──► Style Selection ──► Reference Sheet (T2I)
    │                                                      │
    │                                                      ▼
    │                                              ┌───────────────┐
    │                                              │   Reference   │
    │                                              │    Image      │
    │                                              └───────┬───────┘
    │                                                      │
    ├──► Cover Scene ─────────────────────────────────────►├──► Cover (I2I)
    │                                                      │
    └──► Page Scenes ─────────────────────────────────────►└──► Pages (I2I)
```

## Key Principles

### 1. Separation of Content and Presentation
- **Content** (text, titles) lives in JSON
- **Images** are pure illustrations
- **UI** composes them together at runtime

### 2. Style Consistency via Reference
- One reference sheet per book
- All images for that book use the same reference
- Ensures character, palette, and mood consistency

### 3. No Baked Text
- Images contain NO text, titles, or words
- Text is overlaid by the reader UI
- Allows typography consistency and easy updates

### 4. Level-Appropriate Styles
- Band A: Simple shapes for pre-readers
- Band B: Playful for emerging readers
- Band C: Rich for developing readers
- Band D: Sophisticated for fluent readers

## File Structure

```
public/
├── books/
│   ├── {slug}.json              # Book content
│   ├── references/
│   │   └── {slug}_reference.png # Style reference (9-panel)
│   └── images/
│       └── {slug}_page{NN}.png  # Page illustrations
│
└── images/
    └── covers/
        └── {slug}.png           # Cover illustrations
```

## Models Used

| Step | Model | Type | Why |
|------|-------|------|-----|
| Reference Sheets | `nano-banana-pro` or `gpt-image-1` | Text-to-Image | Highest quality for style guide |
| Covers | `wan2.6-image` | Image-to-Image | Uses reference as style input |
| Pages | `wan2.6-image` | Image-to-Image | Uses reference as style input |

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
# Step 1: Generate reference sheets (Text-to-Image)
uv run python scripts/generate_references.py

# Step 2: Generate covers from references (Image-to-Image)
uv run python scripts/generate_covers.py

# Step 3: (Future) Generate page images (Image-to-Image)
uv run python scripts/generate_pages.py
```

## Prompt Writing Best Practices

### Avoid Negation - Describe What IS There

Text-to-image models attend to concepts even when negated. Saying "no rain" activates "rain" in the model's attention and often produces rain.

**Bad (mentions unwanted concept):**
- "Nature is alive even without rain"
- "No rain falling"
- "Sky with no clouds"

**Good (describes desired state):**
- "Dry dirt trail under overcast gray sky"
- "Parched garden bed, dusty soil"
- "Clear blue sky"

### Use Negative Prompts for Exclusions

If the model supports a `negative_prompt` field, put unwanted elements there instead of in the main prompt:

```python
body = {
    "prompt": "Girl standing in garden, gray overcast sky",
    "negative_prompt": "rain, water drops, wet, puddles"
}
```

### Weather Description Examples

| Story Context | Bad Prompt | Good Prompt |
|--------------|------------|-------------|
| Waiting for rain | "No rain yet" | "Dry overcast day, gray clouds" |
| Drought | "Garden without water" | "Parched soil, wilted plants" |
| Before storm | "Calm before rain" | "Still air, dark clouds gathering" |

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

## Current Status

| Component | Status |
|-----------|--------|
| Book JSONs | 48 books with scene descriptions |
| Reference Images | 47 generated |
| Cover Images | 48 generated |
| Page Images | 2 books fully generated |
