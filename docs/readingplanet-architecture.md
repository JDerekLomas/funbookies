# ReadingPlanet Architecture

## Overview

ReadingPlanet is a digital reading intervention platform for struggling readers in grades 4-10. It bridges the gap between FunBookies (early readers) and grade-level reading, with a focus on age-appropriate content, student choice, and measurable growth.

**Target Users:**
- Students reading 1-4 years below grade level
- Ages 9-16 (grades 4-10)
- Schools, tutors, and homeschool families

**Core Philosophy:**
- Respect student maturity (no "baby" content)
- Choice drives engagement
- Discussion deepens comprehension
- Progress should be visible and celebrated
- Foundational gaps are addressed without stigma

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        ReadingPlanet                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Student    │  │   Teacher    │  │    Parent    │          │
│  │   Portal     │  │  Dashboard   │  │   Reports    │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                 │                 │                   │
│  ┌──────┴─────────────────┴─────────────────┴───────┐          │
│  │                   Core Platform                   │          │
│  ├───────────────────────────────────────────────────┤          │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ │          │
│  │  │ Reader  │ │ Writing │ │ Vocab   │ │ Fluency │ │          │
│  │  │ Engine  │ │ Studio  │ │ Builder │ │ Tracker │ │          │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘ │          │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ │          │
│  │  │Discussion│ │ Skills  │ │Progress │ │ Library │ │          │
│  │  │ Prompts │ │ Practice│ │ Engine  │ │ Manager │ │          │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘ │          │
│  └───────────────────────────────────────────────────┘          │
│                            │                                    │
│  ┌─────────────────────────┴─────────────────────────┐          │
│  │                   Data Layer                       │          │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ │          │
│  │  │ Student │ │ Reading │ │ Content │ │Analytics│ │          │
│  │  │ Profiles│ │ History │ │  Store  │ │  Events │ │          │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘ │          │
│  └───────────────────────────────────────────────────┘          │
│                            │                                    │
│  ┌─────────────────────────┴─────────────────────────┐          │
│  │              External Integrations                 │          │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ │          │
│  │  │FunBookies│ │   AI    │ │  TTS/   │ │  LMS    │ │          │
│  │  │ Bridge  │ │ Feedback│ │  STT    │ │  APIs   │ │          │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘ │          │
│  └───────────────────────────────────────────────────┘          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Core Modules

### 1. Reader Engine
The primary reading interface with adaptive features.

```
/reader/
├── text-display/        # Render text with annotations
│   ├── highlight        # Student highlighting
│   ├── notes            # Margin notes
│   ├── dictionary       # Tap-to-define
│   └── translate        # Multi-language support
├── audio/
│   ├── tts              # Text-to-speech (adjustable speed)
│   ├── read-along       # Highlight words as read
│   └── pronunciation    # Word-level playback
├── comprehension/
│   ├── check-ins        # Periodic questions during reading
│   ├── annotations      # Teacher-placed discussion points
│   └── summary-prompt   # End-of-section summaries
└── tracking/
    ├── time-on-page     # Engagement metrics
    ├── words-read       # Volume tracking
    └── comprehension    # Accuracy on check-ins
```

**Key Features:**
- Clean, distraction-free reading view
- Adjustable font size, spacing, contrast
- Audio support for struggling decoders
- Built-in dictionary (visual + audio)
- Annotation tools (highlight, note, bookmark)
- Comprehension check-ins every 200-300 words

### 2. Writing Studio
AI-powered writing practice with instant feedback.

```
/writing/
├── prompts/
│   ├── summary          # Summarize what you read
│   ├── response         # Respond to a question
│   ├── creative         # Creative writing from prompts
│   └── argument         # Take a position and defend
├── scaffolds/
│   ├── sentence-starters
│   ├── paragraph-frames
│   └── graphic-organizers
├── feedback/
│   ├── ai-scoring       # Instant feedback on drafts
│   ├── revision-tips    # Specific improvement suggestions
│   └── rubric-view      # See how you'll be graded
└── portfolio/
    ├── drafts           # Work in progress
    ├── published        # Final submissions
    └── growth-view      # Compare early vs. recent work
```

