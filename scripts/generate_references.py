#!/usr/bin/env python3
"""Generate reference images for books based on their content.

Supports two strategies:
- single: One 9-panel reference sheet ($0.15)
- multi: Three specialized sheets using cascade approach ($0.21)
  1. characters.png - T2I nano-banana-pro ($0.15) - establishes the style
  2. settings.png - I2I wan2.6 with characters as ref ($0.03)
  3. style.png - I2I wan2.6 with characters as ref ($0.03)

Multi-ref strategy provides:
- Better character consistency (dedicated character sheet)
- No content contamination (style sheet has no story elements)
- Style consistency across all sheets (cascade from characters)

Saves generation metadata to book JSON.
"""

import sys
import os
import json
import urllib.request
from pathlib import Path
from datetime import datetime

# Setup paths relative to project root
from dotenv import load_dotenv
PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / ".env")
load_dotenv(PROJECT_ROOT / ".env.local")

# For MuleRouter fallback - configurable via env var
SKILL_DIR = Path(os.getenv("MULEROUTER_SKILL_DIR", str(Path.home() / ".claude/plugins/cache/mulerouter-skills/mulerouter-skills/1.0.0/skills/mulerouter-skills")))

# Import fal client
from fal_client import FalClient

# Import shared utilities
from image_utils import BOOKS_DIR, REFS_DIR, get_character_block

# Style templates based on reading level/band
STYLE_TEMPLATES = {
    "A": {
        "base": "Simple bold shapes, soft watercolor, very minimal detail, warm pastel colors, toddler-friendly illustration",
        "mood": "gentle, comforting, bright"
    },
    "B": {
        "base": "Playful watercolor illustration, expressive characters, vibrant colors, child-friendly art style",
        "mood": "energetic, fun, adventurous"
    },
    "C": {
        "base": "Rich watercolor illustration, more detailed characters and settings, dynamic compositions",
        "mood": "exciting, imaginative, engaging"
    },
    "D": {
        "base": "Sophisticated illustration style, detailed environments, nuanced lighting, chapter book aesthetic",
        "mood": "atmospheric, immersive, evocative"
    }
}

# Book-specific style overrides for unique themes
BOOK_STYLES = {
    "d1-the-lighthouse-keeper": "Coastal watercolor style, muted blues and warm sunset oranges, vintage seaside aesthetic, atmospheric lighting",
    "d2-the-hidden-garden": "Lush botanical illustration, secret garden aesthetic, dappled sunlight, rich greens and flower colors",
    "d3-the-architects-secret": "Architectural illustration style, warm browns and golds, mysterious shadows, historical building details",
    "d4-signals-from-kepler": "Science fiction illustration, deep space blues and purples, glowing technology, starfield backgrounds",
    "d5-the-winter-of-words": "Cozy winter illustration, soft whites and warm indoor lighting, snowy landscapes, bookish atmosphere",
    "d6-the-bridge-between": "Dreamlike illustration, soft gradients, bridge and connection imagery, ethereal lighting",
    "c1_knight_quest": "Medieval fantasy illustration, castle and forest settings, noble knights, warm golden lighting",
    "c2_magic_city": "Magical urban illustration, floating buildings, sparkles and wonder, vibrant fantasy colors",
    "c4_robot_pilot": "Retro sci-fi illustration, friendly robots, cockpit views, chrome and sky blue palette",
    "c6_biggest_race": "Dynamic sports illustration, motion blur effects, competitive energy, bright action colors",
    "c7_hopeless_garden": "Whimsical garden illustration, overgrown plants, determined characters, green and earth tones",
    "c8_impossible_invention": "Steampunk-lite illustration, gears and gadgets, inventor's workshop, brass and copper tones",
}


