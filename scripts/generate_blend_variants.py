#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["openai", "requests", "python-dotenv"]
# ///
"""
Generate blend sound variants for A/B testing experiment.
Creates audio files using both OpenAI and ElevenLabs TTS.
"""

import os
import json
import requests
from pathlib import Path
from time import sleep
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / ".env.local")
load_dotenv(PROJECT_ROOT / ".env")

OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "").strip().strip('"')
ELEVENLABS_KEY = os.environ.get("ELEVENLABS_API_KEY", "").strip().strip('"')

openai_client = OpenAI(api_key=OPENAI_KEY)

# Directories
VARIANTS_DIR = PROJECT_ROOT / "public" / "activities" / "blends" / "variants"
OPENAI_DIR = VARIANTS_DIR / "openai-us"
ELEVENLABS_DIR = VARIANTS_DIR / "elevenlabs-uk"

# ElevenLabs voices
ELEVENLABS_VOICE = "Xb7hH8MSUJpSbSDYk0k2"  # Alice - clear British


def generate_openai(text: str, output_path: Path) -> bool:
    """Generate audio using OpenAI TTS."""
    try:
        response = openai_client.audio.speech.create(
            model="tts-1-hd",
            voice="nova",
            input=text,
            speed=0.85,
        )
        response.stream_to_file(str(output_path))
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


def generate_elevenlabs(text: str, output_path: Path) -> bool:
    """Generate audio using ElevenLabs TTS."""
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE}"
    headers = {"xi-api-key": ELEVENLABS_KEY, "Content-Type": "application/json"}
    data = {
        "text": text,
        "model_id": "eleven_turbo_v2_5",
        "voice_settings": {"stability": 0.75, "similarity_boost": 0.75}
    }
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            return True
        print(f"Error {response.status_code}: {response.text[:100]}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    print("=" * 60)
    print("GENERATING BLEND SOUND VARIANTS")
    print("=" * 60)

    # Load variants
    variants_path = VARIANTS_DIR / "variants.json"
    with open(variants_path) as f:
        data = json.load(f)

    blends = data["blends"]

    # Create directories
    OPENAI_DIR.mkdir(parents=True, exist_ok=True)
    ELEVENLABS_DIR.mkdir(parents=True, exist_ok=True)

    total = 0
    success = 0

    for blend, variants in blends.items():
        print(f"\n[{blend}]")
        for variant in variants:
            vid = variant["id"]
            spelling = variant["spelling"]

            # OpenAI
            openai_path = OPENAI_DIR / f"{blend}_{vid}.mp3"
            print(f"  OpenAI '{spelling}'...", end=" ")
            if openai_path.exists():
                print("SKIP")
                success += 1
            elif generate_openai(spelling, openai_path):
                print("OK")
                success += 1
            else:
                print("FAILED")
            total += 1
            sleep(0.2)

            # ElevenLabs
            el_path = ELEVENLABS_DIR / f"{blend}_{vid}.mp3"
            print(f"  ElevenLabs '{spelling}'...", end=" ")
            if el_path.exists():
                print("SKIP")
                success += 1
            elif generate_elevenlabs(spelling, el_path):
                print("OK")
                success += 1
            else:
                print("FAILED")
            total += 1
            sleep(0.2)

    print(f"\n{'=' * 60}")
    print(f"Done! {success}/{total} generated")


if __name__ == "__main__":
    main()
