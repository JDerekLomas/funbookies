# FunBookies Development Log

Development session notes and changes.

---

## 2026-01-20: Improved 9-Panel Reference Prompt Generation

### Summary
Enhanced `generate_story.py` to produce higher-quality 9-panel reference image prompts based on patterns from effective past generations.

### Key Improvements

#### 1. Band-Specific Visual Styles
Added automatic style guidance based on reading band:
- **Band A**: Simple bold shapes, pastel, minimal detail
- **Band B**: Playful watercolor, vibrant, expressive
- **Band C**: Rich watercolor, detailed, dynamic
- **Band D**: Sophisticated, nuanced lighting, atmospheric

#### 2. Proper 3-Row Reference Structure
Reference prompts now follow the proven template:
```
Row 1 - Main Character:
[1] Front view [2] Action pose [3] Expression variation

Row 2 - Supporting Elements:
[4] Secondary character/object [5] **KEY MOMENT** (center hero shot) [6] Key prop

Row 3 - Settings:
[7] Primary setting [8] Lighting/time variation [9] Final heartwarming scene
```

#### 3. Technical Requirements
All prompts now include:
- Style block with palette (sage, terracotta, cream, soft gold)
- Format: Square 1:1, 3x3 grid, thin white borders
- CRITICAL: NO TEXT clause

### Files Changed
- `scripts/generate_story.py` - Enhanced reference prompt instructions + band styles
- `public/books/frog-gets-fun.json` - Test book with improved reference prompt
- `public/review/frog-gets-fun-review.html` - Review page

### Text Revisions Made
Fixed awkward generated text:
- "has not got" → "wants"
- "can not get" → "did not get"
- "is wet and has mud" → "is wet with mud"

### Next Steps
- Generate reference image: `python3 scripts/generate_references.py --book frog-gets-fun`
- Test across more levels to tune per-band output

---

## 2026-01-20: Audio System Overhaul - Pre-recorded Audio for All Activities

### Summary
Replaced raw TTS (Text-to-Speech) with pre-recorded audio across all activities and games. Generated word audio, updated blend/letter sounds with experiment winners, and created a letter sounds variant experiment page.

### What Was Done

#### 1. Word Audio Generation
- Generated **255 word audio files** using OpenAI TTS (tts-1-hd, nova voice)
- Location: `/public/audio/words/{word}.mp3`
- Created review page: `/public/review/word-audio.html`

#### 2. Blend Audio Updates
Based on experiment results, updated blend audio in `/audio/phonemes/`:
- **Schwa variants (v2):** br, dr, sm, tw
- **Bare variants (v1):** all other 16 blends

#### 3. Letter Sounds Updates
Updated 9 letter sounds with winning variants from experiments:
- c=k, e=ĕ, f=feh, i=short-i, l=lll, p=p, r=rrr, v=vah, z=zz

#### 4. Letter Sounds Variant Experiment
Created experiment page for all 26 letters:
- Location: `/public/experiments/letter-sounds/variants.html`
- Shows 3-5 variants per letter with play-on-click
- "None" option for each letter
- Progress bar, localStorage persistence, copy/submit results
- Generated 51 new audio files for missing letter variants

#### 5. Activity Audio Updates
Updated **7 activities** to use `AudioUtils` instead of raw TTS:

| Activity | Method Used |
|----------|-------------|
| say-the-sound.html | `AudioUtils.playSound()` |
| sight-words.html | `AudioUtils.playWord()` |
| rhyme-match.html | `AudioUtils.playWord()` |
| sentence-scramble.html | `AudioUtils.playWord()` |
| word-families.html | `AudioUtils.playWord()` |
| read-aloud.html | `AudioUtils.playWord()` |
| letter-sounds-review.html | `AudioUtils.playSound()` for sounds mode |

All activities now use pre-recorded audio with automatic TTS fallback.

#### 6. Sound-Boxes Improvements
- Added click-to-place (in addition to drag)
- Success sequence: plays each letter sound, then full word
- Added delay between last letter and full word

### Files Changed
- `/public/audio/words/` - 255 new word audio files
- `/public/review/word-audio.html` - New review page
- `/public/experiments/letter-sounds/variants.html` - New experiment page
- `/public/activities/letter-sounds/variants/` - 51 new variant audio files
- `/public/activities/sound-boxes.html` - Click-to-place, success sequence
- `/public/activities/say-the-sound.html` - AudioUtils integration
- `/public/activities/sight-words.html` - AudioUtils integration
- `/public/activities/rhyme-match.html` - AudioUtils integration
- `/public/activities/sentence-scramble.html` - AudioUtils integration
- `/public/activities/word-families.html` - AudioUtils integration
- `/public/activities/read-aloud.html` - AudioUtils integration
- `/public/activities/letter-sounds-review.html` - AudioUtils integration

### Audio System Architecture
```
AudioUtils.playWord(word)   → /audio/words/{word}.mp3 → TTS fallback
AudioUtils.playSound(letter) → /activities/letter-sounds/openai-us/sounds/{letter}.mp3 → TTS fallback
```

### Current Audio Inventory
| Type | Count | Location |
|------|-------|----------|
| Word audio | 255 | `/audio/words/` |
| Letter sounds | 26 | `/activities/letter-sounds/openai-us/sounds/` |
| Letter names | 26 | `/activities/letter-sounds/openai-us/names/` |
| Phonemes | 61 | `/audio/phonemes/` |
| Instructions | 30 | `/audio/instructions/` |

---

## 2026-01-20: Completed generate_story.py - Single-Pass Story Generator

### Summary
Finished the `generate_story.py` script for single-pass story + scene generation. Iteratively improved the prompt to fix coherence issues.

### What Was Built

`scripts/generate_story.py` - Complete story generator with:
- Single LLM call generates: story text, scene descriptions, characters, reference prompt
- HTML review page at `public/review/{slug}-review.html`
- Saves book JSON to `public/books/{slug}.json`

### Key Prompt Improvements

1. **Meaning Over Phonics** - Added explicit rules to prevent nonsense sentences
   - BAD: "He got wet in the sun" (sun doesn't make you wet)
   - GOOD: "Max jumped in the mud. Mud splashed on his nose!"

2. **Continuity Tracking** - Scenes must track character state
   - If muddy on page 4, still muddy on page 5
   - If in bath, will be WET when gets out
   - Fixed: "Now Max is not wet" after bath → "Max is wet but clean"

3. **Level-Appropriate Vocabulary** - Stricter word limits
   - Max words per sentence enforced
   - Vocabulary check for multi-syllable words

4. **Reference Prompt After Story** - Reference prompt now based on actual story content
   - Includes actual characters, objects, settings from the story

### Usage

```bash
python3 scripts/generate_story.py --level B2 --concept "A pup in mud" --setting "backyard"
python3 scripts/generate_story.py --level B1 --concept "A cat and a hat" --setting "house" --dry-run
```

### Files Changed
- `scripts/generate_story.py` - Complete rewrite (was 35 lines, now ~420 lines)
- `public/review/` - New directory for review HTML pages
- `public/books/pup-in-mud.json` - Test book generated
- `public/books/mud-pup-fun.json` - Test book generated
- `public/books/pip-gets-a-hit.json` - Test book generated

### Review Page Features
- Shows characters with visual details
- Shows reference image prompt
- Shows word lists (sound out / sight / heart)
- Story pages with scene descriptions expanded
- Generation prompt visible (collapsible) for debugging

### Still To Do
- Scene descriptions could use more enrichment guidance
- May need per-level prompt tuning
- Test across more levels (A, C, D bands)

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
