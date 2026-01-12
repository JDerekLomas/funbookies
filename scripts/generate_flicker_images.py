#!/usr/bin/env python3
"""Generate remaining images for Flicker the Firefly book."""

import base64
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

# Add the skill directory to Python path for imports
SKILL_DIR = Path.home() / ".claude/plugins/cache/mulerouter-skills/mulerouter-skills/1.0.0/skills/mulerouter-skills"
sys.path.insert(0, str(SKILL_DIR))

# Paths
BOOK_DIR = Path("/Users/dereklomas/lilbookies/public/books")
REF_IMAGE = Path("/tmp/flicker_ref_tiny.png")
OUTPUT_DIR = BOOK_DIR / "images"

# Pages to generate (14 and 18 are missing, 17 already exists)
PAGES = [
    {
        "page": 14,
        "prompt": "Flicker the firefly and Dot the moth arriving at a cozy hollow log home. Dot's moth family is there waiting, looking relieved and happy. Warm light spills from inside the log. Dot is rushing toward her family. Flicker watches with a gentle smile. Magical nighttime watercolor style, deep blues and purples with warm golden firefly glows. Cute children's book illustration. Wide shot.",
    },
    {
        "page": 18,
        "prompt": "Peaceful nighttime scene with Flicker glowing contentedly among friends. Dot the moth waves from below near her log home. Stars and firefly lights create a magical atmosphere. Everything feels warm, safe, and happy. A perfect ending. Magical nighttime watercolor, deep blues and purples with warm golden glows. Cute children's book illustration. Wide shot.",
    },
]

def encode_image(path: Path) -> str:
    """Encode image to base64 data URI."""
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")
    return f"data:image/png;base64,{data}"

def call_api(prompt: str, images: list, size: str = "1024*1024", n: int = 1):
    """Call the MuleRun API directly."""
    # Load .env for API key
    env_file = SKILL_DIR / ".env"
    api_key = os.environ.get("MULEROUTER_API_KEY")
    site = os.environ.get("MULEROUTER_SITE", "mulerun")

    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    if key == "MULEROUTER_API_KEY":
                        api_key = value.strip('"\'')
                    elif key == "MULEROUTER_SITE":
                        site = value.strip('"\'')

    if not api_key:
        raise ValueError("MULEROUTER_API_KEY not set")

    # Determine base URL
    if site == "mulerun":
        base_url = "https://api.mulerun.ai"
    else:
        base_url = "https://api.mulerouter.ai"

    url = f"{base_url}/vendors/alibaba/v1/wan2.5-i2i-preview/generation"

    payload = {
        "prompt": prompt,
        "images": images,
        "size": size,
        "n": n
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Create task
    print(f"Creating task at {url}...")
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")

    with urllib.request.urlopen(req, timeout=180) as response:
        result = json.loads(response.read().decode("utf-8"))

    task_id = result.get("id") or result.get("task_id")
    print(f"Task ID: {task_id}")

    # Poll for result
    status_url = f"{base_url}/tasks/{task_id}"

    for i in range(120):  # 10 minutes max
        time.sleep(5)
        req = urllib.request.Request(status_url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            status_result = json.loads(response.read().decode("utf-8"))

        status = status_result.get("status")
        print(f"  Status: {status}")

        if status == "completed":
            # Get output
            output = status_result.get("output", {})
            images_out = output.get("images", [])
            if images_out:
                return images_out[0]
            # Check for other formats
            if "url" in output:
                return output["url"]
            print(f"  No images in output: {output}")
            return None
        elif status == "failed":
            error = status_result.get("error", "Unknown error")
            print(f"  Task failed: {error}")
            return None

    print("  Timeout waiting for task")
    return None

def download_image(url: str, output_path: Path):
    """Download image from URL."""
    print(f"Downloading from: {url}")
    urllib.request.urlretrieve(url, output_path)
    print(f"Saved to: {output_path}")

def main():
    print("Encoding reference image...")
    ref_data_uri = encode_image(REF_IMAGE)
    print(f"Reference encoded ({len(ref_data_uri)} bytes)")

    for page_info in PAGES:
        page_num = page_info["page"]
        output_path = OUTPUT_DIR / f"flicker-the-firefly_page{page_num:02d}.png"

        if output_path.exists():
            print(f"\nPage {page_num} already exists, skipping")
            continue

        print(f"\n{'='*60}")
        print(f"Generating page {page_num}...")
        print(f"Prompt: {page_info['prompt'][:80]}...")

        try:
            url = call_api(page_info["prompt"], [ref_data_uri])
            if url:
                download_image(url, output_path)
            else:
                print(f"Failed to generate page {page_num}")
        except Exception as e:
            print(f"Error generating page {page_num}: {e}")

    print("\n" + "="*60)
    print("Done!")

if __name__ == "__main__":
    main()
