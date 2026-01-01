# Character Consistency in AI Image Generation

Research notes for maintaining consistent characters across multiple images in children's book illustrations.

**Last Updated**: January 2026

---

## The Problem

When generating AI images for children's books, each image generation is independent. Without special techniques, the same character prompt produces different-looking characters on every page - different body shapes, colors, facial features, and styles.

---

## Solutions Comparison Matrix

| Method | Consistency | Cost | Ease | Best For |
|--------|-------------|------|------|----------|
| **Midjourney --cref** | ★★★★★ | $10-30/mo | ★★★★★ | Highest quality, Discord-based |
| **Flux Kontext** | ★★★★★ | $0.04/img | ★★★★☆ | API-first, no training needed |
| **Ideogram Character** | ★★★★★ | $0.08/img | ★★★★★ | Single reference image, API |
| **Flux + LoRA** | ★★★★★ | $2-5 train | ★★★☆☆ | Custom characters, unlimited use |
| **Text prompts only** | ★★★☆☆ | Per-image | ★★★★★ | Simple, works everywhere |

---

## Midjourney (Best Built-in Support)

Midjourney offers native character consistency features.

### `--cref` (Character Reference)

Upload an image of your character, and Midjourney maintains their appearance across new generations.

```
/imagine a girl running through a forest --cref https://example.com/my-character.png
```

### `--cw` (Character Weight)

Controls how strictly Midjourney matches the reference:

| Value | Effect |
|-------|--------|
| `--cw 100` | Default. Matches face, hair, AND clothing |
| `--cw 50` | Moderate matching |
| `--cw 0` | Face only - useful for outfit changes |

```
/imagine a girl in a red dress at a party --cref URL --cw 0
```

### `--sref` (Style Reference)

Maintains consistent art style across images. Use with `--cref` for both character AND style consistency.

```
/imagine scene description --cref character.png --sref style.png
```

### `--sw` (Style Weight)

Control style influence from 0-1000 (default 100):

```
/imagine a forest scene --sref style.png --sw 300
```

### Combined Usage

```
astronaut in dramatic action scene --cref [character-url] --cw 80 --sref [style-url] --sw 60 --v 6.1
```

**Best Practice**: Use `--cref` to keep the actor the same and `--sref` to keep the "camera" and art direction the same.

