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
│   │                                 │                                       │
│   │  ┌───┬───┬───┐                  │    Prompt:                           │
│   │  │ 1 │ 2 │ 3 │  Characters      │    - Style description               │
│   │  ├───┼───┼───┤                  │    - 9 scene vignettes               │
│   │  │ 4 │ 5 │ 6 │  Objects/Props   │    - "No title text"                 │
│   │  ├───┼───┼───┤                  │                                       │
│   │  │ 7 │ 8 │ 9 │  Settings        │                                       │
│   │  └───┴───┴───┘                  │                                       │
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

## Generation Commands

```bash
# Step 1: Generate reference sheets
uv run python scripts/generate_references.py

# Step 2: Generate covers from references
uv run python scripts/generate_covers.py

# Step 3: (Future) Generate page images
uv run python scripts/generate_pages.py
```

## Current Status

| Component | Status |
|-----------|--------|
| Book JSONs | 43 books with scene descriptions |
| Reference Images | 35 generated |
| Cover Images | 43 generated (need regeneration for no-text) |
| Page Images | Not yet generated (shows placeholder) |
