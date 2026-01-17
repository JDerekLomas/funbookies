# FunBookies System Overview

This document describes how the FunBookies system is organized and how the different parts work together.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐ │
│  │  Reader  │  │Activities│  │Dashboard │  │  Author Tools    │ │
│  │reader.html│ │27 games  │  │dashboard │  │generate-story.html│
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────────┬─────────┘ │
│       │             │             │                  │          │
│       └─────────────┴──────┬──────┴──────────────────┘          │
│                            │                                     │
│                    ┌───────┴───────┐                            │
│                    │  Shared JS    │                            │
│                    │ data-service  │                            │
│                    │ student-picker│                            │
│                    │ audio-utils   │                            │
│                    │ toast         │                            │
│                    └───────┬───────┘                            │
└────────────────────────────┼────────────────────────────────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
      ┌───────┴───────┐            ┌────────┴────────┐
      │   IndexedDB   │            │  Vercel API     │
      │ (local data)  │            │  (serverless)   │
      │               │            │                 │
      │ - students    │            │ - generate-*    │
      │ - assessments │            │ - save-book     │
      │ - activities  │            │ - validate-text │
      │ - settings    │            │ - upload-image  │
      └───────────────┘            └────────┬────────┘
                                            │
                              ┌─────────────┴─────────────┐
                              │      External APIs        │
                              │ - Anthropic (Claude)      │
                              │ - OpenAI (TTS)            │
                              │ - fal.ai (images)         │
                              │ - ElevenLabs (phonemes)   │
                              └───────────────────────────┘
```

## Directory Structure

```
lilbookies/
├── public/                    # Static frontend (deployed to Vercel)
│   ├── index.html            # Landing page
│   ├── reader.html           # Book reader with edit mode
│   ├── dashboard.html        # Student progress dashboard
│   ├── generate-story.html   # Story creation tool
│   │
│   ├── activities/           # 27 phonics activities
│   │   ├── index.html        # Activity hub
│   │   ├── blend-it.html     # Sound blending
│   │   ├── sight-words.html  # Sight word practice
│   │   ├── phonics-assessment.html
│   │   └── ...
│   │
│   ├── js/                   # Shared JavaScript
│   │   ├── data-service.js   # IndexedDB wrapper (FunBookiesDB)
│   │   ├── student-picker.js # Student selection modal
│   │   ├── audio-utils.js    # Audio playback utilities
│   │   └── toast.js          # Toast notifications
│   │
│   ├── styles/               # Shared CSS
│   │   └── shared.css        # Common styles, variables
│   │
│   ├── books/                # Book content
│   │   ├── *.json            # Book definitions
│   │   ├── references/       # Style reference images (9-panel)
│   │   └── images/           # Generated page images
│   │
│   ├── images/
│   │   └── covers/           # Book cover images
│   │
│   └── audio/                # Audio assets
│       ├── phonemes/         # Phoneme sounds (ElevenLabs)
│       ├── instructions/     # Activity instructions (OpenAI)
│       └── coaching/         # Coaching audio
│
├── api/                      # Vercel serverless functions
│   ├── generate-story.js     # Story generation (Claude)
│   ├── generate-image.js     # Image generation (fal.ai)
│   ├── save-book.js          # Save book to GitHub
│   ├── validate-text.js      # Text validation
│   └── ...
│
├── scripts/                  # Python CLI tools
│   ├── generate_covers.py    # Generate book covers
│   ├── generate_page_images.py
│   ├── generate_references.py
│   ├── generate_phoneme_sounds.py
│   ├── fal_client.py         # fal.ai API wrapper
│   └── image_utils.py        # Shared image utilities
│
└── docs/                     # Planning & research
```

## Data Flow

### Student Progress

```
Activity Completion
        │
        ▼
┌─────────────────┐
│ FunBookiesDB    │
│ .saveActivity() │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   IndexedDB     │
│ 'activities'    │
│   store         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Dashboard     │
│ getStudentSummary()
└─────────────────┘
```

### Book Creation

```
Author enters concept
        │
        ▼
┌─────────────────┐     ┌─────────────┐
│ /api/           │────▶│   Claude    │
│ generate-story  │     │   API       │
└────────┬────────┘     └─────────────┘
         │
         ▼
   Book JSON created
         │
         ▼
