#!/usr/bin/env python3
"""Generate book cover using reference image for style."""

import sys
import os
import base64
import json
import subprocess

SKILL_DIR = "/Users/dereklomas/.claude/plugins/cache/mulerouter-skills/mulerouter-skills/1.0.0/skills/mulerouter-skills"

def image_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def generate_cover(ref_image_path, prompt, output_path, size="1024*1024"):
    """Generate a cover image using reference for style."""

    # Convert reference image to base64
    b64 = image_to_base64(ref_image_path)
    data_uri = f"data:image/png;base64,{b64}"

    # Create a temp file with the images array
    images_json = json.dumps([data_uri])

    # Write to temp file to avoid command line limits
    temp_images = "/tmp/gen_images.json"
    with open(temp_images, "w") as f:
        f.write(images_json)

    # Run the generation script
    cmd = [
        "uv", "run", "python", "models/alibaba/wan2.6-image/generation.py",
        "--prompt", prompt,
        "--images", images_json,
        "--size", size,
        "--n", "1"
    ]

    result = subprocess.run(
        cmd,
        cwd=SKILL_DIR,
        capture_output=True,
        text=True
    )

    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)

    # Parse output URL and download
    if result.returncode == 0:
        # Look for URL in output
        for line in result.stdout.split('\n'):
            if 'http' in line and ('.png' in line or '.jpg' in line or 'image' in line):
                print(f"Found image URL: {line}")

    return result.returncode == 0

if __name__ == "__main__":
    ref = "/Users/dereklomas/lilbookies/public/books/references/a0-look_reference.png"
    prompt = "Children's book cover illustration. A friendly cartoon eye looking at the viewer with wonder and curiosity. Soft watercolor style, simple bold shapes, warm colors, cute whimsical illustration for young children."
    output = "/Users/dereklomas/lilbookies/public/images/covers/a0-look.png"

    generate_cover(ref, prompt, output)
