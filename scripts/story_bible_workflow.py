#!/usr/bin/env python3
"""
Story Bible Workflow: Generate books from rich narratives.

Workflow:
1. Story Bible First - Write rich narrative without level constraints
2. Level Adaptation - Simplify text while preserving emotional beats
3. Scene Descriptions - Generate image prompts from story bible
4. Reference/Page Generation - Create images (separate step)

Usage:
    python story_bible_workflow.py --premise "A shy octopus learns to make friends" --band B --title "Otto's New Friends"
    python story_bible_workflow.py --from-bible existing_bible.json --band A
    python story_bible_workflow.py --improve public/books/some_book.json
"""

import json
import argparse
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional

BOOKS_DIR = Path("/Users/dereklomas/lilbookies/public/books")

# Reading level specifications
LEVEL_SPECS = {
    "A": {
        "name": "Pre-Reader",
        "age_range": "3-5",
        "words_per_page": "1-5",
        "sentence_structure": "Single words or 2-3 word phrases",
        "vocabulary": "High-frequency sight words, simple nouns",
        "phonics_focus": "Letter recognition, initial sounds",
        "page_count": "8-12 story pages",
        "example": "I see a cat. The cat sat."
    },
    "B": {
        "name": "Emergent Reader",
        "age_range": "4-6",
        "words_per_page": "5-15",
        "sentence_structure": "Simple sentences with CVC words",
        "vocabulary": "CVC words, basic sight words",
        "phonics_focus": "Short vowels, word families (-at, -an, -ig)",
        "page_count": "12-16 story pages",
        "example": "The pup ran to the mud. It is fun! The pup got wet."
    },
    "C": {
        "name": "Early Fluent",
        "age_range": "6-8",
        "words_per_page": "15-40",
        "sentence_structure": "Varied sentences, some compound",
        "vocabulary": "Blends, digraphs, longer words",
        "phonics_focus": "Consonant blends, long vowels, digraphs",
        "page_count": "16-24 story pages",
        "example": "The knight walked through the dark forest. He heard a strange sound and stopped to listen."
    },
    "D": {
        "name": "Fluent Reader",
        "age_range": "8-10",
        "words_per_page": "40-80",
        "sentence_structure": "Complex and compound sentences, dialogue",
        "vocabulary": "Multi-syllable words, descriptive language",
        "phonics_focus": "Advanced patterns, vocabulary building",
        "page_count": "24-48 story pages",
        "example": "Although Maya was only eleven, she decided she would help keep the lighthouse running while her grandmother rested."
    }
}


@dataclass
class StoryBible:
    """Rich narrative structure for book creation."""
    premise: str
    themes: list[str]
    character_arcs: dict[str, str]
    setting: str = ""
    plot_summary: str = ""
    emotional_beats: list[dict] = field(default_factory=list)
    level_adaptation: str = ""
    visual_style: str = ""
    key_vocabulary: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "StoryBible":
        return cls(**data)


@dataclass
class BookPage:
    """A single page in the book."""
    page: int
    type: str  # cover, story, end, etc.
    text: str = ""
    scene: str = ""
    story_page: Optional[int] = None
    shot_type: str = "medium"


def generate_story_bible_prompt(premise: str, target_band: str) -> str:
    """Generate a prompt for creating a story bible from a premise."""
    spec = LEVEL_SPECS.get(target_band, LEVEL_SPECS["B"])

    return f"""Create a detailed story bible for a children's book.

PREMISE: {premise}

TARGET READING LEVEL: Band {target_band} ({spec['name']}, ages {spec['age_range']})

Generate a complete story bible with:

1. PREMISE (2-3 sentences): Expand the core concept with emotional stakes

2. THEMES (3-5 themes): What lessons or ideas does this story explore?

3. CHARACTER ARCS: For each main character, describe their journey:
   - Starting state
   - What challenges them
   - How they transform
   - End state

4. SETTING: Rich description of where and when this takes place. Include:
   - Physical environment
   - Atmosphere and mood
   - Sensory details (what would you see, hear, feel?)

5. PLOT SUMMARY: Full narrative in 2-3 paragraphs. Don't simplify for reading level yet - tell the complete story with emotional complexity.

6. EMOTIONAL BEATS: List 8-12 key emotional moments that MUST be preserved when adapting to reading level. Format:
   - Beat 1: [emotion] - [what happens]
   - Beat 2: [emotion] - [what happens]
   ...

7. VISUAL STYLE: Art direction notes for illustrations:
   - Overall style (watercolor, cartoon, realistic, etc.)
   - Color palette
   - Character design notes
   - Mood/lighting guidance

8. KEY VOCABULARY: 5-8 words that are essential to the story regardless of reading level

Output as JSON matching this schema:
{{
  "premise": "string",
  "themes": ["string"],
  "character_arcs": {{"CharacterName": "arc description"}},
  "setting": "string",
  "plot_summary": "string",
  "emotional_beats": [{{"page": number, "beat": "string"}}],
  "visual_style": "string",
  "key_vocabulary": ["string"]
}}"""


