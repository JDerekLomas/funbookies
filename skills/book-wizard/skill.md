# Book Creation Skill (API-First)

Create children's books using APIs and scripts directly. The wizard is a **display layer only** - Claude Code does the work via files/scripts, wizard shows results.

## Architecture

```
Claude Code → APIs/scripts → files/Supabase → deploy → wizard displays
```

**Key Principle:** Files are source of truth. Deploy after each step so user sees results.

## Workflow Overview

| Step | Claude Action | User Sees |
|------|--------------|-----------|
| 1. Story | Write book JSON | Wizard Phase 3 (story review) |
| 2. References | Run generate_references.py | Wizard Phase 4 (reference images) |
| 3. Pages | Run generate_page_images.py | Wizard Phase 5 (page images) |
| 4. Publish | Deploy to Vercel | Reader view |

## Step 1: Create Book JSON

Generate the book data and write directly to file:

```bash
# Write JSON to public/books/{slug}.json
```

**Required JSON structure:**
```json
{
  "title": "Book Title",
  "slug": "book-title",
  "level": "B1",
  "status": "published",
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
    {
      "page": 3,
      "type": "story",
      "text": "Second story text.",
      "scene": "Visual scene description..."
    },
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

Run the Python script to create 3 reference sheets:

```bash
uv run python scripts/generate_references.py --book {slug}
# Defaults to: --strategy multi --provider mulerouter
```

This creates:
- `public/books/references/{slug}_multi/style_guide.png` - Character/style 9-panel
- `public/books/references/{slug}_multi/opening_scenes.png` - First half pages
- `public/books/references/{slug}_multi/closing_scenes.png` - Second half pages

**Update book JSON with multiRefs paths:**
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

Run the Python script to create all page images:

```bash
uv run python scripts/generate_page_images.py {slug} --provider mulerouter
```

This creates: `public/books/images/{slug}/page{NN}.png`

The script automatically updates book JSON with image paths.

**Then show to user:**
```bash
vercel --prod
open "https://funbookies.com/wizard/?slug={slug}&phase=5"
```

**ASK:** "Review the page images. Ready to publish?"

## Step 4: Publish

Generate thumbnail and set published status:

```bash
# Generate thumbnail from cover image
uv run python scripts/generate_thumbnails.py --slug {slug}

# Set status to published (add to book JSON if not present)
# The book JSON should include: "status": "published"
```

**Update book JSON** to add `"status": "published"` if not already present.

Final deployment and reader link:

```bash
vercel --prod
open "https://funbookies.com/reader.html?book={slug}"
```

The book will now appear in the book listing at `/books/`.

## Scene Description Rules

1. **Never use negations** - "no ball" generates a ball
2. **Physical over emotional** - "eyes wide" not "scared"
3. **Explicit character presence** - say who IS there
4. **Single scene** - "One cohesive illustration"
5. **NO TEXT** - end with "NO TEXT, NO WORDS, NO LETTERS"

## Level Guidelines

| Level | Words/Page | Pages | Guidance |
|-------|-----------|-------|----------|
| A0-A2 | 2-4 | 8-14 | Simple words, picture-driven |
| B1-B2 | 6-8 | 12-16 | Short sentences, dialogue |
| C1-C2 | 10-12 | 16-20 | Complex sentences |
| D1-D2 | 15-18 | 20-24 | Full narrative |

## Validation (Optional)

Before generating images, validate the book:

```bash
uv run python scripts/validate_book_for_images.py {slug}
```

## MCP Browser Use

**Only use MCP for:**
- Taking screenshots for debugging
- Verifying page rendered correctly
- Testing if something isn't working

**Do NOT use MCP for:**
- Primary workflow
- Clicking buttons
- Filling forms
- Generating content

## Example Session

```
User: Create a B2 book about a dragon who collects buttons

Claude:
1. Generates story with 14 pages + title page
2. Writes to public/books/button-dragon.json
3. Deploys: vercel --prod
4. Opens wizard Phase 3
5. ASKS: "Review the story. Ready for references?"

User: Yes

6. Runs: python scripts/generate_references.py --book button-dragon
   (Script automatically adds multiRefs to book JSON)
7. Deploys: vercel --prod
8. Opens wizard Phase 4
9. ASKS: "Review references. Ready for pages?"

User: Yes

10. Runs: python scripts/generate_page_images.py button-dragon
    (Script automatically adds image paths to book JSON)
11. Deploys: vercel --prod
12. Opens wizard Phase 5
13. ASKS: "Review pages. Ready to publish?"

User: Yes

14. Opens reader: https://funbookies.com/reader.html?book=button-dragon
```

## Troubleshooting

### Images not showing in wizard/reader
The API automatically merges Supabase and static file content. Check:
1. API source: `curl https://funbookies.com/api/get-book?slug={slug} | jq .source`
   - "merged" = both sources combined (expected)
   - "static" = only static file found
   - "supabase" = only Supabase found
2. Verify static file has images: `cat public/books/{slug}.json | jq '.pages[0].image'`
3. Deploy if not deployed: `vercel --prod`

### Image directory naming
Ensure the `images/{slug}/` directory name matches the paths in JSON. Common issues:
- Hyphen vs no hyphen: `jean-s-cloud-house` vs `jeans-cloud-house`
- Check JSON image paths and rename directory if needed

## File Locations

| Content | Path |
|---------|------|
| Book JSON | `public/books/{slug}.json` |
| Multi-refs | `public/books/references/{slug}_multi/*.png` |
| Page images | `public/books/images/{slug}/page{NN}.png` |

## Cost Estimate

- Style guide (nano-banana): ~$0.15
- Scene refs x2 (wan2.6): ~$0.06
- Page images (wan2.6): ~$0.03 each
- 14-page book total: ~$0.60-0.80
