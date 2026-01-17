#!/usr/bin/env python3
"""
Prompt Enhancement Pipeline for Children's Book Image Generation

This module transforms simple scene descriptions into literal, physical prompts
that AI image generators can accurately render. It includes:

1. Story Context Analysis - Understanding where we are in the narrative
2. Character Presence Logic - Who MUST be in scene, who MUST NOT
3. Emotional → Physical Translation - Converting mood words to visual descriptions
4. LLM Review & Scoring - Validating prompts before expensive generation
5. Reference Panel Selection - Choosing optimal reference panels per scene
"""

import json
import os
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
from anthropic import Anthropic

from dotenv import load_dotenv
PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / ".env")
load_dotenv(PROJECT_ROOT / ".env.local")

# Initialize Anthropic client
client = Anthropic()


@dataclass
class EnhancedPrompt:
    """Result of prompt enhancement."""
    original_scene: str
    enhanced_prompt: str
    characters_included: list[str]
    characters_excluded: list[str]
    emotional_beat: str
    physical_descriptions: list[str]
    recommended_reference_panels: list[int]
    review_score: Optional[int] = None
    review_notes: Optional[str] = None
    issues: Optional[list[str]] = None


@dataclass
class StoryContext:
    """Context about where this page sits in the story."""
    page_number: int
    story_page_number: int  # Actual story page (excluding front matter)
    total_story_pages: int
    act: str  # "setup", "conflict", "climax", "resolution"
    emotional_beat: str
    previous_page_summary: Optional[str]
    next_page_summary: Optional[str]
    characters_in_story: list[str]


def analyze_story_context(book: dict, page: dict) -> StoryContext:
    """Analyze where this page fits in the story arc."""

    pages = book.get("pages", [])
    story_pages = [p for p in pages if p.get("type") == "story"]
    total_story_pages = len(story_pages)

    page_num = page.get("page", 0)
    story_page_num = page.get("story_page", 0)

    # Determine act based on position
    if total_story_pages > 0:
        position = story_page_num / total_story_pages
        if position <= 0.25:
            act = "setup"
        elif position <= 0.6:
            act = "conflict"
        elif position <= 0.85:
            act = "climax"
        else:
            act = "resolution"
    else:
        act = "unknown"

    # Get emotional beat from story_bible if available
    emotional_beat = ""
    story_bible = book.get("story_bible", {})
    for beat in story_bible.get("emotional_beats", []):
        if beat.get("page") == story_page_num:
            emotional_beat = beat.get("beat", "")
            break

    # Get previous/next page context
    prev_summary = None
    next_summary = None
    for i, p in enumerate(story_pages):
        if p.get("story_page") == story_page_num:
            if i > 0:
                prev_summary = story_pages[i-1].get("text", "")
            if i < len(story_pages) - 1:
                next_summary = story_pages[i+1].get("text", "")
            break

    # Extract character names
    characters = []
    for key, char_data in book.get("characters", {}).items():
        if isinstance(char_data, dict):
            characters.append(char_data.get("name", key.capitalize()))
        else:
            characters.append(key.capitalize())

    return StoryContext(
        page_number=page_num,
        story_page_number=story_page_num,
        total_story_pages=total_story_pages,
        act=act,
        emotional_beat=emotional_beat,
        previous_page_summary=prev_summary,
        next_page_summary=next_summary,
        characters_in_story=characters,
    )


def get_character_descriptions(book: dict) -> dict[str, dict]:
    """Extract detailed character descriptions from book."""
    result = {}
    for key, char_data in book.get("characters", {}).items():
        if isinstance(char_data, dict):
            name = char_data.get("name", key.capitalize())
            result[name] = {
                "visual_shorthand": char_data.get("visual_shorthand", ""),
                "distinctive_features": char_data.get("distinctive_features", []),
                "name": name,
            }
    return result


