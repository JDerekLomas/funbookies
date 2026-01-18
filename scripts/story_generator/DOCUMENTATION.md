# Story Generator System Documentation

A multi-agent pipeline for generating leveled reader stories that balance **curricular rigor** with **creative quality**.

## Philosophy

> "These are curricular tools first, stories second — but the best curricular tools have soul."

Traditional AI-generated leveled readers fail in two ways:
1. **Phonics-first:** Stories feel like word lists wearing plot costumes
2. **Story-first:** Beautiful prose that children can't actually decode

This system separates concerns with specialized agents, then evaluates on both dimensions.

---

## System Architecture

```
                    ┌─────────────────┐
                    │   STORY SEED    │
                    │  level, mode,   │
                    │ setting, anchor │
                    └────────┬────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                      GENERATION PIPELINE                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │  GENERATOR  │───▶│   CRITIC    │───▶│   EDITOR    │     │
│  │             │    │             │    │             │     │
│  │ Creates     │    │ Identifies  │    │ Revises     │     │
│  │ freely,     │    │ problems,   │    │ honoring    │     │
│  │ finds soul  │    │ does NOT    │    │ critique +  │     │
│  │             │    │ rewrite     │    │ constraints │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│        │                   │                  │             │
│        │ (creative         │ (analysis        │ (final      │
│        │  draft)           │  only)           │  story)     │
│        ▼                   ▼                  ▼             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    ARTIFACTS                         │   │
│  │   draft.txt  │  critique.txt  │  final.txt          │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                     EVALUATION PIPELINE                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────┐    ┌──────────────────┐              │
│  │  DECODABILITY    │    │   LLM EVALUATOR  │              │
│  │  CHECKER         │    │                  │              │
│  │                  │    │  Curricular (50%)│              │
│  │  Python code,    │    │  Creative (50%)  │              │
│  │  no LLM needed   │    │  Bonuses/Deducts │              │
│  │                  │    │                  │              │
│  └──────────────────┘    └──────────────────┘              │
│           │                       │                         │
│           ▼                       ▼                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    SCORES                            │   │
│  │  Decodability %  │  Curricular /25  │  Creative /25  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Reading Levels

### Band A: Emergent Readers (Pre-K to early K)

| Level | Skill | Sentence Structure | Words/Page |
|-------|-------|-------------------|------------|
| A0 | Letter recognition | Labels only | 1-2 |
| A1 | Sight words A, I | 2-3 words, SVO | 2-4 |
| A2 | CVC (short a, i) | 3-5 words | 4-6 |
| A3 | CVC + "the" | 4-6 words | 5-8 |
| A4 | CVC all short vowels | 4-7 words | 6-10 |

### Band B: Early Readers (K-1)

| Level | Skill | Sentence Structure | Words/Page |
|-------|-------|-------------------|------------|
| B1 | CVC review | Simple sentences | 8-12 |
| B2 | CVC + blends intro | Compound with "and" | 10-15 |
| B3 | Consonant blends | Questions, exclamations | 12-18 |
| B4 | CVCC/CCVC | Varied sentence types | 12-18 |
| B5 | Digraphs (sh, ch, th) | Dialogue introduced | 15-20 |
| B6 | Long vowels (CVCe) | More complex dialogue | 15-22 |
| B7-B9 | Vowel teams, r-controlled | Richer syntax | 18-25 |

### Band C: Transitional Readers (1st-2nd)

| Level | Skill | Sentence Structure | Words/Page |
|-------|-------|-------------------|------------|
| C1 | Silent letters | Because/when/if clauses | 20-30 |
| C2 | Multisyllabic | Embedded clauses | 25-35 |
| C3+ | Morphology | Complex narratives | 30+ |

---

## Story Modes

### Narrative
Traditional story with character, conflict, resolution.
- **Best for:** Teaching cause/effect, prediction, sequencing
- **Rhythm:** Varied — short for tension, long for calm
- **Example:** Pip and the Croc (B3)

### Poem
Sound-focused, rhythm over plot.
- **Best for:** Phonics patterns with musical quality (sh = whispery)
- **Rhythm:** Highly structured, may use repetition/refrain
- **Example:** "Shush" poem for digraphs

### Lullaby
Quiet, soothing, gentle rhythm.
- **Best for:** Soft sounds, end-of-day reading
- **Rhythm:** Slow, regular, calming
- **Example:** Bioluminescent plankton at night

### Romp
Energetic, playful, percussive.
- **Best for:** Hard consonants, blends (ch, cr, st, pl)
- **Rhythm:** Punchy, fast, physical
- **Example:** Kitchen breakfast chaos

### Observation
Quiet noticing, wonder at small things.
- **Best for:** Building vocabulary, slow reading
- **Rhythm:** Contemplative, pauses for pictures
- **Example:** Grandmother's garden

---

## Evaluation Rubric

### Part A: Curricular Criteria (50% of total)

| Criteria | Weight | 5 (Exceptional) | 1 (Poor) |
|----------|--------|-----------------|----------|
| **Phonics Prominence** | 15% | 8+ pattern words, distributed naturally | <4 pattern words |
| **Sentence Complexity** | 10% | Every sentence readable at level | Too complex |
| **Sight Word Load** | 10% | All known, 0-2 new | Many unknown |
| **Decodability** | 10% | 90%+ decodable | <75% decodable |
| **Word Repetition** | 5% | Key words repeat 2-3x naturally | No repetition |

### Part B: Creative Criteria (50% of total)

| Criteria | Weight | 5 (Exceptional) | 1 (Poor) |
|----------|--------|-----------------|----------|
| **Rhythm & Sound** | 10% | Sings aloud | Clunky |
| **Sensory Grounding** | 10% | 3+ senses, vivid | Abstract |
| **Emotional Truth** | 12.5% | Feels real | AI clichés |
| **Child Engagement** | 10% | Kid asks for more | Boring |
| **Show vs Tell** | 7.5% | All dramatized | All summary |

### Bonuses (+1 each)
- Memorable line
- Educational hook
- Surprising moment
- Perfect ending

### Deductions (-1 each)
- Name spam
- Dialogue ping-pong
- Phonics showing
- AI artifacts

### Final Score
```
Final = (Curricular/25 + Creative/25) / 2 + bonuses - deductions
Max ≈ 30
```

---

## Pipeline Configurations

| Config | Generator | Critic | Editor | Cost/Story |
|--------|-----------|--------|--------|------------|
| **A** | Gemini 3 Flash | Gemini 3 Flash | Gemini 3 Flash | ~$0.002 |
| **B** | Gemini 3 Flash | Claude Haiku | Claude Sonnet | ~$0.01 |
| **C** | Claude Sonnet | Claude Haiku | Claude Sonnet | ~$0.02 |
| **D** | Claude Opus | Claude Sonnet | Claude Opus | ~$0.09 |
| **E** | Claude Opus | Claude Haiku | Claude Sonnet | ~$0.05 |
| **F** | Gemini 2.5 Flash | Gemini 2.5 Flash | Gemini 2.5 Flash | ~$0.001 |

---

## Usage

### Quick Test
```bash
cd scripts/story_generator
python run_experiment.py --quick
```

### Full Experiment
```bash
python run_experiment.py --configs A,C,D --seeds seed_01,seed_02 --auto-eval
```

### Evaluate Existing Results
```bash
python evaluator.py experiments/exp_YYYYMMDD_FULL_RESULTS.json
```

---

## Output Files

Each experiment generates:

| File | Purpose |
|------|---------|
| `*_BLIND_EVAL.md` | Human evaluation sheet (stories with random IDs) |
| `*_ANSWER_KEY.json` | Maps blind IDs to configs (don't peek!) |
| `*_FULL_RESULTS.json` | All artifacts: drafts, critiques, finals |
| `*_COMPARISON.md` | Side-by-side view (reveals configs) |
| `*_AUTO_EVAL.json` | LLM evaluator scores |

---

## Integration with Book JSON

The pipeline outputs can be converted to FunBookies book JSON format:

```python
from story_to_book import convert_to_book_json

