# FunBookies Development Log

Development session notes and changes.

---

## 2026-01-19: Multi-Ref Image Workflow & Story Generation Learnings

### Summary
Completed major experiment comparing 9-panel composite references vs individual multi-ref approach for image generation. Generated images for 6 books, deployed 2 that worked well.

### Key Learnings

#### 1. Multi-Ref > 9-Panel Composite
**The Problem:** 9-panel reference sheets cause "grid contamination" - the model copies the grid layout into outputs and bleeds content between panels.

**The Solution:** Individual reference images that can be selectively combined:
```
{slug}_multi/
├── char_{name}_front.png    # Character front view
├── char_{name}_side.png     # Character in motion
├── char_{name}_expression.png
├── env_day.png              # Environment (day)
├── env_night.png            # Environment (night, if needed)
└── style_palette.png        # Color/style reference
```

**Why it works:** wan2.6-image supports up to 3 refs. Select the most relevant 3 per page:
- Character ref (main character in scene)
- Environment ref (day/night as appropriate)
- Style ref (always include for color consistency)

#### 2. Story Quality Issues Identified
User feedback on 4/6 generated books: "too many unnecessary sentences, not enough interest, too fake, no soul"

**Books that worked:** the-big-pig, bake-day
**Books that didn't:** fit-it-in, sled-run, crab-grab, sail-away

**Problems with failing stories:**
- Filler sentences that don't advance plot
- Forced emotional beats ("Oh no!" when nothing is at stake)
- Repetitive padding to hit page count
- Abrupt/unsatisfying endings
- No genuine character wants or tension

**Insight:** The two-pass generation (story first, then scenes) may disconnect the visual storytelling from narrative. Stories feel written to hit decodability targets rather than to delight children.

#### 3. Proposed Story Generator Improvements
Started prototyping `generate_story.py` with these changes:

1. **Single-pass generation** - Story text + image descriptions created together in one LLM call, so visual moments drive the narrative
2. **Wordlist as palette, not prison** - Treat decodable words as creative inspiration rather than strict constraint. Allow occasional "exception words" when essential.
3. **HTML review page** - Show complete story with image prompts before any image generation. User must approve story quality first.

#### 4. Image Naming Convention
**Correct:** `public/books/images/{slug}_page{NN}.png` (flat in images dir)
**Wrong:** `public/books/images/{slug}/page{NN}.png` (subdirectory)

The reader expects the flat naming convention.

#### 5. Page Number Confusion
Book JSON has both `page` (actual page number, 1-22) and `story_page` (story-only count, 1-12).

Scripts need to use `page` not `story_page` when generating images:
```bash
# Get actual page numbers for story pages
jq -r '[.pages[] | select(.type == "story") | .page] | join(",")'
```

### Commands Reference

```bash
# Generate individual refs for a book
uv run python scripts/multi_ref_experiment.py {slug} --generate-refs

# Generate all story pages with split-3ref
uv run python scripts/multi_ref_experiment.py {slug} --strategies split-3ref --all

# Generate specific pages
uv run python scripts/multi_ref_experiment.py {slug} --strategies split-3ref --pages 6,7,8,9,10
```

### Cost Data
- wan2.6-image: $0.03/image
- 17 pages for sail-away: $0.51 total
- Full book (cover + 12-18 pages): ~$0.50-0.60

### Files Changed
- `public/books/{slug}.json` - Added `characters` with `visual_shorthand` to all 6 books
- `public/books/images/` - Generated images for the-big-pig, bake-day
- `IMAGE_GENERATION_WORKFLOW.md` - Updated for multi-ref approach
- `.claude/skills/book-create.md` - Added story approval checkpoint

### What's Next
- Finish `generate_story.py` prototype with single-pass + review page
- Test whether "wordlist as palette" produces more natural stories
- Re-generate stories for the 4 failing books once generator is improved

---

## 2026-01-18: Surrounding Material Redesign

**Commit:** `a95072b`

### Changes

Complete redesign of all non-story pages to improve branding and visual appeal.

**New End Page**
- Dedicated `end` page type with celebration overlay
- Animated star icon with pulse effect
- "Read Again" and "More Books" action buttons
- Uses story ending image as background

**Copyright Page**
- Added FunBookies logo/icon
- Dynamic copyright year from book creation date
- Book title and ID displayed
- Decorative divider element

**Back Cover**
- Now uses cover image as fallback when no back cover image specified
- Book-specific blurb from back_cover page text or story premise
- Shows actual words from book's word_list
- Logo in header and footer

**Series Info Page**
- Logo and "Books that grow with your reader" tagline
- Level ladder showing current level with "You are here!" indicator
- CTA to funbookies.com

**Level Info Page**
- "Get Ready to Read!" header
- Skill card showing book's target phonics
- Book-specific skill description

**Parent Guide Page**
- Logo in header
- Emoji icons for Before/During/After reading sections
- Cleaner tip layout

**Wordsearch Page**
- Larger 32px cells (up from 28px)
- Uses actual sound_out words from book's word_list
- Gradient background, pill-style word bank
- Search icon in header

**Cover Page Improvements**
- Corner band extended (280px wide) so it extends past edges
- FunBookies logo in bottom-right corner
- Drop shadow on band text

**Story Pages**
- Added FunBookies logo watermark in top-right corner

### Files Changed
- `public/reader.html` - All page type templates and CSS

### Notes
- All special pages now include FunBookies branding
- Pages use book-specific content where available (word lists, blurbs, skills)
- Consistent visual language across all page types

---

## 2025-01-18: Cover and Back Cover Improvements

**Commit:** `a95072b`

### Changes

**Cover Page**
- Moved FunBookies logo from bottom right to top right

**Back Cover**
- Added tagline: *"Every child can learn to read."*
- Added feature badges: Decodable • Phonics-based • Research-backed
- Improved footer styling

### Files Changed
- `public/reader.html` - Cover and back cover layouts

---

## 2025-01-18: Book Editor Improvements

**Commit:** `6f79f9a`

### Changes

**Text Editor Panel**
- Added "Page Text" section above image prompt editor in edit mode
- Users can now edit and save story text directly
- Only shows on story pages (hidden on covers, copyright, etc.)

**Save Button Visibility**
- Save Prompt button is now always visible (terracotta color)
- Previously only appeared on hover
- Status messages appear directly under each save button

**Image Version History**
- When clicking "Use as Current Image", the old image is archived to version history
- Past versions show in "Page Image Versions" section
- Hover over thumbnails to see metadata (prompt, model, timestamp)
- Click any version to restore it as current
- Info icon indicates versions with metadata

### Files Changed
- `public/reader.html` - Editor UI and version tracking logic

### Notes
- Version history only tracks images that were actually used as "current", not every generation attempt
- Existing pages won't have version history until the next time an image is replaced
