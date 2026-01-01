#!/usr/bin/env python3
"""Test Midjourney --cref character reference via MuleRun API."""

import os
import requests
import time
from pathlib import Path

# MuleRun API
API_BASE = "https://api.mulerun.com"
API_KEY = os.environ.get("MULEROUTER_API_KEY", "sk-mr-2dfbbdfe5bbd2e24235960b2d4f5b45bf1b59a087bc2524ff35c6c70a2657436")

# Reference image (publicly accessible)
REFERENCE_URL = "https://funbookies.vercel.app/experiments/images/gus_wan26_hero_1.png"

# Output directory
OUTPUT_DIR = Path("experiments/images")

# Character description
CHARACTER = """A small bright lime-green gecko with big round friendly eyes,
yellow-green belly, curled striped tail, four stubby legs, cute cartoonish style"""

STYLE = """children's book illustration, simple flat cartoon style, bold black outlines,
bright saturated colors, clean digital art, no text"""

# Test scenes
SCENES = [
    ("mj_cref_volcano", "standing on a grassy hill looking at a distant smoking volcano, sunny day"),
    ("mj_cref_running", "running excitedly up a rocky mountain slope"),
    ("mj_cref_crater", "standing at the edge of a volcanic crater, steam rising"),
]


def generate_midjourney(prompt: str, output_name: str, use_cref: bool = True) -> bool:
    """Generate image using Midjourney via MuleRun."""
    print(f"\n{'='*50}")
    print(f"Generating: {output_name}")
    print(f"{'='*50}")

    # Build prompt with --cref if requested
    full_prompt = prompt
    if use_cref:
        full_prompt = f"{prompt} --cref {REFERENCE_URL} --cw 100"

    print(f"Prompt: {full_prompt[:100]}...")

    url = f"{API_BASE}/vendors/midjourney/v1/tob/diffusion"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    print(f"Using API key: {API_KEY[:20]}...")

    payload = {
        "prompt": full_prompt,
        "mode": "fast",  # fast, turbo, draft_fast, draft_turbo
        "aspect_ratio": "1:1",
    }

    try:
        # Submit generation request
        print("Submitting to MuleRun...")
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        print(f"Status: {response.status_code}")

        if response.status_code != 200:
            print(f"Error: {response.text}")
            return False

        result = response.json()
        print(f"Response keys: {list(result.keys())}")

        # Check if we got images directly or need to poll
        if "images" in result:
            images = result["images"]
            if images:
                img_url = images[0] if isinstance(images[0], str) else images[0].get("url")
                print(f"Image URL: {img_url[:80]}...")

                img_resp = requests.get(img_url, timeout=60)
                output_path = OUTPUT_DIR / f"{output_name}.png"
                with open(output_path, "wb") as f:
                    f.write(img_resp.content)
                print(f"SUCCESS: {output_path}")
                return True

        # Check for task_id (async generation)
        task_id = result.get("task_id") or result.get("id") or result.get("request_id")
        if task_id:
            print(f"Task ID: {task_id}")
            return poll_for_result(task_id, output_name, headers)

        # Maybe we got the image URL directly
        if "url" in result:
            img_url = result["url"]
            img_resp = requests.get(img_url, timeout=60)
            output_path = OUTPUT_DIR / f"{output_name}.png"
            with open(output_path, "wb") as f:
                f_write(img_resp.content)
            print(f"SUCCESS: {output_path}")
            return True

        print(f"Unexpected response: {result}")
        return False

    except Exception as e:
        print(f"ERROR: {e}")
        return False


def poll_for_result(task_id: str, output_name: str, headers: dict) -> bool:
    """Poll for async task result."""
    status_url = f"{API_BASE}/vendors/midjourney/v1/tob/diffusion/{task_id}"

    for i in range(60):  # 5 minutes max
        time.sleep(5)

        try:
            resp = requests.get(status_url, headers=headers, timeout=30)
            data = resp.json()

            status = data.get("status", "unknown")
            print(f"  [{i*5}s] Status: {status}")

            if status in ("completed", "succeeded", "COMPLETED"):
                images = data.get("images", [])
                if images:
                    img_url = images[0] if isinstance(images[0], str) else images[0].get("url")
                    img_resp = requests.get(img_url, timeout=60)
                    output_path = OUTPUT_DIR / f"{output_name}.png"
                    with open(output_path, "wb") as f:
                        f.write(img_resp.content)
                    print(f"SUCCESS: {output_path}")
                    return True

            elif status in ("failed", "FAILED", "error"):
                print(f"FAILED: {data}")
                return False

        except Exception as e:
            print(f"  Poll error: {e}")

    print("Timeout waiting for result")
    return False


def main():
    print("="*60)
    print("MIDJOURNEY --CREF TEST VIA MULERUN")
    print("="*60)
    print(f"Reference image: {REFERENCE_URL}")
    print(f"API: {API_BASE}")

    results = []

    for scene_name, scene_desc in SCENES:
        prompt = f"{CHARACTER}, {scene_desc}, {STYLE}"
        success = generate_midjourney(prompt, scene_name, use_cref=True)
        results.append((scene_name, success))
        time.sleep(3)  # Rate limiting

    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    for name, success in results:
        status = "✓" if success else "✗"
        print(f"  {status} {name}")


if __name__ == "__main__":
    main()
