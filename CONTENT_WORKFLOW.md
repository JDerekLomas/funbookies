# FunBookies Content Generation Workflow

## Research-Based Framework

This workflow is grounded in:
- **Orton-Gillingham** structured literacy approach
- **Science of Reading** principles (systematic, explicit, cumulative)
- **DIBELS** assessment benchmarks
- **Lexile** text complexity measures
- **Beck/Marzano** vocabulary tiers

---

## Level-to-Standard Mapping

### Phonics Foundation (Levels 0-8) → Pre-K to Grade 2

| Level | Phonics Skill | DIBELS Measure | Lexile Range | Fry Words |
|-------|--------------|----------------|--------------|-----------|
| 0 | Pre-reader | LNF 25+ | BR | 1-25 |
| 1 | CVC (a,i,o) | PSF 43+, NWF-CLS 36+ | BR-100 | 1-50 |
| 2 | CVC (all vowels) | NWF-CLS 49+ | BR-100 | 1-75 |
| 3 | Digraphs | NWF-WRC 13+ | 100-200 | 1-100 |
| 4 | Initial blends | NWF-CLS 78+ | 100-200 | 1-150 |
| 5 | Final blends/FLOSS | NWF-CLS 87+ | 150-300 | 1-200 |
| 6 | Silent e (VCe) | WRF 29+ | 200-400 | 1-250 |
| 7 | Vowel teams | WRF 60+ | 300-500 | 1-300 |
| 8 | R-controlled | WRF 72+ | 400-600 | 1-400 |

### Transitional (Levels 9-12) → Grades 2-3

| Level | Skill | Lexile Range | Vocabulary Focus |
|-------|-------|--------------|------------------|
| 9 | Diphthongs | 450-650 | Fry 1-500 |
| 10 | Silent letters | 500-700 | Fry 1-600 |
| 11 | Soft c/g | 550-750 | Fry 1-700 |
| 12 | 2-syllable words | 600-800 | Fry 1-800 |

### Developing (Levels 13-16) → Grades 3-5

| Level | Skill | Lexile Range | Vocabulary Focus |
|-------|-------|--------------|------------------|
| 13 | 6 syllable types | 650-850 | Fry 1-900, Tier 2 intro |
| 14 | Suffixes | 700-900 | Tier 2 basic |
| 15 | Prefixes | 750-950 | Tier 2 intermediate |
| 16 | Latin roots | 850-1000 | Tier 2 + Latin morphology |

### Fluent (Levels 17-20) → Grades 5-7

| Level | Skill | Lexile Range | Vocabulary Focus |
|-------|-------|--------------|------------------|
| 17 | Greek roots | 900-1050 | Tier 2 advanced, Greek morphology |
| 18 | Academic Tier 2 | 950-1100 | Cross-curricular academic vocab |
| 19 | Complex sentences | 1000-1150 | Subordinate clauses, transitions |
| 20 | Figurative language | 1050-1200 | Idioms, metaphor, irony |

### Advanced (Levels 21-23) → Grades 7-12

| Level | Skill | Lexile Range | Vocabulary Focus |
|-------|-------|--------------|------------------|
| 21 | Domain Tier 3 | 1100-1300 | Subject-specific terminology |
| 22 | Nuanced language | 1200-1400 | Connotation, register, tone |
| 23 | Literary analysis | 1300-1600+ | Critical lenses, rhetoric |

---

## External Resources

### Word Lists & Phonics Banks

