#!/usr/bin/env python3
"""Add missing educational content to books (parent_tips, comprehension, etc.)."""

import json
import re
from pathlib import Path
from typing import Optional

BOOKS_DIR = Path("/Users/dereklomas/lilbookies/public/books")


def extract_story_text(book: dict) -> str:
    """Extract all story text from a book."""
    pages = book.get("pages", [])
    texts = []
    for page in pages:
        if page.get("type") == "story" and page.get("text"):
            texts.append(page["text"])
    return " ".join(texts)


def extract_key_words(book: dict) -> list[str]:
    """Extract decodable/phonics words from a book."""
    # Check various locations for word lists
    words = []

    # word_list format
    word_list = book.get("word_list", {})
    if isinstance(word_list, dict):
        words.extend(word_list.get("sound_out", []))
        words.extend(word_list.get("decodable", {}).get("cvc", []))
        words.extend(word_list.get("decodable", {}).get("digraphs", []))

    # sightWordsUsed
    words.extend(book.get("sightWordsUsed", []))

    # metadata targetPatternWords
    meta = book.get("metadata", {})
    words.extend(meta.get("targetPatternWords", []))

    # Dedupe and filter
    words = list(set(w.lower() for w in words if len(w) >= 3))
    return words[:20]  # Limit to 20


def get_main_characters(book: dict) -> list[str]:
    """Extract main character names from the book."""
    title = book.get("title", "")
    text = extract_story_text(book)

    # Common pattern: title often contains character name
    characters = []

    # Check character field
    char_info = book.get("character", {})
    if char_info.get("names"):
        characters.extend(char_info["names"])

    # Look for capitalized words that might be names
    words = re.findall(r'\b[A-Z][a-z]+\b', text)
    name_candidates = [w for w in set(words) if w not in ["The", "A", "I", "He", "She", "It", "They", "We", "One", "But", "And", "This", "That"]]

    characters.extend(name_candidates[:3])

    return list(set(characters))[:3]


def get_phonics_focus(book: dict) -> str:
    """Get the phonics/skills focus of the book."""
    return (
        book.get("targetPhonics") or
        book.get("skill") or
        ", ".join(book.get("targetSkills", [])) or
        book.get("phonics_focus", ["general"])[0] if isinstance(book.get("phonics_focus"), list) else
        "reading skills"
    )


def generate_parent_tips(book: dict) -> dict:
    """Generate parent_tips based on book content."""
    title = book.get("title", "this book")
    phonics = get_phonics_focus(book)
    characters = get_main_characters(book)
    band = book.get("band", "B")

    char_str = characters[0] if characters else "the character"

    # Customize by band
    if band == "A":
        before = f"Look at the cover together. Point to pictures and ask: What do you see? This book helps practice {phonics}."
        during = f"Point to each word as you read. Encourage your child to find pictures that match the words."
        after = f"Ask: What happened in the story? Can you find your favorite picture?"
    elif band == "B":
        before = f"Preview the cover of '{title}'. Ask: What do you think will happen? Look for words with {phonics}."
        during = f"When you see tricky words, help your child sound them out. Notice words that use {phonics}."
        after = f"Ask: What was the problem in the story? How was it solved? What did {char_str} learn?"
    elif band == "C":
        before = f"Look at the title and cover of '{title}'. Ask: What might this story be about? This book focuses on {phonics}."
        during = f"Pause to discuss new vocabulary words. Encourage your child to use context clues and {phonics} patterns."
        after = f"Discuss the story together. Ask: Why did {char_str} make those choices? What would you have done differently?"
    else:  # D band
        before = f"Preview '{title}' and make predictions. Discuss any challenging vocabulary: {phonics}."
        during = f"Encourage independent reading. Pause to discuss plot developments and character motivations."
        after = f"Have a conversation about themes in the story. Ask: What message did the author want to share?"

    return {
        "before_reading": before,
        "during_reading": during,
        "after_reading": after
    }


def generate_comprehension_questions(book: dict) -> list[dict]:
    """Generate comprehension questions based on book content."""
    text = extract_story_text(book)
    characters = get_main_characters(book)
    title = book.get("title", "the story")

    char = characters[0] if characters else "the main character"

    # Basic question templates
    questions = [
        {"question": f"Who is the main character in '{title}'?", "answer": char if characters else "Check the story"},
        {"question": "What happens at the beginning of the story?", "answer": "The story introduces the characters and setting"},
        {"question": "What problem does the character face?", "answer": "The main challenge in the story"},
        {"question": f"How does {char} solve the problem?", "answer": "Through determination and help from friends"},
        {"question": "What lesson can we learn from this story?", "answer": "A positive message about friendship, perseverance, or kindness"}
    ]

    return questions[:5]


