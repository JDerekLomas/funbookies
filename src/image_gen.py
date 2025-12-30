"""
Image generation client for Funbookies.
Supports mulerouter (nano-banana-pro), and replicate backends.
"""

import os
import time
import httpx
import base64
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from config import IMAGE_DEFAULTS, PRINT_SPECS

load_dotenv()


class ImageGenerator:
    """Generate illustrations for minibooks using various AI backends."""

    def __init__(self, backend: str = "mulerouter"):
        self.backend = backend
        self.output_dir = Path("output/images")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # API configuration
        self.configs = {
            "mulerouter": {
                "api_key": os.getenv("MULEROUTER_API_KEY"),
                "base_url": os.getenv("MULEROUTER_BASE_URL", "https://api.mulerouter.ai"),
            },
            "replicate": {
                "api_key": os.getenv("REPLICATE_API_TOKEN"),
                "base_url": "https://api.replicate.com/v1",
            },
        }

    def generate(
        self,
        prompt: str,
        filename: str,
        style: Optional[str] = None,
        model: Optional[str] = None,
    ) -> str:
        """
        Generate an image and save it.

        Args:
            prompt: Description of the image to generate
            filename: Output filename (without extension)
            style: Style override (uses default if None)
            model: Model override (backend-specific)

        Returns:
            Path to the generated image
        """
        style = style or IMAGE_DEFAULTS["style"]
        full_prompt = f"{prompt}, {style}"

        if self.backend == "replicate":
            return self._generate_replicate(full_prompt, filename, model)
        else:
            return self._generate_mulerouter(full_prompt, filename, model)

    def _generate_mulerouter(self, prompt: str, filename: str, model: Optional[str]) -> str:
        """Generate using MuleRouter nano-banana-pro API."""
        config = self.configs["mulerouter"]

        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json",
        }

        # Use nano-banana-pro for image generation
        payload = {
            "prompt": prompt,
            "aspect_ratio": "1:1",  # Square for our 10x10cm format
            "resolution": "2K",
        }

        endpoint = f"{config['base_url']}/vendors/google/v1/nano-banana-pro/generation"

        with httpx.Client(timeout=300.0) as client:
            # Start generation task
            response = client.post(endpoint, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()

            # Handle task_info format
            if "task_info" in result:
                task_id = result["task_info"]["id"]
            elif "task_id" in result:
                task_id = result["task_id"]
            else:
                task_id = None

            # If we got a task_id, poll for completion
            if task_id:
                poll_url = f"{endpoint}/{task_id}"

                for _ in range(120):  # Poll for up to 2 minutes
                    time.sleep(2)
                    poll_response = client.get(poll_url, headers=headers)
                    poll_data = poll_response.json()

                    # Handle nested task_info format
                    if "task_info" in poll_data:
                        status = poll_data["task_info"].get("status", "")
                    else:
                        status = poll_data.get("status", "")

                    if status in ["completed", "succeeded"]:
                        result = poll_data
                        break
                    elif status == "failed":
                        raise Exception(f"Image generation failed: {poll_data}")
                    elif status == "pending" or status == "processing":
                        continue
                    else:
                        # Unknown status, keep polling
                        continue

            # Extract image URL and download
            output_path = self.output_dir / f"{filename}.png"

            # Handle different response formats
            img_url = None
            if "images" in result and result["images"]:
                img_url = result["images"][0]
            elif "output" in result:
                img_url = result["output"]
                if isinstance(img_url, list):
                    img_url = img_url[0]
            elif "url" in result:
                img_url = result["url"]
            elif "image_url" in result:
                img_url = result["image_url"]
            elif "data" in result:
                # Base64 encoded
                img_bytes = base64.b64decode(result["data"])
                output_path.write_bytes(img_bytes)
                return str(output_path)

            if not img_url:
                raise Exception(f"No image URL in response: {result}")

            # Download from URL
            img_response = client.get(img_url)
            output_path.write_bytes(img_response.content)

        return str(output_path)

    def _generate_replicate(self, prompt: str, filename: str, model: Optional[str]) -> str:
        """Generate using Replicate API."""
        config = self.configs["replicate"]
        model = model or "black-forest-labs/flux-schnell"

        headers = {
            "Authorization": f"Token {config['api_key']}",
            "Content-Type": "application/json",
        }

        payload = {
            "version": model,
            "input": {
                "prompt": prompt,
                "width": IMAGE_DEFAULTS["width"],
                "height": IMAGE_DEFAULTS["height"],
                "num_outputs": 1,
                "guidance_scale": 3.5,
                "num_inference_steps": 4,
            },
        }

        with httpx.Client(timeout=300.0) as client:
            response = client.post(
                f"{config['base_url']}/predictions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            prediction = response.json()

            # Poll for completion
            while prediction.get("status") in ["starting", "processing"]:
                time.sleep(1)
                response = client.get(
                    prediction["urls"]["get"],
                    headers=headers,
                )
                prediction = response.json()

            if prediction.get("status") == "succeeded":
                output_url = prediction["output"][0]
                img_response = client.get(output_url)
                output_path = self.output_dir / f"{filename}.png"
                output_path.write_bytes(img_response.content)
                return str(output_path)
            else:
                raise Exception(f"Image generation failed: {prediction.get('error')}")

    def generate_book_images(self, pages: list[dict]) -> list[str]:
        """
        Generate all images for a book.

        Args:
            pages: List of dicts with 'prompt' and 'filename' keys

        Returns:
            List of paths to generated images
        """
        paths = []
        for page in pages:
            try:
                path = self.generate(
                    prompt=page["prompt"],
                    filename=page["filename"],
                    style=page.get("style"),
                    model=page.get("model"),
                )
                paths.append(path)
                print(f"  Generated: {path}")
            except Exception as e:
                print(f"  Failed: {page['filename']} - {e}")
                paths.append(None)
        return paths


if __name__ == "__main__":
    gen = ImageGenerator(backend="mulerouter")

    test_prompt = "A friendly cartoon volcano with a smiling face, gentle lava, children's book illustration"
    path = gen.generate(test_prompt, "test_volcano")
    print(f"Test image saved to: {path}")
