# LilBookies Project Index

Quick reference for navigating the codebase.

---

## Books (65 total)

### Level System

| Band | Levels | Focus | Count |
|------|--------|-------|-------|
| **A** | A0-A4 | Emergent (print concepts, letter recognition, CV/VC) | 7 |
| **B** | B1-B9 | Early Decoding (CVC → blends → digraphs → vowel teams) | 38 |
| **C** | C1-C8 | Transitional (silent letters, soft c/g, syllables, affixes) | 10 |
| **D** | D1-D6 | Fluent (chapter-style, advanced vocabulary) | 6 |

### Phonics Progression (B-Band)

| Level | Skill | Example Book |
|-------|-------|--------------|
| B1 | CVC short a, i | Sam and the Cat |
| B2 | CVC all 5 short vowels | Pup in the Mud |
| B3 | Final blends, FLOSS rule | Jump at Camp |
| B4 | Initial blends | Frog and Crab |
| B5 | Consonant digraphs (sh, ch, th) | The Ship in the Shell |
| B6 | Silent E / Magic E | Kate and the Lake |
| B7 | R-controlled vowels | A Star at the Farm |
| B8 | Vowel teams (ai, ay, ea, ee, oa) | The Rain and the Snow |
| B9 | Diphthongs (ow, ou, oi, oy) | The Owl and the Boy |

### Phonics Progression (C-Band)

| Level | Skill | Example Book |
|-------|-------|--------------|
| C1 | Silent letters (kn, wr, gn) | The Knight's Quest |
| C2 | Soft C and G | The Magic City |
| C3 | Two-syllable closed (VC/CV) | Kitten's Hidden Basket |
| C4 | Two-syllable open + consonant-le | The Robot and the Pilot |
| C5 | Contractions + compounds | The Treehouse Mystery |
| C6 | Inflectional endings (-ed, -ing) | The Biggest Race |
| C7 | Derivational suffixes (-ful, -less) | The Hopeless Garden |
| C8 | Prefixes (un-, re-, im-) | The Impossible Invention |

### Book Files

| Path | Content |
|------|---------|
| `public/books/manifest.json` | Full book list with metadata |
| `public/books/index.json` | Slug → title/level lookup |
| `public/books/{slug}.json` | Individual book data |

---

## API Endpoints

### `/api/list-books` (Primary)
Returns all books from Supabase, sorted by most recent:
```json
{
  "slug": "zip-the-little-snail",
  "jsonFile": "zip-the-little-snail.json",
  "title": "Zip the Little Snail",
  "level": "B5",
  "band": "B",
  "skill": "CVC words with short i...",
  "coverImg": "/images/covers/zip-the-little-snail.png",
  "created": "2026-01-17",
  "updated_at": "2026-01-21T23:52:15.804Z"
}
```

### `/api/get-book?slug=X`
Fetch single book (Supabase first, static fallback).

### `/api/save-book`
Save book to Supabase (POST with `{ slug, fullBook }`).

---

## Core URLs

| URL | Purpose |
|-----|---------|
| `funbookies.com` | Production site |
| `/reader.html?book={slug}` | Read a book |
| `/reader.html?book={slug}&mode=edit` | Edit mode (regenerate images, feedback) |
| `/wizard/?slug={slug}` | Book creation wizard |
| `/activities/` | Phonics activities hub |
| `/quality.html` | Book quality ratings dashboard |

---

## Data Storage

### Supabase (Source of Truth)

| Table | Purpose |
|-------|---------|
| `books` | All book data (70 books as of 2026-01-21) |
| `book_ratings` | Quality ratings |

**`books` table schema:**
| Column | Type | Purpose |
|--------|------|---------|
| `slug` | TEXT (PK) | Book identifier |
| `data` | JSONB | Full book JSON |
| `updated_at` | TIMESTAMP | Last modified |

Special slugs (filtered from list-books):
- `_quality-ratings` - Aggregated star ratings
- `_book-evaluations` - LLM quality scores

### Local Files (Backup/Dev)
| Path | Content |
|------|---------|
| `public/books/*.json` | Static backup (not authoritative) |
| `public/books/references/` | 9-panel style sheets |
| `public/books/images/` | Generated page images |
| `public/images/covers/` | Cover images |
| `public/books/manifest.json` | Fallback book list |

### Data Flow
```
Wizard creates book → Supabase
Reader loads book → Supabase first, static fallback
List books → Supabase (sorted by updated_at desc)
```

---

## Wizard Phases

6-phase book creation workflow (`/wizard/`):

1. **Concept** - Level, topic, setting
2. **Outline** - Story structure
3. **Story** - Full text with scenes
4. **Reference** - 9-panel style sheet (single or multi-ref)
5. **Pages** - Generate page images
6. **Review** - Final quality check

State persists to Supabase for cross-device sync.

---

## API Endpoints (`/api/`)

