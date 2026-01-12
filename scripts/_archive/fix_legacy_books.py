#!/usr/bin/env python3
"""Fix legacy books - add scene descriptions and correct content."""

import json
from pathlib import Path

BOOKS_DIR = Path("/Users/dereklomas/lilbookies/public/books")


def fix_volcano():
    """Fix volcano.json with proper content and scene descriptions."""
    book_path = BOOKS_DIR / "volcano.json"

    with open(book_path) as f:
        book = json.load(f)

    # Fix parent_tips
    book["parent_tips"] = {
        "before_reading": "Look at the cover. Ask: What is Gus looking at? What do you know about volcanoes? This book practices CVC words like 'hot', 'got', 'top', and 'run'.",
        "during_reading": "Point out the CVC words: sat, got, top, pit, hot, pop, run. Help your child blend the sounds. Use an excited voice for the action words!",
        "after_reading": "Ask: Was it safe for Gus to climb the volcano? What did he see? Would you want to see a volcano?"
    }

    # Fix comprehension_questions
    book["comprehension_questions"] = [
        {"question": "Where did Gus sit at the beginning?", "answer": "On a rock"},
        {"question": "What did Gus see at the top?", "answer": "A big pit with lava"},
        {"question": "What sounds did the volcano make?", "answer": "Hiss, puff, pop"},
        {"question": "What did Gus do when the magma got big?", "answer": "He ran away"},
        {"question": "How did Gus feel at the end?", "answer": "Excited and proud - Wow! Wow! Wow!"}
    ]

    # Fix summary
    book["summary"] = "Gus the adventurer climbs a big hill that turns out to be a volcano! He sees the hot lava and has to run when it starts to bubble. A fun CVC word adventure about curiosity and excitement."

    # Fix wordsearch_words
    book["wordsearch_words"] = ["gus", "rock", "lava", "hot", "run", "top", "pit", "wow"]

    # Add scene descriptions to pages
    scenes = {
        1: "A cheerful cartoon character named Gus standing in front of a large smoking volcano, looking excited and adventurous. Bright colors, child-friendly style.",
        3: "Gus sitting on a gray rock in a grassy field, looking curious. A large hill (volcano) visible in the background. Simple cartoon style.",
        4: "Gus looking up at a big hill with wonder. The hill has smoke coming from the top. Gus points excitedly.",
        5: "Gus starting to climb the hill, determined expression, one foot on the slope. Speech bubble feeling.",
        6: "Gus climbing higher and higher up the volcano slope. Motion lines showing upward movement. Energetic pose.",
        7: "Gus reaching the top of the volcano, arms raised in triumph. Standing on the crater rim.",
        8: "Gus peering down into a large dark pit/crater. His eyes are wide with curiosity. Steam rising.",
        9: "View inside the volcano crater showing bright red and orange lava bubbling. Dramatic and exciting but not scary.",
        10: "Gus with huge excited eyes and open mouth, amazed at what he sees. Stars and excitement marks around him.",
        11: "The volcano making sounds - steam hissing, smoke puffing, bubbles popping. Onomatopoeia visual effects.",
        12: "The red magma/lava rising and getting bigger inside the crater. Gus looking concerned.",
        13: "Gus feeling the heat, wiping his brow. Heat waves visible. The lava glowing bright orange-red.",
        14: "Gus turning to run, looking back at the volcano. Urgent expression. Starting to move fast.",
        15: "Gus running down the volcano slope at full speed. Legs moving fast, determined face.",
        16: "Gus still running, getting closer to safety. The volcano smoking behind him in the distance.",
        17: "Gus back at his original rock, safe and sound. Looking relieved and happy. Volcano in background.",
        18: "Gus shaking his head 'no' but smiling - he's not done adventuring! Playful expression.",
        19: "Gus striking a proud pose, chest puffed out. He accomplished his goal!",
        20: "Gus telling his story excitedly, gesturing toward the volcano in the background. Happy and proud.",
        21: "Gus celebrating with arms raised, big smile. Stars and celebration marks. The volcano peaceful in background.",
        22: "Final scene: Gus waving goodbye, volcano behind him. 'The End' feeling. Warm sunset colors."
    }

    for page in book["pages"]:
        page_num = page.get("page")
        if page_num in scenes:
            page["scene"] = scenes[page_num]

    # Save
    with open(book_path, "w") as f:
        json.dump(book, f, indent=2)

    print("Fixed volcano.json")


def add_scenes_to_book(slug: str, character_desc: str, scenes: dict):
    """Add scene descriptions to a book's pages."""
    book_path = BOOKS_DIR / f"{slug}.json"

    with open(book_path) as f:
        book = json.load(f)

    for page in book.get("pages", []):
        page_num = page.get("page")
        if page_num in scenes:
            page["scene"] = scenes[page_num]

    with open(book_path, "w") as f:
        json.dump(book, f, indent=2)

    print(f"Added scenes to {slug}.json")


