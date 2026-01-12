#!/usr/bin/env python3
"""Regenerate letter sounds with contextual phrases."""

import requests
from pathlib import Path
from time import sleep

API_KEY = "sk_26621aaaf1ef6e57482788f84453374735a2beb985ddfbec"
VOICE_ID = "Xb7hH8MSUJpSbSDYk0k2"  # Alice

OUTPUT_DIR = Path("/Users/dereklomas/lilbookies/public/activities/letter-sounds")

# Try contextual phrases - extract the sound from natural speech
FIXES = {
    'names': {
        'e': 'E.',              # just the letter with period
        'f': 'F.',              # just the letter
        'h': 'H.',              # just the letter
    },
    'sounds': {
        'a': 'ah',              # like "ah" in "father"
        'e': 'eh',              # short e
        'f': 'f',               # just the consonant
        'i': 'ih',              # short i
        'r': 'rr',              # rolled r
        's': 'ss',              # hissing s
        'v': 'vv',              # buzzing v
    }
}


def generate_audio(text: str, output_path: Path, model: str = "eleven_turbo_v2_5") -> bool:
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"

    headers = {
        "xi-api-key": API_KEY,
        "Content-Type": "application/json"
    }

    data = {
        "text": text,
        "model_id": model,
        "voice_settings": {
            "stability": 0.8,        # higher stability
            "similarity_boost": 0.5,
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
            print(f"  Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"  Error: {e}")
        return False


def main():
    for sound_type, letters in FIXES.items():
        print(f"\nRegenerating {sound_type} (v2)...")
        for letter, text in letters.items():
            output_path = OUTPUT_DIR / sound_type / f"{letter}.mp3"
            print(f"  {letter}: '{text}'", end=" ")
            if generate_audio(text, output_path):
                print("OK")
            else:
                print("FAILED")
            sleep(0.3)

    print("\nDone! Refresh to test.")


if __name__ == "__main__":
    main()
