#!/usr/bin/env python3
"""Multi-provider image generation client.

Unified interface for image generation across providers:

## fal.ai Models (FAL_KEY)
- wan2.6-image: $0.03/img - Style transfer, 1-3 refs
- flux-dev-i2i: $0.03/MP - Strength control
- flux-kontext-pro: $0.04/img - Natural language edits
- flux-kontext-max: $0.08/img - Premium quality
- gemini-2.5-flash: $0.039/img - Fast, 3 refs
- gemini-3-pro: $0.15/img - Best consistency, 14 refs
- z-image-turbo: $0.005/MP - Budget option

## Replicate Models (REPLICATE_API_TOKEN)
- flux-kontext-pro: $0.04/img
- flux-1.1-pro: $0.04/img
- ideogram-v3: $0.09/img

Usage:
    from fal_client import ImageClient
    client = ImageClient()
    result = client.generate_with_reference(
        prompt="A dog playing",
        reference_images=["ref.png"],
        model="wan2.6-image"
    )
"""

import os
import time
import base64
import requests
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Any
from dotenv import load_dotenv

# Load .env and .env.local from project root
PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / ".env")
load_dotenv(PROJECT_ROOT / ".env.local")


@dataclass
class ModelConfig:
    """Configuration for an image generation model."""
    endpoint: str
    provider: str  # fal, replicate, google
    price: float  # $ per image (or per MP for some)
    price_unit: str = "image"  # image, megapixel
    supports_i2i: bool = True
    max_refs: int = 1
    default_params: dict = field(default_factory=dict)
    description: str = ""


