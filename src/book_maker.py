"""
Main Funbookies book generation workflow.
Creates complete minibooks from topic to print-ready EPUB/PDF.
"""

import os
import json
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv

from config import BOOK_SPECS, BRAND, IMAGE_DEFAULTS
from story_gen import StoryGenerator
from image_gen import ImageGenerator
from epub_generator import Book, Page, FixedLayoutEPUB
from word_banks import WordBanks

load_dotenv()

# Initialize word banks for phonics validation
WORD_BANKS = WordBanks()


@dataclass
class BookConfig:
    """Configuration for a new book."""
    topic: str
    age_range: str = "6-7"
    reading_level: str = "beginning reader"
    phonics_level: str = "orange"  # yellow, orange, red, purple
    include_word_list: bool = True
    character_names: list = None  # Character names for validation
    topic_vocabulary: list = None  # Topic words (lava, volcano, etc.)
    art_style: str = "children's book illustration, bright colors, friendly, engaging, educational"

    def __post_init__(self):
        if self.character_names is None:
            self.character_names = []
        if self.topic_vocabulary is None:
            self.topic_vocabulary = []


# Phonics level descriptions for prompts
PHONICS_LEVEL_PROMPTS = {
    "yellow": """
PHONICS LEVEL: Yellow (CVC Only - Easiest)
- Use ONLY simple CVC words: cat, run, hot, big, sun, mom, dad, pet, sit, etc.
- NO digraphs (no sh, ch, th words yet)
- NO blends (no st, cr, bl, etc.)
- Max 5 words per page
- Sight words: a, I, the, to, is, it, in, my, we, go, no, so
""",

    "orange": """
PHONICS LEVEL: Orange (CVC + Digraphs)
- CVC words: cat, run, hot, big, sun, pet, sit, got, top, etc.
- Digraphs OK: sh (ship, wish), ch (chat, much), th (that, with), ck (back, rock)
- NO blends yet (no st, cr, bl words)
- Max 7 words per page
- Sight words: a, I, the, to, is, it, in, my, we, go, no, so, said, was, he, she, they, see, look, for, you, all, are, do, have, here, there, this, that, what, with, and, but, not, can, did, get, got
""",

    "red": """
PHONICS LEVEL: Red (CVC + Digraphs + Blends)
- CVC words: cat, run, hot, big, etc.
- Digraphs OK: sh, ch, th, ck, wh
- Blends OK: st (stop), cr (crash), bl (blue), sp (spin), tr (trip), dr (drop), gr (grab), etc.
- NO magic e yet (no cake, bike, home, etc.)
- Max 8 words per page
- Includes all primer and first-grade sight words
""",

    "purple": """
PHONICS LEVEL: Purple (CVC + Digraphs + Blends + Magic E)
- All previous patterns plus magic e words: cake, bike, home, cute, made, etc.
- Max 10 words per page
- Full Dolch sight word list available
"""
}


