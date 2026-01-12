# Content Production Guide

Single source of truth for creating and managing FunBookies content.

## Quick Reference

### Current Scripts (19 total)

| Script | Purpose | When to Use |
|--------|---------|-------------|
| **Core Libraries** |||
| `book_generator.py` | Book content generation engine | Called by other scripts |
| `image_generator.py` | Image generation utilities | Called by other scripts |
| `quality_evaluator.py` | Book quality assessment | Evaluate book quality |
| `story_bible_workflow.py` | Story bible generation | Plan new book series |
| **Book Creation** |||
| `create_book.py` | Create new book from scratch | New book |
| `generate_book_v2.py` | Generate book content | New book content |
| **Image Generation** |||
| `generate_references.py` | 9-panel style reference sheets | First step for new book |
| `generate_covers.py` | Cover images from references | After reference exists |
| `generate_page_images.py` | Page illustrations | After reference exists |
| `generate_thumbnails.py` | Thumbnail images | After covers exist |
| **Audio Generation** |||
| `generate_phoneme_sounds.py` | Phoneme audio (ElevenLabs IPA) | New phonemes |
| `generate_letter_sounds.py` | Letter sounds | New letters |
| `generate_all_letter_sounds.py` | All letter sounds batch | Full regeneration |
| `generate_instruction_audio.py` | Activity instructions (OpenAI) | New activities |
| `generate_coaching_audio.py` | Letter coaching audio | New coaching content |
| **Icons** |||
| `generate_word_icons.py` | Word icons for activities | New words |
| `generate_missing_word_icons.py` | Fill gaps in word icons | Audit & fill |
| `generate_activity_icons.py` | Activity menu icons | New activities |
| `generate_ui_icons.py` | UI element icons | New UI elements |

### Archived Scripts

Located in `scripts/_archive/`. These are deprecated or one-time-use scripts kept for reference.

---

## Directory Structure

```
public/
├── books/
│   ├── *.json                    # Book content (47 books)
│   ├── images/                   # Page illustrations
│   │   └── {slug}_page{NN}.png
│   ├── references/               # Style reference sheets
│   │   └── {slug}_reference.png
│   └── _archive/                 # Legacy book-specific folders
│
├── images/
│   ├── covers/                   # Cover images
│   │   └── {slug}.png
│   ├── icons/                    # Activity & UI icons
│   └── thumbnails/               # Book thumbnails
│
├── audio/
│   ├── phonemes/                 # Blend/digraph sounds
│   ├── instructions/             # Activity instruction audio
│   └── coaching/                 # Letter coaching audio
│
├── activities/
│   └── letter-sounds/
│       └── openai-us/            # Letter sounds (a-z)
│           ├── sounds/           # Letter sounds
│           └── names/            # Letter names
│
└── data/
    ├── phonics-words.json        # Word lists
    ├── sight-words.json          # Sight word lists
    └── level-specs.json          # Level specifications
```

---

## Workflows

### Creating a New Book

```bash
# 1. Create book JSON with content
uv run python scripts/create_book.py

# 2. Generate style reference (9-panel sheet)
uv run python scripts/generate_references.py --book {slug}

# 3. Generate cover from reference
uv run python scripts/generate_covers.py --book {slug}

# 4. Generate page images
uv run python scripts/generate_page_images.py --book {slug}

# 5. Generate thumbnail
uv run python scripts/generate_thumbnails.py --book {slug}
```

### Generating Audio

```bash
# Phoneme sounds (blends, digraphs, vowel teams)
uv run python scripts/generate_phoneme_sounds.py

# Activity instruction audio
uv run python scripts/generate_instruction_audio.py

# All letter sounds
uv run python scripts/generate_all_letter_sounds.py
```

### Generating Icons

```bash
# Word icons for activities
uv run python scripts/generate_word_icons.py

# Activity menu icons
uv run python scripts/generate_activity_icons.py
```

---

## API Services

| Service | API Key Env Var | Used For |
|---------|-----------------|----------|
| **OpenAI** | `OPENAI_API_KEY` | TTS (Nova voice), GPT-4 for content |
| **ElevenLabs** | `ELEVENLABS_API_KEY` | Phoneme TTS with IPA tags |
| **MuleRouter** | `MULEROUTER_API_KEY` | Image generation (wan2.6, nano-banana) |
| **Anthropic** | `ANTHROPIC_API_KEY` | Claude for story generation |

---

## Book Levels

| Band | Levels | Focus | Style |
|------|--------|-------|-------|
| **A** | A0-A4 | Pre-reading, sight words | Simple, pastel |
| **B** | B1-B9 | CVC words, blends, digraphs | Playful, vibrant |
| **C** | C1-C8 | Multisyllable, complex patterns | Rich, detailed |
| **D** | D1-D6+ | Connected text, fluency | Sophisticated |

---

## Image Generation Pipeline

```
Book JSON → Scene Descriptions → Reference Sheet (T2I: nano-banana-pro)
                                        ↓
                                 Cover (I2I: wan2.6)
                                 Pages (I2I: wan2.6)
```

**Key principle**: Images contain NO text. Text is overlaid by the reader UI.

See `IMAGE_GENERATION_WORKFLOW.md` for detailed pipeline documentation.

---

## Quality Checklist

Before publishing a book:

- [ ] Book JSON has all required fields
- [ ] Reference image captures character/style correctly
- [ ] Cover image is pure illustration (no baked text)
- [ ] All page images generated and consistent
- [ ] Word lists accurate for level
- [ ] Audio generated for any new phonemes/words

---

## Cleanup Notes

**Folders to manually delete when ready:**
- `public/images/icons/backup/` - Old icon versions (current icons finalized)
- `public/audio/phonemes/backup/` - Old phoneme sounds

**Versioned files in references:**
Some books have multiple reference versions (e.g., `_v2.png`, `_v3.png`).
Keep the latest; delete old versions when confirmed working.