def get_book_info(slug: str) -> dict:
    """Load book JSON and extract key info."""
    book_path = BOOKS_DIR / f"{slug}.json"
    if not book_path.exists():
        return None

    with open(book_path) as f:
        book = json.load(f)

    # Get sample scenes (filter out None/empty)
    scenes = [p.get("scene") or p.get("text") or "" for p in book.get("pages", [])]
    scenes = [s for s in scenes if s][:9]

    # Extract visual style from story_bible if present
    story_bible = book.get("story_bible", {})
    visual_style = story_bible.get("visual_style", "")

    # Extract character descriptions for reference sheet
    characters = book.get("characters", {})
    character_blocks = []
    for char_key, char_data in characters.items():
        if isinstance(char_data, dict):
            # Use visual_shorthand if available, otherwise build from appearance
            shorthand = char_data.get("visual_shorthand", "")
            if shorthand:
                character_blocks.append(shorthand)
            elif char_data.get("appearance"):
                app = char_data["appearance"]
                name = char_data.get("name", char_key.capitalize())
                parts = [name + ":"]
                if app.get("body"):
                    parts.append(app["body"])
                if app.get("fur_color"):
                    parts.append(f"with {app['fur_color']} fur")
                if app.get("distinguishing_mark"):
                    parts.append(f"- {app['distinguishing_mark']} (key identifier)")
                if app.get("ears"):
                    parts.append(f"- {app['ears']}")
                if app.get("posture"):
                    parts.append(f"- {app['posture']}")
                character_blocks.append(" ".join(parts))

    return {
        "title": book.get("title", slug),
        "level": book.get("level", "B1"),
        "band": book.get("band", book.get("level", "B")[0]),
        "skill": book.get("skill") or book.get("targetPhonics", ""),
        "summary": book.get("summary", ""),
        "scenes": scenes,
        "visual_style": visual_style,
        "reference_prompt": book.get("reference_prompt", ""),  # Custom prompt if provided
        "character_blocks": character_blocks,  # For character consistency
    }


def build_reference_prompt(slug: str, book_info: dict) -> str:
    """Build a prompt for generating a 9-panel reference image."""

    band = book_info["band"]
    style_template = STYLE_TEMPLATES.get(band, STYLE_TEMPLATES["B"])

    # Priority for style: story_bible.visual_style > BOOK_STYLES > STYLE_TEMPLATES
    if book_info.get("visual_style"):
        book_style = book_info["visual_style"]
    else:
        book_style = BOOK_STYLES.get(slug, style_template["base"])

    # Build character section if we have character descriptions
    character_blocks = book_info.get("character_blocks", [])
    character_section = ""
    if character_blocks:
        character_section = f"""
CHARACTERS (draw EXACTLY as described - they must be visually distinct):

{chr(10).join(character_blocks)}
"""

    # Extract key visual elements from scenes
    scenes = book_info["scenes"][:9]

    # Build panel descriptions with CENTER (panel 5) as hero shot
    panel_descriptions = []

    if character_blocks:
        # Get character names for reference
        char_names = [cb.split(":")[0].strip() for cb in character_blocks[:2]]

        # Panel 1-2: Individual character studies
        for i, char_block in enumerate(character_blocks[:2]):
            char_name = char_block.split(":")[0].strip()
            panel_descriptions.append(f"Panel {i+1}: {char_name} alone - full body, distinguishing features clearly visible")

        # Panel 3-4: Settings from scenes
        for i, scene in enumerate(scenes[:2]):
            if scene:
                if len(scene) > 80:
                    scene = scene[:80] + "..."
                panel_descriptions.append(f"Panel {len(panel_descriptions)+1}: {scene}")
            else:
                panel_descriptions.append(f"Panel {len(panel_descriptions)+1}: Setting from {book_info['title']}")

        # Panel 5: CENTER HERO SHOT - all characters together
        if len(char_names) >= 2:
            panel_descriptions.append(f"Panel 5: **CENTER HERO SHOT** - {' and '.join(char_names)} TOGETHER, side by side, clear visual contrast between them. THE KEY IMAGE.")
        elif len(char_names) == 1:
            panel_descriptions.append(f"Panel 5: **CENTER HERO SHOT** - {char_names[0]} in heroic pose, all distinguishing features visible. THE KEY IMAGE.")
        else:
            panel_descriptions.append(f"Panel 5: **CENTER HERO SHOT** - Main character(s) together. THE KEY IMAGE.")

        # Panel 6: Another setting
        if len(scenes) > 2 and scenes[2]:
            scene = scenes[2][:80] + "..." if len(scenes[2]) > 80 else scenes[2]
            panel_descriptions.append(f"Panel 6: {scene}")
        else:
            panel_descriptions.append(f"Panel 6: Interior or location from {book_info['title']}")

        # Panel 7-9: Key moments from remaining scenes
        for i, scene in enumerate(scenes[3:6]):
            if scene:
                if len(scene) > 80:
                    scene = scene[:80] + "..."
                panel_descriptions.append(f"Panel {len(panel_descriptions)+1}: {scene}")

    else:
        # No characters - use scenes for all panels, but still emphasize panel 5
        for i, scene in enumerate(scenes[:4]):
            if scene:
                if len(scene) > 80:
                    scene = scene[:80] + "..."
                panel_descriptions.append(f"Panel {i+1}: {scene}")
            else:
                panel_descriptions.append(f"Panel {i+1}: Scene from {book_info['title']}")

        # Panel 5 still gets emphasis
        if len(scenes) > 4 and scenes[4]:
            panel_descriptions.append(f"Panel 5: **CENTER** - {scenes[4][:80]}...")
        else:
            panel_descriptions.append(f"Panel 5: **CENTER** - Key moment from {book_info['title']}")

        for i, scene in enumerate(scenes[5:9]):
            if scene:
                if len(scene) > 80:
                    scene = scene[:80] + "..."
                panel_descriptions.append(f"Panel {len(panel_descriptions)+1}: {scene}")

    # Pad to 9 panels if needed
    while len(panel_descriptions) < 9:
        panel_descriptions.append(f"Panel {len(panel_descriptions)+1}: Setting or mood detail")

    prompt = f"""9-PANEL REFERENCE SHEET for '{book_info['title']}'

Create a 3x3 grid. PANEL 5 (CENTER) is the HERO SHOT - most important!

Style: {book_style}
Mood: {style_template['mood']}
{character_section}
PANEL LAYOUT:
{chr(10).join(panel_descriptions[:9])}

Consistent art style across all panels. Each panel is a square vignette.

CRITICAL: NO TEXT, NO WORDS, NO LETTERS anywhere in the image. Pure illustration only."""

    return prompt