class BookMaker:
    """End-to-end book generation pipeline."""

    def __init__(self, backend: str = "mulerouter"):
        self.backend = backend
        self.story_gen = StoryGenerator(backend=backend)
        self.image_gen = ImageGenerator(backend=backend)
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)

    def create_book(self, config: BookConfig) -> str:
        """
        Create a complete book from config.

        Returns path to generated EPUB.
        """
        print(f"Creating book about: {config.topic}")

        # 1. Generate story with word list
        print("Generating story...")
        story = self._generate_story_with_wordlist(config)

        # Save story JSON for reference
        story_path = self.output_dir / f"{self._safe_name(story['title'])}_story.json"
        with open(story_path, "w") as f:
            json.dump(story, f, indent=2)
        print(f"Story saved: {story_path}")

        # 2. Generate images for each page
        print("Generating images...")
        image_paths = self._generate_images(story)

        # 3. Assemble into EPUB
        print("Creating EPUB...")
        epub_path = self._create_epub(story, image_paths)

        print(f"Book complete: {epub_path}")
        return epub_path

    def _generate_story_with_wordlist(self, config: BookConfig) -> dict:
        """Generate story with vocabulary word list for beginning readers."""
        import httpx

        cfg = self.story_gen.configs[self.backend]

        # Get phonics level constraints
        phonics_constraints = PHONICS_LEVEL_PROMPTS.get(config.phonics_level, PHONICS_LEVEL_PROMPTS["orange"])

        # Get sample words for this level
        sample_words = WORD_BANKS.get_words_for_story(config.phonics_level, count=15)
        decodable_examples = ", ".join(sample_words["decodable"][:12])
        sight_examples = ", ".join(sample_words["sight"][:10])
        sound_effects = ", ".join(sample_words["sound_effects"][:5])

        system_prompt = f"""You are an expert children's book author writing for beginning readers ages {config.age_range}.

{phonics_constraints}

APPROVED WORD EXAMPLES FOR THIS LEVEL:
- Decodable: {decodable_examples}
- Sight words: {sight_examples}
- Sound effects: {sound_effects}

RESEARCH-BASED APPROACH (Science of Reading + Mo Willems + Pete the Cat):

1. DECODABLE TEXT PRINCIPLES:
   - 70%+ words should be decodable CVC or simple blends
   - Limit sight words to essentials: the, is, a, to, I, said, you, was
   - For 6-7 year olds: they know short vowels, digraphs (sh, ch, th), blends (cr, st, bl)

2. SENTENCE PATTERNS THAT WORK:
   Simple declarative: "Gus ran up the hill."
   Dialogue with said: "Look!" said Gus.
   Sound words standalone: "CRACK! POP! BOOM!"
   Repetition with variation: "Run, Gus, run! Run, run, run!"
   Question + answer: "What is that? It is hot lava!"

3. MO WILLEMS STYLE (Elephant & Piggie):
   - Short punchy sentences (3-7 words ideal)
   - Expressive punctuation: ! ! ! and ?
   - Genuine emotion through simple words: Gus gasps. Gus grins.
   - Dialogue carries the story

4. PETE THE CAT STYLE:
   - Rhythmic, almost song-like repetition
   - "Did Gus fret? Goodness, no!"
   - Pattern: situation → character's cool reaction

5. WHAT TO AVOID:
   BAD: "The magma is very hot and red." (boring, too many adjectives)
   BAD: "They see it drip." (passive, vague "they")
   BAD: Complex sentences with multiple clauses

   GOOD: "Hot! Hot! Hot!" Gus hops back.
   GOOD: The lava drips. Drip, drip, drip.
   GOOD: "Run!" said Gus. And Gus ran fast.

6. STORY ARC (simple but complete):
   - Character wants to explore/discover something
   - They find it! Wow!
   - Something exciting/scary happens
   - Character responds with courage/cleverness
   - Safe and happy ending with lesson learned

WORD LIST STRUCTURE (must be COMPREHENSIVE - include ALL words used in story):
- Sound-out words: ALL decodable CVC words from the story: hot, red, run, big, drip, pop, get, hiss, etc.
- Sight words: ALL high-frequency words used: the, said, was, to, I, a, is, it, up, etc.
- New words: Topic vocabulary and character names: lava, magma, crater, Gus, etc.

FORMAT: 24 pages, 10x10cm square
- Page 1: Cover
- Page 2: Words to Know (single page with ALL three word categories)
- Pages 3-23: Story (21 pages)
- Page 24: Copyright/credits page"""

        user_prompt = f"""Write a beginning reader book: {config.topic}

TITLE MUST BE: Use the exact title style given in the topic.

Return JSON:
{{
  "title": "Exact title from topic",
  "character": "Character name and description",
  "word_list": {{
    "sound_out": ["hot", "run", "big", "drip", "pop", "hiss", "red", "get", "ran", "top", "got"],
    "sight": ["the", "said", "to", "I", "was", "a", "is", "it", "up", "look", "what"],
    "new": ["lava", "magma", "crater", "Gus"]
  }},
  "pages": [
    {{"page": 1, "type": "cover", "text": "Title", "image_prompt": "character in exciting scene"}},
    {{"page": 2, "type": "wordlist", "text": "Words to Know", "image_prompt": "decorative border with small character"}},
    {{"page": 3, "type": "story", "text": "First story sentence.", "image_prompt": "scene description"}},
    ... pages 4-23: story continues ...
    {{"page": 24, "type": "copyright", "text": "© 2024 Funbookies\\nfunbookies.com\\nAll rights reserved.", "image_prompt": "small character waving goodbye, simple background"}}
  ]
}}

WORD LIST REQUIREMENTS:
- sound_out: Include EVERY decodable word from your story (CVC, blends, digraphs)
- sight: Include EVERY high-frequency word from your story
- new: Include topic words AND character name(s)
- Be COMPREHENSIVE - a parent should be able to practice ALL story words beforehand

CRITICAL RULES:
1. Max 8 words per page (aim for 5-6)
2. Use character name, not "they" or "it"
3. Every page: action verb OR dialogue OR sound word
4. Repetition is GOOD: "Run, Gus! Run, run, run!"
5. Pattern for danger: Sound word → "said [name]" → action
   Example: "CRACK!" / "Run!" said Gus. / Gus ran fast.
6. End with character safe, happy, and proud
7. Page 24 MUST be copyright page"""

        headers = {
            "Authorization": f"Bearer {cfg['api_key']}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://funbookies.com",
            "X-Title": "Funbookies",
        }

        payload = {
            "model": cfg.get("model", "qwen-plus"),
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.7,
            "max_tokens": 5000,
        }

        with httpx.Client(timeout=90.0) as client:
            response = client.post(
                f"{cfg['base_url']}/vendors/openai/v1/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

        content = data["choices"][0]["message"]["content"]

        # Parse JSON
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]

        story = json.loads(content.strip())

        # Add phonics level and config metadata
        story["phonics_level"] = config.phonics_level
        story["age_range"] = config.age_range

        # Enhance image prompts with consistent style
        for page in story["pages"]:
            if "image_prompt" in page:
                page["image_prompt"] = f"{page['image_prompt']}, {config.art_style}, no text in image"

        # Validate phonics level compliance
        validation = WORD_BANKS.validate_story_words(
            story,
            level=config.phonics_level,
            character_names=config.character_names if config.character_names else None,
            topic_words=config.topic_vocabulary if config.topic_vocabulary else None
        )

        story["validation"] = {
            "phonics_level": config.phonics_level,
            "accessible_percent": validation["accessible_percent"],
            "strict_decodable_percent": validation["strict_decodable_percent"],
            "valid": validation["valid"],
            "word_counts": {
                "total": validation["total_words"],
                "decodable": validation["decodable_count"],
                "sight_words": validation["sight_word_count"],
                "heart_words": validation["heart_word_count"],
                "exclamations": validation["exclamation_count"],
                "characters": validation["character_count"],
                "vocabulary": validation["vocabulary_count"],
                "unknown": validation["unknown_count"]
            },
            "issues": validation["issues"]
        }

        # Print validation summary
        print(f"\n  Phonics Validation ({config.phonics_level} level):")
        print(f"    Accessible: {validation['accessible_percent']:.1f}%")
        print(f"    Valid: {validation['valid']}")
        if validation["issues"]:
            print(f"    Issues: {len(validation['issues'])}")
            for issue in validation["issues"][:5]:  # Show first 5
                if issue["word"]:
                    print(f"      - '{issue['word']}': {issue['issue']}")

        return story

    def _generate_images(self, story: dict) -> dict:
        """Generate images for all pages."""
        image_paths = {}
        book_name = self._safe_name(story["title"])

        for page in story["pages"]:
            page_num = page["page"]
            filename = f"{book_name}_page{page_num:02d}"

            if page.get("image_prompt"):
                try:
                    path = self.image_gen.generate(
                        prompt=page["image_prompt"],
                        filename=filename,
                    )
                    image_paths[page_num] = path
                    print(f"  Page {page_num}: {path}")
                except Exception as e:
                    print(f"  Page {page_num}: FAILED - {e}")
                    image_paths[page_num] = None

        return image_paths

    def _create_epub(self, story: dict, image_paths: dict) -> str:
        """Assemble story and images into EPUB."""
        pages = []

        for page_data in story["pages"]:
            page_num = page_data["page"]
            pages.append(Page(
                number=page_num,
                image_path=image_paths.get(page_num, ""),
                text=page_data.get("text", ""),
                text_position="bottom" if page_data.get("type") == "story" else "center",
            ))

        book = Book(
            title=story["title"],
            author=BRAND["name"],
            pages=pages,
        )

        generator = FixedLayoutEPUB(book, output_dir=str(self.output_dir))
        return generator.generate()

    def _safe_name(self, name: str) -> str:
        return "".join(c for c in name if c.isalnum() or c in " -_").strip().replace(" ", "_").lower()


