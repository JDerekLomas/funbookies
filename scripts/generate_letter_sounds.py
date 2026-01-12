#!/usr/bin/env python3
"""Generate letter sound audio files using ElevenLabs TTS."""

import os
import requests
from pathlib import Path
from time import sleep

API_KEY = "sk_26621aaaf1ef6e57482788f84453374735a2beb985ddfbec"
VOICE_ID = "Xb7hH8MSUJpSbSDYk0k2"  # Alice - Clear, Engaging Educator (British)

OUTPUT_DIR = Path("/Users/dereklomas/lilbookies/public/activities/letter-sounds")

# Letter names - how we say the letter name
LETTER_NAMES = {
    'a': 'A', 'b': 'B', 'c': 'C', 'd': 'D', 'e': 'E', 'f': 'F', 'g': 'G',
    'h': 'H', 'i': 'I', 'j': 'J', 'k': 'K', 'l': 'L', 'm': 'M', 'n': 'N',
    'o': 'O', 'p': 'P', 'q': 'Q', 'r': 'R', 's': 'S', 't': 'T', 'u': 'U',
    'v': 'V', 'w': 'W', 'x': 'X', 'y': 'Y', 'z': 'Z'
}

# Letter sounds - the phonetic sound each letter makes
LETTER_SOUNDS = {
    'a': 'ah',      # short a as in "cat"
    'b': 'buh',     # b sound
    'c': 'kuh',     # hard c as in "cat"
    'd': 'duh',     # d sound
    'e': 'eh',      # short e as in "bed"
    'f': 'fff',     # f sound
    'g': 'guh',     # hard g as in "go"
    'h': 'huh',     # h sound
    'i': 'ih',      # short i as in "sit"
    'j': 'juh',     # j sound
    'k': 'kuh',     # k sound
    'l': 'lll',     # l sound
    'm': 'mmm',     # m sound
    'n': 'nnn',     # n sound
    'o': 'oh',      # short o as in "hot"
    'p': 'puh',     # p sound
    'q': 'kwuh',    # q sound
    'r': 'rrr',     # r sound
    's': 'sss',     # s sound
    't': 'tuh',     # t sound
    'u': 'uh',      # short u as in "cup"
    'v': 'vvv',     # v sound
    'w': 'wuh',     # w sound
    'x': 'ks',      # x sound
    'y': 'yuh',     # y sound
    'z': 'zzz'      # z sound
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
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Generate letter names
    print("Generating letter names...")
    names_dir = OUTPUT_DIR / "names"
    names_dir.mkdir(exist_ok=True)

    for letter, text in LETTER_NAMES.items():
        output_path = names_dir / f"{letter}.mp3"
        print(f"  {letter}: '{text}'", end=" ")
        if generate_audio(text, output_path):
            print("OK")
        else:
            print("FAILED")
        sleep(0.3)  # Rate limiting

    # Generate letter sounds
    print("\nGenerating letter sounds...")
    sounds_dir = OUTPUT_DIR / "sounds"
    sounds_dir.mkdir(exist_ok=True)

    for letter, text in LETTER_SOUNDS.items():
        output_path = sounds_dir / f"{letter}.mp3"
        print(f"  {letter}: '{text}'", end=" ")
        if generate_audio(text, output_path):
            print("OK")
        else:
            print("FAILED")
        sleep(0.3)  # Rate limiting

    print(f"\nDone! Files saved to {OUTPUT_DIR}")
    print(f"  Names: {names_dir}")
    print(f"  Sounds: {sounds_dir}")


if __name__ == "__main__":
    main()
