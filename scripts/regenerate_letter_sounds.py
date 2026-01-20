#!/usr/bin/env python3
"""
Regenerate specific letter sounds using ElevenLabs with IPA phoneme tags.

Uses SSML phoneme tags for precise pronunciation control.
Requires eleven_turbo_v2 model (phoneme tags don't work with v2.5).
"""

import os
import requests
from pathlib import Path
from time import sleep

from dotenv import load_dotenv

# Load environment variables
PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / ".env.local")
load_dotenv(PROJECT_ROOT / ".env")

# API Key
ELEVENLABS_KEY = os.environ.get("ELEVENLABS_API_KEY", "").strip().strip('"')
if not ELEVENLABS_KEY:
    print("Error: ELEVENLABS_API_KEY environment variable not set")
    exit(1)

# Voice - Rachel is a clear, neutral American voice good for education
VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Rachel

# Output directory - regenerate to openai-us/sounds since that's what's being used
OUTPUT_DIR = PROJECT_ROOT / "public" / "activities" / "letter-sounds" / "openai-us" / "sounds"

# Letter sounds that need regeneration with proper IPA
# Format: letter -> (SSML with phoneme tag, description)
LETTER_SOUNDS_IPA = {
    "c": ('<phoneme alphabet="ipa" ph="k">k</phoneme>', "/k/ as in cat"),
    "e": ('<phoneme alphabet="ipa" ph="ɛ">e</phoneme>', "/ɛ/ short e as in bed"),
    "f": ('<phoneme alphabet="ipa" ph="f">f</phoneme>', "/f/ as in fan"),
    "i": ('<phoneme alphabet="ipa" ph="ɪ">i</phoneme>', "/ɪ/ short i as in sit"),
    "j": ('<phoneme alphabet="ipa" ph="dʒ">j</phoneme>', "/dʒ/ as in jump"),
    "l": ('<phoneme alphabet="ipa" ph="l">l</phoneme>', "/l/ as in lamp"),
    "p": ('<phoneme alphabet="ipa" ph="p">p</phoneme>', "/p/ as in pig"),
    "r": ('<phoneme alphabet="ipa" ph="ɹ">r</phoneme>', "/ɹ/ as in red"),
    "v": ('<phoneme alphabet="ipa" ph="v">v</phoneme>', "/v/ as in van"),
    "z": ('<phoneme alphabet="ipa" ph="z">z</phoneme>', "/z/ as in zip"),
}


def generate_elevenlabs_phoneme(ssml_text: str, output_path: Path) -> bool:
    """Generate audio using ElevenLabs TTS with SSML phoneme tags."""
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {
        "xi-api-key": ELEVENLABS_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "text": ssml_text,
        "model_id": "eleven_turbo_v2",  # Must use v2 for phoneme tags
        "voice_settings": {
            "stability": 0.8,
            "similarity_boost": 0.6
        }
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            return True
        else:
            print(f"  Error {response.status_code}: {response.text[:100]}")
            return False
    except Exception as e:
        print(f"  Error: {e}")
        return False


def main():
    print("=" * 50)
    print("REGENERATING LETTER SOUNDS (ElevenLabs IPA)")
    print("=" * 50)
    print(f"\nOutput: {OUTPUT_DIR}")
    print(f"Letters: {', '.join(LETTER_SOUNDS_IPA.keys())}\n")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    success = 0
    for letter, (ssml, description) in LETTER_SOUNDS_IPA.items():
        output_path = OUTPUT_DIR / f"{letter}.mp3"
        print(f"  {letter}: {description}", end=" ... ")

        if generate_elevenlabs_phoneme(ssml, output_path):
            print("OK")
            success += 1
        else:
            print("FAILED")

        sleep(0.3)  # Rate limiting

    print(f"\nDone! {success}/{len(LETTER_SOUNDS_IPA)} generated successfully")


if __name__ == "__main__":
    main()