def create_funbookies_series():
    """Create the three requested books."""
    maker = BookMaker(backend="mulerouter")

    topics = [
        BookConfig(
            topic="'Gus and the Volcano' - Gus is a small lime-green gecko who lives near a volcano. Story about Gus exploring the volcano, seeing lava, and staying safe. Gus says 'Wow! Wow! Wow!' when amazed.",
            age_range="6-7",
            reading_level="beginning reader",
            phonics_level="orange",  # CVC + digraphs
            character_names=["Gus"],
            topic_vocabulary=["lava", "magma", "volcano"],
            include_word_list=True,
        ),
        BookConfig(
            topic="'Rats in the Castle' - Rita and Rico are two little rats exploring a castle. Rita is bold and says 'Let's go!' Rico is careful and says 'Are you sure?' They find jam but must escape a cat.",
            age_range="6-7",
            reading_level="beginning reader",
            phonics_level="orange",  # CVC + digraphs
            character_names=["Rita", "Rico"],
            topic_vocabulary=["castle", "jam", "king", "queen"],
            include_word_list=True,
        ),
        BookConfig(
            topic="'Zee and the Jungle' - Zee is a slow, happy sloth who hangs in the jungle. Zee makes a friend and learns that slow is OK. Zee's catchphrase is 'Hang on!'",
            age_range="6-7",
            reading_level="beginning reader",
            phonics_level="orange",  # CVC + digraphs
            character_names=["Zee"],
            topic_vocabulary=["jungle", "sloth", "vine", "bird"],
            include_word_list=True,
        ),
    ]

    books = []
    for config in topics:
        try:
            path = maker.create_book(config)
            books.append(path)
        except Exception as e:
            print(f"Failed to create book about {config.topic}: {e}")

    return books


if __name__ == "__main__":
    books = create_funbookies_series()
    print("\nCreated books:")
    for book in books:
        print(f"  - {book}")
