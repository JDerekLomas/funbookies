#!/usr/bin/env python3
"""Consistency experiment v2 - Using Wan2.6 hero as reference."""

import os
import sys
import json
import base64
import requests
from pathlib import Path
from datetime import datetime

# Image output directory
OUTPUT_DIR = Path(__file__).parent / "images"
OUTPUT_DIR.mkdir(exist_ok=True)

# Reference image
REFERENCE_IMAGE = OUTPUT_DIR / "gus_wan26_reference.png"
REFERENCE_URL = "https://funbookies.vercel.app/experiments/images/gus_wan26_hero_1.png"

# Character description matching the Wan2.6 reference
CHARACTER = """A small bright lime-green gecko with big round friendly eyes with white sparkle highlights,
yellow-green belly, curled striped tail with darker green stripes, four stubby legs with tiny toe pads,
cute cartoonish style, standing upright on two legs, happy expression"""

STYLE = """children's book illustration, simple flat cartoon style, bold black outlines,
bright saturated colors, clean digital art, solid color background, no text"""

# Test scenes
SCENES = [
    ("scene01_volcano", "standing on a grassy hill looking at a distant smoking volcano, sunny day"),
    ("scene02_running", "running excitedly up a rocky mountain slope, determined expression"),
    ("scene03_crater", "standing at the edge of a volcanic crater, looking down with wonder, steam rising"),
]

# API Keys (from environment)
FAL_API_KEY = os.environ.get("FAL_API_KEY", "")
REPLICATE_API_KEY = os.environ.get("REPLICATE_API_TOKEN", "")


