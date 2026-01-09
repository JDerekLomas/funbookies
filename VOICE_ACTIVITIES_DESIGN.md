# Voice-Based Phonics Activities Design

## Research Summary

### Top Exemplars Analyzed

| App | Key Voice Features | What Makes It Work |
|-----|-------------------|-------------------|
| [Readability Tutor](https://www.readabilitytutor.com/) | AI listens to reading aloud, real-time correction, voice Q&A | Adapts to child's voice, gentle corrections, tracks WCPM |
| [Phonics, Reading & Me](https://www.lwtears.com/solutions/reading/phonics-reading-and-me) | Voice engine assesses oral reading, targeted interventions | Johns Hopkins validated, identifies skill gaps |
| [Google Read Along](https://readalong.google.com/) | Speech recognition, Diya assistant encourages | Free, offline capable, gamified |
| [Microsoft Reading Coach](https://education.microsoft.com/en-us/resource/6e1cd8db) | Fluency practice, pronunciation feedback | Integrated with Teams/Immersive Reader |

### Key Patterns from Winners

1. **Listen & Respond**: App listens to child read aloud, provides immediate feedback
2. **Gentle Correction**: Never harsh - "Let's try that again" not "Wrong!"
3. **Phoneme-Level Precision**: Can hear individual sounds, not just words
4. **Adaptive Difficulty**: Adjusts based on performance in real-time
5. **Voice Q&A**: Child answers questions verbally, not just tapping
6. **Encouragement Loop**: Frequent praise, celebrations, streak rewards

---

## Proposed Voice Activities for FunBookies

### Activity 1: "Say the Sound" (Phoneme Recognition)

**Concept**: App shows a letter/digraph, child says the sound aloud.

```
┌─────────────────────────────────────┐
│         Say the Sound!              │
│                                     │
│            ┌─────┐                  │
│            │  sh │                  │
│            └─────┘                  │
│                                     │
│     🎤 "What sound does this make?" │
│                                     │
│         [Tap to listen]             │
│         [🎙️ Record answer]          │
│                                     │
│     ✓ Correct! That's /sh/!         │
└─────────────────────────────────────┘
```

**Flow**:
1. Show letter(s) on screen
2. Play prompt: "What sound does this make?"
3. Child taps mic and says the sound
4. App recognizes phoneme and gives feedback
5. If wrong: "Almost! Listen: /sh/. Now you try."

**Levels**:
- A-Band: Single letters (s, a, t, p, i, n)
- B-Band: Digraphs (sh, ch, th, wh), blends (bl, cr, st)
- C-Band: Complex patterns (tion, ough, ight)

---

### Activity 2: "Blend It Out" (Oral Blending)

**Concept**: App says segmented sounds, child blends and says the word.

```
┌─────────────────────────────────────┐
│         Blend It Out!               │
│                                     │
│            🔊                       │
│       "/c/  /a/  /t/"               │
│                                     │
│     🎤 "What word is that?"         │
│                                     │
│         [🔊 Hear again]             │
│         [🎙️ Say the word]           │
│                                     │
│     🎉 Yes! CAT!                    │
│         ⭐⭐⭐                       │
└─────────────────────────────────────┘
```

**Flow**:
1. App speaks sounds slowly: "/c/ ... /a/ ... /t/"
2. Child blends mentally and says the word
3. App recognizes "cat" and celebrates
4. Progress to faster blending as skill improves

**Progression**:
- Start with 2-phoneme words (at, up, go)
- Move to 3-phoneme CVC (cat, dog, sit)
- Then blends (stop, frog) and digraphs (ship, chat)

---

### Activity 3: "Chop It Up" (Oral Segmenting)

**Concept**: App says a word, child segments it into sounds.

```
┌─────────────────────────────────────┐
│         Chop It Up!                 │
│                                     │
│            🐸                       │
│         "FROG"                      │
│                                     │
│     🎤 "Say each sound you hear"    │
│                                     │
│     ┌───┐ ┌───┐ ┌───┐ ┌───┐        │
│     │ ? │ │ ? │ │ ? │ │ ? │        │
│     └───┘ └───┘ └───┘ └───┘        │
│                                     │
│         [🎙️ Chop the word]          │
└─────────────────────────────────────┘
```

**Flow**:
1. Show picture + hear word "frog"
2. Child says: "/f/ /r/ /o/ /g/"
3. App fills in boxes as each phoneme is recognized
4. Celebrate when all sounds identified

**Scaffolding**:
- Beginner: Boxes show how many sounds to find
- Advanced: No boxes, child determines count
- Expert: Multi-syllable words

---

### Activity 4: "Read Aloud" (Fluency Practice)

**Concept**: Child reads a sentence/passage, app tracks accuracy and fluency.

```
┌─────────────────────────────────────┐
│         Read Aloud                  │
│                                     │
│  ┌─────────────────────────────┐    │
│  │ The cat sat on the mat.    │    │
│  │      ▲                      │    │
│  │   (current word)            │    │
│  └─────────────────────────────┘    │
│                                     │
│     🎙️ Recording...                 │
│     ━━━━━━━━━━━━━━━━━━━━━━━━━━     │
│                                     │
│     Words correct: 5/6              │
│     Let's practice: "mat"           │
└─────────────────────────────────────┘
```

**Flow**:
1. Display sentence from current level book
2. Highlight words as child reads
3. Track words per minute, accuracy
4. Flag mispronounced words for review
5. Offer to practice difficult words

**Metrics Tracked**:
- Words Correct Per Minute (WCPM)
- Accuracy percentage
- Specific error patterns (vowels, blends, etc.)

---

### Activity 5: "Sound Swap" (Phoneme Manipulation)

**Concept**: Change one sound to make a new word.

```
┌─────────────────────────────────────┐
│         Sound Swap                  │
│                                     │
│            CAT                      │
│                                     │
│     🎤 "Change /c/ to /b/"          │
│        "What's the new word?"       │
│                                     │
│         [🎙️ Say it]                 │
│                                     │
│     ✓ BAT! Great job!               │
│                                     │
│     Now change /a/ to /i/...        │
└─────────────────────────────────────┘
```

**Flow**:
1. Start with a word: "cat"
2. Prompt: "Change the /c/ to /b/. What word?"
3. Child says "bat"
4. Chain continues: bat → bit → sit → sat...

**Why It Matters**:
This is advanced phonemic awareness - manipulating sounds mentally. Strong predictor of reading success.

---

### Activity 6: "Word Detective" (Listening Comprehension)

**Concept**: Listen to a short passage, answer questions verbally.

```
┌─────────────────────────────────────┐
│         Word Detective              │
│                                     │
│     🔊 Playing story...             │
│     ━━━━━━━━━━━━━━━━━━━━━━━━━━     │
│                                     │
│     "The frog jumped in the pond.   │
│      He saw a big fish swim by."    │
│                                     │
│     🎤 "Where did the frog jump?"   │
│                                     │
│         [🎙️ Answer]                 │
│                                     │
│     ✓ That's right - the pond!      │
└─────────────────────────────────────┘
```

**Flow**:
1. Play short audio passage (from current level)
2. Ask comprehension question verbally
3. Child answers verbally
4. App recognizes key words in answer
5. Follow-up questions build deeper understanding

---

## Technical Requirements

### Speech Recognition

**Option 1: Web Speech API** (Browser native)
- Pros: Free, no API costs, works offline
- Cons: Accuracy varies, not optimized for children

**Option 2: OpenAI Whisper API**
- Pros: High accuracy, handles accents well
- Cons: Cost per request, requires internet

**Option 3: KeenASR (Children-optimized)**
- Pros: Trained on children's voices, phoneme-level
- Cons: Commercial license, integration complexity

**Recommendation**: Start with Web Speech API for MVP, plan migration to Whisper or specialized ASR for production.

### Phoneme Recognition Challenge

Standard speech recognition gives words, not phonemes. Solutions:
1. **Phoneme mapping**: When child says "/sh/", map to potential words containing that sound
2. **Context-aware**: If showing "sh", expect sounds like "shh" or words starting with sh-
3. **Fuzzy matching**: Accept close approximations, especially for young children

### Audio Feedback

All activities need:
- Clear voice prompts (pre-recorded or TTS)
- Celebration sounds for correct answers
- Gentle "try again" sounds for errors
- Background music option (toggleable)

---

## Implementation Priority

### Phase 1: MVP (Voice Input Foundation)
1. **"Read Aloud"** - Most impactful, validates speech recognition
2. **"Blend It Out"** - Simple to implement, high learning value

### Phase 2: Core Phonics
3. **"Say the Sound"** - Phoneme recognition
4. **"Chop It Up"** - Segmenting practice

### Phase 3: Advanced
5. **"Sound Swap"** - Manipulation (hardest to implement)
6. **"Word Detective"** - Comprehension

---

## UI/UX Principles

1. **Big Mic Button**: Obvious, friendly, one tap to record
2. **Visual Feedback**: Waveform while recording, checkmarks on success
3. **Patience**: Wait for child to respond, don't rush
4. **Encouragement**: Celebrate every attempt, not just correct answers
5. **Parent Mode**: Toggle to see detailed progress, adjust difficulty
6. **Offline Support**: Cache audio prompts, work without internet when possible

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Session completion rate | >80% |
| Average session duration | 5-10 minutes |
| Return rate (next day) | >60% |
| Phoneme recognition accuracy | >85% |
| Parent satisfaction (NPS) | >50 |

---

## Sources

- [Readability Tutor - AI Reading App](https://www.readabilitytutor.com/)
- [Phonics, Reading & Me - Learning Without Tears](https://www.lwtears.com/solutions/reading/phonics-reading-and-me)
- [Reading Rockets - Blending and Segmenting Games](https://www.readingrockets.org/classroom/classroom-strategies/blending-and-segmenting-games)
- [95 Percent Group - Phonemic Awareness Activities](https://www.95percentgroup.com/insights/phonemic-awareness-activities/)
- [The Learning Agency - Speech Recognition Technology](https://the-learning-agency.com/the-cutting-ed/article/teaching-kids-to-read-with-speech-recognition-technology/)
- [UFLI - Phonemic Awareness Resources](https://ufli.education.ufl.edu/resources/teaching-resources/instructional-activities/phonemic-awareness/)
- [KeenASR - Children's Speech Recognition](https://keenresearch.com/keenasr-use-cases-edtech-and-kids-speech-recognition.html)

---

*Document created 2026-01-09 based on competitive analysis and Science of Reading research.*