def generate_level_adaptation_prompt(story_bible: StoryBible, target_band: str, page_count: int) -> str:
    """Generate a prompt for adapting the story to a reading level."""
    spec = LEVEL_SPECS.get(target_band, LEVEL_SPECS["B"])

    return f"""Adapt this story to Band {target_band} reading level.

STORY BIBLE:
Premise: {story_bible.premise}
Plot Summary: {story_bible.plot_summary}
Themes: {', '.join(story_bible.themes)}
Emotional Beats: {json.dumps(story_bible.emotional_beats, indent=2)}
Key Vocabulary: {', '.join(story_bible.key_vocabulary)}

LEVEL REQUIREMENTS:
- Level: Band {target_band} ({spec['name']})
- Age Range: {spec['age_range']}
- Words per page: {spec['words_per_page']}
- Sentence structure: {spec['sentence_structure']}
- Vocabulary focus: {spec['vocabulary']}
- Phonics focus: {spec['phonics_focus']}
- Target page count: {page_count} story pages
- Example text: "{spec['example']}"

INSTRUCTIONS:
1. Break the story into {page_count} pages
2. Each page should have text appropriate for the reading level
3. PRESERVE all emotional beats - the simplified text should still hit these moments
4. Use the key vocabulary naturally
5. The text may be simple, but the STORY should not be dumbed down
6. Let illustrations carry emotional complexity that text cannot

Output as JSON array:
[
  {{"story_page": 1, "text": "Simple text for page", "emotional_beat": "which beat this captures"}},
  ...
]"""


def generate_scene_prompts(story_bible: StoryBible, pages: list[dict]) -> str:
    """Generate a prompt for creating scene descriptions."""
    return f"""Generate illustration scene descriptions for each page.

STORY BIBLE:
Setting: {story_bible.setting}
Visual Style: {story_bible.visual_style}
Character Arcs: {json.dumps(story_bible.character_arcs, indent=2)}
Emotional Beats: {json.dumps(story_bible.emotional_beats, indent=2)}

PAGES TO ILLUSTRATE:
{json.dumps(pages, indent=2)}

For each page, generate a scene description that:
1. Matches the visual style notes
2. Shows the emotional beat for that page
3. Maintains character consistency
4. Uses specific, vivid details
5. Specifies shot type (wide, medium, close)
6. Does NOT include any text or words in the image

Output as JSON array:
[
  {{"story_page": 1, "scene": "Detailed scene description...", "shot_type": "wide|medium|close"}},
  ...
]"""


