# FunBookies Book Template Specification

## Book Structure Overview

A complete FunBookies book follows this page sequence:

```
┌─────────────────────────────────────────────────────────────────┐
│ FRONT MATTER                                                    │
├─────────────────────────────────────────────────────────────────┤
│ 1. Cover (front)           - Title, author, illustration       │
│ 2. Inside Front Cover      - Copyright & publisher info        │
│ 3. About FunBookies        - QR code, how to read together     │
│ 4. Reading Level Guide     - This book's level explanation     │
│ 5. Words to Know           - Vocabulary for this story         │
├─────────────────────────────────────────────────────────────────┤
│ STORY PAGES                                                     │
├─────────────────────────────────────────────────────────────────┤
│ 6-N. Story pages           - Main narrative (numbered 1, 2...) │
├─────────────────────────────────────────────────────────────────┤
│ BACK MATTER                                                     │
├─────────────────────────────────────────────────────────────────┤
│ N+1. Word Search           - Activity using story vocabulary   │
│ N+2. Inside Back Cover     - About the series, other books     │
│ N+3. Back Cover            - Summary, barcode, level badge     │
└─────────────────────────────────────────────────────────────────┘
```

## Page Format

Books use a **square page format** with an **80/20 split** between image and text areas.

```
+---------------------------+
|                           |
|                           |
|      IMAGE AREA           |
|        (80%)              |
|                           |
|                           |
+---------------------------+
|     TEXT AREA (20%)       |
+---------------------------+
```

## Image Dimensions

| Aspect | Dimensions | Notes |
|--------|------------|-------|
| **Page** | 1:1 (square) | Overall book page is square |
| **Image Area** | 5:4 ratio | Top 80% of page |
| **Ideal Image Size** | 1024 x 820 px | Fills 80% without cropping |
| **Alternative** | 1024 x 1024 px | Square (bottom cropped) |

### Image Generation Settings

```bash
# Ideal 5:4 aspect (fills 80% exactly)
--width 1024 --height 820

# Square fallback (cropped at bottom)
--width 1024 --height 1024
```

---

## Page Types

### 1. Cover (`cover`)
Front cover with title and main illustration.

```json
{
  "page": 1,
  "type": "cover",
  "image": "images/cover.png",
  "text": "Book Title",
  "image_prompt": "Children's book cover: [description]. Warm watercolor style."
}
```

### 2. Copyright Page (`copyright`)
Inside front cover with publishing information.

```json
{
  "page": 2,
  "type": "copyright",
  "text": ""
}
```

**Standard copyright text (auto-generated):**
```
FunBookies™

Text copyright © 2025 FunBookies LLC
Illustrations copyright © 2025 FunBookies LLC
All rights reserved.

Published by FunBookies
funbookies.com

No part of this publication may be reproduced, stored in
a retrieval system, or transmitted in any form or by any
means without the prior written permission of the publisher.

First Edition, 2025
Printed in the United States

ISBN: 000-0-00000-000-0
```

### 3. About FunBookies / Parent Guide (`parent_guide`)
QR code linking to digital activities + tips for reading together.

```json
{
  "page": 3,
  "type": "parent_guide",
  "text": "Scan to unlock activities!"
}
```

**Content includes:**
- QR code to funbookies.com/book/{slug}
- "How to Read Together" tips
- Brief intro to decodable reading

**Tips for Reading Together:**
1. **Point to each word** as you read
2. **Let your child try first** - give them time to decode
3. **Sound it out together** when they get stuck
4. **Celebrate effort** not just accuracy
5. **Re-read for fluency** - repetition builds confidence

### 4. Reading Level Guide (`level_info`)
Explains what skills this book practices.

```json
{
  "page": 4,
  "type": "level_info",
  "text": ""
}
```

**Auto-generated based on book level:**
- Level name and color badge
- Skills being practiced
- What child should know before reading
- What they'll learn

### 5. Words to Know (`wordlist`)
Vocabulary page with words grouped by type.

