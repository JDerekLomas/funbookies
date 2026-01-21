#!/usr/bin/env python3
"""Generate book thumbnails with title text baked in.

Creates thumbnail images that look like the title page in the reader:
- Cover illustration as background
- Title text at bottom with white color and black outline/shadow
- Square format
"""

import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import textwrap

BOOKS_DIR = Path("/Users/dereklomas/lilbookies/public/books")
COVERS_DIR = Path("/Users/dereklomas/lilbookies/public/images/covers")
THUMBS_DIR = Path("/Users/dereklomas/lilbookies/public/images/thumbs")

# Font settings
FONT_PATH = "/System/Library/Fonts/Supplemental/Georgia Bold.ttf"
FALLBACK_FONT = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

def get_font(size):
    """Get font, with fallback."""
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except:
        try:
            return ImageFont.truetype(FALLBACK_FONT, size)
        except:
            return ImageFont.load_default()


def draw_text_with_outline(draw, position, text, font, fill="white", outline="black", outline_width=3):
    """Draw text with outline/stroke effect."""
    x, y = position
    # Draw outline
    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            if dx != 0 or dy != 0:
                draw.text((x + dx, y + dy), text, font=font, fill=outline, anchor="mm")
    # Draw main text
    draw.text((x, y), text, font=font, fill=fill, anchor="mm")


def generate_thumbnail(slug: str, title: str, size: int = 512) -> bool:
    """Generate a thumbnail for a book."""

    cover_path = COVERS_DIR / f"{slug}.png"
    thumb_path = THUMBS_DIR / f"{slug}.jpg"

    if not cover_path.exists():
        print(f"  ⚠ No cover image: {cover_path.name}")
        return False

    try:
        # Load and resize cover to square
        img = Image.open(cover_path)

        # Crop to square (center crop)
        w, h = img.size
        min_dim = min(w, h)
        left = (w - min_dim) // 2
        top = (h - min_dim) // 2
        img = img.crop((left, top, left + min_dim, top + min_dim))

        # Resize to target size
        img = img.resize((size, size), Image.Resampling.LANCZOS)

        # Convert to RGBA for compositing
        img = img.convert("RGBA")

        # Create gradient overlay at bottom
        overlay = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw_overlay = ImageDraw.Draw(overlay)

        # Draw gradient from transparent to semi-black at bottom
        gradient_height = size // 3
        for i in range(gradient_height):
            alpha = int(180 * (i / gradient_height))  # 0 to 180
            y = size - gradient_height + i
            draw_overlay.rectangle([(0, y), (size, y + 1)], fill=(0, 0, 0, alpha))

        # Composite gradient onto image
        img = Image.alpha_composite(img, overlay)

        # Draw title text
        draw = ImageDraw.Draw(img)

        # Calculate font size based on title length
        if len(title) <= 10:
            font_size = size // 8
        elif len(title) <= 20:
            font_size = size // 10
        else:
            font_size = size // 12

        font = get_font(font_size)

        # Wrap text if needed
        max_chars = 18
        if len(title) > max_chars:
            lines = textwrap.wrap(title, width=max_chars)
        else:
            lines = [title]

        # Calculate total text height
        line_height = font_size + 8
        total_height = len(lines) * line_height

        # Position text at bottom
        y_start = size - 30 - total_height // 2

        for i, line in enumerate(lines):
            y = y_start + i * line_height
            draw_text_with_outline(
                draw,
                (size // 2, y),
                line,
                font,
                fill="white",
                outline="black",
                outline_width=2
            )

        # Save as JPEG
        img = img.convert("RGB")
        img.save(thumb_path, "JPEG", quality=85)
        print(f"  ✓ {thumb_path.name}")
        return True

    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--slug", help="Generate for specific book only")
    parser.add_argument("--size", type=int, default=512, help="Thumbnail size (default: 512)")
    args = parser.parse_args()

    # Ensure output dir exists
    THUMBS_DIR.mkdir(parents=True, exist_ok=True)

    # Load manifest
    manifest_path = BOOKS_DIR / "manifest.json"
    with open(manifest_path) as f:
        books = json.load(f)

    print(f"Generating thumbnails ({args.size}x{args.size})...\n")

    # Filter if slug specified
    if args.slug:
        books = [b for b in books if b.get("slug") == args.slug]
        if not books:
            print(f"Book not found: {args.slug}")
            return

    success = 0
    for book in books:
        slug = book.get("slug")
        title = book.get("title", slug)

        print(f"[{slug}]")
        if generate_thumbnail(slug, title, args.size):
            success += 1

    print(f"\nDone! Generated {success}/{len(books)} thumbnails.")
    print(f"Output: {THUMBS_DIR}")


if __name__ == "__main__":
    main()
