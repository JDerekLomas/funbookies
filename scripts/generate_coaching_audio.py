#!/usr/bin/env python3
"""
Generate voice coaching audio for Direct Instruction lessons using OpenAI TTS.

Uses the 'nova' voice which is warm and friendly - perfect for parent coaching.

Usage:
    python scripts/generate_coaching_audio.py

Requires:
    - OPENAI_API_KEY environment variable
    - openai Python package (pip install openai)
"""

import os
import json
from pathlib import Path
from openai import OpenAI

# Initialize client
OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "")
if not OPENAI_KEY:
    print("Error: OPENAI_API_KEY environment variable not set")
    exit(1)

client = OpenAI(api_key=OPENAI_KEY)

# Output directory
OUTPUT_DIR = Path(__file__).parent.parent / "public" / "audio" / "coaching"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Voice settings
VOICE = "nova"  # Warm, friendly voice for coaching
MODEL = "tts-1"  # Standard model (tts-1-hd for higher quality)

# Letter sounds (phonetic representations for TTS)
LETTER_SOUNDS = {
    'a': 'aah', 'b': 'buh', 'c': 'kuh', 'd': 'duh', 'e': 'eh',
    'f': 'fff', 'g': 'guh', 'h': 'huh', 'i': 'ih', 'j': 'juh',
    'k': 'kuh', 'l': 'lll', 'm': 'mmm', 'n': 'nnn', 'o': 'ah',
    'p': 'puh', 'q': 'kwuh', 'r': 'rrr', 's': 'sss', 't': 'tuh',
    'u': 'uh', 'v': 'vvv', 'w': 'wuh', 'x': 'ks', 'y': 'yuh', 'z': 'zzz'
}

# Coaching phrases to generate
def get_coaching_phrases():
    """Generate all coaching phrases for the guided lesson."""
    phrases = {}

    # General coaching phrases
    general = {
        "intro_welcome": "Welcome to your guided lesson. Today we'll practice letter sounds together.",
        "intro_di": "We'll use the Model, Lead, Test method. First I show you. Then we do it together. Then it's your turn.",
        "great_job": "Great job!",
        "excellent": "Excellent work!",
        "perfect": "Perfect!",
        "thats_right": "That's right!",
        "try_again": "Let's try that again.",
        "watch_me": "Watch my mouth.",
        "say_with_me": "Say it with me.",
        "your_turn": "Your turn. What sound does this letter make?",
        "lesson_complete": "Wonderful! You finished the lesson. Great teaching today!",
    }
    phrases["general"] = general

    # Per-letter coaching phrases
    for letter, sound in LETTER_SOUNDS.items():
        letter_phrases = {
            "model": f"This letter says {sound}. Watch my mouth: {sound}.",
            "lead": f"Say it with me: {sound}.",
            "test": "Your turn. What sound?",
            "correct": f"{sound}. That's right!",
            "correction": f"That's {sound}. Say {sound}.",
        }
        phrases[f"letter_{letter}"] = letter_phrases

    return phrases


def generate_audio(text: str, output_path: Path):
    """Generate audio file using OpenAI TTS."""
    if output_path.exists():
        print(f"  Skipping (exists): {output_path.name}")
        return True

    try:
        response = client.audio.speech.create(
            model=MODEL,
            voice=VOICE,
            input=text,
            response_format="mp3"
        )

        response.stream_to_file(str(output_path))
        print(f"  Generated: {output_path.name}")
        return True

    except Exception as e:
        print(f"  Error generating {output_path.name}: {e}")
        return False


def main():
    print(f"Generating coaching audio with OpenAI TTS ({VOICE} voice)")
    print(f"Output directory: {OUTPUT_DIR}")
    print()

    phrases = get_coaching_phrases()
    total = 0
    generated = 0

    for category, category_phrases in phrases.items():
        print(f"\n{category}:")
        category_dir = OUTPUT_DIR / category
        category_dir.mkdir(exist_ok=True)

        for key, text in category_phrases.items():
            output_path = category_dir / f"{key}.mp3"
            total += 1

            if generate_audio(text, output_path):
                generated += 1

    print(f"\n\nComplete! Generated {generated}/{total} audio files.")
    print(f"Files saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
