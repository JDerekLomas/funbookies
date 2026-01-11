#!/usr/bin/env python3
"""
Regenerate specific phoneme sounds that failed with IPA tags.

Uses phonetic spelling approach instead of SSML phoneme tags.
"""

import os
import requests
from pathlib import Path
from time import sleep

# Try OpenAI first (better for short sounds), fall back to ElevenLabs
OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "")
ELEVENLABS_KEY = os.environ.get("ELEVENLABS_API_KEY", "")

OUTPUT_DIR = Path(__file__).parent.parent / "public" / "audio" / "phonemes"

# Phonemes that need regeneration with phonetic spellings
# The key insight: TTS needs something pronounceable, not abbreviations
BAD_PHONEMES = {
    # fl blend - f and l blended together
    "fl": "fluh",       # fl with short schwa

    # th voiceless - hissing sound, tongue between teeth
    "th_voiceless": "thh",  # Just the th sound stretched

    # ck - just k sound
    "ck": "kuh",        # k with schwa

    # oo long - as in moon, spoon
    "oo_long": "ooo",   # Long oo sound
}


def generate_openai(text: str, output_path: Path) -> bool:
    """Generate with OpenAI TTS - good for short sounds."""
    if not OPENAI_KEY:
        return False

    url = "https://api.openai.com/v1/audio/speech"
    headers = {"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"}
    data = {
        "model": "tts-1-hd",
        "input": text,
        "voice": "nova",  # Clear, neutral voice
        "response_format": "mp3",
        "speed": 0.85  # Slightly slower for clarity
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            return True
        print(f"  OpenAI error {response.status_code}: {response.text[:100]}")
        return False
    except Exception as e:
        print(f"  OpenAI error: {e}")
        return False


def generate_elevenlabs(text: str, output_path: Path) -> bool:
    """Generate with ElevenLabs as fallback."""
    if not ELEVENLABS_KEY:
        return False

    # Use a clear voice
    voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    headers = {
        "xi-api-key": ELEVENLABS_KEY,
        "Content-Type": "application/json"
    }

    data = {
        "text": text,
        "model_id": "eleven_turbo_v2",
        "voice_settings": {
            "stability": 0.8,
            "similarity_boost": 0.75
        }
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            return True
        print(f"  ElevenLabs error {response.status_code}")
        return False
    except Exception as e:
        print(f"  ElevenLabs error: {e}")
        return False


def main():
    print("=" * 50)
    print("REGENERATING BAD PHONEME SOUNDS")
    print("=" * 50)
    print(f"Output: {OUTPUT_DIR}")
    print(f"Phonemes to fix: {len(BAD_PHONEMES)}")
    print()

    # Back up old files
    backup_dir = OUTPUT_DIR / "backup"
    backup_dir.mkdir(exist_ok=True)

    for phoneme_id, phonetic in BAD_PHONEMES.items():
        output_path = OUTPUT_DIR / f"{phoneme_id}.mp3"
        backup_path = backup_dir / f"{phoneme_id}_old.mp3"

        # Backup existing
        if output_path.exists():
            import shutil
            shutil.copy(output_path, backup_path)

        print(f"  {phoneme_id}: '{phonetic}'", end=" ... ")

        # Try OpenAI first
        if generate_openai(phonetic, output_path):
            print("OK (OpenAI)")
        elif generate_elevenlabs(phonetic, output_path):
            print("OK (ElevenLabs)")
        else:
            print("FAILED")

        sleep(0.3)

    print()
    print("=" * 50)
    print("Done! Old files backed up to /backup/")
    print("Test the new sounds in the review interface.")


if __name__ == "__main__":
    main()
