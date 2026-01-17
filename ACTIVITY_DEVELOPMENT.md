# Activity Development Guide

This guide explains how to create new phonics activities for FunBookies.

## Quick Start

Copy an existing activity (e.g., `blend-it.html`) and modify it. All activities follow the same structure.

## Activity Template

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="icon" type="image/svg+xml" href="/favicon.svg">
  <title>Activity Name - FunBookies</title>

  <!-- Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&display=swap" rel="stylesheet">

  <!-- Shared styles -->
  <link rel="stylesheet" href="/styles/shared.css">

  <style>
    /* Activity-specific styles */
  </style>
</head>
<body>
  <!-- Required scripts (order matters) -->
  <script src="/js/data-service.js"></script>
  <script src="/js/student-picker.js"></script>
  <script src="/js/audio-utils.js"></script>
  <script src="/js/toast.js"></script>

  <div class="container-narrow">
    <div class="page-header">
      <a href="/activities/" class="back-link">&larr; Back to Activities</a>
    </div>

    <div class="game-card">
      <div class="game-header">
        <h1>Activity Name <span id="studentBadge" class="student-badge hidden"></span></h1>
        <div class="score-badge">Score: <span id="scoreDisplay">0</span></div>
      </div>

      <!-- Activity content here -->

    </div>
  </div>

  <script>
    // Activity state
    let currentStudent = null;
    let sessionStartTime = null;
    let score = 0;

    // Initialize
    document.addEventListener('DOMContentLoaded', async () => {
      // 1. Show student picker
      const picker = new StudentPicker({
        title: 'Who is practicing?',
        allowSkip: true
      });
      currentStudent = await picker.show();

      // 2. Show student badge if selected
      if (currentStudent) {
        const badge = document.getElementById('studentBadge');
        badge.textContent = `${currentStudent.avatar} ${currentStudent.name}`;
        badge.classList.remove('hidden');

        // 3. Optionally set level based on assessment
        const level = await window.FunBookiesDB.getCurrentLevel(currentStudent.id);
        if (level) {
          // Use level to configure difficulty
        }
      }

      // 4. Start session timer
      sessionStartTime = Date.now();

      // 5. Start the activity
      startGame();
    });

    // Save progress to IndexedDB
    async function saveActivity() {
      if (!currentStudent || score === 0) return;

      try {
        await window.FunBookiesDB.saveActivity({
          studentId: currentStudent.id,
          type: 'activity-name',        // Unique activity identifier
          level: currentLevel,          // Current difficulty level
          score: score,                 // Points earned
          total: totalPossible,         // Max possible points
          duration: Math.round((Date.now() - sessionStartTime) / 1000),
          details: {
            // Activity-specific data
          }
        });
      } catch (e) {
        console.error('Failed to save activity:', e);
        Toast.error('Could not save progress. Please try again.');
      }
    }

    // Save on page unload
    window.addEventListener('beforeunload', () => {
      if (currentStudent && score > 0) {
        saveActivity();
      }
    });

    // Activity logic...
    function startGame() {
      // Initialize game
    }
  </script>
</body>
</html>
```

## Required Components

### 1. Student Picker

Always show the student picker at activity start:

```javascript
const picker = new StudentPicker({
  title: 'Who is practicing today?',  // Custom prompt
  allowSkip: true                      // Allow anonymous play
});
const student = await picker.show();

// student = { id, name, avatar } or null if skipped
```

### 2. Activity Tracking

Save activity results to IndexedDB:

```javascript
await window.FunBookiesDB.saveActivity({
  studentId: currentStudent.id,  // Required
  type: 'activity-slug',         // Required: unique identifier
  level: 'B3',                   // Optional: difficulty level
  score: 8,                      // Required: points earned
  total: 10,                     // Required: max possible
  duration: 120,                 // Optional: seconds played
  details: {                     // Optional: activity-specific data
    wordsCompleted: ['cat', 'dog'],
    mistakes: 2
  }
});
```

**Activity Types** (use consistent naming):
- `blend-it`
- `chop-it-up`
- `sight-words`
- `word-builder`
- `phonics-assessment`
- etc.

### 3. Audio Playback

Use AudioUtils for consistent audio:

```javascript
// Play a letter sound (preloaded, fast)
await AudioUtils.playLetterSound('a');

// Play any sound (letters, phonemes, with TTS fallback)
await AudioUtils.playSound('sh');
await AudioUtils.playSound('th');

// Speak text via TTS
await AudioUtils.speakTTS('Great job!');

