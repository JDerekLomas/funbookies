#!/usr/bin/env python3
"""
Regenerate ElevenLabs letter sounds and names using IPA phoneme tags.
Uses eleven_turbo_v2 model for phoneme tag support.
"""

import os
import requests
from pathlib import Path
from time import sleep
from dotenv import load_dotenv

# Load environment variables
PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / ".env.local")

# API Key
ELEVENLABS_KEY = os.environ.get("ELEVENLABS_API_KEY", "").strip().strip('"')
if not ELEVENLABS_KEY:
    print("Error: ELEVENLABS_API_KEY not set")
    exit(1)

# Voice - Rachel (American, clear, educational)
VOICE_ID = "21m00Tcm4TlvDq8ikWAM"

# Output directories
SOUNDS_DIR = PROJECT_ROOT / "public" / "activities" / "letter-sounds" / "elevenlabs-uk" / "sounds"
NAMES_DIR = PROJECT_ROOT / "public" / "activities" / "letter-sounds" / "elevenlabs-uk" / "names"

# Letter SOUNDS that need regeneration (using IPA phoneme tags)
# Format: letter -> SSML with phoneme tag
LETTER_SOUNDS_IPA = {
    "c": '<phoneme alphabet="ipa" ph="kə">kuh</phoneme>',   # /k/ + schwa
    "e": '<phoneme alphabet="ipa" ph="ɛ">eh</phoneme>',     # short e
    "f": '<phoneme alphabet="ipa" ph="fə">fuh</phoneme>',   # /f/ + schwa
    "i": '<phoneme alphabet="ipa" ph="ɪ">ih</phoneme>',     # short i
    "k": '<phoneme alphabet="ipa" ph="kə">kuh</phoneme>',   # /k/ + schwa
    "l": '<phoneme alphabet="ipa" ph="lə">luh</phoneme>',   # /l/ + schwa
    "p": '<phoneme alphabet="ipa" ph="pə">puh</phoneme>',   # /p/ + schwa
    "r": '<phoneme alphabet="ipa" ph="ɹə">ruh</phoneme>',   # /r/ + schwa
    "s": '<phoneme alphabet="ipa" ph="sə">suh</phoneme>',   # /s/ + schwa
    "w": '<phoneme alphabet="ipa" ph="wə">wuh</phoneme>',   # /w/ + schwa
    "z": '<phoneme alphabet="ipa" ph="zə">zuh</phoneme>',   # /z/ + schwa
}

# Letter NAMES that need regeneration
# These are just the letter names spoken clearly
LETTER_NAMES = {
    "a": "ay",
    "f": "eff",
    "g": "jee",
    "h": "aitch",
    "i": "eye",
    "s": "ess",
    "t": "tee",
    "w": "double you",
    "y": "why",
}


def generate_elevenlabs(text: str, output_path: Path) -> bool:
    """Generate audio using ElevenLabs TTS."""
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {
        "xi-api-key": ELEVENLABS_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "text": text,
        "model_id": "eleven_turbo_v2",  # Required for phoneme tags
        "voice_settings": {
            "stability": 0.75,
            "similarity_boost": 0.75
        }
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            return True
        else:
            print(f"Error {response.status_code}: {response.text[:100]}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    print("=" * 60)
    print("REGENERATING ELEVENLABS LETTER SOUNDS & NAMES")
    print("=" * 60)

    SOUNDS_DIR.mkdir(parents=True, exist_ok=True)
    NAMES_DIR.mkdir(parents=True, exist_ok=True)

    # Regenerate sounds
    print(f"\n1. SOUNDS ({len(LETTER_SOUNDS_IPA)} letters):")
    print(f"   Output: {SOUNDS_DIR}\n")

    success_sounds = 0
    for letter, ssml in LETTER_SOUNDS_IPA.items():
        output_path = SOUNDS_DIR / f"{letter}.mp3"
        print(f"   {letter}: {ssml[:40]}...", end=" ")

        if generate_elevenlabs(ssml, output_path):
            print("OK")
            success_sounds += 1
        else:
            print("FAILED")

        sleep(0.3)

    # Regenerate names
    print(f"\n2. NAMES ({len(LETTER_NAMES)} letters):")
    print(f"   Output: {NAMES_DIR}\n")

    success_names = 0
    for letter, name in LETTER_NAMES.items():
        output_path = NAMES_DIR / f"{letter}.mp3"
        print(f"   {letter}: '{name}'...", end=" ")

        if generate_elevenlabs(name, output_path):
            print("OK")
            success_names += 1
        else:
            print("FAILED")

        sleep(0.3)

    print(f"\n{'=' * 60}")
    print(f"Done! Sounds: {success_sounds}/{len(LETTER_SOUNDS_IPA)}, Names: {success_names}/{len(LETTER_NAMES)}")


if __name__ == "__main__":
    main()
