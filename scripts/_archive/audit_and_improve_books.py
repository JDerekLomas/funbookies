#!/usr/bin/env python3
"""Audit books against quality rubric and generate missing content."""

import json
import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

BOOKS_DIR = Path("/Users/dereklomas/lilbookies/public/books")
REFS_DIR = BOOKS_DIR / "references"
PAGES_DIR = BOOKS_DIR / "images"
COVERS_DIR = Path("/Users/dereklomas/lilbookies/public/images/covers")


@dataclass
class BookAudit:
    """Audit results for a single book."""
    slug: str
    title: str = ""
    band: str = ""
    level: str = ""

    # Structure checks
    has_parent_tips: bool = False
    has_comprehension: bool = False
    has_word_list: bool = False
    has_wordsearch: bool = False
    has_summary: bool = False
    has_reference_prompt: bool = False
    pages_with_scenes: int = 0
    total_story_pages: int = 0

    # Image checks
    has_reference_image: bool = False
    has_cover_image: bool = False
    page_images_count: int = 0

    # Scores
    structure_score: int = 0
    image_score: int = 0
    alignment_score: int = 0

    # Issues
    issues: list = field(default_factory=list)

    @property
    def total_score(self) -> int:
        return self.structure_score + self.image_score + self.alignment_score

    @property
    def grade(self) -> str:
        score = self.total_score
        if score >= 32: return "A"
        if score >= 26: return "B"
        if score >= 18: return "C"
        if score >= 10: return "D"
        return "F"

    @property
    def image_coverage(self) -> float:
        if self.total_story_pages == 0:
            return 0
        return self.page_images_count / self.total_story_pages


