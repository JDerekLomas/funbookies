#!/usr/bin/env python3
"""
Generate multiple phonetic spelling variants for problematic letter sounds.
These variants will be shown in the review UI for selection.
"""

import os
import requests
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
ELEVENLABS_KEY = os.environ.get("ELEVENLABS_API_KEY", "").strip().strip('"')

openai_client = OpenAI(api_key=OPENAI_KEY)

# ElevenLabs voices
RACHEL_VOICE = "21m00Tcm4TlvDq8ikWAM"  # American
ALICE_VOICE = "Xb7hH8MSUJpSbSDYk0k2"   # British

# Output directory for variants
VARIANTS_DIR = PROJECT_ROOT / "public" / "activities" / "letter-sounds" / "variants"

# Multiple phonetic spelling variants for each problematic letter
# Format: letter -> list of (variant_id, spelling, description)
LETTER_VARIANTS = {
    "c": [
        ("v1", "kuh", "kuh - schwa ending"),
        ("v2", "kah", "kah - ah ending"),
        ("v3", "k", "k - bare consonant"),
        ("v4", "cuh", "cuh - c spelling"),
        ("v5", "keh", "keh - short e ending"),
    ],
    "e": [
        ("v1", "eh", "eh - standard"),
        ("v2", "ehhh", "ehhh - sustained"),
        ("v3", "ĕ", "ĕ - breve symbol"),
        ("v4", "short e", "short e - description"),
    ],
    "f": [
        ("v1", "ff", "ff - sustained fricative"),
        ("v2", "fuh", "fuh - schwa ending"),
        ("v3", "fah", "fah - ah ending"),
        ("v4", "fff", "fff - longer sustained"),
        ("v5", "feh", "feh - short e ending"),
    ],
    "i": [
        ("v1", "ih", "ih - standard"),
        ("v2", "ihhh", "ihhh - sustained"),
        ("v3", "ĭ", "ĭ - breve symbol"),
        ("v4", "short i", "short i - description"),
    ],
    "l": [
        ("v1", "ll", "ll - sustained"),
        ("v2", "luh", "luh - schwa ending"),
        ("v3", "lah", "lah - ah ending"),
        ("v4", "lll", "lll - longer sustained"),
        ("v5", "leh", "leh - short e ending"),
    ],
    "p": [
        ("v1", "puh", "puh - schwa ending"),
        ("v2", "pah", "pah - ah ending"),
        ("v3", "p", "p - bare consonant"),
        ("v4", "peh", "peh - short e ending"),
    ],
    "r": [
        ("v1", "rr", "rr - sustained"),
        ("v2", "ruh", "ruh - schwa ending"),
        ("v3", "rah", "rah - ah ending"),
        ("v4", "rrr", "rrr - longer sustained"),
        ("v5", "er", "er - schwa-r"),
    ],
    "v": [
        ("v1", "vv", "vv - sustained fricative"),
        ("v2", "vuh", "vuh - schwa ending"),
        ("v3", "vah", "vah - ah ending"),
        ("v4", "vvv", "vvv - longer sustained"),
    ],
    "z": [
        ("v1", "zz", "zz - sustained"),
        ("v2", "zuh", "zuh - schwa ending"),
        ("v3", "zah", "zah - ah ending"),
        ("v4", "zzz", "zzz - longer sustained"),
    ],
}


def generate_openai(text: str, output_path: Path, voice: str = "nova") -> bool:
    """Generate audio using OpenAI TTS."""
    try:
        response = openai_client.audio.speech.create(
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


def generate_elevenlabs(text: str, output_path: Path, voice_id: str = ALICE_VOICE) -> bool:
    """Generate audio using ElevenLabs TTS."""
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {"xi-api-key": ELEVENLABS_KEY, "Content-Type": "application/json"}
    data = {
        "text": text,
        "model_id": "eleven_turbo_v2_5",
        "voice_settings": {"stability": 0.75, "similarity_boost": 0.75}
    }
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            return True
        print(f"Error {response.status_code}: {response.text[:50]}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    print("=" * 60)
    print("GENERATING LETTER SOUND VARIANTS")
    print("=" * 60)

    # Create output directories
    openai_dir = VARIANTS_DIR / "openai-us"
    elevenlabs_dir = VARIANTS_DIR / "elevenlabs-uk"
    openai_dir.mkdir(parents=True, exist_ok=True)
    elevenlabs_dir.mkdir(parents=True, exist_ok=True)

    total = 0
    success = 0

    for letter, variants in LETTER_VARIANTS.items():
        print(f"\n{letter.upper()}:")

        for variant_id, spelling, description in variants:
            # OpenAI variant
            openai_path = openai_dir / f"{letter}_{variant_id}.mp3"
            print(f"  OpenAI '{spelling}'...", end=" ")
            if generate_openai(spelling, openai_path):
                print("OK")
                success += 1
            else:
                print("FAILED")
            total += 1
            sleep(0.2)

            # ElevenLabs variant
            eleven_path = elevenlabs_dir / f"{letter}_{variant_id}.mp3"
            print(f"  ElevenLabs '{spelling}'...", end=" ")
            if generate_elevenlabs(spelling, eleven_path):
                print("OK")
                success += 1
            else:
                print("FAILED")
            total += 1
            sleep(0.2)

    # Save variant metadata for the review UI
    import json
    metadata = {
        "letters": {
            letter: [
                {"id": v[0], "spelling": v[1], "description": v[2]}
                for v in variants
            ]
            for letter, variants in LETTER_VARIANTS.items()
        }
    }
    metadata_path = VARIANTS_DIR / "variants.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"\n{'=' * 60}")
    print(f"Done! {success}/{total} generated")
    print(f"Metadata saved to: {metadata_path}")
    print(f"\nVariants saved to:")
    print(f"  {openai_dir}")
    print(f"  {elevenlabs_dir}")


if __name__ == "__main__":
    main()