def generate_wordsearch_words(book: dict) -> list[str]:
    """Generate wordsearch words from book content."""
    words = extract_key_words(book)

    # Also extract words from story text
    text = extract_story_text(book)
    story_words = re.findall(r'\b[a-z]{3,8}\b', text.lower())

    # Get most common story words (excluding common sight words)
    common_sight = {"the", "and", "was", "for", "are", "but", "not", "you", "all", "can", "had", "her", "was", "one", "our", "out", "his", "has", "she", "two", "how", "its", "way", "may"}
    story_words = [w for w in story_words if w not in common_sight]

    from collections import Counter
    word_counts = Counter(story_words)
    frequent = [w for w, c in word_counts.most_common(20) if c >= 2]

    # Combine and dedupe
    all_words = list(set(words + frequent))

    # Filter to good wordsearch words (4-8 letters)
    good_words = [w for w in all_words if 4 <= len(w) <= 8]

    return good_words[:8]


def generate_summary(book: dict) -> str:
    """Generate a brief summary of the book."""
    title = book.get("title", "This book")
    characters = get_main_characters(book)
    phonics = get_phonics_focus(book)

    char_str = " and ".join(characters) if characters else "the characters"

    return f"{title} is a story about {char_str}. This book helps readers practice {phonics} while enjoying an engaging adventure."


def generate_word_list(book: dict) -> dict:
    """Generate word_list structure if missing."""
    text = extract_story_text(book)

    # Extract words from text
    words = re.findall(r'\b[a-z]+\b', text.lower())

    # Categorize
    sight_words = ["a", "i", "the", "is", "to", "and", "it", "in", "on", "my", "see", "he", "she", "we", "be", "you", "are", "was", "for", "said", "have", "they", "come", "what", "there", "down", "out"]
    sound_out = []
    new_words = []

    for word in set(words):
        if word in sight_words:
            continue
        elif len(word) <= 5 and word.isalpha():
            sound_out.append(word)
        elif len(word) > 5:
            new_words.append(word)

    return {
        "sound_out": sorted(set(sound_out))[:20],
        "sight": [w for w in sight_words if w in words][:15],
        "new": sorted(set(new_words))[:5]
    }


def update_book(slug: str, dry_run: bool = True) -> dict:
    """Update a single book with missing content."""
    book_path = BOOKS_DIR / f"{slug}.json"
    if not book_path.exists():
        return {"error": f"Book not found: {slug}"}

    with open(book_path) as f:
        book = json.load(f)

    if not isinstance(book, dict) or "pages" not in book:
        return {"error": f"Invalid book format: {slug}"}

    changes = []

    # Add missing parent_tips
    if not book.get("parent_tips"):
        book["parent_tips"] = generate_parent_tips(book)
        changes.append("parent_tips")

    # Add missing comprehension_questions
    if not book.get("comprehension_questions"):
        book["comprehension_questions"] = generate_comprehension_questions(book)
        changes.append("comprehension_questions")

    # Add missing wordsearch_words
    if not book.get("wordsearch_words"):
        book["wordsearch_words"] = generate_wordsearch_words(book)
        changes.append("wordsearch_words")

    # Add missing summary
    if not book.get("summary"):
        book["summary"] = generate_summary(book)
        changes.append("summary")

    # Add missing word_list
    if not book.get("word_list"):
        book["word_list"] = generate_word_list(book)
        changes.append("word_list")

    if changes and not dry_run:
        with open(book_path, "w") as f:
            json.dump(book, f, indent=2)
        print(f"  Updated {slug}: {', '.join(changes)}")

    return {"slug": slug, "changes": changes}


def update_all_books(dry_run: bool = True):
    """Update all books with missing content."""
    results = []

    for book_file in sorted(BOOKS_DIR.glob("*.json")):
        slug = book_file.stem
        result = update_book(slug, dry_run=dry_run)
        if result.get("changes"):
            results.append(result)

    return results


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Add missing content to books")
    parser.add_argument("--book", type=str, help="Update specific book")
    parser.add_argument("--all", action="store_true", help="Update all books")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be changed without changing")
    parser.add_argument("--apply", action="store_true", help="Actually apply changes")
    args = parser.parse_args()

    dry_run = not args.apply

    if args.book:
        result = update_book(args.book, dry_run=dry_run)
        if result.get("changes"):
            mode = "Would add" if dry_run else "Added"
            print(f"{mode}: {', '.join(result['changes'])}")
        else:
            print(f"No changes needed for {args.book}")
    elif args.all:
        results = update_all_books(dry_run=dry_run)
        mode = "Would update" if dry_run else "Updated"
        print(f"\n{mode} {len(results)} books:")
        for r in results:
            print(f"  {r['slug']}: {', '.join(r['changes'])}")

        if dry_run:
            print("\nRun with --apply to make changes")
    else:
        print("Specify --book <slug> or --all")
        print("Use --dry-run to preview changes")
        print("Use --apply to actually make changes")


if __name__ == "__main__":
    main()
