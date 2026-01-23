# Book Creation Skill

Create children's books by writing JSON directly. The wizard is a display/generation layer - Claude Code writes files, wizard shows results and generates images.

## Quick Start

```bash
# 1. Write book JSON
# 2. Deploy
vercel --prod
# 3. Open wizard
open "https://funbookies.com/wizard/?slug={slug}&phase=3"
```

## Workflow

| Step | Claude Action | User Sees |
|------|--------------|-----------|
| 1. Story | Write `public/books/{slug}.json` | Wizard Phase 3 (story review) |
| 2. References | User clicks "Generate" in wizard | Wizard Phase 4 (reference images) |
| 3. Pages | User clicks "Generate" in wizard | Wizard Phase 5 (page images) |
| 4. Publish | Set `status: "published"`, deploy | Reader view |

## Book JSON Structure

Write to `public/books/{slug}.json`:

```json
{
  "title": "Nat the Bat",
  "slug": "nat-the-bat",
  "level": "B1",
  "status": "draft",
  "characterName": "Nat",
  "characterDescription": "small brown bat with big round eyes, fuzzy body, small pointed ears, and delicate wings folded at sides when not flying",
  "setting": "cave at dusk transitioning to night, with rocks, moss, and eventually stars visible outside",
  "storyType": "growth",
  "visual_style": "soft digital children's book illustration, gentle glowing light, warm cave tones, cozy atmosphere, magical nighttime",
  "pages": [
    {
      "page": 1,
      "type": "cover",
      "text": "Nat the Bat",
      "scene": "Cover illustration: A small brown bat with big round eyes flying through a starry night sky. Wings spread wide. Moon glowing in background. The bat looks curious and happy. Deep blue night with twinkling stars."
    },
    {
      "page": 2,
      "type": "story",
      "text": "Nat is a bat.",
      "scene": "Medium shot: Small brown bat named Nat hanging upside down from a cave ceiling. Big round eyes, fuzzy body, wings folded. Soft evening light coming from cave entrance. Warm brown cave walls."
    },
    {
      "page": 10,
      "type": "end",
      "text": "The End",
      "scene": "Wide shot: Nat the bat soaring through beautiful starry night sky. Full moon in background. Peaceful, magical nighttime scene."
    }
  ]
}
```

## Required Fields

| Field | Purpose | Example |
|-------|---------|---------|
| `title` | Book title | "Nat the Bat" |
| `slug` | URL-safe identifier | "nat-the-bat" |
| `level` | Reading level | "B1" |
| `status` | "draft" or "published" | "draft" |
| `characterName` | Main character name | "Nat" |
| `characterDescription` | Visual details for consistency | "small brown bat with big round eyes..." |
| `setting` | Where story takes place | "cave at dusk..." |
| `visual_style` | Art style for all images | "soft digital children's book illustration..." |
| `pages` | Array of page objects | See below |

## Page Structure

Each page needs:
- `page`: Number (1-indexed)
- `type`: "cover", "story", or "end"
- `text`: The readable text
- `scene`: Visual description for image generation

## Scene Description Rules

1. **Start with shot type**: "Wide shot:", "Medium shot:", "Close-up:"
2. **Include character by name**: "Nat the bat hanging..."
3. **Physical descriptions**: "eyes wide", "wings spread"
4. **Never use negations**: "no ball" generates a ball
5. **End prompt**: Wizard adds "NO TEXT" automatically

### Good Scene Example
```
Medium shot: Nat the bat opening his eyes wide with surprised expression. One wing uncurling from his body. Around him, the dark cave is visible in soft blue-gray tones.
```

### Bad Scene Example
```
The bat is scared and there's no light.
```
(Uses emotion "scared" instead of physical description, uses negation "no light")

## Visual Style Options

Choose based on story mood:

| Style | Best For |
|-------|----------|
| `soft digital children's book illustration, gentle lighting, warm colors` | Cozy, friendly |
| `warm watercolor illustration, soft edges, luminous quality` | Nature, gentle |
| `bold graphic illustration, simple shapes, primary colors` | Action, energy |
| `sketchy whimsical illustration, expressive lines` | Silly, playful |
| `cozy detailed illustration, rich warm colors, intricate patterns` | Rich environments |

## Level Guidelines

| Level | Words/Page | Pages | Focus |
|-------|-----------|-------|-------|
| A0-A2 | 1-3 | 8-12 | Single words, labels |
| B1-B2 | 4-6 | 10-14 | Simple sentences, CVC words |
| B3-B6 | 6-8 | 12-16 | Digraphs, blends |
| C1+ | 10+ | 16-20 | Complex sentences |

## Example Session

```
User: Create a B1 book about a bat who learns to see in the dark

Claude:
1. Writes public/books/nat-the-bat.json with full story
2. Runs: vercel --prod
3. Opens: https://funbookies.com/wizard/?slug=nat-the-bat&phase=3
4. Says: "Review the story. Click through to Phase 4 to generate reference images, then Phase 5 for page images."

User reviews in wizard, generates images, then:

5. Updates JSON: "status": "published"
6. Runs: vercel --prod
7. Opens: https://funbookies.com/reader.html?book=nat-the-bat
```

## File Locations

| Content | Path |
|---------|------|
| Book JSON | `public/books/{slug}.json` |
| Reference images | `public/books/references/{slug}_multi/*.png` |
| Page images | `public/books/images/{slug}/page{NN}.png` |
| Thumbnail | `public/images/thumbs/{slug}.jpg` |

## Wizard Handles

The wizard automatically:
- Builds image prompts from book data
- Uses `characterName`, `characterDescription`, `visual_style`
- Adds "NO TEXT" to all prompts
- Saves generated images back to book JSON
- Manages multi-reference cascade (style guide → scenes)

Claude Code just writes the book JSON. Wizard does the rest.

## Publishing Checklist

Before setting `status: "published"`:
1. All pages have images (check `pages[].image` fields)
2. Story text is final
3. Generate thumbnail: `uv run python scripts/generate_thumbnails.py --slug {slug}`
