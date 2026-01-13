# Book Story Skill

Generate decodable story text for a FunBookies reader with proper phonics level, page structure, and word lists.

## When to Use

Use this skill when the user wants to:
- Create a new book from a concept/idea
- Generate decodable text at a specific reading level
- Structure a story into pages with appropriate text density

## Usage

```
/book-story "<concept>" --level <level> [--setting "<cultural context>"]
```

Examples:
- `/book-story "A girl daydreams about being a tractor" --level B2 --setting "rural Estonia"`
- `/book-story "A frog helps a crab stuck in a stump" --level B4`
- `/book-story "A knight searches for a magical knife" --level C1`

## How It Works

### 1. Determine Phonics Constraints

Read `/public/books/README.md` and `PHONICS_ROADMAP.md` to understand the target level:

| Level | Phonics Focus | Example Words |
|-------|--------------|---------------|
| A0-A2 | Pre-reading, CVC intro | look, I, sit, sat |
| B1-B2 | CVC all short vowels | cat, sit, hot, mud, bed |
| B3-B5 | Blends, digraphs | frog, ship, much |
| B6-B9 | Silent e, vowel teams | cake, rain, boat |
| C1-C8 | Multisyllable, affixes | kitten, jumping |
| D1-D6 | Fluent connected text | complex sentences |

### 2. Identify Heart Words

For high-interest concepts, identify 2-3 "heart words" - words that are phonetically advanced but highly motivating:

```
Concept: "daydreams about tractors and airplanes"
Heart words: tractor, airplane (taught as sight words despite being above level)
```

### 3. Generate Story Text

Write the story following these rules:

**Text Density by Level:**
- A0-A2: 1-4 words per page
- B1-B3: 1-2 short sentences per page
- B4-B6: 2-3 sentences per page
- B7-C4: 3-4 sentences per page
- C5-D6: Paragraphs

**Decodability Target:**
- 85-95% of words should be decodable at the target level
- Remaining words are sight words or heart words

**Story Structure:**
- Clear beginning, middle, end
- 8-14 story pages typical for B-level
- Each page should have a distinct visual moment

### 4. Output Format

Generate a book JSON with this structure:

```json
{
  "id": "b2-if-i-could-only-be-a-red-tractor",
  "title": "If I Could Only Be a Red Tractor",
  "slug": "if-i-could-only-be-a-red-tractor",
  "level": "B2",
  "band": "B",
  "targetPhonics": "CVC short o, u, e",
  "wordFamilies": ["-ot", "-op", "-un", "-up", "-ud"],
  "skill": "CVC Short o, u, e (All 5 short vowels)",
  "skill_description": "Practice reading CVC words with all five short vowels.",
  "age_range": "K-1",
  "created": "2026-01-13",
  "author": "FunBookies",
  "illustrator": "AI Generated",
  "summary": "A blonde girl daydreams about being a red tractor and an airplane.",

  "characters": {
    "main": "Character description for image prompts"
  },
  "setting_context": "Cultural/geographic context for images",

  "word_list": {
    "sound_out": ["sits", "hot", "sun", "mud", "big", "log"],
    "sight": ["a", "I", "the", "is", "in", "she", "her"],
    "heart": ["tractor", "airplane"]
  },

  "story_elements": {
    "airplane": 5,
    "farmhouse": 9
  },

  "pages": [
    {
      "page": 1,
      "type": "cover",
      "text": "Book Title"
    },
    {
      "page": 2,
      "type": "copyright"
    },
    {
      "page": 3,
      "type": "parent_guide"
    },
    {
      "page": 4,
      "type": "level_info"
    },
    {
      "page": 5,
      "type": "wordlist",
      "text": "Words to Know"
    },
    {
      "page": 6,
      "story_page": 1,
      "type": "story",
      "text": "Story text here.\nSecond line if needed."
    }
  ],

  "wordsearch_words": ["word1", "word2"],

  "parent_tips": {
    "before_reading": "...",
    "during_reading": "...",
    "after_reading": "..."
  },

  "comprehension_questions": [
    {"question": "...", "answer": "..."}
  ]
}
```

### 5. Save Location

Save the JSON to: `/public/books/{slug}.json`

### 6. Checkpoint

After generating, show the user:
1. The full story text with page breaks marked
2. Word list breakdown (sound-out, sight, heart)
3. Decodability estimate
4. Ask: "Does this look right? Ready to generate scene descriptions?"

## Key Rules

### DO:
- Match phonics level strictly for sound-out words
- Use repetition and patterns (kids love "Rum, rum, rum!")
- Create distinct visual moments for each page
- Include onomatopoeia where appropriate
- Use line breaks (`\n`) for natural reading pauses

### DON'T:
- Use words above the phonics level (except heart words)
- Write more than 2-3 heart words per book
- Create pages without clear visual content
- Use complex sentence structures at low levels

## The Craft: Write It, Don't Describe It

**The most important rule:** Write *a* children's story, not *about* a children's story.

Generic template-filling produces flat text:
```
I see a girl.
She wishes.
"I wish I were a tractor!"
She dreams and dreams.
```

Actually inhabiting the story produces this:
```
Tiia sits in the hot sun.
A red tractor digs in the mud.

"If I could only be a red tractor!"
Tiia shuts her eyes.

RUM, RUM, RUM!
She tugs a big log.

She is strong! She is loud!
Mud on her legs. Mud on her belly.
```

### What Makes the Difference

| Flat | Alive |
|------|-------|
| "a girl" | "Tiia sits in the hot sun" (name, action, sensory detail) |
| "She wishes" | "If I could only be" (longing lives in "only") |
| "She dreams" | "RUM, RUM, RUM! She tugs a big log." (the dream has ACTION) |
| Abstract concept | Sensory details ("Mud on her legs. Mud on her belly.") |
| "The end" | "But part of her? Still up in the clouds." (emotionally true) |

### Techniques That Work

1. **Onomatopoeia** - "RUM, RUM, RUM!" and "ZIP!" Kids love sounds.

2. **Rhythm and repetition** - "She tips left. She dips right." Singsong patterns.

3. **Sensory specificity** - Not "she got muddy" but "Mud on her legs. Mud on her belly."

4. **Action in fantasy** - The character DOES things in the daydream, not just imagines abstractly.

5. **Emotionally true endings** - "But part of her? Still up in the clouds." That's what daydreaming actually feels like.

6. **Let constraints help** - CVC words (sits, hot, mud, tugs, tips, dips, pop) have punch and texture. Don't fight the phonics level; let it shape the voice.

### The Test

Read it aloud. Does it have music? Would a child want to hear it again? Would YOU want to read it to a child?

If it feels like filling in blanks, start over.

## Example Output

For `/book-story "A girl daydreams about being a tractor" --level B2 --setting "rural Estonia"`:

```
Story Pages:

Page 1: Tiia sits in the hot sun.
        A red tractor digs in the mud.

Page 2: "If I could only be a red tractor!"
        Tiia shuts her eyes.

Page 3: RUM, RUM, RUM!
        She tugs a big log.

...

Word Analysis:
- Sound-out (B2): sits, hot, sun, digs, mud, shuts, rum, tugs, big, log...
- Sight words: a, I, the, in, she, her, if, could, only, be...
- Heart words: tractor, airplane
- Estimated decodability: 87%
```
