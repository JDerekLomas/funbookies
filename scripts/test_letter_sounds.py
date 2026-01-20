#!/usr/bin/env python3
"""
Test different voices and spellings for letter sounds.
Generates multiple versions to compare.
"""

import os
from pathlib import Path
from time import sleep
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / ".env.local")
BACKUP_ENV = Path("/Users/dereklomas/playpowerlearn-v1-archive/playpowerlearn-app/.env.local")
if BACKUP_ENV.exists():
    load_dotenv(BACKUP_ENV)

OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "").strip().strip('"')
client = OpenAI(api_key=OPENAI_KEY)

# Output directory for test sounds
OUTPUT_DIR = PROJECT_ROOT / "public" / "activities" / "letter-sounds" / "test"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Voices to try
VOICES = ["nova", "alloy", "echo", "fable", "onyx", "shimmer"]

# Letters that still need work with different spelling attempts
LETTER_VARIANTS = {
    "c": ["kuh", "cuh", "k-uh", "kah"],
    "e": ["eh", "ehhh", "short e", "eh as in bed"],
    "i": ["ih", "ihhh", "short i", "ih as in sit"],
    "p": ["puh", "p-uh", "pah", "peh"],
    "r": ["ruh", "rruh", "r-uh", "er"],
    "v": ["vuh", "v-uh", "vvuh"],
    "z": ["zuh", "z-uh", "zzuh"],
    "f": ["fuh", "f-uh", "ffuh"],  # Keep f for elevenlabs comparison
    "l": ["luh", "l-uh", "lluh", "leh"],
}


def generate_sound(text: str, voice: str, output_path: Path) -> bool:
    """Generate audio using OpenAI TTS."""
    try:
        response = client.audio.speech.create(
            model="tts-1-hd",
            voice=voice,
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
    print("TESTING LETTER SOUND VARIATIONS")
    print("=" * 60)

    # Test one letter with all voices first
    test_letter = "c"
    test_text = "kuh"

    print(f"\n1. Testing voices for '{test_letter}' with text '{test_text}':\n")
    for voice in VOICES:
        output_path = OUTPUT_DIR / f"{test_letter}_{voice}.mp3"
        print(f"   {voice}...", end=" ")
        if generate_sound(test_text, voice, output_path):
            print("OK")
        sleep(0.3)

    # Test spelling variants with best voice candidates
    print(f"\n2. Testing spelling variants (using 'alloy' voice):\n")
    for letter, variants in LETTER_VARIANTS.items():
        print(f"   {letter}:")
        for i, variant in enumerate(variants):
            output_path = OUTPUT_DIR / f"{letter}_v{i+1}_{variant.replace(' ', '_')}.mp3"
            print(f"      '{variant}'...", end=" ")
            if generate_sound(variant, "alloy", output_path):
                print("OK")
            sleep(0.3)

    print(f"\n✓ Test files saved to: {OUTPUT_DIR}")
    print("\nPlay them with:")
    print(f"  open {OUTPUT_DIR}")
    print("  # or")
    print(f"  afplay {OUTPUT_DIR}/c_nova.mp3")


if __name__ == "__main__":
    main()
