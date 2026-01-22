# Book Creation Skill (API-First)

Create children's books using APIs directly. The wizard is a **display layer only** - Claude Code does the work via API calls and file writes, wizard shows results.

## Architecture

```
Claude Code → MuleRouter API → save images → deploy → wizard displays
```

**Key Principle:** Files are source of truth. Deploy after each step so user sees results.

## Workflow Overview

| Step | Claude Action | User Sees |
|------|--------------|-----------|
| 1. Story | Write book JSON | Wizard Phase 3 (story review) |
| 2. References | Call MuleRouter directly | Wizard Phase 4 (reference images) |
| 3. Pages | Call MuleRouter for each page | Wizard Phase 5 (page images) |
| 4. Publish | Deploy to Vercel | Reader view |

## Step 1: Create Book JSON

Generate the book data and write directly to file:

**Required JSON structure:**
```json
{
  "title": "Book Title",
  "slug": "book-title",
  "level": "B1",
  "status": "draft",
  "characterName": "Character",
  "characterDescription": "visual details for image consistency",
  "setting": "where the story takes place",
  "storyType": "imagination",
  "visual_style": "art style prompt",
  "pages": [
    {
      "page": 1,
      "type": "cover",
      "text": "Book Title",
      "scene": "Cover illustration: Character in setting, title composition..."
    },
    {
      "page": 2,
      "type": "story",
      "text": "First story text.",
      "scene": "Visual scene description for image generation"
    },
    ...
    {
      "page": 10,
      "type": "end",
      "text": "The End",
      "scene": "Final scene showing resolution..."
    }
  ]
}
```

**Then show to user:**
```bash
vercel --prod
open "https://funbookies.com/wizard/?slug={slug}&phase=3"
```

**ASK:** "Review the story at the link above. Ready to generate reference images?"

## Step 2: Generate Reference Images

Generate 3 reference sheets using MuleRouter directly (no Python script needed).

### 2a. Style Guide (Character Sheet)

Use **nano-banana-pro** (T2I, $0.15) with this metaprompt:

```
9-PANEL CHARACTER REFERENCE for '{title}'

Create a 3x3 grid showing {characterName} from different angles and expressions.

CHARACTER (draw EXACTLY as described):
{characterDescription}

Row 1 - Views:
[1] {characterName} front view, full body, neutral expression
[2] {characterName} side profile, walking pose
[3] {characterName} 3/4 view, slight smile

Row 2 - Expressions:
[4] {characterName} happy, wide smile, eyes crinkled
[5] {characterName} sad or worried, downturned mouth
[6] {characterName} surprised, eyes wide, mouth O-shaped

Row 3 - Actions:
[7] {characterName} running, legs mid-stride
[8] {characterName} sitting, relaxed pose
[9] {characterName} in key story pose

CRITICAL: Same character design in ALL 9 panels.
Style: {visual_style}

NO TEXT, NO WORDS, NO LETTERS anywhere in the image.
```

**MuleRouter call:**
```bash
# Use mulerouter-skills to generate
uv run python ~/.claude/plugins/cache/mulerouter-skills/.../models/google/nano-banana-pro/generation.py \
  --prompt "..." --size "1024*1024"
```

Save to: `public/books/references/{slug}_multi/style_guide.png`

### 2b. Opening Scenes (First Half)

Use **wan2.6-image** (I2I, $0.03) with style_guide as reference:

```
9-PANEL SCENES - FIRST HALF for '{title}'

Using the style from the reference image, create scenes from the FIRST HALF of the story.

Row 1:
[1] {scene from page 2}
[2] {scene from page 3}
[3] {scene from page 4}

Row 2:
[4] {scene from page 5}
[5] {scene from page 6}
[6] {scene from page 7}

Row 3:
[7] Establishing shot of {setting}
[8] {characterName} in characteristic pose
[9] Transition moment

Style: {visual_style}
Match the character design from the reference image exactly.

NO TEXT, NO WORDS, NO LETTERS anywhere in the image.
```

Save to: `public/books/references/{slug}_multi/opening_scenes.png`

### 2c. Closing Scenes (Second Half)

Use **wan2.6-image** (I2I, $0.03) with style_guide as reference:

```
9-PANEL SCENES - SECOND HALF for '{title}'

Using the style from the reference image, create scenes from the SECOND HALF of the story.

Row 1:
[1] {scene from page 8}
[2] {scene from page 9}
[3] {scene from page 10}

Row 2:
[4] {scene from page 11}
[5] {scene from page 12}
[6] {scene from page 13}

Row 3:
[7] Climax moment
[8] Resolution scene
[9] Happy ending - {characterName} satisfied/content

Style: {visual_style}
Match the character design from the reference image exactly.

NO TEXT, NO WORDS, NO LETTERS anywhere in the image.
```

Save to: `public/books/references/{slug}_multi/closing_scenes.png`

### Update Book JSON

Add multiRefs paths to book JSON:
```json
{
  "multiRefs": {
    "styleGuide": "/books/references/{slug}_multi/style_guide.png",
    "openingScenes": "/books/references/{slug}_multi/opening_scenes.png",
    "closingScenes": "/books/references/{slug}_multi/closing_scenes.png"
  }
}
```

**Then show to user:**
```bash
vercel --prod
open "https://funbookies.com/wizard/?slug={slug}&phase=4"
```

