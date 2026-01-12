#!/usr/bin/env python3
"""Generate book-specific parent tips and comprehension questions.

Analyzes actual story content to create tailored educational materials
instead of using generic templates.
"""

import json
import re
from pathlib import Path
from dataclasses import dataclass

BOOKS_DIR = Path("/Users/dereklomas/lilbookies/public/books")


@dataclass
class StoryAnalysis:
    """Analysis of a book's story content."""
    title: str
    band: str
    characters: list[str]
    settings: list[str]
    key_events: list[str]
    problem: str
    resolution: str
    phonics_focus: str
    target_words: list[str]
    theme: str


def extract_story_pages(book: dict) -> list[dict]:
    """Get all story pages with text."""
    pages = []
    structural_types = {"cover", "copyright", "parent_guide", "level_info", "wordlist",
                       "end", "wordsearch", "series_info", "back_cover", "activity"}

    for page in book.get("pages", []):
        page_type = page.get("type", "")
        has_text = bool(page.get("text", "").strip())

        # Include if it's marked as story OR has text and isn't a structural page
        if page_type == "story" or (has_text and page_type not in structural_types):
            pages.append({
                "num": page.get("story_page", page.get("page")),
                "text": page["text"],
                "scene": page.get("scene", "")
            })
    return pages


def analyze_story(book: dict) -> StoryAnalysis:
    """Analyze a book's story to extract key elements."""
    title = book.get("title", "")
    band = book.get("band", "B")
    pages = extract_story_pages(book)

    # Get full story text
    full_text = " ".join(p["text"] for p in pages)
    all_scenes = " ".join(p.get("scene", "") for p in pages)

    # Extract characters (capitalized words that appear multiple times)
    words = re.findall(r'\b[A-Z][a-z]+\b', full_text)
    skip_words = {"The", "A", "I", "He", "She", "It", "They", "We", "But", "And",
                  "This", "That", "Then", "Now", "Yes", "No", "Oh", "Wow", "Look"}
    character_counts = {}
    for w in words:
        if w not in skip_words:
            character_counts[w] = character_counts.get(w, 0) + 1
    characters = [w for w, c in sorted(character_counts.items(), key=lambda x: -x[1]) if c >= 2][:3]

    # Also check for common character nouns (lowercase but repeated)
    animal_chars = ["pup", "cat", "dog", "frog", "owl", "mouse", "pig", "fox", "snail",
                   "elephant", "kitten", "puppy", "knight", "robot", "bird"]
    for animal in animal_chars:
        if full_text.lower().count(animal) >= 3 and animal.title() not in characters:
            characters.append(f"the {animal}")
            break

    # Extract settings from scenes
    setting_keywords = ["house", "home", "garden", "forest", "park", "beach", "school",
                       "farm", "city", "pond", "lake", "mud", "bed", "rug", "tub",
                       "castle", "village", "mountain", "lighthouse", "bridge"]
    settings = []
    for kw in setting_keywords:
        if kw in full_text.lower() or kw in all_scenes.lower():
            settings.append(kw)

    # Extract key events (sentences with action words)
    action_patterns = [
        r'(\w+) (ran|run|jump|hop|splash|got|get|find|found|see|saw|went|go)',
        r'(The \w+) (is|was|can|did)',
    ]
    events = []
    for page in pages[:5]:  # First 5 pages for beginning
        events.append(("beginning", page["text"]))
    for page in pages[len(pages)//2:len(pages)//2+2]:  # Middle
        events.append(("middle", page["text"]))
    for page in pages[-3:]:  # End
        events.append(("end", page["text"]))

    # Identify problem and resolution
    problem = ""
    resolution = ""

    # Look for problem indicators
    problem_words = ["but", "not", "can't", "cannot", "need", "want", "where", "how",
                    "lost", "stuck", "hot", "cold", "sad", "scared", "help"]
    for page in pages:
        text_lower = page["text"].lower()
        for pw in problem_words:
            if pw in text_lower:
                problem = page["text"]
                break
        if problem:
            break

    # Resolution is usually in last few pages
    if pages:
        resolution = pages[-1]["text"]

    # Get phonics focus
    phonics = (
        book.get("targetPhonics") or
        book.get("skill") or
        ", ".join(book.get("targetSkills", [])) or
        "reading"
    )

    # Get target words
    word_list = book.get("word_list", {})
    target_words = word_list.get("sound_out", [])[:10]

    # Identify theme
    themes = {
        "friendship": ["friend", "together", "help", "share"],
        "adventure": ["go", "find", "explore", "discover", "quest"],
        "fun and play": ["fun", "play", "run", "jump", "splash"],
        "problem-solving": ["try", "find", "how", "way", "fix"],
        "family": ["mom", "dad", "sister", "brother", "family"],
        "nature": ["tree", "flower", "animal", "bird", "fish"],
        "growing up": ["learn", "new", "can", "did", "first"],
    }
    theme = "adventure"
    for t, keywords in themes.items():
        if any(kw in full_text.lower() for kw in keywords):
            theme = t
            break

    return StoryAnalysis(
        title=title,
        band=band,
        characters=characters,
        settings=settings,
        key_events=[(pos, text) for pos, text in events],
        problem=problem,
        resolution=resolution,
        phonics_focus=phonics,
        target_words=target_words,
        theme=theme
    )


def generate_specific_parent_tips(analysis: StoryAnalysis) -> dict:
    """Generate book-specific parent tips."""
    chars = analysis.characters[0] if analysis.characters else "the main character"
    words = ", ".join(analysis.target_words[:5]) if analysis.target_words else "key words"

    if analysis.band == "A":
        before = f"Look at the cover of '{analysis.title}'. Ask your child: What do you see? Point to the pictures and name things together. This book practices words like: {words}."
        during = f"Point to each word as you read. Help your child find {chars} on each page. When you see words like {words}, sound them out slowly together."
        after = f"Ask: What did {chars} do? Can you find your favorite picture? Let's say some of the words together: {words}."

    elif analysis.band == "B":
        setting = analysis.settings[0] if analysis.settings else "the story"
        before = f"Preview '{analysis.title}' together. Ask: What do you think {chars} will do? Look for short vowel words like: {words}."
        during = f"Help your child sound out tricky words. Notice the short vowel pattern in words like {words}. Encourage expression when reading!"
        # Use problem text or generic question
        problem_q = f"What happened when {chars} got into trouble" if analysis.problem else f"What did {chars} do"
        after = f"Discuss: {problem_q}? What happened at the end? What was your favorite part about the {setting}?"

    elif analysis.band == "C":
        before = f"Read the title '{analysis.title}' and look at the cover. Ask: What might happen in this story? This book focuses on {analysis.phonics_focus}."
        during = f"Encourage your child to read independently. When they get stuck, help them use context clues and {analysis.phonics_focus} patterns."
        after = f"Ask deeper questions: Why do you think {chars} made that choice? How did the story change from beginning to end? What would you have done?"

    else:  # D band
        before = f"Preview '{analysis.title}' and make predictions about the plot. Discuss any challenging vocabulary related to {analysis.phonics_focus}."
        during = f"Let your child read independently. Pause occasionally to discuss character motivations and plot developments."
        after = f"Have a conversation about the themes in the story. Ask: What message do you think the author wanted to share? How did {chars} grow or change?"

    return {
        "before_reading": before,
        "during_reading": during,
        "after_reading": after
    }


def generate_specific_questions(analysis: StoryAnalysis, book: dict) -> list[dict]:
    """Generate book-specific comprehension questions."""
    pages = extract_story_pages(book)
    chars = analysis.characters[0] if analysis.characters else "the main character"

    questions = []

    # Question 1: Character identification (always specific)
    if analysis.characters:
        questions.append({
            "question": f"Who is the main character in this story?",
            "answer": analysis.characters[0]
        })

    # Question 2: Beginning - what happens first
    if pages:
        first_page = pages[0]["text"]
        questions.append({
            "question": "What happens at the very beginning of the story?",
            "answer": first_page
        })

    # Question 3: Problem or challenge (from actual text)
    if analysis.problem:
        # Extract the core problem
        questions.append({
            "question": f"What challenge does {chars} face in the story?",
            "answer": analysis.problem
        })
    elif len(pages) > 2:
        # Use middle of story if no clear problem
        mid_page = pages[len(pages)//2]["text"]
        questions.append({
            "question": "What happens in the middle of the story?",
            "answer": mid_page
        })

    # Question 4: Resolution - how it ends
    if analysis.resolution:
        questions.append({
            "question": "How does the story end?",
            "answer": analysis.resolution
        })

    # Question 5: Theme or lesson (tailored)
    theme_questions = {
        "friendship": f"How do the characters show friendship in this story?",
        "adventure": f"What adventure does {chars} go on?",
        "fun and play": f"What fun activities happen in this story?",
        "problem-solving": f"How does {chars} solve the problem?",
        "family": f"How does the family work together?",
        "nature": f"What does {chars} discover about nature?",
        "growing up": f"What does {chars} learn by the end?",
    }
    theme_q = theme_questions.get(analysis.theme, f"What do you think {chars} learned?")

    # Find answer in last few pages
    end_text = " ".join(p["text"] for p in pages[-2:]) if pages else "The character learned something important"
    questions.append({
        "question": theme_q,
        "answer": end_text
    })

    return questions[:5]


def improve_book(slug: str, dry_run: bool = True) -> dict:
    """Improve a single book's parent tips and comprehension questions."""
    book_path = BOOKS_DIR / f"{slug}.json"
    if not book_path.exists():
        return {"error": f"Book not found: {slug}"}

    with open(book_path) as f:
        book = json.load(f)

    if not isinstance(book, dict):
        return {"error": f"Invalid book format: {slug}"}

    # Analyze the story
    analysis = analyze_story(book)

    # Generate new content
    new_tips = generate_specific_parent_tips(analysis)
    new_questions = generate_specific_questions(analysis, book)

    changes = []

    # Check if current content is template-based
    current_tips = book.get("parent_tips", {})
    current_qs = book.get("comprehension_questions", [])

    # Detect template patterns
    is_template_tips = any([
        "What do you think will happen?" in current_tips.get("before_reading", ""),
        "reading skills" in current_tips.get("before_reading", ""),
        "Look at the cover together" in current_tips.get("before_reading", "")
    ])

    is_template_qs = any(
        "What problem does the character face?" in q.get("question", "") or
        "What lesson can we learn" in q.get("question", "")
        for q in current_qs
    )

    if is_template_tips:
        book["parent_tips"] = new_tips
        changes.append("parent_tips")

    if is_template_qs:
        book["comprehension_questions"] = new_questions
        changes.append("comprehension_questions")

    if changes and not dry_run:
        with open(book_path, "w") as f:
            json.dump(book, f, indent=2)

    return {
        "slug": slug,
        "analysis": {
            "characters": analysis.characters,
            "settings": analysis.settings,
            "theme": analysis.theme,
            "problem": analysis.problem[:50] + "..." if len(analysis.problem) > 50 else analysis.problem
        },
        "changes": changes,
        "new_tips": new_tips if "parent_tips" in changes else None,
        "new_questions": new_questions if "comprehension_questions" in changes else None
    }


def improve_all_books(dry_run: bool = True) -> list:
    """Improve all books with template-based content."""
    results = []

    for book_file in sorted(BOOKS_DIR.glob("*.json")):
        slug = book_file.stem
        result = improve_book(slug, dry_run=dry_run)
        if result.get("changes"):
            results.append(result)
            print(f"  {slug}: {', '.join(result['changes'])}")

    return results


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Improve book content with specific details")
    parser.add_argument("--book", type=str, help="Improve specific book")
    parser.add_argument("--all", action="store_true", help="Improve all books")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes")
    parser.add_argument("--apply", action="store_true", help="Apply changes")
    parser.add_argument("--show", action="store_true", help="Show generated content")
    args = parser.parse_args()

    dry_run = not args.apply

    if args.book:
        result = improve_book(args.book, dry_run=dry_run)
        print(f"\nAnalysis for {args.book}:")
        print(f"  Characters: {result.get('analysis', {}).get('characters', [])}")
        print(f"  Settings: {result.get('analysis', {}).get('settings', [])}")
        print(f"  Theme: {result.get('analysis', {}).get('theme', '')}")

        if args.show or result.get("changes"):
            print(f"\n  Changes: {result.get('changes', [])}")
            if result.get("new_tips"):
                print(f"\n  New Parent Tips:")
                for k, v in result["new_tips"].items():
                    print(f"    {k}: {v[:80]}...")
            if result.get("new_questions"):
                print(f"\n  New Questions:")
                for q in result["new_questions"]:
                    print(f"    Q: {q['question'][:60]}...")
                    print(f"    A: {q['answer'][:60]}...")

        if dry_run and result.get("changes"):
            print("\n  Run with --apply to save changes")

    elif args.all:
        mode = "Preview" if dry_run else "Applying"
        print(f"\n{mode} improvements to books with template content:\n")
        results = improve_all_books(dry_run=dry_run)
        print(f"\n{'Would improve' if dry_run else 'Improved'} {len(results)} books")

        if dry_run:
            print("\nRun with --apply to save changes")

    else:
        print("Usage:")
        print("  --book <slug>    Analyze/improve specific book")
        print("  --all            Improve all books with templates")
        print("  --dry-run        Preview changes (default)")
        print("  --apply          Save changes")
        print("  --show           Show generated content")


if __name__ == "__main__":
    main()