**AI Feedback Focus Areas:**
- Main idea present?
- Text evidence used?
- Clear organization?
- Complete sentences?
- Spelling/grammar issues?

### 3. Vocabulary Builder
Contextual vocabulary instruction.

```
/vocabulary/
├── pre-reading/         # Words to know before reading
│   ├── visual-intro     # Image + definition + audio
│   ├── context-sentence # See it in use
│   └── quick-check      # Can you use it?
├── in-context/          # During reading
│   ├── tap-to-define    # Instant lookup
│   ├── word-bank        # Collected words
│   └── morphology       # Word parts (prefix, root, suffix)
├── practice/
│   ├── flashcards       # Spaced repetition
│   ├── context-match    # Match word to sentence
│   ├── word-relationships # Synonyms, antonyms, categories
│   └── use-it           # Write your own sentence
└── tracking/
    ├── words-learned    # Mastery count
    ├── review-queue     # Due for review
    └── word-map         # Visual vocabulary growth
```

### 4. Fluency Tracker
Voice-based fluency measurement and practice.

```
/fluency/
├── assessment/
│   ├── timed-reading    # 1-minute read
│   ├── wcpm-calc        # Words correct per minute
│   ├── error-marking    # Track miscues
│   └── prosody-score    # Expression rating
├── practice/
│   ├── repeated-reading # Same passage multiple times
│   ├── paired-reading   # Read with audio model
│   ├── phrase-practice  # Chunked text practice
│   └── reader-theater   # Scripts for expression
├── passages/
│   ├── leveled          # Multiple levels per topic
│   ├── topic-linked     # Match current reading
│   └── high-interest    # Engaging standalone
└── progress/
    ├── wcpm-chart       # Growth over time
    ├── goal-tracking    # Target WCPM
    └── celebration      # Milestones achieved
```

### 5. Skills Practice
Foundational skills for students with gaps.

```
/skills/
├── phonics/             # For students with decoding gaps
│   ├── multisyllable    # Breaking long words
│   ├── vowel-patterns   # Advanced vowel teams
│   ├── morphology       # Prefixes, suffixes, roots
│   └── irregular-words  # Exception words
├── comprehension/
│   ├── main-idea        # Identify central ideas
│   ├── inference        # Read between lines
│   ├── text-structure   # How texts are organized
│   ├── author-purpose   # Why was this written?
│   └── perspective      # Point of view
├── grammar/
│   ├── sentence-types   # Simple to complex
│   ├── punctuation      # Meaning from marks
│   └── syntax           # Sentence structure
└── adaptive/
    ├── diagnostic       # Find skill gaps
    ├── pathway          # Personalized sequence
    └── mastery-check    # Ready to move on?
```

**FunBookies Bridge:**
Students with severe phonics gaps can be routed to FunBookies activities:
- Letter Sounds → Early Reader Pathway
- Word Families → Word Builder
- Blending → Voice Blend

### 6. Discussion Prompts
Social learning features for classroom use.

```
/discussion/
├── prompts/
│   ├── text-based       # What did the author mean by...?
│   ├── opinion          # Do you agree that...?
│   ├── connection       # How does this relate to...?
│   └── debate           # Argue for/against...
├── formats/
│   ├── pair-share       # Partner discussion
│   ├── small-group      # 3-4 students
│   ├── whole-class      # Teacher-led
│   └── written          # Discussion board
├── scaffolds/
│   ├── sentence-frames  # "I think... because..."
│   ├── evidence-finder  # Highlight text support
│   └── respectful-disagreement # "I see it differently..."
└── teacher-tools/
    ├── assign-prompts   # Push to students
    ├── monitor          # See responses
    └── highlight        # Feature great responses
```

---

## Content Library

### Text Organization

