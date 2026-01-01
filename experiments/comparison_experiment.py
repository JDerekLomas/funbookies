#!/usr/bin/env python3
"""Compare character consistency across models:
- Flux Kontext (fal.ai) - image reference
- Wan2.5 I2I (MuleRouter) - image-to-image
- Wan2.6 T2I (MuleRouter) - text only
- Nano Banana Pro (MuleRouter) - text only
"""

import os
import requests
import time
import json
from pathlib import Path
from datetime import datetime

OUTPUT_DIR = Path("experiments/images")
OUTPUT_DIR.mkdir(exist_ok=True)

# Reference image
REFERENCE_URL = "https://funbookies.vercel.app/experiments/images/gus_wan26_hero_1.png"

# API Keys
FAL_API_KEY = os.environ.get("FAL_API_KEY", "4249f047-fa0a-4f78-8c6e-8dc227a33bc3:48599b940122a72433d2d1d32616e1aa")
MULEROUTER_API_KEY = os.environ.get("MULEROUTER_API_KEY", "sk-mr-2dfbbdfe5bbd2e24235960b2d4f5b45bf1b59a087bc2524ff35c6c70a2657436")

# Character description for text-only models
CHARACTER = """A small bright lime-green gecko with big round friendly eyes with white sparkle highlights,
yellow-green belly, curled striped tail with darker green stripes, four stubby legs with tiny toe pads,
cute cartoonish style, standing upright on two legs, happy expression"""

STYLE = """children's book illustration, simple flat cartoon style, bold black outlines,
bright saturated colors, clean digital art, solid color background, no text"""

# Test scenes
SCENES = [
    ("volcano", "standing on a grassy hill looking at a distant smoking volcano, sunny day, blue sky"),
    ("running", "running excitedly up a rocky mountain slope, determined happy expression"),
    ("crater", "standing at the edge of a volcanic crater looking down with wonder, steam rising"),
]


