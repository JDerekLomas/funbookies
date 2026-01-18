# FunBookies Lesson Structure Specification

Based on Kalulu's research-backed approach, adapted for English phonics instruction.

## Overview

This specification defines how FunBookies should structure its curriculum into lessons with explicit progression, adaptive learning, and data tracking.

---

## Lesson Data Model

### Lesson Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "id": {
      "type": "integer",
      "description": "Unique lesson identifier, also represents sequence order"
    },
    "name": {
      "type": "string",
      "description": "Human-readable lesson name"
    },
    "phase": {
      "type": "integer",
      "description": "Curriculum phase (1-6, matching UK Letters and Sounds)"
    },
    "gpcs": {
      "type": "array",
      "description": "Grapheme-phoneme correspondences introduced in this lesson",
      "items": {
        "$ref": "#/$defs/gpc"
      }
    },
    "words": {
      "type": "array",
      "description": "Decodable words using GPCs from this and previous lessons",
      "items": {
        "$ref": "#/$defs/word"
      }
    },
    "sightWords": {
      "type": "array",
      "description": "High-frequency words that may not be fully decodable",
      "items": {
        "type": "string"
      }
    },
    "activities": {
      "type": "array",
      "description": "Activity sequence for this lesson",
      "items": {
        "$ref": "#/$defs/activity"
      }
    },
    "sentences": {
      "type": "array",
      "description": "Decodable sentences for fluency practice",
      "items": {
        "type": "string"
      }
    }
  }
}
```

### GPC Schema

```json
{
  "$defs": {
    "gpc": {
      "type": "object",
      "properties": {
        "id": {
          "type": "string",
          "description": "Unique identifier (grapheme-phoneme)"
        },
        "grapheme": {
          "type": "string",
          "description": "Written representation (e.g., 'sh', 'oa', 'a_e')"
        },
        "phoneme": {
          "type": "string",
          "description": "IPA representation of sound"
        },
        "type": {
          "type": "string",
          "enum": ["vowel", "consonant", "digraph", "trigraph", "vowel_team", "r_controlled", "split_vowel"],
          "description": "Category of GPC"
        },
        "keywords": {
          "type": "array",
          "items": { "type": "string" },
          "description": "Example words (e.g., ['ship', 'fish'] for 'sh')"
        },
        "audio": {
          "type": "string",
          "description": "Path to phoneme audio file"
        }
      }
    }
  }
}
```

### Word Schema

```json
{
  "$defs": {
    "word": {
      "type": "object",
      "properties": {
        "id": {
          "type": "integer",
          "description": "Unique word identifier"
        },
        "word": {
          "type": "string",
          "description": "The word itself"
        },
        "gpcs": {
          "type": "array",
          "items": { "type": "string" },
          "description": "Ordered list of GPC IDs that make up the word"
        },
        "syllables": {
          "type": "array",
          "items": { "type": "string" },
          "description": "Syllable breakdown"
        },
        "lessonIntroduced": {
          "type": "integer",
          "description": "Lesson ID where this word is first used"
        },
        "frequency": {
          "type": "integer",
          "description": "Word frequency rank (lower = more common)"
        },
        "audio": {
          "type": "string",
          "description": "Path to word audio file"
        }
      }
    }
  }
}
```

### Activity Schema

```json
{
  "$defs": {
    "activity": {
      "type": "object",
      "properties": {
        "type": {
          "type": "string",
          "enum": [
            "introduction",
            "letter-drill",
            "say-the-sound",
            "sound-boxes",
            "blend-it",
            "word-builder",
            "word-chains",
            "word-families",
            "sight-words",
            "read-aloud",
            "sentence-scramble"
          ]
        },
        "required": {
          "type": "boolean",
          "description": "Must complete to unlock next activities"
        },
        "config": {
          "type": "object",
          "description": "Activity-specific configuration"
        }
      }
    }
  }
}
```

---

## Example Lesson

```json
{
  "id": 1,
  "name": "Lesson 1: s, a, t, p",
  "phase": 1,
  "gpcs": [
    {
      "id": "s-/s/",
      "grapheme": "s",
      "phoneme": "/s/",
      "type": "consonant",
      "keywords": ["sun", "sit", "sad"],
      "audio": "/audio/phonemes/s.mp3"
    },
    {
      "id": "a-/æ/",
      "grapheme": "a",
      "phoneme": "/æ/",
      "type": "vowel",
      "keywords": ["apple", "ant", "at"],
      "audio": "/audio/phonemes/a-short.mp3"
    },
    {
      "id": "t-/t/",
      "grapheme": "t",
      "phoneme": "/t/",
      "type": "consonant",
      "keywords": ["tap", "top", "tin"],
      "audio": "/audio/phonemes/t.mp3"
    },
    {
      "id": "p-/p/",
      "grapheme": "p",
      "phoneme": "/p/",
      "type": "consonant",
      "keywords": ["pat", "pig", "pot"],
      "audio": "/audio/phonemes/p.mp3"
    }
  ],
  "words": [
    { "id": 1, "word": "at", "gpcs": ["a-/æ/", "t-/t/"], "lessonIntroduced": 1 },
    { "id": 2, "word": "sat", "gpcs": ["s-/s/", "a-/æ/", "t-/t/"], "lessonIntroduced": 1 },
    { "id": 3, "word": "pat", "gpcs": ["p-/p/", "a-/æ/", "t-/t/"], "lessonIntroduced": 1 },
    { "id": 4, "word": "tap", "gpcs": ["t-/t/", "a-/æ/", "p-/p/"], "lessonIntroduced": 1 },
    { "id": 5, "word": "sap", "gpcs": ["s-/s/", "a-/æ/", "p-/p/"], "lessonIntroduced": 1 }
  ],
  "sightWords": ["a", "the"],
  "activities": [
    {
      "type": "introduction",
      "required": true,
      "config": {
        "gpcs": ["s-/s/", "a-/æ/", "t-/t/", "p-/p/"],
        "videoUrl": "/videos/lesson-1-intro.mp4"
      }
    },
    {
      "type": "letter-drill",
      "required": true,
      "config": {
        "letters": ["s", "a", "t", "p"],
        "rounds": 10
      }
    },
    {
      "type": "say-the-sound",
      "required": true,
      "config": {
        "gpcs": ["s-/s/", "a-/æ/", "t-/t/", "p-/p/"],
        "rounds": 8
      }
    },
    {
      "type": "blend-it",
      "required": false,
      "config": {
        "words": ["at", "sat", "pat", "tap", "sap"],
        "rounds": 5
      }
    },
    {
      "type": "word-builder",
      "required": true,
      "config": {
        "words": ["sat", "pat", "tap"],
        "rounds": 3
      }
    }
  ],
  "sentences": [
    "Pat sat.",
    "A tap.",
    "Tap, tap, tap."
  ]
}
```

---

## Lesson Progression System

### Progression States

```javascript
const LessonStatus = {
  LOCKED: 'locked',      // Cannot access
  UNLOCKED: 'unlocked',  // Can access, not started
  IN_PROGRESS: 'in_progress',  // Started, not complete
  COMPLETED: 'completed' // All required activities done
};

