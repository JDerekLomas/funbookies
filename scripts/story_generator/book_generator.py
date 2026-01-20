#!/usr/bin/env python3
"""
Complete Book Generator

Generates story + reference image prompt + book JSON structure.
Combines the story pipeline with reference prompt generation.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional

from dotenv import load_dotenv

from config import (
    ModelConfig, PipelineConfig, LevelSpec, StoryMode, StorySeed,
    MODELS, PIPELINE_CONFIGS, LEVEL_SPECS, STORY_MODES, get_api_keys
)
from pipeline import run_pipeline, call_llm


# =============================================================================
# REFERENCE PROMPT GENERATOR
# =============================================================================

REFERENCE_PROMPT_TEMPLATE = """You are an expert at creating 9-panel style reference sheets for children's book illustrators.

Given a story, extract the key visual elements and create a reference sheet prompt.

## STORY
Title: {title}
Level: {level}
Mode: {mode}
Setting: {setting}

```
{story}
```

## CHARACTERS MENTIONED
{characters}

## YOUR TASK

Create a 9-panel reference sheet prompt following this EXACT structure:

```
9-PANEL STYLE REFERENCE SHEET for children's picture book

FOCUS: Character design, setting elements, color palette. [Style direction based on mode].

Row 1 - [MAIN CHARACTER NAME] ([brief description]):
[1] [Character] front view: [Detailed appearance - physical features, clothing, colors, expression]. Simple shapes, big expressive eyes. [Background color]
[2] [Character] expressions: Same [character] showing three faces - [emotion 1], [emotion 2], [emotion 3]
[3] [Character] in action: [Character doing key action from story]

Row 2 - [SECONDARY ELEMENTS AND KEY MOMENT]:
[4] [Secondary character or key object]: [Detailed description]
[5] [Another key element]: [Detailed description]
[6] KEY IMAGE: [The most iconic/memorable moment from the story - this goes in center for maximum style influence]

Row 3 - [SETTING] (simplified):
[7] [Setting element 1]: [Description with colors and mood]
[8] [Setting element 2]: [Description with atmosphere]
[9] [Final scene or characters together]: [Peaceful/resolution moment]

STYLE: [Specific art style based on the story's mode - e.g., "Simple stylized children's book illustration like Eric Carle" or "Soft watercolor with gentle edges like Beatrix Potter" or "Bold graphic shapes like Lois Ehlert"]. [Color palette]. [Shape language]. Friendly and approachable. NOT realistic.

LAYOUT: 3x3 grid, thin white borders between panels.

CRITICAL: NO TEXT, NO WORDS, NO LETTERS anywhere. Pure illustration only.
```

## MODE-SPECIFIC STYLE GUIDANCE

- **narrative:** Dynamic, expressive, clear action. Eric Carle, Leo Lionni style.
- **poem:** Dreamy, atmospheric, softer edges. Watercolor washes, gentle transitions.
- **lullaby:** Soft, muted, cozy. Night colors, warm glows, gentle curves.
- **romp:** Bold, energetic, high contrast. Sharp shapes, bright colors, movement lines.
- **observation:** Detailed naturalistic elements, botanical illustration influence, gentle palette.

