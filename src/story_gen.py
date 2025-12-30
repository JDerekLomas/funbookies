"""
Story generation using LLM for Funbookies minibooks.
"""

import os
import json
import httpx
from typing import Optional
from dotenv import load_dotenv
from config import BOOK_SPECS, BRAND

load_dotenv()


class StoryGenerator:
    """Generate children's stories with page breakdowns."""

    def __init__(self, backend: str = "mulerouter"):
        self.backend = backend

        self.configs = {
            "mulerouter": {
                "api_key": os.getenv("MULEROUTER_API_KEY"),
                "base_url": os.getenv("MULEROUTER_BASE_URL", "https://api.mulerouter.ai"),
                "model": "qwen-plus",
                "endpoint": "/vendors/openai/v1/chat/completions",
            },
            "openrouter": {
                "api_key": os.getenv("OPENROUTER_API_KEY"),
                "base_url": "https://openrouter.ai/api/v1",
                "model": "anthropic/claude-3.5-sonnet",
                "endpoint": "/chat/completions",
            },
        }

    def generate_story(
        self,
        topic: str,
        age_range: str = "3-6",
        style: str = "playful and gentle",
        model: Optional[str] = None,
    ) -> dict:
        """
        Generate a complete story with page-by-page breakdown.

        Args:
            topic: What the story is about
            age_range: Target age range
            style: Writing style
            model: Override default model

        Returns:
            Dict with title, pages (text + image_prompt for each)
        """
        config = self.configs[self.backend]
        model = model or config["model"]

        story_pages = BOOK_SPECS["story_pages"]

        system_prompt = f"""You are a children's book author for {BRAND["name"]}.
You write short, engaging stories for children aged {age_range}.
Style: {style}

Your stories follow the Pixi book format:
- 24 total pages
- Page 1: Front cover (title + main character visual)
- Page 2: Title page with credits
- Pages 3-22: Story ({story_pages} pages, about 1-2 sentences each)
- Page 23: Story conclusion or simple activity
- Page 24: Back cover with {BRAND["name"]} branding

Keep text SHORT - these are tiny books! Max 15-20 words per page.
Each page needs a clear, describable scene for illustration."""

        user_prompt = f"""Create a children's story about: {topic}

Return a JSON object with this structure:
{{
  "title": "Story Title",
  "pages": [
    {{
      "page": 1,
      "type": "cover",
      "text": "The title text",
      "image_prompt": "Detailed description for AI image generation"
    }},
    ...for all 24 pages
  ]
}}

Make image_prompt descriptions detailed and specific for AI image generation.
Include: main subject, setting, colors, mood, style (children's book illustration).
"""

        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://funbookies.com",
            "X-Title": "Funbookies",
        }

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.8,
            "max_tokens": 4000,
        }

        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                f"{config['base_url']}/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

        # Extract the story from response
        content = data["choices"][0]["message"]["content"]

        # Parse JSON from response (handle markdown code blocks)
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]

        story = json.loads(content.strip())
        return story

    def enhance_image_prompts(self, story: dict, art_style: str = None) -> dict:
        """Add consistent art style to all image prompts."""
        art_style = art_style or "children's book illustration, soft watercolor, warm colors, friendly characters, gentle lighting"

        for page in story["pages"]:
            if "image_prompt" in page:
                page["image_prompt"] = f"{page['image_prompt']}, {art_style}"

        return story


if __name__ == "__main__":
    gen = StoryGenerator(backend="mulerouter")

    story = gen.generate_story(
        topic="a tiny snail who wants to see the world",
        age_range="3-5",
    )

    print(json.dumps(story, indent=2))