# =============================================================================
# MULTI-REF STRATEGY: 3 specialized reference sheets
# =============================================================================

def build_characters_prompt(slug: str, book_info: dict) -> str:
    """Build prompt for character reference sheet (multi-ref strategy)."""

    band = book_info["band"]
    style_template = STYLE_TEMPLATES.get(band, STYLE_TEMPLATES["B"])
    book_style = book_info.get("visual_style") or BOOK_STYLES.get(slug, style_template["base"])

    character_blocks = book_info.get("character_blocks", [])

    if not character_blocks:
        # No characters defined - create generic character sheet
        return f"""9-PANEL CHARACTER REFERENCE for '{book_info['title']}'

Create a 3x3 grid showing the main character(s) from different angles and expressions.

Row 1 - Views:
[1] Main character front view, full body, arms at sides, neutral expression
[2] Main character side profile, walking pose
[3] Main character 3/4 view, slight smile

Row 2 - Expressions:
[4] Main character happy, wide smile, eyes crinkled
[5] Main character sad or worried, downturned mouth
[6] Main character surprised, eyes wide, mouth O-shaped

Row 3 - Actions:
[7] Main character running, legs mid-stride, arms pumping
[8] Main character sitting, relaxed pose
[9] Main character in key action from story

CRITICAL: Same character design in ALL 9 panels. Consistent features throughout.
Style: {book_style}
Mood: {style_template['mood']}

NO TEXT, NO WORDS, NO LETTERS anywhere in the image."""

    # Build character-specific prompt
    char_names = [cb.split(":")[0].strip() for cb in character_blocks[:2]]
    main_char = char_names[0] if char_names else "Main character"
    main_desc = character_blocks[0] if character_blocks else ""

    if len(char_names) >= 2:
        # Two characters - split panels between them
        second_char = char_names[1]
        second_desc = character_blocks[1] if len(character_blocks) > 1 else ""

        prompt = f"""9-PANEL CHARACTER REFERENCE for '{book_info['title']}'

Create a 3x3 grid showing both main characters consistently.

CHARACTERS (draw EXACTLY as described):
{chr(10).join(character_blocks)}

Row 1 - {main_char}:
[1] {main_char} front view, full body, neutral expression - {main_desc}
[2] {main_char} side profile, walking pose
[3] {main_char} happy expression, wide smile

Row 2 - {second_char}:
[4] {second_char} front view, full body - {second_desc}
[5] {second_char} side profile
[6] {second_char} expression variation

Row 3 - Together & Actions:
[7] {main_char} and {second_char} side by side, size comparison (KEY PANEL)
[8] {main_char} in action pose
[9] {second_char} in action pose

CRITICAL: Each character must look IDENTICAL across all their panels.
Style: {book_style}

NO TEXT, NO WORDS, NO LETTERS anywhere in the image."""
    else:
        # Single character - full sheet dedicated to them
        prompt = f"""9-PANEL CHARACTER REFERENCE for '{book_info['title']}'

Create a 3x3 grid showing {main_char} from different angles and expressions.

CHARACTER (draw EXACTLY as described):
{main_desc}

Row 1 - Views:
[1] {main_char} front view, full body, arms at sides, neutral expression
[2] {main_char} side profile, walking pose
[3] {main_char} 3/4 view, slight turn

Row 2 - Expressions:
[4] {main_char} happy, wide smile, eyes crinkled, cheeks raised
[5] {main_char} sad or worried, downturned mouth, drooping posture
[6] {main_char} surprised, eyes wide open, mouth O-shaped

Row 3 - Actions:
[7] {main_char} running, legs mid-stride, arms pumping, body leaning forward
[8] {main_char} sitting, relaxed comfortable pose
[9] {main_char} with key prop or in key story pose

CRITICAL: {main_char} must look IDENTICAL in all 9 panels. Same features, proportions, colors.
Style: {book_style}

NO TEXT, NO WORDS, NO LETTERS anywhere in the image."""

    return prompt