**ASK:** "Review the reference images. Ready to generate page images?"

## Step 3: Generate Page Images

For each page, use **wan2.6-image** (I2I, $0.03) with appropriate reference:
- Pages 1-7: Use `opening_scenes.png` as reference
- Pages 8+: Use `closing_scenes.png` as reference

**Page prompt template:**
```
Single cohesive children's book illustration filling the entire canvas.

{scene description from page}

Style: {visual_style}
Match the character and style from the reference image exactly.

NO TEXT, NO WORDS, NO LETTERS anywhere in the image.
```

Save to: `public/books/images/{slug}/page{NN}.png`

Update each page in book JSON with image path:
```json
{
  "page": 2,
  "type": "story",
  "text": "...",
  "scene": "...",
  "image": "/books/images/{slug}/page02.png"
}
```

**Then show to user:**
```bash
vercel --prod
open "https://funbookies.com/wizard/?slug={slug}&phase=5"
```

**ASK:** "Review the page images. Ready to publish?"

## Step 4: Publish

1. Generate thumbnail from cover:
```bash
uv run python scripts/generate_thumbnails.py --slug {slug}
```

2. Update book JSON: set `"status": "published"`

3. Deploy and open reader:
```bash
vercel --prod
open "https://funbookies.com/reader.html?book={slug}"
```

The book will now appear in the book listing at `/books/`.

## Visual Style Selection

Choose a visual style that matches the story's mood:

| Style | Best For | Example |
|-------|----------|---------|
| `warm-watercolor` | Cozy, gentle, nature | Forest animals, bedtime |
| `bold-graphic` | Action, adventure | Racing, jumping, sports |
| `soft-digital` | Modern, friendly | School, home, family |
| `sketchy-whimsical` | Silly, playful | Fantasy, dreams |
| `retro-midcentury` | Classic feel | Vintage settings |
| `cozy-detailed` | Rich environments | Homes, gardens |

**Format:** `"{style} children's book illustration, {mood}, {qualities}"`

## Scene Description Rules

1. **Never use negations** - "no ball" generates a ball
2. **Physical over emotional** - "eyes wide" not "scared"
3. **Explicit character presence** - say who IS there
4. **Single scene** - "One cohesive illustration"
5. **NO TEXT** - end with "NO TEXT, NO WORDS, NO LETTERS"

### CRITICAL: Accurate Actions

**The scene must match the text EXACTLY.** If the text says:
- "Fox runs" → Scene shows fox mid-stride, legs moving
- "Fox taps the box" → Scene shows paw touching box
- "Fox sits" → Scene shows fox seated, NOT standing

**Before writing each scene, ask:** "What specific physical action does the text describe?"

## Level Guidelines

| Level | Words/Page | Pages | Guidance |
|-------|-----------|-------|----------|
| A0-A2 | 2-4 | 8-14 | Simple words, picture-driven |
| B1-B2 | 6-8 | 12-16 | Short sentences, dialogue |
| C1-C2 | 10-12 | 16-20 | Complex sentences |
| D1-D2 | 15-18 | 20-24 | Full narrative |

## Example Session

```
User: Create a B2 book about a dragon who collects buttons

Claude:
1. Generates story with 14 pages
2. Writes to public/books/button-dragon.json
3. Deploys and opens wizard Phase 3
4. ASKS: "Review the story. Ready for references?"

User: Yes

5. Builds style_guide prompt from book data
6. Calls MuleRouter nano-banana-pro T2I
7. Saves to references/button-dragon_multi/style_guide.png
8. Builds opening_scenes prompt with actual scenes 2-7
9. Calls MuleRouter wan2.6-image I2I with style_guide ref
10. Saves to opening_scenes.png
11. Builds closing_scenes prompt with scenes 8-14
12. Calls MuleRouter wan2.6-image I2I with style_guide ref
13. Saves to closing_scenes.png
14. Updates book JSON with multiRefs
15. Deploys and opens wizard Phase 4
16. ASKS: "Review references. Ready for pages?"

User: Yes

17. For each page, calls MuleRouter with appropriate reference
18. Saves images, updates book JSON
19. Deploys and opens wizard Phase 5
20. ASKS: "Review pages. Ready to publish?"

User: Yes

21. Generates thumbnail, sets status published
22. Opens reader: https://funbookies.com/reader.html?book=button-dragon
```

## File Locations

| Content | Path |
|---------|------|
| Book JSON | `public/books/{slug}.json` |
| Style guide | `public/books/references/{slug}_multi/style_guide.png` |
| Opening scenes | `public/books/references/{slug}_multi/opening_scenes.png` |
| Closing scenes | `public/books/references/{slug}_multi/closing_scenes.png` |
| Page images | `public/books/images/{slug}/page{NN}.png` |

## Cost Estimate

- Style guide (nano-banana-pro T2I): ~$0.15
- Opening scenes (wan2.6 I2I): ~$0.03
- Closing scenes (wan2.6 I2I): ~$0.03
- Page images (wan2.6 I2I): ~$0.03 each
- 14-page book total: ~$0.60-0.80

## MCP Browser Use

**Only use MCP for:**
- Taking screenshots for debugging
- Verifying page rendered correctly

**Do NOT use MCP for:**
- Primary workflow
- Clicking buttons
- Generating content
