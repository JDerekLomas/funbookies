# Book Quality Evaluation Rubric

## Overview
This rubric evaluates books across three dimensions: **Story Quality**, **Image Quality**, and **Alignment**. Each dimension has specific criteria scored 0-3.

---

## 1. STORY QUALITY (Max: 15 points)

### 1.1 Structure Completeness (0-3)
| Score | Criteria |
|-------|----------|
| 0 | Missing most structural elements |
| 1 | Has pages but missing parent_tips, comprehension_questions, word_list |
| 2 | Has parent_tips OR comprehension_questions, plus word_list |
| 3 | Complete: parent_tips, comprehension_questions, word_list, wordsearch_words, summary |

### 1.2 Reading Level Alignment (0-3)
| Score | Criteria |
|-------|----------|
| 0 | Text complexity mismatched to stated level |
| 1 | Mostly appropriate but some sentences too complex/simple |
| 2 | Good match with minor inconsistencies |
| 3 | Perfect match - sentence length, vocabulary, and phonics align to band |

### 1.3 Narrative Quality (0-3)
| Score | Criteria |
|-------|----------|
| 0 | No clear story arc or engagement |
| 1 | Basic story exists but flat |
| 2 | Clear beginning/middle/end with some engagement |
| 3 | Compelling arc, emotional beats, age-appropriate themes |

### 1.4 Educational Value (0-3)
| Score | Criteria |
|-------|----------|
| 0 | No clear phonics/skill focus |
| 1 | Skills mentioned but not well integrated |
| 2 | Good skill integration with some repetition |
| 3 | Excellent skill practice naturally woven into story |

### 1.5 Parent/Teacher Support (0-3)
| Score | Criteria |
|-------|----------|
| 0 | No guidance provided |
| 1 | Minimal tips (just before_reading OR after_reading) |
| 2 | Good tips for all three phases but generic |
| 3 | Specific, actionable tips tied to book content and skills |

---

## 2. IMAGE QUALITY (Max: 12 points)

### 2.1 Coverage (0-3)
| Score | Criteria |
|-------|----------|
| 0 | No images or only cover |
| 1 | Cover + <50% of story pages have images |
| 2 | Cover + 50-90% of story pages have images |
| 3 | Cover + all story pages have images |

### 2.2 Style Consistency (0-3)
| Score | Criteria |
|-------|----------|
| 0 | No reference image, inconsistent style |
| 1 | Has reference but pages vary significantly |
| 2 | Mostly consistent with minor variations |
| 3 | Unified style throughout - characters, colors, mood consistent |

### 2.3 Visual Clarity (0-3)
| Score | Criteria |
|-------|----------|
| 0 | Confusing compositions, unclear subjects |
| 1 | Understandable but cluttered or poorly composed |
| 2 | Clear compositions with good focus |
| 3 | Excellent clarity, age-appropriate visual hierarchy |

### 2.4 Text-Free Images (0-3)
| Score | Criteria |
|-------|----------|
| 0 | Text baked into most images |
| 1 | Some images have unwanted text |
| 2 | Rare text artifacts |
| 3 | All images are pure illustration (text overlaid by UI) |

---

## 3. ALIGNMENT (Max: 9 points)

### 3.1 Text-Image Match (0-3)
| Score | Criteria |
|-------|----------|
| 0 | Images don't match text content |
| 1 | Loose connection between text and images |
| 2 | Good match with minor discrepancies |
| 3 | Images precisely illustrate the text on each page |

### 3.2 Character Consistency (0-3)
| Score | Criteria |
|-------|----------|
| 0 | Characters unrecognizable between pages |
| 1 | Characters vary significantly (wrong colors, features) |
| 2 | Characters mostly consistent with minor variations |
| 3 | Characters perfectly consistent - same design throughout |

### 3.3 Scene Prompt Quality (0-3)
| Score | Criteria |
|-------|----------|
| 0 | No scene descriptions in JSON |
| 1 | Brief/vague scene descriptions |
| 2 | Good descriptions with character and setting details |
| 3 | Detailed prompts with composition, mood, style notes |

---

## SCORING SUMMARY

| Dimension | Max Points |
|-----------|------------|
| Story Quality | 15 |
| Image Quality | 12 |
| Alignment | 9 |
| **TOTAL** | **36** |

### Grade Thresholds
| Grade | Score | Description |
|-------|-------|-------------|
| A | 32-36 | Publication ready |
| B | 26-31 | Minor improvements needed |
| C | 18-25 | Significant gaps to address |
| D | 10-17 | Major work required |
| F | 0-9 | Incomplete/unusable |

---

## AUTOMATED CHECKS

The following can be verified programmatically:

### Structure (from JSON):
- [ ] Has `parent_tips` with before/during/after
- [ ] Has `comprehension_questions` (4+ questions)
- [ ] Has `word_list` with sound_out/sight/new
- [ ] Has `wordsearch_words` (6+ words)
- [ ] Has `summary`
- [ ] All story pages have `scene` or `image_prompt`
- [ ] Has `reference_prompt`

### Images (from filesystem):
- [ ] Reference image exists: `references/{slug}_reference.png`
- [ ] Cover image exists: `covers/{slug}.png`
- [ ] Page images exist for each story page
- [ ] Image count matches story page count

### Metadata:
- [ ] Has `level` and `band`
- [ ] Has `targetPhonics` or `targetSkills`
- [ ] Has `metadata.wordCount`
- [ ] Has `metadata.storyPages`