def build_settings_prompt(slug: str, book_info: dict) -> str:
    """Build prompt for settings/environment reference sheet (multi-ref strategy)."""

    band = book_info["band"]
    style_template = STYLE_TEMPLATES.get(band, STYLE_TEMPLATES["B"])
    book_style = book_info.get("visual_style") or BOOK_STYLES.get(slug, style_template["base"])

    # Extract setting hints from scenes
    scenes = book_info.get("scenes", [])[:6]

    # Try to identify settings from story
    title = book_info.get("title", slug)

    prompt = f"""9-PANEL SETTINGS REFERENCE for '{title}'

Create a 3x3 grid showing environments and locations from the story.
NO CHARACTERS in any panel - settings only.

Row 1 - Main Location Exterior:
[1] Main story location, wide establishing shot, bright daylight
[2] Same location, golden hour sunset lighting, warm tones
[3] Same location, early morning or dusk, softer light

Row 2 - Interior / Secondary Locations:
[4] Interior space from story, warm inviting lighting
[5] Secondary location or different area, clear details
[6] Detail shot of important furniture, object, or architectural element

Row 3 - Atmosphere & Environment:
[7] Sky and weather typical of the story (sunny, cloudy, etc.)
[8] Nature elements: trees, grass, flowers, water - as relevant to story
[9] Mood/atmosphere shot capturing the feeling of the story world

CRITICAL: NO characters, NO people, NO animals in any panel.
Pure environments and settings only.
Consistent color palette and lighting style across all panels.

Style: {book_style}
Mood: {style_template['mood']}

NO TEXT, NO WORDS, NO LETTERS anywhere in the image."""

    return prompt


def build_style_prompt(slug: str, book_info: dict) -> str:
    """Build prompt for style/palette reference sheet (multi-ref strategy).

    This sheet contains NO story content - only abstract style elements.
    This prevents content contamination during page generation.
    """

    band = book_info["band"]
    style_template = STYLE_TEMPLATES.get(band, STYLE_TEMPLATES["B"])
    book_style = book_info.get("visual_style") or BOOK_STYLES.get(slug, style_template["base"])

    prompt = f"""9-PANEL STYLE REFERENCE - Abstract Color and Texture Samples

Create a 3x3 grid of ABSTRACT style samples. NO characters, NO scenes, NO story elements.

Row 1 - Color Palette:
[1] Primary color gradient swatch - main colors used in the art style
[2] Secondary/accent color swatches - complementary tones
[3] Neutral tones - backgrounds, shadows, highlights

Row 2 - Textures & Brushwork:
[4] Brush stroke texture sample - showing the painting technique
[5] Soft edge texture - how edges blend and feather
[6] Surface texture sample - paper grain, canvas feel

Row 3 - Lighting & Mood:
[7] Warm lighting color study - golden, cozy, inviting tones
[8] Cool lighting color study - blue, calm, peaceful tones
[9] Contrast study - light and shadow interplay

CRITICAL REQUIREMENTS:
- ABSTRACT ONLY - no recognizable objects, characters, or scenes
- Just color swatches, gradients, texture samples, and brushwork
- This establishes the visual style without any story content

Style to capture: {book_style}
Mood: {style_template['mood']}

NO TEXT, NO WORDS, NO LETTERS anywhere in the image."""

    return prompt


