"""
Story Evaluator

Automated evaluation of generated stories using LLM-as-judge.
Can be used alongside human evaluation or for large-scale testing.
"""

import json
from dataclasses import dataclass
from typing import Optional

from config import ModelConfig, MODELS, LevelSpec, StoryMode, get_api_keys
from pipeline import call_llm


# =============================================================================
# EVALUATION RUBRIC
# =============================================================================

EVALUATION_RUBRIC = """
# CHILDREN'S LEVELED READER EVALUATION RUBRIC

You are an expert evaluator of children's leveled readers / decodable books.
These are CURRICULAR TOOLS first, stories second.
Rate using BOTH pedagogical and creative criteria.

## SCORING SCALE
- 5 = Exceptional — Meets all criteria, ready to use
- 4 = Strong — Minor issues, clearly works for instruction
- 3 = Adequate — Functional but could be improved
- 2 = Weak — Significant problems for learners
- 1 = Poor — Doesn't serve the instructional goal

---

# PART A: CURRICULAR CRITERIA (50% of total)

### 1. PHONICS PATTERN PROMINENCE (weight: 15%)

**What to evaluate:**
- Are the TARGET phonics patterns actually prominent in the text?
- Do pattern words appear naturally, not forced?
- Is there enough repetition for practice without being tedious?
- Are patterns distributed throughout, not front-loaded?

**Target patterns for this text: {patterns}**

**5 — Exceptional:**
- Target patterns appear 8+ times naturally
- Patterns are distributed across the story
- Repetition feels purposeful (like a refrain)
- Child will encounter the pattern enough to internalize it
- Example: "Shush. / She wishes. / The ship shifts." (sh appears naturally, repeatedly)

**3 — Adequate:**
- Target patterns appear 4-7 times
- Some patterns feel natural, others forced
- Uneven distribution
- Example: Story uses "ship" and "shell" but then abandons sh- sounds

**1 — Poor:**
- Target patterns appear <4 times
- Patterns feel shoehorned or absent
- Child won't get enough practice
- Story could be about anything — phonics are incidental

---

### 2. SENTENCE COMPLEXITY FOR LEVEL (weight: 10%)

**What to evaluate:**
- Are sentences appropriate for the reading level?
- Is syntax simple enough for emerging readers?
- Are there too many clauses, conjunctions, or embedded phrases?
- Does sentence length vary appropriately?

**Level: {level}**

**Level Guidelines:**
- **A (emergent):** 2-5 words per sentence, simple SVO, mostly declarative
- **B (early):** 4-8 words, simple compound sentences (and, but), some questions
- **C (transitional):** 6-12 words, can include because/when/if, dialogue

**5 — Exceptional:**
- Every sentence is readable at this level
- Syntax supports decoding, doesn't fight it
- Variety in length creates rhythm without complexity
- Example (Level B): "Pip took a step. / Stop! Will he snap?"

**3 — Adequate:**
- Most sentences appropriate, a few too complex
- Some awkward constructions
- Example: "Pip, who was hungry, looked at the crocodile that was big."

**1 — Poor:**
- Sentences too complex for level
- Multiple clauses, difficult syntax
- Would frustrate a learner at this level

---

### 3. SIGHT WORD APPROPRIATENESS (weight: 10%)

**What to evaluate:**
- Are high-frequency sight words used appropriately?
- Are new sight words limited (1-3 per book)?
- Are sight words from the level's known set?
- Is sight word load manageable?

**Known sight words for this level: {sight_words}**

**5 — Exceptional:**
- Uses sight words from the known set
- 0-2 new sight words introduced clearly
- Sight words support fluency, don't overwhelm
- Example: Uses "the, a, is, was, said" — all known

**3 — Adequate:**
- Mostly known sight words
- 3-4 new sight words
- Some may challenge learners

**1 — Poor:**
- Many unknown sight words
- Would require too much teacher support
- Sight word load makes text frustrating

---

### 4. DECODABILITY SCORE (weight: 10%)

**What to evaluate:**
- What percentage of words can the child decode with taught skills?
- Are non-decodable words limited to sight words?
- Would a child at this level be able to read most words independently?

**Target decodability: {decodability_target}%**

**5 — Exceptional:**
- 90%+ decodable with level-appropriate skills
- Non-decodable words are all known sight words
- Child can read independently with minimal help

**3 — Adequate:**
- 75-89% decodable
- A few challenging words that need support
- Mostly independent reading possible

**1 — Poor:**
- <75% decodable
- Many words child cannot decode
- Requires significant adult support

---

### 5. WORD REPETITION FOR PRACTICE (weight: 5%)

**What to evaluate:**
- Do key decodable words repeat for practice?
- Is there enough exposure without being boring?
- Do pattern words appear in different contexts?

**5 — Exceptional:**
- Key pattern words appear 2-3 times each
- Repetition feels natural (not "see spot run" tedium)
- Words appear in varied sentences
- Example: "scrub" appears as "She scrubs," "Scrub, scrub, scrub!" "scrubs his teeth"

**3 — Adequate:**
- Some repetition of key words
- Could use more practice opportunities

**1 — Poor:**
- No repetition — each word appears once
- Or tedious repetition that feels like drill

---

# PART B: CREATIVE CRITERIA (50% of total)

## CRITERIA

### 1. RHYTHM & SOUND (weight: 20%)

**What to evaluate:**
- Does it feel good to read aloud?
- Do the phonics patterns create music rather than clunk?
- Is there variation in sentence length and cadence?
- Do stressed syllables land naturally?

**5 — Exceptional:**
- Sentences sing when read aloud
- Phonics patterns feel inevitable, not forced
- Rhythm varies purposefully (short for tension, long for calm)
- Could be memorized naturally by a child
- Example: "Shush. / The shell on the shore. / The shimmer. The shine."

**3 — Adequate:**
- Readable but not musical
- Phonics patterns present but mechanical
- Rhythm is consistent but monotonous
- Example: "Chuck found a shell. The shell was white. Chuck liked the shell."

**1 — Poor:**
- Awkward to read aloud
- Phonics patterns feel shoehorned
- No sense of rhythm or flow
- Example: "The ship which was in the shell was such a rich thing with a ring."

---

### 2. SENSORY GROUNDING (weight: 20%)

**What to evaluate:**
- Can you SEE, HEAR, FEEL the story?
- Are details specific or generic?
- Does the setting feel real?
- Are there textures, temperatures, sounds?

**5 — Exceptional:**
- Vivid, specific sensory details throughout
- Setting feels inhabitable
- At least 3 senses engaged
- Details are fresh, not clichéd
- Example: "Mud on her legs. Mud on her belly." / "Hot sand. Salt wind."

**3 — Adequate:**
- Some sensory details present
- Setting is identifiable but generic
- Relies on common descriptors
- Example: "The beach was sunny. The water was blue."

**1 — Poor:**
- Abstract, no sensory grounding
- Setting is vague or absent
- Reader cannot picture the scene
- Example: "They were at a nice place. It was good."

---

### 3. EMOTIONAL TRUTH (weight: 25%)

**What to evaluate:**
- Does the story feel REAL or like "a story about X"?
- Are emotions shown through action, not stated?
- Is there genuine feeling, not performed feeling?
- Would a child recognize this emotion?

**5 — Exceptional:**
- Emotions arise naturally from situation
- Never tells us how to feel
- Has a moment that lands emotionally
- Feels human-written, not AI-generated
- Example: "But part of her? Still up in the clouds." (longing, shown)

**3 — Adequate:**
- Emotions are present but surface-level
- Some telling mixed with showing
- Functional but doesn't resonate
- Example: "They were happy to be friends." (told, not shown)

**1 — Poor:**
- Emotions are stated directly ("She felt sad")
- Generic AI emotional language
- Clichés: "heart swelled," "learned an important lesson"
- No genuine feeling

**RED FLAGS (automatic deduction):**
- "She felt [emotion]" — deduct 1 point
- "This was [adjective]" (fun, nice, great) — deduct 1 point
- Stated moral at end — deduct 1 point
- "Heart swelled/warmed" or similar clichés — deduct 1 point

---

### 4. CHILD ENGAGEMENT (weight: 20%)

**What to evaluate:**
- Will a 4-6 year old lean in or tune out?
- Is there something to wonder about, laugh at, or feel?
- Does it respect children's intelligence?
- Is there a reason to turn the page?

**5 — Exceptional:**
- Child would ask to hear it again
- Has humor, surprise, or genuine tension
- Respects child's capacity for real emotion
- Creates participation (anticipation, prediction)
- Example: "Stop! Will he snap?" (genuine tension, child wonders)

**3 — Adequate:**
- Child would listen without complaint
- Moves forward but doesn't captivate
- Safe but not memorable
- Example: Standard "friends help each other" plot

**1 — Poor:**
- Child would lose interest
- Feels like medicine disguised as story
- Talks down to children
- Nothing to wonder about

---

### 5. SHOW VS. TELL (weight: 15%)

**What to evaluate:**
- Does the story DRAMATIZE or SUMMARIZE?
- Are we in the scene or hearing about it?
- Do characters act, or does narrator explain?

**5 — Exceptional:**
- All key moments are dramatized
- Reader experiences events firsthand
- Narrator is invisible
- Example: "RUM, RUM, RUM! She tugs a big log." (action, sound)

**3 — Adequate:**
- Mix of showing and telling
- Some scenes dramatized, others summarized
- Example: "She worked hard all day. Then she rested."

**1 — Poor:**
- Mostly summary and explanation
- Events reported rather than experienced
- Example: "The knight went on a journey and faced challenges."

---

## BONUS POINTS (up to +3)

Award bonus points for:
- **+1 Memorable line** — A line you'd quote or remember
- **+1 Educational hook** — Teaches something real about the world
- **+1 Surprising moment** — Does something unexpected within the form
- **+1 Perfect ending** — Lands with resonance, not summary

---

## DEDUCTIONS (up to -3)

Deduct points for:
- **-1 Name spam** — Character name used in >50% of sentences
- **-1 Dialogue ping-pong** — "said X" / "said Y" alternation throughout
- **-1 Phonics showing** — Can tell a word exists only for the pattern
- **-1 AI artifacts** — Unnatural phrasing, over-explanation, hedging

---

## OUTPUT FORMAT

Provide your evaluation as JSON:

```json
{{
  "curricular_scores": {{
    "phonics_prominence": <1-5>,
    "sentence_complexity": <1-5>,
    "sight_word_appropriateness": <1-5>,
    "decodability": <1-5>,
    "word_repetition": <1-5>
  }},
  "creative_scores": {{
    "rhythm_sound": <1-5>,
    "sensory_grounding": <1-5>,
    "emotional_truth": <1-5>,
    "child_engagement": <1-5>,
    "show_vs_tell": <1-5>
  }},
  "bonuses": {{
    "memorable_line": <true/false>,
    "educational_hook": <true/false>,
    "surprising_moment": <true/false>,
    "perfect_ending": <true/false>
  }},
  "deductions": {{
    "name_spam": <true/false>,
    "dialogue_pingpong": <true/false>,
    "phonics_showing": <true/false>,
    "ai_artifacts": <true/false>
  }},
  "curricular_total": <weighted curricular score out of 25>,
  "creative_total": <weighted creative score out of 25>,
  "final_score": <(curricular + creative) / 2 + bonuses - deductions, out of ~28>,
  "best_line": "<quote the single best line>",
  "worst_line": "<quote the single worst line>",
  "hardest_word": "<word that would be hardest for a child at this level>",
  "pattern_words_found": ["<list of words using target patterns>"],
  "curricular_verdict": "<one sentence on curricular fit>",
  "creative_verdict": "<one sentence on story quality>",
  "ready_for_instruction": <"yes" | "with_edits" | "no">
}}
```
"""


