"""
Character Consistency Experiment

Systematically test different approaches to maintaining character consistency
across multiple image generations for children's book illustrations.

Providers tested:
1. MuleRouter (Nano Banana Pro) - Text prompts only
2. MuleRouter (Midjourney) - --cref and --sref if available
3. fal.ai (Flux Kontext) - Character reference
4. fal.ai (Flux + LoRA) - Custom trained (future)
5. Replicate (Ideogram Character) - Single reference

Metrics:
- Visual consistency (manual review)
- Style consistency
- Cost per image
- Generation time
- API reliability
"""

import os
import json
import time
import httpx
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional, List
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Experiment output directory
EXPERIMENT_DIR = Path(__file__).parent.parent / "experiments"
EXPERIMENT_DIR.mkdir(exist_ok=True)


@dataclass
class ExperimentConfig:
    """Configuration for a character consistency experiment."""
    name: str
    character_name: str
    character_description: str
    style_prompt: str
    test_scenes: List[str]
    reference_image_url: Optional[str] = None


@dataclass
class GenerationResult:
    """Result of a single image generation."""
    provider: str
    model: str
    scene: str
    prompt: str
    image_path: Optional[str]
    generation_time_ms: int
    cost_estimate: float
    success: bool
    error: Optional[str] = None
    metadata: dict = None


# =============================================================================
# TEST CHARACTER: Gus the Gecko
# =============================================================================

GUS_EXPERIMENT = ExperimentConfig(
    name="gus_gecko_consistency",
    character_name="Gus",
    character_description="""Gus the gecko: a small bright lime-green gecko with:
- Round head with two large friendly black eyes with white highlights
- Small smile with no visible teeth
- Four stubby legs with tiny toe pads
- Long curled tail with darker green stripes
- Belly is lighter yellow-green
- About 6 inches long, cute and cartoonish
- Stands upright on hind legs like a cartoon character""",
    style_prompt="""children's book illustration, simple flat cartoon style,
bold black outlines, minimal shading, bright saturated colors,
solid color backgrounds, clean digital art, cute and friendly,
age-appropriate for 6-7 year olds, NO TEXT IN IMAGE""",
    test_scenes=[
        "standing proudly on a rocky hill with a smoking volcano in background",
        "running eagerly up a grassy hill toward a distant volcano",
        "peeking over the edge of a volcanic crater with wide eyes",
        "jumping back in surprise with alarmed expression",
        "walking happily toward a sunset, content and proud",
    ],
    reference_image_url=None  # Will be set after generating hero image
)


# =============================================================================
# PROVIDER: MuleRouter (Current)
# =============================================================================

