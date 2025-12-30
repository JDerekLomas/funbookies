"""
Character consistency system for Funbookies.
Ensures the same character appears across all pages.
"""

# Detailed character definitions with VERY specific visual descriptions
CHARACTERS = {
    "gus_gecko": {
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
        "style_ref": "simple flat cartoon style, bold outlines, minimal shading, bright saturated colors, Pixar-junior aesthetic"
    },

    "rita_rico_rats": {
        "name": "Rita and Rico",
        "species": "rats",
        "description": """Rita and Rico the rats: two small brown rats with:
- Rita: light brown fur, pink inner ears, small pink nose, wears tiny red bow on head
- Rico: darker brown fur, slightly bigger, small scar on left ear, wears tiny blue bandana
- Both have round black eyes with white highlights
- Long thin tails, small rounded ears
- Stand upright, about 4 inches tall
- Whiskers: 3 on each side
- Expressions shown through ears (up=happy, back=scared) and eyes""",
        "style_ref": "simple flat cartoon style, bold outlines, minimal shading, bright saturated colors, Pixar-junior aesthetic"
    },

    "zee_sloth": {
        "name": "Zee",
        "species": "sloth",
        "description": """Zee the sloth: a small three-toed sloth with:
- Round face with dark eye patches (like a mask)
- Big round black eyes with sleepy/happy expression
- Small black nose, gentle smile
- Shaggy tan/beige fur with greenish tinge
- Long arms with three curved claws each
- Moves slowly but always smiling
- About 2 feet long when stretched out
- Often hanging from branches by arms or curled up""",
        "style_ref": "simple flat cartoon style, bold outlines, minimal shading, bright saturated colors, Pixar-junior aesthetic"
    }
}

# Master style prompt - MUST be identical for every image
MASTER_STYLE = """children's book illustration, simple flat cartoon style, bold black outlines,
minimal shading, bright saturated colors, solid color backgrounds,
clean digital art, cute and friendly, age-appropriate for 6-7 year olds,
NO TEXT IN IMAGE, no words, no letters, no writing"""


def build_consistent_prompt(scene_description: str, character_key: str, include_character: bool = True) -> str:
    """
    Build a prompt that maintains character consistency.

    Args:
        scene_description: What's happening in the scene (e.g., "running up a grassy hill")
        character_key: Key from CHARACTERS dict
        include_character: Whether to include character in scene

    Returns:
        Full prompt with character reference and style
    """
    char = CHARACTERS.get(character_key, CHARACTERS["gus_gecko"])

    if include_character:
        prompt = f"""{char['description']}

SCENE: {char['name']} {scene_description}

STYLE: {MASTER_STYLE}, {char['style_ref']}"""
    else:
        # For pages without the main character (like word lists)
        prompt = f"""SCENE: {scene_description}

STYLE: {MASTER_STYLE}"""

    return prompt


def get_character_for_book(book_title: str) -> str:
    """Get the appropriate character key for a book title."""
    title_lower = book_title.lower()

    if "volcano" in title_lower or "gus" in title_lower:
        return "gus_gecko"
    elif "castle" in title_lower or "rat" in title_lower:
        return "rita_rico_rats"
    elif "jungle" in title_lower or "sloth" in title_lower or "zee" in title_lower:
        return "zee_sloth"
    else:
        return "gus_gecko"  # Default


# Page-specific prompts for volcano book with consistent character
VOLCANO_PAGES = [
    {"page": 1, "type": "cover", "scene": "standing proudly on a rocky hill with a smoking volcano in the background, looking excited and brave", "include_char": True},
    {"page": 2, "type": "wordlist", "scene": "decorative border with small volcanoes, lava drops, and tropical plants, no characters", "include_char": False},
    {"page": 3, "type": "story", "scene": "running eagerly up a grassy hill toward a distant volcano, tail curled with excitement", "include_char": True},
    {"page": 4, "type": "story", "scene": "climbing a steep rocky slope, looking determined, panting slightly", "include_char": True},
    {"page": 5, "type": "story", "scene": "peeking over the edge of a volcanic crater, eyes wide with wonder", "include_char": True},
    {"page": 6, "type": "story", "scene": "looking down into a big round crater hole, steam rising", "include_char": True},
    {"page": 7, "type": "story", "scene": "staring at a glowing red crater far below, orange glow reflecting on face", "include_char": True},
    {"page": 8, "type": "story", "scene": "seeing bright red bubbling lava for the first time, jaw dropped in amazement", "include_char": True},
    {"page": 9, "type": "story", "scene": "clapping tiny hands together with joy, big smile, standing at crater edge", "include_char": True},
    {"page": 10, "type": "story", "scene": "watching thick red magma slowly rising up in the crater", "include_char": True},
    {"page": 11, "type": "story", "scene": "jumping back startled as sparks and steam burst from the crater, POP sound effect shown", "include_char": True},
    {"page": 12, "type": "story", "scene": "turning around quickly with alarmed expression, about to run", "include_char": True},
    {"page": 13, "type": "story", "scene": "running fast down the volcano slope, legs blurred with speed, determined face", "include_char": True},
    {"page": 14, "type": "story", "scene": "in distance, lava dripping slowly over the crater rim behind", "include_char": True},
    {"page": 15, "type": "story", "scene": "close up of red lava drops hitting black rock, sizzling", "include_char": False},
    {"page": 16, "type": "story", "scene": "hopping away from a wave of heat, wiping brow, looking relieved", "include_char": True},
    {"page": 17, "type": "story", "scene": "hiding safely behind a large boulder, catching breath, volcano in background", "include_char": True},
    {"page": 18, "type": "story", "scene": "watching from safe distance as orange lava flows down the mountainside", "include_char": True},
    {"page": 19, "type": "story", "scene": "covering ears as the volcano rumbles loudly, sound waves shown", "include_char": True},
    {"page": 20, "type": "story", "scene": "standing tall and proud, chest puffed out, big grin", "include_char": True},
    {"page": 21, "type": "story", "scene": "shaking head 'no' with one hand up, sensible expression", "include_char": True},
    {"page": 22, "type": "story", "scene": "puffing out chest proudly, hands on hips, confident smile", "include_char": True},
    {"page": 23, "type": "story", "scene": "walking happily toward a sunset, tail swishing, content expression", "include_char": True},
    {"page": 24, "type": "copyright", "scene": "small waving goodbye in corner, simple background", "include_char": True},
]


if __name__ == "__main__":
    # Test prompt generation
    prompt = build_consistent_prompt(
        "running up a grassy hill toward a volcano",
        "gus_gecko"
    )
    print(prompt)