def enhance_prompt_with_llm(
    book: dict,
    page: dict,
    context: StoryContext,
    verbose: bool = False
) -> EnhancedPrompt:
    """Use Claude to enhance a scene description into a literal, physical prompt."""

    scene = page.get("scene", "")
    text = page.get("text", "")
    characters = get_character_descriptions(book)
    story_bible = book.get("story_bible", {})

    system_prompt = """You are an expert at converting vague scene descriptions into precise, literal prompts for AI image generation.

Your job is to transform mood-based descriptions into PHYSICAL, VISUAL descriptions that an image generator can accurately render.

CRITICAL RULES:
1. NEVER use emotional/mood words (panicked, scared, happy) - describe the PHYSICAL manifestation instead
2. ALWAYS specify exactly which characters are in the scene
3. ALWAYS specify which characters are NOT in the scene (if they might be confused)
4. Convert emotional states to body language and facial expressions
5. Be extremely literal about physical positioning and scale
6. Include specific colors, textures, and visual details
7. Describe what IS visible, not what is happening narratively

EMOTIONAL → PHYSICAL TRANSLATIONS:
- "scared/panicked" → "eyes wide open, mouth agape, eyebrows raised high, body leaning back"
- "happy/joyful" → "wide smile showing teeth, eyes crinkled, cheeks raised"
- "sad/worried" → "downturned mouth, eyebrows furrowed inward, shoulders slumped"
- "stuck in mud" → "body buried up to [specific point], only [parts] visible above surface"
- "running away" → "legs extended mid-stride, arms pumping, body leaning forward"

OUTPUT FORMAT (JSON):
{
  "enhanced_prompt": "The full enhanced prompt text",
  "characters_included": ["Name1", "Name2"],
  "characters_excluded": ["Name3"],
  "physical_descriptions": ["specific physical detail 1", "detail 2"],
  "recommended_panels": [1, 5]  // Which reference panels to use (1-9)
}

Reference panel guide:
- Panels 1-2: Individual character studies
- Panel 5: Characters together (center hero shot)
- Panels 7-9: Settings/environments"""

    user_prompt = f"""STORY CONTEXT:
- Book: {book.get('title', 'Unknown')}
- Page {context.story_page_number} of {context.total_story_pages}
- Story act: {context.act}
- Emotional beat: {context.emotional_beat}
- Previous page: "{context.previous_page_summary or 'N/A'}"
- Current page text: "{text}"
- Next page: "{context.next_page_summary or 'N/A'}"

CHARACTERS IN STORY:
{json.dumps(characters, indent=2)}

PLOT SUMMARY:
{story_bible.get('plot_summary', 'Not available')[:500]}

ORIGINAL SCENE DESCRIPTION:
"{scene}"

VISUAL STYLE:
{story_bible.get('visual_style', 'Watercolor children\'s book illustration')}

Transform this scene into a precise, physical, literal prompt. Pay special attention to:
1. Based on the story context, which characters should/shouldn't be in this specific scene?
2. What is the PHYSICAL state of each character (not emotional)?
3. What specific visual details would show this moment clearly?

Return JSON only."""

    if verbose:
        print(f"  Enhancing prompt for page {context.story_page_number}...")

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        messages=[
            {"role": "user", "content": user_prompt}
        ],
        system=system_prompt,
    )

    # Parse response
    response_text = response.content[0].text

    # Extract JSON from response
    try:
        # Handle case where response might have markdown code blocks
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]

        result = json.loads(response_text)
    except json.JSONDecodeError:
        # Fallback if JSON parsing fails
        result = {
            "enhanced_prompt": scene,  # Use original
            "characters_included": context.characters_in_story,
            "characters_excluded": [],
            "physical_descriptions": [],
            "recommended_panels": [5],
        }

    return EnhancedPrompt(
        original_scene=scene,
        enhanced_prompt=result.get("enhanced_prompt", scene),
        characters_included=result.get("characters_included", []),
        characters_excluded=result.get("characters_excluded", []),
        emotional_beat=context.emotional_beat,
        physical_descriptions=result.get("physical_descriptions", []),
        recommended_reference_panels=result.get("recommended_panels", [5]),
    )