# All supported models with their configurations
MODELS = {
    # === fal.ai Models ===

    # Wan 2.6 - Best value for style transfer
    "wan2.6-image": ModelConfig(
        endpoint="wan/v2.6/image-to-image",
        provider="fal",
        price=0.03,
        supports_i2i=True,
        max_refs=3,
        default_params={
            "image_size": "square_hd",  # Must be preset: square_hd, square, portrait_4_3, etc.
            "enable_llm_prompt": True,  # Better results, +3-4s
        },
        description="Style transfer from 1-3 reference images"
    ),
    "wan2.6-t2i": ModelConfig(
        endpoint="wan/v2.6/text-to-image",
        provider="fal",
        price=0.03,
        supports_i2i=False,
        max_refs=0,
        description="Text-to-image only"
    ),

    # FLUX.1 [dev] - Good strength control
    "flux-dev-i2i": ModelConfig(
        endpoint="fal-ai/flux/dev/image-to-image",
        provider="fal",
        price=0.03,
        price_unit="megapixel",
        supports_i2i=True,
        max_refs=1,
        default_params={
            "strength": 0.85,
            "guidance_scale": 3.5,
            "num_inference_steps": 40,
        },
        description="Strength control 0.01-1.0, good prompt adherence"
    ),
    "flux-dev": ModelConfig(
        endpoint="fal-ai/flux/dev",
        provider="fal",
        price=0.025,
        price_unit="megapixel",
        supports_i2i=False,
        max_refs=0,
        description="High quality T2I"
    ),
    "flux-schnell": ModelConfig(
        endpoint="fal-ai/flux/schnell",
        provider="fal",
        price=0.003,
        supports_i2i=False,
        max_refs=0,
        description="Fast, cheap T2I"
    ),

    # FLUX Kontext - Natural language editing
    "flux-kontext-pro": ModelConfig(
        endpoint="fal-ai/flux-pro/kontext",
        provider="fal",
        price=0.04,
        supports_i2i=True,
        max_refs=1,
        default_params={
            "guidance_scale": 3.5,
            "num_inference_steps": 28,
        },
        description="Natural language edits, character consistency"
    ),
    "flux-kontext-max": ModelConfig(
        endpoint="fal-ai/flux-pro/kontext/max",
        provider="fal",
        price=0.08,
        supports_i2i=True,
        max_refs=3,  # Multi-image support
        default_params={
            "guidance_scale": 3.5,
        },
        description="Premium quality, best typography"
    ),
    "flux-kontext-dev": ModelConfig(
        endpoint="fal-ai/flux-kontext/dev",
        provider="fal",
        price=0.025,
        supports_i2i=True,
        max_refs=1,
        default_params={
            "guidance_scale": 2.5,
            "num_inference_steps": 28,
        },
        description="Cheaper Kontext variant"
    ),

    # Google Gemini via fal.ai
    "gemini-2.5-flash": ModelConfig(
        endpoint="fal-ai/gemini-2.5-flash-image-preview",
        provider="fal",
        price=0.039,
        supports_i2i=True,
        max_refs=3,
        default_params={
            "aspect_ratio": "1:1",
        },
        description="Fast, good free tier (Nano Banana)"
    ),
    "gemini-3-pro": ModelConfig(
        endpoint="fal-ai/gemini-3-pro-image-preview/edit",
        provider="fal",
        price=0.15,
        supports_i2i=True,
        max_refs=14,  # Best for character consistency!
        default_params={
            "resolution": "1K",
            "aspect_ratio": "1:1",
        },
        description="14 refs! Best character consistency (Nano Banana Pro)"
    ),

    # Nano Banana Pro direct
    "nano-banana-pro": ModelConfig(
        endpoint="fal-ai/nano-banana-pro",
        provider="fal",
        price=0.15,
        supports_i2i=False,
        max_refs=0,
        default_params={
            "resolution": "1K",
        },
        description="High quality T2I"
    ),
    "nano-banana-pro-edit": ModelConfig(
        endpoint="fal-ai/nano-banana-pro/edit",
        provider="fal",
        price=0.15,
        supports_i2i=True,
        max_refs=14,
        description="Same as gemini-3-pro"
    ),

    # Budget option
    "z-image-turbo": ModelConfig(
        endpoint="fal-ai/z-image/turbo/image-to-image",
        provider="fal",
        price=0.005,
        price_unit="megapixel",
        supports_i2i=True,
        max_refs=1,
        default_params={
            "num_inference_steps": 8,
        },
        description="Budget bulk generation, decent quality"
    ),

    # Recraft V3
    "recraft-v3": ModelConfig(
        endpoint="fal-ai/recraft/v3",
        provider="fal",
        price=0.04,
        supports_i2i=False,  # Style via presets, not refs
        max_refs=0,
        default_params={
            "style": "realistic_image",
        },
        description="Brand consistency, vector support ($0.08)"
    ),

    # === Replicate Models ===

    "replicate/flux-kontext-pro": ModelConfig(
        endpoint="black-forest-labs/flux-kontext-pro",
        provider="replicate",
        price=0.04,
        supports_i2i=True,
        max_refs=1,
        description="Same as fal Kontext Pro"
    ),
    "replicate/flux-1.1-pro": ModelConfig(
        endpoint="black-forest-labs/flux-1.1-pro",
        provider="replicate",
        price=0.04,
        supports_i2i=False,
        max_refs=0,
        description="High quality T2I"
    ),
    "replicate/ideogram-v3": ModelConfig(
        endpoint="ideogram-ai/ideogram-v3",
        provider="replicate",
        price=0.09,
        supports_i2i=True,
        max_refs=3,
        description="Best text rendering, style refs"
    ),
}


@dataclass
class GenerationResult:
    """Result from image generation."""
    url: Optional[str] = None
    error: Optional[str] = None
    request_id: Optional[str] = None
    model: Optional[str] = None
    cost: Optional[float] = None
    generation_time: Optional[float] = None

    @property
    def success(self) -> bool:
        return self.url is not None


