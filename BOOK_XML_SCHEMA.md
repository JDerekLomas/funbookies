# Book XML Schema

The XML format is the single source of truth for book creation. It's generated from a concept using AI, then edited and refined through the workflow.

## Level Specifications

Level specs are defined in `/public/data/level-specs.json`. The XML references these constraints.

### Band Overview

| Band | Levels | Focus | Sight Words | Lexile |
|------|--------|-------|-------------|--------|
| **A** | A0-A4 | Pre-reading, letter mastery | 0-9 | BR |
| **B** | B1-B9 | Phonics foundation, decoding | 9-37 | BR-200L |
| **C** | C1-C8 | Word study, morphology | 37-56 | 200L-450L |
| **D** | D1-D6 | Fluency, comprehension | unlimited | 450L-800L |

### Key Constraints by Level

Each level in `level-specs.json` defines:
- `wordsPerPage` / `wordsPerSentence` - Text length limits
- `phonicsPatterns` - Allowed patterns (e.g., CVC, CVCe, digraphs)
- `sightWords` / `sightWordsCumulative` - High-frequency words allowed
- `decodability` - Percentage of words that must be decodable
- `pages` - Expected page count
- `fluencyTarget` - Target words per minute
- `storyGuidance` - Narrative suggestions

### Example: B3 Constraints

```json
{
  "wordsPerSentence": "5-6",
  "phonicsPatterns": ["-nd: and, hand", "-mp: jump, bump", "-st: best, fast", "FLOSS: ff, ll, ss, zz"],
  "sightWordsCumulative": 19,
  "pages": "14",
  "decodability": "85%+",
  "storyGuidance": "Action stories: jump, stomp, bump. Suspense: 'What was that?'"
}
```

## Full Schema

