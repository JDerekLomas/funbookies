#!/usr/bin/env python3
"""Batch optimize existing book images - generate responsive versions"""

import json
from pathlib import Path
from PIL import Image

# Book registry from reader.html - only process these images
BOOK_REGISTRY = {
    'dog_pink': {'imageFolder': 'images', 'imagePrefix': 'dog_pink_page'},
    'pig_yellow': {'imageFolder': 'images', 'imagePrefix': 'pig_yellow_page'},
    'volcano': {'imageFolder': 'volcano_images', 'imagePrefix': 'page_'},
    'castle': {'imageFolder': 'castle_images', 'imagePrefix': 'page_'},
    'elephant_red': {'imageFolder': 'images', 'imagePrefix': 'elephant_red_page'},
    'fox_purple': {'imageFolder': 'images', 'imagePrefix': 'fox_purple_page'},
    'snail_blue': {'imageFolder': 'images', 'imagePrefix': 'snail_blue_page'},
    'owl_green': {'imageFolder': 'images', 'imagePrefix': 'owl_green_page'},
    'mouse_gold': {'imageFolder': 'images', 'imagePrefix': 'mouse_gold_page'}
}

def get_missing_versions(png_path: Path) -> list[str]:
    """Check which responsive versions are missing and return list of suffixes to generate

    Returns:
        List of suffixes that need to be generated (e.g., ['1x', '2x', 'thumb'])
        Empty list if all versions exist
    """
    base_path = png_path.with_suffix('')

    # Define all required versions with their suffixes
    required_versions = {
        '1x': [f"{base_path}_1x.webp", f"{base_path}_1x.png"],
        '2x': [f"{base_path}_2x.webp", f"{base_path}_2x.png"],
        '3x': [f"{base_path}_3x.webp", f"{base_path}_3x.png"],
        '4x': [f"{base_path}_4x.webp", f"{base_path}_4x.png"],
        'thumb': [f"{base_path}_thumb.webp"]
    }

    # Find which versions are missing
    missing = set([suffix for suffix, file_paths in required_versions.items()
               for file_path in file_paths
               if not Path(file_path).exists()])

    return list(missing)

def matches_book_registry(png_path: Path, books_dir: Path) -> bool:
    """Check if the image matches any pattern in the book registry"""
    relative_path = png_path.relative_to(books_dir)
    folder_name = relative_path.parts[0]
    file_name = png_path.stem  # filename without extension

    for book_id, config in BOOK_REGISTRY.items():
        if config['imageFolder'] == folder_name and file_name.startswith(config['imagePrefix']):
            return True
    return False

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
    skipped_count = 0
    not_in_registry_count = 0

    # Collect all image directories mentioned in the book registry
    image_dirs = [books_dir / config['imageFolder'] for config in BOOK_REGISTRY.values()]

    for image_dir in sorted(set(image_dirs)):
        if not image_dir.exists():
            continue

        print(f"\n📁 {image_dir.name}")

        for png_path in sorted(image_dir.glob("*.png")):
            # Skip files that are already responsive versions (have suffixes like _1x, _2x, etc.)
            if any(png_path.stem.endswith(suffix) for suffix in ['_1x', '_2x', '_3x', '_4x', '_thumb']):
                continue

            # Check if this image matches the book registry
            if not matches_book_registry(png_path, books_dir):
                print(f"  ⊘  {png_path.name} (not in registry)")
                not_in_registry_count += 1
                continue

            # Check which versions are missing
            missing_versions = get_missing_versions(png_path)

            if not missing_versions:
                print(f"  ⏭  {png_path.name} (already optimized)")
                skipped_count += 1
                continue

            try:
                original_size = png_path.stat().st_size
                base_path = png_path.with_suffix('')

                with Image.open(png_path) as img:
                    original_width, original_height = img.size
                    aspect_ratio = original_height / original_width

                    # Show what we're generating
                    versions_str = ', '.join(missing_versions)
                    print(f"  ✓ Processing {png_path.name} ({original_size/1024:.0f}KB, {original_width}x{original_height})")
                    print(f"    Generating: {versions_str}")

                    # Generate only the missing responsive versions
                    for suffix in missing_versions:
                        if suffix == 'thumb':
                            # Thumbnail for LQIP
                            thumb = img.copy()
                            thumb.thumbnail((20, 16), Image.Resampling.LANCZOS)
                            thumb_path = f"{base_path}_thumb.webp"
                            thumb.save(thumb_path, 'WEBP', quality=60)
                        else:
                            # Regular responsive versions
                            target_width = target_widths[suffix]
                            target_height = int(target_width * aspect_ratio)

                            # WebP version
                            webp_path = f"{base_path}_{suffix}.webp"
                            resized = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
                            resized.save(webp_path, 'WEBP', quality=85, method=6)

                            # PNG fallback
                            png_fallback = f"{base_path}_{suffix}.png"
                            resized.save(png_fallback, 'PNG', optimize=True, compress_level=9)

                    # Optimize original PNG if needed
                    # if original_size > 100_000:  # Only if larger than 100KB
                    #     img.save(str(png_path), 'PNG', optimize=True, compress_level=9)

                # Calculate savings (comparing original to 2x WebP - typical mobile use)
                webp_2x_path = Path(f"{base_path}_2x.webp")
                if webp_2x_path.exists():
                    webp_2x_size = webp_2x_path.stat().st_size
                    saved = original_size - webp_2x_size
                    total_saved += saved
                    print(f"    ✓ Generated {len(missing_versions)} version(s)")
                    print(f"    💾 Typical savings: {saved/1024:.0f}KB ({saved*100/original_size:.0f}%)")
                else:
                    print(f"    ✓ Generated {len(missing_versions)} version(s)")

                total_files += 1

            except Exception as e:
                print(f"  ✗ {png_path.name}: {e}")

    print(f"\n{'='*50}")
    print(f"📊 Summary:")
    print(f"  ✅ Processed: {total_files} images")
    print(f"  ⏭  Skipped (already optimized): {skipped_count} images")
    print(f"  ⊘  Skipped (not in registry): {not_in_registry_count} images")
    if total_files > 0:
        print(f"  💾 Average savings per image: {total_saved/total_files/1024:.0f}KB")
        print(f"  💾 Total potential savings: {total_saved/1024/1024:.1f}MB")
    else:
        print(f"  ℹ️  No new images to process")

if __name__ == "__main__":
    books_dir = Path(__file__).parent.parent / "public" / "books"

    if not books_dir.exists():
        print(f"❌ Error: Books directory not found at {books_dir}")
        exit(1)

    optimize_book_images(books_dir)
