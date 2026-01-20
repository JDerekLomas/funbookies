#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["openai", "python-dotenv"]
# ///
"""
Generate letter sound variants for A/B testing experiment.
Creates audio files using OpenAI TTS.
"""

import os
import json
from pathlib import Path
from time import sleep
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / ".env.local")
load_dotenv(PROJECT_ROOT / ".env")

OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "").strip().strip('"')
openai_client = OpenAI(api_key=OPENAI_KEY)

# Directories
VARIANTS_DIR = PROJECT_ROOT / "public" / "activities" / "letter-sounds" / "variants"
OUTPUT_DIR = VARIANTS_DIR / "openai-us"


def generate_audio(text: str, output_path: Path) -> bool:
    """Generate audio using OpenAI TTS."""
    try:
        response = openai_client.audio.speech.create(
            model="tts-1-hd",
            voice="nova",
            input=text,
            speed=0.85,
        )
        response.stream_to_file(str(output_path))
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    print("=" * 60)
    print("GENERATING LETTER SOUND VARIANTS")
    print("=" * 60)

    # Load variants
    variants_path = VARIANTS_DIR / "variants-full.json"
    with open(variants_path) as f:
        data = json.load(f)

    letters = data["letters"]

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    total = 0
    success = 0
    skipped = 0

    for letter, variants in letters.items():
        print(f"\n[{letter.upper()}]")
        for variant in variants:
            vid = variant["id"]
            spelling = variant["spelling"]

            output_path = OUTPUT_DIR / f"{letter}_{vid}.mp3"

            if output_path.exists():
                print(f"  {vid} '{spelling}': SKIP (exists)")
                skipped += 1
                total += 1
                continue

            print(f"  {vid} '{spelling}'...", end=" ", flush=True)

            if generate_audio(spelling, output_path):
                print("OK")
                success += 1
            else:
                print("FAILED")

            total += 1
            sleep(0.15)  # Rate limit

    print(f"\n{'=' * 60}")
    print(f"Done! {success} generated, {skipped} skipped, {total} total")
    print(f"Output: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