book = convert_to_book_json(
    story=result.final,
    level_spec=level_spec,
    seed=seed,
    reference_prompt=generated_reference_prompt,
)

# Saves to public/books/{slug}.json
```

---

## Key Design Decisions

### 1. Critic Doesn't Rewrite
The critic identifies problems but never rewrites. This preserves creative voice and prevents the "AI smoothing" effect where revision homogenizes prose.

### 2. Phonics Patterns Have Personalities
- **sh, wh:** Whispery, quiet → poems, lullabies
- **ch, cr, st:** Percussive, energetic → romps
- **long vowels:** Stretchy, dreamy → observations

The generator prompt encourages leaning INTO the sound's personality.

### 3. Real-World Anchors
Every story seed includes a real phenomenon:
- Plover-crocodile symbiosis (teaches biology)
- Bioluminescent plankton (teaches science)
- Static electricity (teaches physics)

This grounds fiction in truth and gives children something to learn beyond phonics.

### 4. Dual Evaluation
A story can fail by being:
- Beautiful but undecodable (creative ✓, curricular ✗)
- Decodable but soulless (curricular ✓, creative ✗)

The rubric measures both, and reports separate winners for each dimension.

---

## Prompt Engineering Principles

### Generator Prompt
- Lead with mode and sound palette
- Provide real-world anchor
- Offer word resources without mandating them
- Forbid emotional telling explicitly
- Request sensory specifics

### Critic Prompt
- Clear rubric with examples
- Rate AND explain
- Identify best/worst lines by quoting
- Explicitly forbid rewriting

### Editor Prompt
- Provide both draft and critique
- List constraints explicitly
- Emphasize protecting "lines that sing"
- Request constraint invisibility

---

## Future Improvements

1. **LoRA-trained evaluator:** Fine-tune on human ratings for better calibration
2. **Adaptive difficulty:** Adjust based on child's performance data
3. **Multi-book arcs:** Character consistency across a series
4. **Audio generation:** TTS with appropriate pacing for level
