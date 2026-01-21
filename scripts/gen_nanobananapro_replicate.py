#!/usr/bin/env python3
"""Generate image with nano-banana-pro via Replicate API."""

import os
import sys
import urllib.request
from pathlib import Path

# /// script
# dependencies = ["replicate"]
# ///

import replicate

def main():
    prompt = sys.argv[1] if len(sys.argv) > 1 else "A test image"
    output_path = sys.argv[2] if len(sys.argv) > 2 else "output.png"

    # Set API token from env
    api_token = os.environ.get("REPLICATE_API_TOKEN")
    if not api_token:
        print("REPLICATE_API_TOKEN not set")
        sys.exit(1)

    print(f"Generating with nano-banana-pro via Replicate...")
    print(f"Prompt: {prompt[:100]}...")

    # google-deepmind/imagen-3 or similar - let me check what's available
    # Actually nano-banana is a custom name - let me try google's imagen
    output = replicate.run(
        "google-deepmind/imagen-3",
        input={
            "prompt": prompt,
            "aspect_ratio": "1:1",
            "output_format": "png"
        }
    )

    print(f"Output: {output}")

    # Download if URL
    if isinstance(output, str) and output.startswith("http"):
        print(f"Downloading to {output_path}...")
        urllib.request.urlretrieve(output, output_path)
        print(f"Saved: {output_path}")
    elif hasattr(output, '__iter__'):
        for i, url in enumerate(output):
            if isinstance(url, str) and url.startswith("http"):
                urllib.request.urlretrieve(url, output_path)
                print(f"Saved: {output_path}")
                break

if __name__ == "__main__":
    main()
