#!/usr/bin/env python3
"""
Generate audio instructions for activities using OpenAI TTS.
Uses the 'nova' voice for clear, friendly instructions.
"""

import os
import requests
from pathlib import Path
from time import sleep

API_KEY = os.environ.get("OPENAI_API_KEY", "")
if not API_KEY:
    print("Error: OPENAI_API_KEY environment variable not set")
    exit(1)

OUTPUT_DIR = Path(__file__).parent.parent / "public" / "audio" / "instructions"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Instructions for each activity
INSTRUCTIONS = {
    # Word Builder
    "word-builder-intro": "Look at the picture. Tap the letters to spell the word!",
    "word-builder-hint": "Listen to the word, then find each letter.",
    "word-builder-correct": "Great job! You spelled it!",
    "word-builder-try-again": "Not quite. Try again!",

    # Letter Drill
    "letter-drill-intro": "Look at the letter. Say its sound out loud!",
    "letter-drill-sounds": "Let's practice letter sounds.",
    "letter-drill-names": "Let's practice letter names.",
    "letter-drill-correct": "That's right!",
    "letter-drill-next": "Here's the next letter.",

    # Sound Boxes
    "sound-boxes-intro": "Listen to the word. Drag each sound into a box!",
    "sound-boxes-hint": "Tap a letter to hear its sound.",
    "sound-boxes-correct": "Perfect! You got all the sounds!",
    "sound-boxes-try-again": "Oops! Let's try that again.",

    # Say the Sound
    "say-sound-intro": "Look at the letter. Say its sound into the microphone!",
    "say-sound-hint": "Press the big button and say the sound.",
    "say-sound-correct": "You said it perfectly!",
    "say-sound-try-again": "Try saying it again. Get close to the microphone.",

    # Blend It
    "blend-it-intro": "Tap each box to hear the sounds. Then blend them together!",
    "blend-it-hint": "Tap Sound Out to hear all the sounds.",
    "blend-it-correct": "You blended it!",

    # Voice Blend
    "voice-blend-intro": "Listen to each sound. Then say the whole word!",
    "voice-blend-hint": "Tap the speaker to hear the sounds again.",
    "voice-blend-correct": "That's the word!",
    "voice-blend-try-again": "Listen again and try once more.",

    # Word Chains
    "word-chains-intro": "Change one letter to make a new word!",
    "word-chains-hint": "Find the letter that's different.",
    "word-chains-correct": "Great! On to the next word!",

    # Chop It Up
    "chop-it-up-intro": "Listen to the word. Then say each sound, one at a time!",
    "chop-it-up-hint": "Break the word into pieces. Say each sound slowly.",
    "chop-it-up-check": "Tap the boxes to check your sounds.",
}


def generate_audio(text: str, output_path: Path, voice: str = "nova") -> bool:
    """Generate audio using OpenAI TTS."""
    if output_path.exists():
        print(f"  Skipping (exists): {output_path.name}")
        return True

    url = "https://api.openai.com/v1/audio/speech"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "tts-1",
        "input": text,
        "voice": voice,
        "response_format": "mp3",
        "speed": 0.9  # Slightly slower for clarity
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(response.content)
            print(f"  Generated: {output_path.name}")
            return True
        else:
            print(f"  Error {response.status_code}: {response.text[:100]}")
            return False
    except Exception as e:
        print(f"  Error: {e}")
        return False


def main():
    print(f"Generating instruction audio with OpenAI TTS (nova voice)")
    print(f"Output directory: {OUTPUT_DIR}\n")

    total = len(INSTRUCTIONS)
    generated = 0

    for key, text in INSTRUCTIONS.items():
        output_path = OUTPUT_DIR / f"{key}.mp3"
        if generate_audio(text, output_path):
            generated += 1
        sleep(0.1)  # Rate limiting

    print(f"\nComplete! Generated {generated}/{total} instruction files.")
    print(f"Files saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
