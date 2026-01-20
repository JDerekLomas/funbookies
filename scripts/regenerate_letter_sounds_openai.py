#!/usr/bin/env python3
"""
Regenerate specific letter sounds using OpenAI TTS.

Uses the same approach as the original letter sound generation.
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

# Also try playpowerlearn backup
BACKUP_ENV = Path("/Users/dereklomas/playpowerlearn-v1-archive/playpowerlearn-app/.env.local")
if BACKUP_ENV.exists():
    load_dotenv(BACKUP_ENV)

# API Key
OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "").strip().strip('"')
if not OPENAI_KEY:
    print("Error: OPENAI_API_KEY environment variable not set")
    exit(1)

client = OpenAI(api_key=OPENAI_KEY)

# Output directory
OUTPUT_DIR = PROJECT_ROOT / "public" / "activities" / "letter-sounds" / "openai-us" / "sounds"

# Letter sounds - user-selected from variants review
LETTER_SOUNDS = {
    "c": "kah",      # /k/ as in cat
    "e": "ehhh",     # /ɛ/ short e - sustained
    "f": "fuh",      # /f/ as in fan
    "i": "ihhh",     # /ɪ/ short i - sustained
    "l": "lah",      # /l/ as in lamp
    "p": "peh",      # /p/ as in pig - short e ending
    "r": "rah",      # /ɹ/ as in red
    "v": "vah",      # /v/ as in van
    "z": "zah",      # /z/ as in zip
}


def generate_sound(text: str, output_path: Path) -> bool:
    """Generate audio using OpenAI TTS."""
    try:
        response = client.audio.speech.create(
            model="tts-1-hd",
            voice="nova",  # Clear, neutral voice
            input=text,
            speed=0.9,  # Slightly slower for clarity
        )
        response.stream_to_file(str(output_path))
        return True
    except Exception as e:
        print(f"  Error: {e}")
        return False


def main():
    print("=" * 50)
    print("REGENERATING LETTER SOUNDS (OpenAI TTS)")
    print("=" * 50)
    print(f"\nOutput: {OUTPUT_DIR}")
    print(f"Letters: {', '.join(LETTER_SOUNDS.keys())}\n")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    success = 0
    for letter, phoneme in LETTER_SOUNDS.items():
        output_path = OUTPUT_DIR / f"{letter}.mp3"
        print(f"  {letter}: '{phoneme}'", end=" ... ")

        if generate_sound(phoneme, output_path):
            print("OK")
            success += 1
        else:
            print("FAILED")

        sleep(0.3)  # Rate limiting

    print(f"\nDone! {success}/{len(LETTER_SOUNDS)} generated successfully")


if __name__ == "__main__":
    main()