# =============================================================================
# EVALUATOR PROMPT
# =============================================================================

EVALUATOR_PROMPT = """
{rubric}

---

## STORY TO EVALUATE

**Level:** {level}
**Band:** {band}
**Mode:** {mode}
**Target phonics patterns:** {patterns}
**Known sight words:** {sight_words}
**Target decodability:** {decodability_target}%
**Max words:** {max_words}

```
{story}
```

---

Evaluate this story using the rubric above.
Be specific in identifying:
- The best and worst lines
- The hardest word for a child at this level
- All words that use the target phonics patterns

Output ONLY the JSON evaluation, no other text.
"""


# =============================================================================
# EVALUATION RESULT
# =============================================================================

@dataclass
class EvaluationResult:
    """Result from story evaluation."""
    curricular_scores: dict
    creative_scores: dict
    bonuses: dict
    deductions: dict
    curricular_total: float
    creative_total: float
    final_score: float
    best_line: str
    worst_line: str
    hardest_word: str
    pattern_words_found: list
    curricular_verdict: str
    creative_verdict: str
    ready_for_instruction: str
    raw_response: str


def calculate_curricular_score(scores: dict) -> float:
    """Calculate weighted curricular score (out of 25)."""
    weights = {
        "phonics_prominence": 0.30,        # 15% of 50% = 30% of curricular
        "sentence_complexity": 0.20,       # 10% of 50% = 20% of curricular
        "sight_word_appropriateness": 0.20,
        "decodability": 0.20,
        "word_repetition": 0.10,
    }
    total = sum(scores.get(k, 3) * w for k, w in weights.items())
    return total * 5  # Scale to 25