Output ONLY the reference prompt, nothing else.
"""


def generate_reference_prompt(
    story: str,
    title: str,
    level: str,
    mode: str,
    setting: str,
    characters: str,
    model: str = "claude-sonnet",
    api_keys: dict = None,
    verbose: bool = True
) -> str:
    """Generate a 9-panel reference sheet prompt for the story."""

    if api_keys is None:
        api_keys = get_api_keys()

    model_config = MODELS[model]

    prompt = REFERENCE_PROMPT_TEMPLATE.format(
        title=title,
        level=level,
        mode=mode,
        setting=setting,
        story=story,
        characters=characters,
    )

    if verbose:
        print(f"Generating reference prompt with {model}...")

    response = call_llm(model_config, prompt, api_keys)

    # Clean up response - find the reference prompt
    if "9-PANEL" in response:
        start = response.find("9-PANEL")
        return response[start:].strip()
    return response.strip()


# =============================================================================
# BOOK STRUCTURE GENERATOR
# =============================================================================

def story_to_pages(story: str, mode: str) -> list:
    """Convert story text to page structure."""

    # Split by double newlines or significant breaks
    lines = [l.strip() for l in story.strip().split('\n') if l.strip()]

    pages = []
    current_page_text = []

    for line in lines:
        current_page_text.append(line)

        # For poems/lullabies, shorter pages
        if mode in ['poem', 'lullaby']:
            if len(current_page_text) >= 2 or line.endswith('.') or line.endswith('!') or line.endswith('?'):
                pages.append('\n'.join(current_page_text))
                current_page_text = []
        # For narratives, 2-3 sentences per page
        else:
            sentence_count = sum(1 for t in current_page_text for c in t if c in '.!?')
            if sentence_count >= 2:
                pages.append('\n'.join(current_page_text))
                current_page_text = []

    # Don't forget remaining text
    if current_page_text:
        pages.append('\n'.join(current_page_text))

    return pages


def generate_book_json(
    story: str,
    title: str,
    slug: str,
    level_spec: LevelSpec,
    seed: StorySeed,
    reference_prompt: str,
    pipeline_config: PipelineConfig,
    draft: str = None,
    critique: str = None,
) -> dict:
    """Generate complete book JSON structure."""

    story_pages = story_to_pages(story, seed.mode)

    pages = [
        {
            "page": 1,
            "type": "cover",
            "text": title,
            "scene": f"Cover illustration for '{title}'. {seed.setting}. Style matches the reference sheet."
        },
        {"page": 2, "type": "copyright"},
        {"page": 3, "type": "parent_guide"},
        {"page": 4, "type": "level_info"},
        {"page": 5, "type": "wordlist", "text": "Words to Know"},
    ]

    # Add story pages
    # NOTE: Scene descriptions are PLACEHOLDERS and must be regenerated
    # before image generation. Run: python scripts/generate_scene_descriptions.py <slug>
    for i, text in enumerate(story_pages, 1):
        pages.append({
            "page": 5 + i,
            "story_page": i,
            "type": "story",
            "text": text,
            # PLACEHOLDER - must be replaced with proper scene description before images
            # Proper scenes need: WHO/WHERE/WHAT/COMPOSITION/STYLE
            # Run generate_scene_descriptions.py to fix
            "scene": f"[PLACEHOLDER - run generate_scene_descriptions.py] {text[:80]}..."
        })

    # Add end matter
    story_end_page = 5 + len(story_pages)
    pages.extend([
        {
            "page": story_end_page + 1,
            "type": "end",
            "text": "The End",
            # PLACEHOLDER - must be replaced with proper scene description before images
            # End pages should show a satisfying final moment with main character(s)
            "scene": "[PLACEHOLDER - run generate_scene_descriptions.py] Final celebratory scene"
        },
        {"page": story_end_page + 2, "type": "wordsearch"},
        {"page": story_end_page + 3, "type": "series_info"},
        {"page": story_end_page + 4, "type": "back_cover", "text": ""},
    ])

    return {
        "id": slug,
        "title": title,
        "slug": slug,
        "level": level_spec.level,
        "band": level_spec.band,
        "targetPhonics": ", ".join(level_spec.phonics_patterns),
        "wordFamilies": level_spec.word_families,
        "skill": level_spec.skill,
        "skill_description": level_spec.skill_description,
        "age_range": "K-1" if level_spec.band == "B" else ("Pre-K" if level_spec.band == "A" else "1-2"),
        "created": datetime.now().strftime("%Y-%m-%d"),
        "author": "FunBookies",
        "illustrator": "AI Generated",
        "summary": seed.anchor,
        "characters": {},  # To be filled in
        "setting_context": seed.setting,
        "word_list": {
            "sound_out": level_spec.decodable_words[:30],
            "sight": level_spec.sight_words,
            "heart": []
        },
        "sightWordsUsed": level_spec.sight_words,
        "wordsearch_words": level_spec.decodable_words[:8],
        "pages": pages,
        "metadata": {
            "generatedAt": datetime.now().isoformat(),
            "levelSpecs": "v2",
            "wordCount": len(story.split()),
            "decodabilityTarget": f"{int(level_spec.target_decodability * 100)}%",
            "storyPages": len(story_pages),
            "pipeline": pipeline_config.name,
            "mode": seed.mode,
        },
        "reference_prompt": reference_prompt,
        "generation_artifacts": {
            "draft": draft,
            "critique": critique,
            "final": story,
        },
        "parent_tips": {
            "before_reading": f"Look at the cover of '{title}'. What do you see? This book focuses on {level_spec.skill}.",
            "during_reading": f"Help your child sound out words with {', '.join(level_spec.phonics_patterns[:3])} patterns.",
            "after_reading": "What was your favorite part? Can you find words with our special sounds?"
        },
        "comprehension_questions": [
            {"question": "What happens at the beginning?", "answer": ""},
            {"question": "What happens in the middle?", "answer": ""},
            {"question": "How does it end?", "answer": ""},
        ]
    }


# =============================================================================
# COMPLETE BOOK GENERATION
# =============================================================================

@dataclass
class BookGenerationResult:
    """Complete result from book generation."""
    title: str
    slug: str
    story: str
    draft: str
    critique: str
    reference_prompt: str
    book_json: dict
    seed: StorySeed
    level_spec: LevelSpec
    pipeline_config: str


def generate_complete_book(
    seed: StorySeed,
    pipeline_config: PipelineConfig,
    title: str = None,
    api_keys: dict = None,
    verbose: bool = True
) -> BookGenerationResult:
    """Generate a complete book: story + reference prompt + JSON structure."""

    if api_keys is None:
        api_keys = get_api_keys()

    level_spec = LEVEL_SPECS[seed.level]

    # Generate title if not provided
    if not title:
        title = f"Story for {seed.level} - {seed.mode}"

    slug = title.lower().replace(' ', '-').replace("'", "")[:50]

    if verbose:
        print(f"\n{'='*60}")
        print(f"GENERATING BOOK: {title}")
        print(f"Level: {seed.level} | Mode: {seed.mode}")
        print(f"Pipeline: {pipeline_config.name} - {pipeline_config.description}")
        print(f"{'='*60}")

    # Step 1: Generate story through pipeline
    result = run_pipeline(seed, pipeline_config, api_keys, verbose=verbose)

    # Step 2: Extract characters from the story
    characters_prompt = f"List the main characters in this story, with brief descriptions:\n\n{result.final}"
    # Use same provider as pipeline - prefer claude-haiku if anthropic key available
    if api_keys.get("anthropic"):
        characters = call_llm(MODELS["claude-haiku"], characters_prompt, api_keys)
    else:
        characters = call_llm(MODELS["gemini-3-flash"], characters_prompt, api_keys)

    # Step 3: Generate reference prompt
    if verbose:
        print(f"\n[+] Generating reference image prompt...")

    # Choose model for reference prompt based on available keys
    ref_model = "claude-haiku" if api_keys.get("anthropic") else "gemini-3-flash"
    reference_prompt = generate_reference_prompt(
        story=result.final,
        title=title,
        level=seed.level,
        mode=seed.mode,
        setting=seed.setting,
        characters=characters,
        model=ref_model,
        api_keys=api_keys,
        verbose=verbose,
    )

    # Step 4: Create book JSON
    if verbose:
        print(f"\n[+] Creating book JSON structure...")

    book_json = generate_book_json(
        story=result.final,
        title=title,
        slug=slug,
        level_spec=level_spec,
        seed=seed,
        reference_prompt=reference_prompt,
        pipeline_config=pipeline_config,
        draft=result.draft,
        critique=result.critique,
    )

    return BookGenerationResult(
        title=title,
        slug=slug,
        story=result.final,
        draft=result.draft,
        critique=result.critique,
        reference_prompt=reference_prompt,
        book_json=book_json,
        seed=seed,
        level_spec=level_spec,
        pipeline_config=pipeline_config.name,
    )


# =============================================================================
# CLI
# =============================================================================

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Generate complete book")
    parser.add_argument("--level", required=True, help="Reading level (e.g., B3, B5, C1)")
    parser.add_argument("--mode", required=True, choices=["narrative", "poem", "lullaby", "romp", "observation"])
    parser.add_argument("--setting", required=True, help="Story setting")
    parser.add_argument("--anchor", required=True, help="Real-world anchor/phenomenon")
    parser.add_argument("--title", help="Book title (optional)")
    parser.add_argument("--config", default="C", help="Pipeline config (A-F)")
    parser.add_argument("--output", default="generated_books", help="Output directory")
    args = parser.parse_args()

    load_dotenv()
    api_keys = get_api_keys()

    # Create seed
    seed = StorySeed(
        id=f"custom_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        level=args.level,
        mode=args.mode,
        setting=args.setting,
        anchor=args.anchor,
    )

    # Get pipeline config
    pipeline_config = PIPELINE_CONFIGS[args.config]

    # Generate book
    result = generate_complete_book(
        seed=seed,
        pipeline_config=pipeline_config,
        title=args.title,
        api_keys=api_keys,
        verbose=True,
    )

    # Save outputs
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save book JSON
    book_path = output_dir / f"{result.slug}.json"
    with open(book_path, "w") as f:
        json.dump(result.book_json, f, indent=2)
    print(f"\n✓ Book JSON: {book_path}")

    # Save story text
    story_path = output_dir / f"{result.slug}_story.txt"
    with open(story_path, "w") as f:
        f.write(f"# {result.title}\n\n")
        f.write(result.story)
    print(f"✓ Story text: {story_path}")

    # Save reference prompt
    ref_path = output_dir / f"{result.slug}_reference_prompt.txt"
    with open(ref_path, "w") as f:
        f.write(result.reference_prompt)
    print(f"✓ Reference prompt: {ref_path}")

    # Save artifacts
    artifacts_path = output_dir / f"{result.slug}_artifacts.json"
    with open(artifacts_path, "w") as f:
        json.dump({
            "draft": result.draft,
            "critique": result.critique,
            "final": result.story,
            "reference_prompt": result.reference_prompt,
        }, f, indent=2)
    print(f"✓ Artifacts: {artifacts_path}")

    print(f"\n{'='*60}")
    print("GENERATION COMPLETE")
    print(f"{'='*60}")
    print(f"\nSTORY:\n{result.story}")
    print(f"\n{'='*60}")
    print(f"REFERENCE PROMPT:\n{result.reference_prompt[:500]}...")


if __name__ == "__main__":
    main()
