#!/usr/bin/env python3
"""
Story Generator - Single-Pass Story + Scene Generation

Creates a complete book with story text AND scene descriptions in one LLM call,
treating the phonics wordlist as creative inspiration rather than strict constraint.

Generates an HTML review page for human approval before any image generation.

Usage:
    python generate_story.py --level B1 --concept "A pig who loves mud" --setting "farm"
"""

import json
import sys
import os
import re
import webbrowser
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / ".env")
load_dotenv(PROJECT_ROOT / ".env.local")

BOOKS_DIR = PROJECT_ROOT / "public" / "books"
REVIEW_DIR = PROJECT_ROOT / "public" / "review"

with open(PROJECT_ROOT / "public/data/level-specs.json") as f:
    LEVEL_SPECS = json.load(f)

ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_KEY:
    print("Error: ANTHROPIC_API_KEY not found in environment")
    sys.exit(1)

import anthropic
client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)


def call_llm(prompt: str, max_tokens: int = 8000) -> str:
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text.strip()


def get_level_spec(level: str) -> dict:
    return LEVEL_SPECS["levels"].get(level, {})


def get_band_info(band: str) -> dict:
    return LEVEL_SPECS["bands"].get(band, {})


def slugify(title: str) -> str:
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    return slug.strip('-')