def create_book_structure(
    title: str,
    slug: str,
    band: str,
    story_bible: StoryBible,
    pages: list[dict]
) -> dict:
    """Create the complete book JSON structure."""
    spec = LEVEL_SPECS.get(band, LEVEL_SPECS["B"])

    # Build page list with structural pages
    book_pages = []
    page_num = 1

    # Cover
    book_pages.append({
        "page": page_num,
        "type": "cover",
        "text": title,
        "scene": f"Book cover for '{title}'. {pages[0].get('scene', story_bible.setting)}",
        "shot_type": "wide"
    })
    page_num += 1

    # Copyright
    book_pages.append({"page": page_num, "type": "copyright"})
    page_num += 1

    # Parent guide
    book_pages.append({"page": page_num, "type": "parent_guide"})
    page_num += 1

    # Level info
    book_pages.append({"page": page_num, "type": "level_info"})
    page_num += 1

    # Word list
    book_pages.append({"page": page_num, "type": "wordlist", "text": "Words to Know"})
    page_num += 1

    # Story pages
    for i, p in enumerate(pages):
        book_pages.append({
            "page": page_num,
            "story_page": i + 1,
            "type": "story",
            "text": p.get("text", ""),
            "scene": p.get("scene", ""),
            "shot_type": p.get("shot_type", "medium")
        })
        page_num += 1

    # End page
    book_pages.append({
        "page": page_num,
        "type": "end",
        "text": "The End",
        "scene": f"Peaceful closing scene. {story_bible.visual_style}"
    })
    page_num += 1

    # Wordsearch
    book_pages.append({"page": page_num, "type": "wordsearch"})
    page_num += 1

    # Series info
    book_pages.append({"page": page_num, "type": "series_info"})
    page_num += 1

    # Back cover
    book_pages.append({
        "page": page_num,
        "type": "back_cover",
        "text": story_bible.premise
    })

    # Build complete book
    book = {
        "id": slug,
        "title": title,
        "slug": slug,
        "level": f"{band}1",
        "band": band,
        "age_range": spec["age_range"],
        "author": "FunBookies",
        "illustrator": "AI Generated",
        "summary": story_bible.premise,
        "story_bible": story_bible.to_dict(),
        "pages": book_pages,
        "wordsearch_words": story_bible.key_vocabulary[:8],
        "metadata": {
            "storyPages": len(pages),
            "generatedAt": "2026-01-11",
            "workflow": "story_bible_first"
        }
    }

    return book


def improve_existing_book(book_path: Path) -> dict:
    """Add story bible to an existing book by analyzing its content."""
    with open(book_path) as f:
        book = json.load(f)

    if book.get("story_bible"):
        print(f"Book already has story_bible")
        return book

    # Extract story content
    title = book.get("title", "Unknown")
    band = book.get("band", "B")
    pages = [p for p in book.get("pages", []) if p.get("type") == "story"]
    full_text = " ".join(p.get("text", "") for p in pages)

    # Generate prompt for creating story bible from existing content
    prompt = f"""Analyze this existing children's book and create a story bible that captures its narrative essence.

TITLE: {title}
READING LEVEL: Band {band}

STORY TEXT (simplified for level):
{full_text}

Based on this text, reverse-engineer the rich narrative that underlies it. Create a story bible with:

1. PREMISE: What is the full story concept? (beyond the simple text)
2. THEMES: What deeper themes are present?
3. CHARACTER ARCS: What journeys do characters take?
4. SETTING: Rich description of the world
5. PLOT SUMMARY: Full narrative (not level-constrained)
6. EMOTIONAL BEATS: Key emotional moments in the story
7. VISUAL STYLE: Based on existing scenes/descriptions
8. KEY VOCABULARY: Important story words

Output as JSON."""

    print(f"\nTo generate story bible for '{title}', use this prompt with an LLM:")
    print("-" * 60)
    print(prompt[:500] + "...")
    print("-" * 60)

    return book