```json
{
  "page": 5,
  "type": "wordlist",
  "text": "Words to Know"
}
```

**Word list rules by level:**

| Level | Sound-Out Words | Sight Words | New Words |
|-------|-----------------|-------------|-----------|
| 0-2 (Pink-Orange) | All phonetic words | All sight words | All new |
| 3-4 (Orange-Red) | New patterns only | New sight words only | All new |
| 5+ (Purple+) | Focus patterns only | Challenging only | All new |

For higher levels, omit common sight words like: *a, the, is, to, and, I, in, it, of, on, he, she, we, they, was, for, you, are, his, her, with, as, at, be, have, from, or, an, by*

### 6-N. Story Pages (`story`)
Main narrative pages with illustrations and text.

```json
{
  "page": 6,
  "story_page": 1,
  "type": "story",
  "image": "images/page_01.png",
  "text": "The cat sat on the mat.",
  "image_prompt": "A fluffy orange cat sitting on a colorful mat. Warm watercolor style."
}
```

Note: `story_page` is the reader-facing page number (starts at 1).

### N+1. Word Search (`wordsearch`)
Activity page reinforcing vocabulary.

```json
{
  "page": 22,
  "type": "wordsearch",
  "text": "Find the Words!",
  "words": ["cat", "sat", "mat", "hat", "rat", "bat"]
}
```

**Word search rules:**
- Use 6-10 key words from the story
- Grid size: 8x8 for levels 0-3, 10x10 for levels 4+
- Words can go horizontal and vertical (no diagonal for early levels)
- Include word bank below grid

### N+2. Inside Back Cover (`series_info`)
Information about the FunBookies series.

```json
{
  "page": 23,
  "type": "series_info",
  "text": ""
}
```

**Content:**
- "About FunBookies" blurb
- Reading level progression chart
- "Collect them all!" with other book thumbnails
- Website/app info

### N+3. Back Cover (`back_cover`)
Marketing and identification.

```json
{
  "page": 24,
  "type": "back_cover",
  "image": "images/back_cover.png",
  "text": "A delightful story about...",
  "image_prompt": "Simple illustration of main character waving. Warm watercolor style."
}
```

**Back cover elements:**
- Book summary (1-2 sentences)
- Reading level badge
- Age recommendation
- Barcode/ISBN area
- FunBookies logo
- Small character illustration

---

## Book JSON Structure

```json
{
  "title": "Book Title",
  "slug": "book_slug",
  "level": 3,
  "color": "Orange",
  "skill": "CVC + Digraphs",
  "skill_description": "Consonant-vowel-consonant words with digraphs like 'sh', 'ch', 'th'",
  "age_range": "4-6",
  "created": "2025-01-05",
  "model": "wan2.6-t2i",
  "author": "FunBookies",
  "illustrator": "AI Generated",

  "word_list": {
    "sound_out": ["cat", "sat", "mat"],
    "sight": ["the", "on"],
    "new": ["castle"]
  },

  "wordsearch_words": ["cat", "sat", "mat", "hat", "rat", "bat"],

  "summary": "A fun story about a cat who finds the perfect spot to nap.",

  "pages": [
    { "page": 1, "type": "cover", ... },
    { "page": 2, "type": "copyright" },
    { "page": 3, "type": "parent_guide" },
    { "page": 4, "type": "level_info" },
    { "page": 5, "type": "wordlist" },
    { "page": 6, "story_page": 1, "type": "story", ... },
    { "page": 7, "story_page": 2, "type": "story", ... },
    ...
    { "page": 21, "story_page": 16, "type": "story", ... },
    { "page": 22, "type": "wordsearch" },
    { "page": 23, "type": "series_info" },
    { "page": 24, "type": "back_cover", ... }
  ]
}
```

---

## Reading Levels

