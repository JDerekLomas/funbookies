#!/usr/bin/env python3
"""
FunBookies Book Generator

Creates complete leveled reader books with:
- Hero's Journey story structure
- Controlled vocabulary by reading level
- Image prompts for NanoBanana generation
- Full book JSON output
"""

import json
import os
from pathlib import Path
from dataclasses import dataclass, field
from datetime import date
from typing import Optional
import anthropic

# Reading level definitions
LEVELS = {
    0: {
        "name": "Pink",
        "skill": "Pre-reader",
        "skill_description": "Picture reading with simple labels",
        "words_per_sentence": 2,
        "sentences_per_page": 1,
        "story_pages": 8,
        "rules": "Only use 1-2 word phrases. Focus on naming objects and actions."
    },
    1: {
        "name": "Yellow",
        "skill": "Simple CVC",
        "skill_description": "Basic consonant-vowel-consonant words like cat, dog, sun",
        "words_per_sentence": 3,
        "sentences_per_page": 1,
        "story_pages": 10,
        "rules": "Use only simple CVC words (cat, dog, sun, hat, pig, run). No blends, no digraphs."
    },
    2: {
        "name": "Orange",
        "skill": "CVC with short u",
        "skill_description": "CVC words including short u sounds like bug, cup, mud",
        "words_per_sentence": 4,
        "sentences_per_page": 1,
        "story_pages": 12,
        "rules": "CVC words including short u (bug, cup, mud, fun, hug). No blends."
    },
    3: {
        "name": "Orange",
        "skill": "CVC + Digraphs",
        "skill_description": "CVC words combined with digraphs like sh, ch, th",
        "words_per_sentence": 5,
        "sentences_per_page": 1,
        "story_pages": 16,
        "rules": "CVC words plus digraphs (ship, chat, that, fish, much, with). Short sentences."
    },
    4: {
        "name": "Red",
        "skill": "Beginning blends",
        "skill_description": "Words with beginning consonant blends like stop, flag, crab",
        "words_per_sentence": 6,
        "sentences_per_page": 1,
        "story_pages": 18,
        "rules": "Beginning blends allowed (stop, flag, crab, drum, frog, trip). Keep sentences clear."
    },
    5: {
        "name": "Purple",
        "skill": "Ending blends",
        "skill_description": "Words with ending consonant blends like jump, help, fast",
        "words_per_sentence": 7,
        "sentences_per_page": 2,
        "story_pages": 18,
        "rules": "Beginning and ending blends (jump, help, fast, crisp, stamp). More complex actions."
    },
    6: {
        "name": "Blue",
        "skill": "Silent e",
        "skill_description": "Magic e words where silent e changes vowel sound like cake, bike",
        "words_per_sentence": 8,
        "sentences_per_page": 2,
        "story_pages": 20,
        "rules": "Silent e words (cake, bike, home, tube, make, huge). Can express more emotions."
    },
    7: {
        "name": "Green",
        "skill": "Vowel teams",
        "skill_description": "Words with vowel teams like rain, boat, see, coat",
        "words_per_sentence": 10,
        "sentences_per_page": 2,
        "story_pages": 22,
        "rules": "Vowel teams (rain, boat, see, coat, team, play). Richer vocabulary."
    },
    8: {
        "name": "Gold",
        "skill": "R-controlled vowels",
        "skill_description": "Words with r-controlled vowels like car, bird, corn",
        "words_per_sentence": 12,
        "sentences_per_page": 3,
        "story_pages": 24,
        "rules": "R-controlled vowels (car, bird, corn, turn, hurt). More descriptive language."
    }
}

