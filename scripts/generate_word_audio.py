#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["openai", "python-dotenv"]
# ///
"""
Generate word audio files for activities.
Uses OpenAI TTS to create pronunciations for all word icons.
"""

import os
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
WORD_ICONS_DIR = PROJECT_ROOT / "public" / "activities" / "word-icons"
AUDIO_OUTPUT_DIR = PROJECT_ROOT / "public" / "audio" / "words"


def generate_word_audio(word: str, output_path: Path) -> bool:
    """Generate audio using OpenAI TTS."""
    try:
        response = openai_client.audio.speech.create(
            model="tts-1-hd",
            voice="nova",
            input=word,
            speed=0.9,
        )
        response.stream_to_file(str(output_path))
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    print("=" * 60)
    print("GENERATING WORD AUDIO FILES")
    print("=" * 60)

    # Create output directory
    AUDIO_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Get all word icons
    words = sorted([f.stem for f in WORD_ICONS_DIR.glob("*.png")])
    print(f"Found {len(words)} words with icons\n")

    success = 0
    skipped = 0

    for i, word in enumerate(words, 1):
        output_path = AUDIO_OUTPUT_DIR / f"{word}.mp3"

        if output_path.exists():
            print(f"[{i}/{len(words)}] {word}: SKIP (exists)")
            skipped += 1
            continue

        print(f"[{i}/{len(words)}] {word}...", end=" ", flush=True)

        if generate_word_audio(word, output_path):
            print("OK")
            success += 1
        else:
            print("FAILED")

        sleep(0.15)  # Rate limit

    print(f"\n{'=' * 60}")
    print(f"Done! {success} generated, {skipped} skipped")
    print(f"Output: {AUDIO_OUTPUT_DIR}")


if __name__ == "__main__":
    main()
