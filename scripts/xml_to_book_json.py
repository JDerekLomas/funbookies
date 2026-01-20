#!/usr/bin/env python3
"""
Convert Book XML to Reader JSON format.

Takes the XML output from generate_book_xml.py and converts it
to the JSON format used by the FunBookies reader.
"""

import json
import re
import sys
from pathlib import Path
from datetime import datetime
import xml.etree.ElementTree as ET

PROJECT_ROOT = Path(__file__).parent.parent
BOOKS_DIR = PROJECT_ROOT / "public" / "books"


def parse_book_xml(xml_path: Path) -> dict:
    """Parse book XML and extract all components."""

    with open(xml_path) as f:
        content = f.read()

    # Parse XML
    root = ET.fromstring(content)

    # Extract metadata
    metadata = root.find("metadata")
    title = metadata.find("title").text if metadata.find("title") is not None else "Untitled"
    slug = metadata.find("slug").text if metadata.find("slug") is not None else "untitled"
    band = metadata.find("band").text if metadata.find("band") is not None else "B"
    level = metadata.find("level").text if metadata.find("level") is not None else "B1"

    # Extract validation
    validation = root.find("validation")
    decodability = validation.find("actual_decodability").text if validation is not None else "N/A"

    # Extract story bible
    story_bible = root.find("story_bible")
    premise = story_bible.find("premise").text if story_bible.find("premise") is not None else ""
    setting = story_bible.find("setting").text if story_bible.find("setting") is not None else ""
    characters = story_bible.find("characters").text if story_bible.find("characters") is not None else ""
    art_style = story_bible.find("art_style").text if story_bible.find("art_style") is not None else ""

    # Extract reference prompt
    ref_prompt_elem = root.find("reference_prompt")
    reference_prompt = ref_prompt_elem.text.strip() if ref_prompt_elem is not None else ""

    # Extract story pages
    story_elem = root.find("story")
    story_pages = []
    if story_elem is not None:
        for page in story_elem.findall("page"):
            page_num = int(page.get("n", 0))
            texts = [t.text for t in page.findall("text") if t.text]
            story_pages.append({
                "page_num": page_num,
                "text": "\n".join(texts),
            })

    # Extract scenes
    scenes_elem = root.find("scenes")
    scenes = {}
    if scenes_elem is not None:
        for page in scenes_elem.findall("page"):
            page_num = int(page.get("n", 0))
            scene = page.find("scene")
            image_prompt = page.find("image_prompt")
            scenes[page_num] = {
                "scene": scene.text if scene is not None else "",
                "image_prompt": image_prompt.text if image_prompt is not None else "",
            }

    return {
        "title": title,
        "slug": slug,
        "band": band,
        "level": level,
        "decodability": decodability,
        "premise": premise,
        "setting": setting,
        "characters": characters,
        "art_style": art_style,
        "reference_prompt": reference_prompt,
        "story_pages": story_pages,
        "scenes": scenes,
    }


def create_book_json(parsed: dict) -> dict:
    """Create book JSON structure from parsed XML."""

    # Build pages array
    pages = [
        {"page": 1, "type": "cover", "text": parsed["title"]},
        {"page": 2, "type": "copyright"},
        {"page": 3, "type": "parent_guide"},
        {"page": 4, "type": "level_info"},
        {"page": 5, "type": "wordlist", "text": "Words to Know"},
    ]

    # Add story pages
    for i, sp in enumerate(parsed["story_pages"], 1):
        page_num = 5 + i
        scene_data = parsed["scenes"].get(sp["page_num"], {})

        pages.append({
            "page": page_num,
            "story_page": i,
            "type": "story",
            "text": sp["text"],
            "scene": scene_data.get("scene", ""),
            "image_prompt": scene_data.get("image_prompt", ""),
        })

    # Add end matter
    story_end_page = 5 + len(parsed["story_pages"])
    pages.extend([
        {"page": story_end_page + 1, "type": "end", "text": "The End"},
        {"page": story_end_page + 2, "type": "wordsearch"},
        {"page": story_end_page + 3, "type": "series_info"},
        {"page": story_end_page + 4, "type": "back_cover", "text": ""},
    ])

    # Extract word list from story
    all_text = " ".join(sp["text"] for sp in parsed["story_pages"])
    words = list(set(re.findall(r'[a-zA-Z]+', all_text.lower())))

    return {
        "id": parsed["slug"],
        "title": parsed["title"],
        "slug": parsed["slug"],
        "level": parsed["level"],
        "band": parsed["band"],
        "targetPhonics": f"Level {parsed['level']} patterns",
        "skill": f"Level {parsed['level']}",
        "skill_description": parsed.get("premise", ""),
        "age_range": "K-1" if parsed["band"] == "B" else "Pre-K",
        "created": datetime.now().strftime("%Y-%m-%d"),
        "author": "FunBookies",
        "illustrator": "AI Generated",
        "summary": parsed["premise"],
        "characters": {},
        "setting_context": parsed["setting"],
        "story_bible": {
            "premise": parsed["premise"],
            "setting": parsed["setting"],
            "characters": parsed["characters"],
            "visual_style": parsed["art_style"],
        },
        "word_list": {
            "sound_out": words[:20],
            "sight": [],
            "heart": [],
        },
        "sightWordsUsed": [],
        "wordsearch_words": words[:8],
        "pages": pages,
        "metadata": {
            "generatedAt": datetime.now().isoformat(),
            "decodability": parsed["decodability"],
            "storyPages": len(parsed["story_pages"]),
        },
        "reference_prompt": parsed["reference_prompt"],
        "parent_tips": {
            "before_reading": f"Look at the cover. What do you see?",
            "during_reading": f"Help your child sound out the words.",
            "after_reading": "What was your favorite part?",
        },
        "comprehension_questions": [
            {"question": "What happens at the beginning?", "answer": ""},
            {"question": "What happens in the middle?", "answer": ""},
            {"question": "How does it end?", "answer": ""},
        ],
    }


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Convert book XML to JSON")
    parser.add_argument("xml_path", help="Path to book XML file")
    parser.add_argument("--output", help="Output JSON path (default: public/books/{slug}.json)")
    args = parser.parse_args()

    xml_path = Path(args.xml_path)
    if not xml_path.exists():
        print(f"File not found: {xml_path}")
        sys.exit(1)

    print(f"Parsing: {xml_path}")
    parsed = parse_book_xml(xml_path)

    print(f"  Title: {parsed['title']}")
    print(f"  Level: {parsed['level']}")
    print(f"  Story pages: {len(parsed['story_pages'])}")
    print(f"  Decodability: {parsed['decodability']}")

    book_json = create_book_json(parsed)

    if args.output:
        output_path = Path(args.output)
    else:
        output_path = BOOKS_DIR / f"{parsed['slug']}.json"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(book_json, f, indent=2)

    print(f"\n✓ Saved to: {output_path}")


if __name__ == "__main__":
    main()
