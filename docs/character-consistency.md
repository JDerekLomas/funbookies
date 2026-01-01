# Character Consistency in AI Image Generation

Research notes for maintaining consistent characters across multiple images in children's book illustrations.

## The Problem

When generating AI images for children's books, each image generation is independent. Without special techniques, the same character prompt produces different-looking characters on every page - different body shapes, colors, facial features, and styles.

## Solutions by Platform

### Midjourney (Best Built-in Support)

Midjourney offers native character consistency features as of 2024.

#### `--cref` (Character Reference)
The primary tool for character consistency. Upload an image of your character, and Midjourney will maintain their appearance across new generations.

```
/imagine a girl running through a forest --cref https://example.com/my-character.png
```

**Best practices:**
- Generate your "hero" character image first in Midjourney
- Use that generated image as `--cref` for all subsequent images
- Works best with Midjourney-generated images (not photos)
- Simple clothing (solid colors) reproduces more reliably than patterns

#### `--cw` (Character Weight)
Controls how strictly Midjourney matches the reference.

| Value | Effect |
|-------|--------|
| `--cw 100` | Default. Matches face, hair, AND clothing |
| `--cw 50` | Moderate matching |
| `--cw 0` | Face only - useful for outfit changes |

```
/imagine a girl in a red dress at a party --cref URL --cw 0
```

#### `--sref` (Style Reference)
Maintains consistent art style across images. Can combine with `--cref`.

```
/imagine scene description --cref character.png --sref style.png
```

#### `--seed`
Same seed + similar prompt = similar results. Useful for minor variations.

```
/imagine a cartoon fox --seed 12345
```

#### V7: `--oref` (Omni Reference)
New in Midjourney V7 - enhanced character consistency.
- `--ow 0-50`: Subtle influence, keeps essence but allows style changes
- `--ow 400+`: Strong enforcement, close replication of features

