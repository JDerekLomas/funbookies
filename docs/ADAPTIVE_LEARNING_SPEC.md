# FunBookies Adaptive Learning System Specification

Based on Kalulu's research-backed approach to spaced repetition, remediation, and confusion tracking.

---

## Overview

The adaptive learning system has three components:

1. **Remediation Engine** - Tracks struggling items and prioritizes them
2. **Confusion Matrix** - Tracks what gets confused with what
3. **Difficulty Adjustment** - Adapts game speed/complexity per student

---

## 1. Remediation Engine

### Purpose

Track performance per item (GPC, word, etc.) and prioritize struggling content for additional practice.

### Score Mechanics

```javascript
const REMEDIATION_CONFIG = {
  MIN_SCORE: -3,           // Floor (maximum struggle indicator)
  MAX_SCORE: 0,            // Ceiling (mastered)
  REMEDIATION_THRESHOLD: -2,  // Below this = needs extra practice
};

// Scoring rules:
// - Correct answer: +1 to item score
// - Wrong answer: -1 to expected item AND -1 to selected item
// - Score clamped to [MIN_SCORE, MAX_SCORE]
// - Items at score 0 are considered mastered
// - Items at or below THRESHOLD get prioritized
```

### Data Schema

```javascript
// Stored in IndexedDB per student
const remediationSchema = {
  studentId: 'string',
  gpcs: {
    // GPC ID → score
    's-/s/': -2,    // Struggling
    'a-/æ/': -1,    // Needs attention
    't-/t/': 0,     // Mastered (can be omitted)
  },
  words: {
    // Word ID → score
    'sat': -1,
    'pat': 0,
  },
  syllables: {
    'sa': -2,
    'at': 0,
  },
  lastModified: 'ISO date string'
};
```

### Implementation

```javascript
// /public/js/remediation.js

const Remediation = (function() {
  const CONFIG = {
    MIN_SCORE: -3,
    MAX_SCORE: 0,
    THRESHOLD: -2,
  };

  // Get current score for an item
  async function getScore(type, itemId) {
    const data = await FunBookiesDB.get('remediation', type);
    if (!data || !data[itemId]) return 0;
    const score = data[itemId];
    return score <= CONFIG.THRESHOLD ? score : 0;
  }

  // Update score after response
  async function updateScore(type, itemId, delta) {
    const data = await FunBookiesDB.get('remediation', type) || {};

    let newScore = (data[itemId] || 0) + delta;
    newScore = Math.max(CONFIG.MIN_SCORE, Math.min(CONFIG.MAX_SCORE, newScore));

    if (newScore >= CONFIG.MAX_SCORE) {
      delete data[itemId];  // Mastered, remove from tracking
    } else {
      data[itemId] = newScore;
    }

    await FunBookiesDB.set('remediation', type, data);
    return newScore;
  }

  // Record a response (correct or incorrect)
  async function recordResponse(type, expectedId, selectedId, wasCorrect) {
    if (wasCorrect) {
      // +1 for correct
      await updateScore(type, expectedId, 1);
    } else {
      // -1 for expected (missed it)
      await updateScore(type, expectedId, -1);
      // -1 for selected (chose wrong one)
      if (selectedId !== expectedId) {
        await updateScore(type, selectedId, -1);
      }
    }
  }

  // Get items that need remediation
  async function getItemsNeedingRemediation(type) {
    const data = await FunBookiesDB.get('remediation', type) || {};
    return Object.entries(data)
      .filter(([id, score]) => score <= CONFIG.THRESHOLD)
      .sort((a, b) => a[1] - b[1])  // Most negative first
      .map(([id, score]) => ({ id, score }));
  }

  // Sort items by remediation priority (struggling first)
  async function sortByPriority(type, items, idField = 'id') {
    const scores = await FunBookiesDB.get('remediation', type) || {};

    return [...items].sort((a, b) => {
      const scoreA = scores[a[idField]] || 0;
      const scoreB = scores[b[idField]] || 0;
      return scoreA - scoreB;  // Lower (more negative) first
    });
  }

  return {
    getScore,
    updateScore,
    recordResponse,
    getItemsNeedingRemediation,
    sortByPriority,
    CONFIG,
  };
})();
```