```
/library/
├── genres/
│   ├── realistic-fiction    # Contemporary life
│   ├── mystery              # Puzzles and suspense
│   ├── fantasy              # Other worlds
│   ├── sci-fi               # Future and technology
│   ├── historical           # Past eras
│   ├── biography            # Real people
│   ├── sports               # Athletic stories
│   ├── horror               # Age-appropriate scary
│   └── graphic              # Visual storytelling
├── topics/                  # Nonfiction
│   ├── science              # Nature, space, biology
│   ├── history              # Events, eras, movements
│   ├── current-events       # News and issues
│   ├── technology           # Innovation, digital
│   ├── social-issues        # Identity, justice
│   ├── careers              # Jobs, futures
│   └── how-to               # Practical skills
├── formats/
│   ├── novels               # Full books (excerpts + full)
│   ├── articles             # 500-1500 words
│   ├── passages             # 100-500 words (fluency)
│   └── multimedia           # Text + video/audio
└── levels/
    ├── lexile               # Quantitative measure
    ├── grade-equivalent     # 3rd, 4th, etc.
    └── interest-level       # Age appropriateness
```

### Content Metadata

```javascript
{
  id: "txt_001",
  title: "The Outsiders",
  author: "S.E. Hinton",
  type: "novel",
  genre: ["realistic-fiction"],
  themes: ["identity", "class", "belonging", "violence"],

  // Reading levels
  lexile: 750,
  gradeLevel: 5.8,
  interestLevel: "6-12",  // Age appropriate for

  // Content info
  wordCount: 48523,
  estimatedTime: 240,  // minutes
  hasAudio: true,
  hasTranslation: ["es", "zh", "vi"],

  // Curriculum links
  vocabulary: ["rivalry", "tension", "hood", "greaser"],
  skills: ["inference", "character-analysis", "theme"],
  discussionPrompts: ["prompt_001", "prompt_002"],
  writingPrompts: ["write_001"],

  // Engagement
  rating: 4.6,
  reviewCount: 1247,
  tags: ["classic", "movie-adaptation", "quick-read"],

  // Content warnings (for teachers/parents)
  warnings: ["violence", "death", "smoking"],

  // Related content
  relatedTexts: ["txt_015", "txt_023"],
  fluencyPassages: ["flu_012", "flu_013", "flu_014"]
}
```

---

## Student Data Model

```javascript
// Student Profile
{
  id: "stu_12345",
  name: "Marcus",
  avatar: "astronaut",
  gradeLevel: 7,

  // Assessment data
  currentLexile: 680,
  targetLexile: 900,  // Grade level
  initialLexile: 520, // At enrollment

  wcpm: {
    current: 112,
    target: 150,
    history: [/* weekly measurements */]
  },

  // Skills profile
  skills: {
    decoding: { level: "proficient", lastAssessed: "2024-01-10" },
    fluency: { level: "developing", lastAssessed: "2024-01-10" },
    vocabulary: { level: "developing", lastAssessed: "2024-01-10" },
    comprehension: { level: "emerging", lastAssessed: "2024-01-10" }
  },

  // Preferences
  preferences: {
    favoriteGenres: ["mystery", "sci-fi"],
    dislikedGenres: ["romance"],
    audioSpeed: 1.0,
    fontSize: "large",
    theme: "dark"
  },

  // Progress
  progress: {
    textsCompleted: 23,
    wordsRead: 145000,
    timeSpent: 2340,  // minutes
    writingSubmissions: 18,
    vocabularyMastered: 156,
    currentStreak: 5,
    longestStreak: 12
  },

  // Current state
  currentReading: {
    textId: "txt_001",
    position: 0.34,  // 34% through
    lastRead: "2024-01-15T14:30:00Z"
  },

  // Engagement
  badges: ["first-book", "week-streak", "vocab-100"],
  goals: {
    weekly: { type: "minutes", target: 60, current: 35 },
    monthly: { type: "books", target: 2, current: 1 }
  }
}
```

---

## Daily Session Flow

### Recommended 45-Minute Structure

