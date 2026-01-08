#!/usr/bin/env python3
"""
FunBookies Image Generator using MuleRouter/NanoBanana API

This module provides batch image generation for leveled readers,
with support for character consistency and style locking.
"""

import os
import json
import time
import asyncio
import aiohttp
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

# MuleRouter configuration
MULEROUTER_API_KEY = os.environ.get(
    "MULEROUTER_API_KEY",
    "sk-mr-2dfbbdfe5bbd2e24235960b2d4f5b45bf1b59a087bc2524ff35c6c70a2657436"
)
MULEROUTER_SITE = os.environ.get("MULEROUTER_SITE", "mulerouter")
MULEROUTER_BASE_URL = "https://api.mulerun.ai"

# Default image settings for FunBookies (5:4 aspect for 80% page coverage)
DEFAULT_WIDTH = 1024
DEFAULT_HEIGHT = 820
DEFAULT_MODEL = "wan2.6-t2i"

# Style presets
STYLE_PRESETS = {
    "classic": "Warm soft watercolor style, golden hour lighting, gentle colors",
    "adventure": "Bold gouache illustration, dynamic composition, vibrant colors",
    "nature": "Detailed botanical illustration style, soft greens and earth tones",
    "silly": "Playful cartoon style with exaggerated expressions, bright colors",
    "cozy": "Warm soft watercolor style, cozy atmosphere, soft pastels"
}


@dataclass
class ImageRequest:
    """Single image generation request"""
    prompt: str
    page_id: str
    output_path: str
    width: int = DEFAULT_WIDTH
    height: int = DEFAULT_HEIGHT
    model: str = DEFAULT_MODEL
    style_preset: str = "classic"
    reference_image: Optional[str] = None
    seed: Optional[int] = None


@dataclass
class ImageResult:
    """Result of image generation"""
    page_id: str
    success: bool
    output_path: Optional[str] = None
    error: Optional[str] = None
    generation_time: float = 0.0
    seed_used: Optional[int] = None


@dataclass
class BookImageJob:
    """Complete book image generation job"""
    book_slug: str
    title: str
    character_description: str
    style_preset: str = "classic"
    pages: list = field(default_factory=list)
    reference_image: Optional[str] = None
    output_dir: Optional[str] = None

    def __post_init__(self):
        if self.output_dir is None:
            self.output_dir = f"public/books/{self.book_slug}_images"