### Usage in Activities

```javascript
// In any activity that tracks responses:

async function handleResponse(expected, selected) {
  const wasCorrect = expected.id === selected.id;

  // Record for remediation
  await Remediation.recordResponse('gpcs', expected.id, selected.id, wasCorrect);

  // Show feedback...
}

// When selecting stimuli for a session:
async function selectStimuli(lesson, count) {
  const allWords = lesson.words;

  // Shuffle first
  shuffle(allWords);

  // Then sort by remediation priority
  const sorted = await Remediation.sortByPriority('words', allWords, 'id');

  return sorted.slice(0, count);
}
```

---

## 2. Confusion Matrix

### Purpose

Track which items get confused with each other to:
- Identify common error patterns (e.g., b/d confusion)
- Generate better distractors
- Inform intervention strategies

### Data Schema

```javascript
// Stored in IndexedDB per student
const confusionMatrixSchema = {
  studentId: 'string',
  gpcs: {
    // Expected ID → array of last N responses (including correct ones)
    's-/s/': ['s-/s/', 's-/s/', 'sh-/ʃ/', 's-/s/', 's-/s/'],  // Confused with 'sh' once
    'b-/b/': ['b-/b/', 'd-/d/', 'b-/b/', 'd-/d/', 'b-/b/'],   // Confused with 'd' twice
  },
  words: {
    'was': ['was', 'saw', 'was', 'was', 'saw'],  // Confused with 'saw'
  },
  historyLength: 5,
  lastModified: 'ISO date string'
};
```

### Implementation

```javascript
// /public/js/confusion-matrix.js

const ConfusionMatrix = (function() {
  const HISTORY_LENGTH = 5;

  // Record a response
  async function recordResponse(type, expectedId, selectedId) {
    const data = await FunBookiesDB.get('confusionMatrix', type) || {};

    // Get or create history array
    const history = data[expectedId] || [];

    // Add new response
    history.push(selectedId);

    // Trim to HISTORY_LENGTH (FIFO)
    while (history.length > HISTORY_LENGTH) {
      history.shift();
    }

    data[expectedId] = history;
    await FunBookiesDB.set('confusionMatrix', type, data);
  }

  // Get confusion partners for an item
  async function getConfusions(type, itemId) {
    const data = await FunBookiesDB.get('confusionMatrix', type) || {};
    const history = data[itemId] || [];

    // Count errors (responses that weren't the expected item)
    const confusions = {};
    for (const response of history) {
      if (response !== itemId) {
        confusions[response] = (confusions[response] || 0) + 1;
      }
    }

    // Sort by frequency
    return Object.entries(confusions)
      .sort((a, b) => b[1] - a[1])
      .map(([id, count]) => ({ id, count, rate: count / history.length }));
  }

  // Get all confusion pairs
  async function getAllConfusions(type) {
    const data = await FunBookiesDB.get('confusionMatrix', type) || {};
    const allConfusions = [];

    for (const [expectedId, history] of Object.entries(data)) {
      for (const response of history) {
        if (response !== expectedId) {
          allConfusions.push({
            expected: expectedId,
            selected: response,
          });
        }
      }
    }

    // Group and count
    const grouped = {};
    for (const { expected, selected } of allConfusions) {
      const key = `${expected}→${selected}`;
      grouped[key] = (grouped[key] || 0) + 1;
    }

    return Object.entries(grouped)
      .map(([key, count]) => {
        const [expected, selected] = key.split('→');
        return { expected, selected, count };
      })
      .sort((a, b) => b.count - a.count);
  }

  // Generate smart distractors based on confusions
  async function getSmartDistractors(type, targetId, candidates, count = 3) {
    const confusions = await getConfusions(type, targetId);
    const distractors = [];

    // First, add known confusions
    for (const { id } of confusions) {
      if (candidates.includes(id) && distractors.length < count) {
        distractors.push(id);
      }
    }

    // Fill rest with random candidates
    const remaining = candidates.filter(c =>
      c !== targetId && !distractors.includes(c)
    );
    shuffle(remaining);

    while (distractors.length < count && remaining.length > 0) {
      distractors.push(remaining.pop());
    }

    return distractors;
  }

  return {
    recordResponse,
    getConfusions,
    getAllConfusions,
    getSmartDistractors,
    HISTORY_LENGTH,
  };
})();
```