def generate_multi_refs_fal(slug: str, fal_client: FalClient) -> bool:
    """Generate 3 specialized reference sheets using fal.ai (multi-ref strategy).

    Uses a cascade approach for style consistency and lower cost:
    1. Characters sheet - nano-banana-pro T2I ($0.15) - establishes the style
    2. Settings sheet - wan2.6-image I2I with characters as ref ($0.03)
    3. Style sheet - wan2.6-image I2I with characters as ref ($0.03)

    Total: $0.21 instead of $0.45 with all T2I
    """

    book_info = get_book_info(slug)
    if not book_info:
        print(f"  Book not found: {slug}")
        return False

    # Create output directory
    multi_dir = REFS_DIR / f"{slug}_multi"
    multi_dir.mkdir(parents=True, exist_ok=True)

    print(f"  Title: {book_info['title']}")
    print(f"  Band: {book_info['band']}")
    print(f"  Output: {multi_dir}/")
    print(f"  Strategy: cascade (T2I -> I2I -> I2I)")

    results = {}
    characters_path = None
    total_cost = 0.0

    # Step 1: Generate characters sheet with T2I (establishes style)
    print(f"\n  [1/3 characters] - nano-banana-pro T2I ($0.15)")
    characters_path = multi_dir / f"{slug}_characters.png"
    prompt = build_characters_prompt(slug, book_info)
    print(f"    Prompt preview: {prompt[:100]}...")

    result = fal_client.generate_image(
        prompt=prompt,
        model="nano-banana-pro",
        size="square_hd",
        verbose=True,
    )

    if not result.success:
        print(f"    Failed: {result.error}")
        print(f"    Cannot continue without characters sheet")
        return False

    print(f"    Generated: {result.url[:60]}...")
    try:
        urllib.request.urlretrieve(result.url, characters_path)
        print(f"    Saved: {characters_path.name}")
        results["characters"] = {
            "path": str(characters_path.relative_to(REFS_DIR.parent.parent)),
            "prompt": prompt,
            "model": "nano-banana-pro",
            "generated_at": datetime.now().isoformat(),
        }
        total_cost += 0.15
    except Exception as e:
        print(f"    Download error: {e}")
        return False

    # Step 2 & 3: Generate settings and style with I2I using characters as reference
    i2i_sheets = [
        ("settings", build_settings_prompt),
        ("style", build_style_prompt),
    ]

    for idx, (sheet_name, prompt_builder) in enumerate(i2i_sheets, start=2):
        print(f"\n  [{idx}/3 {sheet_name}] - wan2.6-image I2I ($0.03)")
        output_path = multi_dir / f"{slug}_{sheet_name}.png"
        prompt = prompt_builder(slug, book_info)

        # Add style reference instruction for I2I
        prompt = f"Generate an image using the style of image 1.\n\n{prompt}"
        print(f"    Prompt preview: {prompt[:100]}...")
        print(f"    Reference: {characters_path.name}")

        result = fal_client.generate_with_reference(
            prompt=prompt,
            reference_images=[characters_path],
            model="wan2.6-image",
            size="1024x1024",
            verbose=True,
        )

        if result.success:
            print(f"    Generated: {result.url[:60]}...")
            try:
                urllib.request.urlretrieve(result.url, output_path)
                print(f"    Saved: {output_path.name}")
                results[sheet_name] = {
                    "path": str(output_path.relative_to(REFS_DIR.parent.parent)),
                    "prompt": prompt,
                    "model": "wan2.6-image",
                    "reference": "characters",
                    "generated_at": datetime.now().isoformat(),
                }
                total_cost += 0.03
            except Exception as e:
                print(f"    Download error: {e}")
        else:
            print(f"    Failed: {result.error}")

    success_count = len(results)

    # Save metadata to book JSON
    if success_count > 0:
        book_path = BOOKS_DIR / f"{slug}.json"
        with open(book_path) as f:
            book = json.load(f)

        book["multi_reference_metadata"] = {
            "strategy": "multi-3ref-cascade",
            "generated_at": datetime.now().isoformat(),
            "provider": "fal.ai",
            "cost": f"${total_cost:.2f}",
            "sheets": results,
        }

        with open(book_path, 'w') as f:
            json.dump(book, f, indent=2)

        print(f"\n  Metadata saved to book JSON")

    print(f"\n  Total cost: ${total_cost:.2f}")
    return success_count == 3