**Sources:**
- [Midjourney Character Reference Docs](https://docs.midjourney.com/hc/en-us/articles/32162917505293-Character-Reference)
- [Tom's Guide: Midjourney Consistent Character](https://www.tomsguide.com/ai/ai-image-video/how-to-use-midjourneys-new-consistent-character-feature)

---

### Flux (Most Flexible via LoRA)

Flux doesn't have built-in character reference, but supports custom LoRA (Low-Rank Adaptation) models trained on your specific character.

#### What is a LoRA?
A small model trained on 20-40 images of a specific subject (character, style, concept). When applied to Flux, it "teaches" the model to generate that subject consistently.

#### Training Requirements
- **Images needed:** 20-40 high-quality images
- **Image specs:** 1024x1024, subject clearly visible and centered
- **Variety:** Different poses, angles, expressions, backgrounds
- **Hardware:** 8GB+ VRAM locally, or use cloud services

#### Training Tools

| Tool | Cost | Notes |
|------|------|-------|
| [FluxGym](https://learn.thinkdiffusion.com/make-your-character-style-lora-stand-out-easy-lora-training-with-fluxgym/) | Free (local) | Web UI, beginner-friendly |
| [fal.ai](https://fal.ai/models/fal-ai/flux-lora-fast-training) | ~$2-5 | Cloud training, fast |
| [Replicate](https://replicate.com) | ~$2-5 | Cloud training |
| [TheFluxTrain](https://thefluxtrain.com/) | Varies | 3-9 images, downloadable models |

#### Pre-made Children's Book LoRAs
- [Children's book illustration (Flux)](https://civitai.com/models/670727/childrens-book-illustration-flux) on Civitai
- Trigger word: `childrens_book_illustration`

#### Workflow
1. Generate 20-40 reference images of your character
2. Train LoRA (1 hour locally, minutes on cloud)
3. Use LoRA with trigger word in all prompts:
   ```
   my_character_lora, a small brown mouse with a red bow running through a castle
   ```

**Sources:**
- [Creating Consistent Characters Across Images](https://www.mayerdan.com/programming/2024/10/22/consistent-ai-book-characters)
- [Mickmumpitz: Consistent Characters with Flux](https://mickmumpitz.ai/guides/create-consistent-characters-for-your-projects-with-flux)

---

### Text-Only Approach (Our Current Method)

When using APIs without image reference support (like MuleRouter/nano-banana-pro), consistency relies entirely on detailed text prompts.

#### Character Definition Template
```python
CHARACTER = {
    "name": "Gus",
    "species": "gecko",
    "description": """Gus the gecko: a small bright lime-green gecko with:
- Round head with two large friendly black eyes with white highlights
- Small smile with no visible teeth
- Four stubby legs with tiny toe pads
- Long curled tail with darker green stripes
- Belly is lighter yellow-green
- About 6 inches long, cute and cartoonish
- Stands upright on hind legs like a cartoon character
- Expressions shown through eyes and body posture""",
    "style_ref": "simple flat cartoon style, bold outlines, minimal shading"
}
```

#### Master Style Prompt
Include identical style instructions in EVERY prompt:
```python
MASTER_STYLE = """children's book illustration, simple flat cartoon style,
bold black outlines, minimal shading, bright saturated colors,
solid color backgrounds, clean digital art, cute and friendly,
age-appropriate for 6-7 year olds, NO TEXT IN IMAGE"""
```

#### Prompt Structure
```
{CHARACTER_DESCRIPTION}

SCENE: {character_name} {scene_description}

STYLE: {MASTER_STYLE}, {character_style_ref}
```

#### Limitations
- Less reliable than image reference methods
- Character may drift between images
- Works better with simpler character designs
- Solid colors more consistent than patterns

---

### Specialized Services

#### ConsistentCharacter.ai
- Purpose-built for children's book illustration
- Handles character consistency automatically
- [consistentcharacter.ai](https://consistentcharacter.ai/)

#### Childbook.ai
- End-to-end children's book creation
- Claims consistent character generation
- [childbook.ai](https://www.childbook.ai/)

#### Phygital+
- Chain multiple AI models together
- Sketch to final image workflows
- [phygital.plus](https://phygital.plus/tools/ai-book-illustration-generator/)

---

## Best Practices (All Platforms)

### Character Design
1. **Keep it simple** - Solid colors, distinctive features
2. **Unique identifiers** - Rita's red bow, Rico's blue bandana
3. **Consistent proportions** - Define size relative to objects
4. **Limited color palette** - Easier to maintain

### Prompting
1. **Be specific** - "7-year-old boy with red curly hair" not "a boy"
2. **Include distinguishing features** - Accessories, scars, clothing
3. **Describe pose AND expression** - "running excitedly" not just "running"
4. **Avoid ambiguity** - One interpretation possible

### Quality Control
1. **Generate hero image first** - Establish the "canonical" look
2. **Review every generation** - Catch drift early
3. **Regenerate outliers** - Don't accept inconsistent images
4. **Post-process if needed** - Photoshop for color matching

### POV Shots
Mix character shots with POV (point-of-view) shots showing what the character sees:
- Reduces repetition of character in every frame
- Adds visual variety
- Builds immersion
- Easier to maintain consistency (no character to match!)

---

## Comparison Matrix

| Method | Consistency | Cost | Ease | Flexibility |
|--------|-------------|------|------|-------------|
| Midjourney `--cref` | ★★★★★ | $10-30/mo | ★★★★★ | ★★★★☆ |
| Flux + LoRA | ★★★★★ | $2-5/character | ★★★☆☆ | ★★★★★ |
| Text prompts only | ★★★☆☆ | Per-image | ★★★★★ | ★★★☆☆ |
| Specialized services | ★★★★☆ | Varies | ★★★★★ | ★★☆☆☆ |

---

## Recommendations for Funbookies

### Short-term (Current)
Continue with detailed text prompts via MuleRouter. Acceptable consistency with careful prompt engineering.

### Medium-term
Switch to Midjourney with `--cref` for new books. Better consistency, reasonable cost.

### Long-term
Train Flux LoRAs for recurring characters (Gus, Rita, Rico, Zee). One-time $2-5 investment per character, then unlimited consistent generations.

---

## References

- [Midjourney Character Reference Documentation](https://docs.midjourney.com/hc/en-us/articles/32162917505293-Character-Reference)
- [Creating Consistent Characters Across Images](https://www.mayerdan.com/programming/2024/10/22/consistent-ai-book-characters)
- [FluxGym LoRA Training Guide](https://learn.thinkdiffusion.com/make-your-character-style-lora-stand-out-easy-lora-training-with-fluxgym/)
- [Mickmumpitz: Consistent Characters with Flux](https://mickmumpitz.ai/guides/create-consistent-characters-for-your-projects-with-flux)
- [How to Illustrate a Children's Book with AI](https://kidsbookart.com/how-to-illustrate-a-childrens-book-with-ai/)
- [Civitai: Children's Book Illustration LoRA](https://civitai.com/models/670727/childrens-book-illustration-flux)