def build_story_prompt(level: str, concept: str, setting: str, title: str = None) -> str:
    spec = get_level_spec(level)
    if not spec:
        raise ValueError(f"Unknown level: {level}")

    band = spec.get("band", "B")

    # Band-specific visual style guidance
    band_styles = {
        "A": "Simple bold shapes, soft watercolor, very minimal detail, warm pastel colors. Gentle, comforting, bright mood.",
        "B": "Playful watercolor illustration, expressive characters, vibrant colors. Energetic, fun, adventurous mood.",
        "C": "Rich watercolor, more detailed characters and settings, dynamic compositions. Exciting, imaginative mood.",
        "D": "Sophisticated watercolor style, detailed environments, nuanced lighting. Atmospheric, immersive mood."
    }
    band_style = band_styles.get(band, band_styles["B"])

    constraints = spec.get("constraints", {})
    phonics_patterns = constraints.get("phonicsPatterns", [])
    word_families = constraints.get("wordFamilies", [])
    sight_words = constraints.get("sightWords", [])
    max_words = constraints.get("maxWordsPerSentence", 6)
    pages = constraints.get("pages", "12")
    decodability = constraints.get("decodability", "90%+")
    story_guidance = spec.get("storyGuidance", "")

    word_palette = []
    if phonics_patterns:
        word_palette.append("PHONICS PATTERNS:")
        for p in phonics_patterns:
            word_palette.append(f"  {p}")
    if word_families:
        word_palette.append(f"WORD FAMILIES: {', '.join(word_families)}")
    if sight_words:
        word_palette.append(f"SIGHT WORDS: {sight_words}")
    word_palette_text = '\n'.join(word_palette) or "Use simple CVC words."

    if isinstance(pages, str) and '-' in pages:
        target_pages = int(pages.split('-')[1])
    else:
        target_pages = int(pages) if pages else 12
    story_page_count = min(target_pages, 12)

    title_line = f'Title: {title}' if title else 'Suggest a catchy title (2-4 words)'
    
    prompt = f"""You are a master children's book author creating stories that are BOTH phonetically appropriate AND emotionally compelling.

Create a {story_page_count}-page story for level {level} ({spec.get('name', '')}) readers.

Concept: {concept}
Setting: {setting}
{title_line}

## WORD PALETTE (inspiration, not constraint)

{word_palette_text}

## CRITICAL RULE: LOGIC AND CONTINUITY

Every sentence MUST make logical sense. Check cause and effect. Check physical reality.

LOGIC ERRORS TO AVOID:
- "He got wet in the sun." (sun doesn't make you wet)
- "Now Max is not wet." (after a bath? he'd be soaking wet!)
- "He is wet and red." (why red? makes no sense)
- "The cat ran to sit." (awkward phrasing)

GOOD LOGIC:
- "Max jumped in the mud. Mud splashed on his nose!" (cause → effect)
- "Mom dried Max with a towel. Now his fur was fluffy." (action → result)
- "The pup ran fast. He wanted that ball!" (motivation → action)

CONTINUITY CHECK - Before writing each page, ask:
- What state is the character in from the previous page?
- What would logically happen next?
- Does this follow from what just happened?

If a phonics word doesn't fit naturally, DON'T USE IT.

## REQUIREMENTS

Level guidance: {story_guidance}
- Max {max_words} words per sentence (STRICT - count every word!)
- {story_page_count} story pages, 2-3 short sentences each
- Use SIMPLE words from the palette - avoid multi-syllable words
- Every sentence must pass the "does this make sense?" test

VOCABULARY CHECK - these are TOO HARD for early levels:
- "washes" → use "gets" or "rubs"
- "ready" → use "set"
- "water" → ok as sight word but keep sentences short
- "towel" → ok but keep it simple

AWKWARD PHRASING TO AVOID:
- "has not got" → use "wants" or "needs"
- "can not get" → use "did not get" or restructure
- "is wet and has mud" → use "is wet with mud"
- Double negatives or clunky constructions
- Sentences that sound like grammar exercises
Write like you're talking to a child, not filling in blanks.

## VISUAL STYLE FOR THIS BAND ({band})

{band_style}

Use this style guidance for visual_style field and all scene descriptions.

## WHAT MAKES A GOOD STORY

1. CHARACTER WANT - wants something specific and clear
2. OBSTACLE - a real problem (not manufactured drama)
3. TRY-FAIL - genuine attempt that fails for a logical reason
4. RESOLUTION - satisfying and earned
5. CAUSATION - each event causes the next (not random scenes)

## OUTPUT: JSON only

```json
{{{{
  "title": "Story Title",
  "summary": "One sentence description",
  "characters": {{{{
    "char_id": {{{{
      "name": "Name",
      "visual_shorthand": "brief visual description",
      "distinctive_features": ["feature1", "feature2"]
    }}}}
  }}}},
  "setting_context": "Setting description",
  "visual_style": "Describe your art style based on the VISUAL STYLE section above",
  "word_list": {{{{"sound_out": [], "sight": [], "heart": []}}}},
  "pages": [
    {{{{
      "story_page": 1,
      "text": "Story text here.",
      "scene": "Medium shot: [WHO with visual details] [ACTION verb-ing] in [WHERE with specifics]. [Mood/lighting]."
    }}}}
  ],
  "reference_prompt": "[Full 9-panel reference sheet prompt - see instructions below]"
}}}}
```

SCENE RULES:
- WHO: Character with exact visual details from characters section
- WHERE: Specific setting with lighting/atmosphere
- WHAT: Active verb describing the action
- STATE: Show character's current physical state (wet? muddy? clean? tired?)
- Shot type: Wide/Medium/Close-up
- NEVER use negations ("no ball" makes ball appear)
- Keep scenes CLEAN - no "NO TEXT" instructions (added later)

SCENE CONTINUITY - scenes must flow like a movie:
- If character got muddy on page 4, they're STILL muddy on page 5 (unless cleaned)
- If character is in the bath, they'll be WET when they get out
- Track: location changes, character state changes, time of day
- Each scene should visually connect to the previous one

REFERENCE_PROMPT (write this LAST, after completing all pages):

Write a complete 9-panel reference sheet prompt using this EXACT structure:

```
9-panel children's book reference sheet, grid layout (3x3), consistent [your visual_style] throughout all panels:

Row 1 - [MAIN CHARACTER NAME]:
[1] [Name], [full visual description], front view, [expression], cream background
[2] Same [character] [doing action from story], side view, [pose details]
[3] Same [character] [different action/expression from story], [pose details]

Row 2 - [Supporting Elements]:
[4] [Secondary character OR key object from YOUR story], [detailed visual description]
[5] **KEY MOMENT** - [Main character(s) in central story moment - this is the HERO SHOT]
[6] [Another key object/prop from YOUR story], [detailed visual description]

Row 3 - Settings:
[7] [First setting from story], [specific details], [lighting/mood]
[8] [Second setting OR different time of day], [specific details]
[9] [Final heartwarming scene with character(s)], [resolution mood]

STYLE: [Your visual_style]. Soft edges, muted earthy palette (sage, terracotta, cream, soft gold).
FORMAT: Square 1:1, 3x3 grid, thin white borders between panels.
CRITICAL: NO TEXT, NO WORDS, NO LETTERS anywhere in any panel. Pure illustration only.
```

Use SPECIFIC details from YOUR story - actual character names, actual objects, actual settings.

Output ONLY valid JSON."""

    return prompt


def parse_story_response(response: str) -> dict:
    match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
    json_str = match.group(1) if match else response.strip()
    return json.loads(json_str)