def review_prompt_with_llm(
    enhanced: EnhancedPrompt,
    book: dict,
    context: StoryContext,
    verbose: bool = False
) -> EnhancedPrompt:
    """Have Claude review and score the enhanced prompt before generation."""

    characters = get_character_descriptions(book)

    system_prompt = """You are a quality reviewer for AI image generation prompts for children's books.

Score the prompt from 1-10 and identify any issues that would cause generation problems.

SCORING CRITERIA:
- 9-10: Perfect - physically specific, correct characters, clear composition
- 7-8: Good - minor improvements possible but should generate correctly
- 5-6: Acceptable - some vagueness but main elements clear
- 3-4: Problematic - likely to generate wrong characters or emotions
- 1-2: Fail - will definitely generate incorrectly

COMMON ISSUES TO CHECK:
1. Wrong characters present (character should be alone but prompt doesn't exclude others)
2. Emotional words without physical translation
3. Vague positioning ("in the scene" vs specific placement)
4. Missing key character identifiers (colors, distinctive features)
5. Ambiguous scale or size relationships
6. Story continuity errors (character in wrong location for this plot point)

OUTPUT FORMAT (JSON):
{
  "score": 8,
  "issues": ["Issue 1 if any", "Issue 2 if any"],
  "notes": "Brief explanation of score",
  "suggested_fix": "Optional improved prompt if score < 7"
}"""

    user_prompt = f"""STORY CONTEXT:
- Page {context.story_page_number} of {context.total_story_pages}
- Act: {context.act}
- Emotional beat: {context.emotional_beat}
- Page text: "{book.get('pages', [{}])[context.page_number-1].get('text', '')}"

CHARACTERS IN STORY:
{json.dumps(characters, indent=2)}

PROMPT TO REVIEW:
"{enhanced.enhanced_prompt}"

Characters supposedly included: {enhanced.characters_included}
Characters supposedly excluded: {enhanced.characters_excluded}

Review this prompt and return JSON with score, issues, and notes."""

    if verbose:
        print(f"  Reviewing enhanced prompt...")

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=800,
        messages=[
            {"role": "user", "content": user_prompt}
        ],
        system=system_prompt,
    )

    response_text = response.content[0].text

    try:
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]

        result = json.loads(response_text)
    except json.JSONDecodeError:
        result = {"score": 5, "issues": ["Could not parse review"], "notes": "Review failed"}

    # Update the enhanced prompt with review results
    enhanced.review_score = result.get("score", 5)
    enhanced.review_notes = result.get("notes", "")
    enhanced.issues = result.get("issues", [])

    # If score is low and there's a suggested fix, use it
    if enhanced.review_score < 7 and result.get("suggested_fix"):
        if verbose:
            print(f"  Score {enhanced.review_score}/10 - applying suggested fix")
        enhanced.enhanced_prompt = result["suggested_fix"]

    return enhanced


def build_final_prompt(
    enhanced: EnhancedPrompt,
    book: dict,
    include_reference_instruction: bool = True,
) -> str:
    """Build the final prompt string for image generation."""

    # Get character block
    char_lines = []
    characters = get_character_descriptions(book)
    for name in enhanced.characters_included:
        if name in characters:
            char = characters[name]
            shorthand = char.get("visual_shorthand", "")
            features = char.get("distinctive_features", [])
            if shorthand:
                feature_str = " | ".join([f for f in features[:2] if "(KEY)" in f or features.index(f) == 0])
                char_lines.append(f"{name}: {shorthand}" + (f" | {feature_str}" if feature_str else ""))

    char_block = "\n".join(char_lines)

    # Get style
    story_bible = book.get("story_bible", {})
    style = story_bible.get("visual_style", "Watercolor children's book illustration")

    # Build exclusion note
    exclusion_note = ""
    if enhanced.characters_excluded:
        exclusion_note = f"\n\nCRITICAL - DO NOT INCLUDE: {', '.join(enhanced.characters_excluded)}. These characters must NOT appear in this image."

    # Assemble final prompt
    parts = []

    if include_reference_instruction:
        parts.append("Generate an image using the style of image 1.")
        parts.append("")

    parts.append(enhanced.enhanced_prompt)

    if char_block:
        parts.append("")
        parts.append("CHARACTERS IN THIS SCENE (draw EXACTLY as described):")
        parts.append(char_block)

    if exclusion_note:
        parts.append(exclusion_note)

    parts.append("")
    parts.append(f"STYLE: {style}")
    parts.append("")
    parts.append("IMPORTANT: NO TEXT, NO WORDS, NO LETTERS in the image. Visual storytelling only.")

    return "\n".join(parts)


