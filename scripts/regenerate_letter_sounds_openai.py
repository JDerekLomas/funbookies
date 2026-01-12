#!/usr/bin/env python3
"""Regenerate letter sounds with OpenAI TTS."""

import requests
from pathlib import Path
from time import sleep

API_KEY = "OPENAI_API_KEY_PLACEHOLDER"

OUTPUT_DIR = Path("/Users/dereklomas/lilbookies/public/activities/letter-sounds")

# Rejected letters that need fixing
FIXES = {
    'names': {
        'a': 'A',
        'e': 'E',
        'f': 'F',
        'h': 'H',
        'u': 'U',
    },
    'sounds': {
        'a': 'ah',
        'e': 'eh',
        'f': 'ff',
        'i': 'ih',
        'r': 'rr',
        's': 'ss',
    }
}


def generate_audio(text: str, output_path: Path, voice: str = "nova") -> bool:
    """Generate audio using OpenAI TTS."""
    url = "https://api.openai.com/v1/audio/speech"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "tts-1-hd",  # Higher quality
        "input": text,
        "voice": voice,       # nova is clear and friendly
        "response_format": "mp3",
        "speed": 0.9          # Slightly slower for clarity
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            return True
        else:
            print(f"  Error: {response.status_code} - {response.text[:100]}")
            return False
    except Exception as e:
        print(f"  Error: {e}")
        return False


def main():
    for sound_type, letters in FIXES.items():
        print(f"\nRegenerating {sound_type} with OpenAI...")
        for letter, text in letters.items():
            output_path = OUTPUT_DIR / sound_type / f"{letter}.mp3"
            print(f"  {letter}: '{text}'", end=" ")
            if generate_audio(text, output_path):
                print("OK")
            else:
                print("FAILED")
            sleep(0.2)

    print("\nDone! Refresh to test.")


if __name__ == "__main__":
    main()
