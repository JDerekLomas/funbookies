#!/usr/bin/env python3
"""Retry Kontext with direct URL reference."""

import requests
import time

import os
FAL_API_KEY = os.environ.get("FAL_API_KEY", "")
REFERENCE_URL = "https://funbookies.vercel.app/experiments/images/gus_wan26_hero_1.png"

CHARACTER = """A small bright lime-green gecko with big round friendly eyes with white sparkle highlights,
yellow-green belly, curled striped tail with darker green stripes, four stubby legs with tiny toe pads,
cute cartoonish style, standing upright on two legs, happy expression"""

STYLE = """children's book illustration, simple flat cartoon style, bold black outlines,
bright saturated colors, clean digital art, solid color background, no text"""

SCENES = [
    ("scene01_volcano", "standing on a grassy hill looking at a distant smoking volcano, sunny day"),
    ("scene02_running", "running excitedly up a rocky mountain slope, determined expression"),
    ("scene03_crater", "standing at the edge of a volcanic crater, looking down with wonder, steam rising"),
]

output_dir = "experiments/images"
headers = {
    "Authorization": f"Key {FAL_API_KEY}",
    "Content-Type": "application/json"
}

for scene_name, scene_desc in SCENES:
    print(f"\n{'='*50}")
    print(f"SCENE: {scene_name}")
    print(f"{'='*50}")

    prompt = f"{CHARACTER}, {scene_desc}, {STYLE}"

    # Try flux-subject with image_url
    payload = {
        "prompt": prompt,
        "image_url": REFERENCE_URL,  # Try this key
        "image_size": "square",
        "num_inference_steps": 28,
        "guidance_scale": 3.5,
    }

    url = "https://queue.fal.run/fal-ai/flux-subject"

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        print(f"  Response status: {response.status_code}")
        result = response.json()

        if "request_id" in result:
            request_id = result["request_id"]
            print(f"  Submitted: {request_id}")

            # Poll for result
            for _ in range(90):  # 3 minutes
                time.sleep(2)
                status_url = f"https://queue.fal.run/fal-ai/flux-subject/requests/{request_id}/status"
                status_resp = requests.get(status_url, headers=headers, timeout=30)
                status_data = status_resp.json()
                status = status_data.get("status")

                if status == "COMPLETED":
                    result_url = f"https://queue.fal.run/fal-ai/flux-subject/requests/{request_id}"
                    result_resp = requests.get(result_url, headers=headers, timeout=30)
                    result_data = result_resp.json()
                    print(f"  Result keys: {list(result_data.keys())}")

                    images = result_data.get("images", [])
                    if images:
                        img_url = images[0].get("url")
                        img_resp = requests.get(img_url, timeout=60)
                        output_path = f"{output_dir}/gus_v2_kontext_{scene_name}.png"
                        with open(output_path, "wb") as f:
                            f.write(img_resp.content)
                        print(f"  SUCCESS: {output_path}")
                    else:
                        print(f"  No images: {result_data}")
                    break
                elif status in ("FAILED", "CANCELLED"):
                    print(f"  FAILED: {status}")
                    break
                else:
                    if _ % 10 == 0:
                        print(f"  Status: {status}...")
        else:
            print(f"  ERROR: {result}")

    except Exception as e:
        print(f"  ERROR: {e}")

    time.sleep(3)

print("\n\nDone!")