const ActivityStatus = {
  LOCKED: 'locked',
  UNLOCKED: 'unlocked',
  COMPLETED: 'completed'
};
```

### Student Progress Schema

```json
{
  "studentId": "abc123",
  "lessons": {
    "1": {
      "status": "completed",
      "activities": {
        "introduction": "completed",
        "letter-drill": "completed",
        "say-the-sound": "completed",
        "blend-it": "completed",
        "word-builder": "completed"
      },
      "completedAt": "2024-01-15T10:30:00Z",
      "duration": 1245
    },
    "2": {
      "status": "in_progress",
      "activities": {
        "introduction": "completed",
        "letter-drill": "unlocked"
      }
    },
    "3": {
      "status": "locked"
    }
  }
}
```

### Unlock Rules

```javascript
function calculateActivityStatus(lesson, activityIndex, studentProgress) {
  const activity = lesson.activities[activityIndex];
  const lessonProgress = studentProgress.lessons[lesson.id];

  // First activity: unlocked if lesson is unlocked
  if (activityIndex === 0) {
    return lessonProgress.status !== 'locked' ? 'unlocked' : 'locked';
  }

  // Required activities must be completed in order
  const prevActivity = lesson.activities[activityIndex - 1];
  if (prevActivity.required) {
    const prevStatus = lessonProgress.activities[prevActivity.type];
    if (prevStatus !== 'completed') {
      return 'locked';
    }
  }

  return 'unlocked';
}

function calculateLessonStatus(lessonId, studentProgress) {
  // Lesson 1 always starts unlocked
  if (lessonId === 1) {
    return studentProgress.lessons[1]?.status || 'unlocked';
  }

  // Check if previous lesson is completed
  const prevLesson = studentProgress.lessons[lessonId - 1];
  if (!prevLesson || prevLesson.status !== 'completed') {
    return 'locked';
  }

  return studentProgress.lessons[lessonId]?.status || 'unlocked';
}
```

---

## Activity Mapping to Kalulu Patterns

| Kalulu Pattern | FunBookies Activity | Purpose |
|----------------|---------------------|---------|
| Hear & Find | `say-the-sound` | Phoneme discrimination |
| Hear & Find | `sound-boxes` | Phoneme segmentation |
| Word Building | `word-builder` | Blending GPCs → words |
| Word Building | `blend-it` | Oral blending practice |
| Word Building | `word-chains` | Minimal pair awareness |
| Lexical Decision | `sight-words` | Automatic word recognition |
| Sentences | `sentence-scramble` | Syntax + fluency |
| Sentences | `read-aloud` | Connected text fluency |
| Introduction | `letter-drill` | Letter-sound correspondence |

---

## Activity Requirements per Lesson

### Minimum Required Activities

Each lesson MUST include:

1. **Introduction** - Present new GPCs (video, animation, or interactive)
2. **Phoneme Practice** - `letter-drill` or `say-the-sound`
3. **Blending Practice** - `word-builder` or `blend-it`

### Recommended Activity Sequence

```
Introduction → Letter Drill → Say the Sound → Blend It → Word Builder → Read Aloud
     │              │              │             │            │            │
     ▼              ▼              ▼             ▼            ▼            ▼
  New GPCs     Letter→Sound   Hear→Select   Oral blend   Build words   Fluency
  introduced    practice       practice      practice     with GPCs     practice
