#!/usr/bin/env python3
"""
Apply fade-out effect to audio files for smoother endings.

Uses ffmpeg to apply a 0.25 second fade-out to the end of each audio file.
"""

import subprocess
import os
from pathlib import Path
import shutil

AUDIO_DIR = Path(__file__).parent.parent / "public" / "audio" / "phonemes"
FADE_DURATION = 0.25  # seconds


def get_audio_duration(file_path: Path) -> float:
    """Get duration of audio file in seconds."""
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(file_path)],
        capture_output=True, text=True
    )
    return float(result.stdout.strip())


def apply_fadeout(file_path: Path, fade_duration: float = FADE_DURATION) -> bool:
    """Apply fade-out effect to audio file using ffmpeg."""
    try:
        duration = get_audio_duration(file_path)
        fade_start = max(0, duration - fade_duration)

        # Create temp output file
        temp_path = file_path.with_suffix('.tmp.mp3')

        # Apply fade-out filter
        result = subprocess.run([
            "ffmpeg", "-y", "-i", str(file_path),
            "-af", f"afade=t=out:st={fade_start}:d={fade_duration}",
            "-c:a", "libmp3lame", "-q:a", "2",
            str(temp_path)
        ], capture_output=True, text=True)

        if result.returncode == 0 and temp_path.exists():
            # Replace original with faded version
            shutil.move(str(temp_path), str(file_path))
            return True
        else:
            if temp_path.exists():
                temp_path.unlink()
            print(f"  Error: {result.stderr[:100]}")
            return False

    except Exception as e:
        print(f"  Error: {e}")
        return False


def main():
    print("=" * 50)
    print("APPLYING FADE-OUT TO PHONEME AUDIO")
    print("=" * 50)
    print(f"Directory: {AUDIO_DIR}")
    print(f"Fade duration: {FADE_DURATION}s")
    print()

    # Get all MP3 files (excluding backup folder)
    mp3_files = [f for f in AUDIO_DIR.glob("*.mp3") if f.is_file()]
    print(f"Found {len(mp3_files)} audio files")
    print()

    success = 0
    failed = 0

    for mp3_file in sorted(mp3_files):
        print(f"  {mp3_file.stem}", end=" ... ")
        if apply_fadeout(mp3_file):
            print("OK")
            success += 1
        else:
            print("FAILED")
            failed += 1

    print()
    print("=" * 50)
    print(f"Done! {success} processed, {failed} failed")


if __name__ == "__main__":
    main()
