# Kalulu Reading Program Analysis

Analysis of Stanislas Dehaene's Kalulu reading program for potential alignment with FunBookies.

## Overview

**Kalulu** is a research-backed reading instruction app developed by the Excello lab (associated with Stanislas Dehaene's cognitive neuroscience research). It teaches reading through systematic phonics using a decoding-based method.

**Key Research Papers:**
- https://www.tandfonline.com/doi/pdf/10.1080/00220973.2023.2173129
- https://hal.science/hal-03015914/document
- https://hal.science/hal-03702075/document

## Architecture

### Data Storage
- **SQLite Database**: Per-language curriculum stored in `language.db`
- **Language Packs**: Downloaded from AWS API Gateway per locale (French, Spanish, Portuguese)
- **User Progress**: Local storage with cloud sync for teachers/parents

### Database Schema

```sql
-- Grapheme-Phoneme Correspondences (GPCs)
CREATE TABLE "GPs" (
    "ID" INTEGER PRIMARY KEY,
    "Grapheme" TEXT NOT NULL,      -- e.g., "ch", "ou", "a"
    "Phoneme" TEXT NOT NULL,       -- IPA representation
    "Type" INTEGER DEFAULT 0,       -- vowel/consonant/digraph
    "Exception" INTEGER DEFAULT 0   -- irregular patterns
);

-- Lessons (ordered sequence)
CREATE TABLE "Lessons" (
    "ID" INTEGER PRIMARY KEY,
    "LessonNb" INTEGER NOT NULL    -- 1, 2, 3, etc.
);

-- Which GPCs are introduced in which lesson
CREATE TABLE "GPsInLessons" (
    "GPID" INTEGER NOT NULL,
    "LessonID" INTEGER NOT NULL,
    FOREIGN KEY("LessonID") REFERENCES "Lessons"("ID"),
    FOREIGN KEY("GPID") REFERENCES "GPs"("ID")
);

-- Words used in lessons
CREATE TABLE "Words" (
    "ID" INTEGER PRIMARY KEY,
    "Word" TEXT NOT NULL,
    "LessonNb" INTEGER NOT NULL
);

-- Syllables (intermediate decoding unit)
CREATE TABLE "Syllables" (
    "ID" INTEGER PRIMARY KEY,
    "Grapheme" TEXT NOT NULL,
    "Phoneme" TEXT NOT NULL,
    "LessonNb" INTEGER NOT NULL
);

-- Sentences for fluency practice
CREATE TABLE "Sentences" (
    "ID" INTEGER PRIMARY KEY,
    "Sentence" TEXT NOT NULL,
    "LessonNb" INTEGER NOT NULL
);

-- Exercise types per lesson
CREATE TABLE "ExerciseTypes" (
    "ID" INTEGER PRIMARY KEY,
    "Type" TEXT NOT NULL           -- Syllable, Pairing, Words, Sentences, Boss
);
```

## Lesson Structure

Each lesson follows this sequence:

1. **Look and Learn** (Video/Introduction)
   - New GPC is introduced
   - Visual demonstration of letter-sound correspondence
   - Must complete before games unlock

2. **Three Minigames** (unlock after Look and Learn)
   - Game 1: Syllable decoding (hear phoneme, find grapheme)
   - Game 2: Word building (assemble GPCs into words)
   - Game 3: Lexical decision (identify real words)

3. **Boss Level** (after completing all three games)
   - Sentence-level practice
   - Combines all learned GPCs

## Minigame Types

### 1. Syllable Games (Hear and Find)
**Examples**: Jellyfish, Crabs, Parakeets, Monkeys

**Mechanics**:
- Audio plays syllable/phoneme
- Student finds matching grapheme on screen
- Adaptive difficulty:
  - Level 1: All distractors have different letters
  - Level 2-3: Single letter change distractors (e.g., "cha" vs "la")
  - Level 4-5: Inverted distractors (e.g., "il" vs "li")

### 2. Word Games (Build the Word)
**Examples**: Turtles, Ants, Penguin

**Mechanics**:
- Audio plays word
- Student selects GPCs in correct order to build word
- Progressive: GPC by GPC within each word
- Max 6 GPCs per word

### 3. Fish Game (Lexical Decision)
**Mechanics**:
- Words and pseudowords appear
- Student identifies real words vs pseudowords
- Tests whole-word recognition

## Adaptive Learning System

### Difficulty Progression
```gdscript
# 5 difficulty levels per minigame
var difficulty_settings: Array[DifficultySettings] = [
    DifficultySettings.new(.75, 200., 4.),   # Easy: 75% stimuli, slow, long spawn
    DifficultySettings.new(.66, 250., 3.5),
    DifficultySettings.new(.33, 300., 3.),
    DifficultySettings.new(.25, 333., 2.5),
    DifficultySettings.new(.25, 366., 2.)    # Hard: 25% stimuli, fast, quick spawn
]
```

### Remediation Engine
- Tracks error scores per GP, syllable, and word
- Items with more errors get prioritized in future sessions
- Spaced repetition based on performance

```gdscript
# Score tracking
var remediation_gp_scores: Dictionary = {}
var remediation_syllables_scores: Dictionary = {}
var remediation_words_scores: Dictionary = {}

# Negative score = more errors, gets prioritized
func _update_remediation_gp_score(id: int, score: int):
    # +1 for correct, -1 for incorrect
```

### Confusion Matrix
- Tracks which GPCs get confused with each other
- Used to generate better distractors

```gdscript
var confusion_matrix_gp_scores: Dictionary[int, PackedInt32Array] = {}
# Key: expected GP ID, Value: array of selected GP IDs (including errors)
```

## Stimuli Selection Algorithm

```gdscript
func _find_stimuli_and_distractions():
    # 1. Get all words/syllables up to current lesson
    var words_list = Database.get_words_for_lesson(lesson_nb, false)

    # 2. Split into current lesson vs previous lessons
    var current_lesson_words = []
    var previous_lesson_words = []

    # 3. Shuffle and sort by remediation score (struggling items first)
    current_lesson_words.sort_custom(_sort_scoring)

    # 4. Fill stimuli:
    #    - 70% from current lesson
    #    - 30% from previous lessons (review)

    # 5. Find distractors for each stimulus
    for stimulus in stimuli:
        distractions.append(Database.get_distractors_for_grapheme(gp.ID))
```

## Progression Rules

1. **Sequential Unlock**: Must complete lesson N before accessing lesson N+1
2. **Within-Lesson Order**: Look and Learn → Games 1-3 (any order) → Boss
3. **Completion Tracking**:
   - Status: Locked → Unlocked → Completed
   - Duration tracking per game for analytics

```gdscript
func game_completed(lesson_number: int, game_number: int) -> bool:
    unlocks[lesson_number]["games"][game_number] = Status.Completed

    # Check if all games complete
    var all_completed = true
    for index in range(3):
        all_completed = all_completed and unlocks[lesson_number]["games"][index] == Status.Completed

    # Unlock next lesson
    if all_completed and unlocks.has(lesson_number + 1):
        unlocks[lesson_number + 1]["look_and_learn"] = Status.Unlocked
```

## GPC Ordering (French - from Manulex corpus)

Based on frequency in children's literature (most common first):

| Order | Grapheme | Type |
|-------|----------|------|
| 1 | a | vowel |
| 2 | i | vowel |
| 3 | o | vowel |
| 4 | u | vowel |
| 5 | e | vowel |
| 6 | l | consonant |
| 7 | r | consonant |
| 8 | s | consonant |
| ... | ... | ... |
| Later | ch | digraph |
| Later | ou | vowel team |
| Later | an/en | nasal |

## Key Insights for FunBookies

### 1. Lesson-Based Progression
Currently FunBookies has activities with band levels (A1-C6) but no formal lesson structure.

**Recommendation**: Create explicit lessons that group:
- Target GPC introduction
- 2-3 practice activities
- Review/assessment

### 2. Adaptive Difficulty
Kalulu adjusts:
- Speed of gameplay
- Ratio of new vs review items
- Distractor difficulty

**Recommendation**: Add difficulty parameters to activities based on:
- Time limits
- Number of distractors
- Similarity of distractors to target

### 3. Remediation/Spaced Repetition
Kalulu tracks errors and prioritizes struggling items.

**Recommendation**: Store error history per GPC/word and:
- Surface struggling items more frequently
- Track confusion patterns (e.g., b/d confusion)

### 4. Curriculum Database
Kalulu uses SQLite for curriculum data separate from code.

**Recommendation**: Consider a curriculum data structure:
```json
{
  "lessons": [
    {
      "id": 1,
      "gpcs": ["a", "m", "t"],
      "words": ["am", "mat", "at"],
      "activities": ["letter-drill", "word-builder", "read-aloud"]
    }
  ]
}
```

### 5. Exercise Type Variety
Kalulu has distinct game types:
- Hear → Find (auditory discrimination)
- Build → Word (blending)
- Real → Fake (lexical decision)

**FunBookies Mapping**:
| Kalulu Type | FunBookies Equivalent |
|-------------|----------------------|
| Syllable games | say-the-sound, sound-boxes |
| Word games | word-builder, blend-it |
| Lexical decision | sight-words |
| Sentences | sentence-scramble, read-aloud |

### 6. Audio-First Design
Every item in Kalulu plays audio before visual selection.

**Recommendation**: Ensure all FunBookies activities:
- Play target sound/word automatically
- Allow replay on demand
- Use consistent voice/pronunciation

## English GPC Ordering (Proposed)

Based on frequency and decodability research:

**Phase 1: Single Letters (Short Vowels + Common Consonants)**
1. s, a, t, p
2. i, n, m, d
3. g, o, c, k
4. e, u, r, h
5. b, f, l, j
6. v, w, x, y, z, q

**Phase 2: Consonant Digraphs**
7. sh, ch, th, wh
8. ck, ng, qu

**Phase 3: Long Vowels (CVCe)**
9. a_e, i_e, o_e, u_e, e_e

**Phase 4: Vowel Teams**
10. ai, ay, ee, ea
11. oa, ow, oo, ou
12. oi, oy, au, aw

**Phase 5: R-Controlled Vowels**
13. ar, er, ir, or, ur

**Phase 6: Complex Patterns**
14. igh, ough, eigh
15. tion, sion

## Next Steps

1. **Map FunBookies activities to Kalulu exercise types**
2. **Create lesson structure for existing content**
3. **Implement remediation scoring**
4. **Add confusion matrix tracking**
5. **Design curriculum progression data format**
