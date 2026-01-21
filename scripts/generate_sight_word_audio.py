#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["openai", "python-dotenv"]
# ///
"""
Generate audio for sight words and common words missing from the audio library.
Uses OpenAI TTS with Nova voice.
"""

import os
from pathlib import Path
from time import sleep
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / ".env.local")
load_dotenv(PROJECT_ROOT / ".env")

OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "").strip().strip('"')
openai_client = OpenAI(api_key=OPENAI_KEY)

AUDIO_OUTPUT_DIR = PROJECT_ROOT / "public" / "audio" / "words"

# Sight words from the sight-words activity
SIGHT_WORDS = [
    # A levels
    'a', 'i', 'the', 'is', 'to', 'and', 'it', 'in', 'on',
    # B levels
    'my', 'see', 'he', 'she', 'we', 'be', 'you', 'are', 'was', 'for',
    'said', 'have', 'they', 'come', 'there', 'what', 'from',
    'would', 'could', 'should', 'very', 'other', 'another', 'people',
    'where', 'were', 'here', 'their',
    # C levels
    'thought', 'through', 'eight', 'enough',
    'once', 'dance', 'since', 'little', 'something', 'nothing',
    'before', 'after', 'always', 'beautiful', 'special', 'important',
    'impossible', 'disappear', 'discover'
]

# Additional common words from rhyme-match and other activities
RHYME_WORDS = [
    # -at family extras
    'sat', 'pat', 'flat', 'chat',
    # -an family extras
    'ran', 'tan', 'plan',
    # -ig/-in extras
    'big', 'dig', 'win', 'tin', 'spin',
    # -op/-ot extras
    'hop', 'stop', 'drop', 'hot', 'dot', 'got', 'not', 'lot',
    # -ug/-ub/-un extras
    'hug', 'dug', 'rub', 'run', 'fun', 'spun',
    # Blends extras
    'grab', 'clap', 'snap', 'trip', 'drip', 'skip', 'slip', 'flip',
    # Digraph extras
    'thin', 'thick', 'think', 'this', 'that', 'them', 'then', 'than',
    'much', 'such', 'rich', 'which', 'lunch', 'bunch',
    'crash', 'trash', 'splash', 'brush', 'crush', 'rush',
    # -atch/-itch/-etch
    'catch', 'match', 'patch', 'batch', 'hatch', 'latch', 'scratch',
    'itch', 'pitch', 'ditch', 'switch', 'witch', 'stitch',
    # Magic e extras
    'make', 'take', 'bake', 'wake', 'shake', 'like', 'hide', 'ride', 'side', 'wide',
    'home', 'hope', 'rope', 'joke', 'poke', 'smoke',
    'cute', 'huge', 'use', 'rule',
    # R-controlled extras
    'art', 'part', 'start', 'smart', 'dark', 'mark', 'shark',
    'her', 'term', 'verb',
    'first', 'third', 'dirt', 'firm',
    'more', 'store', 'shore', 'wore', 'bore', 'core', 'score',
    'burn', 'turn', 'hurt', 'curl',
    # Vowel teams extras
    'day', 'say', 'play', 'stay', 'way', 'pay', 'may', 'lay',
    'team', 'dream', 'stream', 'cream', 'clean', 'mean', 'lean',
    'deep', 'keep', 'sleep', 'sheep', 'green', 'queen', 'seen',
    'lie', 'tie', 'pie', 'die', 'tried', 'cried',
    'low', 'slow', 'grow', 'show', 'know', 'blow', 'flow', 'glow',
    'loud', 'proud', 'found', 'sound', 'round', 'ground', 'pound',
    # Diphthongs extras
    'joy', 'enjoy',
    'oil', 'boil', 'foil', 'spoil', 'join', 'point',
    'now', 'how', 'cow', 'wow', 'brown', 'down', 'frown',
    # oo words
    'too', 'zoo', 'boo', 'room', 'boom', 'zoom', 'pool', 'cool', 'tool', 'school',
    'good', 'stood', 'hood', 'look', 'took', 'cook', 'shook',
]

ALL_WORDS = sorted(set(SIGHT_WORDS + RHYME_WORDS))


def generate_word_audio(word: str, output_path: Path) -> bool:
    """Generate audio using OpenAI TTS."""
    try:
        response = openai_client.audio.speech.create(
            model="tts-1-hd",
            voice="nova",
            input=word,
            speed=0.9,
        )
        response.stream_to_file(str(output_path))
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--sight-only", action="store_true", help="Only generate sight words")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be generated")
    args = parser.parse_args()

    words = SIGHT_WORDS if args.sight_only else ALL_WORDS

    print("=" * 60)
    print("GENERATING WORD AUDIO FILES")
    print("=" * 60)
    print(f"Words to check: {len(words)}")

    # Create output directory
    AUDIO_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Find missing words
    missing = []
    for word in words:
        output_path = AUDIO_OUTPUT_DIR / f"{word}.mp3"
        if not output_path.exists():
            missing.append(word)

    print(f"Missing audio: {len(missing)}")
    print()

    if args.dry_run:
        print("Would generate:")
        for w in missing:
            print(f"  - {w}")
        return

    if not missing:
        print("All words have audio files!")
        return

    success = 0
    for i, word in enumerate(missing, 1):
        output_path = AUDIO_OUTPUT_DIR / f"{word}.mp3"
        print(f"[{i}/{len(missing)}] {word}...", end=" ", flush=True)

        if generate_word_audio(word, output_path):
            print("OK")
            success += 1
        else:
            print("FAILED")

        sleep(0.15)  # Rate limit

    print(f"\n{'=' * 60}")
    print(f"Done! Generated {success}/{len(missing)} audio files")
    print(f"Output: {AUDIO_OUTPUT_DIR}")


if __name__ == "__main__":
    main()
