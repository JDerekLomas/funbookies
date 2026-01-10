#!/usr/bin/env python3
"""
Optimize all book images for web delivery.

Uses pngquant for lossy PNG compression (~70-80% size reduction).
"""

import subprocess
import sys
from pathlib import Path

BOOKS_DIR = Path("/Users/dereklomas/lilbookies/public/books")
PAGES_DIR = BOOKS_DIR / "images"
REFS_DIR = BOOKS_DIR / "references"
COVERS_DIR = Path("/Users/dereklomas/lilbookies/public/images/covers")


def get_file_size(path: Path) -> int:
    """Get file size in bytes."""
    return path.stat().st_size if path.exists() else 0


def format_size(size: int) -> str:
    """Format size in human readable format."""
    if size < 1024:
        return f"{size}B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.1f}KB"
    else:
        return f"{size / (1024 * 1024):.1f}MB"


def optimize_png(path: Path, quality: str = "65-80") -> tuple[int, int]:
    """
    Optimize a PNG file using pngquant.

    Returns (original_size, new_size).
    """
    original_size = get_file_size(path)

    # pngquant overwrites with --force --ext .png
    result = subprocess.run(
        ["pngquant", "--force", "--ext", ".png", "--quality", quality, str(path)],
        capture_output=True,
        text=True
    )

    new_size = get_file_size(path)
    return original_size, new_size


def optimize_directory(directory: Path, pattern: str = "*.png") -> dict:
    """Optimize all PNGs in a directory."""
    stats = {
        "files": 0,
        "original_total": 0,
        "new_total": 0,
        "errors": 0
    }

    for path in directory.glob(pattern):
        try:
            original, new = optimize_png(path)
            stats["files"] += 1
            stats["original_total"] += original
            stats["new_total"] += new

            reduction = ((original - new) / original * 100) if original > 0 else 0
            print(f"  {path.name}: {format_size(original)} → {format_size(new)} ({reduction:.0f}% smaller)")
        except Exception as e:
            print(f"  {path.name}: ERROR - {e}")
            stats["errors"] += 1

    return stats


def main():
    print("="*60)
    print("IMAGE OPTIMIZATION")
    print("="*60)

    total_original = 0
    total_new = 0
    total_files = 0

    # Optimize page images
    print("\n[PAGE IMAGES]")
    stats = optimize_directory(PAGES_DIR)
    total_original += stats["original_total"]
    total_new += stats["new_total"]
    total_files += stats["files"]

    # Optimize covers
    print("\n[COVER IMAGES]")
    stats = optimize_directory(COVERS_DIR)
    total_original += stats["original_total"]
    total_new += stats["new_total"]
    total_files += stats["files"]

    # Optimize references
    print("\n[REFERENCE IMAGES]")
    stats = optimize_directory(REFS_DIR)
    total_original += stats["original_total"]
    total_new += stats["new_total"]
    total_files += stats["files"]

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Files optimized: {total_files}")
    print(f"Original size: {format_size(total_original)}")
    print(f"New size: {format_size(total_new)}")

    if total_original > 0:
        reduction = (total_original - total_new) / total_original * 100
        saved = total_original - total_new
        print(f"Space saved: {format_size(saved)} ({reduction:.0f}%)")


if __name__ == "__main__":
    main()