def calculate_creative_score(scores: dict) -> float:
    """Calculate weighted creative score (out of 25)."""
    weights = {
        "rhythm_sound": 0.20,
        "sensory_grounding": 0.20,
        "emotional_truth": 0.25,
        "child_engagement": 0.20,
        "show_vs_tell": 0.15,
    }
    total = sum(scores.get(k, 3) * w for k, w in weights.items())
    return total * 5  # Scale to 25


def calculate_final_score(curricular: float, creative: float, bonuses: dict, deductions: dict) -> float:
    """Calculate final score: average of curricular + creative, plus bonuses minus deductions."""
    base = (curricular + creative) / 2
    bonus_points = sum(1 for v in bonuses.values() if v)
    deduction_points = sum(1 for v in deductions.values() if v)
    return max(0, min(30, base + bonus_points - deduction_points))


# =============================================================================
# EVALUATOR
# =============================================================================

def evaluate_story(
    story: str,
    level_spec: LevelSpec,
    mode: str,
    evaluator_model: str = "claude-sonnet",
    api_keys: dict = None,
    verbose: bool = True
) -> EvaluationResult:
    """Evaluate a story using LLM-as-judge."""

    if api_keys is None:
        api_keys = get_api_keys()

    model_config = MODELS[evaluator_model]

    prompt = EVALUATOR_PROMPT.format(
        rubric=EVALUATION_RUBRIC.format(
            patterns=", ".join(level_spec.phonics_patterns),
            level=level_spec.level,
            sight_words=", ".join(level_spec.sight_words[:20]),
            decodability_target=int(level_spec.target_decodability * 100),
        ),
        level=level_spec.level,
        band=level_spec.band,
        mode=mode,
        patterns=", ".join(level_spec.phonics_patterns),
        sight_words=", ".join(level_spec.sight_words),
        decodability_target=int(level_spec.target_decodability * 100),
        max_words=level_spec.max_words,
        story=story,
    )

    if verbose:
        print(f"Evaluating with {evaluator_model}...")

    response = call_llm(model_config, prompt, api_keys)

    # Parse JSON from response
    try:
        # Find JSON in response
        json_start = response.find("{")
        json_end = response.rfind("}") + 1
        if json_start >= 0 and json_end > json_start:
            json_str = response[json_start:json_end]
            data = json.loads(json_str)
        else:
            raise ValueError("No JSON found in response")
    except json.JSONDecodeError as e:
        if verbose:
            print(f"JSON parse error: {e}")
            print(f"Response: {response[:500]}...")
        # Return default scores
        data = {
            "curricular_scores": {
                "phonics_prominence": 3, "sentence_complexity": 3,
                "sight_word_appropriateness": 3, "decodability": 3, "word_repetition": 3
            },
            "creative_scores": {
                "rhythm_sound": 3, "sensory_grounding": 3, "emotional_truth": 3,
                "child_engagement": 3, "show_vs_tell": 3
            },
            "bonuses": {},
            "deductions": {},
            "best_line": "",
            "worst_line": "",
            "hardest_word": "",
            "pattern_words_found": [],
            "curricular_verdict": "Could not parse evaluation",
            "creative_verdict": "Could not parse evaluation",
            "ready_for_instruction": "no"
        }

    # Extract scores
    curricular_scores = data.get("curricular_scores", {})
    creative_scores = data.get("creative_scores", {})
    bonuses = data.get("bonuses", {})
    deductions = data.get("deductions", {})

    # Calculate totals if not provided
    curricular_total = data.get("curricular_total") or calculate_curricular_score(curricular_scores)
    creative_total = data.get("creative_total") or calculate_creative_score(creative_scores)
    final = data.get("final_score") or calculate_final_score(curricular_total, creative_total, bonuses, deductions)

    return EvaluationResult(
        curricular_scores=curricular_scores,
        creative_scores=creative_scores,
        bonuses=bonuses,
        deductions=deductions,
        curricular_total=curricular_total,
        creative_total=creative_total,
        final_score=final,
        best_line=data.get("best_line", ""),
        worst_line=data.get("worst_line", ""),
        hardest_word=data.get("hardest_word", ""),
        pattern_words_found=data.get("pattern_words_found", []),
        curricular_verdict=data.get("curricular_verdict", ""),
        creative_verdict=data.get("creative_verdict", ""),
        ready_for_instruction=data.get("ready_for_instruction", "no"),
        raw_response=response,
    )


