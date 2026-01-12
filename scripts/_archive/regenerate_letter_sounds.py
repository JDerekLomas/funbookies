#!/usr/bin/env python3
"""Regenerate specific letter sounds with improved phonetics."""

import requests
from pathlib import Path
from time import sleep

API_KEY = "sk_26621aaaf1ef6e57482788f84453374735a2beb985ddfbec"
VOICE_ID = "Xb7hH8MSUJpSbSDYk0k2"  # Alice - British educator

OUTPUT_DIR = Path("/Users/dereklomas/lilbookies/public/activities/letter-sounds")

# Improved phonetics for rejected letters
FIXES = {
    # Letter names - say it more clearly
    'names': {
        'e': 'eee',           # stretch it out
        'f': 'eff',           # clear F sound
        'h': 'aitch',         # British H
        'i': 'eye',           # like the word "eye"
        'o': 'oh',            # like saying "oh!"
        's': 'ess',           # clear S name
        'u': 'you',           # like the word "you"
        'w': 'double you',    # full name
        'y': 'why',           # like the word "why"
        'z': 'zed',           # British Z
    },
    # Letter sounds - pure phonics
    'sounds': {
        'a': 'aaa',           # short a, stretch it
        'e': 'ehhh',          # short e as in "bed"
        'f': 'ffff',          # pure f sound
        'i': 'ihhh',          # short i as in "sit"
        'n': 'nnnn',          # pure n sound
        'r': 'errr',          # r sound
        's': 'ssss',          # pure s sound
        'v': 'vvvv',          # pure v sound
        'x': 'ks',            # x sound
    }
}


def generate_audio(text: str, output_path: Path) -> bool:
    """Generate audio using ElevenLabs TTS."""
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"

    headers = {
        "xi-api-key": API_KEY,
        "Content-Type": "application/json"
    }

    data = {
        "text": text,
        "model_id": "eleven_turbo_v2_5",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.0,
            "use_speaker_boost": True
        }
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            return True
        else:
            print(f"  Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"  Error: {e}")
        return False


def main():
    for sound_type, letters in FIXES.items():
        print(f"\nRegenerating {sound_type}...")
        for letter, text in letters.items():
            output_path = OUTPUT_DIR / sound_type / f"{letter}.mp3"
            print(f"  {letter}: '{text}'", end=" ")
            if generate_audio(text, output_path):
                print("OK")
            else:
                print("FAILED")
            sleep(0.3)

    print("\nDone! Refresh the review page to test.")


if __name__ == "__main__":
    main()
