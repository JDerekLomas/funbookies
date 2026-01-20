#!/usr/bin/env python3
"""Audit all books and generate a status report.

Checks each book for:
- Story quality indicators (story_bible, characters, summary)
- Reference image (9-panel or multi-ref)
- Page images
- Basic stats (pages, words)

Outputs:
- Console summary
- BOOK_ROADMAP.md with full audit
"""

import json
import os
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
BOOKS_DIR = PROJECT_ROOT / "public" / "books"
REFS_DIR = BOOKS_DIR / "references"
IMAGES_DIR = BOOKS_DIR / "images"
COVERS_DIR = PROJECT_ROOT / "public" / "images" / "covers"


def audit_book(slug: str) -> dict:
    """Audit a single book and return status dict."""
    book_path = BOOKS_DIR / f"{slug}.json"

    if not book_path.exists():
        return {"slug": slug, "error": "File not found"}

    with open(book_path) as f:
        book = json.load(f)

    # Basic info
    level = book.get("level", "?")
    band = level[0] if level else "?"
    title = book.get("title", slug)

    # Page stats
    pages = book.get("pages", [])
    story_pages = [p for p in pages if p.get("type") == "story"]
    total_words = sum(len((p.get("text") or "").split()) for p in pages)

    # Story quality indicators
    has_story_bible = bool(book.get("story_bible"))
    has_characters = bool(book.get("characters"))
    has_summary = bool(book.get("summary"))
    has_reference_prompt = bool(book.get("reference_prompt"))

    # Check for scene descriptions (not just placeholders)
    scenes_ok = 0
    scenes_placeholder = 0
    for p in story_pages:
        scene = p.get("scene", "")
        if scene and not scene.startswith("Illustration for:") and len(scene) > 50:
            scenes_ok += 1
        elif scene:
            scenes_placeholder += 1

    # Reference image check
    ref_9panel = (REFS_DIR / f"{slug}_reference.png").exists()
    ref_multi_dir = REFS_DIR / f"{slug}_multi"
    ref_multi = ref_multi_dir.exists() and (ref_multi_dir / "manifest.json").exists()

    # Count multi-ref images if exists
    multi_ref_count = 0
    if ref_multi:
        try:
            with open(ref_multi_dir / "manifest.json") as f:
                manifest = json.load(f)
                multi_ref_count = len(manifest.get("references", {}))
        except:
            pass

    # Page images check
    images_found = 0
    images_missing = 0
    for i, p in enumerate(pages):
        page_num = p.get("page", i + 1)
        page_type = p.get("type", "story")

        if page_type == "cover":
            img_path = COVERS_DIR / f"{slug}.png"
        else:
            img_path = IMAGES_DIR / f"{slug}_page{str(page_num).zfill(2)}.png"

        # Also check without padding
        img_path_alt = IMAGES_DIR / f"{slug}_page{page_num}.png"

        if img_path.exists() or img_path_alt.exists():
            images_found += 1
        else:
            images_missing += 1

    # Determine status
    if images_found == len(pages) and (ref_9panel or ref_multi):
        status = "complete"
    elif images_found > 0:
        status = "partial"
    elif ref_9panel or ref_multi:
        status = "has-ref"
    elif has_reference_prompt:
        status = "has-prompt"
    elif has_story_bible or has_characters:
        status = "has-story"
    else:
        status = "minimal"

    # Calculate a simple quality score
    quality_score = 0
    if has_story_bible: quality_score += 2
    if has_characters: quality_score += 2
    if has_summary: quality_score += 1
    if has_reference_prompt: quality_score += 1
    if scenes_ok > 0: quality_score += min(scenes_ok, 3)

    return {
        "slug": slug,
        "title": title,
        "level": level,
        "band": band,
        "pages": len(pages),
        "story_pages": len(story_pages),
        "words": total_words,
        "has_story_bible": has_story_bible,
        "has_characters": has_characters,
        "has_summary": has_summary,
        "has_reference_prompt": has_reference_prompt,
        "scenes_ok": scenes_ok,
        "scenes_placeholder": scenes_placeholder,
        "ref_9panel": ref_9panel,
        "ref_multi": ref_multi,
        "multi_ref_count": multi_ref_count,
        "images_found": images_found,
        "images_missing": images_missing,
        "status": status,
        "quality_score": quality_score,
    }


def str_pad(s, n):
    """Left-pad a string for table alignment (Python version of padStart)."""
    return str(s).zfill(n)