# Hero's Journey beat templates by level
HERO_JOURNEY_BEATS = {
    "low": [  # Levels 0-3
        ("ordinary_world", "Character in everyday setting"),
        ("call", "Sees or finds something interesting"),
        ("threshold", "Decides to investigate/approach"),
        ("ordeal", "Faces a challenge or obstacle"),
        ("reward", "Overcomes or succeeds"),
        ("return", "Returns happy/satisfied")
    ],
    "mid": [  # Levels 4-6
        ("ordinary_world", "Character introduced in their world"),
        ("call", "Discovery that disrupts routine"),
        ("refusal", "Hesitation or doubt"),
        ("threshold", "Commits to the adventure"),
        ("tests", "Faces challenges, may need help"),
        ("ordeal", "Biggest challenge of the story"),
        ("reward", "Success or prize earned"),
        ("return", "Returns transformed/wiser")
    ],
    "high": [  # Levels 7+
        ("ordinary_world", "Establish character and their world"),
        ("call", "Inciting incident"),
        ("refusal", "Initial resistance or fear"),
        ("mentor", "Gets help or encouragement"),
        ("threshold", "Crosses into adventure"),
        ("tests", "Series of challenges"),
        ("allies", "Makes friends or finds help"),
        ("ordeal", "Faces greatest fear"),
        ("reward", "Achieves goal"),
        ("road_back", "Journey home begins"),
        ("resurrection", "Final test"),
        ("return", "Returns changed, shares wisdom")
    ]
}

# Character templates
CHARACTERS = {
    "rat": {
        "names": ["Rita", "Rico", "Remy", "Rose"],
        "description": "cute cartoon rat with bright eyes",
        "traits": ["curious", "clever", "brave"],
        "settings": ["castle", "kitchen", "garden", "bakery"]
    },
    "dog": {
        "names": ["Duke", "Daisy", "Doug", "Dot"],
        "description": "friendly cartoon dog with floppy ears",
        "traits": ["loyal", "playful", "determined"],
        "settings": ["park", "home", "beach", "forest"]
    },
    "pig": {
        "names": ["Pip", "Penny", "Pete", "Polly"],
        "description": "round pink cartoon pig",
        "traits": ["cheerful", "messy", "kind"],
        "settings": ["farm", "mud puddle", "fair", "garden"]
    },
    "salamander": {
        "names": ["Gus", "Sally", "Sam", "Sage"],
        "description": "bright orange cartoon salamander with spots",
        "traits": ["adventurous", "curious", "quick"],
        "settings": ["volcano", "pond", "forest", "cave"]
    },
    "fox": {
        "names": ["Felix", "Fern", "Finn", "Flora"],
        "description": "clever red cartoon fox with a fluffy tail",
        "traits": ["smart", "crafty", "helpful"],
        "settings": ["forest", "meadow", "den", "village"]
    },
    "owl": {
        "names": ["Oliver", "Olive", "Oscar", "Opal"],
        "description": "wise cartoon owl with big round eyes",
        "traits": ["thoughtful", "patient", "wise"],
        "settings": ["tree", "library", "night sky", "barn"]
    }
}

# Common sight words by level
SIGHT_WORDS = {
    0: ["I", "a", "the"],
    1: ["is", "in", "it", "on", "to"],
    2: ["and", "he", "she", "we", "go", "no", "so"],
    3: ["said", "was", "for", "are", "you", "they", "have"],
    4: ["with", "what", "this", "from", "that", "there", "were"],
    5: ["could", "would", "should", "their", "been", "more", "some"],
    6: ["when", "your", "which", "about", "many", "then", "into"],
    7: ["because", "through", "before", "after", "again", "always"],
    8: ["thought", "together", "different", "important", "sometimes"]
}


@dataclass
class BookSpec:
    """Specification for a new book"""
    level: int
    character_type: str
    theme: str
    title: Optional[str] = None
    custom_words: list = field(default_factory=list)
    style_preset: str = "classic"


@dataclass
class GeneratedBook:
    """Complete generated book data"""
    title: str
    slug: str
    level: int
    color: str
    skill: str
    skill_description: str
    age_range: str
    summary: str
    word_list: dict
    pages: list
    wordsearch_words: list
    character_description: str
    style_preset: str
    created: str = field(default_factory=lambda: date.today().isoformat())
    model: str = "wan2.6-t2i"
    author: str = "FunBookies"
    illustrator: str = "AI Generated"


