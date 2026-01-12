#!/usr/bin/env python3
"""Regenerate all rejected sounds using OpenAI."""

import requests
from pathlib import Path
from time import sleep

OPENAI_KEY = "OPENAI_API_KEY_PLACEHOLDER"

OUTPUT_BASE = Path("/Users/dereklomas/lilbookies/public/activities/letter-sounds")


def generate_openai(text: str, output_path: Path, voice: str = "nova") -> bool:
    url = "https://api.openai.com/v1/audio/speech"
    headers = {"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"}
    data = {
        "model": "tts-1-hd",
        "input": text,
        "voice": voice,
        "response_format": "mp3",
        "speed": 0.85
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


def regenerate_set(set_name: str, sound_type: str, letters: dict, voice: str = "nova"):
    print(f"\n{set_name} {sound_type}:")
    output_dir = OUTPUT_BASE / set_name / sound_type
    output_dir.mkdir(parents=True, exist_ok=True)

    for letter, text in letters.items():
        output_path = output_dir / f"{letter}.mp3"
        print(f"  {letter}: '{text}'", end=" ")
        if generate_openai(text, output_path, voice):
            print("OK")
        else:
            print("FAILED")
        sleep(0.2)


def main():
    # 1. Fix OpenAI US sounds: c, f, i, p, r, v
    # Try different phonetic approaches
    us_sounds_fixes = {
        'c': 'k',       # just the k sound
        'f': 'f',       # pure f
        'i': 'i',       # short i vowel
        'p': 'p',       # pure p
        'r': 'r',       # pure r
        'v': 'v',       # pure v
    }
    regenerate_set("openai-us", "sounds", us_sounds_fixes)

    # 2. Create/update OpenAI UK set
    # UK letter names (with zed)
    uk_names = {
        'a': 'A', 'f': 'F', 'g': 'G', 'h': 'H', 'i': 'I',
        's': 'S', 'u': 'U', 'w': 'W', 'y': 'Y'
    }
    regenerate_set("openai-uk", "names", uk_names)

    # Also do Z as zed for UK
    print("\n  z: 'zed'", end=" ")
    if generate_openai("zed", OUTPUT_BASE / "openai-uk" / "names" / "z.mp3"):
        print("OK")
    else:
        print("FAILED")

    # 3. UK sounds
    uk_sounds_fixes = {
        'c': 'k',
        'e': 'e',       # short e
        'k': 'k',
        'p': 'p',
        's': 's',
        'w': 'w',
        'z': 'z',
    }
    regenerate_set("openai-uk", "sounds", uk_sounds_fixes)

    # Generate rest of UK names and sounds that weren't rejected
    print("\n\nGenerating remaining UK letters...")

    all_letters = 'abcdefghijklmnopqrstuvwxyz'
    existing_uk_names = set(uk_names.keys()) | {'z'}
    existing_uk_sounds = set(uk_sounds_fixes.keys())

    # Remaining UK names
    remaining_names = {l: l.upper() for l in all_letters if l not in existing_uk_names}
    if remaining_names:
        regenerate_set("openai-uk", "names", remaining_names)

    # Remaining UK sounds
    sound_phonetics = {
        'a': 'ah', 'b': 'buh', 'd': 'duh', 'f': 'f', 'g': 'guh',
        'h': 'huh', 'i': 'i', 'j': 'juh', 'l': 'l', 'm': 'm',
        'n': 'n', 'o': 'o', 'q': 'kwuh', 'r': 'r', 't': 't',
        'u': 'uh', 'v': 'v', 'x': 'ks', 'y': 'yuh'
    }
    remaining_sounds = {l: sound_phonetics.get(l, l) for l in all_letters if l not in existing_uk_sounds}
    if remaining_sounds:
        regenerate_set("openai-uk", "sounds", remaining_sounds)

    print("\n\nDone!")


if __name__ == "__main__":
    main()
