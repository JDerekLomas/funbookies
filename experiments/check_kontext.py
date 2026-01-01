#!/usr/bin/env python3
"""Check Kontext job status and download results."""

import requests

import os
FAL_API_KEY = os.environ.get("FAL_API_KEY", "")
headers = {"Authorization": f"Key {FAL_API_KEY}"}

request_ids = [
    ("8cbd5774-79f6-49fa-8795-e09d369ac01e", "scene02_running"),
    ("4cef6e91-7cc3-4d53-8cb7-3e363ad96437", "scene03_crater"),
]

output_dir = "experiments/images"

for request_id, scene in request_ids:
    print(f"\nChecking Kontext {scene}: {request_id}")

    try:
        status_url = f"https://queue.fal.run/fal-ai/flux-subject/requests/{request_id}/status"
        resp = requests.get(status_url, headers=headers, timeout=30)
        data = resp.json()
        status = data.get("status")
        print(f"  Status: {status}")

        if status == "COMPLETED":
            result_url = f"https://queue.fal.run/fal-ai/flux-subject/requests/{request_id}"
            result_resp = requests.get(result_url, headers=headers, timeout=30)
            result_data = result_resp.json()
            print(f"  Result keys: {list(result_data.keys())}")

            images = result_data.get("images", [])
            if not images:
                # Try alternative key
                images = result_data.get("image", [])
                if isinstance(images, dict):
                    images = [images]

            print(f"  Found {len(images)} images")

            if images:
                img_url = images[0].get("url") if isinstance(images[0], dict) else images[0]
                print(f"  Image URL: {img_url[:80]}...")

                img_resp = requests.get(img_url, timeout=60)
                output_path = f"{output_dir}/gus_v2_kontext_{scene}.png"
                with open(output_path, "wb") as f:
                    f.write(img_resp.content)
                print(f"  SAVED: {output_path}")
            else:
                print(f"  No images in response: {result_data}")
        elif status == "IN_QUEUE" or status == "IN_PROGRESS":
            print(f"  Still processing...")
    except Exception as e:
        print(f"  ERROR: {e}")