```xml
<?xml version="1.0" encoding="UTF-8"?>
<book>
  <!-- METADATA -->
  <metadata>
    <title>The Lighthouse Keeper</title>
    <slug>d1-the-lighthouse-keeper</slug>
    <band>D</band>
    <level>D1</level>
    <author>FunBookies</author>
  </metadata>

  <!-- LEVEL CONSTRAINTS (from level-specs.json, included for reference) -->
  <level_constraints>
    <words_per_sentence min="14" max="18" />
    <total_pages min="26" max="30" />
    <decodability>N/A for D-band</decodability>
    <fluency_target>105-115 wpm with expression</fluency_target>
    <sight_words>All previous levels</sight_words>
    <phonics_patterns>
      All patterns mastered. Focus on sentence variety and dialogue.
    </phonics_patterns>
    <story_guidance>
      Character-driven with rich dialogue. Multiple speakers distinguished by voice.
      Compound and complex sentences. Dialogue with varied tags.
    </story_guidance>
  </level_constraints>

  <!-- TARGET PHONICS/VOCABULARY -->
  <targets>
    <phonics_focus>Compound-complex sentences, dialogue punctuation</phonics_focus>
    <target_words>lighthouse, keeper, generations, responsibility, beacon</target_words>
    <sight_words_used>there, where, through, thought, would, could</sight_words_used>
  </targets>

  <!-- STORY BIBLE - Characters, setting, themes -->
  <story_bible>
    <premise>A girl learns responsibility by helping her grandmother maintain a lighthouse</premise>
    <setting>
      Coastal New England lighthouse, weathered white tower on rocky cliffs,
      grandmother's cottage nearby, late summer atmosphere
    </setting>
    <characters>
      <character name="Maya" role="protagonist">
        8-year-old girl, curious and determined, windblown brown hair,
        wears yellow raincoat and red boots
      </character>
      <character name="Grandma" role="mentor">
        Elderly woman, kind eyes, silver hair in bun, weathered hands,
        wears blue cardigan and practical clothing
      </character>
    </characters>
    <themes>
      <theme>Responsibility and growing up</theme>
      <theme>Family bonds across generations</theme>
      <theme>Preserving traditions</theme>
    </themes>
    <emotional_arc>
      Wonder → Concern → Determination → Pride → Connection
    </emotional_arc>
  </story_bible>

  <!-- AUTHOR NOTES - Internal guidance, not shown to readers -->
  <author_notes>
    <note type="phonics">Focus on long vowel patterns: lighthouse, keeper, beacon</note>
    <note type="pacing">Build tension in middle, resolution by page 18</note>
    <note type="style">Warm, nostalgic tone - think Studio Ghibli meets New England</note>
  </author_notes>

  <!-- REFERENCE IMAGE PROMPT - For 9-panel style sheet -->
  <reference_prompt>
9-PANEL REFERENCE SHEET for "The Lighthouse Keeper"

STYLE: Warm watercolor illustration with soft edges, muted coastal palette
(sage green, warm white, terracotta accents, ocean blue), friendly rounded
character shapes, gentle natural lighting, nostalgic storybook quality.

PANELS:
Panel 1 (top-left): Maya full body - 8-year-old girl, brown windblown hair,
yellow raincoat, red boots, curious expression, standing pose

Panel 2 (top-center): Maya expressions - happy, worried, determined, proud
(4 small head shots showing emotional range)

Panel 3 (top-right): Grandma full body - elderly woman, silver bun, kind eyes,
blue cardigan, weathered hands, warm smile

Panel 4 (middle-left): The lighthouse exterior - tall white tower, red roof,
on rocky cliff, ocean backdrop, late summer sky

Panel 5 (middle-center): Lighthouse interior - spiral staircase, brass fixtures,
warm wood panels, light streaming through windows

Panel 6 (middle-right): Grandma's cottage - cozy kitchen, checkered curtains,
wood stove, family photos on walls

Panel 7 (bottom-left): Props - lighthouse beacon/lamp, maintenance tools,
old logbook, brass telescope

Panel 8 (bottom-center): Coastal setting - rocky shore, crashing waves,
seabirds, wild grass, weathered dock

Panel 9 (bottom-right): Key moment - Maya and Grandma silhouetted against
sunset, lighthouse beam sweeping across sky

TECHNICAL: Pure visual reference only, NO TEXT anywhere in image.
  </reference_prompt>

  <!-- STORY PAGES -->
  <story>
    <!-- Front matter -->
    <page type="cover">
      <text>The Lighthouse Keeper</text>
      <image_prompt>
        Tall white lighthouse on rocky cliff at golden hour, young girl in
        yellow raincoat gazing up at it, ocean waves crashing below, warm
        nostalgic atmosphere. Style: soft watercolor, muted coastal palette.
        NO TEXT in image.
      </image_prompt>
    </page>

    <page type="copyright" />

    <page type="title">
      <text>The Lighthouse Keeper</text>
    </page>

    <!-- Story pages -->
    <page number="1">
      <text>Maya had always loved the old lighthouse.<br/>She visited it every summer.</text>
      <scene>Girl with windblown hair stands before tall white lighthouse, waves crashing on rocks below</scene>
      <image_prompt>
        8-year-old Maya in yellow raincoat standing on rocky path, looking up
        at tall white lighthouse, ocean waves crashing on rocks, late summer
        afternoon light. Wide shot establishing setting. Warm watercolor style,
        muted coastal palette. NO TEXT.
      </image_prompt>
      <shot_type>wide</shot_type>
    </page>

    <page number="2">
      <text>"That lighthouse has been in our family<br/>for three generations," Grandma said.</text>
      <scene>Elderly woman in rocking chair, gesturing while telling stories</scene>
      <image_prompt>
        Grandma with silver bun and blue cardigan sitting in wooden rocking
        chair, warm smile, gesturing with weathered hands as she tells a story,
        cozy cottage interior with family photos visible. Medium close shot.
        Warm watercolor style. NO TEXT.
      </image_prompt>
      <shot_type>medium</shot_type>
    </page>

    <!-- More pages... -->

    <!-- Back matter -->
    <page type="wordlist">
      <words>lighthouse, keeper, beacon, summer, grandmother, generations</words>
    </page>

    <page type="parent_guide">
      <text>Reading tips for parents...</text>
    </page>

    <page type="back_cover" />
  </story>
</book>
```