```
┌─────────────────────────────────────────────────────────────┐
│                    Daily Session (45 min)                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  1. WARM-UP (5 min)                                 │   │
│  │     • Welcome back + streak check                   │   │
│  │     • Quick vocabulary review (3-5 words)           │   │
│  │     • Goal reminder                                 │   │
│  └─────────────────────────────────────────────────────┘   │
│                           ↓                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  2. FLUENCY PRACTICE (5-8 min)                      │   │
│  │     • 1-minute timed reading                        │   │
│  │     • Repeated reading (if needed)                  │   │
│  │     • Track WCPM                                    │   │
│  └─────────────────────────────────────────────────────┘   │
│                           ↓                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  3. MAIN READING (20-25 min)                        │   │
│  │     • Pre-reading: vocab preview, predictions       │   │
│  │     • Reading: with check-ins every 300 words       │   │
│  │     • Post-reading: summary or discussion prompt    │   │
│  └─────────────────────────────────────────────────────┘   │
│                           ↓                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  4. SKILL PRACTICE (5-8 min)                        │   │
│  │     • Adaptive: based on skill gaps                 │   │
│  │     • Could be: vocabulary, comprehension, grammar  │   │
│  │     • Or: writing response to reading               │   │
│  └─────────────────────────────────────────────────────┘   │
│                           ↓                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  5. WRAP-UP (2-3 min)                               │   │
│  │     • Progress summary                              │   │
│  │     • XP/badge earned                               │   │
│  │     • Preview tomorrow                              │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Flexible Mode (Self-Paced)

For homework or independent use:
- **Free Reading** - Choose from library, tracked time
- **Skill Practice** - Work on assigned or self-selected skills
- **Writing** - Complete writing assignments
- **Vocabulary** - Flashcard review

---

## Gamification System

### Engagement Elements

```javascript
// XP System
const xpRewards = {
  readingMinute: 2,           // 2 XP per minute reading
  fluencyPractice: 25,        // Per session
  comprehensionCorrect: 10,   // Per question
  writingSubmitted: 50,       // Per submission
  vocabularyMastered: 15,     // Per word
  dailyLogin: 20,             // Show up bonus
  streakDay: 10,              // Per consecutive day
  bookCompleted: 100,         // Finish a book
  goalMet: 75,                // Weekly goal achieved
};

// Levels (avoid childish names)
const levels = [
  { level: 1, name: "Reader", xpRequired: 0 },
  { level: 2, name: "Explorer", xpRequired: 500 },
  { level: 3, name: "Scholar", xpRequired: 1500 },
  { level: 4, name: "Analyst", xpRequired: 3500 },
  { level: 5, name: "Critic", xpRequired: 7000 },
  { level: 6, name: "Thinker", xpRequired: 12000 },
  { level: 7, name: "Authority", xpRequired: 20000 },
  { level: 8, name: "Master", xpRequired: 35000 },
];

