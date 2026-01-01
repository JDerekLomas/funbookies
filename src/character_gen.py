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


# Page-specific prompts for volcano book - MIX of character shots and POV shots
# POV shots show what the character SEES (no character in frame)
# Character shots show the character doing something
VOLCANO_PAGES = [
    {"page": 1, "type": "cover", "scene": "standing proudly on a rocky hill with a smoking volcano in the background, looking excited and brave", "include_char": True},
    {"page": 2, "type": "wordlist", "scene": "decorative border with small volcanoes, lava drops, and tropical plants, no characters", "include_char": False},
    {"page": 3, "type": "story", "scene": "running eagerly up a grassy hill toward a distant volcano, tail curled with excitement", "include_char": True},
    {"page": 4, "type": "story", "scene": "POV looking up at a tall steep volcanic mountain with rocky path ahead, first-person perspective", "include_char": False},
    {"page": 5, "type": "story", "scene": "peeking over the edge of a volcanic crater, eyes wide with wonder, seen from behind", "include_char": True},
    {"page": 6, "type": "story", "scene": "POV looking down into a deep dark volcanic crater from the rim, steam rising up, dizzying depth", "include_char": False},
    {"page": 7, "type": "story", "scene": "POV view deep into crater showing glowing red magma far below, orange glow, heat waves", "include_char": False},
    {"page": 8, "type": "story", "scene": "POV close view of bright red bubbling lava, bubbles popping, intense orange-red glow", "include_char": False},
    {"page": 9, "type": "story", "scene": "clapping tiny hands together with joy, big smile, standing at crater edge", "include_char": True},
    {"page": 10, "type": "story", "scene": "POV looking at thick red magma slowly rising and bubbling up toward the viewer", "include_char": False},
    {"page": 11, "type": "story", "scene": "POV sparks and steam bursting upward from crater, bright orange explosions, dramatic", "include_char": False},
    {"page": 12, "type": "story", "scene": "turning around quickly with alarmed expression, about to run away", "include_char": True},
    {"page": 13, "type": "story", "scene": "running fast down the volcano slope, legs blurred with speed, determined face", "include_char": True},
    {"page": 14, "type": "story", "scene": "POV looking back up the slope as lava drips slowly over the crater rim above", "include_char": False},
    {"page": 15, "type": "story", "scene": "POV close up of red lava drops hitting black volcanic rock, sizzling steam", "include_char": False},
    {"page": 16, "type": "story", "scene": "hopping away from a wave of heat, wiping brow, looking relieved", "include_char": True},
    {"page": 17, "type": "story", "scene": "hiding safely behind a large boulder, peeking out, volcano erupting in background", "include_char": True},
    {"page": 18, "type": "story", "scene": "POV safe distance view of orange lava flowing down the mountainside, beautiful but dangerous", "include_char": False},
    {"page": 19, "type": "story", "scene": "standing tall and proud on a rock, chest puffed out, big grin, volcano behind", "include_char": True},
    {"page": 20, "type": "story", "scene": "proudly telling story with animated gestures, eyes bright with excitement", "include_char": True},
    {"page": 21, "type": "story", "scene": "puffing out chest proudly, hands on hips, confident heroic pose", "include_char": True},
    {"page": 22, "type": "story", "scene": "walking happily toward a sunset with volcano silhouette behind, content expression", "include_char": True},
    {"page": 23, "type": "copyright", "scene": "small waving goodbye in corner, simple background", "include_char": True},
]


