# Kalulu Pedagogical Principles

Deep analysis of Stanislas Dehaene's Kalulu reading program, documenting the cognitive science principles and implementation details that make it effective.

## Table of Contents

1. [Core Principles](#core-principles)
2. [Lesson Architecture](#lesson-architecture)
3. [Adaptive Learning Systems](#adaptive-learning-systems)
4. [Exercise Design Patterns](#exercise-design-patterns)
5. [Error Feedback Mechanisms](#error-feedback-mechanisms)
6. [Data Tracking & Analytics](#data-tracking--analytics)
7. [Implementation Details](#implementation-details)

---

## Core Principles

### Dehaene's Four Pillars of Learning

Kalulu implements Stanislas Dehaene's research on how the brain learns to read:

#### 1. Attention
- **Audio-first design**: Every item plays audio BEFORE visual selection
- **Single focus**: One target stimulus per trial
- **Clear visual hierarchy**: Target highlighted, distractors muted
- **Minimal distractions**: Clean game interfaces

#### 2. Active Engagement
- **Interactive games**: Not passive watching
- **Physical response**: Touch/click required for every item
- **Immediate feedback**: Every action gets response
- **Student agency**: Can replay audio, choose pace

#### 3. Error Feedback
- **Immediate**: Wrong answer shown instantly
- **Corrective**: Correct answer played after error
- **Non-punitive**: Errors are learning opportunities
- **Adaptive**: More errors = more support

#### 4. Consolidation
- **Spaced repetition**: Struggling items resurface
- **70/30 rule**: 70% new, 30% review
- **Sleep consolidation**: Sessions designed to be short
- **Multi-day progression**: Not designed for cramming

### Systematic Phonics Approach

Kalulu uses **synthetic phonics** (decoding-based method):

1. **Grapheme-Phoneme Correspondences (GPCs)** taught explicitly
2. **Sound → Letter** direction (hear phoneme, find grapheme)
3. **Blending** (combine GPCs to read words)
4. **Segmenting** (break words into GPCs)

### Frequency-Based Ordering

GPCs are introduced based on:
- **Frequency in children's literature** (Manulex corpus for French)
- **Decodability** (simpler patterns first)
- **Utility** (high-frequency GPCs = more readable words sooner)

---

## Lesson Architecture

### Lesson Sequence

Each lesson follows a strict pedagogical sequence:

```
┌─────────────────────────────────────────────────────────────┐
│                        LESSON N                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. LOOK AND LEARN (Video Introduction)                     │
│     ├── New GPC introduced visually                         │
│     ├── Letter formation shown                              │
│     ├── Sound pronunciation modeled                         │
│     └── Must complete to unlock games                       │
│                                                              │
│  2. THREE MINIGAMES (unlock in parallel after Look & Learn) │
│     ├── Game 1: Syllable Decoding (hear → find)            │
│     ├── Game 2: Word Building (assemble GPCs)              │
│     └── Game 3: Lexical Decision (real vs pseudoword)      │
│                                                              │
│  3. BOSS LEVEL (unlocks after all 3 games complete)        │
│     └── Sentence-level practice                             │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                        LESSON N+1
```

### Unlock Progression

```javascript
// Progression states
enum Status {
  Locked,    // Cannot access
  Unlocked,  // Can access, not completed
  Completed  // Finished successfully
}

// Rules:
// 1. Lesson N must be fully complete before Lesson N+1 unlocks
// 2. Look and Learn must complete before Games unlock
// 3. All 3 Games must complete before Boss unlocks
// 4. First lesson always starts Unlocked
```

### Lesson Data Model

```javascript
{
  "lesson_id": 1,
  "gpcs": [
    { "grapheme": "a", "phoneme": "/a/", "type": "vowel" }
  ],
  "syllables": [
    { "grapheme": "ma", "phoneme": "/ma/", "gpcs": ["m", "a"] }
  ],
  "words": [
    { "word": "mama", "gpcs": ["m", "a", "m", "a"], "audio": "mama.mp3" }
  ],
  "sentences": [
    { "sentence": "Mama a mal.", "words": ["mama", "a", "mal"] }
  ]
}
```

---

## Adaptive Learning Systems

### 1. Remediation Engine

Tracks performance per item and prioritizes struggling content.

#### Score Mechanics

```javascript
// Constants
const MIN_SCORE = -3;        // Floor (max struggle)
const MAX_SCORE = 0;         // Ceiling (mastered)
const REMEDIATION_THRESHOLD = -2;  // Below this = needs remediation

// Scoring
// Correct answer: +1
// Wrong answer: -1
// Both the correct AND selected answer get -1 on errors

// Score clamped to [MIN_SCORE, MAX_SCORE]
// Items at 0 are removed from tracking (mastered)
// Items <= REMEDIATION_THRESHOLD are flagged for extra practice
```

#### Data Structure

```javascript
// Per student, tracked separately for:
{
  "gps_scores": {
    12: -2,  // GP ID 12 has score -2 (needs remediation)
    45: -1,  // GP ID 45 has score -1 (struggling)
    // Items at 0 are not stored (mastered)
  },
  "syllables_scores": { ... },
  "words_scores": { ... }
}
```

#### Remediation Sorting

When selecting stimuli, items are sorted by remediation score:

```javascript
// Lower score = more errors = higher priority
function sortByRemediation(stimuli) {
  return stimuli.sort((a, b) => {
    const scoreA = getRemediationScore(a);
    const scoreB = getRemediationScore(b);
    return scoreA - scoreB;  // Lowest (most negative) first
  });
}
```

### 2. Confusion Matrix

Tracks which items get confused with each other.

#### Purpose
- Identify common confusions (e.g., b/d, p/q)
- Generate better distractors based on actual confusions
- Inform intervention strategies

#### Data Structure

```javascript
// For each expected answer, store history of actual responses
{
  "gp_scores": {
    12: [12, 12, 45, 12, 12],  // Expected GP 12, got [12,12,45,12,12]
    // First two were correct, third was confused with GP 45
  }
}

// Limited to last 5 responses (FIFO)
const HISTORY_LENGTH = 5;
```

#### Analysis

```javascript
// To find confusions for GP 12:
const history = confusion_matrix[12];  // [12, 12, 45, 12, 12]
const errors = history.filter(x => x !== 12);  // [45]
// GP 12 is often confused with GP 45
```

### 3. Difficulty Adjustment

Per-minigame difficulty that adapts to student performance.

#### Levels

```javascript
// 5 difficulty levels (0-4)
const DIFFICULTY_LEVELS = [
  { spawn_time: 4.0, stimuli_ratio: 0.75, velocity: 150 },  // Level 0: Easy
  { spawn_time: 3.5, stimuli_ratio: 0.66, velocity: 175 },  // Level 1
  { spawn_time: 3.0, stimuli_ratio: 0.33, velocity: 200 },  // Level 2
  { spawn_time: 2.5, stimuli_ratio: 0.25, velocity: 250 },  // Level 3
  { spawn_time: 2.0, stimuli_ratio: 0.25, velocity: 300 },  // Level 4: Hard
];

// Parameters affected:
// - spawn_time: How often new items appear
// - stimuli_ratio: % of items that are targets vs distractors
// - velocity: How fast items move
```

#### Adjustment Algorithm

```javascript
const CONSECUTIVE_WINS_TO_PROMOTE = 2;
const CONSECUTIVE_LOSSES_TO_DEMOTE = 2;

function updateDifficulty(minigame, won) {
  if (won) {
    consecutiveLosses = 0;
    consecutiveWins++;
    if (consecutiveWins >= CONSECUTIVE_WINS_TO_PROMOTE) {
      consecutiveWins = 0;
      difficulty = Math.min(difficulty + 1, MAX_DIFFICULTY);
    }
  } else {
    consecutiveWins = 0;
    consecutiveLosses++;
    if (consecutiveLosses >= CONSECUTIVE_LOSSES_TO_DEMOTE) {
      consecutiveLosses = 0;
      difficulty = Math.max(difficulty - 1, MIN_DIFFICULTY);
    }
  }
}
```

### 4. Hint System

Progressive hints when student struggles.

#### Hint Escalation

```javascript
// Configurable per minigame
const ERRORS_BEFORE_HELP_SPEECH = 2;  // Play Kalulu help audio
const ERRORS_BEFORE_HIGHLIGHT = 3;    // Visually highlight correct answer

// On each error:
consecutive_errors++;

if (consecutive_errors >= ERRORS_BEFORE_HELP_SPEECH) {
  playKaluluHelpSpeech();  // "Remember, listen carefully..."
}

if (consecutive_errors >= ERRORS_BEFORE_HIGHLIGHT) {
  is_highlighting = true;  // Correct answer glows/pulses
}

// Reset on correct answer
if (correct) {
  consecutive_errors = 0;
  is_highlighting = false;
}
```

---

## Exercise Design Patterns

### Pattern 1: Hear and Find (Syllable Games)

**Minigames**: Jellyfish, Crabs, Parakeets, Monkeys

**Mechanics**:
1. Audio plays target syllable/phoneme
2. Multiple items appear on screen (moving)
3. Student taps the matching grapheme
4. Immediate visual/audio feedback

**Difficulty Scaling**:
```javascript
// Level 1: All distractors have completely different letters
distractor = findDifferentLetters(target);

// Level 2-3: Single letter change ("cha" vs "la" or "che")
distractor = changeOneLetter(target);

// Level 4-5: Include inversions ("il" vs "li")
distractor = invertLetters(target);
```

**Key Design Principles**:
- Audio MUST play before student can respond
- Replay button always available
- Timer auto-replays if no response (15 seconds)
- Wrong answer plays its sound, then replays target

### Pattern 2: Word Building (Word Games)

**Minigames**: Turtles, Ants, Penguin

**Mechanics**:
1. Audio plays complete word
2. Student builds word GPC by GPC (left to right)
3. Each GPC selection is validated immediately
4. Word completes when all GPCs selected correctly

**Key Design Principles**:
- Progressive disclosure (one GPC at a time)
- Can't skip ahead
- Error on any GPC = must redo that GPC
- Visual shows which GPCs are complete

### Pattern 3: Lexical Decision (Fish Game)

**Mechanics**:
1. Words and pseudowords appear
2. Student identifies which are real words
3. Tests whole-word recognition

**Key Design Principles**:
- Pseudowords follow phonetic rules (decodable but meaningless)
- Tests automaticity (quick recognition vs slow decoding)
- Builds sight word vocabulary

---

## Error Feedback Mechanisms

### Immediate Feedback Loop

```
Student selects item
        │
        ▼
┌─────────────────┐
│ Is it correct?  │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
   YES        NO
    │         │
    ▼         ▼
┌───────┐  ┌────────────────────┐
│ Happy │  │ Show error effect  │
│ sound │  │ Play selected item │
│ +1    │  │ Play correct item  │
│ Next  │  │ -1 life            │
└───────┘  │ Continue           │
           └────────────────────┘
```

### Corrective Feedback

On error:
1. **Visual**: Wrong answer shakes/turns red
2. **Auditory**: Error sound plays
3. **Corrective**: Selected item's sound plays
4. **Model**: Correct answer's sound plays
5. **Continue**: Game resumes (not game over)

### Loss Conditions

- Lives system (typically 3-5 lives)
- Run out of lives = must restart level
- But: WINNING triggers next level unlock
- Losing does NOT lock progression

---

## Data Tracking & Analytics

### Session Logging

Each minigame session logs:

```javascript
{
  "answers": [
    {
      "response": { "ID": 45, "Grapheme": "ch" },
      "awaited_response": { "ID": 12, "Grapheme": "sh" },
      "is_right": false,
      "minigame": "jellyfish",
      "number_of_hints": 1,
      "current_progression": 3,
      "max_progression": 10,
      "current_lives": 2,
      "max_number_of_lives": 3
    },
    // ... more answers
  ]
}

// Saved per student, per minigame, per lesson, timestamped
// Path: /student_folder/minigame_name.tres
// Grouped by lesson_nb, then by timestamp
```

### Duration Tracking

```javascript
// Per lesson, per game
{
  "last_duration": [120, 85, 0],   // Seconds spent in last attempt
  "total_duration": [450, 320, 0]  // Cumulative seconds
}
// Index 0 = Game 1, Index 1 = Game 2, Index 2 = Game 3
```

### Metrics Available

1. **Per Student**:
   - Lesson progression (which lessons complete)
   - Game durations
   - Remediation scores per GP/syllable/word
   - Confusion patterns
   - Difficulty level per minigame

2. **Per Session**:
   - All responses with correctness
   - Hint usage
   - Lives remaining
   - Time spent

3. **Per Item**:
   - Error rate
   - Confusion partners
   - Remediation priority

---

## Implementation Details

### Stimulus Selection Algorithm

```javascript
function findStimuliAndDistractions(lessonNb, maxProgression) {
  // 1. Get all available items up to current lesson
  const allItems = Database.getItemsForLesson(lessonNb);

  // 2. Split by lesson
  const currentLessonItems = allItems.filter(i => i.lessonNb === lessonNb);
  const previousLessonItems = allItems.filter(i => i.lessonNb < lessonNb);

  // 3. Shuffle both arrays
  shuffle(currentLessonItems);
  shuffle(previousLessonItems);

  // 4. Sort by remediation score (struggling items first)
  currentLessonItems.sort(sortByRemediation);
  previousLessonItems.sort(sortByRemediation);

  // 5. Build stimulus list with 70/30 ratio
  const targetFromCurrent = Math.floor(maxProgression * 0.7);
  const stimuli = [];

  // Add current lesson items
  for (let i = 0; i < targetFromCurrent && i < currentLessonItems.length; i++) {
    stimuli.push(currentLessonItems[i]);
  }

  // Fill rest with previous lessons
  const remaining = maxProgression - stimuli.length;
  for (let i = 0; i < remaining && i < previousLessonItems.length; i++) {
    stimuli.push(previousLessonItems[i]);
  }

  // 6. Final shuffle
  shuffle(stimuli);

  // 7. Find distractors for each stimulus
  for (const stimulus of stimuli) {
    stimulus.distractors = Database.getDistractorsFor(stimulus.id, lessonNb);
  }

  return stimuli;
}
```

### Distractor Selection

```javascript
function getDistractorsForGrapheme(gpId, lessonNb, difficulty) {
  const target = Database.getGP(gpId);
  const allGPs = Database.getGPsForLesson(lessonNb);
  const distractors = [];

  // Difficulty 1: Completely different letters
  for (const gp of allGPs) {
    if (gp.id !== target.id && !sharesLetters(gp, target)) {
      distractors.push(gp);
    }
  }

  // Difficulty 2-3: Single letter change
  if (difficulty >= 2) {
    for (const gp of allGPs) {
      if (differsByOneLetter(gp, target)) {
        distractors.push(gp);
      }
    }
  }

  // Difficulty 4-5: Inversions
  if (difficulty >= 4) {
    for (const gp of allGPs) {
      if (isInversion(gp, target)) {
        distractors.push(gp);
      }
    }
  }

  return shuffle(distractors);
}
```

### Game Loop Structure

```javascript
// Base minigame flow
class Minigame {
  async run() {
    // 1. Initialize
    this.findStimuliAndDistractions();
    this.setupUI();

    // 2. Opening
    await this.openCurtain();
    if (!this.hasSeenIntro()) {
      await this.playKaluluIntro();
      this.markIntroSeen();
    }

    // 3. Start timer
    this.startTime = now();

    // 4. Main loop
    while (this.currentProgression < this.maxProgression && this.lives > 0) {
      await this.playStimulus();
      const response = await this.waitForResponse();
      this.logResponse(response);

      if (this.isCorrect(response)) {
        await this.showCorrectFeedback();
        this.currentProgression++;
        this.consecutiveErrors = 0;
      } else {
        await this.showWrongFeedback();
        this.lives--;
        this.consecutiveErrors++;
        this.checkHints();
      }
    }

    // 5. End
    this.recordDuration();
    this.updateRemediationScores();
    this.updateConfusionMatrix();

    if (this.lives > 0) {
      await this.win();
    } else {
      await this.lose();
    }
  }
}
```

---

## Key Takeaways for FunBookies

### Must-Have Features

1. **Audio-First**: Every activity should play the target sound before allowing response
2. **Immediate Feedback**: Correct/wrong shown within 100ms
3. **Corrective Feedback**: On error, play both selected AND correct sounds
4. **Progressive Hints**: After N errors, provide visual highlighting
5. **Spaced Repetition**: Track errors and resurface struggling items

### Should-Have Features

1. **Lesson Structure**: Group GPCs into explicit lessons with sequence
2. **Confusion Matrix**: Track what gets confused with what
3. **Adaptive Difficulty**: Adjust speed/complexity per student
4. **Session Logging**: Record all responses for analysis

### Nice-to-Have Features

1. **70/30 Mix**: Balance new content with review
2. **Kalulu-style Mascot**: Character that provides encouragement
3. **Per-Minigame Difficulty**: Different difficulty per game type
4. **Duration Tracking**: Time spent per lesson/game

---

## Research References

1. Dehaene, S. (2009). *Reading in the Brain*
2. Dehaene, S. (2020). *How We Learn*
3. Kalulu published research:
   - https://www.tandfonline.com/doi/pdf/10.1080/00220973.2023.2173129
   - https://hal.science/hal-03015914/document
   - https://hal.science/hal-03702075/document
