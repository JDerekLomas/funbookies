#!/usr/bin/env python3
"""
Story Validator for Children's Book Image Generation

Validates story logic, visual continuity, and scene descriptions BEFORE
image generation to catch issues like:
- Props appearing in wrong locations
- Characters appearing when they shouldn't
- Template/repetitive text
- Scene descriptions that contradict the story

Run this BEFORE generating images to catch logical errors.
"""

import json
import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
from anthropic import Anthropic

from dotenv import load_dotenv
PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / ".env")
load_dotenv(PROJECT_ROOT / ".env.local")

client = Anthropic()


@dataclass
class PropState:
    """Track where a prop is across pages."""
    name: str
    current_location: str
    location_history: list = field(default_factory=list)


@dataclass
class CharacterState:
    """Track where a character is and what they're doing."""
    name: str
    current_location: str
    current_action: str
    with_characters: list = field(default_factory=list)


@dataclass
class ValidationIssue:
    """A detected issue in the story."""
    page: int
    severity: str  # "error", "warning", "suggestion"
    category: str  # "continuity", "character", "text", "scene"
    message: str
    suggestion: Optional[str] = None


def validate_story_with_llm(book: dict) -> list[ValidationIssue]:
    """Use Claude to validate the entire story for logical issues."""

    # Build a summary of the story for validation
    pages_summary = []
    for page in book.get("pages", []):
        if page.get("type") not in ["story", "cover", "end"]:
            continue
        pages_summary.append({
            "page": page.get("page"),
            "type": page.get("type"),
            "text": page.get("text", ""),
            "scene": page.get("scene", ""),
        })

    system_prompt = """You are a story editor specializing in children's picture books. Your job is to find LOGICAL and VISUAL CONTINUITY errors that would cause problems when the scenes are illustrated.

CRITICAL: Image generators will FILL IN any unspecified details. If a scene description doesn't say where a prop is, the generator might place it ANYWHERE - often incorrectly!

Focus on these specific issues:

1. **PROP CONTINUITY** - THE MOST IMPORTANT CHECK!
   - Every scene description MUST explicitly state where important props are
   - If a prop moved to a specific location (ball rolled INTO tunnel), EVERY subsequent scene MUST state where it is
   - ERROR: Ball rolled into tunnel on page 4, but pages 5-6 don't mention ball location at all (generator might show ball outside!)
   - ERROR: Scene says "Rex at tunnel entrance" but doesn't say "ball visible INSIDE dark tunnel"
   - ERROR: Scene focuses on character's face but doesn't mention the prop that's central to the story
   - RULE: After a prop moves to a location, EVERY scene until retrieval must say "[prop] still inside [location]" or similar

2. **CHARACTER PRESENCE** - Characters should only appear in scenes where the story says they are.
   - ERROR: Text says character went alone, but scene description doesn't explicitly EXCLUDE other characters
   - FIX: Scene should say "ONLY Rex visible" or "Rosie NOT in scene"
   - ERROR: Character arrives on page 6 but scene description on page 4 doesn't exclude them

3. **TEMPLATE TEXT** - Flag generic, lazy openings that could apply to any story.
   - WARNING: "[X] and [Y] were pals. They had fun in the sun!" is template text
   - WARNING: "One sunny day..." is overused

4. **SCENE-TEXT MISMATCH** - Scene descriptions must match what the text says is happening.
   - ERROR: Text says character is scared, scene says "happy expression"
   - ERROR: Text says character is alone, scene includes other characters

5. **STORY LOGIC** - The plot must make sense.
   - ERROR: The problem is already solved before the climax
   - ERROR: Stakes are undermined by scene showing solution prematurely

CHECK EACH PAGE: For each page, verify that EVERY important prop's location is explicitly stated in the scene description!

Return a JSON array of issues:
[
  {
    "page": 5,
    "severity": "error",
    "category": "continuity",
    "message": "Scene doesn't specify ball location - ball is INSIDE tunnel but scene just says 'Rex looking scared at tunnel entrance'",
    "suggestion": "Add to scene: 'Red ball visible as small bright spot INSIDE the dark tunnel opening'"
  }
]

Return ONLY the JSON array. If no issues found, return []."""

    user_prompt = f"""Validate this children's book for visual continuity and story logic:

TITLE: {book.get('title', 'Unknown')}

STORY SUMMARY:
{book.get('story_bible', {}).get('plot_summary', book.get('summary', 'Not provided'))}

KEY PROPS:
{json.dumps(book.get('props', {}), indent=2)}

CHARACTERS:
{json.dumps({k: v.get('name', k) for k, v in book.get('characters', {}).items()}, indent=2)}

PAGES:
{json.dumps(pages_summary, indent=2)}

Find all logical, continuity, and template text issues. Return JSON array of issues."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=3000,
        messages=[{"role": "user", "content": user_prompt}],
        system=system_prompt,
    )

    response_text = response.content[0].text

    # Parse JSON response
    try:
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]

        issues_data = json.loads(response_text.strip())

        return [
            ValidationIssue(
                page=issue.get("page", 0),
                severity=issue.get("severity", "warning"),
                category=issue.get("category", "unknown"),
                message=issue.get("message", ""),
                suggestion=issue.get("suggestion"),
            )
            for issue in issues_data
        ]
    except json.JSONDecodeError:
        return [ValidationIssue(
            page=0,
            severity="error",
            category="system",
            message=f"Failed to parse validation response: {response_text[:200]}",
        )]


def check_template_text(book: dict) -> list[ValidationIssue]:
    """Check for template/repetitive text patterns."""

    TEMPLATE_PATTERNS = [
        ("were pals", "Generic friendship intro"),
        ("had fun in the sun", "Cliché rhyme"),
        ("One sunny day", "Overused opening"),
        ("Once upon a time", "Fairy tale cliché for decodable"),
        ("happily ever after", "Cliché ending"),
        ("The end", "Consider something more specific to story"),
    ]

    issues = []

    for page in book.get("pages", []):
        text = page.get("text", "").lower()
        page_num = page.get("page", 0)

        for pattern, reason in TEMPLATE_PATTERNS:
            if pattern.lower() in text:
                issues.append(ValidationIssue(
                    page=page_num,
                    severity="warning",
                    category="text",
                    message=f"Template text detected: '{pattern}' - {reason}",
                    suggestion="Write a unique, story-specific version",
                ))

    return issues


def check_prop_continuity(book: dict) -> list[ValidationIssue]:
    """Check that props are tracked across all scene descriptions."""

    issues = []
    props = book.get("props", {})

    if not props:
        return issues

    # Track when each prop is "active" (mentioned in story)
    prop_names = [p.get("name", k).lower() for k, p in props.items()]

    # Find the page where each prop is introduced
    prop_introduced = {}
    prop_last_seen = {}

    for page in book.get("pages", []):
        if page.get("type") not in ["story", "cover", "end"]:
            continue

        text = page.get("text", "").lower()
        scene = page.get("scene", "").lower()
        page_num = page.get("page", 0)

        for prop_name in prop_names:
            # Check if prop is mentioned in text
            if prop_name in text or any(word in text for word in prop_name.split()):
                if prop_name not in prop_introduced:
                    prop_introduced[prop_name] = page_num

                # After prop is introduced, check if it's in scene description
                if prop_name in prop_introduced:
                    prop_words = prop_name.split()
                    prop_in_scene = any(word in scene for word in prop_words)

                    if prop_in_scene:
                        prop_last_seen[prop_name] = page_num
                    else:
                        # Prop is in text but not in scene - potential issue!
                        issues.append(ValidationIssue(
                            page=page_num,
                            severity="warning",
                            category="continuity",
                            message=f"Prop '{prop_name}' mentioned in text but not tracked in scene description",
                            suggestion=f"Add explicit mention of where the {prop_name} is in this scene",
                        ))

    # Check for props that disappear from scenes after being introduced
    for page in book.get("pages", []):
        if page.get("type") not in ["story", "cover", "end"]:
            continue

        text = page.get("text", "").lower()
        scene = page.get("scene", "").lower()
        page_num = page.get("page", 0)

        for prop_name in prop_names:
            if prop_name in prop_introduced:
                intro_page = prop_introduced[prop_name]
                # If prop was introduced and this is after, but prop not in scene or text
                if page_num > intro_page:
                    prop_words = prop_name.split()
                    prop_in_scene = any(word in scene for word in prop_words)
                    prop_in_text = any(word in text for word in prop_words)

                    if not prop_in_scene and not prop_in_text:
                        # Check if prop should still be visible
                        # This is a potential continuity gap
                        pass  # This is handled by LLM validation for now

    return issues


def check_scene_character_consistency(book: dict) -> list[ValidationIssue]:
    """Check that scenes match character presence in text."""

    issues = []
    characters = list(book.get("characters", {}).keys())

    # Keywords that suggest solo scenes
    SOLO_KEYWORDS = ["alone", "by himself", "by herself", "on his own", "on her own"]

    for page in book.get("pages", []):
        if page.get("type") not in ["story", "cover", "end"]:
            continue

        text = page.get("text", "").lower()
        scene = page.get("scene", "").lower()
        page_num = page.get("page", 0)

        # Check for "alone" in text but multiple characters in scene
        for keyword in SOLO_KEYWORDS:
            if keyword in text:
                # Count character mentions in scene
                chars_in_scene = [c for c in characters if c.lower() in scene]
                if len(chars_in_scene) > 1:
                    issues.append(ValidationIssue(
                        page=page_num,
                        severity="error",
                        category="character",
                        message=f"Text says '{keyword}' but scene includes multiple characters: {chars_in_scene}",
                        suggestion=f"Scene should only include the solo character",
                    ))

    return issues


def validate_book(book_path: Path, verbose: bool = True) -> list[ValidationIssue]:
    """Run all validations on a book."""

    with open(book_path) as f:
        book = json.load(f)

    all_issues = []

    if verbose:
        print(f"Validating: {book.get('title', book_path.name)}")
        print("=" * 60)

    # Run template text check
    if verbose:
        print("\n[1/3] Checking for template text...")
    template_issues = check_template_text(book)
    all_issues.extend(template_issues)
    if verbose and template_issues:
        for issue in template_issues:
            print(f"  Page {issue.page}: {issue.message}")

    # Run character consistency check
    if verbose:
        print("\n[2/3] Checking character presence in scenes...")
    char_issues = check_scene_character_consistency(book)
    all_issues.extend(char_issues)
    if verbose and char_issues:
        for issue in char_issues:
            print(f"  Page {issue.page}: {issue.message}")

    # Run LLM validation for deeper issues
    if verbose:
        print("\n[3/3] Running LLM story logic validation...")
    llm_issues = validate_story_with_llm(book)
    all_issues.extend(llm_issues)
    if verbose and llm_issues:
        for issue in llm_issues:
            icon = "❌" if issue.severity == "error" else "⚠️" if issue.severity == "warning" else "💡"
            print(f"  {icon} Page {issue.page} [{issue.category}]: {issue.message}")
            if issue.suggestion:
                print(f"     → {issue.suggestion}")

    # Summary
    if verbose:
        print("\n" + "=" * 60)
        errors = [i for i in all_issues if i.severity == "error"]
        warnings = [i for i in all_issues if i.severity == "warning"]
        print(f"Found {len(errors)} errors, {len(warnings)} warnings")

        if errors:
            print("\n⛔ ERRORS MUST BE FIXED BEFORE IMAGE GENERATION:")
            for e in errors:
                print(f"   - Page {e.page}: {e.message}")

    return all_issues


# CLI interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Validate story before image generation")
    parser.add_argument("slug", help="Book slug")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--quiet", action="store_true", help="Only show errors")

    args = parser.parse_args()

    books_dir = PROJECT_ROOT / "public" / "books"
    book_path = books_dir / f"{args.slug}.json"

    if not book_path.exists():
        print(f"Book not found: {book_path}")
        exit(1)

    issues = validate_book(book_path, verbose=not args.json)

    if args.json:
        output = [
            {
                "page": i.page,
                "severity": i.severity,
                "category": i.category,
                "message": i.message,
                "suggestion": i.suggestion,
            }
            for i in issues
        ]
        print(json.dumps(output, indent=2))

    # Exit with error code if there are errors
    errors = [i for i in issues if i.severity == "error"]
    exit(1 if errors else 0)