### Books
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `get-book` | GET | Fetch book by slug |
| `save-book` | POST | Save to Supabase |
| `list-books` | GET | All books (Supabase or fallback) |
| `validate-book` | POST | Check book structure |

### Generation
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `generate-story` | POST | LLM story generation |
| `generate-scenes` | POST | Scene descriptions from story |
| `generate-image` | POST | Single image generation |
| `generate-ref-i2i` | POST | Image-to-image with reference |
| `generate-refs-cascade` | POST | Multi-ref sheet generation |
| `generate-ref-prompt` | POST | LLM prompt for reference sheet |

### Quality
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `evaluate-book` | POST | LLM quality scoring |
| `get-evaluations` | GET | Cached evaluation results |
| `book-ratings` | GET/POST | Star ratings |
| `feedback` | POST | Per-page feedback |

### Utilities
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `upload-image` | POST | Image upload |
| `save-reference` | POST | Save reference sheet |
| `log-image-gen` | POST | Audit trail |
| `refine-concept` | POST | Improve story concept |

---

## Python Scripts (`/scripts/`)

### Book Creation
| Script | Purpose |
|--------|---------|
| `generate_story.py` | Story from concept |
| `generate_scene_descriptions.py` | Scenes from story |
| `validate_book_for_images.py` | Pre-flight check |
| `generate_references.py` | Multi-ref cascade |
| `generate_page_images.py` | Page illustrations |
| `generate_covers.py` | Cover images |
| `generate_thumbnails.py` | Thumbnail versions |

### Audio Generation
| Script | Purpose |
|--------|---------|
| `generate_phoneme_sounds.py` | Phoneme audio (ElevenLabs IPA) |
| `generate_all_letter_sounds.py` | Letter sounds a-z |
| `generate_instruction_audio.py` | Activity instructions |
| `generate_coaching_audio.py` | Encouragement phrases |
| `generate_word_audio.py` | Word pronunciations |
| `generate_sight_word_audio.py` | Sight word audio |

### Quality & Validation
| Script | Purpose |
|--------|---------|
| `story_validator.py` | Story quality checks |
| `quality_evaluator.py` | Multi-factor scoring |
| `audit_books.py` | Content audit |

### Experiments
| Script | Purpose |
|--------|---------|
| `batch_experiment.py` | Batch generation tests |
| `multi_ref_experiment.py` | Multi-reference tests |
| `prompt_enhancer.py` | Prompt improvement |

### Utilities
| Script | Purpose |
|--------|---------|
| `xml_to_book_json.py` | XML → JSON conversion |
| `generate_book_xml.py` | JSON → XML conversion |
| `image_utils.py` | Image helpers |
| `fal_client.py` | FAL API client |

---

## Activities (`/public/activities/`)

Phonics practice games:

| Activity | Skill |
|----------|-------|
| `letter-drill` | Letter recognition speed |
| `say-the-sound` | Letter-sound correspondence |
| `blend-it` | Blending sounds |
| `chop-it-up` | Segmenting words |
| `word-builder` | Spelling with tiles |
| `sound-boxes` | Elkonin boxes |
| `word-chains` | Minimal pairs |
| `word-families` | Rhyme patterns |
| `rhyme-match` | Rhyme identification |
| `sight-words` | High-frequency words |
| `voice-blend` | Voice-controlled blending |
| `read-aloud` | Oral reading |
| `sentence-scramble` | Sentence construction |
| `monster-munch` | Gamified phonics |
| `phonics-assessment` | Skill evaluation |

---

## Audio Files

| Path | Content |
|------|---------|
| `/activities/letter-sounds/openai-us/sounds/` | Letter sounds (a.mp3-z.mp3) |
| `/activities/letter-sounds/openai-us/names/` | Letter names (A.mp3-Z.mp3) |
| `/audio/phonemes/` | Blends, digraphs (64 files) |
| `/audio/instructions/` | Activity instructions |
| `/audio/coaching/` | Encouragement phrases |

---

## Environment Variables

| Variable | Service | Purpose |
|----------|---------|---------|
| `OPENAI_API_KEY` | OpenAI | TTS, GPT-4 |
| `ELEVENLABS_API_KEY` | ElevenLabs | IPA phoneme TTS |
| `MULEROUTER_API_KEY` | MuleRouter | Image generation |
| `SUPABASE_URL` | Supabase | Database URL |
| `SUPABASE_SERVICE_KEY` | Supabase | Admin access |
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase | Frontend URL |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase | Public key |

---

## Key Documentation

| Doc | When to read |
|-----|--------------|
| `CLAUDE.md` | First - project instructions |
| `PROMPTING_CHEATSHEET.md` | Writing image prompts |
| `BOOK_CREATION_PROCESS.md` | Making a new book |
| `STORY_CONTENT_GUIDE.md` | Writing story text |
| `IMAGE_GENERATION_WORKFLOW.md` | Understanding image pipeline |
| `DEVLOG.md` | Recent changes |