class BookGenerator:
    """Generate complete leveled reader books"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.books_dir = self.project_root / "public" / "books"
        self.client = anthropic.Anthropic()

    def _get_journey_beats(self, level: int) -> list:
        """Get appropriate Hero's Journey beats for level"""
        if level <= 3:
            return HERO_JOURNEY_BEATS["low"]
        elif level <= 6:
            return HERO_JOURNEY_BEATS["mid"]
        else:
            return HERO_JOURNEY_BEATS["high"]

    def _get_sight_words(self, level: int) -> list:
        """Get cumulative sight words up to this level"""
        words = []
        for lvl in range(level + 1):
            words.extend(SIGHT_WORDS.get(lvl, []))
        return list(set(words))

    def _build_story_prompt(self, spec: BookSpec) -> str:
        """Build the Claude prompt for story generation"""
        level_info = LEVELS[spec.level]
        char_info = CHARACTERS[spec.character_type]
        journey_beats = self._get_journey_beats(spec.level)
        sight_words = self._get_sight_words(spec.level)

        # Select character name
        char_name = char_info["names"][0]

        beats_text = "\n".join([f"- {beat[0].upper()}: {beat[1]}" for beat in journey_beats])

        prompt = f"""You are creating a decodable leveled reader for beginning readers. Generate a complete story following these STRICT constraints:

## READING LEVEL: {spec.level} ({level_info['name']})
- Skill focus: {level_info['skill']}
- Maximum words per sentence: {level_info['words_per_sentence']}
- Sentences per page: {level_info['sentences_per_page']}
- Total story pages: {level_info['story_pages']}
- Rules: {level_info['rules']}

## CHARACTER
- Name: {char_name}
- Type: {char_info['description']}
- Traits: {', '.join(char_info['traits'])}
- Suggested settings: {', '.join(char_info['settings'])}

## THEME
{spec.theme}

## HERO'S JOURNEY STRUCTURE
Follow these beats across your {level_info['story_pages']} story pages:
{beats_text}

## ALLOWED SIGHT WORDS
{', '.join(sight_words)}

## CUSTOM WORDS TO INCLUDE (if any)
{', '.join(spec.custom_words) if spec.custom_words else 'None specified'}

## CRITICAL RULES
1. ONLY use words a child at level {spec.level} can decode
2. Every word must be either:
   - A decodable word matching the level's phonics patterns
   - An allowed sight word from the list above
3. Keep sentences SHORT - max {level_info['words_per_sentence']} words
4. One clear idea per sentence
5. Use repetition - repeat key words naturally
6. Make it emotionally engaging despite simple vocabulary
7. The images will carry narrative weight - text is skeletal

## OUTPUT FORMAT
Return a JSON object with this exact structure:
{{
  "title": "Story Title",
  "summary": "One sentence summary for back cover",
  "word_list": {{
    "sound_out": ["list", "of", "decodable", "words"],
    "sight": ["list", "of", "sight", "words", "used"],
    "new": ["any", "character", "names", "or", "setting", "words"]
  }},
  "wordsearch_words": ["6-8", "key", "words", "for", "puzzle"],
  "pages": [
    {{
      "story_page": 1,
      "text": "The story text for this page.",
      "image_prompt": "Detailed illustration description for AI image generation. Include character ({char_name}, {char_info['description']}), action, setting, emotion. End with 'Warm soft watercolor style.'"
    }}
  ]
}}

Generate exactly {level_info['story_pages']} story pages. Return ONLY the JSON, no other text."""

        return prompt

    def generate_story(self, spec: BookSpec) -> dict:
        """Generate story content using Claude"""
        prompt = self._build_story_prompt(spec)

        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=8192,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # Extract JSON from response
        content = message.content[0].text
        try:
            # Handle potential markdown code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            return json.loads(content)
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {e}")
            print(f"Raw content: {content[:500]}...")
            raise

    def create_full_book(self, spec: BookSpec) -> GeneratedBook:
        """Create a complete book with all metadata and pages"""
        level_info = LEVELS[spec.level]
        char_info = CHARACTERS[spec.character_type]

        # Generate the story
        story_data = self.generate_story(spec)

        # Create slug from title
        title = spec.title or story_data["title"]
        slug = title.lower().replace(" ", "_").replace("!", "").replace("'", "")
        slug = "".join(c for c in slug if c.isalnum() or c == "_")

        # Build full page list with front/back matter
        pages = []
        page_num = 1

        # Front matter
        pages.append({
            "page": page_num,
            "type": "cover",
            "image": f"{slug}_images/page_{page_num:02d}_cover.png",
            "text": title,
            "image_prompt": f"Children's book cover: {char_info['description']} in an exciting scene. Title '{title}'. Warm soft watercolor style."
        })
        page_num += 1

        pages.append({"page": page_num, "type": "copyright"})
        page_num += 1

        pages.append({"page": page_num, "type": "parent_guide"})
        page_num += 1

        pages.append({"page": page_num, "type": "level_info"})
        page_num += 1

        pages.append({"page": page_num, "type": "wordlist", "text": "Words to Know"})
        page_num += 1

        # Story pages
        for story_page in story_data["pages"]:
            pages.append({
                "page": page_num,
                "story_page": story_page["story_page"],
                "type": "story",
                "image": f"{slug}_images/page_{page_num:02d}.png",
                "text": story_page["text"],
                "image_prompt": story_page["image_prompt"]
            })
            page_num += 1

        # Back matter
        pages.append({
            "page": page_num,
            "type": "end",
            "image": f"{slug}_images/page_{page_num:02d}_end.png",
            "text": "The End",
            "image_prompt": f"{char_info['description']} looking happy and content. 'The End' moment. Warm soft watercolor style."
        })
        page_num += 1

        pages.append({"page": page_num, "type": "wordsearch"})
        page_num += 1

        pages.append({"page": page_num, "type": "series_info"})
        page_num += 1

        pages.append({
            "page": page_num,
            "type": "back_cover",
            "image": f"{slug}_images/page_{page_num:02d}_back.png",
            "text": story_data["summary"],
            "image_prompt": f"{char_info['description']} waving goodbye, friendly pose. Warm soft watercolor style."
        })

        # Determine age range
        age_ranges = {
            0: "3-5", 1: "4-5", 2: "4-6", 3: "4-6",
            4: "5-7", 5: "5-7", 6: "5-8", 7: "6-8", 8: "6-9"
        }

        return GeneratedBook(
            title=title,
            slug=slug,
            level=spec.level,
            color=level_info["name"],
            skill=level_info["skill"],
            skill_description=level_info["skill_description"],
            age_range=age_ranges.get(spec.level, "4-7"),
            summary=story_data["summary"],
            word_list=story_data["word_list"],
            pages=pages,
            wordsearch_words=story_data["wordsearch_words"],
            character_description=f"{char_info['names'][0]}, {char_info['description']}",
            style_preset=spec.style_preset
        )

    def save_book(self, book: GeneratedBook) -> Path:
        """Save book to JSON file"""
        output_path = self.books_dir / f"{book.slug}.json"

        book_dict = {
            "title": book.title,
            "slug": book.slug,
            "level": book.level,
            "color": book.color,
            "skill": book.skill,
            "skill_description": book.skill_description,
            "age_range": book.age_range,
            "created": book.created,
            "model": book.model,
            "author": book.author,
            "illustrator": book.illustrator,
            "summary": book.summary,
            "word_list": book.word_list,
            "wordsearch_words": book.wordsearch_words,
            "character_description": book.character_description,
            "style_preset": book.style_preset,
            "pages": book.pages
        }

        with open(output_path, "w") as f:
            json.dump(book_dict, f, indent=2)

        # Create images directory
        images_dir = self.books_dir / f"{book.slug}_images"
        images_dir.mkdir(exist_ok=True)

        print(f"Book saved to: {output_path}")
        print(f"Images directory created: {images_dir}")

        return output_path