def generate_roadmap(audits: list[dict]) -> str:
    """Generate markdown roadmap from audit results."""

    # Sort by band, then level, then quality score descending
    def sort_key(a):
        band_order = {"A": 0, "B": 1, "C": 2, "D": 3, "?": 9}
        return (band_order.get(a["band"], 9), a["level"], -a["quality_score"])

    audits_sorted = sorted(audits, key=sort_key)

    # Group by status for summary
    by_status = {}
    for a in audits:
        status = a.get("status", "unknown")
        by_status.setdefault(status, []).append(a)

    lines = [
        "# Book Roadmap",
        "",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## Summary",
        "",
        f"- **Total books:** {len(audits)}",
        f"- **Complete:** {len(by_status.get('complete', []))}",
        f"- **Partial images:** {len(by_status.get('partial', []))}",
        f"- **Has reference:** {len(by_status.get('has-ref', []))}",
        f"- **Has prompt only:** {len(by_status.get('has-prompt', []))}",
        f"- **Has story only:** {len(by_status.get('has-story', []))}",
        f"- **Minimal:** {len(by_status.get('minimal', []))}",
        "",
        "## Status Legend",
        "",
        "| Status | Meaning |",
        "|--------|---------|",
        "| complete | Has reference + all page images |",
        "| partial | Has some page images |",
        "| has-ref | Has reference image but no page images |",
        "| has-prompt | Has reference_prompt but no reference image |",
        "| has-story | Has story_bible/characters but no prompt |",
        "| minimal | Basic book data only |",
        "",
        "## Priority Guide",
        "",
        "- **P1 (Showcase):** Quality score 6+, good for demos",
        "- **P2 (Solid):** Quality score 3-5, needs images",
        "- **P3 (Rework):** Quality score 0-2, needs story work",
        "",
        "---",
        "",
        "## Full Audit",
        "",
        "| Slug | Level | Pages | Words | Story | Ref | Images | Status | Score | Priority |",
        "|------|-------|-------|-------|-------|-----|--------|--------|-------|----------|",
    ]

    for a in audits_sorted:
        # Story quality indicator
        story_parts = []
        if a["has_story_bible"]: story_parts.append("SB")
        if a["has_characters"]: story_parts.append("CH")
        if a["has_reference_prompt"]: story_parts.append("RP")
        story_indicator = ",".join(story_parts) if story_parts else "-"

        # Reference indicator
        if a["ref_9panel"] and a["ref_multi"]:
            ref_indicator = "9p+multi"
        elif a["ref_9panel"]:
            ref_indicator = "9-panel"
        elif a["ref_multi"]:
            ref_indicator = f"multi({a['multi_ref_count']})"
        else:
            ref_indicator = "-"

        # Images indicator
        if a["images_missing"] == 0 and a["images_found"] > 0:
            img_indicator = f"✅ {a['images_found']}"
        elif a["images_found"] > 0:
            img_indicator = f"{a['images_found']}/{a['images_found'] + a['images_missing']}"
        else:
            img_indicator = "-"

        # Priority
        score = a["quality_score"]
        if score >= 6:
            priority = "P1"
        elif score >= 3:
            priority = "P2"
        else:
            priority = "P3"

        lines.append(
            f"| {a['slug']} | {a['level']} | {a['pages']} | {a['words']} | "
            f"{story_indicator} | {ref_indicator} | {img_indicator} | "
            f"{a['status']} | {score} | {priority} |"
        )

    # Add sections by band
    lines.extend([
        "",
        "---",
        "",
        "## By Band",
        "",
    ])

    for band in ["A", "B", "C", "D"]:
        band_books = [a for a in audits_sorted if a["band"] == band]
        if not band_books:
            continue

        complete = len([b for b in band_books if b["status"] == "complete"])
        lines.extend([
            f"### Band {band} ({len(band_books)} books, {complete} complete)",
            "",
        ])

        for a in band_books:
            status_emoji = {
                "complete": "✅",
                "partial": "🔶",
                "has-ref": "🖼️",
                "has-prompt": "📝",
                "has-story": "📖",
                "minimal": "⚪",
            }.get(a["status"], "❓")

            lines.append(f"- {status_emoji} **{a['slug']}** - {a['title']} ({a['status']})")

        lines.append("")

    # Other books (no standard band)
    other_books = [a for a in audits_sorted if a["band"] not in ["A", "B", "C", "D"]]
    if other_books:
        lines.extend([
            "### Other/Uncategorized",
            "",
        ])
        for a in other_books:
            lines.append(f"- **{a['slug']}** - {a['title']} (level: {a['level']})")
        lines.append("")

    return "\n".join(lines)


def main():
    # Find all book JSON files
    book_files = sorted(BOOKS_DIR.glob("*.json"))

    print(f"Auditing {len(book_files)} books...")
    print()

    audits = []
    errors = []

    for book_file in book_files:
        slug = book_file.stem
        try:
            audit = audit_book(slug)
            if "error" in audit:
                errors.append(audit)
            else:
                audits.append(audit)
        except Exception as e:
            errors.append({"slug": slug, "error": str(e)})

    # Print summary
    print(f"Successfully audited: {len(audits)}")
    print(f"Errors: {len(errors)}")

    if errors:
        print("\nErrors:")
        for e in errors:
            print(f"  - {e['slug']}: {e['error']}")

    # Status counts
    by_status = {}
    for a in audits:
        status = a.get("status", "unknown")
        by_status.setdefault(status, []).append(a)

    print("\nBy Status:")
    for status in ["complete", "partial", "has-ref", "has-prompt", "has-story", "minimal"]:
        count = len(by_status.get(status, []))
        print(f"  {status}: {count}")

    # Generate roadmap
    roadmap = generate_roadmap(audits)
    roadmap_path = PROJECT_ROOT / "BOOK_ROADMAP.md"

    with open(roadmap_path, "w") as f:
        f.write(roadmap)

    print(f"\nRoadmap written to: {roadmap_path}")


if __name__ == "__main__":
    main()