def generate_multi_refs_mulerouter(slug: str, config) -> bool:
    """Generate 3 specialized reference sheets using MuleRouter (multi-ref strategy).

    Uses same cascade approach as fal.ai version:
    1. Characters sheet - nano-banana-pro T2I ($0.15) - establishes the style
    2. Settings sheet - wan2.6-image I2I with characters as ref ($0.12)
    3. Style sheet - wan2.6-image I2I with characters as ref ($0.12)

    Total: $0.39 (more expensive than fal.ai's $0.21)
    """
    sys.path.insert(0, str(SKILL_DIR))
    load_dotenv(SKILL_DIR / ".env")
    from core import APIClient, create_and_poll_task

    book_info = get_book_info(slug)
    if not book_info:
        print(f"  Book not found: {slug}")
        return False

    # Create output directory
    multi_dir = REFS_DIR / f"{slug}_multi"
    multi_dir.mkdir(parents=True, exist_ok=True)

    print(f"  Title: {book_info['title']}")
    print(f"  Band: {book_info['band']}")
    print(f"  Output: {multi_dir}/")
    print(f"  Strategy: cascade (T2I -> I2I -> I2I)")

    results = {}
    characters_path = None
    total_cost = 0.0

    with APIClient(config) as client:
        # Step 1: Generate characters sheet with T2I (establishes style)
        print(f"\n  [1/3 characters] - nano-banana-pro T2I ($0.15)")
        characters_path = multi_dir / f"{slug}_characters.png"
        prompt = build_characters_prompt(slug, book_info)
        print(f"    Prompt preview: {prompt[:100]}...")

        body = {
            "prompt": prompt,
            "size": "1024*1024",
            "n": 1
        }

        result = create_and_poll_task(
            client=client,
            endpoint_path="/vendors/google/v1/nano-banana-pro/generation",
            request_body=body,
            result_key="images",
            interval=5.0,
            max_wait=300.0,
            verbose=True
        )

        if not result.results:
            print(f"    Failed: {result.error}")
            print(f"    Cannot continue without characters sheet")
            return False

        url = result.results[0]
        print(f"    Generated: {url[:60]}...")
        try:
            urllib.request.urlretrieve(url, characters_path)
            print(f"    Saved: {characters_path.name}")
            results["characters"] = {
                "path": str(characters_path.relative_to(REFS_DIR.parent.parent)),
                "prompt": prompt,
                "model": "nano-banana-pro",
                "generated_at": datetime.now().isoformat(),
            }
            total_cost += 0.15
        except Exception as e:
            print(f"    Download error: {e}")
            return False

        # Step 2 & 3: Generate settings and style with I2I using characters as reference
        i2i_sheets = [
            ("settings", build_settings_prompt),
            ("style", build_style_prompt),
        ]

        # Load reference image as base64 for I2I
        from image_utils import image_to_base64_uri
        ref_uri = image_to_base64_uri(characters_path)

        for idx, (sheet_name, prompt_builder) in enumerate(i2i_sheets, start=2):
            print(f"\n  [{idx}/3 {sheet_name}] - wan2.6-image I2I ($0.12)")
            output_path = multi_dir / f"{slug}_{sheet_name}.png"
            prompt = prompt_builder(slug, book_info)
            print(f"    Prompt preview: {prompt[:100]}...")
            print(f"    Reference: {characters_path.name}")

            body = {
                "prompt": prompt,
                "images": [ref_uri],
                "size": "1024*1024",
                "n": 1
            }

            result = create_and_poll_task(
                client=client,
                endpoint_path="/vendors/alibaba/v1/wan2.6-image/generation",
                request_body=body,
                result_key="images",
                interval=5.0,
                max_wait=300.0,
                verbose=True
            )

            if result.results:
                url = result.results[0]
                print(f"    Generated: {url[:60]}...")
                try:
                    urllib.request.urlretrieve(url, output_path)
                    print(f"    Saved: {output_path.name}")
                    results[sheet_name] = {
                        "path": str(output_path.relative_to(REFS_DIR.parent.parent)),
                        "prompt": prompt,
                        "model": "wan2.6-image",
                        "reference": "characters",
                        "generated_at": datetime.now().isoformat(),
                    }
                    total_cost += 0.12
                except Exception as e:
                    print(f"    Download error: {e}")
            else:
                print(f"    Failed: {result.error}")

    success_count = len(results)

    # Save metadata to book JSON
    if success_count > 0:
        book_path = BOOKS_DIR / f"{slug}.json"
        with open(book_path) as f:
            book = json.load(f)

        book["multi_reference_metadata"] = {
            "strategy": "multi-3ref-cascade",
            "generated_at": datetime.now().isoformat(),
            "provider": "mulerouter",
            "cost": f"${total_cost:.2f}",
            "sheets": results,
        }

        with open(book_path, 'w') as f:
            json.dump(book, f, indent=2)

        print(f"\n  Metadata saved to book JSON")

    print(f"\n  Total cost: ${total_cost:.2f}")
    return success_count == 3


