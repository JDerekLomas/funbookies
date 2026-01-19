#!/usr/bin/env python3
"""
Generate letter sounds with multiple voices for A/B testing experiment.
Creates audio files for all combinations of:
- Letters (problematic ones: c, e, f, i, l, p, r, v, z)
- Phonetic spellings (user-selected best options)
- Voices (OpenAI: nova, alloy, shimmer; ElevenLabs: Alice, Sarah, Jessica)
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
BACKUP_ENV = Path("/Users/dereklomas/playpowerlearn-v1-archive/playpowerlearn-app/.env.local")
if BACKUP_ENV.exists():
    load_dotenv(BACKUP_ENV)

OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "").strip().strip('"')
ELEVENLABS_KEY = os.environ.get("ELEVENLABS_API_KEY", "").strip().strip('"')

openai_client = OpenAI(api_key=OPENAI_KEY)

# Output directory
EXPERIMENT_DIR = PROJECT_ROOT / "public" / "experiments" / "letter-sounds"

# Voices to test
VOICES = {
    "openai": {
        "nova": {"name": "Nova", "description": "Clear, neutral American"},
        "alloy": {"name": "Alloy", "description": "Warm, balanced"},
        "shimmer": {"name": "Shimmer", "description": "Expressive, upbeat"},
    },
    "elevenlabs": {
        "Xb7hH8MSUJpSbSDYk0k2": {"name": "Alice", "description": "Clear British educator"},
        "EXAVITQu4vr4xnSDxMaL": {"name": "Sarah", "description": "Mature, reassuring American"},
        "cgSgspJ2msm6clMCkdW9": {"name": "Jessica", "description": "Playful, bright American"},
    }
}

# User-selected best phonetic spellings
LETTER_SOUNDS = {
    "c": "kah",
    "e": "ehhh",
    "f": "fuh",
    "i": "ihhh",
    "l": "lah",
    "p": "peh",
    "r": "rah",
    "v": "vah",
    "z": "zah",
}


def generate_openai(text: str, voice: str, output_path: Path) -> bool:
    """Generate audio using OpenAI TTS."""
    try:
        response = openai_client.audio.speech.create(
            model="tts-1-hd",
            voice=voice,
            input=text,
            speed=0.85,
        )
        response.stream_to_file(str(output_path))
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


def generate_elevenlabs(text: str, voice_id: str, output_path: Path) -> bool:
    """Generate audio using ElevenLabs TTS."""
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
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
        print(f"Error {response.status_code}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    print("=" * 60)
    print("GENERATING VOICE EXPERIMENT DATA")
    print("=" * 60)

    # Create output directory
    audio_dir = EXPERIMENT_DIR / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)

    # Track all generated files
    experiment_data = {
        "letters": list(LETTER_SOUNDS.keys()),
        "spellings": LETTER_SOUNDS,
        "voices": {},
        "samples": []
    }

    total = 0
    success = 0

    # Generate OpenAI voices
    print("\n[OpenAI Voices]")
    for voice_id, voice_info in VOICES["openai"].items():
        experiment_data["voices"][f"openai_{voice_id}"] = {
            "service": "openai",
            "id": voice_id,
            "name": voice_info["name"],
            "description": voice_info["description"]
        }

        for letter, spelling in LETTER_SOUNDS.items():
            filename = f"openai_{voice_id}_{letter}.mp3"
            output_path = audio_dir / filename
            print(f"  {voice_info['name']} - {letter} ({spelling})...", end=" ")

            if generate_openai(spelling, voice_id, output_path):
                print("OK")
                success += 1
                experiment_data["samples"].append({
                    "letter": letter,
                    "spelling": spelling,
                    "voice": f"openai_{voice_id}",
                    "file": filename
                })
            else:
                print("FAILED")
            total += 1
            sleep(0.2)

    # Generate ElevenLabs voices
    print("\n[ElevenLabs Voices]")
    for voice_id, voice_info in VOICES["elevenlabs"].items():
        safe_id = voice_id[:8]
        experiment_data["voices"][f"elevenlabs_{safe_id}"] = {
            "service": "elevenlabs",
            "id": voice_id,
            "name": voice_info["name"],
            "description": voice_info["description"]
        }

        for letter, spelling in LETTER_SOUNDS.items():
            filename = f"elevenlabs_{safe_id}_{letter}.mp3"
            output_path = audio_dir / filename
            print(f"  {voice_info['name']} - {letter} ({spelling})...", end=" ")

            if generate_elevenlabs(spelling, voice_id, output_path):
                print("OK")
                success += 1
                experiment_data["samples"].append({
                    "letter": letter,
                    "spelling": spelling,
                    "voice": f"elevenlabs_{safe_id}",
                    "file": filename
                })
            else:
                print("FAILED")
            total += 1
            sleep(0.2)

    # Save experiment metadata
    metadata_path = EXPERIMENT_DIR / "experiment.json"
    with open(metadata_path, 'w') as f:
        json.dump(experiment_data, f, indent=2)

    print(f"\n{'=' * 60}")
    print(f"Done! {success}/{total} generated")
    print(f"Metadata: {metadata_path}")
    print(f"Audio: {audio_dir}")


if __name__ == "__main__":
    main()