class MuleRouterProvider:
    """MuleRouter API for image generation."""

    def __init__(self):
        self.api_key = os.getenv("MULEROUTER_API_KEY")
        self.base_url = "https://api.mulerouter.ai"

    def generate(self, prompt: str, filename: str, model: str = "nano-banana-pro") -> GenerationResult:
        """Generate image using MuleRouter."""
        start_time = time.time()

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        # Check if this is a Midjourney request
        if model.startswith("midjourney"):
            endpoint = f"{self.base_url}/v1/images/generations"
            payload = {
                "model": model,
                "prompt": prompt,
                "n": 1,
            }
        else:
            # Nano Banana Pro or Wan models
            endpoint = f"{self.base_url}/vendors/replicate/nano-banana/generations"
            payload = {
                "prompt": prompt,
                "aspect_ratio": "1:1",
                "output_format": "png",
            }

        try:
            with httpx.Client(timeout=120.0) as client:
                response = client.post(endpoint, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()

            # Handle async task polling if needed
            if "task_id" in data:
                image_url = self._poll_task(data["task_id"], headers)
            else:
                image_url = data.get("data", [{}])[0].get("url") or data.get("output", {}).get("url")

            # Download and save image
            if image_url:
                image_path = self._save_image(image_url, filename)
            else:
                image_path = None

            elapsed_ms = int((time.time() - start_time) * 1000)

            return GenerationResult(
                provider="mulerouter",
                model=model,
                scene=filename,
                prompt=prompt,
                image_path=str(image_path) if image_path else None,
                generation_time_ms=elapsed_ms,
                cost_estimate=0.02,  # Estimate
                success=image_path is not None,
                metadata={"response": data}
            )

        except Exception as e:
            elapsed_ms = int((time.time() - start_time) * 1000)
            return GenerationResult(
                provider="mulerouter",
                model=model,
                scene=filename,
                prompt=prompt,
                image_path=None,
                generation_time_ms=elapsed_ms,
                cost_estimate=0,
                success=False,
                error=str(e)
            )

    def _poll_task(self, task_id: str, headers: dict, max_attempts: int = 60) -> Optional[str]:
        """Poll for async task completion."""
        for _ in range(max_attempts):
            with httpx.Client(timeout=30.0) as client:
                response = client.get(
                    f"{self.base_url}/v1/tasks/{task_id}",
                    headers=headers
                )
                data = response.json()

            status = data.get("status")
            if status == "completed":
                return data.get("output", {}).get("url")
            elif status == "failed":
                raise Exception(f"Task failed: {data.get('error')}")

            time.sleep(2)

        raise Exception("Task polling timeout")

    def _save_image(self, url: str, filename: str) -> Path:
        """Download and save image."""
        output_dir = EXPERIMENT_DIR / "images"
        output_dir.mkdir(exist_ok=True)

        with httpx.Client() as client:
            response = client.get(url)
            response.raise_for_status()

        path = output_dir / f"{filename}.png"
        path.write_bytes(response.content)
        return path


# =============================================================================
# PROVIDER: fal.ai (Flux Kontext)
# =============================================================================

class FalProvider:
    """fal.ai API for Flux models with character reference."""

    def __init__(self):
        self.api_key = os.getenv("FAL_KEY")

    def generate_kontext(self, prompt: str, filename: str,
                         reference_image_url: Optional[str] = None) -> GenerationResult:
        """Generate image using Flux Kontext with optional character reference."""
        try:
            import fal_client
        except ImportError:
            return GenerationResult(
                provider="fal",
                model="flux-kontext",
                scene=filename,
                prompt=prompt,
                image_path=None,
                generation_time_ms=0,
                cost_estimate=0,
                success=False,
                error="fal_client not installed. Run: pip install fal-client"
            )

        start_time = time.time()

        try:
            args = {
                "prompt": prompt,
                "guidance_scale": 7.5,
            }

            if reference_image_url:
                args["image_url"] = reference_image_url
                model = "fal-ai/flux-pro/kontext"
            else:
                model = "fal-ai/flux/dev"

            result = fal_client.subscribe(model, arguments=args)

            # Get image URL from result
            image_url = result.get("images", [{}])[0].get("url")

            if image_url:
                image_path = self._save_image(image_url, filename)
            else:
                image_path = None

            elapsed_ms = int((time.time() - start_time) * 1000)

            return GenerationResult(
                provider="fal",
                model="flux-kontext" if reference_image_url else "flux-dev",
                scene=filename,
                prompt=prompt,
                image_path=str(image_path) if image_path else None,
                generation_time_ms=elapsed_ms,
                cost_estimate=0.04 if reference_image_url else 0.02,
                success=image_path is not None,
                metadata={"result": result}
            )

        except Exception as e:
            elapsed_ms = int((time.time() - start_time) * 1000)
            return GenerationResult(
                provider="fal",
                model="flux-kontext",
                scene=filename,
                prompt=prompt,
                image_path=None,
                generation_time_ms=elapsed_ms,
                cost_estimate=0,
                success=False,
                error=str(e)
            )

    def _save_image(self, url: str, filename: str) -> Path:
        """Download and save image."""
        output_dir = EXPERIMENT_DIR / "images"
        output_dir.mkdir(exist_ok=True)

        with httpx.Client() as client:
            response = client.get(url)
            response.raise_for_status()

        path = output_dir / f"{filename}.png"
        path.write_bytes(response.content)
        return path


# =============================================================================
# PROVIDER: Replicate (Ideogram Character)
# =============================================================================

class ReplicateProvider:
    """Replicate API for Ideogram Character."""

    def __init__(self):
        self.api_key = os.getenv("REPLICATE_API_TOKEN")
        self.base_url = "https://api.replicate.com/v1"

    def generate_ideogram(self, prompt: str, filename: str,
                          reference_image_url: Optional[str] = None) -> GenerationResult:
        """Generate image using Ideogram Character."""
        start_time = time.time()

        if not self.api_key:
            return GenerationResult(
                provider="replicate",
                model="ideogram-character",
                scene=filename,
                prompt=prompt,
                image_path=None,
                generation_time_ms=0,
                cost_estimate=0,
                success=False,
                error="REPLICATE_API_TOKEN not set"
            )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            # Use Ideogram Character model
            payload = {
                "version": "ideogram-ai/ideogram-character",
                "input": {
                    "prompt": prompt,
                }
            }

            if reference_image_url:
                payload["input"]["character_reference"] = reference_image_url

            with httpx.Client(timeout=120.0) as client:
                response = client.post(
                    f"{self.base_url}/predictions",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                prediction = response.json()

            # Poll for completion
            prediction_id = prediction["id"]
            image_url = self._poll_prediction(prediction_id, headers)

            if image_url:
                image_path = self._save_image(image_url, filename)
            else:
                image_path = None

            elapsed_ms = int((time.time() - start_time) * 1000)

            return GenerationResult(
                provider="replicate",
                model="ideogram-character",
                scene=filename,
                prompt=prompt,
                image_path=str(image_path) if image_path else None,
                generation_time_ms=elapsed_ms,
                cost_estimate=0.08,
                success=image_path is not None,
            )

        except Exception as e:
            elapsed_ms = int((time.time() - start_time) * 1000)
            return GenerationResult(
                provider="replicate",
                model="ideogram-character",
                scene=filename,
                prompt=prompt,
                image_path=None,
                generation_time_ms=elapsed_ms,
                cost_estimate=0,
                success=False,
                error=str(e)
            )

    def _poll_prediction(self, prediction_id: str, headers: dict) -> Optional[str]:
        """Poll for prediction completion."""
        for _ in range(120):
            with httpx.Client(timeout=30.0) as client:
                response = client.get(
                    f"{self.base_url}/predictions/{prediction_id}",
                    headers=headers
                )
                data = response.json()

            status = data.get("status")
            if status == "succeeded":
                output = data.get("output")
                if isinstance(output, list):
                    return output[0]
                return output
            elif status == "failed":
                raise Exception(f"Prediction failed: {data.get('error')}")

            time.sleep(2)

        raise Exception("Prediction polling timeout")

    def _save_image(self, url: str, filename: str) -> Path:
        """Download and save image."""
        output_dir = EXPERIMENT_DIR / "images"
        output_dir.mkdir(exist_ok=True)

        with httpx.Client() as client:
            response = client.get(url)
            response.raise_for_status()

        path = output_dir / f"{filename}.png"
        path.write_bytes(response.content)
        return path


# =============================================================================
# EXPERIMENT RUNNER
# =============================================================================

class CharacterExperiment:
    """Run character consistency experiments across providers."""

    def __init__(self, config: ExperimentConfig):
        self.config = config
        self.results: List[GenerationResult] = []
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Initialize providers
        self.mulerouter = MuleRouterProvider()
        self.fal = FalProvider()
        self.replicate = ReplicateProvider()

    def run_text_only_baseline(self):
        """Run baseline test with text prompts only (no reference images)."""
        print("\n=== TEXT-ONLY BASELINE (MuleRouter) ===\n")

        for i, scene in enumerate(self.config.test_scenes):
            prompt = f"""{self.config.character_description}

SCENE: {self.config.character_name} {scene}

STYLE: {self.config.style_prompt}"""

            filename = f"{self.config.name}_mulerouter_scene{i+1:02d}"
            print(f"Generating scene {i+1}: {scene[:50]}...")

            result = self.mulerouter.generate(prompt, filename)
            self.results.append(result)

            if result.success:
                print(f"  ✓ Saved: {result.image_path} ({result.generation_time_ms}ms)")
            else:
                print(f"  ✗ Failed: {result.error}")

            time.sleep(2)  # Rate limiting

    def run_fal_kontext(self, reference_url: Optional[str] = None):
        """Run test with Flux Kontext character reference."""
        print("\n=== FLUX KONTEXT (fal.ai) ===\n")

        if not os.getenv("FAL_KEY"):
            print("  ⚠ FAL_KEY not set. Skipping fal.ai tests.")
            return

        for i, scene in enumerate(self.config.test_scenes):
            if reference_url:
                # With reference: simpler prompt, let reference do the work
                prompt = f"{self.config.character_name} {scene}, {self.config.style_prompt}"
            else:
                # Without reference: full character description
                prompt = f"""{self.config.character_description}

SCENE: {self.config.character_name} {scene}

STYLE: {self.config.style_prompt}"""

            filename = f"{self.config.name}_fal_kontext_scene{i+1:02d}"
            print(f"Generating scene {i+1}: {scene[:50]}...")

            result = self.fal.generate_kontext(prompt, filename, reference_url)
            self.results.append(result)

            if result.success:
                print(f"  ✓ Saved: {result.image_path} ({result.generation_time_ms}ms)")
            else:
                print(f"  ✗ Failed: {result.error}")

            time.sleep(2)

    def run_ideogram_character(self, reference_url: Optional[str] = None):
        """Run test with Ideogram Character reference."""
        print("\n=== IDEOGRAM CHARACTER (Replicate) ===\n")

        if not os.getenv("REPLICATE_API_TOKEN"):
            print("  ⚠ REPLICATE_API_TOKEN not set. Skipping Ideogram tests.")
            return

        for i, scene in enumerate(self.config.test_scenes):
            prompt = f"{self.config.character_name} {scene}, {self.config.style_prompt}"
            filename = f"{self.config.name}_ideogram_scene{i+1:02d}"
            print(f"Generating scene {i+1}: {scene[:50]}...")

            result = self.replicate.generate_ideogram(prompt, filename, reference_url)
            self.results.append(result)

            if result.success:
                print(f"  ✓ Saved: {result.image_path} ({result.generation_time_ms}ms)")
            else:
                print(f"  ✗ Failed: {result.error}")

            time.sleep(2)

    def generate_hero_image(self) -> Optional[str]:
        """Generate a hero/reference image for character consistency tests."""
        print("\n=== GENERATING HERO IMAGE ===\n")

        prompt = f"""{self.config.character_description}

SCENE: {self.config.character_name} standing front-facing, looking at camera, clear full body view, simple background

STYLE: {self.config.style_prompt}"""

        filename = f"{self.config.name}_hero"
        print("Generating hero reference image...")

        result = self.mulerouter.generate(prompt, filename)

        if result.success:
            print(f"  ✓ Hero image saved: {result.image_path}")
            # For remote APIs, we'd need to upload this somewhere accessible
            # For now, return local path
            return result.image_path
        else:
            print(f"  ✗ Failed to generate hero image: {result.error}")
            return None

    def save_results(self):
        """Save experiment results to JSON."""
        output_path = EXPERIMENT_DIR / f"{self.config.name}_{self.timestamp}_results.json"

        data = {
            "config": asdict(self.config),
            "timestamp": self.timestamp,
            "results": [asdict(r) for r in self.results],
            "summary": self._compute_summary()
        }

        with open(output_path, "w") as f:
            json.dump(data, f, indent=2, default=str)

        print(f"\nResults saved to: {output_path}")
        return output_path

    def _compute_summary(self) -> dict:
        """Compute summary statistics."""
        by_provider = {}

        for result in self.results:
            key = f"{result.provider}/{result.model}"
            if key not in by_provider:
                by_provider[key] = {
                    "total": 0,
                    "success": 0,
                    "failed": 0,
                    "total_time_ms": 0,
                    "total_cost": 0,
                }

            by_provider[key]["total"] += 1
            if result.success:
                by_provider[key]["success"] += 1
                by_provider[key]["total_time_ms"] += result.generation_time_ms
                by_provider[key]["total_cost"] += result.cost_estimate
            else:
                by_provider[key]["failed"] += 1

        # Compute averages
        for key, stats in by_provider.items():
            if stats["success"] > 0:
                stats["avg_time_ms"] = stats["total_time_ms"] / stats["success"]
                stats["avg_cost"] = stats["total_cost"] / stats["success"]
            else:
                stats["avg_time_ms"] = 0
                stats["avg_cost"] = 0

        return by_provider

    def print_summary(self):
        """Print experiment summary."""
        summary = self._compute_summary()

        print("\n" + "=" * 60)
        print("EXPERIMENT SUMMARY")
        print("=" * 60)

        for provider, stats in summary.items():
            print(f"\n{provider}:")
            print(f"  Success: {stats['success']}/{stats['total']}")
            print(f"  Avg time: {stats['avg_time_ms']:.0f}ms")
            print(f"  Avg cost: ${stats['avg_cost']:.3f}")


def run_full_experiment():
    """Run the complete character consistency experiment."""
    print("=" * 60)
    print("CHARACTER CONSISTENCY EXPERIMENT")
    print("=" * 60)
    print(f"\nCharacter: {GUS_EXPERIMENT.character_name}")
    print(f"Scenes: {len(GUS_EXPERIMENT.test_scenes)}")

    experiment = CharacterExperiment(GUS_EXPERIMENT)

    # Phase 1: Text-only baseline
    experiment.run_text_only_baseline()

    # Phase 2: Generate hero image for reference-based tests
    hero_path = experiment.generate_hero_image()

    # For reference-based tests, we'd need the hero image accessible via URL
    # For local testing, we'll skip reference-based tests or use a placeholder
    hero_url = None  # Would need to upload to get URL

    # Phase 3: Flux Kontext (if FAL_KEY set)
    experiment.run_fal_kontext(hero_url)

    # Phase 4: Ideogram Character (if REPLICATE_API_TOKEN set)
    experiment.run_ideogram_character(hero_url)

    # Save and summarize
    experiment.save_results()
    experiment.print_summary()

    return experiment


def run_quick_test():
    """Run a quick test with just one scene per provider."""
    print("=" * 60)
    print("QUICK CHARACTER TEST (1 scene per provider)")
    print("=" * 60)

    config = ExperimentConfig(
        name="quick_test",
        character_name="Gus",
        character_description=GUS_EXPERIMENT.character_description,
        style_prompt=GUS_EXPERIMENT.style_prompt,
        test_scenes=["standing proudly on a volcanic crater rim, excited expression"],
    )

    experiment = CharacterExperiment(config)
    experiment.run_text_only_baseline()
    experiment.run_fal_kontext()
    experiment.run_ideogram_character()
    experiment.save_results()
    experiment.print_summary()

    return experiment


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        run_quick_test()
    else:
        run_full_experiment()