def generate_reference_fal(slug: str, fal_client: FalClient) -> bool:
    """Generate a 9-panel reference image using fal.ai."""

    book_info = get_book_info(slug)
    if not book_info:
        print(f"  Book not found: {slug}")
        return False

    output_path = REFS_DIR / f"{slug}_reference.png"

    # Use custom reference_prompt from book JSON if provided, otherwise build one
    if book_info.get("reference_prompt"):
        prompt = book_info["reference_prompt"]
        print(f"  Using custom reference_prompt from book JSON")
    else:
        prompt = build_reference_prompt(slug, book_info)
        print(f"  Using auto-generated prompt")

    print(f"  Title: {book_info['title']}")
    print(f"  Band: {book_info['band']}")
    if book_info.get("visual_style"):
        print(f"  Style: {book_info['visual_style'][:60]}...")
    print(f"  Prompt preview: {prompt[:200]}...")

    model = "nano-banana-pro"

    # Generate using fal.ai
    result = fal_client.generate_image(
        prompt=prompt,
        model=model,
        size="square_hd",  # 1024x1024
        verbose=True,
    )

    if result.success:
        print(f"  Generated: {result.url[:60]}...")
        try:
            urllib.request.urlretrieve(result.url, output_path)
            print(f"  Saved to: {output_path}")

            # Save metadata to book JSON
            book_path = BOOKS_DIR / f"{slug}.json"
            with open(book_path) as f:
                book = json.load(f)

            book["reference_metadata"] = {
                "generated_at": datetime.now().isoformat(),
                "model": model,
                "provider": "fal.ai",
                "prompt": prompt,
                "output_path": str(output_path.relative_to(BOOKS_DIR.parent)),
                "cost": "$0.15",
            }

            with open(book_path, 'w') as f:
                json.dump(book, f, indent=2)

            print(f"  Metadata saved to book JSON")
            return True
        except Exception as e:
            print(f"  Download error: {e}")
            return False
    else:
        print(f"  Failed: {result.error}")
        return False


