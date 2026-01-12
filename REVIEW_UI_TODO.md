# Review UI - Work in Progress

## Completed This Session

### 1. Review Hub Consolidation
- Created `/public/review/` directory with consolidated review interfaces
- Hub at `/review/index.html` links to all review tools

### 2. Book Review Redesign (`/review/books.html`)
- 3-panel layout: sidebar | main view | info panel
- Page-by-page navigation with arrow keys
- Creation Notes (page -2) and Reference Sheet (page -1) as special pages
- Per-page feedback with thumbs up/down and notes
- Export feedback per book

**NEEDS FIXES:**
- [ ] Scene prompts not aligned properly with pages
- [ ] Images too large - should fit without scrolling
- [ ] Reference sheet should be IN the page flow (not right panel) so it can receive feedback
- [ ] Right panel should show: page info, scene prompt, feedback only (no ref image)

### 3. Curriculum Review (`/review/curriculum.html`) - NEW
- Bands Overview tab
- Level Details table (28 levels)
- Book Progression timeline
- Phonics by Level cards

### 4. Consistent Feedback System
All review pages now have:
- Thumbs up/down (👍/👎) buttons
- localStorage persistence with timestamps
- "Copy" button for clipboard
- "Create GitHub Issue" button
- Filter buttons (All, Unreviewed, Needs Regen)

Updated pages:
- `/review/activity-icons.html`
- `/review/letter-sounds.html`
- `/review/word-icons.html`
- `/review/phoneme-sounds.html`

### 5. Bug Fixes
- Word icons: Fixed path from `/activities/word-icons/icons/` to `/activities/word-icons/`
- Word icons: Added hardcoded list of 255 words (directory listing doesn't work on Vercel)
- Activity icons: Changed from HEAD requests to image onload/onerror
- Book references: Now tries versioned files (_v4, _v3, _v2, base)

## Still TODO

### Book Review Fixes (Priority) - COMPLETED
1. ~~Make images smaller to fit without scrolling~~ - Added max-height constraint
2. ~~Move reference sheet from right panel INTO page navigation~~ - Ref is now page -1 in flow
3. ~~Fix scene prompt alignment~~ - Added page label, better styling with left border
4. ~~Right panel = page info + scene prompt + feedback only~~ - Removed reference section from panel

### New Review Pages Needed
1. **Activities Config** (`/review/activities.html`)
   - Activity definitions and settings
   - Word lists per activity
   - Activity-to-skill mapping

2. **Phonics Data** (`/review/phonics.html`)
   - More detailed than curriculum tab
   - Phoneme mappings
   - Letter-sound relationships
   - Editable/reviewable

3. **Word Lists** (`/review/words.html`)
   - Decodable words by level
   - Sight words progression
   - Story vocabulary

## Data Files Reference
- `/public/data/level-specs.json` - 28-level curriculum specs
- `/public/data/phonics-words.json` - Words by level
- `/public/data/sight-words.json` - Sight word lists
- `/public/data/story-vocabulary.json` - Story vocab
- `/public/books/manifest.json` - All books metadata