**Sources:**
- [Midjourney Character Reference Docs](https://docs.midjourney.com/hc/en-us/articles/32162917505293-Character-Reference)
- [Midjourney Style Reference Docs](https://docs.midjourney.com/hc/en-us/articles/32180011136653-Style-Reference)
- [ImaginePro Complete Guide](https://www.imaginepro.ai/blog/2025/7/midjourney-character-reference-guide)

---

## FLUX Kontext (Best API Option)

FLUX Kontext Pro is excellent for character consistency via API - no training required.

### Key Features

- **No Fine-tuning**: Works from a single reference image
- **Robust Consistency**: Multiple successive edits with minimal visual drift
- **Fast & Cheap**: Less than 1/4 the price of GPT-Image-1, fastest generation

### API Providers

| Provider | Model | Price | Link |
|----------|-------|-------|------|
| **fal.ai** | flux-pro/kontext | $0.04/img | [fal.ai/models/fal-ai/flux-pro/kontext](https://fal.ai/models/fal-ai/flux-pro/kontext) |
| **Replicate** | flux-kontext-pro | ~$0.03/img | [replicate.com/black-forest-labs/flux-kontext-pro](https://replicate.com/black-forest-labs/flux-kontext-pro) |

### Usage Pattern

```python
import fal_client

result = fal_client.subscribe(
    "fal-ai/flux-pro/kontext",
    arguments={
        "prompt": "Change the background to a volcanic landscape while keeping the character in the exact same position",
        "image_url": "https://example.com/character-reference.png"
    }
)
```

### Best Practices

> "Start with a clear reference (like 'the woman with short black hair') and say what's changing. If you want the same person to stick around, mention what to keep: face, expression, clothing."

For scene changes while maintaining character:
```
"Change the background to a beach while keeping the person in the exact same position, maintain identical subject placement, camera angle, framing, and perspective."
```

**Sources:**
- [Replicate: FLUX Kontext](https://replicate.com/blog/flux-kontext)
- [Replicate: Generate Consistent Characters](https://replicate.com/blog/generate-consistent-characters)
- [fal.ai Flux Kontext](https://fal.ai/models/fal-ai/flux-pro/kontext)

---

## FLUX.2 (Latest - Nov 2025)

FLUX.2 introduces multi-reference support - up to 4 reference images per generation.

### Key Improvements

- **4 Reference Images**: Fundamentally changes character consistency approach
- **Sub-second Generation**: Much faster than FLUX.1
- **Better Controllability**: Superior for product photography and brand assets

### API Access

| Provider | Model | Price |
|----------|-------|-------|
| **fal.ai** | flux-2/flex | $0.06/megapixel |
| **fal.ai** | flux-2/dev/lora | Custom LoRA support |

### Multi-Reference Usage

```python
result = fal_client.subscribe(
    "fal-ai/flux-2-flex/edit",
    arguments={
        "prompt": "Gus the gecko standing on a volcano",
        "reference_images": [
            "character_front.png",
            "character_side.png",
            "character_back.png"
        ]
    }
)
```

**Sources:**
- [fal.ai FLUX.2](https://fal.ai/flux-2)
- [FLUX.2 Developer Guide](https://fal.ai/learn/devs/flux-2-developer-guide)

---

## Ideogram Character (Easiest Single-Reference)

First character consistency model that works with just ONE reference image.

### Key Features

- **Single Image**: No need for multiple reference angles
- **Automatic Detection**: Facial and hair features detected automatically
- **Free Tier**: Available free on ideogram.ai

### API Operations

1. **Base Generation**: Create consistent images from single reference
2. **Edit**: Modify pose, expression, clothing while preserving identity
3. **Remix**: Transform into new artistic styles

### API Usage

```python
import requests

response = requests.post(
    "https://api.ideogram.ai/generate",
    headers={"Api-Key": "YOUR_KEY"},
    json={
        "prompt": "Gus the gecko on a volcano",
        "character_reference": "https://example.com/gus-reference.png"
    }
)
```

**Limitations**: Only 1 reference image (max 10MB), JPEG/PNG/WebP formats

**Sources:**
- [Ideogram Character Docs](https://docs.ideogram.ai/using-ideogram/features-and-tools/reference-features/character-reference)
- [Ideogram Character API on Replicate](https://replicate.com/ideogram-ai/ideogram-character)
- [The Decoder: Ideogram Character API](https://the-decoder.com/ideogram-now-lets-developers-create-characters-with-a-consistent-look-directly-through-its-api/)

---

## Flux + LoRA (Best for Recurring Characters)

Train a custom LoRA for characters that will appear in many books.

### What is LoRA?

A small model (typically 4-32MB) trained on 10-40 images of a specific subject. When applied to Flux, it "teaches" the model to generate that subject consistently.

### Training Requirements

| Requirement | Details |
|-------------|---------|
| **Images** | 10-30 diverse, high-res images |
| **Resolution** | 1024x1024, subject clearly visible |
| **Variety** | Different poses, angles, expressions |
| **Captions** | Proper descriptions for each image |

### Training Services

| Service | Cost | Speed | Notes |
|---------|------|-------|-------|
| [fal.ai](https://fal.ai/models/fal-ai/flux-lora-fast-training) | $2-5 | Minutes | Cloud, fast |
| [Replicate](https://replicate.com) | $2-5 | Minutes | Cloud |
| [FluxGym](https://learn.thinkdiffusion.com/make-your-character-style-lora-stand-out-easy-lora-training-with-fluxgym/) | Free | ~1 hour | Local, 8GB+ VRAM |

### Using Trained LoRA

```python
result = fal_client.subscribe(
    "fal-ai/flux-2/dev/lora",
    arguments={
        "prompt": "gus_gecko running up a volcanic hill",
        "loras": [{
            "path": "https://example.com/gus-lora.safetensors",
            "scale": 0.8
        }]
    }
)
```

### Pro Tips

- Flux is more forgiving than SD - requires fewer training images
- Use `network_dim` of 16-32 for good balance
- Simple, solid-color characters work best

**Sources:**
- [LoRA Training Best Practices 2025](https://apatero.com/blog/lora-training-best-practices-flux-stable-diffusion-2025)
- [fal.ai LoRA Training](https://fal.ai/models/fal-ai/flux-lora-fast-training)

---

## MuleRouter / Nano Banana Pro (Current Setup)

MuleRouter provides access to Nano Banana Pro for image generation.

### Current Capabilities

| Feature | Support |
|---------|---------|
| Text-to-Image | ✅ Yes |
| Image-to-Image | ✅ Yes |
| Character Reference | ❌ Not documented |
| Style Reference | ❌ Not documented |
| LoRA | ❌ Not documented |

### Workarounds for Character Consistency

Since MuleRouter doesn't have built-in character reference:

1. **Detailed Text Prompts**: Use very specific character descriptions
2. **Master Style Prompt**: Include identical style instructions in EVERY prompt
3. **POV Shots**: Mix character shots with first-person views (no character to match!)

### Current Character Prompt Template

```python
CHARACTER = """Gus the gecko: a small bright lime-green gecko with:
- Round head with two large friendly black eyes with white highlights
- Small smile with no visible teeth
- Four stubby legs with tiny toe pads
- Long curled tail with darker green stripes
- Belly is lighter yellow-green
- About 6 inches long, cute and cartoonish
- Stands upright on hind legs like a cartoon character"""

MASTER_STYLE = """children's book illustration, simple flat cartoon style,
bold black outlines, minimal shading, bright saturated colors,
solid color backgrounds, clean digital art, cute and friendly,
age-appropriate for 6-7 year olds, NO TEXT IN IMAGE"""

prompt = f"""{CHARACTER}

SCENE: Gus running up a grassy hill toward a volcano

STYLE: {MASTER_STYLE}"""
```

---

## Recommended Strategy for Funbookies

### Immediate (Current Books)

1. Continue with **detailed text prompts** via MuleRouter
2. Use **POV shots** for 40-50% of pages (no character to match)
3. Regenerate inconsistent images manually

### Short-term (Next Books)

1. Switch to **Flux Kontext** via fal.ai for character pages
   - $0.04/image, API-based
   - Generate "hero" reference image first
   - Use as reference for all subsequent pages

2. Or try **Ideogram Character** via Replicate
   - Single reference image
   - Even easier workflow

### Long-term (Recurring Characters)

1. **Train LoRAs** for Gus, Rita/Rico, Zee
   - One-time $2-5 per character
   - Unlimited consistent generations
   - Works across any Flux-based service

### Hybrid Workflow

```
1. Generate "hero" character image (front-facing, clear)
2. Use Flux Kontext for character pages (with hero as reference)
3. Use MuleRouter for POV pages (no character needed)
4. Review all images for consistency
5. Regenerate outliers with Kontext
```

---

## API Integration Options

### For Funbookies Skill

| Service | Character Ref | Style Ref | LoRA | Price | Recommendation |
|---------|--------------|-----------|------|-------|----------------|
| **fal.ai** | ✅ Kontext | ✅ | ✅ | $0.04+ | **Best overall** |
| **Replicate** | ✅ Kontext | ✅ | ✅ | $0.03+ | Good alternative |
| **Ideogram** | ✅ Native | ❌ | ❌ | $0.08 | Easiest setup |
| **MuleRouter** | ❌ | ❌ | ❌ | Varies | Current, limited |

### fal.ai Setup

```bash
pip install fal-client
export FAL_KEY="your-api-key"
```

```python
import fal_client

# Character-consistent generation
result = fal_client.subscribe(
    "fal-ai/flux-pro/kontext",
    arguments={
        "prompt": "Gus the gecko peeking into a volcanic crater, excited expression",
        "image_url": "https://funbookies.com/characters/gus-hero.png",
        "guidance_scale": 7.5
    }
)
print(result["images"][0]["url"])
```

---

## References

### Official Documentation
- [Midjourney Character Reference](https://docs.midjourney.com/hc/en-us/articles/32162917505293-Character-Reference)
- [Midjourney Style Reference](https://docs.midjourney.com/hc/en-us/articles/32180011136653-Style-Reference)
- [Ideogram Character Docs](https://docs.ideogram.ai/using-ideogram/features-and-tools/reference-features/character-reference)
- [fal.ai Flux Kontext](https://fal.ai/models/fal-ai/flux-pro/kontext)
- [fal.ai FLUX.2](https://fal.ai/flux-2)

### Tutorials & Guides
- [Replicate: Generate Consistent Characters](https://replicate.com/blog/generate-consistent-characters)
- [LoRA Training Best Practices 2025](https://apatero.com/blog/lora-training-best-practices-flux-stable-diffusion-2025)
- [Medium: Consistent AI Characters 2025](https://medium.com/design-bootcamp/how-to-design-consistent-ai-characters-with-prompts-diffusion-reference-control-2025-a1bf1757655d)

### API Platforms
- [fal.ai](https://fal.ai) - Recommended for Funbookies
- [Replicate](https://replicate.com) - Good alternative
- [Ideogram API](https://developer.ideogram.ai) - Easiest character ref