def fix_dog_pink():
    """Add scenes to dog_pink.json."""
    scenes = {
        1: "A cute fluffy brown dog with floppy ears and big eyes on the cover, looking playfully guilty. Pink/orange accents.",
        3: "The brown dog jumping on a couch, cushions flying everywhere. Playful chaos.",
        4: "The dog digging in a flower garden, dirt flying, flowers scattered. Naughty but cute.",
        5: "The dog splashing in a mud puddle, mud splatters everywhere. Joyful expression.",
        6: "The dog running through the house with toilet paper trailing behind.",
        7: "The dog knocking over a plant pot, soil spilling. Oops expression.",
        8: "The dog chewing on a shoe, looking innocent despite the evidence.",
        9: "A child hugging the messy dog anyway, both smiling. Love despite the chaos.",
        10: "The dog sleeping peacefully, finally tired out. Cute ending."
    }
    add_scenes_to_book("dog_pink", "cute fluffy brown dog with floppy ears", scenes)


def fix_elephant_red():
    """Add scenes to elephant_red.json."""
    book_path = BOOKS_DIR / "elephant_red.json"
    with open(book_path) as f:
        book = json.load(f)

    # Check if pages have text to determine scenes
    pages = book.get("pages", [])
    scenes = {}

    for i, page in enumerate(pages):
        text = page.get("text", "")
        page_num = page.get("page", i + 1)

        if "stomp" in text.lower():
            scenes[page_num] = "A big friendly elephant stomping with big feet, dust clouds rising. Energetic and fun."
        elif "trunk" in text.lower():
            scenes[page_num] = "The elephant spraying water with its trunk, water droplets sparkling."
        elif "big" in text.lower():
            scenes[page_num] = "The large elephant standing tall, showing how big it is compared to surroundings."
        elif "eat" in text.lower() or "food" in text.lower():
            scenes[page_num] = "The elephant eating leaves or hay, trunk curled around food."
        elif page.get("type") == "cover":
            scenes[page_num] = "A happy cartoon elephant with big ears and friendly eyes on the cover."
        elif page.get("type") == "story":
            scenes[page_num] = "The friendly elephant in a colorful savanna setting, warm colors."

    for page in pages:
        page_num = page.get("page")
        if page_num in scenes and not page.get("scene"):
            page["scene"] = scenes[page_num]

    with open(book_path, "w") as f:
        json.dump(book, f, indent=2)
    print("Fixed elephant_red.json")


def fix_mouse_gold():
    """Add scenes to mouse_gold.json."""
    book_path = BOOKS_DIR / "mouse_gold.json"
    with open(book_path) as f:
        book = json.load(f)

    pages = book.get("pages", [])
    scenes = {}

    for i, page in enumerate(pages):
        text = page.get("text", "")
        page_num = page.get("page", i + 1)

        if "house" in text.lower():
            scenes[page_num] = "A tiny mouse exploring inside a cozy house, warm golden lighting."
        elif "cheese" in text.lower():
            scenes[page_num] = "The mouse finding a piece of yellow cheese, eyes wide with excitement."
        elif "cat" in text.lower():
            scenes[page_num] = "The mouse hiding from a cat, peeking out nervously."
        elif "run" in text.lower():
            scenes[page_num] = "The mouse running quickly, little legs moving fast."
        elif "hide" in text.lower():
            scenes[page_num] = "The mouse hiding in a small hole or behind furniture."
        elif page.get("type") == "cover":
            scenes[page_num] = "A cute small brown mouse with big ears and whiskers on the cover."
        elif page.get("type") == "story":
            scenes[page_num] = "The little mouse in a house setting, golden warm tones."

    for page in pages:
        page_num = page.get("page")
        if page_num in scenes and not page.get("scene"):
            page["scene"] = scenes[page_num]

    with open(book_path, "w") as f:
        json.dump(book, f, indent=2)
    print("Fixed mouse_gold.json")


def fix_castle():
    """Add scenes to castle.json."""
    book_path = BOOKS_DIR / "castle.json"
    with open(book_path) as f:
        book = json.load(f)

    pages = book.get("pages", [])
    scenes = {}

    for i, page in enumerate(pages):
        text = page.get("text", "")
        page_num = page.get("page", i + 1)

        if "castle" in text.lower():
            scenes[page_num] = "A grand stone castle with tall towers and flags, medieval fantasy style."
        elif "rat" in text.lower():
            scenes[page_num] = "Cute cartoon rats scurrying through castle corridors."
        elif "king" in text.lower():
            scenes[page_num] = "A friendly cartoon king with a crown sitting on a throne."
        elif "queen" in text.lower():
            scenes[page_num] = "A kind queen in a royal dress and tiara."
        elif "knight" in text.lower():
            scenes[page_num] = "A brave knight in shiny armor with a sword and shield."
        elif page.get("type") == "cover":
            scenes[page_num] = "A medieval castle with cute rats peeking out of windows and doorways."
        elif page.get("type") == "story":
            scenes[page_num] = "Inside a cozy castle with stone walls and torches, rats exploring."

    for page in pages:
        page_num = page.get("page")
        if page_num in scenes and not page.get("scene"):
            page["scene"] = scenes[page_num]

    with open(book_path, "w") as f:
        json.dump(book, f, indent=2)
    print("Fixed castle.json")


def main():
    print("Fixing legacy books...")
    fix_volcano()
    fix_dog_pink()
    fix_elephant_red()
    fix_mouse_gold()
    fix_castle()
    print("\nDone! All legacy books fixed.")


if __name__ == "__main__":
    main()