def main():
    parser = argparse.ArgumentParser(description="Story Bible Workflow for book creation")
    parser.add_argument("--premise", type=str, help="Story premise to develop")
    parser.add_argument("--title", type=str, help="Book title")
    parser.add_argument("--band", type=str, choices=["A", "B", "C", "D"], default="B", help="Target reading band")
    parser.add_argument("--pages", type=int, help="Number of story pages")
    parser.add_argument("--from-bible", type=str, help="Path to existing story bible JSON")
    parser.add_argument("--improve", type=str, help="Path to existing book to add story bible")
    parser.add_argument("--output", type=str, help="Output path for book JSON")
    parser.add_argument("--show-prompts", action="store_true", help="Show LLM prompts for each step")

    args = parser.parse_args()

    # Set default page counts by band
    default_pages = {"A": 10, "B": 14, "C": 20, "D": 28}
    page_count = args.pages or default_pages.get(args.band, 14)

    if args.improve:
        # Improve existing book
        book_path = Path(args.improve)
        if not book_path.exists():
            print(f"Error: Book not found: {book_path}")
            return
        improve_existing_book(book_path)

    elif args.premise:
        # New book from premise
        if not args.title:
            print("Error: --title required when using --premise")
            return

        print(f"\n{'='*60}")
        print(f"STORY BIBLE WORKFLOW")
        print(f"{'='*60}")
        print(f"Title: {args.title}")
        print(f"Band: {args.band}")
        print(f"Pages: {page_count}")
        print(f"{'='*60}")

        # Step 1: Generate story bible prompt
        print("\n[STEP 1] Generate Story Bible")
        print("-" * 40)
        bible_prompt = generate_story_bible_prompt(args.premise, args.band)
        if args.show_prompts:
            print(bible_prompt)
        else:
            print(f"Prompt generated ({len(bible_prompt)} chars)")
            print("Use this prompt with an LLM to generate the story bible.")

        # Create placeholder story bible
        placeholder_bible = StoryBible(
            premise=args.premise,
            themes=["[Generate with LLM]"],
            character_arcs={"Main Character": "[Generate with LLM]"},
            setting="[Generate with LLM]",
            plot_summary="[Generate with LLM]",
            emotional_beats=[{"page": 1, "beat": "[Generate with LLM]"}],
            visual_style="Warm watercolor style, child-friendly",
            key_vocabulary=["[Generate with LLM]"]
        )

        # Step 2: Level adaptation prompt
        print(f"\n[STEP 2] Level Adaptation (Band {args.band})")
        print("-" * 40)
        adaptation_prompt = generate_level_adaptation_prompt(placeholder_bible, args.band, page_count)
        if args.show_prompts:
            print(adaptation_prompt)
        else:
            print(f"Prompt generated ({len(adaptation_prompt)} chars)")

        # Step 3: Scene generation prompt
        print(f"\n[STEP 3] Scene Descriptions")
        print("-" * 40)
        placeholder_pages = [{"story_page": i, "text": "[Adapted text]"} for i in range(1, page_count + 1)]
        scene_prompt = generate_scene_prompts(placeholder_bible, placeholder_pages)
        if args.show_prompts:
            print(scene_prompt)
        else:
            print(f"Prompt generated ({len(scene_prompt)} chars)")

        # Create placeholder book structure
        slug = args.title.lower().replace(" ", "-").replace("'", "")
        book = create_book_structure(
            title=args.title,
            slug=slug,
            band=args.band,
            story_bible=placeholder_bible,
            pages=placeholder_pages
        )

        # Output
        output_path = Path(args.output) if args.output else BOOKS_DIR / f"{slug}.json"
        print(f"\n[OUTPUT]")
        print("-" * 40)
        print(f"Would save to: {output_path}")
        print("\nTo complete this book:")
        print("1. Run each prompt through an LLM (Claude, GPT-4, etc.)")
        print("2. Replace placeholder content with LLM outputs")
        print("3. Generate reference image and page illustrations")

    elif args.from_bible:
        # Load existing story bible
        bible_path = Path(args.from_bible)
        if not bible_path.exists():
            print(f"Error: Story bible not found: {bible_path}")
            return

        with open(bible_path) as f:
            bible_data = json.load(f)

        story_bible = StoryBible.from_dict(bible_data)
        print(f"Loaded story bible: {story_bible.premise[:50]}...")

        # Generate adaptation prompts
        print(f"\n[STEP 2] Level Adaptation (Band {args.band})")
        print("-" * 40)
        adaptation_prompt = generate_level_adaptation_prompt(story_bible, args.band, page_count)
        print(adaptation_prompt if args.show_prompts else f"Prompt generated ({len(adaptation_prompt)} chars)")

    else:
        print("Usage:")
        print("  --premise 'story idea' --title 'Book Title' --band B")
        print("  --from-bible path/to/bible.json --band A")
        print("  --improve path/to/existing/book.json")
        print("  --show-prompts to display full LLM prompts")
        print("\nExamples:")
        print("  python story_bible_workflow.py --premise 'A shy octopus learns to make friends' --title 'Otto Makes Friends' --band B")
        print("  python story_bible_workflow.py --improve public/books/pig_mud.json")


if __name__ == "__main__":
    main()