# Page-specific prompts for castle book - Rita and Rico rats
CASTLE_PAGES = [
    {"page": 1, "type": "cover", "scene": "standing proudly in front of a grand medieval castle entrance, looking mischievous and excited", "include_char": True},
    {"page": 2, "type": "wordlist", "scene": "decorative border with castle elements, crowns, cheese, medieval flags", "include_char": False},
    {"page": 3, "type": "story", "scene": "sneaking through a crack in the castle wall, tails disappearing inside", "include_char": True},
    {"page": 4, "type": "story", "scene": "POV looking up at enormous castle hallway with tall stone columns and red carpet, grand and intimidating", "include_char": False},
    {"page": 5, "type": "story", "scene": "whispering to each other excitedly, Rita pointing toward the kitchen", "include_char": True},
    {"page": 6, "type": "story", "scene": "tiptoeing past a sleeping king on his throne, trying to be quiet", "include_char": True},
    {"page": 7, "type": "story", "scene": "tiptoeing past the queen who is reading a book, almost caught", "include_char": True},
    {"page": 8, "type": "story", "scene": "POV close-up of a beautiful jar of red jam on a kitchen shelf, glowing enticingly", "include_char": False},
    {"page": 9, "type": "story", "scene": "POV dramatic view of a large fluffy orange castle cat with piercing eyes blocking the path", "include_char": False},
    {"page": 10, "type": "story", "scene": "Rico shouting with alarm, pulling Rita by the paw to run", "include_char": True},
    {"page": 11, "type": "story", "scene": "running at full speed down a castle corridor, legs blurred with motion", "include_char": True},
    {"page": 12, "type": "story", "scene": "POV looking back at the cat chasing from behind, claws out, dramatic angle", "include_char": False},
    {"page": 13, "type": "story", "scene": "Rita diving headfirst into a fancy teacup to hide, only tail visible", "include_char": True},
    {"page": 14, "type": "story", "scene": "Rico hiding under a fancy hat on a table, peeking out nervously", "include_char": True},
    {"page": 15, "type": "story", "scene": "POV the cat sitting and waiting, looking around confused, can't find the rats", "include_char": False},
    {"page": 16, "type": "story", "scene": "Rita and Rico high-fiving each other, relieved and giggling", "include_char": True},
    {"page": 17, "type": "story", "scene": "happily eating jam together from the jar, jam on their faces, satisfied", "include_char": True},
    {"page": 18, "type": "copyright", "scene": "waving goodbye with jam-covered paws, happy ending", "include_char": True},
]


# Page-specific prompts for jungle book - Zee the sloth
JUNGLE_PAGES = [
    {"page": 1, "type": "cover", "scene": "hanging happily from a jungle vine with lush green leaves and colorful flowers around", "include_char": True},
    {"page": 2, "type": "wordlist", "scene": "decorative jungle border with vines, leaves, flowers, butterflies, no characters", "include_char": False},
    {"page": 3, "type": "story", "scene": "slowly waking up in a tree, stretching long arms, gentle smile", "include_char": True},
    {"page": 4, "type": "story", "scene": "POV looking up through jungle canopy at the bright sun peeking through leaves", "include_char": False},
    {"page": 5, "type": "story", "scene": "grinning happily at the jungle morning, arms stretched wide", "include_char": True},
    {"page": 6, "type": "story", "scene": "hanging from a thick vine with both arms, swinging gently", "include_char": True},
    {"page": 7, "type": "story", "scene": "hanging peacefully from vines, forest canopy all around", "include_char": True},
    {"page": 8, "type": "story", "scene": "POV swinging rapidly through jungle canopy, vines and leaves blurring past", "include_char": False},
    {"page": 9, "type": "story", "scene": "looking curious at a colorful tropical bird perched nearby", "include_char": True},
    {"page": 10, "type": "story", "scene": "POV close-up of a beautiful tropical bird with bright feathers and friendly eyes", "include_char": False},
    {"page": 11, "type": "story", "scene": "high-fiving the bird happily, both smiling", "include_char": True},
    {"page": 12, "type": "story", "scene": "running fast through jungle with bird flying beside", "include_char": True},
    {"page": 13, "type": "story", "scene": "climbing quickly up a tall tree trunk, bird above", "include_char": True},
    {"page": 14, "type": "story", "scene": "swinging down vines rapidly, moving with surprising speed", "include_char": True},
    {"page": 15, "type": "story", "scene": "POV colorful jungle flowers, fruits, and canopy leaves from high vantage point", "include_char": False},
    {"page": 16, "type": "story", "scene": "sitting contentedly on a branch with bird friend, sunset light", "include_char": True},
    {"page": 17, "type": "story", "scene": "smiling peacefully at sunset, surrounded by jungle beauty", "include_char": True},
    {"page": 18, "type": "copyright", "scene": "waving goodbye from a tree branch, peaceful expression", "include_char": True},
]


if __name__ == "__main__":
    # Test prompt generation
    prompt = build_consistent_prompt(
        "running up a grassy hill toward a volcano",
        "gus_gecko"
    )
    print(prompt)
