#!/usr/bin/env python3
"""Generate all letter sounds for both US and UK locales."""

import os
import requests
from pathlib import Path
from time import sleep

from dotenv import load_dotenv

# Load environment variables
PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / ".env")
load_dotenv(PROJECT_ROOT / ".env.local")

# API Keys - set via environment variables
OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "")
ELEVENLABS_KEY = os.environ.get("ELEVENLABS_API_KEY", "")

# ElevenLabs voices
ALICE_VOICE = "Xb7hH8MSUJpSbSDYk0k2"  # British educator

# Use project-relative path
OUTPUT_BASE = PROJECT_ROOT / "public/activities/letter-sounds"

# Letter names - US vs UK differences
LETTER_NAMES_US = {
    'a': 'A', 'b': 'B', 'c': 'C', 'd': 'D', 'e': 'E', 'f': 'F', 'g': 'G',
    'h': 'H', 'i': 'I', 'j': 'J', 'k': 'K', 'l': 'L', 'm': 'M', 'n': 'N',
    'o': 'O', 'p': 'P', 'q': 'Q', 'r': 'R', 's': 'S', 't': 'T', 'u': 'U',
    'v': 'V', 'w': 'W', 'x': 'X', 'y': 'Y', 'z': 'Z'  # "zee"
}

LETTER_NAMES_UK = {
    'a': 'A', 'b': 'B', 'c': 'C', 'd': 'D', 'e': 'E', 'f': 'F', 'g': 'G',
    'h': 'H', 'i': 'I', 'j': 'J', 'k': 'K', 'l': 'L', 'm': 'M', 'n': 'N',
    'o': 'O', 'p': 'P', 'q': 'Q', 'r': 'R', 's': 'S', 't': 'T', 'u': 'U',
    'v': 'V', 'w': 'W', 'x': 'X', 'y': 'Y', 'z': 'zed'  # "zed" for UK
}

# Letter sounds (phonics) - same for both locales
LETTER_SOUNDS = {
    'a': 'ah',
    'b': 'buh',
    'c': 'kuh',
    'd': 'duh',
    'e': 'eh',
    'f': 'ff',
    'g': 'guh',
    'h': 'huh',
    'i': 'ih',
    'j': 'juh',
    'k': 'kuh',
    'l': 'll',
    'm': 'mm',
    'n': 'nn',
    'o': 'oh',
    'p': 'puh',
    'q': 'kwuh',
    'r': 'rr',
    's': 'ss',
    't': 'tuh',
    'u': 'uh',
    'v': 'vv',
    'w': 'wuh',
    'x': 'ks',
    'y': 'yuh',
    'z': 'zz'
}


def generate_openai(text: str, output_path: Path, voice: str = "nova") -> bool:
    """Generate audio using OpenAI TTS."""
    url = "https://api.openai.com/v1/audio/speech"
    headers = {"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"}
    data = {
        "model": "tts-1-hd",
        "input": text,
        "voice": voice,
        "response_format": "mp3",
        "speed": 0.9
    }
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            return True
        print(f" Error: {response.status_code}")
        return False
    except Exception as e:
        print(f" Error: {e}")
        return False


def generate_elevenlabs(text: str, output_path: Path, voice_id: str = ALICE_VOICE) -> bool:
    """Generate audio using ElevenLabs TTS."""
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {"xi-api-key": ELEVENLABS_KEY, "Content-Type": "application/json"}
    data = {
        "text": text,
        "model_id": "eleven_turbo_v2_5",
        "voice_settings": {"stability": 0.7, "similarity_boost": 0.5}
    }
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            return True
        print(f" Error: {response.status_code}")
        return False
    except Exception as e:
        print(f" Error: {e}")
        return False


def generate_set(name: str, letters: dict, output_dir: Path, generator_func, delay: float = 0.25):
    """Generate a complete set of letter sounds."""
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n{name} -> {output_dir}")

    for letter, text in letters.items():
        output_path = output_dir / f"{letter}.mp3"
        print(f"  {letter}: '{text}'", end=" ")
        if generator_func(text, output_path):
            print("OK")
        else:
            print("FAILED")
        sleep(delay)


def main():
    # OpenAI Nova (American)
    print("=" * 50)
    print("OPENAI NOVA (American)")
    print("=" * 50)

    generate_set(
        "US Letter Names",
        LETTER_NAMES_US,
        OUTPUT_BASE / "openai-us" / "names",
        generate_openai
    )

    generate_set(
        "US Letter Sounds",
        LETTER_SOUNDS,
        OUTPUT_BASE / "openai-us" / "sounds",
        generate_openai
    )

    # ElevenLabs Alice (British)
    print("\n" + "=" * 50)
    print("ELEVENLABS ALICE (British)")
    print("=" * 50)

    generate_set(
        "UK Letter Names",
        LETTER_NAMES_UK,
        OUTPUT_BASE / "elevenlabs-uk" / "names",
        generate_elevenlabs
    )

    generate_set(
        "UK Letter Sounds",
        LETTER_SOUNDS,
        OUTPUT_BASE / "elevenlabs-uk" / "sounds",
        generate_elevenlabs
    )

    print("\n\nDone! Generated 4 sets:")
    print("  - openai-us/names")
    print("  - openai-us/sounds")
    print("  - elevenlabs-uk/names")
    print("  - elevenlabs-uk/sounds")


if __name__ == "__main__":
    main()
