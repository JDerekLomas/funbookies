# Book Generation Guide

Two approaches to creating FunBookies books with AI assistance.

## Option A: Conversational Workflow (Recommended for Iteration)

Use this prompt to start a book generation conversation:

---

### Conversation Starter Prompt

```
I want to create a new FunBookies decodable reader. Let's work through this step by step with checkpoints.

**Book Concept:** [describe your idea]
**Reading Level:** [A0-D6, e.g., "B2"]
**Setting:** [optional cultural/geographic context, e.g., "rural Estonia"]

Please guide me through these steps, stopping for my approval at each checkpoint:

1. STORY TEXT - Write the decodable story text, show me page breaks and line breaks
2. SCENE DESCRIPTIONS - Generate concrete visual prompts for each page
3. REFERENCE SHEET - Create and generate the 9-panel style reference
4. PAGE IMAGES - Generate all page images with proper negative prompts
5. REVIEW & ITERATE - Deploy and review, fix any issues

At each step, show me the output and wait for my feedback before proceeding.
```

---

### Checkpoint Details

#### Checkpoint 1: Story Text
**Input:** Concept, level, setting
**Output:** Story text with `<page>` and `<line>` markers

```xml
<book level="B2" setting="rural Estonia">
  <page n="1">
    <line>Tiia sits in the hot sun.</line>
    <line>A red tractor digs in the mud.</line>
    <scene>Tiia, a small blonde girl (5-6) with wispy hair in blue overalls, sits cross-legged in tall golden barley. Bright summer sun overhead. In the field behind her, an old red tractor with large wheels digs through dark brown muddy soil. Estonian countryside with birch trees at the edge of the field. Warm watercolor style.</scene>
  </page>
  ...
</book>
```

**Review questions:**
- Does the text match the target phonics level?
- Are heart words appropriate and limited?
- Does each page have a clear visual moment?

#### Checkpoint 2: Scene Descriptions
**Input:** Story text with page breaks
**Output:** Concrete scene descriptions for each page

**Scene Description Rules:**
1. WHO - Character with visual identifiers (age, hair, clothing)
2. WHERE - Setting with cultural specificity
3. WHAT - Action that matches page text exactly
4. CONTEXT - Only elements relevant to THIS page
5. STYLE - "Warm watercolor style."

**Review questions:**
- Is each description concrete and visual (not poetic/abstract)?
- Are there any negations ("no airplane")? Remove them.
- Do descriptions match the text on each page?

#### Checkpoint 3: Reference Sheet
**Input:** Character specs, setting context, key objects
**Output:** 9-panel style reference image

**Reference Structure:**
- Row 1: Character design (front, expressions, motion)
- Row 2: Key objects (vehicles, props, toys)
- Row 3: Setting elements (exterior, landscape, interior)

**Key principle:** Focus on STYLE VOCABULARY, not story scenes. This prevents content contamination.

**Review questions:**
- Is the character consistent across panels?
- Does the setting match the cultural context?
- Are objects designed in a child-friendly style?

#### Checkpoint 4: Page Images
**Input:** Scene descriptions + reference + computed negative prompts
**Output:** All page illustrations

**Negative Prompt Strategy:**
```python
story_elements = {
    "airplane": 5,   # First appears on page 5
    "farmhouse": 9   # First appears on page 9
}

# For page 3, negative_prompt includes: "airplane, flying, farmhouse"
# For page 6, negative_prompt includes: "farmhouse" (airplane now OK)
```

**Review questions:**
- Do images match the text on each page?
- Is there content contamination from future story elements?
- Is the style consistent with the reference?

#### Checkpoint 5: Review & Iterate
**Actions:**
1. Deploy to funbookies.com
2. Review in edit mode: `/reader.html?book={slug}&mode=edit`
3. Identify pages that need regeneration
4. Re-run specific page generations with adjusted prompts

---

## Option B: Modular Skills

Individual skills for each step, allowing targeted re-runs.

### `/book-story`
Generate decodable story text with page structure.

```
/book-story "A girl daydreams about being a tractor and airplane" --level B2 --setting "rural Estonia"
```

**Output:** Book JSON with text, pages, word_list, but no images yet.

### `/book-scenes`
Generate scene descriptions for an existing book.

```
/book-scenes b2-if-i-could-only-be-a-red-tractor
```

**Output:** Updates book JSON with concrete scene descriptions for each page.

### `/book-reference`
Generate 9-panel style reference sheet.

```
/book-reference b2-if-i-could-only-be-a-red-tractor
```

**Output:** Reference image saved to `/books/references/{slug}_reference.png`

### `/book-images`
Generate all page images using reference and negative prompts.

```
/book-images b2-if-i-could-only-be-a-red-tractor
```

**Options:**
- `--pages 3,5,7` - Only regenerate specific pages
- `--cover` - Only regenerate cover
- `--all` - Regenerate everything

**Output:** Page images saved to `/books/images/{slug}_page{NN}.png`

### `/book-deploy`
Commit and push book to production.

```
/book-deploy b2-if-i-could-only-be-a-red-tractor
```

---

## Key Learnings (Why This Process)

### 1. Scene Descriptions: Concrete > Poetic
```
BAD:  "The world blurs and shimmers. Dreamy atmosphere."
GOOD: "Tiia sits in golden barley, eyes closed. Red tractor in background field."
```

### 2. Negative Prompts: Parameter, Not Prompt
Mentioning "no airplane" activates "airplane" in the model. Use `--negative-prompt` API parameter instead.

### 3. Reference Images: Style, Not Story
A 9-panel reference showing story scenes will contaminate every page with all story elements. Focus on character design, objects, and settings instead.

### 4. Story Progression Awareness
Track when elements first appear (`story_elements` field) and compute negative prompts dynamically to prevent future elements appearing too early.

---

## File Locations

| Type | Path |
|------|------|
| Book JSON | `/public/books/{slug}.json` |
| Reference | `/public/books/references/{slug}_reference.png` |
| Cover | `/public/images/covers/{slug}.png` |
| Pages | `/public/books/images/{slug}_page{NN}.png` |

## Review URLs

| Mode | URL |
|------|-----|
| Read | `https://funbookies.com/reader.html?book={slug}` |
| Edit | `https://funbookies.com/reader.html?book={slug}&mode=edit` |