class ImageClient:
    """Unified client for multiple image generation providers."""

    FAL_BASE_URL = "https://queue.fal.run"
    REPLICATE_BASE_URL = "https://api.replicate.com/v1"

    def __init__(
        self,
        fal_key: Optional[str] = None,
        replicate_token: Optional[str] = None,
    ):
        """Initialize with API keys from env or parameters."""
        self.fal_key = fal_key or os.getenv("FAL_KEY")
        self.replicate_token = replicate_token or os.getenv("REPLICATE_API_TOKEN")

        if not self.fal_key and not self.replicate_token:
            raise ValueError(
                "No API keys found. Set FAL_KEY or REPLICATE_API_TOKEN in .env\n"
                "Get keys at: https://fal.ai/dashboard/keys or https://replicate.com/account/api-tokens"
            )

    def list_models(self, i2i_only: bool = False) -> dict[str, ModelConfig]:
        """List available models with their configs."""
        models = MODELS.copy()
        if i2i_only:
            models = {k: v for k, v in models.items() if v.supports_i2i}
        return models

    def get_model_info(self, model: str) -> ModelConfig:
        """Get configuration for a model."""
        if model not in MODELS:
            raise ValueError(f"Unknown model: {model}. Available: {list(MODELS.keys())}")
        return MODELS[model]

    def _fal_headers(self) -> dict:
        """Get fal.ai request headers."""
        return {
            "Authorization": f"Key {self.fal_key}",
            "Content-Type": "application/json",
        }

    def _replicate_headers(self) -> dict:
        """Get Replicate request headers."""
        return {
            "Authorization": f"Bearer {self.replicate_token}",
            "Content-Type": "application/json",
        }

    def _image_to_data_url(self, image_path: Path) -> str:
        """Convert local image to data URL."""
        with open(image_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        ext = image_path.suffix.lower()
        mime = "image/png" if ext == ".png" else "image/jpeg"
        return f"data:{mime};base64,{b64}"

    def _prepare_references(self, reference_images: list) -> list[str]:
        """Convert reference images to URLs."""
        ref_urls = []
        for ref in reference_images:
            if isinstance(ref, Path) or (isinstance(ref, str) and not ref.startswith(("http", "data:"))):
                ref_urls.append(self._image_to_data_url(Path(ref)))
            else:
                ref_urls.append(ref)
        return ref_urls

    def _generate_fal(
        self,
        model: str,
        config: ModelConfig,
        body: dict,
        verbose: bool = False,
    ) -> GenerationResult:
        """Generate image using fal.ai."""
        start_time = time.time()

        try:
            # Submit request
            url = f"{self.FAL_BASE_URL}/{config.endpoint}"
            if verbose:
                print(f"  Submitting to fal.ai ({model})...")

            response = requests.post(url, json=body, headers=self._fal_headers())
            response.raise_for_status()
            submit_result = response.json()
            request_id = submit_result.get("request_id")

            if verbose:
                print(f"  Request ID: {request_id}")

            # Use URLs from response (fal.ai returns the correct paths)
            status_url = submit_result.get("status_url") or f"{self.FAL_BASE_URL}/{config.endpoint}/requests/{request_id}/status"
            result_url = submit_result.get("response_url") or f"{self.FAL_BASE_URL}/{config.endpoint}/requests/{request_id}"

            while time.time() - start_time < 300:
                status_response = requests.get(status_url, headers=self._fal_headers())
                status_response.raise_for_status()
                status = status_response.json()

                if status.get("status") == "COMPLETED":
                    result_response = requests.get(result_url, headers=self._fal_headers())
                    result_response.raise_for_status()
                    result = result_response.json()

                    images = result.get("images", [])
                    if images:
                        img_url = images[0].get("url") if isinstance(images[0], dict) else images[0]
                        if verbose:
                            print(f"  Generated: {img_url[:60]}...")
                        return GenerationResult(
                            url=img_url,
                            request_id=request_id,
                            model=model,
                            cost=config.price,
                            generation_time=time.time() - start_time,
                        )
                    return GenerationResult(error="No images in response", request_id=request_id, model=model)

                elif status.get("status") == "FAILED":
                    return GenerationResult(
                        error=status.get("error", "Generation failed"),
                        request_id=request_id,
                        model=model,
                    )

                time.sleep(2)

            return GenerationResult(error="Timeout after 300s", request_id=request_id, model=model)

        except requests.exceptions.RequestException as e:
            return GenerationResult(error=str(e), model=model)

    def _generate_replicate(
        self,
        model: str,
        config: ModelConfig,
        body: dict,
        verbose: bool = False,
    ) -> GenerationResult:
        """Generate image using Replicate."""
        start_time = time.time()

        try:
            # Create prediction
            url = f"{self.REPLICATE_BASE_URL}/predictions"
            payload = {
                "version": config.endpoint,
                "input": body,
            }

            if verbose:
                print(f"  Submitting to Replicate ({model})...")

            response = requests.post(url, json=payload, headers=self._replicate_headers())
            response.raise_for_status()
            prediction = response.json()
            prediction_id = prediction.get("id")

            if verbose:
                print(f"  Prediction ID: {prediction_id}")

            # Poll for result
            poll_url = f"{self.REPLICATE_BASE_URL}/predictions/{prediction_id}"

            while time.time() - start_time < 300:
                poll_response = requests.get(poll_url, headers=self._replicate_headers())
                poll_response.raise_for_status()
                status = poll_response.json()

                if status.get("status") == "succeeded":
                    output = status.get("output")
                    if output:
                        img_url = output[0] if isinstance(output, list) else output
                        if verbose:
                            print(f"  Generated: {img_url[:60]}...")
                        return GenerationResult(
                            url=img_url,
                            request_id=prediction_id,
                            model=model,
                            cost=config.price,
                            generation_time=time.time() - start_time,
                        )
                    return GenerationResult(error="No output", request_id=prediction_id, model=model)

                elif status.get("status") == "failed":
                    return GenerationResult(
                        error=status.get("error", "Generation failed"),
                        request_id=prediction_id,
                        model=model,
                    )

                time.sleep(2)

            return GenerationResult(error="Timeout after 300s", model=model)

        except requests.exceptions.RequestException as e:
            return GenerationResult(error=str(e), model=model)

    def generate_image(
        self,
        prompt: str,
        model: str = "nano-banana-pro",
        size: str = "1024x1024",
        verbose: bool = False,
        **kwargs,
    ) -> GenerationResult:
        """Generate an image from text prompt (T2I).

        Args:
            prompt: Text description of desired image
            model: Model to use (see list_models())
            size: Image size (1024x1024, square_hd, etc.)
            verbose: Print progress messages
            **kwargs: Model-specific parameters (guidance_scale, steps, etc.)

        Returns:
            GenerationResult with url or error
        """
        config = self.get_model_info(model)

        # Build request body with defaults
        body = {**config.default_params, **kwargs}
        body["prompt"] = prompt
        body["num_images"] = 1

        # Handle size parameter
        if "image_size" not in body:
            body["image_size"] = size

        # Route to provider
        if config.provider == "fal":
            return self._generate_fal(model, config, body, verbose)
        elif config.provider == "replicate":
            return self._generate_replicate(model, config, body, verbose)
        else:
            return GenerationResult(error=f"Unknown provider: {config.provider}", model=model)

    def generate_with_reference(
        self,
        prompt: str,
        reference_images: list[str | Path],
        model: str = "wan2.6-image",
        size: str = "1024x1024",
        strength: Optional[float] = None,
        guidance_scale: Optional[float] = None,
        verbose: bool = False,
        **kwargs,
    ) -> GenerationResult:
        """Generate an image using reference images for style transfer (I2I).

        Args:
            prompt: Description (for wan2.6, include "use style of image 1")
            reference_images: List of image URLs or local Paths
            model: Model to use (must support I2I)
            size: Output size
            strength: How much to transform (0.0-1.0, model-dependent)
            guidance_scale: Prompt adherence (model-dependent)
            verbose: Print progress messages
            **kwargs: Additional model-specific parameters

        Returns:
            GenerationResult with url or error
        """
        config = self.get_model_info(model)

        if not config.supports_i2i:
            return GenerationResult(
                error=f"Model {model} does not support I2I. Use: {[k for k, v in MODELS.items() if v.supports_i2i]}",
                model=model,
            )

        if len(reference_images) > config.max_refs:
            return GenerationResult(
                error=f"Model {model} supports max {config.max_refs} refs, got {len(reference_images)}",
                model=model,
            )

        # Prepare reference images
        ref_urls = self._prepare_references(reference_images)

        # Build request body
        body = {**config.default_params, **kwargs}
        body["num_images"] = 1

        # Model-specific parameter names
        if "wan" in model:
            body["prompt"] = prompt if "image 1" in prompt.lower() else f"Generate using style of image 1. {prompt}"
            body["image_urls"] = ref_urls  # wan2.6 uses image_urls, not reference_images
            # wan2.6 uses preset sizes, not dimensions - use default from config
        elif "flux" in model and "kontext" in model:
            body["prompt"] = prompt
            body["image_url"] = ref_urls[0]  # Single image
        elif "flux" in model and "i2i" in model:
            body["prompt"] = prompt
            body["image_url"] = ref_urls[0]
            if strength:
                body["strength"] = strength
        elif "gemini" in model or "nano-banana" in model:
            body["prompt"] = prompt
            body["image_urls"] = ref_urls
        elif "z-image" in model:
            body["prompt"] = prompt
            body["image_url"] = ref_urls[0]
        else:
            body["prompt"] = prompt
            body["image_urls"] = ref_urls  # Default to image_urls

        # Override with explicit params
        if strength is not None:
            body["strength"] = strength
        if guidance_scale is not None:
            body["guidance_scale"] = guidance_scale

        if verbose:
            print(f"  Using {len(ref_urls)} reference(s), model={model}")

        # Route to provider
        if config.provider == "fal":
            return self._generate_fal(model, config, body, verbose)
        elif config.provider == "replicate":
            return self._generate_replicate(model, config, body, verbose)
        else:
            return GenerationResult(error=f"Unknown provider: {config.provider}", model=model)


# === Convenience aliases ===
FalClient = ImageClient  # Backwards compatibility


def generate_text_to_image(prompt: str, model: str = "nano-banana-pro", **kwargs) -> str:
    """Quick T2I generation. Returns URL or raises error."""
    client = ImageClient()
    result = client.generate_image(prompt, model=model, **kwargs)
    if result.error:
        raise RuntimeError(result.error)
    return result.url


def generate_with_style_transfer(prompt: str, reference_path: Path, model: str = "wan2.6-image", **kwargs) -> str:
    """Quick style transfer. Returns URL or raises error."""
    client = ImageClient()
    result = client.generate_with_reference(prompt, [reference_path], model=model, **kwargs)
    if result.error:
        raise RuntimeError(result.error)
    return result.url


def build_character_consistent_prompt(
    scene: str,
    characters: dict[str, dict],
    style: str,
    reference_assignments: dict[str, int] | None = None,
) -> str:
    """Build a prompt optimized for character consistency.

    Best used with gemini-3-pro which supports 14 reference images.

    Args:
        scene: Scene description
        characters: Dict of {name: {visual_shorthand, distinctive_features}}
        style: Art style description
        reference_assignments: Optional {character_name: image_index} mapping

    Example:
        prompt = build_character_consistent_prompt(
            scene="Flicker flies over the moonlit pond",
            characters={
                "Flicker": {
                    "visual_shorthand": "tiny golden-green firefly with bright amber glow",
                    "distinctive_features": ["amber light (KEY)", "tiny size", "friendly expression"],
                }
            },
            style="warm watercolor, soft edges, children's book",
            reference_assignments={"Flicker": 1}  # Image 1 is Flicker's reference
        )
    """
    # Character block
    char_lines = []
    for name, data in characters.items():
        line = f"- {name}: {data.get('visual_shorthand', '')}"
        features = data.get("distinctive_features", [])
        if features:
            line += f" | MUST HAVE: {', '.join(features)}"
        if reference_assignments and name in reference_assignments:
            line += f" (see Image {reference_assignments[name]})"
        char_lines.append(line)

    char_block = "\n".join(char_lines)

    prompt = f"""{scene}

CHARACTERS (draw EXACTLY as shown in references):
{char_block}

STYLE: {style}

CRITICAL REQUIREMENTS:
- Characters MUST match their reference images exactly
- Maintain distinctive features in every frame
- NO TEXT, NO WORDS, NO LETTERS in the image"""

    return prompt


# === Reference Assignment Guide ===
# For Gemini 3 Pro / Nano Banana Pro (14 refs max)
# Recommended allocation for storybooks:
#
# Images 1-5: Character references (different poses/angles)
# Images 6-8: Object/prop references (recurring items)
# Images 9-11: Environment/setting references
# Images 12-14: Style references (color palette, mood)
#
# In prompts, refer to images by number:
# "Draw [Character] EXACTLY as shown in Image 1"
# "The house style should match Image 12"


if __name__ == "__main__":
    print("Image Generation Client")
    print("=" * 50)

    try:
        client = ImageClient()

        # List I2I models
        print("\nAvailable I2I Models:")
        print("-" * 50)
        for name, cfg in client.list_models(i2i_only=True).items():
            price_str = f"${cfg.price}/{cfg.price_unit}"
            print(f"  {name:25} {price_str:12} refs={cfg.max_refs}  {cfg.description}")

        print("\n" + "=" * 50)
        if client.fal_key:
            print(f"FAL_KEY: {client.fal_key[:12]}...")
        if client.replicate_token:
            print(f"REPLICATE_API_TOKEN: {client.replicate_token[:12]}...")

    except ValueError as e:
        print(f"Setup error: {e}")