def build_book_json(story_data: dict, level: str) -> dict:
    spec = get_level_spec(level)
    band = spec.get("band", "B")
    band_info = get_band_info(band)
    title = story_data.get("title", "Untitled")
    slug = slugify(title)

    pages = [
        {"page": 1, "type": "cover", "text": title},
        {"page": 2, "type": "copyright"},
        {"page": 3, "type": "parent_guide"},
        {"page": 4, "type": "level_info"},
        {"page": 5, "type": "wordlist", "text": "Words to Know"},
    ]

    for i, sp in enumerate(story_data.get("pages", [])):
        pages.append({
            "page": 6 + i,
            "story_page": sp.get("story_page", i + 1),
            "type": "story",
            "text": sp.get("text", ""),
            "scene": sp.get("scene", "")
        })

    last = 5 + len(story_data.get("pages", []))
    pages.extend([
        {"page": last + 1, "type": "end", "text": "The End"},
        {"page": last + 2, "type": "wordsearch"},
        {"page": last + 3, "type": "series_info"},
        {"page": last + 4, "type": "back_cover", "text": ""},
    ])

    word_list = story_data.get("word_list", {})
    
    return {
        "id": slug, "title": title, "slug": slug, "level": level, "band": band,
        "targetPhonics": f"Level {level} patterns",
        "skill": f"Level {level}",
        "skill_description": story_data.get("summary", ""),
        "age_range": band_info.get("grades", "K-1"),
        "created": datetime.now().strftime("%Y-%m-%d"),
        "author": "FunBookies", "illustrator": "AI Generated",
        "summary": story_data.get("summary", ""),
        "characters": story_data.get("characters", {}),
        "setting_context": story_data.get("setting_context", ""),
        "story_bible": {
            "premise": story_data.get("summary", ""),
            "setting": story_data.get("setting_context", ""),
            "visual_style": story_data.get("visual_style", "Warm children's book illustration")
        },
        "reference_prompt": story_data.get("reference_prompt", ""),
        "word_list": word_list,
        "sightWordsUsed": word_list.get("sight", []),
        "wordsearch_words": [w for w in word_list.get("sound_out", []) if 2 <= len(w) <= 8][:8],
        "pages": pages,
        "metadata": {"generatedAt": datetime.now().isoformat(), "storyPages": len(story_data.get("pages", []))},
        "parent_tips": {"before_reading": "Look at the cover.", "during_reading": "Help sound out words.", "after_reading": "What was your favorite part?"},
    }


