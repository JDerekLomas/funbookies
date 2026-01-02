#!/usr/bin/env python3
"""Generate book images using Wan2.6 T2I via MuleRouter.

Usage:
    python src/generate_book_images.py volcano    # Regenerate volcano book
    python src/generate_book_images.py <book.json> # Generate from any book JSON
"""

import json
import os
import sys
import subprocess
from pathlib import Path

# Paths
SKILL_DIR = Path("/Users/dereklomas/mulerouter-skills-dev/skills/mulerouter-skills")
OUTPUT_DIR = Path("web/books/images")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Character definition - CONSISTENT across all images
GUS_CHARACTER = """A small bright lime-green gecko named Gus with:
- Big round friendly eyes with white sparkle highlights
- Yellow-green belly
- Curled striped tail with darker green stripes
- Four stubby legs with tiny toe pads
- Cute cartoonish style, expressive face
- Standing upright on two legs"""

STYLE = """children's book illustration, simple flat cartoon style, bold black outlines,
bright saturated colors, clean digital art, solid color background, no text,
single character focus, child-friendly"""

# Scene prompts for volcano book
VOLCANO_SCENES = {
    "volcano_page01.png": "Gus standing heroically in front of a large volcano, title scene, dramatic sky",
    "volcano_page03.png": "Gus running happily up a grassy green hill, sunny day, blue sky",
    "volcano_page04.png": "Gus looking surprised at a big dark hole in the ground, curious expression",
    "volcano_page06.png": "Gus standing at the edge of a volcanic crater, looking down with wonder, steam rising",
    "volcano_page08.png": "Gus looking amazed at bright red glowing lava inside the crater, warm orange glow",
    "volcano_page09.png": "Gus with big excited eyes saying wow, speech expression, amazed face",
    "volcano_page10.png": "Gus watching red magma bubbling and rising up from below, dramatic lighting",
    "volcano_page11.png": "Gus startled by explosion, rocks popping, steam hissing, action scene",
    "volcano_page12.png": "Gus turning to run away, looking back at volcano, worried expression",
    "volcano_page13.png": "Gus running fast down the hill, legs moving, determined expression",
    "volcano_page14.png": "Gus running while lava drips behind him, dramatic escape scene",
    "volcano_page15.png": "Gus feeling the heat, sweating, running faster, urgent expression",
    "volcano_page17.png": "Gus standing safely at bottom of hill, relieved expression, volcano in background",
    "volcano_page20.png": "Gus standing proudly, pointing back at the volcano, telling his story",
    "volcano_page21.png": "Gus standing tall and proud, brave pose, confident smile",
    "volcano_page22.png": "Gus walking happily toward a cozy home, sunset sky, peaceful ending",
    "volcano_page23.png": "Gus waving goodbye, happy smile, THE END scene, warm feeling",
}


def generate_image(prompt: str, output_name: str) -> bool:
    """Generate a single image using Wan2.6 T2I."""
    full_prompt = f"{GUS_CHARACTER}, {prompt}, {STYLE}"
    output_path = OUTPUT_DIR / output_name

    print(f"\n{'='*60}")
    print(f"Generating: {output_name}")
    print(f"Scene: {prompt[:60]}...")
    print(f"{'='*60}")

    # Run the skill
    env = os.environ.copy()
    env["MULEROUTER_SITE"] = "mulerouter"
    env["MULEROUTER_API_KEY"] = os.environ.get(
        "MULEROUTER_API_KEY",
        "sk-mr-2dfbbdfe5bbd2e24235960b2d4f5b45bf1b59a087bc2524ff35c6c70a2657436"
    )

    cmd = [
        "uv", "run", "python",
        "models/alibaba/wan2.6-t2i/generation.py",
        "--prompt", full_prompt,
        "--n", "1",
        "--size", "1536*1024"  # 3:2 landscape for print (300 DPI at 106x68mm)
    ]

    try:
        result = subprocess.run(
            cmd,
            cwd=SKILL_DIR,
            env=env,
            capture_output=True,
            text=True,
            timeout=120
        )

        # Parse output for image URL
        output = result.stdout + result.stderr
        for line in output.split("\n"):
            if "result_00.png" in line or "mule-router-assets" in line:
                # Extract URL
                parts = line.split()
                for part in parts:
                    if part.startswith("http"):
                        url = part
                        # Download image
                        import requests
                        resp = requests.get(url, timeout=60)
                        with open(output_path, "wb") as f:
                            f.write(resp.content)
                        print(f"✓ Saved: {output_path}")
                        return True

        print(f"✗ No image URL found in output")
        print(output[-500:] if len(output) > 500 else output)
        return False

    except subprocess.TimeoutExpired:
        print(f"✗ Timeout")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def generate_volcano_book():
    """Regenerate all volcano book images."""
    print("="*60)
    print("REGENERATING VOLCANO BOOK IMAGES")
    print(f"Character: Gus the Gecko")
    print(f"Pages: {len(VOLCANO_SCENES)}")
    print("="*60)

    results = []
    for filename, scene in VOLCANO_SCENES.items():
        success = generate_image(scene, filename)
        results.append((filename, success))

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    success_count = sum(1 for _, s in results if s)
    print(f"Generated: {success_count}/{len(results)}")
    for filename, success in results:
        status = "✓" if success else "✗"
        print(f"  {status} {filename}")


def generate_from_json(json_path: str):
    """Generate images from a book JSON file."""
    with open(json_path) as f:
        book = json.load(f)

    print("="*60)
    print(f"GENERATING: {book.get('title', 'Unknown')}")
    print("="*60)

    results = []
    for page in book.get("pages", []):
        if page.get("image"):
            text = page.get("text", "")
            image_name = page["image"]

            # Generate scene prompt from text
            scene = f"Scene showing: {text}"
            if page.get("type") == "cover":
                scene = f"Cover illustration, title scene, {text}"
            elif page.get("type") == "end":
                scene = "Happy ending scene, THE END, warm peaceful feeling"

            success = generate_image(scene, image_name)
            results.append((image_name, success))

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    success_count = sum(1 for _, s in results if s)
    print(f"Generated: {success_count}/{len(results)}")


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python src/generate_book_images.py volcano")
        print("  python src/generate_book_images.py <book.json>")
        sys.exit(1)

    arg = sys.argv[1]

    if arg == "volcano":
        generate_volcano_book()
    elif arg.endswith(".json"):
        generate_from_json(arg)
    else:
        print(f"Unknown argument: {arg}")
        sys.exit(1)


if __name__ == "__main__":
    main()