def generate_reference_mulerouter(slug: str, config) -> bool:
    """Generate a 9-panel reference image using MuleRouter (fallback)."""

    sys.path.insert(0, str(SKILL_DIR))
    load_dotenv(SKILL_DIR / ".env")
    from core import APIClient, create_and_poll_task

    book_info = get_book_info(slug)
    if not book_info:
        print(f"  Book not found: {slug}")
        return False

    output_path = REFS_DIR / f"{slug}_reference.png"

    # Use custom reference_prompt from book JSON if provided, otherwise build one
    if book_info.get("reference_prompt"):
        prompt = book_info["reference_prompt"]
        print(f"  Using custom reference_prompt from book JSON")
    else:
        prompt = build_reference_prompt(slug, book_info)
        print(f"  Using auto-generated prompt")

    print(f"  Title: {book_info['title']}")
    print(f"  Band: {book_info['band']}")
    if book_info.get("visual_style"):
        print(f"  Style: {book_info['visual_style'][:60]}...")
    print(f"  Prompt preview: {prompt[:200]}...")

    # Use nano-banana-pro for highest quality reference sheets
    model = "nano-banana-pro"

    # Use text-to-image for reference generation
    body = {
        "prompt": prompt,
        "size": "1024*1024",
        "n": 1
    }

    with APIClient(config) as client:
        result = create_and_poll_task(
            client=client,
            endpoint_path=f"/vendors/google/v1/{model}/generation",
            request_body=body,
            result_key="images",
            interval=5.0,
            max_wait=300.0,
            verbose=True
        )

        if result.results:
            url = result.results[0]
            print(f"  Generated: {url}")
            try:
                urllib.request.urlretrieve(url, output_path)
                print(f"  Saved to: {output_path}")

                # Save metadata to book JSON
                book_path = BOOKS_DIR / f"{slug}.json"
                with open(book_path) as f:
                    book = json.load(f)

                book["reference_metadata"] = {
                    "generated_at": datetime.now().isoformat(),
                    "model": model,
                    "provider": "mulerouter",
                    "prompt": prompt,
                    "output_path": str(output_path.relative_to(BOOKS_DIR.parent))
                }

                with open(book_path, 'w') as f:
                    json.dump(book, f, indent=2)

                print(f"  Metadata saved to book JSON")
                return True
            except Exception as e:
                print(f"  Download error: {e}")
                return False
        else:
            print(f"  Failed: {result.error}")
            return False


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate reference images for books")
    parser.add_argument("--book", help="Single book slug to generate")
    parser.add_argument("--all-missing", action="store_true", help="Generate for all books missing references")
    parser.add_argument("--force", action="store_true", help="Regenerate even if reference exists")
    parser.add_argument("--provider", choices=["fal", "mulerouter"], default="fal",
                        help="API provider (default: fal)")
    parser.add_argument("--strategy", choices=["single", "multi"], default="single",
                        help="Reference strategy: single (1 sheet) or multi (3 sheets)")
    args = parser.parse_args()

    if args.book:
        # Single book mode
        existing = [args.book]
        if not (BOOKS_DIR / f"{args.book}.json").exists():
            print(f"Book not found: {args.book}")
            return
        # Check if reference exists and --force not set
        if args.strategy == "single":
            ref_exists = (REFS_DIR / f"{args.book}_reference.png").exists()
        else:
            ref_exists = (REFS_DIR / f"{args.book}_multi").exists()
        if ref_exists and not args.force:
            print(f"Reference already exists for {args.book}. Use --force to regenerate.")
            return
    elif args.all_missing:
        # Find all books missing reference images
        all_books = [p.stem for p in BOOKS_DIR.glob("*.json") if p.stem != "manifest"]
        if args.strategy == "single":
            existing = [s for s in all_books if not (REFS_DIR / f"{s}_reference.png").exists()
                        and not (REFS_DIR / f"{s}_reference_v2.png").exists()
                        and not (REFS_DIR / f"{s}_reference_v3.png").exists()
                        and not (REFS_DIR / f"{s}_reference_v4.png").exists()]
        else:
            existing = [s for s in all_books if not (REFS_DIR / f"{s}_multi").exists()]
    else:
        print("Usage: python generate_references.py --book SLUG [--strategy single|multi]")
        print("       python generate_references.py --all-missing [--strategy single|multi]")
        print("")
        print("Strategies:")
        print("  --strategy single  One 9-panel sheet (default, $0.15)")
        print("  --strategy multi   Three specialized sheets ($0.21, cascade)")
        print("                     1. characters.png: T2I, establishes style")
        print("                     2. settings.png: I2I from characters")
        print("                     3. style.png: I2I from characters (no content)")
        print("")
        print("Options:")
        print("  --provider fal        Use fal.ai (default)")
        print("  --provider mulerouter Use MuleRouter")
        print("  --force               Regenerate even if exists")
        return

    print(f"Generating reference images for {len(existing)} books:")
    for s in existing:
        print(f"  - {s}")

    print(f"\nStrategy: {args.strategy}")
    print(f"Provider: {args.provider}")

    if args.strategy == "single":
        cost_per_book = 0.15
        print(f"Cost: $0.15 per book (1 T2I image)")
    else:
        if args.provider == "fal":
            cost_per_book = 0.21
            print(f"Cost: $0.21 per book (1 T2I + 2 I2I cascade)")
        else:
            cost_per_book = 0.39
            print(f"Cost: $0.39 per book (1 T2I + 2 I2I cascade, MuleRouter)")

    print(f"Estimated total: ${len(existing) * cost_per_book:.2f}")

    # Initialize client
    if args.provider == "fal":
        try:
            client = FalClient()
            print(f"API key: {client.fal_key[:8]}...")
        except ValueError as e:
            print(f"\nError: {e}")
            return
    else:
        sys.path.insert(0, str(SKILL_DIR))
        load_dotenv(SKILL_DIR / ".env")
        from core import load_config
        client = load_config()
        print(f"API: {client.site}")

    REFS_DIR.mkdir(parents=True, exist_ok=True)

    success = 0
    for slug in existing:
        print(f"\n[{slug}]")

        if args.strategy == "multi":
            # Multi-ref strategy: 3 specialized sheets
            if args.provider == "fal":
                if generate_multi_refs_fal(slug, client):
                    success += 1
            else:
                if generate_multi_refs_mulerouter(slug, client):
                    success += 1
        else:
            # Single strategy: one 9-panel sheet
            if args.provider == "fal":
                if generate_reference_fal(slug, client):
                    success += 1
            else:
                if generate_reference_mulerouter(slug, client):
                    success += 1

    print(f"\n\nDone! Generated {success}/{len(existing)} references.")
    print(f"Total cost: ~${success * cost_per_book:.2f}")


if __name__ == "__main__":
    main()