### Usage in Activities

```javascript
// After every response:
async function handleResponse(expected, selected) {
  // Record for confusion matrix (even correct responses)
  await ConfusionMatrix.recordResponse('gpcs', expected.id, selected.id);

  // Also record for remediation
  const wasCorrect = expected.id === selected.id;
  await Remediation.recordResponse('gpcs', expected.id, selected.id, wasCorrect);
}

// When generating distractors:
async function generateDistractors(target, allOptions) {
  // Use confusion matrix to pick challenging distractors
  return await ConfusionMatrix.getSmartDistractors(
    'gpcs',
    target.id,
    allOptions.map(o => o.id),
    3  // number of distractors
  );
}
```

### Analytics Dashboard

```javascript
// Get common confusion pairs for a student
const confusions = await ConfusionMatrix.getAllConfusions('gpcs');
// Returns: [
//   { expected: 'b-/b/', selected: 'd-/d/', count: 5 },
//   { expected: 's-/s/', selected: 'sh-/ʃ/', count: 3 },
//   ...
// ]

// Identify students who need b/d intervention
const bConfusions = await ConfusionMatrix.getConfusions('gpcs', 'b-/b/');
if (bConfusions.some(c => c.id === 'd-/d/' && c.rate > 0.3)) {
  // Student confuses b/d more than 30% of the time
  suggestIntervention('b-d-discrimination');
}
```

---

## 3. Difficulty Adjustment

### Purpose

Adapt game parameters per student per activity to maintain optimal challenge.

### Difficulty Levels

```javascript
const DIFFICULTY_LEVELS = {
  // Per activity type
  'word-builder': [
    { level: 0, timeLimit: null, hints: true, distractorSimilarity: 'low' },
    { level: 1, timeLimit: 60, hints: true, distractorSimilarity: 'low' },
    { level: 2, timeLimit: 45, hints: true, distractorSimilarity: 'medium' },
    { level: 3, timeLimit: 30, hints: false, distractorSimilarity: 'medium' },
    { level: 4, timeLimit: 20, hints: false, distractorSimilarity: 'high' },
  ],
  'say-the-sound': [
    { level: 0, speed: 0.5, distractorCount: 2, similarity: 'different' },
    { level: 1, speed: 0.75, distractorCount: 3, similarity: 'different' },
    { level: 2, speed: 1.0, distractorCount: 3, similarity: 'similar' },
    { level: 3, speed: 1.25, distractorCount: 4, similarity: 'similar' },
    { level: 4, speed: 1.5, distractorCount: 4, similarity: 'minimal-pair' },
  ],
  // ... other activities
};
```

### Adjustment Algorithm

```javascript
const DIFFICULTY_CONFIG = {
  MIN_LEVEL: 0,
  MAX_LEVEL: 4,
  WINS_TO_PROMOTE: 2,    // Consecutive wins to level up
  LOSSES_TO_DEMOTE: 2,   // Consecutive losses to level down
};

// Schema
const difficultySchema = {
  studentId: 'string',
  activities: {
    'word-builder': {
      level: 2,
      consecutiveWins: 1,
      consecutiveLosses: 0,
      history: [true, false, true, true],  // Last N outcomes
    },
    'say-the-sound': {
      level: 1,
      consecutiveWins: 0,
      consecutiveLosses: 1,
      history: [true, true, false],
    },
  },
  lastModified: 'ISO date string'
};
```

### Implementation