```

### Activity Selection Logic

```javascript
function getActivitiesForLesson(lesson, studentData) {
  const activities = [];

  // 1. Always start with introduction (if not seen)
  if (!studentData.hasSeenIntro(lesson.id)) {
    activities.push({ type: 'introduction', required: true });
  }

  // 2. Phoneme practice
  activities.push({
    type: 'letter-drill',
    required: true,
    config: { letters: lesson.gpcs.map(g => g.grapheme) }
  });

  // 3. Discrimination practice
  activities.push({
    type: 'say-the-sound',
    required: true,
    config: { gpcs: lesson.gpcs.map(g => g.id) }
  });

  // 4. Blending (if lesson has words)
  if (lesson.words.length > 0) {
    activities.push({
      type: 'blend-it',
      required: false,
      config: { words: lesson.words.slice(0, 5) }
    });

    activities.push({
      type: 'word-builder',
      required: true,
      config: { words: lesson.words.slice(0, 3) }
    });
  }

  // 5. Fluency (if lesson has sentences)
  if (lesson.sentences.length > 0) {
    activities.push({
      type: 'read-aloud',
      required: false,
      config: { sentences: lesson.sentences }
    });
  }

  return activities;
}
```

---

## Curriculum Phases

Based on UK Letters and Sounds + Common Core alignment:

### Phase 1: Foundation (Pre-reading)
- Environmental sounds
- Rhyme awareness
- Oral blending/segmenting
- No lessons needed - separate activities

### Phase 2: Basic GPCs (Lessons 1-6)
- Single letter GPCs
- CVC words
- Lessons:
  1. s, a, t, p
  2. i, n, m, d
  3. g, o, c, k
  4. ck, e, u, r
  5. h, b, f, l
  6. ss, ff, ll, j, v, w, x, y, z, qu

### Phase 3: Consonant Digraphs (Lessons 7-12)
- sh, ch, th, ng
- ai, ee, igh, oa, oo
- Lessons:
  7. sh, ch
  8. th, ng
  9. ai, ee
  10. igh, oa
  11. oo (long), oo (short)
  12. ar, or, ur, er

### Phase 4: Adjacent Consonants (Lessons 13-18)
- CCVC, CVCC words
- Consonant blends
- Lessons:
  13. Initial blends (st, sp, sm)
  14. Initial blends (sc, sk, sn)
  15. Initial blends (bl, cl, fl)
  16. Initial blends (br, cr, dr, fr, gr, tr)
  17. Final blends (nd, nt, nk)
  18. Final blends (mp, lt, lk, pt)

### Phase 5: Complex GPCs (Lessons 19-30)
- Alternative spellings
- Split digraphs
- Lessons:
  19-24: Alternative vowel spellings (ay/ai, ea/ee, etc.)
  25-30: Alternative consonant spellings (c/k/ck, etc.)

### Phase 6: Fluency (Lessons 31+)
- Suffixes, prefixes
- Multi-syllable words
- Fluency practice

---

## File Structure

```
/public/curriculum/
├── curriculum.json          # Master file with all lessons
├── phases/
│   ├── phase-2.json        # Lessons 1-6
│   ├── phase-3.json        # Lessons 7-12
│   ├── phase-4.json        # Lessons 13-18
│   └── phase-5.json        # Lessons 19-30
├── gpcs/
│   └── english-gpcs.json   # All GPC definitions
├── words/
│   ├── decodable-words.json    # Words by lesson
│   └── sight-words.json        # High-frequency words
└── sentences/
    └── decodable-sentences.json # Sentences by lesson
```

---

## Integration with Existing Activities

### Activity Configuration Updates

Each activity needs to accept lesson-based configuration:

```javascript
// Current: Activity uses hardcoded word list
const words = ['cat', 'dog', 'fish'];

// New: Activity receives words from lesson
async function initActivity(config) {
  const { lessonId, activityType } = config;
  const lesson = await loadLesson(lessonId);
  const activityConfig = lesson.activities.find(a => a.type === activityType);

  // Use lesson-specific words
  const words = activityConfig.config.words || lesson.words;
  // ...
}
```

### URL Structure

```
/activities/{activity}?lesson={lessonId}

Examples:
/activities/word-builder?lesson=1
/activities/blend-it?lesson=5
/activities/read-aloud?lesson=12
```

---

## Next Steps

1. Create `curriculum.json` with Phase 2 lessons
2. Update activities to accept lesson configuration
3. Build lesson selector UI
4. Implement progression tracking
5. Add remediation system