## Element Reference

### `<metadata>`
| Element | Required | Description |
|---------|----------|-------------|
| `title` | Yes | Book title |
| `slug` | Yes | URL-safe identifier (auto-generated from title) |
| `band` | Yes | Reading band: A, B, C, D |
| `level` | Yes | Specific level: A1, B3, D1, etc. |
| `author` | No | Author name (default: FunBookies) |

### `<level_constraints>`
Auto-populated from `level-specs.json` based on selected level. Included in XML for reference.

| Element | Description |
|---------|-------------|
| `words_per_sentence` | Min/max words per sentence for this level |
| `total_pages` | Expected page count range |
| `decodability` | Percentage of words that must be decodable |
| `fluency_target` | Target reading speed (wpm) |
| `sight_words` | Cumulative sight words allowed |
| `phonics_patterns` | Phonics patterns introduced at this level |
| `story_guidance` | Narrative suggestions for this level |

### `<targets>`
| Element | Required | Description |
|---------|----------|-------------|
| `phonics_focus` | Yes | Primary phonics skill being practiced |
| `target_words` | Yes | Words featuring the target phonics pattern |
| `sight_words_used` | No | High-frequency words used in this book |

### `<story_bible>`
| Element | Required | Description |
|---------|----------|-------------|
| `premise` | Yes | One-sentence story summary |
| `setting` | Yes | Physical and temporal setting details |
| `characters` | Yes | Character descriptions with visual details |
| `themes` | No | Thematic elements |
| `emotional_arc` | No | Emotional journey through the story |

### `<character>`
| Attribute | Required | Description |
|-----------|----------|-------------|
| `name` | Yes | Character name |
| `role` | No | protagonist, mentor, antagonist, supporting |

### `<author_notes>`
Internal notes not shown to readers. `type` can be: phonics, pacing, style, visual, etc.

### `<reference_prompt>`
Full prompt for generating the 9-panel reference sheet. Should include:
- Style description
- 9 panel descriptions
- Technical requirements (NO TEXT)

### `<page>`
| Attribute | Values | Description |
|-----------|--------|-------------|
| `type` | cover, copyright, title, wordlist, parent_guide, back_cover | Special page types |
| `number` | 1, 2, 3... | Story page number (auto-assigned if omitted) |

### Page Children
| Element | Required | Description |
|---------|----------|-------------|
| `text` | Yes* | Page text with `<br/>` for line breaks |
| `scene` | No | Brief scene description (for reference) |
| `image_prompt` | No | Full prompt for image generation |
| `shot_type` | No | wide, medium, close, detail |
| `words` | For wordlist | Comma-separated word list |

*Not required for copyright, back_cover types

## Line Breaks and Formatting

Use `<br/>` for line breaks within text:
```xml
<text>Maya had always loved the old lighthouse.<br/>She visited it every summer.</text>
```

This renders as:
> Maya had always loved the old lighthouse.
> She visited it every summer.

## Generating from Concept

Input concept:
```
A story about a girl who helps her grandmother maintain a lighthouse.
Level: D1 (longer sentences, complex themes)
Style: Warm, nostalgic watercolor
```

AI generates complete XML using templates for:
1. Story structure appropriate for level
2. Reference prompt format
3. Image prompt format
4. Page count and pacing for band

## Converting to Book JSON

The XML is converted to the existing book JSON format for the reader:

```javascript
// XML → JSON conversion
{
  "id": "d1-the-lighthouse-keeper",
  "title": "The Lighthouse Keeper",
  "band": "D",
  "level": "D1",
  "reference_prompt": "...",
  "story_bible": { ... },
  "pages": [
    { "page": 1, "type": "cover", "text": "...", "image_prompt": "..." },
    ...
  ]
}
```

## Workflow States

```
concept.txt  →  draft.xml  →  reviewed.xml  →  book.json  →  published
                    ↑              ↑
                    └──── edit ────┘
```

Each state is saved, allowing rollback and iteration.