def enhance_book_prompts(
    book_path: Path,
    pages: list[int] = None,
    verbose: bool = True,
    review: bool = True,
) -> dict[int, EnhancedPrompt]:
    """Enhance prompts for specified pages (or all story pages) in a book."""

    with open(book_path) as f:
        book = json.load(f)

    results = {}

    for page in book.get("pages", []):
        if page.get("type") != "story" and page.get("type") != "cover" and page.get("type") != "end":
            continue

        if not page.get("scene"):
            continue

        page_num = page.get("page", 0)

        # Filter to specific pages if requested
        if pages and page_num not in pages:
            continue

        if verbose:
            print(f"\n[Page {page_num}]")
            print(f"  Original: {page.get('scene', '')[:80]}...")

        # Analyze context
        context = analyze_story_context(book, page)

        # Enhance prompt
        enhanced = enhance_prompt_with_llm(book, page, context, verbose=verbose)

        # Review if requested
        if review:
            enhanced = review_prompt_with_llm(enhanced, book, context, verbose=verbose)
            if verbose:
                print(f"  Score: {enhanced.review_score}/10")
                if enhanced.issues:
                    print(f"  Issues: {enhanced.issues}")

        if verbose:
            print(f"  Enhanced: {enhanced.enhanced_prompt[:80]}...")
            print(f"  Include: {enhanced.characters_included}")
            print(f"  Exclude: {enhanced.characters_excluded}")

        results[page_num] = enhanced

    return results


# CLI interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Enhance image generation prompts")
    parser.add_argument("slug", help="Book slug")
    parser.add_argument("--pages", help="Comma-separated page numbers (e.g., 11,12,13)")
    parser.add_argument("--no-review", action="store_true", help="Skip LLM review step")
    parser.add_argument("--output", help="Output JSON file for enhanced prompts")
    parser.add_argument("--quiet", action="store_true", help="Minimal output")

    args = parser.parse_args()

    # Find book
    books_dir = PROJECT_ROOT / "public" / "books"
    book_path = books_dir / f"{args.slug}.json"

    if not book_path.exists():
        print(f"Book not found: {book_path}")
        exit(1)

    # Parse pages
    pages = None
    if args.pages:
        pages = [int(p.strip()) for p in args.pages.split(",")]

    # Enhance
    results = enhance_book_prompts(
        book_path,
        pages=pages,
        verbose=not args.quiet,
        review=not args.no_review,
    )

    # Output
    if args.output:
        output_data = {
            page_num: {
                "original_scene": ep.original_scene,
                "enhanced_prompt": ep.enhanced_prompt,
                "characters_included": ep.characters_included,
                "characters_excluded": ep.characters_excluded,
                "review_score": ep.review_score,
                "review_notes": ep.review_notes,
                "issues": ep.issues,
                "recommended_panels": ep.recommended_reference_panels,
            }
            for page_num, ep in results.items()
        }

        with open(args.output, 'w') as f:
            json.dump(output_data, f, indent=2)
        print(f"\nSaved enhanced prompts to {args.output}")

    # Summary
    print(f"\n{'='*60}")
    print(f"Enhanced {len(results)} prompts")
    if not args.no_review:
        scores = [ep.review_score for ep in results.values() if ep.review_score]
        if scores:
            avg_score = sum(scores) / len(scores)
            print(f"Average review score: {avg_score:.1f}/10")
            low_scores = [p for p, ep in results.items() if ep.review_score and ep.review_score < 7]
            if low_scores:
                print(f"Pages needing attention: {low_scores}")