def generate_flux_kontext(scene_name: str, scene_desc: str) -> dict:
    """Generate with Flux Kontext using image reference."""
    print(f"\n  [Flux Kontext] {scene_name}...")

    url = "https://queue.fal.run/fal-ai/flux-subject"
    headers = {
        "Authorization": f"Key {FAL_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"{CHARACTER}, {scene_desc}, {STYLE}"
    payload = {
        "prompt": prompt,
        "image_url": REFERENCE_URL,
        "image_size": "square",
        "num_inference_steps": 28,
        "guidance_scale": 3.5,
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        if response.status_code != 200:
            return {"success": False, "error": response.text}

        result = response.json()
        request_id = result.get("request_id")
        if not request_id:
            return {"success": False, "error": "No request_id"}

        # Poll for result
        for _ in range(90):
            time.sleep(2)
            status_url = f"https://queue.fal.run/fal-ai/flux-subject/requests/{request_id}/status"
            status_resp = requests.get(status_url, headers=headers, timeout=30)
            status = status_resp.json().get("status")

            if status == "COMPLETED":
                result_url = f"https://queue.fal.run/fal-ai/flux-subject/requests/{request_id}"
                result_resp = requests.get(result_url, headers=headers, timeout=30)
                images = result_resp.json().get("images", [])
                if images:
                    img_url = images[0].get("url")
                    img_resp = requests.get(img_url, timeout=60)
                    output_path = OUTPUT_DIR / f"cmp_kontext_{scene_name}.png"
                    with open(output_path, "wb") as f:
                        f.write(img_resp.content)
                    return {"success": True, "path": str(output_path)}
                break
            elif status in ("FAILED", "CANCELLED"):
                return {"success": False, "error": status}

        return {"success": False, "error": "Timeout"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def generate_wan25_i2i(scene_name: str, scene_desc: str) -> dict:
    """Generate with Wan2.5 I2I using image reference."""
    print(f"\n  [Wan2.5 I2I] {scene_name}...")

    url = "https://api.mulerouter.ai/vendors/alibaba/v1/wan2.5-i2i-preview/generation"
    headers = {
        "Authorization": f"Bearer {MULEROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    # For I2I, we provide the reference and ask to transform it into the scene
    prompt = f"Transform this gecko character into a new scene: {scene_desc}. Keep the exact same gecko character appearance - lime-green color, big eyes, curled tail. {STYLE}"

    payload = {
        "prompt": prompt,
        "images": [REFERENCE_URL],
        "size": "1024*1024",
        "n": 1,
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        if response.status_code != 200:
            return {"success": False, "error": response.text}

        result = response.json()
        # Handle different response structures
        task_id = result.get("task_id") or result.get("id")
        if not task_id and "task_info" in result:
            task_id = result["task_info"].get("id")
        if not task_id:
            # Maybe direct result
            images = result.get("images", [])
            if images:
                img_url = images[0] if isinstance(images[0], str) else images[0].get("url")
                img_resp = requests.get(img_url, timeout=60)
                output_path = OUTPUT_DIR / f"cmp_wan25i2i_{scene_name}.png"
                with open(output_path, "wb") as f:
                    f.write(img_resp.content)
                return {"success": True, "path": str(output_path)}
            return {"success": False, "error": f"No task_id or images: {str(result)[:100]}"}

        # Poll for result
        status_url = f"https://api.mulerouter.ai/vendors/alibaba/v1/wan2.5-i2i-preview/generation/{task_id}"
        for _ in range(60):
            time.sleep(5)
            status_resp = requests.get(status_url, headers=headers, timeout=30)
            status_data = status_resp.json()
            status = status_data.get("status", "unknown")

            if status == "completed":
                images = status_data.get("images", [])
                if images:
                    img_url = images[0] if isinstance(images[0], str) else images[0].get("url")
                    img_resp = requests.get(img_url, timeout=60)
                    output_path = OUTPUT_DIR / f"cmp_wan25i2i_{scene_name}.png"
                    with open(output_path, "wb") as f:
                        f.write(img_resp.content)
                    return {"success": True, "path": str(output_path)}
                break
            elif status == "failed":
                return {"success": False, "error": status_data.get("error", "Failed")}

        return {"success": False, "error": "Timeout"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def generate_wan26_t2i(scene_name: str, scene_desc: str) -> dict:
    """Generate with Wan2.6 T2I (text only)."""
    print(f"\n  [Wan2.6 T2I] {scene_name}...")

    url = "https://api.mulerouter.ai/vendors/alibaba/v1/wan2.6-t2i/generation"
    headers = {
        "Authorization": f"Bearer {MULEROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"{CHARACTER}, {scene_desc}, {STYLE}"
    payload = {
        "prompt": prompt,
        "size": "1024*1024",
        "n": 1,
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        if response.status_code != 200:
            return {"success": False, "error": response.text}

        result = response.json()
        task_id = result.get("task_id") or result.get("id")
        if not task_id and "task_info" in result:
            task_id = result["task_info"].get("id")
        if not task_id:
            return {"success": False, "error": f"No task_id: {str(result)[:100]}"}

        # Poll for result
        status_url = f"https://api.mulerouter.ai/vendors/alibaba/v1/wan2.6-t2i/generation/{task_id}"
        for _ in range(60):
            time.sleep(5)
            status_resp = requests.get(status_url, headers=headers, timeout=30)
            status_data = status_resp.json()
            status = status_data.get("status", "unknown")

            if status == "completed":
                images = status_data.get("images", [])
                if images:
                    img_url = images[0] if isinstance(images[0], str) else images[0].get("url")
                    img_resp = requests.get(img_url, timeout=60)
                    output_path = OUTPUT_DIR / f"cmp_wan26t2i_{scene_name}.png"
                    with open(output_path, "wb") as f:
                        f.write(img_resp.content)
                    return {"success": True, "path": str(output_path)}
                break
            elif status == "failed":
                return {"success": False, "error": status_data.get("error", "Failed")}

        return {"success": False, "error": "Timeout"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def generate_nano_banana(scene_name: str, scene_desc: str) -> dict:
    """Generate with Nano Banana Pro (text only)."""
    print(f"\n  [Nano Banana Pro] {scene_name}...")

    url = "https://api.mulerouter.ai/vendors/google/v1/nano-banana-pro/generation"
    headers = {
        "Authorization": f"Bearer {MULEROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"{CHARACTER}, {scene_desc}, {STYLE}"
    payload = {
        "prompt": prompt,
        "aspect_ratio": "1:1",
        "resolution": "1K",
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        if response.status_code != 200:
            return {"success": False, "error": response.text}

        result = response.json()
        task_id = result.get("task_id") or result.get("id")
        if not task_id and "task_info" in result:
            task_id = result["task_info"].get("id")
        if not task_id:
            return {"success": False, "error": f"No task_id: {str(result)[:100]}"}

        # Poll for result
        status_url = f"https://api.mulerouter.ai/vendors/google/v1/nano-banana-pro/generation/{task_id}"
        for _ in range(60):
            time.sleep(5)
            status_resp = requests.get(status_url, headers=headers, timeout=30)
            status_data = status_resp.json()
            status = status_data.get("status", "unknown")

            if status == "completed":
                images = status_data.get("images", [])
                if images:
                    img_url = images[0] if isinstance(images[0], str) else images[0].get("url")
                    img_resp = requests.get(img_url, timeout=60)
                    output_path = OUTPUT_DIR / f"cmp_nanobanana_{scene_name}.png"
                    with open(output_path, "wb") as f:
                        f.write(img_resp.content)
                    return {"success": True, "path": str(output_path)}
                break
            elif status == "failed":
                return {"success": False, "error": status_data.get("error", "Failed")}

        return {"success": False, "error": "Timeout"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def main():
    print("=" * 70)
    print("CHARACTER CONSISTENCY COMPARISON EXPERIMENT")
    print("=" * 70)
    print(f"Reference: {REFERENCE_URL}")
    print(f"Models: Flux Kontext, Wan2.5 I2I, Wan2.6 T2I, Nano Banana Pro")
    print("=" * 70)

    results = {
        "kontext": [],
        "wan25_i2i": [],
        "wan26_t2i": [],
        "nano_banana": [],
    }

    for scene_name, scene_desc in SCENES:
        print(f"\n{'='*70}")
        print(f"SCENE: {scene_name}")
        print(f"  {scene_desc}")
        print("=" * 70)

        # Test each model
        r = generate_flux_kontext(scene_name, scene_desc)
        results["kontext"].append({"scene": scene_name, **r})
        print(f"    Kontext: {'✓' if r['success'] else '✗ ' + r.get('error', '')[:50]}")

        time.sleep(2)

        r = generate_wan25_i2i(scene_name, scene_desc)
        results["wan25_i2i"].append({"scene": scene_name, **r})
        print(f"    Wan2.5 I2I: {'✓' if r['success'] else '✗ ' + r.get('error', '')[:50]}")

        time.sleep(2)

        r = generate_wan26_t2i(scene_name, scene_desc)
        results["wan26_t2i"].append({"scene": scene_name, **r})
        print(f"    Wan2.6 T2I: {'✓' if r['success'] else '✗ ' + r.get('error', '')[:50]}")

        time.sleep(2)

        r = generate_nano_banana(scene_name, scene_desc)
        results["nano_banana"].append({"scene": scene_name, **r})
        print(f"    Nano Banana: {'✓' if r['success'] else '✗ ' + r.get('error', '')[:50]}")

        time.sleep(3)

    # Summary
    print("\n" + "=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)

    for model, model_results in results.items():
        success_count = sum(1 for r in model_results if r.get("success"))
        print(f"\n{model}: {success_count}/{len(SCENES)}")
        for r in model_results:
            status = "✓" if r.get("success") else "✗"
            path = r.get("path", r.get("error", "")[:40])
            print(f"  {status} {r['scene']}: {path}")

    # Save results
    results_file = OUTPUT_DIR.parent / "comparison_results.json"
    with open(results_file, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "reference": REFERENCE_URL,
            "results": results,
        }, f, indent=2)
    print(f"\nResults saved to: {results_file}")


if __name__ == "__main__":
    main()