// Speak a word
await AudioUtils.speakWord('cat');
```

### 4. Toast Notifications

Provide user feedback:

```javascript
Toast.show('Keep going!');              // Info (3s)
Toast.success('Correct!');              // Green (3s)
Toast.warning('Try again');             // Yellow (3s)
Toast.error('Could not save', 5000);    // Red (5s)
```

### 5. Level Selection (Optional)

For activities with multiple difficulty levels:

```html
<div class="level-select">
  <button class="chip active" data-level="B1">B1</button>
  <button class="chip" data-level="B2">B2</button>
  <button class="chip" data-level="B3">B3</button>
</div>
```

```javascript
// Save current progress before switching levels
document.querySelectorAll('.chip').forEach(btn => {
  btn.addEventListener('click', async () => {
    if (score > 0) {
      await saveActivity();
      score = 0;
      sessionStartTime = Date.now();
    }

    document.querySelector('.chip.active').classList.remove('active');
    btn.classList.add('active');
    currentLevel = btn.dataset.level;
    startGame();
  });
});
```

## Styling

### CSS Variables (from shared.css)

```css
/* Colors */
--color-sage: #8BC49E;
--color-sage-light: #E8F5EC;
--color-sage-dark: #5A9B6B;
--color-cream: #FDF8F3;
--color-charcoal: #2D3748;
--color-text-muted: #718096;
--color-border: #E2E8F0;

/* Spacing */
--space-xs: 4px;
--space-sm: 8px;
--space-md: 16px;
--space-lg: 24px;
--space-xl: 32px;

/* Typography */
--font-body: 'DM Sans', sans-serif;
--font-display: 'Fraunces', serif;

/* Border radius */
--border-radius-sm: 4px;
--border-radius-md: 8px;
--border-radius-lg: 12px;
--border-radius-xl: 16px;
```

### Common Classes

```css
.container-narrow   /* Max-width container */
.game-card          /* White card with shadow */
.btn                /* Base button */
.btn-primary        /* Sage green button */
.btn-lg             /* Large button */
.chip               /* Small rounded button */
.chip.active        /* Selected chip */
.hidden             /* display: none */
.student-badge      /* Student name display */
```

## Accessibility Checklist

- [ ] All buttons have `aria-label` if icon-only
- [ ] Interactive elements work with keyboard (Tab, Enter, Space)
- [ ] Focus states are visible (handled by shared.css)
- [ ] Color is not the only indicator (add text/icons)
- [ ] Audio has visual feedback too
- [ ] Animations respect `prefers-reduced-motion`

## Testing Checklist

Before submitting a new activity:

- [ ] Student picker shows and works
- [ ] Activity plays correctly at all levels
- [ ] Progress saves to IndexedDB (check DevTools > Application > IndexedDB)
- [ ] Toast shows on save failure
- [ ] Audio plays correctly
- [ ] Responsive on mobile (320px+)
- [ ] Back button returns to activity hub
- [ ] No console errors

## File Location

Save new activities to:
```
public/activities/your-activity-name.html
```

Add to the activity index at:
```
public/activities/index.html
```

## Example Activities

Reference these for patterns:

| Activity | Key Features |
|----------|--------------|
| `blend-it.html` | Sound segmentation, level selection |
| `sight-words.html` | Adaptive difficulty, band progression |
| `phonics-assessment.html` | Comprehensive assessment, level placement |
| `word-builder.html` | Drag-and-drop letters |
| `chop-it-up.html` | Word segmentation with visuals |

## Common Patterns

### Shuffle Array (Fisher-Yates)

```javascript
function shuffle(arr) {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}
```

### Word Lists by Level

```javascript
const wordsByLevel = {
  'B1': ['cat', 'hat', 'mat', 'sat'],
  'B2': ['dog', 'log', 'fog', 'jog'],
  'B3': ['ship', 'chip', 'shop', 'chop'],
};

function getWordsForLevel(level) {
  return wordsByLevel[level] || wordsByLevel['B1'];
}
```

### Progress Tracking

```javascript
let correct = 0;
let total = 0;

function recordAnswer(isCorrect) {
  total++;
  if (isCorrect) correct++;
  updateScoreDisplay();
}

function getAccuracy() {
  return total > 0 ? Math.round((correct / total) * 100) : 0;
}
```

### Auto-Advance Level

```javascript
// Move up after 5 correct in a row
let streak = 0;

function onCorrect() {
  streak++;
  if (streak >= 5) {
    advanceLevel();
    streak = 0;
  }
}

function onIncorrect() {
  streak = 0;
}
```
