#!/usr/bin/env python3
"""Generate images for Zee and the Jungle book using Wan2.6 T2I via MuleRouter."""

import os
import subprocess
from pathlib import Path

# Paths
SKILL_DIR = Path("/Users/dereklomas/mulerouter-skills-dev/skills/mulerouter-skills")
OUTPUT_DIR = Path("web/books/images")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Character definition - CONSISTENT across all images
ZEE_CHARACTER = """A small cute gray sloth named Zee with:
- Round fluffy gray fur
- Big gentle dark eyes with a warm expression
- Long fuzzy arms with curved claws
- Small black nose and gentle smile
- Relaxed, happy demeanor
- Cute cartoonish style, expressive face"""

STYLE = """children's book illustration, simple flat cartoon style, bold black outlines,
bright saturated colors, clean digital art, lush jungle background, no text,
single character focus, child-friendly"""

# Scene prompts for jungle book
JUNGLE_SCENES = {
    "jungle_page01.png": "Zee the sloth hanging from a vine in a colorful jungle, title scene, tropical trees and flowers",
    "jungle_page03.png": "Zee the sloth waking up slowly on a tree branch, sleepy eyes, morning sunshine filtering through leaves",
    "jungle_page04.png": "Zee looking up at the bright sun through jungle canopy, warm golden light",
    "jungle_page05.png": "Zee hanging happily from a branch, excited expression, saying it's a fun day",
    "jungle_page06.png": "Zee hanging from a green vine, holding on with long arms, jungle background",
    "jungle_page07.png": "Zee swinging gently on vine, relaxed hang position, peaceful jungle scene",
    "jungle_page08.png": "Zee swinging through the air on a vine, motion and excitement, trees rushing past",
    "jungle_page09.png": "Zee looking at a colorful tropical bird perched nearby, curious expression",
    "jungle_page10.png": "Colorful tropical bird saying hi to Zee, friendly interaction, bright feathers",
    "jungle_page11.png": "Zee and the bird together, Zee looking happy about new friend, warm scene",
    "jungle_page12.png": "Zee moving through trees with bird friend flying alongside, adventure scene",
    "jungle_page13.png": "Zee climbing up a tall tree with bird friend, looking up excitedly",
    "jungle_page14.png": "Zee sliding down a vine with bird flying nearby, fun movement",
    "jungle_page15.png": "Zee looking at beautiful colorful jungle flowers, wonder and amazement",
    "jungle_page16.png": "Zee and the bird sitting together on a branch, resting, peaceful sunset",
    "jungle_page17.png": "Zee looking very happy, best day ever expression, warm golden light",
    "jungle_page18.png": "Zee waving goodbye happily, THE END scene, cozy jungle sunset",
}


def generate_image(prompt: str, output_name: str) -> bool:
    """Generate a single image using Wan2.6 T2I."""
    full_prompt = f"{ZEE_CHARACTER}, {prompt}, {STYLE}"
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
                        print(f"OK Saved: {output_path}")
                        return True

        print(f"X No image URL found in output")
        print(output[-500:] if len(output) > 500 else output)
        return False

    except subprocess.TimeoutExpired:
        print(f"X Timeout")
        return False
    except Exception as e:
        print(f"X Error: {e}")
        return False


def main():
    """Generate all jungle book images."""
    print("="*60)
    print("GENERATING ZEE AND THE JUNGLE IMAGES")
    print(f"Character: Zee the Sloth")
    print(f"Pages: {len(JUNGLE_SCENES)}")
    print("="*60)

    results = []
    for filename, scene in JUNGLE_SCENES.items():
        success = generate_image(scene, filename)
        results.append((filename, success))

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    success_count = sum(1 for _, s in results if s)
    print(f"Generated: {success_count}/{len(results)}")
    for filename, success in results:
        status = "OK" if success else "X"
        print(f"  {status} {filename}")


if __name__ == "__main__":
    main()
