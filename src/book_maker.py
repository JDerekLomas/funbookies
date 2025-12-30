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

load_dotenv()


@dataclass
class BookConfig:
    """Configuration for a new book."""
    topic: str
    age_range: str = "6-7"
    reading_level: str = "beginning reader"
    include_word_list: bool = True
    art_style: str = "children's book illustration, bright colors, friendly, engaging, educational"


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

        system_prompt = f"""You are a children's book author for {BRAND["name"]}, creating books for beginning readers.

Target: {config.age_range} year olds, {config.reading_level}
Format: 24-page Pixi-style minibook (10x10cm)

IMPORTANT FOR BEGINNING READERS:
- Use simple, decodable words when possible
- Short sentences (5-10 words max per page)
- Repetitive patterns help learning
- High-frequency sight words are good
- Pages 2-3 should be a WORD LIST for practice

Page structure:
- Page 1: Cover (title + eye-catching image)
- Page 2: Word List title "Words to Know"
- Page 3: The actual word list (8-12 key words from the story)
- Pages 4-22: Story (19 pages, 1-2 short sentences each)
- Page 23: Fun fact or simple question about the topic
- Page 24: Back cover with {BRAND["name"]} logo

Style: {config.art_style}"""

        user_prompt = f"""Create a beginning reader book about: {config.topic}

Return JSON:
{{
  "title": "Simple Title",
  "word_list": ["word1", "word2", ...],  // 8-12 key vocabulary words
  "pages": [
    {{"page": 1, "type": "cover", "text": "Title", "image_prompt": "detailed scene description"}},
    {{"page": 2, "type": "wordlist_title", "text": "Words to Know", "image_prompt": "decorative border with topic elements"}},
    {{"page": 3, "type": "wordlist", "text": "word1 - word2 - word3...", "image_prompt": "small icons for each word"}},
    {{"page": 4, "type": "story", "text": "Story begins...", "image_prompt": "scene description"}},
    ... // continue to page 24
  ]
}}

Make image prompts detailed: subject, action, setting, colors, mood.
Keep text VERY simple for beginning readers!"""

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

        # Enhance image prompts with consistent style
        for page in story["pages"]:
            if "image_prompt" in page:
                page["image_prompt"] = f"{page['image_prompt']}, {config.art_style}, no text in image"

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
            topic="volcanoes - how they work, famous volcanoes, lava and eruptions",
            age_range="6-7",
            reading_level="beginning reader",
            include_word_list=True,
        ),
        BookConfig(
            topic="castles - who lived there, parts of a castle, knights and princesses",
            age_range="6-7",
            reading_level="beginning reader",
            include_word_list=True,
        ),
        BookConfig(
            topic="jungles - rainforest animals, layers of the jungle, amazing plants",
            age_range="6-7",
            reading_level="beginning reader",
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
