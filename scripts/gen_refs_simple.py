#!/usr/bin/env python3
"""Simple reference image generator using MuleRouter API directly."""

import os
import json
import time
import urllib.request
from pathlib import Path
from datetime import datetime
import requests
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / ".env")

BOOKS_DIR = PROJECT_ROOT / "public" / "books"
REFS_DIR = BOOKS_DIR / "references"

# MuleRouter config
MULEROUTER_API_KEY = os.getenv("MULEROUTER_API_KEY")
# Try different endpoints
MULERUN_BASE_URL = "https://api.mulerun.ai"
BASE_URL = "https://api.mulerouter.ai"
# Use mulerun which seems to be more stable
BASE_URL = MULERUN_BASE_URL


def generate_reference_image(slug: str) -> bool:
    """Generate a 9-panel reference image for a book."""

    book_path = BOOKS_DIR / f"{slug}.json"
    if not book_path.exists():
        print(f"  Book not found: {slug}")
        return False

    with open(book_path) as f:
        book = json.load(f)

    # Get reference prompt from book
    prompt = book.get("reference_prompt", "")
    if not prompt:
        print(f"  No reference_prompt in book JSON")
        return False

    title = book.get("title", slug)
    print(f"  Title: {title}")
    print(f"  Prompt preview: {prompt[:150]}...")

    output_path = REFS_DIR / f"{slug}_reference.png"

    # Call MuleRouter API
    headers = {
        "Authorization": f"Bearer {MULEROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    # Try wan2.6-t2i first (cheaper and good quality)
    endpoint = f"{BASE_URL}/vendors/alibaba/v1/wan2.6-t2i/generation"

    body = {
        "prompt": prompt,
        "size": "1024*1024",
        "n": 1
    }

    print(f"  Submitting to MuleRouter (wan2.6-t2i)...")

    try:
        response = requests.post(endpoint, json=body, headers=headers, timeout=120)
        print(f"  Response status: {response.status_code}")
        print(f"  Response: {response.text[:500]}")
        response.raise_for_status()
        result = response.json()

        # Task ID might be nested in task_info
        task_info = result.get("task_info", {})
        task_id = task_info.get("id") or result.get("id") or result.get("task_id") or result.get("request_id")
        print(f"  Task ID: {task_id}")

        # Poll for completion
        poll_endpoint = f"{BASE_URL}/vendors/alibaba/v1/wan2.6-t2i/generation/{task_id}"

        for _ in range(60):  # Max 5 minutes
            time.sleep(5)
            poll_response = requests.get(poll_endpoint, headers=headers, timeout=60)
            poll_response.raise_for_status()
            status = poll_response.json()

            # Status might be nested in task_info
            task_info = status.get("task_info", status)
            state = task_info.get("status") or status.get("status") or status.get("state")
            print(f"  Status: {state}")

            if state in ["completed", "COMPLETED", "succeeded", "SUCCESS", "success"]:
                # Images might be in various locations
                images = status.get("images") or status.get("output") or task_info.get("output") or status.get("result", {}).get("images") or []
                print(f"  Full response: {str(status)[:300]}...")
                if images:
                    url = images[0] if isinstance(images[0], str) else images[0].get("url")
                    print(f"  Generated: {url[:60]}...")

                    # Download image
                    REFS_DIR.mkdir(parents=True, exist_ok=True)
                    urllib.request.urlretrieve(url, output_path)
                    print(f"  Saved to: {output_path}")

                    # Update book JSON with metadata
                    book["reference_metadata"] = {
                        "generated_at": datetime.now().isoformat(),
                        "model": "wan2.6-t2i",
                        "provider": "mulerouter",
                    }
                    with open(book_path, 'w') as f:
                        json.dump(book, f, indent=2)

                    return True
                else:
                    print(f"  No images in response")
                    return False

            elif state in ["failed", "FAILED", "error", "ERROR"]:
                print(f"  Failed: {status.get('error', 'Unknown error')}")
                return False

        print(f"  Timeout waiting for generation")
        return False

    except Exception as e:
        print(f"  Error: {e}")
        return False


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--book", required=True, help="Book slug to generate reference for")
    args = parser.parse_args()

    print(f"\n[{args.book}]")
    success = generate_reference_image(args.book)
    print(f"\n{'✓ Success' if success else '✗ Failed'}")


if __name__ == "__main__":
    main()