def image_to_data_url(image_path: Path) -> str:
    """Convert image to base64 data URL."""
    with open(image_path, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    return f"data:image/png;base64,{data}"


def generate_flux_kontext(prompt: str, reference_image: Path, output_path: Path) -> bool:
    """Generate image using Flux Kontext with character reference."""
    print(f"\n  Flux Kontext: {output_path.name}")

    # Convert reference to data URL
    image_data_url = image_to_data_url(reference_image)

    url = "https://queue.fal.run/fal-ai/flux-subject"
    headers = {
        "Authorization": f"Key {FAL_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "prompt": prompt,
        "subject_image_url": image_data_url,
        "image_size": "square",
        "num_inference_steps": 28,
        "guidance_scale": 3.5,
    }

    try:
        # Submit job
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()

        request_id = result.get("request_id")
        if not request_id:
            print(f"    ERROR: No request_id in response")
            return False

        print(f"    Submitted: {request_id}")

        # Poll for result
        status_url = f"https://queue.fal.run/fal-ai/flux-subject/requests/{request_id}/status"
        import time
        for _ in range(60):  # 2 minutes max
            time.sleep(2)
            status_resp = requests.get(status_url, headers=headers, timeout=30)
            status_data = status_resp.json()
            status = status_data.get("status")

            if status == "COMPLETED":
                # Get result
                result_url = f"https://queue.fal.run/fal-ai/flux-subject/requests/{request_id}"
                result_resp = requests.get(result_url, headers=headers, timeout=30)
                result_data = result_resp.json()

                images = result_data.get("images", [])
                if images:
                    img_url = images[0].get("url")
                    img_resp = requests.get(img_url, timeout=60)
                    with open(output_path, "wb") as f:
                        f.write(img_resp.content)
                    print(f"    SUCCESS: {output_path}")
                    return True
                break
            elif status in ("FAILED", "CANCELLED"):
                print(f"    FAILED: {status}")
                return False
            else:
                print(f"    Status: {status}...")

    except Exception as e:
        print(f"    ERROR: {e}")

    return False


def generate_replicate_flux_dev(prompt: str, output_path: Path) -> bool:
    """Generate image using Flux Dev on Replicate."""
    print(f"\n  Flux Dev: {output_path.name}")

    url = "https://api.replicate.com/v1/models/black-forest-labs/flux-dev/predictions"
    headers = {
        "Authorization": f"Bearer {REPLICATE_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "input": {
            "prompt": prompt,
            "aspect_ratio": "1:1",
            "output_format": "png",
            "output_quality": 90,
            "num_inference_steps": 28,
            "guidance": 3.5,
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()

        get_url = result.get("urls", {}).get("get")
        if not get_url:
            print(f"    ERROR: No get URL")
            return False

        print(f"    Submitted...")

        import time
        for _ in range(60):
            time.sleep(2)
            status_resp = requests.get(get_url, headers=headers, timeout=30)
            status_data = status_resp.json()
            status = status_data.get("status")

            if status == "succeeded":
                output = status_data.get("output")
                if output:
                    img_url = output[0] if isinstance(output, list) else output
                    img_resp = requests.get(img_url, timeout=60)
                    with open(output_path, "wb") as f:
                        f.write(img_resp.content)
                    print(f"    SUCCESS: {output_path}")
                    return True
                break
            elif status == "failed":
                print(f"    FAILED: {status_data.get('error')}")
                return False
            else:
                print(f"    Status: {status}...")

    except Exception as e:
        print(f"    ERROR: {e}")

    return False


def generate_replicate_flux_schnell(prompt: str, output_path: Path) -> bool:
    """Generate image using Flux Schnell on Replicate."""
    print(f"\n  Flux Schnell: {output_path.name}")

    url = "https://api.replicate.com/v1/models/black-forest-labs/flux-schnell/predictions"
    headers = {
        "Authorization": f"Bearer {REPLICATE_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "input": {
            "prompt": prompt,
            "aspect_ratio": "1:1",
            "output_format": "png",
            "num_inference_steps": 4,
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()

        get_url = result.get("urls", {}).get("get")
        if not get_url:
            print(f"    ERROR: No get URL")
            return False

        print(f"    Submitted...")

        import time
        for _ in range(30):
            time.sleep(2)
            status_resp = requests.get(get_url, headers=headers, timeout=30)
            status_data = status_resp.json()
            status = status_data.get("status")

            if status == "succeeded":
                output = status_data.get("output")
                if output:
                    img_url = output[0] if isinstance(output, list) else output
                    img_resp = requests.get(img_url, timeout=60)
                    with open(output_path, "wb") as f:
                        f.write(img_resp.content)
                    print(f"    SUCCESS: {output_path}")
                    return True
                break
            elif status == "failed":
                print(f"    FAILED: {status_data.get('error')}")
                return False
            else:
                print(f"    Status: {status}...")

    except Exception as e:
        print(f"    ERROR: {e}")

    return False


def main():
    print("=" * 60)
    print("CHARACTER CONSISTENCY EXPERIMENT v2")
    print(f"Reference: {REFERENCE_IMAGE}")
    print("=" * 60)

    results = {"kontext": [], "flux_dev": [], "flux_schnell": []}

    for scene_name, scene_desc in SCENES:
        print(f"\n{'='*60}")
        print(f"SCENE: {scene_name}")
        print(f"  {scene_desc}")
        print("=" * 60)

        # Full prompt with character and style
        full_prompt = f"{CHARACTER}, {scene_desc}, {STYLE}"

        # Test Flux Kontext (with image reference)
        kontext_path = OUTPUT_DIR / f"gus_v2_kontext_{scene_name}.png"
        if generate_flux_kontext(full_prompt, REFERENCE_IMAGE, kontext_path):
            results["kontext"].append(str(kontext_path))

        import time
        time.sleep(3)  # Rate limiting

        # Test Flux Dev (text only)
        dev_path = OUTPUT_DIR / f"gus_v2_fluxdev_{scene_name}.png"
        if generate_replicate_flux_dev(full_prompt, dev_path):
            results["flux_dev"].append(str(dev_path))

        time.sleep(12)  # Replicate rate limiting

        # Test Flux Schnell (text only)
        schnell_path = OUTPUT_DIR / f"gus_v2_schnell_{scene_name}.png"
        if generate_replicate_flux_schnell(full_prompt, schnell_path):
            results["flux_schnell"].append(str(schnell_path))

        time.sleep(12)  # Replicate rate limiting

    print("\n" + "=" * 60)
    print("EXPERIMENT COMPLETE")
    print("=" * 60)

    for model, paths in results.items():
        print(f"\n{model}: {len(paths)}/{len(SCENES)} successful")
        for p in paths:
            print(f"  - {Path(p).name}")

    # Save results
    results_file = OUTPUT_DIR.parent / "consistency_v2_results.json"
    with open(results_file, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "reference": str(REFERENCE_IMAGE),
            "results": results
        }, f, indent=2)
    print(f"\nResults saved to: {results_file}")


if __name__ == "__main__":
    main()
