#!/usr/bin/env python3
"""Shared image utilities for book generation scripts.

Consolidates common functions used across:
- generate_covers.py
- generate_page_images.py
- generate_references.py
"""

import base64
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
BOOKS_DIR = PROJECT_ROOT / "public/books"
REFS_DIR = BOOKS_DIR / "references"
IMAGES_DIR = BOOKS_DIR / "images"
COVERS_DIR = PROJECT_ROOT / "public/images/covers"


def image_to_base64_uri(path: Path) -> str:
    """Convert image file to data URI.

    Args:
        path: Path to image file (PNG or JPEG)

    Returns:
        Data URI string (e.g., "data:image/png;base64,...")
    """
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    ext = path.suffix.lower()
    mime = "image/png" if ext == ".png" else "image/jpeg"
    return f"data:{mime};base64,{b64}"


def find_reference_image(slug: str) -> tuple[Path | None, str | None]:
    """Find the reference image for a book, checking versioned files.

    Looks for reference images in order of preference: v4, v3, v2, v1 (no suffix).

    Args:
        slug: Book slug (e.g., "the-red-balloon")

    Returns:
        Tuple of (path, version) or (None, None) if not found.
        Version is a string like "v4", "v3", "v2", or "v1".
    """
    versions = ["_v4", "_v3", "_v2", ""]
    for version in versions:
        suffix = f"_reference{version}.png"
        path = REFS_DIR / f"{slug}{suffix}"
        if path.exists():
            version_str = version.replace("_", "") if version else "v1"
            return path, version_str
    return None, None


def find_multi_references(slug: str) -> tuple[list[Path], str | None]:
    """Find multi-ref images for a book (3-ref strategy).

    Looks for the {slug}_multi/ directory with characters, settings, style sheets.

    Args:
        slug: Book slug (e.g., "mud-pup-fun")

    Returns:
        Tuple of (list of paths, strategy) or ([], None) if not found.
        Returns paths in order: [characters, settings, style]
    """
    multi_dir = REFS_DIR / f"{slug}_multi"
    if not multi_dir.exists():
        return [], None

    paths = []
    sheet_types = ["characters", "settings", "style"]
    for sheet_type in sheet_types:
        path = multi_dir / f"{slug}_{sheet_type}.png"
        if path.exists():
            paths.append(path)

    if len(paths) == 3:
        return paths, "multi-3ref"
    elif len(paths) > 0:
        return paths, f"multi-{len(paths)}ref"
    return [], None


def find_best_references(slug: str) -> tuple[list[Path], str]:
    """Find the best available references for a book.

    Prefers multi-ref strategy if available, falls back to single ref.

    Args:
        slug: Book slug

    Returns:
        Tuple of (list of paths, strategy_name)
        - For multi-ref: ([characters.png, settings.png, style.png], "multi-3ref")
        - For single ref: ([reference.png], "single")
        - If none found: ([], "none")
    """
    # Try multi-ref first
    multi_paths, multi_strategy = find_multi_references(slug)
    if multi_paths:
        return multi_paths, multi_strategy

    # Fall back to single reference
    single_path, version = find_reference_image(slug)
    if single_path:
        return [single_path], f"single-{version}"

    return [], "none"


def get_character_block(book: dict) -> str:
    """Extract a consistent character description block from book data.

    Uses visual_shorthand from characters field for concise, consistent descriptions.
    Falls back to building from appearance fields if shorthand not available.

    Args:
        book: Book JSON data dict

    Returns:
        Multi-line string with character descriptions, or empty string if none.
    """
    # Try new schema first (characters plural)
    characters = book.get("characters", {})

    # Fall back to old schema (character singular)
    if not characters:
        characters = book.get("character", {})

    char_lines = []
    for key, char_data in characters.items():
        if isinstance(char_data, dict) and key not in ["names", "style_notes"]:
            # Prefer visual_shorthand if available (new schema)
            if char_data.get("visual_shorthand"):
                char_lines.append(char_data["visual_shorthand"])
            elif char_data.get("appearance"):
                # Build from appearance (new schema)
                app = char_data["appearance"]
                name = char_data.get("name", key.capitalize())
                parts = [f"{name}:"]
                if app.get("body"):
                    parts.append(app["body"])
                if app.get("fur_color"):
                    parts.append(f"with {app['fur_color']} fur")
                if app.get("distinguishing_mark"):
                    parts.append(f"- {app['distinguishing_mark']} (KEY FEATURE)")
                if app.get("ears"):
                    parts.append(f"- {app['ears']}")
                if app.get("tail"):
                    parts.append(f"- {app['tail']}")
                if app.get("posture"):
                    parts.append(f"- {app['posture']}")
                char_lines.append(" ".join(parts))
            else:
                # Old schema fallback
                name = key.capitalize()
                species = char_data.get("species", "")
                color = char_data.get("color", "")
                body = char_data.get("body", "")
                distinguishing = char_data.get("distinguishing_feature", "")

                parts = []
                if species:
                    parts.append(species)
                if color:
                    parts.append(f"({color})")
                if body:
                    parts.append(body)
                if distinguishing:
                    parts.append(f"- {distinguishing}")

                if parts:
                    char_lines.append(f"{name}: {' '.join(parts)}")

    return "\n".join(char_lines)