// Badges (achievements)
const badges = [
  // Reading milestones
  { id: "first-book", name: "First Finish", desc: "Complete your first book" },
  { id: "page-turner", name: "Page Turner", desc: "Read 10,000 words" },
  { id: "bookworm", name: "Bookworm", desc: "Read 100,000 words" },
  { id: "library-card", name: "Library Card", desc: "Read from 5 different genres" },

  // Fluency
  { id: "speed-reader", name: "Speed Reader", desc: "Reach 120 WCPM" },
  { id: "fluent", name: "Fluent", desc: "Reach 150 WCPM" },
  { id: "expression", name: "Expressive", desc: "Score 4/4 on prosody" },

  // Vocabulary
  { id: "word-collector", name: "Word Collector", desc: "Learn 50 vocabulary words" },
  { id: "linguist", name: "Linguist", desc: "Learn 200 vocabulary words" },

  // Writing
  { id: "first-draft", name: "First Draft", desc: "Submit your first writing" },
  { id: "prolific", name: "Prolific Writer", desc: "Submit 25 writing pieces" },
  { id: "revision-pro", name: "Revision Pro", desc: "Improve a draft by 20+ points" },

  // Consistency
  { id: "week-streak", name: "Week Warrior", desc: "7-day streak" },
  { id: "month-streak", name: "Monthly Master", desc: "30-day streak" },
  { id: "consistent", name: "Consistent", desc: "Meet weekly goal 4 weeks in a row" },

  // Social
  { id: "discusser", name: "Discusser", desc: "Respond to 10 discussion prompts" },
  { id: "helpful", name: "Helpful", desc: "Get 5 likes on discussion responses" },
];
```

### Anti-Gaming Measures

- XP caps per day (prevent grinding)
- Quality gates (comprehension required for reading XP)
- Decay system (streaks pause, don't reset, after 2 days)
- Rotate badges quarterly (freshness)

---

## Teacher Dashboard

### Class Overview

```
┌──────────────────────────────────────────────────────────────┐
│  Period 3 - Reading Intervention          [+ Add Student]   │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Class Averages                    This Week's Focus         │
│  ┌────────────┬────────────┐      ┌─────────────────────┐   │
│  │ Lexile     │ 645 (+23)  │      │ Main Idea           │   │
│  │ WCPM       │ 98 (+5)    │      │ 65% mastery         │   │
│  │ Time/Week  │ 42 min     │      │ [Assign Practice]   │   │
│  └────────────┴────────────┘      └─────────────────────────┘   │
│                                                              │
│  Students                          ▼ Sort by: Needs Help    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 🔴 Marcus J.    Lexile 520   WCPM 78   Inactive 5d   │   │
│  │ 🟡 Aaliyah T.   Lexile 610   WCPM 95   On track      │   │
│  │ 🟡 Devon R.     Lexile 580   WCPM 88   Needs vocab   │   │
│  │ 🟢 Sofia M.     Lexile 720   WCPM 115  Exceeding     │   │
│  │ 🟢 James K.     Lexile 690   WCPM 108  On track      │   │
│  │ ...                                                   │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  Quick Actions                                               │
│  [Assign Text] [Send Message] [Run Assessment] [Reports]    │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Individual Student View