```javascript
// /public/js/difficulty.js

const Difficulty = (function() {
  const CONFIG = {
    MIN_LEVEL: 0,
    MAX_LEVEL: 4,
    WINS_TO_PROMOTE: 2,
    LOSSES_TO_DEMOTE: 2,
  };

  async function getLevel(activityType) {
    const data = await FunBookiesDB.get('difficulty', activityType);
    return data?.level || 0;
  }

  async function recordOutcome(activityType, won) {
    let data = await FunBookiesDB.get('difficulty', activityType) || {
      level: 0,
      consecutiveWins: 0,
      consecutiveLosses: 0,
      history: [],
    };

    // Update history
    data.history.push(won);
    if (data.history.length > 10) data.history.shift();

    if (won) {
      data.consecutiveLosses = 0;
      data.consecutiveWins++;

      // Level up?
      if (data.consecutiveWins >= CONFIG.WINS_TO_PROMOTE) {
        data.consecutiveWins = 0;
        if (data.level < CONFIG.MAX_LEVEL) {
          data.level++;
          console.log(`Difficulty increased to ${data.level} for ${activityType}`);
        }
      }
    } else {
      data.consecutiveWins = 0;
      data.consecutiveLosses++;

      // Level down?
      if (data.consecutiveLosses >= CONFIG.LOSSES_TO_DEMOTE) {
        data.consecutiveLosses = 0;
        if (data.level > CONFIG.MIN_LEVEL) {
          data.level--;
          console.log(`Difficulty decreased to ${data.level} for ${activityType}`);
        }
      }
    }

    await FunBookiesDB.set('difficulty', activityType, data);
    return data.level;
  }

  async function getSettings(activityType) {
    const level = await getLevel(activityType);
    const settings = DIFFICULTY_LEVELS[activityType];
    return settings?.[level] || settings?.[0] || {};
  }

  return {
    getLevel,
    recordOutcome,
    getSettings,
    CONFIG,
  };
})();
```

### Usage in Activities

```javascript
// At activity start:
async function initActivity() {
  const settings = await Difficulty.getSettings('word-builder');
  // settings = { level: 2, timeLimit: 45, hints: true, distractorSimilarity: 'medium' }

  if (settings.timeLimit) {
    startTimer(settings.timeLimit);
  }
  if (!settings.hints) {
    hideHintButton();
  }
  // etc.
}

// At activity end:
async function endActivity(completed, livesRemaining) {
  const won = completed && livesRemaining > 0;
  await Difficulty.recordOutcome('word-builder', won);
}
```

---

## 4. Hint System

### Progressive Hints

```javascript
const HINT_CONFIG = {
  ERRORS_BEFORE_AUDIO_HINT: 2,   // Replay correct sound
  ERRORS_BEFORE_VISUAL_HINT: 3,  // Highlight correct answer
};

class HintManager {
  constructor() {
    this.consecutiveErrors = 0;
    this.hintsGiven = 0;
  }

  recordError() {
    this.consecutiveErrors++;
    return this.getHintLevel();
  }

  recordCorrect() {
    this.consecutiveErrors = 0;
  }

  getHintLevel() {
    if (this.consecutiveErrors >= HINT_CONFIG.ERRORS_BEFORE_VISUAL_HINT) {
      return 'visual';  // Show correct answer
    }
    if (this.consecutiveErrors >= HINT_CONFIG.ERRORS_BEFORE_AUDIO_HINT) {
      return 'audio';   // Replay target sound
    }
    return 'none';
  }

  shouldHighlight() {
    return this.consecutiveErrors >= HINT_CONFIG.ERRORS_BEFORE_VISUAL_HINT;
  }
}
```

### Usage

```javascript
const hints = new HintManager();

function handleResponse(selected, expected) {
  if (selected.id === expected.id) {
    hints.recordCorrect();
    showCorrectFeedback();
  } else {
    const hintLevel = hints.recordError();
    showWrongFeedback();

    if (hintLevel === 'audio') {
      // Replay the target sound
      playAudio(expected.audio);
    }

    if (hintLevel === 'visual') {
      // Highlight the correct option
      highlightCorrectAnswer(expected);
    }
  }
}
```

---

## 5. Stimulus Selection Algorithm

### The 70/30 Rule

Each session should use approximately:
- 70% items from current lesson
- 30% items from previous lessons (review)

### Implementation

