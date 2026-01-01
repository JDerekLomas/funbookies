#!/usr/bin/env python3
"""Test PuLID Flux for character consistency via fal.ai."""

import os
import requests
import time
from pathlib import Path

FAL_API_KEY = os.environ.get("FAL_API_KEY", "4249f047-fa0a-4f78-8c6e-8dc227a33bc3:48599b940122a72433d2d1d32616e1aa")
REFERENCE_URL = "https://funbookies.vercel.app/experiments/images/gus_wan26_hero_1.png"

OUTPUT_DIR = Path("experiments/images")

CHARACTER = """A small bright lime-green gecko with big round friendly eyes,
yellow-green belly, curled striped tail, four stubby legs, cute cartoonish style"""

STYLE = """children's book illustration, simple flat cartoon style, bold black outlines,
bright saturated colors, clean digital art, no text"""

SCENES = [
    ("pulid_volcano", "standing on a grassy hill looking at a distant smoking volcano, sunny day"),
    ("pulid_running", "running excitedly up a rocky mountain slope"),
    ("pulid_crater", "standing at the edge of a volcanic crater, steam rising"),
]


def generate_pulid(prompt: str, reference_url: str, output_name: str) -> bool:
    """Generate image using PuLID Flux."""
    print(f"\n{'='*50}")
    print(f"Generating: {output_name}")
    print(f"{'='*50}")

    url = "https://queue.fal.run/fal-ai/flux-pulid"
    headers = {
        "Authorization": f"Key {FAL_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "prompt": prompt,
        "reference_image_url": reference_url,  # PuLID takes single reference image
        "image_size": "square",
        "num_inference_steps": 28,
        "guidance_scale": 4.0,
    }

    try:
        print(f"Submitting to fal.ai PuLID...")
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        print(f"Status: {response.status_code}")

        if response.status_code != 200:
            print(f"Error: {response.text}")
            return False

        result = response.json()
        request_id = result.get("request_id")

        if not request_id:
            print(f"No request_id: {result}")
            return False

        print(f"Request ID: {request_id}")

        # Poll for result
        for i in range(90):  # 3 minutes
            time.sleep(2)
            status_url = f"https://queue.fal.run/fal-ai/flux-pulid/requests/{request_id}/status"
            status_resp = requests.get(status_url, headers=headers, timeout=30)
            status_data = status_resp.json()
            status = status_data.get("status")

            if status == "COMPLETED":
                result_url = f"https://queue.fal.run/fal-ai/flux-pulid/requests/{request_id}"
                result_resp = requests.get(result_url, headers=headers, timeout=30)
                result_data = result_resp.json()

                images = result_data.get("images", [])
                if images:
                    img_url = images[0].get("url")
                    img_resp = requests.get(img_url, timeout=60)
                    output_path = OUTPUT_DIR / f"gus_{output_name}.png"
                    with open(output_path, "wb") as f:
                        f.write(img_resp.content)
                    print(f"SUCCESS: {output_path}")
                    return True
                else:
                    print(f"No images: {result_data}")
                break
            elif status in ("FAILED", "CANCELLED"):
                print(f"FAILED: {status_data}")
                return False
            else:
                if i % 5 == 0:
                    print(f"  Status: {status}...")

    except Exception as e:
        print(f"ERROR: {e}")

    return False


def main():
    print("="*60)
    print("PULID FLUX CHARACTER CONSISTENCY TEST")
    print("="*60)
    print(f"Reference: {REFERENCE_URL}")

    results = []

    for scene_name, scene_desc in SCENES:
        prompt = f"{CHARACTER}, {scene_desc}, {STYLE}"
        success = generate_pulid(prompt, REFERENCE_URL, scene_name)
        results.append((scene_name, success))
        time.sleep(3)

    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    for name, success in results:
        status = "✓" if success else "✗"
        print(f"  {status} {name}")


if __name__ == "__main__":
    main()
