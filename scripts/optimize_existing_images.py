#!/usr/bin/env python3
"""Batch optimize existing book images - generate responsive versions"""

import json
from pathlib import Path
from PIL import Image

def optimize_book_images(books_dir: Path):
    print("FunBookies Responsive Image Generator")
    print("=" * 50)

    # Define responsive widths (prioritize width, calculate height from aspect ratio)
    target_widths = {
        '4x': 800,
        '3x': 600,
        '2x': 400,
        '1x': 256,
    }

    total_saved = 0
    total_files = 0

    for image_dir in sorted(books_dir.glob("*_images")):
        print(f"\n📁 {image_dir.name}")

        for png_path in image_dir.glob("*.png"):
            # Skip if already processed (check for 1x version)
            base_path = png_path.with_suffix('')
            if Path(f"{base_path}_1x.webp").exists():
                print(f"  ⏭  {png_path.name} (already done)")
                continue

            try:
                original_size = png_path.stat().st_size

                with Image.open(png_path) as img:
                    original_width, original_height = img.size
                    aspect_ratio = original_height / original_width
                    print(f"  Processing {png_path.name} ({original_size/1024:.0f}KB, {original_width}x{original_height})")

                    # Generate responsive versions
                    for suffix, target_width in target_widths.items():
                        # Calculate height maintaining aspect ratio
                        target_height = int(target_width * aspect_ratio)

                        # WebP version
                        webp_path = f"{base_path}_{suffix}.webp"
                        resized = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
                        resized.save(webp_path, 'WEBP', quality=85, method=6)

                        # PNG fallback
                        png_fallback = f"{base_path}_{suffix}.png"
                        resized.save(png_fallback, 'PNG', optimize=True, compress_level=9)

                    # Thumbnail for LQIP
                    thumb = img.copy()
                    thumb.thumbnail((20, 16), Image.Resampling.LANCZOS)
                    thumb_path = f"{base_path}_thumb.webp"
                    thumb.save(thumb_path, 'WEBP', quality=60)

                    # Optimize original
                    img.save(str(png_path), 'PNG', optimize=True, compress_level=9)

                # Calculate savings (comparing original to 2x WebP - typical mobile use)
                webp_2x_size = Path(f"{base_path}_2x.webp").stat().st_size
                saved = original_size - webp_2x_size
                total_saved += saved
                total_files += 1

                print(f"    ✓ Generated 4 sizes + thumbnail")
                print(f"    💾 Typical savings: {saved/1024:.0f}KB ({saved*100/original_size:.0f}%)")

            except Exception as e:
                print(f"  ✗ {png_path.name}: {e}")

    print(f"\n{'='*50}")
    print(f"✅ Processed {total_files} images")
    if total_files > 0:
        print(f"💾 Average savings per image: {total_saved/total_files/1024:.0f}KB")
    print(f"💾 Total potential savings: {total_saved/1024/1024:.1f}MB")

if __name__ == "__main__":
    books_dir = Path(__file__).parent.parent / "public" / "books"

    if not books_dir.exists():
        print(f"❌ Error: Books directory not found at {books_dir}")
        exit(1)

    optimize_book_images(books_dir)