| Level | Color | Skill Focus | Prerequisite |
|-------|-------|-------------|--------------|
| 0 | Pink | Pre-reader | Letter recognition |
| 1 | Yellow | Short vowels (a, i) | Letter sounds |
| 2 | Orange | CVC words | Short vowels |
| 3 | Orange | CVC + Digraphs | CVC mastery |
| 4 | Red | Ending blends | Digraphs |
| 5 | Purple | Beginning blends | Ending blends |
| 6 | Blue | Silent e | Blends |
| 7 | Green | Vowel teams | Silent e |
| 8 | Gold | R-controlled vowels | Vowel teams |
| 9 | Silver | Advanced patterns | R-controlled |

---

## File Organization

```
/public/books/
├── book_slug.json              # Book data
├── images/                     # Shared images folder
│   └── covers/
│       └── book_slug.png
└── book_slug_images/           # Book-specific images
    ├── cover.png
    ├── page_01.png
    ├── page_02.png
    └── back_cover.png
```

---

## Image Prompt Guidelines

### Style Consistency
End all prompts with: **"Warm soft watercolor style."**

### Character Consistency
Create a character description and reference it:
```
Main character: "Rita, a small brown rat with a red bow"
Use in prompts: "Rita (small brown rat with red bow) looking excited..."
```

### Scene Guidelines
- Simple, uncluttered compositions
- Warm, inviting colors (soft oranges, greens, blues)
- Clear character expressions
- Child-appropriate content
- Consistent background style

### Example Prompts
```
Cover:
"Children's book cover: Two cute cartoon rats exploring a fairy tale castle. Warm watercolor style."

Story page:
"A small brown rat with a red bow discovering a jar of strawberry jam on a castle table. Warm soft watercolor style."

Back cover:
"Two cute cartoon rats waving goodbye, standing together happily. Simple composition, warm soft watercolor style."
```

---

## Format Progression by Level

As readers advance, book format evolves:

| Level Range | Format | Pages | Text/Image | Notes |
|-------------|--------|-------|------------|-------|
| 0-3 (Pink-Orange) | Picture book | 24 | 80/20 split | Large text, simple sentences |
| 4-6 (Red-Blue) | Early reader | 24-32 | 70/30 split | More text, 2-3 sentences/page |
| 7-8 (Green-Gold) | Transitional | 32-48 | 60/40 split | Paragraphs, smaller illustrations |
| 9+ (Silver+) | Chapter book | 48-64 | Text-heavy | Chapter breaks, spot illustrations |

### Early Levels (0-3)
- One sentence per page
- Large, clear font (24pt+)
- Full-page illustrations
- 80/20 image/text split
- Word search activity

### Mid Levels (4-6)
- 2-3 sentences per page
- Medium font (18-20pt)
- 70/30 image/text split
- May include simple comprehension questions
- Word search + vocabulary matching

### Advanced Levels (7-8)
- Short paragraphs
- Standard font (14-16pt)
- 60/40 or side-by-side layout
- Comprehension questions
- Writing prompts

### Chapter Books (9+)
- Multiple paragraphs per page
- Chapter divisions
- Spot illustrations (1-2 per chapter)
- Discussion questions
- Glossary

---

## Print Specifications (Future)

| Spec | Value |
|------|-------|
| Trim Size | 8" x 8" (square) |
| Page Count | 24 pages (multiple of 4) |
| Paper | 80# gloss text |
| Cover | 100# gloss cover, laminated |
| Binding | Saddle stitch |
| Color | Full color throughout |
| Bleed | 0.125" all sides |

---

## Sources

- [Kindlepreneur - Parts of a Book](https://kindlepreneur.com/parts-of-a-book/)
- [Reading Rockets - Decodable Books](https://www.readingrockets.org/topics/curriculum-and-instruction/articles/what-are-decodable-books-and-why-are-they-important)
- [Scholastic - Bob Books](https://www.scholastic.com/site/bob-books.html)
- [Kindlepreneur - Copyright Page Templates](https://kindlepreneur.com/book-copyright-page-examples-ebook/)
- [Karen Cioffi - Children's Books Back Matter](https://karencioffiwritingforchildren.com/2018/09/23/childrens-books-and-back-matter/)
