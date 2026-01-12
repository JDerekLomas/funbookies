# Review UI & Content Production - Status

## Completed

### Review Hub (`/review/`)
- **Hub**: `/review/index.html` - Central navigation to all review tools
- **Books**: `/review/books.html` - Page-by-page book review with feedback
- **Covers**: `/review/covers.html` - Cover image review
- **References**: `/review/references.html` - 9-panel reference sheets
- **Curriculum**: `/review/curriculum.html` - Scope & sequence, levels, phonics
- **Audio**: `/review/phoneme-sounds.html`, `/review/letter-sounds.html`
- **Icons**: `/review/word-icons.html`, `/review/activity-icons.html`

### Book Review Features
- 3-panel layout: sidebar | main view | info panel
- Page-by-page navigation with arrow keys
- Creation Notes (page -2) and Reference Sheet (page -1) as reviewable pages
- Vertical layout: image, text, scene prompt (all visible without scrolling)
- Per-page feedback with thumbs up/down and notes
- Generation metadata display (model, date, reference used)
- Export feedback per book

### Generation Metadata Tracking
Scripts now save metadata to book JSON:
- `generate_page_images.py` → `page.generation_metadata`
- `generate_references.py` → `book.reference_metadata`
- `generate_covers.py` → `book.cover_metadata`

Metadata includes: `generated_at`, `model`, `used_reference`, `reference_version`

### Consistent Feedback System
All review pages have:
- Thumbs up/down buttons
- localStorage persistence with timestamps
- Copy to clipboard
- Create GitHub Issue button
- Filter buttons (All, Unreviewed, Needs Regen)

### Bug Fixes Applied
- Image/prompt alignment: Using original page index for image filenames
- Word icons: Fixed path, added hardcoded word list
- Activity icons: Changed to image onload/onerror
- Reference images: Auto-detect versioned files (_v4, _v3, _v2, base)

---

## Still TODO

### Review Pages Needed
1. **Activities Config** (`/review/activities.html`)
   - Activity definitions and settings
   - Word lists per activity
   - Activity-to-skill mapping

2. **Phonics Data** (`/review/phonics.html`)
   - Detailed phoneme mappings
   - Letter-sound relationships

3. **Word Lists** (`/review/words.html`)
   - Decodable words by level
   - Sight words progression

### Content Production
- [ ] Create a new book end-to-end using current pipeline
- [ ] Test review workflow on fresh content
- [ ] Validate metadata tracking works

---

## Quick Reference

### Book Creation Pipeline
```bash
# 1. Create book JSON
uv run python scripts/create_book.py

# 2. Generate reference sheet (9-panel)
uv run python scripts/generate_references.py --book {slug}

# 3. Generate cover
uv run python scripts/generate_covers.py --book {slug}

# 4. Generate page images (with style transfer)
uv run python scripts/generate_page_images.py {slug} --use-reference

# 5. Review at
https://funbookies.com/review/books.html
```

### Data Files
- `/public/data/level-specs.json` - 28-level curriculum
- `/public/data/phonics-words.json` - Words by level
- `/public/books/manifest.json` - All books metadata

### Review URL
https://funbookies.com/review/
