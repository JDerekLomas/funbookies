"""
Story Generation Pipeline

Generator → Critic → Editor pipeline for creating leveled reader stories.
"""

import json
import os
from dataclasses import dataclass, asdict
from typing import Optional
from datetime import datetime

from config import (
    ModelConfig, PipelineConfig, LevelSpec, StoryMode, StorySeed,
    MODELS, PIPELINE_CONFIGS, LEVEL_SPECS, STORY_MODES, get_api_keys
)


# =============================================================================
# PROMPTS
# =============================================================================

GENERATOR_PROMPT = """You are a children's book author with a gift for finding music in language.

CREATIVE DIRECTION:
{mode_guidance}

SOUND PALETTE:
These phonics patterns should feel natural, not forced: {patterns}
Let the sounds create rhythm. The constraint should feel like music, not homework.

SETTING:
{setting}

REAL-WORLD ANCHOR:
Base this on: {anchor}
Ground your story in something true. Kids learn while they feel.

WORD RESOURCES (use naturally, don't force):
Decodable words: {decodable_sample}
Sight words available: {sight_words}

CRITICAL RULES:
- NEVER tell emotions directly. No "she felt scared" or "this was fun"
- Show through: actions, dialogue, physical sensations, environment
- Include 3+ sensory details (sounds, textures, temperatures)
- End with an IMAGE or MOMENT, not a stated moral
- Vary sentence length: fragments for tension, longer for calm

Write freely. Find the soul first. We'll adapt for constraints later.
"""

CRITIC_PROMPT = """You are a children's book editor with 20 years of experience.
You have a sharp eye for dead prose and a deep love for language that sings.

DRAFT TO EVALUATE:
{draft}

EVALUATE ON THESE CRITERIA (rate each 1-5):

1. RHYTHM & SOUND PLEASURE
   Does it feel good to read aloud? Do the phonics patterns ({patterns}) create music?

2. SENSORY GROUNDING
   Can you see, hear, feel the story? Or is it abstract and floaty?

3. EMOTIONAL TRUTH
   Does it feel real? Or like an AI wrote "a story about friendship"?

4. CHILD ENGAGEMENT
   Will a 5-year-old lean in? Or tune out?

5. SHOW VS TELL
   Does it dramatize or summarize? Action or explanation?

NOW LIST:
- DEAD PHRASES: Lines that should be cut or rewritten (be specific, quote them)
- LINES THAT SING: Protect these at all costs (quote them)
- WHAT'S MISSING: What would make this come alive?

IMPORTANT: DO NOT REWRITE THE STORY. Critique only.
Your job is to identify problems, not fix them. The editor will do that.
"""

EDITOR_PROMPT = """You are a master editor who loves both language AND constraints.
You believe limitations can spark creativity, not kill it.

ORIGINAL DRAFT:
{draft}

CRITIC'S FEEDBACK:
{critique}

CURRICULUM CONSTRAINTS:
- Level: {level}
- Skill: {skill}
- Max words: {max_words}
- Target decodability: {decodability}%
- Required patterns: {patterns}
- Decodable words: {decodable_words}
- Sight words: {sight_words}

YOUR TASK:
1. PROTECT the "lines that sing" identified by the critic
2. CUT or REWRITE the "dead phrases"
3. ADDRESS what's missing
4. MEET the curriculum constraints
5. PRESERVE the mode ({mode}) - if it's a poem, keep it a poem

The constraint should be invisible in the final work.
If a line exists only to showcase a phonics pattern, it's not good enough.

Output ONLY the revised story. No commentary.
"""


# =============================================================================
# LLM CLIENTS
# =============================================================================

def call_google(model_config: ModelConfig, prompt: str, api_key: str) -> str:
    """Call Google Gemini API."""
    import requests

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_config.model_id}:generateContent?key={api_key}"

    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": model_config.temperature,
            "maxOutputTokens": model_config.max_tokens,
        }
    }

    response = requests.post(url, json=body, headers={"Content-Type": "application/json"})
    result = response.json()

    if "candidates" in result and result["candidates"]:
        return result["candidates"][0]["content"]["parts"][0]["text"]
    else:
        raise Exception(f"Gemini API error: {result}")


def call_anthropic(model_config: ModelConfig, prompt: str, api_key: str) -> str:
    """Call Anthropic Claude API."""
    import requests

    url = "https://api.anthropic.com/v1/messages"

    body = {
        "model": model_config.model_id,
        "max_tokens": model_config.max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }

    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
    }

    response = requests.post(url, json=body, headers=headers)
    result = response.json()

    if "content" in result and result["content"]:
        return result["content"][0]["text"]
    else:
        raise Exception(f"Anthropic API error: {result}")