┌─────────────────┐     ┌─────────────┐
│ scripts/        │────▶│   fal.ai    │
│ generate_       │     │ (wan2.6)    │
│ references.py   │     └─────────────┘
└────────┬────────┘
         │
         ▼
   Reference image (9-panel style guide)
         │
         ▼
┌─────────────────┐     ┌─────────────┐
│ scripts/        │────▶│   fal.ai    │
│ generate_       │     │ (wan2.6 I2I)│
│ page_images.py  │     └─────────────┘
└────────┬────────┘
         │
         ▼
   Page images with consistent style
```

## Key Components

### FunBookiesDB (data-service.js)

The central data layer. Stores all local data in IndexedDB.

```javascript
// Students
await FunBookiesDB.addStudent({ name, avatar })
await FunBookiesDB.getStudents()
await FunBookiesDB.getStudent(id)

// Assessments
await FunBookiesDB.saveAssessment({ studentId, level, ... })
await FunBookiesDB.getLatestAssessment(studentId)
await FunBookiesDB.getCurrentLevel(studentId)

// Activities
await FunBookiesDB.saveActivity({ studentId, type, score, ... })
await FunBookiesDB.getActivities(studentId, { type, since })

// Settings (key-value store)
await FunBookiesDB.setSetting(key, value)
await FunBookiesDB.getSetting(key)
```

### StudentPicker (student-picker.js)

Modal for selecting which student is using an activity.

```javascript
const picker = new StudentPicker({
  title: 'Who is practicing?',
  allowSkip: true
});
const student = await picker.show();
// student = { id, name, avatar } or null if skipped
```

### AudioUtils (audio-utils.js)

Handles audio playback with fallbacks.

```javascript
// Play letter sound (preloaded)
await AudioUtils.playLetterSound('a');

// Play any sound with TTS fallback
await AudioUtils.playSound('sh');

// Speak text via TTS
await AudioUtils.speakTTS('Hello');
```

### Toast (toast.js)

User notifications.

```javascript
Toast.show('Info message');
Toast.success('Great job!');
Toast.warning('Check your answer');
Toast.error('Could not save progress');
```

## Book JSON Schema

Books are stored as JSON files in `/public/books/`:

```json
{
  "slug": "book-name",
  "title": "Book Title",
  "level": "B3",
  "summary": "Brief description",

  "story_bible": {
    "visual_style": "Soft watercolor...",
    "characters": {
      "pip": {
        "description": "A small brown mouse",
        "visual_tags": ["brown fur", "pink nose"]
      }
    }
  },

  "pages": [
    {
      "page": 1,
      "type": "cover",
      "text": "",
      "scene": "Scene description for image generation",
      "image": "images/book-name/page01.png"
    },
    {
      "page": 2,
      "text": "Page text shown to reader",
      "scene": "Visual scene description",
      "image": "images/book-name/page02.png"
    }
  ]
}
```

## Environment Variables

```bash
# AI APIs
ANTHROPIC_API_KEY=    # Claude for story generation
OPENAI_API_KEY=       # TTS for audio
FAL_KEY=              # fal.ai for images
ELEVENLABS_API_KEY=   # ElevenLabs for phonemes

# GitHub (for save-book API)
GITHUB_TOKEN=
GITHUB_REPO=
```

## URLs

| URL | Purpose |
|-----|---------|
| `/` | Landing page |
| `/activities/` | Activity hub |
| `/activities/phonics-assessment.html` | Level placement |
| `/reader.html?book=slug` | Read a book |
| `/reader.html?book=slug&mode=edit` | Edit book images |
| `/dashboard.html` | Student progress |
| `/generate-story.html` | Create new book |

## Development

```bash
# Start local server
python -m http.server 8080 --directory public

# Or with Vercel CLI (includes API routes)
vercel dev

# Generate book assets
uv run python scripts/generate_references.py --book slug
uv run python scripts/generate_page_images.py slug
uv run python scripts/generate_covers.py --book slug
```

## See Also

- `CLAUDE.md` - Instructions for AI assistants
- `IMAGE_GENERATION_WORKFLOW.md` - Detailed image pipeline
- `PHONICS_ROADMAP.md` - Curriculum structure
- `BOOK_GENERATION_GUIDE.md` - Book creation process
