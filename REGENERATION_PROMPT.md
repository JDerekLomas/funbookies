# FunBookies Platform — Regeneration Prompt

Use this document to rebuild the FunBookies platform from scratch. It captures everything worth keeping from the original and defines a clean architecture.

---

## What This Platform Does

FunBookies is a web platform that uses AI to generate illustrated decodable phonics books for beginning readers (ages 5-7). It serves three user types:

1. **Authors** — create books using an AI-assisted wizard
2. **Parents/Teachers** — browse and assign books to children
3. **Children** — read leveled books with optional audio support

The core loop: Author enters a concept and reading level → AI generates a phonics-constrained story → AI generates consistent illustrations → Book is published and readable.

---

## Domain Model

### Reading Levels

Four bands, each with numbered sub-levels:

| Band | Levels | Focus | Text Density |
|------|--------|-------|--------------|
| A | A0-A3 | CVC words, basic phonics | 1-4 words per page |
| B | B0-B3 | Digraphs, blends, silent-e | 1-3 sentences per page |
| C | C0-C3 | Morphology, word study | 2-5 sentences per page |
| D | D0-D6 | Fluency, dialogue, complex sentences | 4-8 lines per page |

Each level has a specification defining:
- Allowed phonics patterns (CVC, CCVC, digraphs, vowel teams, etc.)
- Maximum words per sentence
- Target page count (8-16 pages)
- Decodability target (85-95%)
- Sight words permitted at that level
- Fluency targets (words per minute)

Store these specs in a single `level-specs.json` file.

### Book Structure

A book contains:

```
book/
  metadata: { title, slug, level, band, author, created, status }
  storyBible: { premise, setting, characters[], theme, emotionalArc }
  characters[]: { name, role, physicalDescription, visualPrompt }
  pages[]: { pageNumber, text, lines[], emotion, sceneDescription, imagePrompt, imageUrl }
  frontMatter: { cover, copyright, parentGuide }
  backMatter: { endPage, wordSearch, comprehension[] }
  wordLists: { targetWords[], sightWords[], decodableWords[] }
  references: { styleGuide, characterSheet }
```

### Story Quality Principles

These are non-negotiable for generated stories:
- **"Write it, don't describe it."** — Inhabit the narrative with specific names, actions, onomatopoeia, sensory details. Not templates.
- **Natural dialogue** — Characters speak authentically. No forced phonics sentences.
- **Clear setup by page 2** — State the problem plainly, then show it.
- **Logical causation** — Each action follows naturally from the previous.
- **Meaningful repetition** — Repeated words carry emotional weight, not random decodability.
- **Emotional arc** — Every page has a nameable emotion forming a coherent progression.
- **Resolution mirrors setup** — The ending directly solves the opening problem.
- **Simple over clever** — Clarity beats impressive phonics complexity.
- **Heart words** — 2-3 motivating words above level as strategic sight words to smooth phrasing.

### Image Generation Principles

- **Separate content from presentation** — Text overlays are rendered by the UI, never baked into images.
- **Describe what to show, not what to avoid** — "clear blue sky" not "no clouds." Negations activate the concept.
- **Physical descriptions over emotional** — Convert emotions to observable states (fear → "eyes wide, mouth agape, body leaning back").
- **WHO/WHERE/WHAT/STATE structure** for scene prompts.
- **3-reference cascade for consistency:**
  1. Style guide (text-to-image) — establishes visual vocabulary
  2. Opening scenes reference (image-to-image) — early story visuals
  3. Closing scenes reference (image-to-image) — late story visuals
- **Track physical state across pages** — clothing, wetness, props, location, time of day.
- **Single scene per image** — no split panels or sequences.

---

## Architecture

### Tech Stack

- **Frontend:** Static HTML/CSS/JS hosted on Vercel
- **API:** Vercel serverless functions (Node.js)
- **Database:** Supabase (Postgres + storage)
- **AI Story Generation:** Claude API (Anthropic)
- **AI Image Generation:** fal.ai (with reference image support)
- **Audio:** OpenAI TTS or ElevenLabs for read-aloud
- **Local Storage:** IndexedDB for offline reading progress

