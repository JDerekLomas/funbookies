# Book Scenes Skill

Generate concrete, visual scene descriptions for each page of a FunBookies book.

## When to Use

Use this skill when:
- A book JSON exists but needs scene descriptions
- Scene descriptions need to be rewritten (too abstract/poetic)
- Adding a new book that was created without scenes

## Usage

```
/book-scenes <slug>
```

Examples:
- `/book-scenes b2-if-i-could-only-be-a-red-tractor`
- `/book-scenes c1-the-knights-quest`

## How It Works

### 1. Load Book JSON

Read the book from `/public/books/{slug}.json` and extract:
- `characters` - Character descriptions
- `setting_context` - Cultural/geographic context
- `story_elements` - When each element first appears (for negative prompts)
- `pages` - All pages that need scene descriptions

### 2. Apply Scene Description Rules

For each story page, generate a scene description following the **Concrete > Poetic** rule:

```
BAD:  "The world around her starts to blur and shimmer. Dreamy atmosphere."
GOOD: "Tiia, a small blonde girl (5-6) in blue overalls, sits in golden barley.
       Eyes closed, peaceful smile. Red tractor in background field."
```

**Every scene must include:**

| Element | Description | Example |
|---------|-------------|---------|
| WHO | Character with visual identifiers | "Tiia, a small blonde girl (5-6) with wispy hair in blue overalls" |
| WHERE | Setting with cultural specificity | "sits cross-legged in tall golden barley" |
| WHAT | Action matching page text exactly | "eyes closed, peaceful smile" |
| CONTEXT | Only elements relevant to THIS page | "Red tractor works in muddy field behind her" |
| STYLE | Always end with style instruction | "Warm watercolor style." |

### 3. Rules to Follow

**DO:**
- Describe what a camera would see
- Match the page text exactly
- Include character identifiers every time (don't assume the model remembers)
- Use setting_context for cultural specificity
- End every scene with "Warm watercolor style."

**DON'T:**
- Use abstract/mood language ("dreamy", "magical feeling", "blur and shimmer")
- Mention what shouldn't be there ("no airplane visible")
- Reference future story events ("about to imagine being a tractor")
- Use negations of any kind

### 4. Update Book JSON

Add `scene` field to each story page:

```json
{
  "page": 6,
  "story_page": 1,
  "type": "story",
  "text": "Tiia sits in the hot sun.\nA red tractor digs in the mud.",
  "scene": "Tiia, a small blonde girl (5-6) with wispy hair in blue overalls, sits cross-legged in tall golden barley. Bright summer sun overhead. In the field behind her, an old red tractor with large wheels digs through dark brown muddy soil. Estonian countryside with birch trees at the edge of the field. Warm watercolor style."
}
```

Also add/update the cover scene and end page scene.

### 5. Generate Reference Prompt

Create the `reference_prompt` field for the 9-panel style sheet:

```json
{
  "reference_prompt": "9-PANEL STYLE REFERENCE SHEET for children's book illustration\n\nFOCUS: Character design, setting elements, and color palette. NOT story scenes.\n\nRow 1 - CHARACTER DESIGN:\n[1] Character front view...\n[2] Character expressions...\n[3] Character in motion...\n\nRow 2 - KEY OBJECTS:\n[4] Object 1...\n[5] Object 2...\n[6] Props together...\n\nRow 3 - SETTING:\n[7] Exterior...\n[8] Landscape...\n[9] Interior...\n\nSTYLE: Warm soft watercolor...\n\nCRITICAL: NO TEXT, NO WORDS, NO LETTERS anywhere."
}
```

**Key principle:** Reference should show STYLE VOCABULARY (character, objects, settings), NOT story scenes. This prevents content contamination.

### 6. Checkpoint

After generating, show the user:
1. All scene descriptions in a table
2. The reference_prompt
3. Ask: "Do these scene descriptions look concrete and visual? Ready to generate the reference sheet?"

## Scene Description Template

Use this template for each page:

```
[CHARACTER with identifiers], [LOCATION with cultural context]. [ACTION matching text]. [RELEVANT CONTEXT for this page only]. Warm watercolor style.
```

## Example Transformation

**Page text:** "If I could only be a red tractor!" Tiia shuts her eyes.

**Before (bad):**
```
Close-up of the blonde girl with her eyes squeezed shut, a peaceful smile
on her face, sunlight on her hair. The world around her starts to blur
and shimmer. Dreamy watercolor style.
```

**After (good):**
```
Close-up of Tiia, a small blonde girl (5-6) with wispy hair in blue overalls.
Her eyes are squeezed shut, a big hopeful smile on her face. Golden sunlight
glows on her hair. The red tractor is visible but blurred in the background
field. Warm watercolor style.
```

## Validation Checklist

Before finishing, verify each scene:
- [ ] Has WHO with visual identifiers
- [ ] Has WHERE with cultural context
- [ ] Has WHAT matching page text
- [ ] Has only relevant CONTEXT (no future elements)
- [ ] Ends with STYLE instruction
- [ ] Contains NO abstract language
- [ ] Contains NO negations
- [ ] Contains NO future references