# =============================================================================
# BATCH EVALUATION
# =============================================================================

def evaluate_experiment_results(
    results_file: str,
    evaluator_model: str = "claude-sonnet",
    output_file: str = None,
    verbose: bool = True
) -> dict:
    """Evaluate all stories from an experiment results file."""

    from config import LEVEL_SPECS, TEST_SEEDS

    api_keys = get_api_keys()

    with open(results_file) as f:
        experiment = json.load(f)

    evaluations = []

    for result in experiment["results"]:
        seed_id = result["seed_id"]
        seed = next(s for s in TEST_SEEDS if s.id == seed_id)
        level_spec = LEVEL_SPECS[seed.level]

        if verbose:
            print(f"\nEvaluating {seed_id} / Config {result['config_name']}...")

        evaluation = evaluate_story(
            story=result["final"],
            level_spec=level_spec,
            mode=seed.mode,
            evaluator_model=evaluator_model,
            api_keys=api_keys,
            verbose=verbose,
        )

        evaluations.append({
            "seed_id": seed_id,
            "config_name": result["config_name"],
            "curricular_scores": evaluation.curricular_scores,
            "creative_scores": evaluation.creative_scores,
            "bonuses": evaluation.bonuses,
            "deductions": evaluation.deductions,
            "curricular_total": evaluation.curricular_total,
            "creative_total": evaluation.creative_total,
            "final_score": evaluation.final_score,
            "best_line": evaluation.best_line,
            "worst_line": evaluation.worst_line,
            "hardest_word": evaluation.hardest_word,
            "pattern_words_found": evaluation.pattern_words_found,
            "curricular_verdict": evaluation.curricular_verdict,
            "creative_verdict": evaluation.creative_verdict,
            "ready_for_instruction": evaluation.ready_for_instruction,
        })

        if verbose:
            print(f"   Curricular: {evaluation.curricular_total:.1f}/25 | Creative: {evaluation.creative_total:.1f}/25")
            print(f"   Final: {evaluation.final_score:.1f}/30 | Ready: {evaluation.ready_for_instruction}")

    # Aggregate by config
    from collections import defaultdict
    config_scores = defaultdict(lambda: {"final": [], "curricular": [], "creative": []})
    for e in evaluations:
        config_scores[e["config_name"]]["final"].append(e["final_score"])
        config_scores[e["config_name"]]["curricular"].append(e["curricular_total"])
        config_scores[e["config_name"]]["creative"].append(e["creative_total"])

    summary = {
        "experiment_id": experiment["experiment_id"],
        "evaluator_model": evaluator_model,
        "evaluations": evaluations,
        "summary": {
            config: {
                "avg_final": sum(scores["final"]) / len(scores["final"]),
                "avg_curricular": sum(scores["curricular"]) / len(scores["curricular"]),
                "avg_creative": sum(scores["creative"]) / len(scores["creative"]),
                "count": len(scores["final"]),
            }
            for config, scores in config_scores.items()
        },
        "winner_overall": max(config_scores.keys(), key=lambda c: sum(config_scores[c]["final"]) / len(config_scores[c]["final"])),
        "winner_curricular": max(config_scores.keys(), key=lambda c: sum(config_scores[c]["curricular"]) / len(config_scores[c]["curricular"])),
        "winner_creative": max(config_scores.keys(), key=lambda c: sum(config_scores[c]["creative"]) / len(config_scores[c]["creative"])),
    }

    if output_file:
        with open(output_file, "w") as f:
            json.dump(summary, f, indent=2)
        if verbose:
            print(f"\nEvaluations saved to: {output_file}")

    return summary