1. **[Phonics Word List Generator](https://www.phonicswordlist.com/)** - Generate custom CVC, digraph, blend, silent e, vowel team lists
2. **[Reading Universe Decodable Texts](https://readinguniverse.org/article/explore-teaching-topics/word-recognition/phonics/decodable-texts-for-each-phonics-skill)** - Free texts by phonics skill
3. **[Fry 1000 Words](https://www.k12reader.com/subject/vocabulary/fry-words/)** - High-frequency words by level
4. **[Dolch Words by Grade](https://dolchword.net/by-grade-frequency/)** - Sight words organized by grade

### Scope & Sequence References

1. **[IMSE Orton-Gillingham Scope & Sequence](https://journal.imse.com/understanding-scope-and-sequence/)** - Research-based phonics progression
2. **[UFLI Foundations](https://ufli.education.ufl.edu/)** - University of Florida Literacy Institute
3. **[The Reading League Decodable Sources](https://www.thereadingleague.org/decodable-text-sources/)** - Curated publisher list

### Assessment Frameworks

1. **[DIBELS 8th Edition](https://dibels.uoregon.edu/materials/dibels)** - Benchmark goals PDF
2. **[Lexile Grade Level Charts](https://hub.lexile.com/lexile-grade-level-charts/)** - Official Lexile-grade mapping
3. **[Marzano Vocabulary Lists](https://docs.steinhardt.nyu.edu/pdfs/metrocenter/atn293/pdf/cloud01232019/Grade-level-Marzano-list-LA_-SS_-Sci_-M.pdf)** - Academic vocabulary by grade

### Decodable Book Publishers (for reference style)

1. **Bob Books** - Classic CVC progression
2. **[Developing Decoders](https://www.developingdecoders.com/)** - UFLI & Fundations aligned
3. **Geodes** - High-interest decodables with rich content
4. **Phonic Books** - UK-based systematic readers

---

## Content Generation Workflow

### Step 1: Define Target Level

```
Input: Level number (0-23)
Output: Constraints object with:
  - phonics_patterns: allowed patterns
  - word_bank: decodable words
  - sight_words: cumulative list
  - max_words_per_sentence: number
  - sentence_structures: allowed types
  - avoid_patterns: patterns from higher levels
```

### Step 2: Generate Story Draft

```
Prompt Template:
- Reading level constraints
- Hero's Journey structure (simplified for lower levels)
- Character and setting
- Target phonics patterns to practice
- Word count targets

Output: JSON with pages, scenes, word lists
```

### Step 3: Phonics Validation

```
For each word in story:
  1. Check against allowed patterns
  2. Check against sight word list
  3. Flag any violations

For each sentence:
  1. Count words
  2. Check against max_words_per_sentence
  3. Flag violations
```

### Step 4: Revision Pass

```
If violations exist:
  - Send to Claude with specific instructions
  - Include violation list
  - Request substitutions
  - Re-validate
```

### Step 5: Assessment Generation

Generate companion assessments based on level:

#### Levels 0-8: Phonics-Focused
- Letter sound identification
- Word decoding (nonsense words)
- Word reading fluency
- Sentence reading
- Comprehension (picture-based for 0-2)

#### Levels 9-12: Transitional
- Multi-syllable word decoding
- Oral reading fluency (WCPM)
- Retelling
- Basic inference questions

#### Levels 13-16: Developing
- Vocabulary in context
- Main idea identification
- Text structure recognition
- Morphology (prefix/suffix meaning)

#### Levels 17-20: Fluent
- Academic vocabulary
- Inference and analysis
- Author's purpose
- Text evidence citing

#### Levels 21-23: Advanced
- Critical analysis
- Synthesis across texts
- Rhetorical analysis
- Original argument construction

---

## Assessment Question Types by Level

### Phonics Levels (0-8)

```javascript
const phonicsAssessments = {
  letterSound: {
    type: "audio-match",
    prompt: "Which word starts with the /s/ sound?",
    options: ["sun", "run", "fun", "bun"],
    correct: 0
  },
  wordDecode: {
    type: "read-aloud",
    prompt: "Read this word:",
    word: "sip",
    expectedPhonemes: ["s", "i", "p"]
  },
  sentenceRead: {
    type: "fluency",
    sentence: "The cat sat on the mat.",
    targetWCPM: 30
  },
  comprehension: {
    type: "picture-match",
    prompt: "Which picture shows: The pig is in mud?",
    options: ["pig_mud.png", "pig_sun.png", "dog_mud.png"]
  }
}
```

### Transitional Levels (9-12)

```javascript
const transitionalAssessments = {
  syllableDivision: {
    type: "segment",
    word: "rabbit",
    expectedParts: ["rab", "bit"]
  },
  fluency: {
    type: "oral-reading",
    passage: "...",
    targetWCPM: 90,
    comprehensionQuestions: 3
  },
  retelling: {
    type: "open-response",
    prompt: "Tell me what happened in the story.",
    rubric: ["characters", "setting", "problem", "solution"]
  }
}
```

### Developing Levels (13-16)

```javascript
const developingAssessments = {
  vocabularyContext: {
    type: "multiple-choice",
    sentence: "The scientist performed an experiment to test her hypothesis.",
    targetWord: "hypothesis",
    prompt: "What does 'hypothesis' mean in this sentence?",
    options: [
      "A guess based on evidence",
      "A type of microscope",
      "A science lab",
      "A final answer"
    ]
  },
  morphology: {
    type: "word-parts",
    word: "unhappiness",
    prompt: "Break this word into parts and explain each:",
    expected: {
      prefix: "un- (not)",
      root: "happy (feeling good)",
      suffix: "-ness (state of being)"
    }
  }
}
```

### Fluent Levels (17-20)

```javascript
const fluentAssessments = {
  inference: {
    type: "text-evidence",
    passage: "...",
    question: "How did the character feel about the decision?",
    requireEvidence: true
  },
  figurativeLanguage: {
    type: "interpretation",
    sentence: "Time is money.",
    prompt: "What does this metaphor mean?",
    rubric: ["identifies as metaphor", "explains comparison", "applies to context"]
  }
}
```

### Advanced Levels (21-23)

```javascript
const advancedAssessments = {
  rhetoricalAnalysis: {
    type: "essay",
    passage: "...",
    prompt: "Analyze how the author uses ethos, pathos, and logos to persuade the reader.",
    rubric: ["identifies techniques", "provides examples", "evaluates effectiveness"]
  },
  synthesis: {
    type: "multi-source",
    sources: ["source1.txt", "source2.txt"],
    prompt: "Compare and contrast the authors' perspectives on...",
    rubric: ["identifies similarities", "identifies differences", "draws conclusions"]
  }
}
```

---

## Quality Evaluation Criteria

### Decodability Score (Levels 0-12)

```
decodability_score = (decodable_words + sight_words) / total_words * 100

Target: 95%+ for levels 0-8
Target: 90%+ for levels 9-12
```

### Sentence Complexity Score

```
complexity_score = average_words_per_sentence / max_allowed_words

Target: 0.7-0.9 (use most of allowance without exceeding)
```

### Phonics Pattern Coverage

```
coverage_score = patterns_used / target_patterns * 100

Target: Include at least 3 instances of target phonics pattern
```

### Engagement Metrics

```
- Story arc completeness (Hero's Journey beats)
- Character development
- Repetition for reinforcement (especially levels 0-5)
- Illustration potential (scene descriptions)
```

---

## Implementation Checklist

### Phase 1: Core Infrastructure
- [ ] Word bank database by level
- [ ] Sight word lists (cumulative)
- [ ] Pattern validation functions
- [ ] Sentence analysis tools

### Phase 2: Content Generation
- [ ] Story prompt templates by level
- [ ] Claude API integration with constraints
- [ ] Revision loop automation
- [ ] Image prompt generation

### Phase 3: Assessment System
- [ ] Question type templates
- [ ] Scoring rubrics
- [ ] Progress tracking
- [ ] Recommendation engine

### Phase 4: Quality Assurance
- [ ] Automated decodability checking
- [ ] Human review workflow
- [ ] A/B testing framework
- [ ] User feedback integration

---

## Next Steps

1. **Build word bank database** - Import Fry words, phonics patterns
2. **Create validation API** - Check stories against level constraints
3. **Implement assessment generator** - Question templates by level
4. **Add progress tracking** - Store user assessment results
5. **Build recommendation engine** - Match books to user level