class MuleRouterClient:
    """Client for MuleRouter/NanoBanana API"""

    def __init__(self, api_key: str = MULEROUTER_API_KEY):
        self.api_key = api_key
        self.base_url = MULEROUTER_BASE_URL
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def generate_image(self, request: ImageRequest) -> ImageResult:
        """Generate a single image"""
        start_time = time.time()

        # Build the full prompt with style
        style_suffix = STYLE_PRESETS.get(request.style_preset, STYLE_PRESETS["classic"])
        full_prompt = f"{request.prompt}. {style_suffix}"

        payload = {
            "model": request.model,
            "prompt": full_prompt,
            "width": request.width,
            "height": request.height,
        }

        if request.seed:
            payload["seed"] = request.seed

        if request.reference_image:
            payload["image"] = request.reference_image
            payload["strength"] = 0.7  # Balance between reference and prompt

        try:
            async with self.session.post(
                f"{self.base_url}/v1/images/generations",
                json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    return ImageResult(
                        page_id=request.page_id,
                        success=False,
                        error=f"API error {response.status}: {error_text}"
                    )

                data = await response.json()

                # Extract image URL or base64
                if "data" in data and len(data["data"]) > 0:
                    image_data = data["data"][0]
                    image_url = image_data.get("url") or image_data.get("b64_json")
                    seed_used = image_data.get("seed")

                    # Download and save the image
                    if image_url and image_url.startswith("http"):
                        await self._download_image(image_url, request.output_path)
                    elif image_url:
                        # Base64 encoded
                        import base64
                        image_bytes = base64.b64decode(image_url)
                        Path(request.output_path).parent.mkdir(parents=True, exist_ok=True)
                        with open(request.output_path, "wb") as f:
                            f.write(image_bytes)

                    # Create responsive versions
                    await self._create_responsive_versions(request.output_path)

                    return ImageResult(
                        page_id=request.page_id,
                        success=True,
                        output_path=request.output_path,
                        generation_time=time.time() - start_time,
                        seed_used=seed_used
                    )
                else:
                    return ImageResult(
                        page_id=request.page_id,
                        success=False,
                        error="No image data in response"
                    )

        except Exception as e:
            return ImageResult(
                page_id=request.page_id,
                success=False,
                error=str(e),
                generation_time=time.time() - start_time
            )

    async def _download_image(self, url: str, output_path: str):
        """Download image from URL and save to disk"""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        async with self.session.get(url) as response:
            if response.status == 200:
                content = await response.read()
                with open(output_path, "wb") as f:
                    f.write(content)

    async def _create_responsive_versions(self, png_path: str):
        """Create responsive image versions (1x, 2x, 3x, 4x) + thumbnail"""
        from PIL import Image
        from pathlib import Path

        base_path = Path(png_path).with_suffix('')

        # Define responsive widths (prioritize width, calculate height from aspect ratio)
        target_widths = {
            '4x': 800,   # Large tablets, retina
            '3x': 600,   # Standard tablets
            '2x': 400,   # Large phones
            '1x': 256,   # Small phones, slow connections
        }

        try:
            with Image.open(png_path) as img:
                original_size = Path(png_path).stat().st_size
                original_width, original_height = img.size
                aspect_ratio = original_height / original_width
                print(f"  Original: {original_size/1024:.0f}KB ({original_width}x{original_height})")

                # Generate each responsive version
                for suffix, target_width in target_widths.items():
                    # Calculate height maintaining aspect ratio
                    target_height = int(target_width * aspect_ratio)

                    # WebP version (primary)
                    webp_path = f"{base_path}_{suffix}.webp"
                    resized = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
                    resized.save(webp_path, 'WEBP', quality=85, method=6)
                    webp_size = Path(webp_path).stat().st_size

                    # PNG fallback
                    png_fallback = f"{base_path}_{suffix}.png"
                    resized.save(png_fallback, 'PNG', optimize=True, compress_level=9)
                    png_size = Path(png_fallback).stat().st_size

                    print(f"  {suffix}: {target_width}x{target_height} - WebP {webp_size/1024:.0f}KB, PNG {png_size/1024:.0f}KB")

                # Tiny thumbnail for blur placeholder (LQIP)
                thumb = img.copy()
                thumb.thumbnail((20, 16), Image.Resampling.LANCZOS)
                thumb_path = f"{base_path}_thumb.webp"
                thumb.save(thumb_path, 'WEBP', quality=60)
                thumb_size = Path(thumb_path).stat().st_size
                print(f"  Thumbnail: {thumb_size/1024:.1f}KB")

                # Optimize original PNG
                img.save(png_path, 'PNG', optimize=True, compress_level=9)
                optimized_size = Path(png_path).stat().st_size
                print(f"  Original optimized: {optimized_size/1024:.0f}KB")

                # Calculate savings
                smallest_webp = Path(f"{base_path}_2x.webp").stat().st_size
                print(f"  ✅ Total bandwidth savings: {(original_size - smallest_webp)/1024:.0f}KB per load")

        except Exception as e:
            print(f"  ✗ Optimization failed: {e}")

    async def generate_batch(
        self,
        requests: list[ImageRequest],
        concurrency: int = 3,
        delay_between: float = 1.0
    ) -> list[ImageResult]:
        """Generate multiple images with rate limiting"""
        results = []
        semaphore = asyncio.Semaphore(concurrency)

        async def limited_generate(req: ImageRequest) -> ImageResult:
            async with semaphore:
                result = await self.generate_image(req)
                await asyncio.sleep(delay_between)  # Rate limiting
                return result

        tasks = [limited_generate(req) for req in requests]
        results = await asyncio.gather(*tasks)
        return results


class BookImageGenerator:
    """High-level book image generation orchestrator"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.books_dir = self.project_root / "public" / "books"

    def load_book(self, book_slug: str) -> dict:
        """Load book JSON"""
        book_path = self.books_dir / f"{book_slug}.json"
        with open(book_path) as f:
            return json.load(f)

    def save_book(self, book_data: dict):
        """Save book JSON with responsive image references"""
        from pathlib import Path

        # Add responsive image references to each page
        for page in book_data.get("pages", []):
            if "image" in page:
                base_path = str(Path(page["image"]).with_suffix(''))

                # Store all available versions
                page["image_versions"] = {
                    "original": page["image"],
                    "4x": f"{base_path}_4x.webp",
                    "3x": f"{base_path}_3x.webp",
                    "2x": f"{base_path}_2x.webp",
                    "1x": f"{base_path}_1x.webp",
                    "thumb": f"{base_path}_thumb.webp",
                    # PNG fallbacks
                    "4x_png": f"{base_path}_4x.png",
                    "3x_png": f"{base_path}_3x.png",
                    "2x_png": f"{base_path}_2x.png",
                    "1x_png": f"{base_path}_1x.png",
                }

        # Save JSON
        book_path = self.books_dir / f"{book_data['slug']}.json"
        with open(book_path, "w") as f:
            json.dump(book_data, f, indent=2)

    def create_image_requests(
        self,
        book_data: dict,
        style_preset: str = "classic",
        character_desc: str = "",
        regenerate_pages: list[int] = None
    ) -> list[ImageRequest]:
        """Create image requests for all story pages"""
        requests = []
        book_slug = book_data["slug"]
        output_dir = self.books_dir / f"{book_slug}_images"

        for page in book_data["pages"]:
            # Only process pages with image prompts
            if "image_prompt" not in page:
                continue

            page_num = page.get("page", 0)

            # Skip if not in regenerate list (when specified)
            if regenerate_pages and page_num not in regenerate_pages:
                continue

            # Build enhanced prompt with character description
            prompt = page["image_prompt"]
            if character_desc:
                prompt = f"{character_desc}. {prompt}"

            # Determine output filename
            page_type = page.get("type", "story")
            if page_type == "cover":
                filename = f"page_{page_num:02d}_cover.png"
            elif page_type == "back_cover":
                filename = f"page_{page_num:02d}_back_cover.png"
            else:
                # Extract key words from text for filename
                text = page.get("text", "")
                text_slug = "_".join(text.lower().split()[:3]).replace('"', '').replace("'", "")
                filename = f"page_{page_num:02d}_{text_slug}.png"

            requests.append(ImageRequest(
                prompt=prompt,
                page_id=f"page_{page_num}",
                output_path=str(output_dir / filename),
                style_preset=style_preset
            ))

        return requests

    async def generate_book_images(
        self,
        book_slug: str,
        style_preset: str = "classic",
        character_desc: str = "",
        regenerate_pages: list[int] = None,
        concurrency: int = 2
    ) -> dict:
        """Generate all images for a book"""
        book_data = self.load_book(book_slug)

        requests = self.create_image_requests(
            book_data,
            style_preset=style_preset,
            character_desc=character_desc,
            regenerate_pages=regenerate_pages
        )

        print(f"Generating {len(requests)} images for '{book_data['title']}'...")

        async with MuleRouterClient() as client:
            results = await client.generate_batch(
                requests,
                concurrency=concurrency,
                delay_between=2.0  # Be nice to the API
            )

        # Update book JSON with image paths
        for result in results:
            if result.success:
                # Find the matching page and update image path
                page_num = int(result.page_id.split("_")[1])
                for page in book_data["pages"]:
                    if page.get("page") == page_num:
                        # Convert absolute path to relative
                        rel_path = str(Path(result.output_path).relative_to(self.books_dir))
                        page["image"] = rel_path
                        if result.seed_used:
                            page["image_seed"] = result.seed_used
                        break

        # Save updated book
        self.save_book(book_data)

        # Return summary
        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]

        return {
            "book_slug": book_slug,
            "total": len(results),
            "successful": len(successful),
            "failed": len(failed),
            "results": [
                {
                    "page_id": r.page_id,
                    "success": r.success,
                    "path": r.output_path if r.success else None,
                    "error": r.error if not r.success else None,
                    "time": r.generation_time
                }
                for r in results
            ]
        }


# CLI interface
async def main():
    import argparse

    parser = argparse.ArgumentParser(description="Generate images for FunBookies books")
    parser.add_argument("book_slug", help="Book slug (e.g., 'castle')")
    parser.add_argument("--style", default="classic", choices=list(STYLE_PRESETS.keys()))
    parser.add_argument("--character", default="", help="Character description for consistency")
    parser.add_argument("--pages", type=str, help="Comma-separated page numbers to regenerate")
    parser.add_argument("--concurrency", type=int, default=2, help="Concurrent requests")
    parser.add_argument("--project-root", default=".", help="Project root directory")

    args = parser.parse_args()

    regenerate_pages = None
    if args.pages:
        regenerate_pages = [int(p.strip()) for p in args.pages.split(",")]

    generator = BookImageGenerator(args.project_root)

    result = await generator.generate_book_images(
        args.book_slug,
        style_preset=args.style,
        character_desc=args.character,
        regenerate_pages=regenerate_pages,
        concurrency=args.concurrency
    )

    print("\n" + "="*50)
    print(f"Generation complete: {result['successful']}/{result['total']} successful")
    print("="*50)

    for r in result["results"]:
        status = "OK" if r["success"] else "FAILED"
        print(f"  {r['page_id']}: {status} ({r['time']:.1f}s)")
        if r["error"]:
            print(f"    Error: {r['error']}")


if __name__ == "__main__":
    asyncio.run(main())