```
┌──────────────────────────────────────────────────────────────┐
│  Marcus Johnson                    Grade 7 | Period 3        │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Reading Level                    Skills Profile             │
│  ┌─────────────────────┐         ┌─────────────────────┐    │
│  │ Start:  520 Lexile  │         │ Decoding    ████░░ │    │
│  │ Current: 680 Lexile │         │ Fluency     ███░░░ │    │
│  │ Target: 900 Lexile  │         │ Vocabulary  ██░░░░ │    │
│  │                     │         │ Comprehension █░░░░░ │    │
│  │ [=====>----] 40%    │         └─────────────────────┘    │
│  └─────────────────────┘                                     │
│                                                              │
│  WCPM Growth                      Recent Activity            │
│  ┌─────────────────────┐         ┌─────────────────────┐    │
│  │     _____           │         │ Jan 15: Read 12 min │    │
│  │    /     \          │         │ Jan 14: Vocab quiz  │    │
│  │   /       ----      │         │ Jan 12: Writing sub │    │
│  │  /                  │         │ Jan 10: No activity │    │
│  │ 78 → 95 → 102       │         └─────────────────────┘    │
│  └─────────────────────┘                                     │
│                                                              │
│  Recommendations                                             │
│  ⚠️ Inactive for 5 days - consider check-in                 │
│  📚 Below target on vocabulary - assign extra practice       │
│  💪 Fluency improving - celebrate progress!                  │
│                                                              │
│  [View Full Report] [Assign Text] [Message Parent]          │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## Technical Stack

### Frontend
```
- Framework: React or Vue 3
- State: Zustand or Pinia
- Styling: Tailwind CSS
- Reader: Custom + epub.js for books
- Audio: Web Speech API + ElevenLabs for quality TTS
- Voice: Web Speech API (recognition) + Whisper API (backup)
```

### Backend
```
- API: Node.js + Express or Python + FastAPI
- Database: PostgreSQL (main) + Redis (cache/sessions)
- Search: Elasticsearch or Meilisearch (library search)
- AI: Claude API (writing feedback, comprehension questions)
- Storage: S3/R2 (content, audio files)
- Auth: Auth0 or Clerk (SSO for schools)
```

### Data & Analytics
```
- Events: Segment or custom event pipeline
- Analytics: Mixpanel or Amplitude
- Reporting: Metabase or custom dashboards
- ML: Lexile prediction, reading recommendations
```

### Integrations
```
- LMS: Canvas, Google Classroom, Clever
- Assessment: NWEA MAP, STAR, i-Ready (import scores)
- SSO: SAML, OAuth, Clever
- FunBookies: Shared student database, progress sync
```

---

## MVP Scope

### Phase 1: Core Reading Experience
- [ ] Student authentication & profiles
- [ ] Text library (50 high-interest texts)
- [ ] Reader with annotations, dictionary, audio
- [ ] Comprehension check-ins (multiple choice)
- [ ] Basic progress tracking
- [ ] Simple teacher view (class list, time tracking)

### Phase 2: Assessment & Fluency
- [ ] Placement assessment (adaptive Lexile)
- [ ] WCPM measurement with voice recording
- [ ] Fluency passage library
- [ ] Skill gap detection
- [ ] Personalized pathway recommendations

### Phase 3: Writing & Feedback
- [ ] Writing prompts tied to reading
- [ ] AI feedback on summaries
- [ ] Revision workflow
- [ ] Writing portfolio

### Phase 4: Vocabulary & Skills
- [ ] Pre-reading vocabulary
- [ ] Spaced repetition flashcards
- [ ] Skills practice modules
- [ ] FunBookies bridge for phonics gaps

### Phase 5: Social & Gamification
- [ ] Discussion prompts & responses
- [ ] XP system & badges
- [ ] Student goals & streaks
- [ ] Leaderboards (optional, class-only)

### Phase 6: Advanced Features
- [ ] Full adaptive learning engine
- [ ] LMS integrations
- [ ] Parent portal
- [ ] Advanced analytics & predictions

---

## Content Strategy

### Initial Library (MVP)

| Category | Count | Source |
|----------|-------|--------|
| High-interest novels (excerpts) | 10 | Licensed or public domain |
| Articles (current events) | 20 | Original or licensed |
| Fluency passages (leveled) | 50 | Original |
| Short stories | 10 | Original or public domain |
| Nonfiction (science, history) | 10 | Original or licensed |

### Content Creation Priorities
1. **Fluency passages** - Need multiple levels per topic
2. **High-interest articles** - Sports, gaming, social media, music
3. **Diverse representation** - Characters/authors reflecting student population
4. **Vocabulary-controlled** - Match Lexile with intentional stretch words

---

## Success Metrics

### Student Outcomes
- Lexile growth (target: 1.5 years growth per year)
- WCPM improvement (target: 20+ words per semester)
- Time on task (target: 30+ min/day)
- Books completed (target: 1/month)

### Engagement Metrics
- Daily active users
- Session length
- Return rate (next day, next week)
- Feature usage (which tools used)

### Teacher Metrics
- Dashboard logins
- Student progress views
- Assignment creation
- Report generation

---

## Competitive Differentiation

| Feature | iLit | Newsela | ReadingPlanet |
|---------|------|---------|---------------|
| Adaptive reading level | ✓ | ✓ | ✓ |
| AI writing feedback | ✓ | ✗ | ✓ |
| Voice fluency tracking | ✗ | ✗ | ✓ |
| Discussion tools | ✓ | ✓ | ✓ |
| FunBookies phonics bridge | ✗ | ✗ | ✓ |
| Price | $$$$ | $$$ | $$ |
| Free tier | ✗ | Limited | Yes |

**Key differentiators:**
1. Voice-based fluency (from FunBookies)
2. Seamless phonics bridge for severe gaps
3. AI writing feedback at lower price
4. Clean, modern UX (not enterprise bloat)
5. Free tier for individual teachers

---

## Next Steps

1. **Validate content needs** - Survey teachers on must-have texts
2. **Build reader prototype** - Core reading experience
3. **Test fluency tracking** - Port WCPM from FunBookies
4. **AI feedback pilot** - Writing feedback with Claude
5. **Teacher interviews** - Dashboard requirements