def audit_book(slug: str) -> Optional[BookAudit]:
    """Audit a single book."""
    book_path = BOOKS_DIR / f"{slug}.json"
    if not book_path.exists():
        return None

    with open(book_path) as f:
        book = json.load(f)

    # Skip non-book JSON files (arrays, etc.)
    if not isinstance(book, dict):
        return None

    # Skip if no pages (not a real book)
    if "pages" not in book:
        return None

    audit = BookAudit(slug=slug)
    audit.title = book.get("title", slug)
    audit.band = book.get("band", "?")
    audit.level = book.get("level", "?")

    # Structure checks
    audit.has_parent_tips = bool(book.get("parent_tips"))
    audit.has_comprehension = bool(book.get("comprehension_questions"))
    audit.has_word_list = bool(book.get("word_list"))
    audit.has_wordsearch = bool(book.get("wordsearch_words"))
    audit.has_summary = bool(book.get("summary"))
    audit.has_reference_prompt = bool(book.get("reference_prompt"))

    # Count pages - include pages with text that aren't structural types
    pages = book.get("pages", [])
    structural_types = {"cover", "copyright", "parent_guide", "level_info", "wordlist", "end", "wordsearch", "series_info", "back_cover", "title"}
    story_pages = [p for p in pages if p.get("type") == "story" or (p.get("text") and p.get("type") not in structural_types)]
    audit.total_story_pages = len(story_pages)
    audit.pages_with_scenes = len([p for p in story_pages if p.get("scene") or p.get("image_prompt")])

    # Image checks
    ref_v2 = REFS_DIR / f"{slug}_reference_v2.png"
    ref_v1 = REFS_DIR / f"{slug}_reference.png"
    audit.has_reference_image = ref_v2.exists() or ref_v1.exists()
    audit.has_cover_image = (COVERS_DIR / f"{slug}.png").exists()

    # Count page images
    page_images = list(PAGES_DIR.glob(f"{slug}_page*.png"))
    audit.page_images_count = len(page_images)

    # Calculate structure score (max 15)
    # 1.1 Structure completeness (0-3)
    struct_count = sum([
        audit.has_parent_tips,
        audit.has_comprehension,
        audit.has_word_list,
        audit.has_wordsearch,
        audit.has_summary
    ])
    if struct_count >= 5:
        struct_complete = 3
    elif struct_count >= 3:
        struct_complete = 2
    elif struct_count >= 1:
        struct_complete = 1
    else:
        struct_complete = 0

    # 1.4 Educational value - check for phonics focus
    has_phonics = bool(book.get("targetPhonics") or book.get("targetSkills") or book.get("phonics_focus"))
    edu_score = 2 if has_phonics else 1

    # 1.5 Parent support
    parent_score = 0
    if audit.has_parent_tips:
        tips = book.get("parent_tips", {})
        if all(k in tips for k in ["before_reading", "during_reading", "after_reading"]):
            parent_score = 3
        elif len(tips) >= 2:
            parent_score = 2
        else:
            parent_score = 1

    # Simplified scoring (we can't evaluate narrative quality automatically)
    audit.structure_score = struct_complete + edu_score + parent_score + 4  # +4 for assumed narrative

    # Calculate image score (max 12)
    # 2.1 Coverage
    if audit.has_cover_image and audit.image_coverage >= 0.9:
        coverage_score = 3
    elif audit.has_cover_image and audit.image_coverage >= 0.5:
        coverage_score = 2
    elif audit.has_cover_image:
        coverage_score = 1
    else:
        coverage_score = 0

    # 2.2 Style consistency (assume 2 if has reference)
    style_score = 2 if audit.has_reference_image else 0

    # 2.3/2.4 Visual clarity and text-free (assume 2 each for generated images)
    visual_score = 2 if audit.page_images_count > 0 else 0

    audit.image_score = coverage_score + style_score + visual_score + 2  # +2 baseline

    # Calculate alignment score (max 9)
    # 3.3 Scene prompt quality
    if audit.pages_with_scenes == audit.total_story_pages and audit.total_story_pages > 0:
        scene_score = 3
    elif audit.pages_with_scenes > audit.total_story_pages * 0.5:
        scene_score = 2
    elif audit.pages_with_scenes > 0:
        scene_score = 1
    else:
        scene_score = 0

    # Assume moderate alignment for other scores
    audit.alignment_score = scene_score + 4  # +4 for assumed text-image match

    # Identify issues
    if not audit.has_parent_tips:
        audit.issues.append("Missing parent_tips")
    if not audit.has_comprehension:
        audit.issues.append("Missing comprehension_questions")
    if not audit.has_word_list:
        audit.issues.append("Missing word_list")
    if not audit.has_wordsearch:
        audit.issues.append("Missing wordsearch_words")
    if not audit.has_summary:
        audit.issues.append("Missing summary")
    if not audit.has_reference_image:
        audit.issues.append("Missing reference image")
    if not audit.has_cover_image:
        audit.issues.append("Missing cover image")
    if audit.page_images_count < audit.total_story_pages:
        audit.issues.append(f"Missing page images ({audit.page_images_count}/{audit.total_story_pages})")
    if audit.pages_with_scenes < audit.total_story_pages:
        audit.issues.append(f"Pages missing scene descriptions ({audit.pages_with_scenes}/{audit.total_story_pages})")

    return audit


def audit_all_books() -> list[BookAudit]:
    """Audit all books in the books directory."""
    audits = []

    for book_file in sorted(BOOKS_DIR.glob("*.json")):
        slug = book_file.stem
        audit = audit_book(slug)
        if audit:
            audits.append(audit)

    return audits