### Directory Structure

```
funbookies/
├── public/
│   ├── index.html              # Landing / book browser
│   ├── reader.html             # Book reader
│   ├── wizard.html             # Author book creation wizard
│   ├── dashboard.html          # Parent/teacher dashboard
│   ├── activities/             # Phonics practice activities
│   ├── css/
│   │   └── styles.css          # Single stylesheet
│   └── js/
│       ├── app.js              # Shared utilities, router, auth
│       ├── reader.js           # Book reading logic
│       ├── wizard.js           # Book creation wizard
│       ├── dashboard.js        # Progress tracking
│       ├── db.js               # IndexedDB wrapper
│       └── audio.js            # TTS and audio playback
├── api/
│   ├── _lib/
│   │   ├── claude.js           # Claude API client
│   │   ├── fal.js              # fal.ai image client
│   │   ├── supabase.js         # Supabase client
│   │   └── levels.js           # Level spec loader
│   ├── generate-story.js       # Story generation endpoint
│   ├── generate-images.js      # Image generation endpoint
│   ├── evaluate-book.js        # Book quality evaluation
│   ├── books.js                # CRUD for books
│   └── progress.js             # Reading progress tracking
├── data/
│   └── level-specs.json        # Phonics level definitions
├── vercel.json
├── package.json
└── README.md
```

**That's it.** No sprawling docs folder. No duplicate markdown guides. No scripts directory. No logs directory. The platform is small and readable.

### API Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/generate-story` | Generate story text from concept + level |
| POST | `/api/generate-images` | Generate illustrations for a book |
| POST | `/api/evaluate-book` | Score a book on story, phonics, and technical quality |
| GET/POST | `/api/books` | List books / save a book |
| GET | `/api/books?slug=x` | Get a single book |
| POST | `/api/progress` | Save reading progress |
| GET | `/api/progress?student=x` | Get student progress |

### Data Flow

```
Author enters concept + level
        ↓
POST /api/generate-story
  → Load level-specs.json for constraints
  → Send concept + constraints to Claude
  → Return book JSON (story, scenes, word lists)
        ↓
Author reviews story, edits if needed
        ↓
POST /api/generate-images
  → Generate style reference (text-to-image)
  → Generate page images (image-to-image with reference)
  → Upload to Supabase storage
  → Update book JSON with image URLs
        ↓
POST /api/evaluate-book
  → Score story quality (Claude, harsh critic)
  → Score phonics accuracy (programmatic)
  → Score technical completeness (programmatic)
  → Return weighted score + verdict
        ↓
Author publishes or iterates
        ↓
Book appears in reader
```

---

## Book Creation Wizard

The wizard is the core authoring experience. Five steps, linear progression, each requiring approval before advancing:

### Step 1: Concept
- Input: title idea, reading level, optional setting/theme
- Action: Calls `/api/generate-story` with `phase=concept`
- Output: Refined concept with character suggestions, premise, emotional arc
- Author approves or modifies

### Step 2: Story
- Input: Approved concept
- Action: Calls `/api/generate-story` with `phase=story`
- Output: Full book JSON with pages, text, word lists, scene descriptions
- Author reviews each page, can edit text directly
- System shows decodability score and flagged words in real-time

### Step 3: Scenes
- Input: Approved story
- Action: Auto-generates scene descriptions from story bible + page text
- Output: Detailed visual prompts for each page following WHO/WHERE/WHAT/STATE
- Author reviews and adjusts scene descriptions

### Step 4: Images
- Input: Approved scenes
- Action: Calls `/api/generate-images`
  - First: generate style reference sheet
  - Then: generate each page image with reference
- Output: Illustrated book
- Author can regenerate individual pages

### Step 5: Review & Publish
- Action: Calls `/api/evaluate-book`
- Shows scores for story, phonics, technical quality
- Author can go back to any step to iterate
- Publish makes book available in the reader

---

## Book Reader

The reader is simple and focused:

