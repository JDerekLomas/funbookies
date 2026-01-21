#!/usr/bin/env python3
"""Migrate books from separate level_info + wordlist pages to combined level_wordlist."""

import json
from pathlib import Path

BOOKS_DIR = Path(__file__).parent.parent / "public" / "books"

def migrate_book(book_path: Path) -> bool:
    """Migrate a single book. Returns True if changes were made."""
    with open(book_path) as f:
        book = json.load(f)

    # Skip non-dict files (like index.json which is a list)
    if not isinstance(book, dict):
        return False

    pages = book.get("pages", [])
    if not pages:
        return False

    # Find level_info and wordlist pages
    level_info_idx = None
    wordlist_idx = None

    for i, page in enumerate(pages):
        if page.get("type") == "level_info":
            level_info_idx = i
        elif page.get("type") == "wordlist":
            wordlist_idx = i

    # Skip if already migrated or doesn't have both
    if level_info_idx is None or wordlist_idx is None:
        return False

    # Check if they're consecutive (level_info then wordlist)
    if wordlist_idx != level_info_idx + 1:
        print(f"  WARNING: {book_path.name} - level_info and wordlist not consecutive, skipping")
        return False

    # Get the page number of the level_info page
    level_info_page = pages[level_info_idx]
    page_num = level_info_page.get("page", level_info_idx + 1)

    # Replace level_info with level_wordlist
    pages[level_info_idx] = {
        "page": page_num,
        "type": "level_wordlist"
    }

    # Remove wordlist page
    del pages[wordlist_idx]

    # Renumber all subsequent pages (decrease by 1)
    for i in range(wordlist_idx, len(pages)):
        if "page" in pages[i]:
            pages[i]["page"] -= 1

    # Update the book
    book["pages"] = pages

    # Write back
    with open(book_path, "w") as f:
        json.dump(book, f, indent=2)

    return True

def main():
    book_files = sorted(BOOKS_DIR.glob("*.json"))

    # Skip index.json
    book_files = [f for f in book_files if f.name != "index.json"]

    migrated = 0
    skipped = 0

    for book_path in book_files:
        if migrate_book(book_path):
            print(f"✓ Migrated: {book_path.name}")
            migrated += 1
        else:
            skipped += 1

    print(f"\nDone! Migrated {migrated} books, skipped {skipped}")

if __name__ == "__main__":
    main()