def generate_review_html(book: dict) -> str:
    title = book.get("title", "Untitled")
    slug = book.get("slug", "")
    level = book.get("level", "?")
    summary = book.get("summary", "")
    visual_style = book.get("story_bible", {}).get("visual_style", "")
    reference_prompt = book.get("reference_prompt", "")
    generation_prompt = book.get("metadata", {}).get("generation_prompt", "")
    characters = book.get("characters", {})
    word_list = book.get("word_list", {})
    story_pages = [p for p in book.get("pages", []) if p.get("type") == "story"]

    # Characters section
    chars_html = ""
    for cid, c in characters.items():
        features = ", ".join(c.get("distinctive_features", []))
        chars_html += f'<div class="char"><strong>{c.get("name", cid)}</strong>: {c.get("visual_shorthand", "")}<br><small>Features: {features}</small></div>'

    # Word lists
    sound_out = ", ".join(word_list.get("sound_out", []))
    sight = ", ".join(word_list.get("sight", []))
    heart = ", ".join(word_list.get("heart", []))

    # Pages
    pages_html = ""
    for p in story_pages:
        text = p.get("text", "").replace("\n", "<br>")
        scene = p.get("scene", "")
        pages_html += f'<div class="page"><h3>Page {p.get("story_page")}</h3><div class="text">{text}</div><details open><summary>Scene Description</summary><p class="scene">{scene}</p></details></div>'

    return f"""<!DOCTYPE html>
<html><head><title>Review: {title}</title>
<style>
body {{ font-family: Georgia, serif; max-width: 900px; margin: 0 auto; padding: 20px; background: #f5f5f5; }}
h1 {{ color: #2c5530; margin-bottom: 0.3em; }}
h2 {{ color: #2c5530; border-bottom: 2px solid #c8e6c9; padding-bottom: 5px; }}
.meta {{ color: #666; margin-bottom: 1.5em; }}
.section {{ background: white; padding: 20px; margin: 15px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
.page {{ background: white; padding: 20px; margin: 15px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
.text {{ font-size: 1.4em; background: #fffde7; padding: 15px; border-radius: 8px; margin: 10px 0; line-height: 1.5; }}
.scene {{ background: #e3f2fd; padding: 12px; border-radius: 6px; font-size: 0.95em; line-height: 1.4; white-space: pre-wrap; }}
.char {{ background: #f5f5f5; padding: 10px; margin: 8px 0; border-radius: 6px; }}
.ref-prompt {{ background: #fff3e0; padding: 15px; border-radius: 8px; font-family: monospace; font-size: 0.9em; white-space: pre-wrap; }}
details {{ margin-top: 10px; }}
summary {{ cursor: pointer; color: #1565c0; font-weight: bold; }}
.words {{ color: #555; }}
.words span {{ background: #e8f5e9; padding: 2px 8px; border-radius: 10px; margin: 2px; display: inline-block; }}
.words.sight span {{ background: #fff3e0; }}
.words.heart span {{ background: #fce4ec; }}
.gen-prompt {{ background: #f5f5f5; padding: 15px; border-radius: 8px; font-family: monospace; font-size: 0.8em; white-space: pre-wrap; overflow-x: auto; max-height: 500px; overflow-y: auto; }}
details.section summary {{ list-style: none; }}
details.section summary::-webkit-details-marker {{ display: none; }}
</style></head>
<body>
<h1>{title}</h1>
<p class="meta">Level {level} | {len(story_pages)} pages | Slug: {slug}</p>
<p><em>{summary}</em></p>

<div class="section">
<h2>Characters</h2>
{chars_html or "<p>No characters defined</p>"}
<p><strong>Visual Style:</strong> {visual_style}</p>
</div>

<div class="section">
<h2>Reference Image Prompt</h2>
<div class="ref-prompt">{reference_prompt or "Not generated"}</div>
</div>

<div class="section">
<h2>Word Lists</h2>
<p><strong>Sound Out:</strong> <span class="words">{sound_out}</span></p>
<p><strong>Sight:</strong> <span class="words sight">{sight}</span></p>
<p><strong>Heart:</strong> <span class="words heart">{heart}</span></p>
</div>

<h2>Story Pages</h2>
{pages_html}

<div class="section">
<h2>Next Steps</h2>
<ol>
<li>Review story quality (want/obstacle/resolution?)</li>
<li>Review scene descriptions (WHO/WHERE/WHAT?)</li>
<li>Generate reference image from prompt above</li>
<li>Run: <code>python scripts/generate_page_images.py {slug}</code></li>
</ol>
</div>

<details class="section">
<summary><h2 style="display:inline">Generation Prompt (for debugging)</h2></summary>
<pre class="gen-prompt">{generation_prompt}</pre>
</details>
</body></html>"""


def generate_story(level: str, concept: str, setting: str, title: str = None, dry_run: bool = False, no_browser: bool = False):
    print(f"\nGenerating {level} story: {concept}")
    
    prompt = build_story_prompt(level, concept, setting, title)
    if dry_run:
        print(prompt[:1500] + "\n...")
        return None

    print("Calling Claude...")
    response = call_llm(prompt)
    
    print("Parsing...")
    story_data = parse_story_response(response)
    book = build_book_json(story_data, level)
    book["metadata"]["generation_prompt"] = prompt
    slug = book["slug"]

    book_path = BOOKS_DIR / f"{slug}.json"
    with open(book_path, 'w') as f:
        json.dump(book, f, indent=2)
    print(f"Saved: {book_path}")

    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    review_path = REVIEW_DIR / f"{slug}-review.html"
    with open(review_path, 'w') as f:
        f.write(generate_review_html(book))
    print(f"Review: {review_path}")

    if not no_browser:
        webbrowser.open(f"file://{review_path.absolute()}")

    print(f"\nDone! {book['title']} ({len([p for p in book['pages'] if p['type']=='story'])} pages)")
    return book


def main():
    import argparse
    p = argparse.ArgumentParser(description="Generate a children's book")
    p.add_argument("--level", "-l", required=True, help="Reading level (B1, B2, etc)")
    p.add_argument("--concept", "-c", required=True, help="Story concept")
    p.add_argument("--setting", "-s", required=True, help="Story setting")
    p.add_argument("--title", "-t", help="Optional title")
    p.add_argument("--dry-run", action="store_true", help="Show prompt only")
    p.add_argument("--no-browser", action="store_true", help="Don't open browser")
    args = p.parse_args()

    if args.level not in LEVEL_SPECS["levels"]:
        print(f"Unknown level: {args.level}")
        sys.exit(1)

    book = generate_story(args.level, args.concept, args.setting, args.title, args.dry_run, args.no_browser)
    sys.exit(0 if book else 1)


if __name__ == "__main__":
    main()
