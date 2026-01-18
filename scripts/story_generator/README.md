# Story Generator Experiment

A/B test different LLM configurations for generating children's leveled reader stories.

## The Pipeline

```
Generator → Critic → Editor → Decodability Check
   │           │         │            │
   │           │         │            └── Python (no LLM)
   │           │         └── Revises based on critique + constraints
   │           └── Identifies problems (doesn't rewrite)
   └── Creates freely, finds the soul
```

## Quick Start

```bash
cd scripts/story_generator

# Install dependencies
pip install requests python-dotenv

# Set API keys
export GOOGLE_AI_API_KEY=your_key
export ANTHROPIC_API_KEY=your_key  # optional, for Claude configs

# Quick test (1 config × 1 seed)
python run_experiment.py --quick

# Run default experiment (3 configs × 2 seeds)
python run_experiment.py

# Run specific configs
python run_experiment.py --configs A,D --seeds seed_01,seed_03
```

## Configurations

| Config | Generator | Critic | Editor | Cost |
|--------|-----------|--------|--------|------|
| **A** | Gemini 3 Flash | Gemini 3 Flash | Gemini 3 Flash | $ |
| **B** | Gemini 3 Flash | Claude Haiku | Claude Sonnet | $$ |
| **C** | Claude Sonnet | Claude Haiku | Claude Sonnet | $$$ |
| **D** | Claude Opus | Claude Sonnet | Claude Opus | $$$$ |
| **E** | Claude Opus | Claude Haiku | Claude Sonnet | $$$ |
| **F** | Gemini 2.5 Flash | Gemini 2.5 Flash | Gemini 2.5 Flash | ¢ |

## Test Seeds

| ID | Level | Mode | Setting |
|----|-------|------|---------|
| seed_01 | B5 | poem | Tide pools at dawn |
| seed_02 | B3 | narrative | African riverbank (plover-croc) |
| seed_03 | B5 | lullaby | Fishing village at night |
| seed_04 | C1 | observation | Grandmother's garden |
| seed_05 | B3 | romp | Kitchen during breakfast |

## Running the Experiment

### Step 1: Generate Stories

```bash
python run_experiment.py --configs A,C,D --seeds seed_01,seed_02
```

This creates in `experiments/`:
- `exp_YYYYMMDD_HHMMSS_BLIND_EVAL.md` — Rate stories here (blind)
- `exp_YYYYMMDD_HHMMSS_ANSWER_KEY.json` — Don't peek!
- `exp_YYYYMMDD_HHMMSS_FULL_RESULTS.json` — All artifacts
- `exp_YYYYMMDD_HHMMSS_COMPARISON.md` — Side-by-side (reveals configs)

### Step 2: Blind Evaluation

1. Open `BLIND_EVAL.md`
2. Rate each story 1-5 on:
   - Rhythm & Sound Pleasure
   - Sensory Grounding
   - Emotional Truth
   - Child Engagement
   - Show vs Tell
3. Note best/worst lines
4. Mark: Would publish? Yes / With edits / No

### Step 3: Reveal Results

```bash
python analyze_results.py experiments/exp_YYYYMMDD_HHMMSS_ANSWER_KEY.json
```

Enter your scores. Script reveals:
- Which config produced which story
- Aggregate scores by config
- Winner recommendation
- Cost per story estimate

## Evaluation Criteria

| Criteria | 5 (Exceptional) | 3 (Adequate) | 1 (Poor) |
|----------|-----------------|--------------|----------|
| **Rhythm** | Sings when read aloud | Readable | Clunky |
| **Sensory** | Vivid, specific | Some details | Abstract |
| **Emotional** | Feels true | Functional | AI-generic |
| **Engagement** | Kid leans in | Acceptable | Boring |
| **Show/Tell** | All action | Mixed | All telling |

## Adding New Configurations

Edit `config.py`:

```python
PIPELINE_CONFIGS["G"] = PipelineConfig(
    name="G",
    description="Your new config",
    generator="claude-opus",
    critic="gemini-3-flash",
    editor="claude-sonnet",
)
```

## Adding New Test Seeds

Edit `config.py`:

```python
TEST_SEEDS.append(StorySeed(
    id="seed_06",
    level="B5",
    mode="romp",
    setting="playground at recess",
    anchor="Static electricity making hair stand up",
))
```

## Auto-Evaluation with LLM-as-Judge

Run automatic evaluation alongside human evaluation:

```bash
# Generate + auto-evaluate in one command
python run_experiment.py --configs A,C,D --auto-eval

# Use a specific evaluator model
python run_experiment.py --configs A,C,D --auto-eval --eval-model claude-opus

# Evaluate existing results
python evaluator.py experiments/exp_YYYYMMDD_FULL_RESULTS.json
```

### Evaluation Rubric (10 Criteria, 2 Categories)

The rubric evaluates **both** curricular fit and creative quality.

#### Part A: Curricular Criteria (50% of total)

| Criteria | Weight | What It Measures |
|----------|--------|------------------|
| **Phonics Prominence** | 15% | Target patterns appear naturally, 8+ times |
| **Sentence Complexity** | 10% | Appropriate syntax for level (A/B/C) |
| **Sight Word Appropriateness** | 10% | Uses known sight words, limits new ones |
| **Decodability** | 10% | % of words child can decode with taught skills |
| **Word Repetition** | 5% | Key words repeat for practice |

#### Part B: Creative Criteria (50% of total)

| Criteria | Weight | What It Measures |
|----------|--------|------------------|
| **Rhythm & Sound** | 10% | Read-aloud quality, phonics as music |
| **Sensory Grounding** | 10% | Can you see/hear/feel it? |
| **Emotional Truth** | 12.5% | Real feeling vs "a story about X" |
| **Child Engagement** | 10% | Will a 5-year-old lean in? |
| **Show vs Tell** | 7.5% | Dramatized or summarized? |

### Bonuses (+1 each, max +4)
- Memorable line
- Educational hook (teaches something real)
- Surprising moment
- Perfect ending

### Deductions (-1 each, max -4)
- Name spam (character name >50% of sentences)
- Dialogue ping-pong ("said X" / "said Y")
- Phonics showing (words exist only for pattern)
- AI artifacts (unnatural phrasing)

### Red Flags (deduct from Emotional Truth)
- "She felt [emotion]" — telling
- "This was fun/nice/great" — telling
- Stated moral at end
- "Heart swelled/warmed" clichés

### Score Ranges

- **Curricular Score:** /25 (is it teachable?)
- **Creative Score:** /25 (does it have soul?)
- **Final Score:** (curricular + creative) / 2 + bonuses - deductions ≈ /30

**Interpretation:**
- 25-30: Ready for instruction, has soul
- 20-24: Usable with minor edits
- 15-19: Functional but needs work
- <15: Significant revision needed

## Files

```
story_generator/
├── config.py           # Models, pipelines, levels, seeds
├── pipeline.py         # Generator → Critic → Editor logic
├── run_experiment.py   # Experiment runner
├── evaluator.py        # LLM-as-judge auto-evaluation
├── analyze_results.py  # Human results analyzer
└── README.md           # This file
```
