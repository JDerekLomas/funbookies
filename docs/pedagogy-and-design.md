# Funbookies: Pedagogy & Design Guide

## 1. The Science of Reading

### Why Decodable Books?

Decodable books are specifically designed for beginning readers. They contain **only** the grapheme-phoneme correspondences (letter-sound relationships) that students have already learned. This allows learners to:

- Practice **decoding** (sounding out) rather than guessing from pictures
- Build **automaticity** - recognizing words quickly and effortlessly
- Make direct connections between letters and sounds
- Develop confidence through successful reading experiences

> "Children were more likely to apply their phonics knowledge, read more accurately, and needed less assistance when reading decodable books." — Mesmer (2005)

**Sources:** [Reading Rockets](https://www.readingrockets.org), [Reading Universe](https://readinguniverse.org)

---

## 2. Phonics Progression Sequence

Books should follow a **systematic phonics sequence** from simple to complex:

### Level 1: CVC Words (Consonant-Vowel-Consonant)
- Short vowel sounds: a, e, i, o, u
- Examples: cat, hot, run, big, red
- **Our books should start here**

### Level 2: Consonant Blends
- Beginning blends: st-, tr-, bl-, cr-
- Ending blends: -nd, -nt, -mp, -st
- Examples: stop, trip, hand, jump

### Level 3: Digraphs
- Two letters, one sound: sh, ch, th, wh, ck
- Examples: ship, chat, this, duck

### Level 4: Long Vowels
- Magic E / Silent E: a_e, i_e, o_e, u_e
- Examples: cake, bike, home, cute

### Level 5: Vowel Teams
- Two vowels together: ea, oa, ee, ai, oo
- Examples: boat, rain, tree, moon

### Level 6: R-Controlled Vowels
- Vowels modified by r: ar, or, er, ir, ur
- Examples: car, for, her, bird

---

## 3. Word Types in Each Book

Each book should contain a controlled mix:

| Word Type | Description | Example |
|-----------|-------------|---------|
| **Decodable words** | Follow taught patterns | cat, hot, run |
| **Sight words** | High-frequency, often irregular | the, said, was, to, I |
| **Story words** | Topic-specific, introduced with support | volcano, lava, crater |

### Sight Word Progression (Most Common First)
```
Level 1: the, a, I, to, is, it, in, and
Level 2: he, she, was, for, on, are, as, with
Level 3: his, her, they, said, have, from, but, not
```

---

## 4. Pixi Book Format

### Physical Specifications
- **Size:** 10 × 10 cm (4 × 4 inches)
- **Pages:** 24 pages
- **Weight:** ~20 grams
- **Binding:** Saddle-stitch (stapled)
- **Price point:** €0.99–€1.99

### Page Structure (24 pages)
```
Page 1:     Cover (title, main character, engaging image)
Page 2:     Title page or Word List
Pages 3-22: Story pages (10 spreads)
Page 23:    "The End" or final illustration
Page 24:    Back cover (about the series, word review)
```

### For Print-Ready PDFs
- **Bleed:** 3mm on all sides
- **Safe zone:** 5mm from trim edge for text
- **Final trim size:** 100 × 100 mm
- **File size with bleed:** 106 × 106 mm

---

## 5. Typography for Early Readers

### Font Size by Age
| Age Group | Font Size | Line Spacing |
|-----------|-----------|--------------|
| Ages 3-5 (Pre-K) | 24pt+ | Double-spaced |
| Ages 5-7 (K-1st) | 18-22pt | 1.5-2x spacing |
| Ages 7-9 (2nd-3rd) | 14-16pt | 1.3-1.5x spacing |

### Font Selection Criteria
- **Large x-height** (lowercase letters are tall relative to capitals)
- **Single-story 'a' and 'g'** (infant letterforms children learn to write)
- **Clear, open counters** (spaces inside letters like 'o', 'e', 'd')
- **Medium weight** (not too thin, not too bold)
- **Good letter spacing**

### Recommended Fonts
- **Serif:** Bembo Infant, Plantin Infant, Sassoon Primary
- **Sans-serif:** Gill Sans Infant, Century Gothic, Andika
- **Free options:** Lexie Readable, OpenDyslexic, Andika

### Avoid
- Decorative or script fonts
- Condensed or expanded typefaces
- Very thin or very bold weights
- Fonts with ambiguous letters (l/I/1, O/0)

---

## 6. Page Layout Principles

### Text Placement
- **30 words per page maximum** (ideally 10-20 for early readers)
- **One sentence per line** when possible
- **Consistent text position** (bottom third of page recommended)
- **White space** around text for readability

### Image-Text Relationship
```
Option A: Separation
┌─────────┬─────────┐
│         │         │
│  IMAGE  │  TEXT   │
│         │         │
└─────────┴─────────┘

Option B: Text overlay (with solid background)
┌─────────────────────┐
│                     │
│       IMAGE         │
│   ┌───────────┐     │
│   │   TEXT    │     │
│   └───────────┘     │
└─────────────────────┘

Option C: Full bleed with text area
┌─────────────────────┐
│ █████████████████ │ ← Image (70%)
│ █████████████████ │
│                     │
│ Text goes here.     │ ← Text area (30%)
└─────────────────────┘
```

### Visual Variety
- Mix full-spread illustrations with simpler layouts
- Use **spot illustrations** for less dramatic moments
- Save **full spreads** for emotional peaks of the story
- Vary text placement to create rhythm

---

## 7. Book Template Structure

### Front Matter (Pages 1-2)
```json
{
  "page": 1,
  "type": "cover",
  "elements": ["title", "character_image", "series_logo"]
}
{
  "page": 2,
  "type": "wordlist",
  "sections": {
    "sound_out": ["CVC words from this book"],
    "sight": ["sight words used"],
    "new": ["story-specific vocabulary"]
  }
}
```

### Story Pages (Pages 3-22)
```json
{
  "page": 3,
  "type": "story",
  "text": "One short sentence.",
  "text_position": "bottom",
  "image_prompt": "Scene description matching text"
}
```

### Story Arc for 10 Spreads
1. **Introduction** - Meet character, establish setting
2. **Situation** - What does character want/notice?
3. **Action** - Character does something
4. **Discovery** - Something interesting happens
5. **Rising tension** - Things get exciting/challenging
6. **Peak moment** - Most dramatic point
7. **Response** - Character reacts
8. **Resolution begins** - Working toward solution
9. **Resolution** - Problem solved
10. **Ending** - Emotional conclusion, lesson learned

### Back Matter (Pages 23-24)
```json
{
  "page": 23,
  "type": "end",
  "text": "The End",
  "image": "Happy/resolved character image"
}
{
  "page": 24,
  "type": "back_cover",
  "elements": ["series_info", "reading_level", "word_count"]
}
```

---

## 8. Funbookies Design System

### Color Palette
- **Primary:** Bright, saturated colors (children respond to vivid colors)
- **Backgrounds:** Solid colors or simple gradients (not busy patterns)
- **Text backgrounds:** Opaque white or cream for readability

### Illustration Style
- Bold black outlines
- Flat colors (not realistic shading)
- Large, expressive eyes on characters
- Simple, uncluttered compositions
- Child-friendly, warm aesthetic

### Character Consistency Checklist
- [ ] Same color (exact hex/description)
- [ ] Same body proportions
- [ ] Same facial features (eye size, expression style)
- [ ] Same clothing/markings
- [ ] Consistent style (line weight, shading approach)

---

## 9. Image Generation Specifications

### Print Requirements
| Spec | Value |
|------|-------|
| Page trim size | 100 × 100mm |
| With bleed | 106 × 106mm |
| Print resolution | 300 DPI |
| Image area | 65% of page height |

### Image Dimensions
The image occupies the top 65% of the page:
- **Width:** 106mm (with bleed) = 1252px at 300 DPI
- **Height:** 68mm (65mm + 3mm top bleed) = 803px at 300 DPI
- **Aspect ratio:** ~3:2 landscape

### Generation Settings
```
Model: Wan2.6 T2I (via MuleRouter)
Size: 1536 × 1024 pixels (3:2 landscape)
Output: PNG, RGB
```

This provides:
- Slightly more resolution than minimum (allows for adjustments)
- Correct aspect ratio (no cropping needed)
- Print-ready at 300 DPI after minor scaling

### Cover Page Images
Cover pages use 70% image area:
- Height: 73mm (70mm + 3mm bleed) = 862px
- Same width: 1252px
- Aspect ratio: ~1.45:1 (slightly less wide)

For simplicity, use the same 1536×1024 generation and crop/position as needed.

---

## 10. Quality Checklist for Each Book

### Pedagogy
- [ ] All decodable words match taught phonics patterns
- [ ] Sight words are high-frequency and appropriate
- [ ] New vocabulary is introduced with picture support
- [ ] Text is predictable but not repetitive
- [ ] Story supports comprehension, not just decoding

### Design
- [ ] Font size 18pt+ for target age
- [ ] Text has adequate spacing and contrast
- [ ] Images clearly illustrate the text
- [ ] Character is consistent across all pages
- [ ] Layout has visual variety

### Print-Ready
- [ ] 3mm bleed on all sides
- [ ] Text within safe zone (5mm from edge)
- [ ] Images are 300 DPI minimum
- [ ] Colors in CMYK (not RGB)
- [ ] File format: PDF/X-1a or PDF/X-4

---

## 11. References

### Pedagogy
- [Reading Rockets: What Are Decodable Books?](https://www.readingrockets.org/topics/curriculum-and-instruction/articles/what-are-decodable-books-and-why-are-they-important)
- [Reading Universe: Decodable Texts](https://readinguniverse.org/article/explore-teaching-topics/word-recognition/phonics/decodable-texts-for-each-phonics-skill)
- [Structured Literacy: Decodable vs Leveled Readers](https://www.structuredliteracy.com/decodable-readers-vs-leveled-readers-why-are-decodable-readers-the-best-for-reading-instruction/)

### Design
- [SHMH: 70 Years of Pixi Books](https://www.shmh.de/ausstellungen/en-pixi/)
- [Fonts.com: Typography for Children](https://www.myfonts.com/pages/fontscom-learning-fyti-situational-typography-typography-for-children)
- [TypeEd: Typography of Children's Books](https://type-ed.com/resources/rag-right/2016/10/03/typography-childrens-books)
- [Blurb: Children's Book Template Tips](https://www.blurb.com/blog/childrens-book-template-layout-design-tips/)
- [Book Design Made Simple: Picture Book Design](https://www.bookdesignmadesimple.com/design-a-childrens-picture-book/)
