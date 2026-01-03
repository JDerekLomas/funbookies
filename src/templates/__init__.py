"""
Level-specific book templates for Funbookies.

Templates define:
- Word constraints (max per page, allowed patterns)
- Approved word lists
- Story structure (pages, pacing)
- Sentence patterns
- Example stories

Usage:
    from templates import get_template, get_template_prompt

    # Get full template data
    template = get_template("orange")

    # Get prompt constraints for LLM
    prompt = get_template_prompt("orange")
"""

import json
from pathlib import Path
from typing import Optional

TEMPLATE_DIR = Path(__file__).parent


def get_template(level: str) -> dict:
    """Load a level template by name."""
    template_path = TEMPLATE_DIR / f"level_{level}.json"

    if not template_path.exists():
        raise ValueError(f"Unknown level: {level}. Available: yellow, orange, red, purple")

    with open(template_path, 'r') as f:
        return json.load(f)


def get_all_templates() -> dict:
    """Load all templates."""
    templates = {}
    for level in ["yellow", "orange", "red", "purple"]:
        try:
            templates[level] = get_template(level)
        except ValueError:
            pass
    return templates


def get_template_prompt(level: str) -> str:
    """
    Generate LLM prompt constraints from a template.

    Returns a formatted string suitable for including in system prompts.
    """
    template = get_template(level)

    constraints = template.get("constraints", {})
    word_lists = template.get("word_lists", {})
    sentence_patterns = template.get("sentence_patterns", {})

    lines = [
        f"=== PHONICS LEVEL: {level.upper()} ({template.get('name', '')}) ===",
        f"Target age: {template.get('target_age', 'N/A')}",
        f"Target grade: {template.get('target_grade', 'N/A')}",
        "",
        "CONSTRAINTS:",
        f"- Max words per page: {constraints.get('max_words_per_page', 8)}",
        f"- Allowed patterns: {', '.join(constraints.get('decodable_patterns', []))}",
        f"- FORBIDDEN patterns: {', '.join(constraints.get('forbidden_patterns', []))}",
        "",
        "APPROVED SIGHT WORDS:",
    ]

    sight_words = word_lists.get("approved_sight_words", [])
    if isinstance(sight_words, list):
        lines.append(", ".join(sight_words[:40]))
        if len(sight_words) > 40:
            lines.append(f"... and {len(sight_words) - 40} more")
    else:
        lines.append(str(sight_words))

    lines.append("")
    lines.append("SOUND EFFECTS (use these!):")
    sounds = word_lists.get("sound_effects", [])
    if isinstance(sounds, list):
        lines.append(", ".join(sounds[:15]))

    lines.append("")
    lines.append("SENTENCE PATTERNS:")
    for pattern_type, patterns in sentence_patterns.items():
        if isinstance(patterns, list) and patterns:
            lines.append(f"  {pattern_type}: {patterns[0]}")

    return "\n".join(lines)


def get_example_story(level: str) -> Optional[dict]:
    """Get the example story from a template if available."""
    template = get_template(level)
    return template.get("example_story")


def list_levels() -> list:
    """List available levels."""
    return ["yellow", "orange", "red", "purple"]


def get_level_info(level: str) -> dict:
    """Get summary info about a level."""
    template = get_template(level)
    return {
        "level": level,
        "name": template.get("name", ""),
        "description": template.get("description", ""),
        "target_age": template.get("target_age", ""),
        "target_grade": template.get("target_grade", ""),
        "max_words_per_page": template.get("constraints", {}).get("max_words_per_page", 8),
        "decodable_patterns": template.get("constraints", {}).get("decodable_patterns", []),
    }


if __name__ == "__main__":
    print("Available levels:")
    for level in list_levels():
        info = get_level_info(level)
        print(f"\n{level.upper()}: {info['name']}")
        print(f"  {info['description']}")
        print(f"  Age: {info['target_age']}, Grade: {info['target_grade']}")
        print(f"  Max words/page: {info['max_words_per_page']}")
        print(f"  Patterns: {', '.join(info['decodable_patterns'])}")