def print_audit_report(audits: list[BookAudit]):
    """Print a formatted audit report."""
    print("=" * 80)
    print("BOOK QUALITY AUDIT REPORT")
    print("=" * 80)

    # Sort by band then by score
    audits_sorted = sorted(audits, key=lambda a: (a.band, -a.total_score))

    # Group by band
    bands = {}
    for audit in audits_sorted:
        band = audit.band
        if band not in bands:
            bands[band] = []
        bands[band].append(audit)

    for band in sorted(bands.keys()):
        print(f"\n{'='*40}")
        print(f"BAND {band}")
        print("="*40)

        for audit in bands[band]:
            grade_emoji = {"A": "✅", "B": "🟢", "C": "🟡", "D": "🟠", "F": "🔴"}
            print(f"\n{grade_emoji.get(audit.grade, '❓')} [{audit.grade}] {audit.title} ({audit.level})")
            print(f"   Score: {audit.total_score}/36 (Story:{audit.structure_score} Image:{audit.image_score} Align:{audit.alignment_score})")
            print(f"   Images: {audit.page_images_count}/{audit.total_story_pages} pages | Ref: {'✓' if audit.has_reference_image else '✗'} | Cover: {'✓' if audit.has_cover_image else '✗'}")
            if audit.issues:
                print(f"   Issues: {', '.join(audit.issues[:3])}")
                if len(audit.issues) > 3:
                    print(f"           +{len(audit.issues)-3} more")

    # Summary stats
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    grades = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
    for audit in audits:
        grades[audit.grade] += 1

    print(f"\nTotal books: {len(audits)}")
    print(f"Grades: A={grades['A']} B={grades['B']} C={grades['C']} D={grades['D']} F={grades['F']}")

    # Common issues
    issue_counts = {}
    for audit in audits:
        for issue in audit.issues:
            base_issue = issue.split("(")[0].strip()
            issue_counts[base_issue] = issue_counts.get(base_issue, 0) + 1

    print("\nMost common issues:")
    for issue, count in sorted(issue_counts.items(), key=lambda x: -x[1])[:5]:
        print(f"  {count:3d} books: {issue}")

    # Books needing most work
    print("\nBooks needing most work (grade D/F):")
    for audit in sorted(audits, key=lambda a: a.total_score)[:10]:
        if audit.grade in ["D", "F"]:
            print(f"  {audit.slug}: {audit.total_score}/36 - {', '.join(audit.issues[:2])}")


def get_books_needing_content() -> dict:
    """Get lists of books needing specific content."""
    audits = audit_all_books()

    needs = {
        "parent_tips": [],
        "comprehension": [],
        "word_list": [],
        "wordsearch": [],
        "summary": [],
        "page_images": [],
    }

    for audit in audits:
        if not audit.has_parent_tips:
            needs["parent_tips"].append(audit.slug)
        if not audit.has_comprehension:
            needs["comprehension"].append(audit.slug)
        if not audit.has_word_list:
            needs["word_list"].append(audit.slug)
        if not audit.has_wordsearch:
            needs["wordsearch"].append(audit.slug)
        if not audit.has_summary:
            needs["summary"].append(audit.slug)
        if audit.page_images_count < audit.total_story_pages:
            needs["page_images"].append((audit.slug, audit.page_images_count, audit.total_story_pages))

    return needs


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Audit book quality")
    parser.add_argument("--book", type=str, help="Audit specific book")
    parser.add_argument("--band", type=str, help="Audit specific band (A, B, C, D)")
    parser.add_argument("--needs", action="store_true", help="Show what's needed")
    args = parser.parse_args()

    if args.book:
        audit = audit_book(args.book)
        if audit:
            print_audit_report([audit])
        else:
            print(f"Book not found: {args.book}")
    elif args.needs:
        needs = get_books_needing_content()
        print("Books needing content:\n")
        for category, books in needs.items():
            if books:
                print(f"{category}: {len(books)} books")
                if category == "page_images":
                    for slug, have, need in books[:5]:
                        print(f"  - {slug}: {have}/{need}")
                else:
                    for slug in books[:5]:
                        print(f"  - {slug}")
                if len(books) > 5:
                    print(f"  ... and {len(books)-5} more")
                print()
    else:
        audits = audit_all_books()
        if args.band:
            audits = [a for a in audits if a.band == args.band.upper()]
        print_audit_report(audits)


if __name__ == "__main__":
    main()