# =============================================================================
# CLI
# =============================================================================

if __name__ == "__main__":
    import argparse
    from dotenv import load_dotenv

    load_dotenv()

    parser = argparse.ArgumentParser(description="Evaluate stories")
    parser.add_argument("results_file", help="Path to FULL_RESULTS.json file")
    parser.add_argument("--model", default="claude-sonnet", help="Evaluator model")
    parser.add_argument("--output", help="Output file for evaluations")
    args = parser.parse_args()

    output = args.output or args.results_file.replace("FULL_RESULTS", "EVALUATIONS")

    summary = evaluate_experiment_results(
        args.results_file,
        evaluator_model=args.model,
        output_file=output,
    )

    print("\n" + "="*60)
    print("EVALUATION SUMMARY")
    print("="*60)

    print(f"\n{'Config':<8} {'Final':>8} {'Curric':>8} {'Creative':>8} {'n':>4}")
    print("-"*40)
    for config, stats in summary["summary"].items():
        print(f"{config:<8} {stats['avg_final']:>8.1f} {stats['avg_curricular']:>8.1f} {stats['avg_creative']:>8.1f} {stats['count']:>4}")

    print(f"\n🏆 Overall Winner: Config {summary['winner_overall']}")
    print(f"📚 Best Curricular: Config {summary['winner_curricular']}")
    print(f"✨ Best Creative: Config {summary['winner_creative']}")
