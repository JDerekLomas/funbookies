# Funbookies

A children's reading app with decodable books, phonics assessments, and practice activities for beginning readers ages 5-7.

**Live at: [funbookies.com](https://funbookies.com)**

## Features

### Decodable Books
9 illustrated books progressing from simple CVC words to multi-syllable words:

| Level | Book | Skills |
|-------|------|--------|
| 0 Pink | No, No, Dog! | Pre-reader |
| 1 Yellow | Pig in Mud | Short vowels |
| 2 Orange | Gus and the Volcano | CVC words |
| 3 Orange | Rats in the Castle | CVC + Digraphs |
| 4 Red | Stomp! Elephant | Ending blends |
| 5 Purple | The Cake Mistake | Digraphs |
| 6 Blue | The Sneaky Snail | Silent e |
| 7 Green | The Owl at Night | Vowel teams |
| 8 Gold | Mouse in the House | R-controlled |

### Practice Activities
- **Phonics Assessment** - Adaptive word reading that adjusts to skill level
- **Sight Words** - Flashcard practice with Dolch and Fry word lists
- **Word Builder** - Drag letter tiles to build CVC words
- **Rhyme Match** - Match words by word families
- **Blend It** - Sound out and blend words
- **Story Generator** - AI-powered custom stories based on reading level

## Project Structure

```
lilbookies/
├── public/
│   ├── index.html          # Main landing page
│   ├── generate-story.html # AI story generator
│   ├── activities/         # Practice games
│   │   ├── index.html
│   │   ├── phonics-assessment.html
│   │   ├── sight-words.html
│   │   ├── word-builder.html
│   │   ├── rhyme-match.html
│   │   ├── blend-it.html
│   │   └── ...
│   ├── books/              # Book content
│   │   ├── index.html      # Book library
│   │   ├── images/         # Book illustrations
│   │   ├── *_preview.html  # Full book previews
│   │   └── *.json          # Book data
│   └── images/             # Site images
├── api/
│   └── generate-story.js   # Claude API endpoint
└── vercel.json             # Deployment config
```

## Development

### Local Development
```bash
# Serve locally (any static server works)
npx serve public
```

### Deployment
Deployed on Vercel. Push to main to deploy automatically.

```bash
vercel --prod
```

### Environment Variables
Set in Vercel dashboard:
- `ANTHROPIC_API_KEY` - For AI story generation

## Tech Stack
- Vanilla HTML/CSS/JavaScript
- Vercel serverless functions
- Claude API for story generation

## License
All rights reserved.
