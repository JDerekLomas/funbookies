# Funbookies Riso Picture Book Project

## Project Goal
Create decodable children's picture books (ages 5-7) designed for **Risograph printing**. Books should look like indie picture books, not educational materials. The phonics scaffolding should be invisible - kids grab these because they look fun.

## Print Partner
**Riso Pop** - Amsterdam risograph studio (https://www.risopop.com/)
- Get their specific specs before final output
- Typical: 2-3 spot colors, A5 or custom zine size, saddle-stitch binding

---

# WORKFLOW: Human + AI Collaboration

This workflow has **4 phases with approval gates**. Do NOT proceed to the next phase without explicit human approval. Each gate requires a clear "approved" or revision notes.

---

## Phase 1: Story Concept

### Human Decides:
- [ ] **Topic/theme** (volcano, castle, elements, etc.)
- [ ] **Phonics level** (Yellow, Orange, Red, Purple)
- [ ] **Character concept** (species, name, personality trait)
- [ ] **Emotional arc** (what feeling journey?)
- [ ] **Catchphrase** (what will kids repeat?)

### AI Delivers:
- Draft story text (all pages)
- Word list verification (80% rule check)
- Story structure breakdown (beats per page)

### Deliverable Format:
```
PHASE 1 DELIVERABLE: [Book Title]
─────────────────────────────────
Level: [Orange]
Theme: [description]
Character: [Name] - [species], [personality]
Catchphrase: "[phrase]"
Emotional Arc: [start] → [middle] → [end]

STORY TEXT:
Page 3: [text]
Page 4: [text]
...

WORD CHECK:
- Decodable: X words
- Sight words: X words
- Topic vocab: X words
- Compliance: XX%
```

### ✅ GATE 1: Story Text Approved
**Do not generate ANY images until story text is approved.**

Human reviews and either:
- Approves → proceed to Phase 2
- Requests revisions → AI revises, re-submit

---

## Phase 2: Art Direction

### Human Decides:
- [ ] **Riso ink palette** (pick 2-3 specific inks from Riso Pop catalog)
- [ ] **Color assignments** (which ink for character, background, accents)
- [ ] **Character design direction** (round/angular, cute/cool, etc.)

### AI Delivers:
- 4-6 character reference options (designed for chosen ink palette)
- Color assignment guide showing what gets each ink
- Style notes for consistency

### Deliverable Format:
```
PHASE 2 DELIVERABLE: [Book Title] Art Direction
───────────────────────────────────────────────
RISO PALETTE:
- Black: outlines, text, details
- [Ink A name]: [what it's used for]
- [Ink B name]: [what it's used for]

CHARACTER DESIGN OPTIONS:
[Generate 4-6 reference images]
- Option A: [description]
- Option B: [description]
...

Recommendation: Option [X] because [reason]
```

### ✅ GATE 2: Character Design Locked
**Do not generate page images until character design is locked.**

Human reviews and either:
- Selects one option → that design is LOCKED for all pages
- Requests new options → AI generates more refs
- Requests modifications → AI adjusts and re-generates

---

## Phase 3: Page Illustrations

### Human Decides:
- [ ] **Approve/reject each spread** (pages reviewed in pairs)
- [ ] **Revision notes** for rejected pages

### AI Delivers:
- Page images in batches of 4-6 (2-3 spreads)
- Consistent with locked character design
- Designed for Riso color separation

### Process:
```
BATCH 1: Cover + Pages 3-6
[Generate images]
→ Human reviews
→ Approved pages move forward
→ Rejected pages get revision notes
→ AI regenerates rejected pages
→ Repeat until batch approved

BATCH 2: Pages 7-12
[Same process]

BATCH 3: Pages 13-18
[Same process]

BATCH 4: Pages 19-24 + End
[Same process]
```

### ✅ GATE 3: All Pages Approved
**Do not proceed to Riso prep until all pages are approved.**

---

## Phase 4: Riso Separation & Print Prep

### Human Decides:
- [ ] **Final proof approval** (full book review)
- [ ] **Print specs confirmation** (page size, bleed, binding)
- [ ] **Quantity and paper stock** (coordinate with Riso Pop)

### AI Delivers:
- Color-separated grayscale layers (one PDF per ink)
- Registration marks added
- Proper bleed (3mm)
- 85% opacity on solid areas
- 300 DPI minimum

### Deliverable Format:
```
PHASE 4 DELIVERABLE: Print-Ready Files
──────────────────────────────────────
Files:
- [book]_black.pdf (all outlines, text)
- [book]_[ink_a].pdf (grayscale for ink A)
- [book]_[ink_b].pdf (grayscale for ink B)

Specs:
- Size: [A5 / custom]
- Bleed: 3mm
- Resolution: 300 DPI
- Pages: [X]
```

### ✅ GATE 4: Send to Printer
Human sends files to Riso Pop with specs.

---

## Workflow Summary

```
┌─────────────────────────────────────────────────────────────┐
│  PHASE 1: STORY         Human: topic, level, character     │
│                         AI: draft story text               │
│                         ✅ GATE: Story approved            │
├─────────────────────────────────────────────────────────────┤
│  PHASE 2: ART DIRECTION Human: ink palette, design pick    │
│                         AI: character reference options    │
│                         ✅ GATE: Character locked          │
├─────────────────────────────────────────────────────────────┤
│  PHASE 3: PAGES         Human: approve each spread         │
│                         AI: page images in batches         │
│                         ✅ GATE: All pages approved        │
├─────────────────────────────────────────────────────────────┤
│  PHASE 4: PRINT PREP    Human: final proof, specs          │
│                         AI: separated layers, PDFs         │
│                         ✅ GATE: Send to printer           │
└─────────────────────────────────────────────────────────────┘
```

---

## Book Status Tracker

Use this to track each book's progress:

```
| Book Title | Phase 1 | Phase 2 | Phase 3 | Phase 4 | Status |
|------------|---------|---------|---------|---------|--------|
| [Name]     | ✅/🔄/⏳ | ✅/🔄/⏳ | ✅/🔄/⏳ | ✅/🔄/⏳ | [note] |

✅ = Approved   🔄 = In revision   ⏳ = Not started
```

---

# REFERENCE: Phonics Framework

### Phonics Levels (Science of Reading aligned)

| Level | Name | Patterns | Max Words/Page | Target Age |
|-------|------|----------|----------------|------------|
| Yellow | CVC Only | cat, dog, run | 5 | 5-6 |
| Orange | CVC + Digraphs | sh, ch, th, ck | 7 | 6-7 |
| Red | + Blends | bl, cr, st, sp | 8 | 6-7 |
| Purple | + Magic E | make, like, home | 10 | 7-8 |

### Word Types
- **Decodable**: Words kids can sound out using known patterns
- **Sight words (Flash)**: Common words to memorize (the, to, a, is, it, we, go, said)
- **Heart words**: Irregular spellings to learn "by heart" (said, was, they)
- **Topic vocabulary**: 3-5 special words introduced for the story topic

### The 80% Rule
At least 80% of words on each page must be decodable or sight words appropriate for that level. This is non-negotiable.

### Word Banks
See `src/word_banks.json` for approved word lists by phonics level.

---

# REFERENCE: Story Craft for Early Readers

### Study These Masters

**Mo Willems (Elephant & Piggie, Pigeon)**
- Two characters with OPPOSING personalities create instant drama
- Expressions do 90% of the emotional work
- Simple sentences, huge feelings
- The "straight man / wild card" dynamic
- Catchphrases that kids want to repeat

**Pete the Cat (James Dean & Kimberly Dean)**
- Resilience messaging: "Did Pete cry? Goodness, no!"
- Repetition with variation builds reading confidence
- Predictable structure lets kids "read ahead"
- Cool, unflappable protagonist
- Musical/rhythmic language

**Jon Klassen (I Want My Hat Back, This Is Not My Hat)**
- Deadpan humor through minimal text
- What's NOT said creates tension
- Minimal backgrounds focus attention
- Dark humor that respects kids' intelligence
- Perfect page turn reveals

**Julia Donaldson (Gruffalo, Room on the Broom)**
- Rhyme and rhythm (though harder for decodable books)
- Cumulative structure (A meets B, then A+B meet C...)
- Satisfying reversals
- Memorable character descriptions

### Story Structure Principles

**Character Design:**
- TWO characters with contrasting traits work best
- Each needs a DISTINGUISHING FEATURE (visual shorthand)
- Each needs a CATCHPHRASE or verbal tic
- Contrast creates comedy: bold/cautious, loud/quiet, fast/slow

**Emotional Arc (16-24 pages):**
```
Opening:     Setup - introduce characters, establish normal
Early:       Want - character desires something
Middle:      Action - character pursues goal
Turn:        Obstacle - something changes (PAGE TURN SURPRISE!)
Rising:      Tension - stakes increase
Climax:      Peak moment - biggest emotion
Resolution:  Safe landing - satisfied, proud, changed
```

**Page Turn Power:**
- Right-hand pages are REVEALS
- Build anticipation on left: "But then..."
- Deliver surprise on right: "A DRAGON!"
- Kids physically participate by turning

**Writing Techniques:**
- Repetition with variation: "Run! Run! Run!" → "Run, [Name], run!"
- Sound effects as sentences: "CRASH! BANG! BOOM!"
- Catchphrase callbacks at key moments
- Parallel structure: "X hid in the cup. Y hid in the hat."
- Questions to the reader: "Did [Name] stop? No!"
- One idea per page maximum

**What Makes Kids Re-read:**
- Predictability (they know what's coming = mastery feeling)
- Participation (catchphrases to shout, sounds to make)
- Humor (mild peril, silly situations, deadpan reactions)
- Agency (characters who DO things, make choices)
- Satisfaction (problems solved, goals achieved)

---

# REFERENCE: Riso Art Direction

### Design Philosophy
**"Expressive Minimal"** - Mo Willems expressiveness meets Riso aesthetics.
Simple shapes, bold expression, limited spot colors.

### Riso Color Strategy

**2-3 ink approach per book:**
```
Layer 1: BLACK - All outlines, text, details
Layer 2: SPOT COLOR A - Main character, warm elements
Layer 3: SPOT COLOR B - Secondary elements, cool accents
```

**Popular Riso ink combinations:**
- Black + Fluorescent Orange + Yellow (warm, energetic)
- Black + Fluorescent Pink + Blue (playful, contrast)
- Black + Green + Risofederal Blue (nature, calm)
- Black + Red + Gold (bold, classic)

**Riso Pop Ink Catalog** (confirm availability):
- Fluorescent Orange, Fluorescent Pink, Yellow, Red, Blue, Green
- Risofederal Blue, Gold, Purple, Teal, Brown
- Check current stock: https://www.risopop.com/

### Image Style for Riso

**DO:**
- Flat color fills (no gradients)
- Bold black outlines (separate layer)
- Simple geometric shapes
- High contrast
- Large areas of single color
- Exaggerated expressions (eyes do the work)
- Minimal backgrounds (saves ink, focuses attention)
- Silhouettes that read instantly

**DON'T:**
- Gradients or soft shading
- Complex textures
- Detailed backgrounds
- Small intricate details (Riso can't resolve)
- More than 3 colors per spread
- Thin lines (may not print)

### Character Design for Riso

Each character needs:
1. **Silhouette recognition** - identifiable as solid shape
2. **One distinguishing feature** in contrasting color
3. **Simple body** - oval/circle shapes, tube limbs
4. **Expressive face** - eyes carry emotion

---

# REFERENCE: File Structure

```
minibooks/
├── src/
│   ├── templates/           # Level-specific constraints
│   ├── word_banks.json      # Approved words by phonics level
│   └── book_maker.py        # Story generation with constraints
├── web/books/
│   ├── [book_name]/
│   │   ├── story.json       # Story data (Phase 1 output)
│   │   ├── art_direction.md # Color/character specs (Phase 2)
│   │   ├── refs/            # Character reference images
│   │   ├── pages/           # Page illustrations (Phase 3)
│   │   └── print/           # Riso-separated files (Phase 4)
│   │       ├── black/
│   │       ├── color_a/
│   │       └── color_b/
│   └── preview.html         # Review interface
├── reference_images/        # Inspiration, style refs
└── docs/
```

---

# REFERENCE: Riso Separation Specs

**Output specs for Riso Pop:**
- 300 DPI minimum
- Grayscale PDFs per color
- Include registration marks
- Reduce solid areas to 85% opacity
- Add 3mm bleed if full-bleed pages

---

# REFERENCE: Validation Checklist

### Story Text
- [ ] Max words per page within level limit
- [ ] 80%+ words are decodable or sight words
- [ ] Catchphrases used at key moments
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

# Resources

### Phonics & Reading Science
- Dolch sight word lists
- Fry's first 100 words
- Science of Reading research
- Orton-Gillingham methodology

### Story Craft (Study These)
- **Mo Willems**: Elephant & Piggie series, Don't Let the Pigeon Drive the Bus
- **Pete the Cat**: I Love My White Shoes, Pete the Cat and His Four Groovy Buttons
- **Jon Klassen**: I Want My Hat Back, This Is Not My Hat, Triangle/Square/Circle
- **Mac Barnett & Jon Klassen**: Sam and Dave Dig a Hole, Extra Yarn
- **Julia Donaldson**: The Gruffalo, Room on the Broom (for structure)

### Riso Resources
- Riso Pop Amsterdam: https://www.risopop.com/
- RISOTTO print setup guide: https://risottostudio.com/pages/basic-print-setup
- Color library tester: https://colorlibrary.ch/
- Stencil zine aesthetics for inspiration

### Image Generation
- MuleRouter API for text-to-image (Wan2.6-T2I)
- Use seed values for style consistency
- Generate character refs before page images