def call_openai(model_config: ModelConfig, prompt: str, api_key: str) -> str:
    """Call OpenAI API."""
    import requests

    url = "https://api.openai.com/v1/chat/completions"

    body = {
        "model": model_config.model_id,
        "max_tokens": model_config.max_tokens,
        "temperature": model_config.temperature,
        "messages": [{"role": "user", "content": prompt}],
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    response = requests.post(url, json=body, headers=headers)
    result = response.json()

    if "choices" in result and result["choices"]:
        return result["choices"][0]["message"]["content"]
    else:
        raise Exception(f"OpenAI API error: {result}")


def call_llm(model_config: ModelConfig, prompt: str, api_keys: dict) -> str:
    """Route to appropriate LLM provider."""
    provider = model_config.provider
    api_key = api_keys.get(provider)

    if not api_key:
        raise Exception(f"No API key found for provider: {provider}")

    if provider == "google":
        return call_google(model_config, prompt, api_key)
    elif provider == "anthropic":
        return call_anthropic(model_config, prompt, api_key)
    elif provider == "openai":
        return call_openai(model_config, prompt, api_key)
    else:
        raise Exception(f"Unknown provider: {provider}")


# =============================================================================
# DECODABILITY CHECKER (no LLM needed)
# =============================================================================

def check_decodability(text: str, level_spec: LevelSpec) -> dict:
    """Check what percentage of words are decodable."""
    import re

    # Simple tokenization
    words = re.findall(r"[a-zA-Z]+", text.lower())

    # Build allowed word set
    allowed = set(w.lower() for w in level_spec.decodable_words)
    allowed.update(w.lower() for w in level_spec.sight_words)

    # Count
    total = len(words)
    decodable = sum(1 for w in words if w in allowed)
    unknown = [w for w in set(words) if w not in allowed]

    return {
        "total_words": total,
        "decodable_count": decodable,
        "decodability": decodable / total if total > 0 else 0,
        "unknown_words": sorted(set(unknown)),
        "meets_target": (decodable / total if total > 0 else 0) >= level_spec.target_decodability,
    }


# =============================================================================
# PIPELINE
# =============================================================================

@dataclass
class PipelineResult:
    """Result from running the full pipeline."""
    seed_id: str
    config_name: str
    draft: str
    critique: str
    final: str
    decodability: dict
    timestamps: dict
    model_info: dict


def run_pipeline(
    seed: StorySeed,
    pipeline_config: PipelineConfig,
    api_keys: dict,
    verbose: bool = True
) -> PipelineResult:
    """Run the full Generator → Critic → Editor pipeline."""

    level_spec = LEVEL_SPECS[seed.level]
    story_mode = STORY_MODES[seed.mode]
    timestamps = {}

    if verbose:
        print(f"\n{'='*60}")
        print(f"Running pipeline: {pipeline_config.name}")
        print(f"Seed: {seed.id} | Level: {seed.level} | Mode: {seed.mode}")
        print(f"{'='*60}")

    # --- STEP 1: GENERATE ---
    if verbose:
        print(f"\n[1/3] Generating with {pipeline_config.generator}...")

    timestamps["generate_start"] = datetime.now().isoformat()

    generator_prompt = GENERATOR_PROMPT.format(
        mode_guidance=story_mode.prompt_guidance,
        patterns=", ".join(level_spec.phonics_patterns),
        setting=seed.setting,
        anchor=seed.anchor,
        decodable_sample=", ".join(level_spec.decodable_words[:20]),
        sight_words=", ".join(level_spec.sight_words),
    )

    draft = call_llm(pipeline_config.get_generator(), generator_prompt, api_keys)
    timestamps["generate_end"] = datetime.now().isoformat()

    if verbose:
        print(f"   Draft generated ({len(draft.split())} words)")

    # --- STEP 2: CRITIQUE ---
    if verbose:
        print(f"\n[2/3] Critiquing with {pipeline_config.critic}...")

    timestamps["critique_start"] = datetime.now().isoformat()

    critic_prompt = CRITIC_PROMPT.format(
        draft=draft,
        patterns=", ".join(level_spec.phonics_patterns),
    )

    critique = call_llm(pipeline_config.get_critic(), critic_prompt, api_keys)
    timestamps["critique_end"] = datetime.now().isoformat()

    if verbose:
        print(f"   Critique complete")

    # --- STEP 3: EDIT ---
    if verbose:
        print(f"\n[3/3] Editing with {pipeline_config.editor}...")

    timestamps["edit_start"] = datetime.now().isoformat()

    editor_prompt = EDITOR_PROMPT.format(
        draft=draft,
        critique=critique,
        level=level_spec.level,
        skill=level_spec.skill,
        max_words=level_spec.max_words,
        decodability=int(level_spec.target_decodability * 100),
        patterns=", ".join(level_spec.phonics_patterns),
        decodable_words=", ".join(level_spec.decodable_words),
        sight_words=", ".join(level_spec.sight_words),
        mode=seed.mode,
    )

    final = call_llm(pipeline_config.get_editor(), editor_prompt, api_keys)
    timestamps["edit_end"] = datetime.now().isoformat()

    if verbose:
        print(f"   Final story ({len(final.split())} words)")

    # --- STEP 4: CHECK DECODABILITY ---
    decodability = check_decodability(final, level_spec)

    if verbose:
        print(f"\n[4/4] Decodability: {decodability['decodability']:.1%}")
        if decodability['unknown_words']:
            print(f"   Unknown words: {', '.join(decodability['unknown_words'][:10])}")

    return PipelineResult(
        seed_id=seed.id,
        config_name=pipeline_config.name,
        draft=draft,
        critique=critique,
        final=final,
        decodability=decodability,
        timestamps=timestamps,
        model_info={
            "generator": pipeline_config.generator,
            "critic": pipeline_config.critic,
            "editor": pipeline_config.editor,
        }
    )


# =============================================================================
# MAIN (for testing)
# =============================================================================

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    api_keys = get_api_keys()
    print("API keys loaded:", {k: "✓" if v else "✗" for k, v in api_keys.items()})

    # Test with one seed and one config
    from config import TEST_SEEDS

    seed = TEST_SEEDS[0]
    config = PIPELINE_CONFIGS["A"]  # Gemini 3 Flash

    result = run_pipeline(seed, config, api_keys, verbose=True)

    print("\n" + "="*60)
    print("FINAL STORY:")
    print("="*60)
    print(result.final)
