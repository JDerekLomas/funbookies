#!/usr/bin/env python3
"""Regenerate specific letter sounds with cleaner phonetics."""

import requests
from pathlib import Path
from time import sleep

OPENAI_KEY = "OPENAI_API_KEY_PLACEHOLDER"
ELEVENLABS_KEY = "sk_26621aaaf1ef6e57482788f84453374735a2beb985ddfbec"
ALICE_VOICE = "Xb7hH8MSUJpSbSDYk0k2"

OUTPUT_BASE = Path("/Users/dereklomas/lilbookies/public/activities/letter-sounds")

# Improved phonetics for consonant sounds
# Try to make them sound like short, clipped phonemes
SOUND_FIXES = {
    'c': 'cuh',      # hard c
    'f': 'fuh',      # f with slight vowel
    'i': 'ih',       # short i
    'k': 'cuh',      # same as c
    'm': 'muh',      # m with slight vowel
    'n': 'nuh',      # n with slight vowel
    'p': 'puh',      # p with slight vowel
    'r': 'ruh',      # r with vowel
    't': 'tuh',      # t with slight vowel
    'v': 'vuh',      # v with vowel
    'x': 'eks',      # x sound
}


def generate_openai(text: str, output_path: Path) -> bool:
    url = "https://api.openai.com/v1/audio/speech"
    headers = {"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"}
    data = {
        "model": "tts-1-hd",
        "input": text,
        "voice": "nova",
        "response_format": "mp3",
        "speed": 0.85  # Slower for clarity
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


def generate_elevenlabs(text: str, output_path: Path) -> bool:
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ALICE_VOICE}"
    headers = {"xi-api-key": ELEVENLABS_KEY, "Content-Type": "application/json"}
    data = {
        "text": text,
        "model_id": "eleven_turbo_v2_5",
        "voice_settings": {"stability": 0.8, "similarity_boost": 0.5}
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


def main():
    print("Regenerating letter sounds with 'uh' endings...\n")

    # OpenAI US
    print("OpenAI US sounds:")
    for letter, text in SOUND_FIXES.items():
        output_path = OUTPUT_BASE / "openai-us" / "sounds" / f"{letter}.mp3"
        print(f"  {letter}: '{text}'", end=" ")
        if generate_openai(text, output_path):
            print("OK")
        else:
            print("FAILED")
        sleep(0.2)

    # ElevenLabs UK
    print("\nElevenLabs UK sounds:")
    for letter, text in SOUND_FIXES.items():
        output_path = OUTPUT_BASE / "elevenlabs-uk" / "sounds" / f"{letter}.mp3"
        print(f"  {letter}: '{text}'", end=" ")
        if generate_elevenlabs(text, output_path):
            print("OK")
        else:
            print("FAILED")
        sleep(0.2)

    print("\nDone! Refresh to test.")


if __name__ == "__main__":
    main()