- Full-screen page display with large illustration
- Text overlay below image (never in the image)
- Tap/swipe to advance pages
- Optional read-aloud audio (TTS)
- Word highlighting during audio playback
- Tap any word to hear it pronounced
- Progress saved to IndexedDB (works offline)
- Syncs to Supabase when online

---

## Story Generation Prompt

This is the core prompt sent to Claude for story generation. It must be part of the codebase, not a separate doc.

```
You are writing a decodable phonics book for children ages 5-7.

LEVEL: {level}
BAND: {band}
CONSTRAINTS:
- Phonics focus: {phonicsPatterns}
- Max words per sentence: {maxWordsPerSentence}
- Target pages: {pageCount}
- Decodability target: {decodabilityTarget}%
- Allowed sight words: {sightWords}
- Target words (must appear 4+ times): {targetWords}

CONCEPT: {concept}

RULES:
1. Write it, don't describe it. Use specific names, actions, sounds, sensory details.
2. Natural dialogue only. Characters speak like real people, not phonics exercises.
3. State the problem plainly by page 2.
4. Every action must follow logically from the previous one.
5. Repeated words must carry emotional weight tied to the story's conflict.
6. Every page needs a clear, nameable emotion forming a coherent arc.
7. The ending must directly mirror and resolve the opening problem.
8. Prefer simple, clear language over clever phonics tricks.
9. Include 2-3 "heart words" above level as sight words to smooth awkward phrasing.
10. Maximum 2-3 recurring characters with detailed physical descriptions.

OUTPUT: Return a complete book JSON matching this schema:
{bookSchema}
```

---

## Image Generation Prompt

The prompt template for page illustrations:

```
Scene: {sceneDescription}

Characters present:
{characterBlocks}

Composition: {shotType} shot
Setting: {settingDescription}
Lighting: {timeOfDay}
Physical states: {physicalStates}

Style: {styleDescription}
Medium: Children's book illustration, {bandStyle}

IMPORTANT: Do not include any text, words, letters, or numbers in the image.
```

Band styles:
- A: Simple watercolor, minimal backgrounds, bold outlines
- B: Warm gouache, moderate detail, clear expressions
- C: Rich digital illustration, detailed environments
- D: Sophisticated mixed media, complex compositions

---

## Evaluation System

Three scoring dimensions, weighted:

**Story Quality (50%)** — Claude evaluates: coherence, engagement, clarity, emotional arc, age-appropriateness, educational value. Prompt instructs harsh scoring — default to lower scores unless genuinely exceptional.

**Phonics Accuracy (25%)** — Programmatic: decodability percentage, target word frequency, average word length, CVC ratio, sight word compliance.

**Technical Completeness (25%)** — Programmatic: metadata present, characters defined, scene descriptions complete, word counts within range, page count correct.

Overall score maps to verdict:
- 8-10: Good — ready to publish
- 5-7: Needs improvement — iterate on flagged areas
- 1-4: Poor — major revision needed

---

## What NOT to Build

- No user authentication in v1. Use simple student picker (name entry).
- No payment system.
- No admin panel. Author tools are the wizard.
- No separate mobile app. Responsive web only.
- No complex state management library. Vanilla JS with IndexedDB.
- No build step. No webpack, no bundler. Plain files served by Vercel.
- No duplicate documentation. This file + inline code comments only.
- No scripts directory. Everything is either an API endpoint or client JS.

---

## Implementation Order

Build in this sequence. Each step should be fully working before moving on:

1. **Data layer** — `level-specs.json`, Supabase schema, `api/_lib/` clients
2. **Story generation** — `/api/generate-story` endpoint, test with curl
3. **Wizard steps 1-2** — Concept and story generation UI
4. **Book reader** — Display a book, page navigation, text overlay
5. **Image generation** — `/api/generate-images`, wizard steps 3-4
6. **Evaluation** — `/api/evaluate-book`, wizard step 5
7. **Book browser** — Landing page listing published books
8. **Progress tracking** — IndexedDB + Supabase sync
9. **Audio** — TTS integration, word highlighting
10. **Activities** — Phonics practice games (port best ones from original)