```javascript
async function selectStimuli(lesson, totalCount) {
  const currentLessonRatio = 0.7;
  const currentCount = Math.floor(totalCount * currentLessonRatio);
  const reviewCount = totalCount - currentCount;

  // Get items from current lesson
  let currentItems = [...lesson.words];
  shuffle(currentItems);
  currentItems = await Remediation.sortByPriority('words', currentItems);

  // Get items from previous lessons
  let reviewItems = await getPreviousLessonItems(lesson.id);
  shuffle(reviewItems);
  reviewItems = await Remediation.sortByPriority('words', reviewItems);

  // Select items
  const stimuli = [];

  // Add current lesson items (prioritizing struggling ones)
  for (let i = 0; i < currentCount && i < currentItems.length; i++) {
    stimuli.push(currentItems[i]);
  }

  // Add review items
  for (let i = 0; i < reviewCount && i < reviewItems.length; i++) {
    stimuli.push(reviewItems[i]);
  }

  // If not enough, fill from current lesson
  while (stimuli.length < totalCount && currentItems.length > stimuli.length) {
    const remaining = currentItems.filter(i => !stimuli.includes(i));
    if (remaining.length > 0) {
      stimuli.push(remaining[0]);
    } else {
      break;
    }
  }

  // Final shuffle
  shuffle(stimuli);
  return stimuli;
}
```

---

## 6. Integration with FunBookiesDB

### Schema Updates

```javascript
// Add to FunBookiesDB stores
const additionalStores = {
  remediation: {
    keyPath: 'type',  // 'gpcs', 'words', 'syllables'
    // value: { [itemId]: score }
  },
  confusionMatrix: {
    keyPath: 'type',
    // value: { [expectedId]: [history] }
  },
  difficulty: {
    keyPath: 'activityType',
    // value: { level, consecutiveWins, consecutiveLosses, history }
  },
};
```

### Migration

```javascript
// Upgrade FunBookiesDB to include new stores
const DB_VERSION = 2;  // Increment from current version

function upgrade(db, oldVersion) {
  if (oldVersion < 2) {
    db.createObjectStore('remediation', { keyPath: 'type' });
    db.createObjectStore('confusionMatrix', { keyPath: 'type' });
    db.createObjectStore('difficulty', { keyPath: 'activityType' });
  }
}
```

---

## 7. Analytics Events

### Track for Analysis

```javascript
// Events to log for learning analytics
const AnalyticsEvents = {
  RESPONSE: 'response',           // Every answer
  SESSION_START: 'session_start', // Activity started
  SESSION_END: 'session_end',     // Activity completed
  HINT_GIVEN: 'hint_given',       // Hint was shown
  DIFFICULTY_CHANGE: 'difficulty_change',  // Level up/down
};

function logEvent(event, data) {
  const entry = {
    event,
    timestamp: new Date().toISOString(),
    studentId: getCurrentStudent(),
    ...data,
  };

  // Store locally
  FunBookiesDB.append('analyticsLog', entry);

  // Optional: send to server
  // sendToAnalytics(entry);
}

// Example: Log every response
logEvent(AnalyticsEvents.RESPONSE, {
  activityType: 'word-builder',
  lessonId: 1,
  expected: 'sat',
  selected: 'pat',
  correct: false,
  responseTimeMs: 2340,
  hintsShown: 1,
  difficultyLevel: 2,
});
```

---

## Summary

| Component | Purpose | Key Metric |
|-----------|---------|------------|
| Remediation | Prioritize struggling items | Score: 0 (mastered) to -3 (struggling) |
| Confusion Matrix | Track error patterns | History of last 5 responses per item |
| Difficulty | Adapt challenge level | Level 0-4, adjusts after 2 wins/losses |
| Hints | Support struggling students | After 2-3 consecutive errors |
| 70/30 Mix | Balance new + review | 70% current lesson, 30% review |

All systems work together:
1. **Remediation** identifies WHAT needs practice
2. **Confusion Matrix** identifies WHY errors happen
3. **Difficulty** adjusts HOW challenging games are
4. **Hints** provide SUPPORT when struggling
5. **70/30 Mix** ensures REVIEW without boring mastered content