# CLI interface
def main():
    import argparse

    parser = argparse.ArgumentParser(description="Generate a FunBookies leveled reader")
    parser.add_argument("--level", type=int, required=True, help="Reading level (0-8)")
    parser.add_argument("--character", required=True, choices=list(CHARACTERS.keys()))
    parser.add_argument("--theme", required=True, help="Story theme/premise")
    parser.add_argument("--title", help="Optional title (will be generated if not provided)")
    parser.add_argument("--words", help="Comma-separated custom words to include")
    parser.add_argument("--style", default="classic", help="Art style preset")
    parser.add_argument("--project-root", default=".", help="Project root directory")

    args = parser.parse_args()

    custom_words = []
    if args.words:
        custom_words = [w.strip() for w in args.words.split(",")]

    spec = BookSpec(
        level=args.level,
        character_type=args.character,
        theme=args.theme,
        title=args.title,
        custom_words=custom_words,
        style_preset=args.style
    )

    generator = BookGenerator(args.project_root)
    book = generator.create_full_book(spec)
    generator.save_book(book)

    print(f"\nGenerated: {book.title}")
    print(f"Level: {book.level} ({book.color})")
    print(f"Pages: {len(book.pages)}")
    print(f"Slug: {book.slug}")


if __name__ == "__main__":
    main()
