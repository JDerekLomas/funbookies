"""
Story Generator Configurations

Model configurations for A/B testing different LLM combinations
in the Generator → Critic → Editor pipeline.
"""

from dataclasses import dataclass, field
from typing import Optional
import os

# =============================================================================
# MODEL DEFINITIONS
# =============================================================================

@dataclass
class ModelConfig:
    """Configuration for a single model."""
    provider: str  # "google", "anthropic", "openai"
    model_id: str
    temperature: float = 0.7
    max_tokens: int = 2000


# Available models
MODELS = {
    # Google Gemini
    "gemini-3-flash": ModelConfig("google", "gemini-3-flash-preview", temperature=0.7),
    "gemini-2.5-flash": ModelConfig("google", "gemini-2.5-flash", temperature=0.7),
    "gemini-3-pro": ModelConfig("google", "gemini-3-pro", temperature=0.7),

    # Anthropic Claude
    "claude-opus": ModelConfig("anthropic", "claude-opus-4-5-20251101", temperature=0.7),
    "claude-sonnet": ModelConfig("anthropic", "claude-sonnet-4-20250514", temperature=0.7),
    "claude-haiku": ModelConfig("anthropic", "claude-3-5-haiku-20241022", temperature=0.7),

    # OpenAI (if available)
    "gpt-4o": ModelConfig("openai", "gpt-4o", temperature=0.7),
    "gpt-4-turbo": ModelConfig("openai", "gpt-4-turbo", temperature=0.7),
}


# =============================================================================
# PIPELINE CONFIGURATIONS (for A/B testing)
# =============================================================================

@dataclass
class PipelineConfig:
    """Configuration for the full Generator → Critic → Editor pipeline."""
    name: str
    description: str
    generator: str  # key from MODELS
    critic: str
    editor: str

    def get_generator(self) -> ModelConfig:
        return MODELS[self.generator]

    def get_critic(self) -> ModelConfig:
        return MODELS[self.critic]

    def get_editor(self) -> ModelConfig:
        return MODELS[self.editor]


# Configurations to test
PIPELINE_CONFIGS = {
    # Config A: All Gemini 3 Flash (cheapest)
    "A": PipelineConfig(
        name="A",
        description="All Gemini 3 Flash - cheapest option",
        generator="gemini-3-flash",
        critic="gemini-3-flash",
        editor="gemini-3-flash",
    ),

    # Config B: Gemini 3 Flash generator, Claude critic/editor
    "B": PipelineConfig(
        name="B",
        description="Gemini 3 Flash + Claude Haiku critic + Sonnet editor",
        generator="gemini-3-flash",
        critic="claude-haiku",
        editor="claude-sonnet",
    ),

    # Config C: Claude Sonnet throughout (mid-tier)
    "C": PipelineConfig(
        name="C",
        description="All Claude Sonnet - balanced quality/cost",
        generator="claude-sonnet",
        critic="claude-haiku",
        editor="claude-sonnet",
    ),

    # Config D: Claude Opus generator (quality-first)
    "D": PipelineConfig(
        name="D",
        description="Claude Opus generator - highest quality",
        generator="claude-opus",
        critic="claude-sonnet",
        editor="claude-opus",
    ),

    # Config E: Mixed best-of-breed
    "E": PipelineConfig(
        name="E",
        description="Opus generate, Haiku critique, Sonnet edit",
        generator="claude-opus",
        critic="claude-haiku",
        editor="claude-sonnet",
    ),

    # Config F: Gemini 2.5 Flash (cheapest possible)
    "F": PipelineConfig(
        name="F",
        description="All Gemini 2.5 Flash - absolute cheapest",
        generator="gemini-2.5-flash",
        critic="gemini-2.5-flash",
        editor="gemini-2.5-flash",
    ),
}


# =============================================================================
# LEVEL SPECIFICATIONS (curriculum)
# =============================================================================

@dataclass
class LevelSpec:
    """Phonics/reading level specification."""
    level: str
    band: str
    skill: str
    skill_description: str
    phonics_patterns: list
    word_families: list
    decodable_words: list
    sight_words: list
    max_words: int
    target_decodability: float  # 0.0 to 1.0


# Example level specs (you can expand these)
LEVEL_SPECS = {
    "B1": LevelSpec(
        level="B1",
        band="B",
        skill="CVC Words (Short a, i)",
        skill_description="Three-letter words with short a and short i vowels",
        phonics_patterns=["CVC-a", "CVC-i"],
        word_families=["-at", "-an", "-am", "-ap", "-ad", "-ag", "-it", "-in", "-im", "-ip", "-id", "-ig"],
        decodable_words=[
            # Short a words
            "cat", "bat", "hat", "mat", "rat", "sat", "fat", "pat", "vat",
            "can", "man", "pan", "ran", "tan", "van", "fan", "Dan",
            "ham", "jam", "ram", "Sam", "yam",
            "cap", "gap", "lap", "map", "nap", "tap", "zap",
            "bad", "dad", "had", "mad", "sad", "lad", "pad",
            "bag", "rag", "tag", "wag", "sag", "nag",
            # Short i words
            "bit", "fit", "hit", "kit", "lit", "pit", "sit", "wit",
            "bin", "din", "fin", "pin", "tin", "win",
            "dim", "him", "rim", "Tim", "Jim",
            "dip", "hip", "lip", "rip", "sip", "tip", "zip",
            "bid", "did", "hid", "kid", "lid", "rid",
            "big", "dig", "fig", "jig", "pig", "wig",
        ],
        sight_words=[
            "the", "a", "is", "I", "to", "and", "it", "in", "on", "my",
            "see", "he", "she", "we", "be", "me", "no", "go", "so"
        ],
        max_words=80,
        target_decodability=0.90,
    ),

    "B3": LevelSpec(
        level="B3",
        band="B",
        skill="Consonant Blends",
        skill_description="Initial blends (pl-, cr-, sn-, sp-, st-) and final blends (-mp, -st, -nd)",
        phonics_patterns=["pl-", "cr-", "sn-", "sp-", "st-", "-mp", "-st", "-nd"],
        word_families=["-ip", "-op", "-amp", "-ust", "-est"],
        decodable_words=[
            "plop", "snap", "snaps", "spot", "spots", "stop", "stomp", "step", "steps",
            "croc", "crisp", "chomp", "scrub", "scrubs", "grin", "grins", "glad",
            "trust", "best", "must", "just", "rest", "prop", "drip", "strip", "stuck",
            "plod", "plan", "spit", "spin", "snip", "snug", "stun", "stamp", "stump"
        ],
        sight_words=[
            "the", "a", "is", "was", "in", "on", "I", "he", "she", "her", "his",
            "said", "to", "what", "no", "not", "big", "it", "but", "will", "can",
            "do", "you", "my", "me"
        ],
        max_words=150,
        target_decodability=0.85,
    ),

    "B4": LevelSpec(
        level="B4",
        band="B",
        skill="Initial Consonant Blends",
        skill_description="Two consonants blended together at the start: L-blends, R-blends, S-blends",
        phonics_patterns=["bl-", "cl-", "fl-", "gl-", "pl-", "sl-", "br-", "cr-", "dr-", "fr-", "gr-", "pr-", "tr-", "sc-", "sk-", "sm-", "sn-", "sp-", "st-", "sw-"],
        word_families=["-ap", "-ip", "-op", "-ot", "-ug", "-um", "-an", "-in", "-ock", "-ick"],
        decodable_words=[
            # L-blends
            "black", "blink", "block", "blob", "clap", "clip", "clock", "club", "clam",
            "flag", "flat", "flip", "flop", "fled", "glad", "glen", "glum", "glob",
            "plan", "plot", "plop", "plug", "plum", "slam", "slap", "slid", "slim", "slip", "slot", "slug",
            # R-blends
            "brag", "brick", "brim", "brush", "crab", "crack", "crib", "crop", "crush",
            "drag", "drip", "drop", "drum", "fresh", "frog", "frost", "from",
            "grab", "gram", "grass", "grill", "grin", "grip", "grit",
            "press", "prick", "print", "prod", "prop",
            "track", "trap", "trick", "trim", "trip", "trot", "truck", "trust",
            # S-blends
            "scab", "scan", "scat", "skill", "skim", "skin", "skip", "skit", "skull", "skunk",
            "smack", "small", "smash", "smell", "smog", "snack", "snag", "snap", "sniff", "snip", "snob", "snug",
            "span", "spell", "spend", "spill", "spin", "spit", "spot", "spun",
            "stack", "stamp", "stand", "step", "stick", "still", "stomp", "stop", "stuck", "stump", "stung",
            "swam", "swell", "swept", "swift", "swim", "swing", "swung",
        ],
        sight_words=[
            "the", "a", "is", "was", "in", "on", "I", "he", "she", "her", "his",
            "said", "to", "what", "no", "not", "it", "but", "will", "can",
            "do", "you", "my", "me", "from", "there", "they", "come"
        ],
        max_words=160,
        target_decodability=0.85,
    ),

    "B5": LevelSpec(
        level="B5",
        band="B",
        skill="Consonant Digraphs",
        skill_description="Two letters making one sound: sh, ch, th, wh, ck, ng",
        phonics_patterns=["sh", "ch", "th", "wh", "ck", "ng"],
        word_families=["-ish", "-ash", "-ush", "-ich", "-uch", "-ath", "-ick", "-ock", "-ing", "-ang"],
        decodable_words=[
            "ship", "shell", "shop", "shut", "shack", "fish", "wish", "rush", "dash",
            "chip", "chop", "chat", "chin", "rich", "much", "such", "lunch",
            "this", "that", "them", "then", "with", "bath", "path", "thick", "thin",
            "when", "what", "which", "where", "white",
            "back", "kick", "rock", "duck", "stick", "black", "truck",
            "ring", "sing", "song", "long", "king", "thing", "bring", "wing"
        ],
        sight_words=[
            "a", "I", "the", "is", "to", "and", "it", "in", "on", "my", "see",
            "he", "she", "we", "be", "you", "are", "was", "for", "said", "have",
            "they", "come", "there", "what", "from"
        ],
        max_words=180,
        target_decodability=0.85,
    ),

    "B7": LevelSpec(
        level="B7",
        band="B",
        skill="Vowel Teams",
        skill_description="Two vowels working together: ai/ay, ee/ea, oa/ow",
        phonics_patterns=["ai", "ay", "ee", "ea", "oa", "ow"],
        word_families=["-ail", "-ain", "-ay", "-eep", "-eet", "-ead", "-eat", "-oat", "-oad", "-ow"],
        decodable_words=[
            # ai words
            "mail", "nail", "pail", "rail", "sail", "tail", "trail", "snail",
            "rain", "brain", "chain", "drain", "grain", "main", "pain", "plain", "Spain", "stain", "train",
            "wait", "bait", "paid", "maid", "aid", "laid", "raid",
            # ay words
            "bay", "day", "gay", "hay", "jay", "lay", "may", "pay", "ray", "say", "way",
            "clay", "gray", "play", "pray", "stay", "spray", "stray", "sway", "tray",
            # ee words
            "bee", "fee", "see", "tree", "free", "three",
            "beef", "reef", "beet", "feet", "meet", "sweet", "street",
            "beep", "deep", "jeep", "keep", "peep", "seep", "sleep", "steep", "sweep", "creep",
            "deed", "feed", "need", "seed", "speed", "weed",
            "feel", "heel", "peel", "reel", "steel", "wheel",
            "seen", "been", "keen", "green", "queen", "screen",
            # ea words
            "bean", "dean", "jean", "lean", "mean", "clean",
            "beat", "eat", "heat", "meat", "neat", "seat", "treat", "wheat",
            "bead", "lead", "read", "plead",
            "beach", "each", "peach", "reach", "teach",
            "beam", "dream", "ream", "seam", "steam", "stream", "team",
            "leaf", "tea", "pea", "sea", "flea",
            # oa words
            "boat", "coat", "float", "goat", "moat", "oat",
            "foam", "loam", "roam",
            "load", "road", "toad",
            "coal", "foal", "goal",
            "coast", "roast", "toast", "boast",
            "oak", "soak", "cloak", "croak",
            # ow (long o) words
            "bow", "flow", "glow", "grow", "know", "low", "mow", "row", "show", "slow", "snow", "stow", "throw", "tow",
            "blown", "flown", "grown", "known", "shown", "thrown",
            "bowl", "own", "yellow", "follow", "hollow", "swallow",
        ],
        sight_words=[
            "the", "a", "is", "was", "to", "and", "he", "she", "they", "said",
            "I", "you", "my", "me", "we", "be", "have", "are", "were", "there",
            "what", "when", "where", "who", "one", "two", "do", "does"
        ],
        max_words=180,
        target_decodability=0.85,
    ),

    "B6": LevelSpec(
        level="B6",
        band="B",
        skill="Magic E (CVCe)",
        skill_description="Silent e makes the vowel say its name: a_e, i_e, o_e, u_e",
        phonics_patterns=["a_e", "i_e", "o_e", "u_e"],
        word_families=["-ake", "-ame", "-ade", "-ate", "-ave", "-ike", "-ide", "-ine", "-ite", "-ome", "-ope", "-ote", "-ube", "-ule", "-ute"],
        decodable_words=[
            # a_e words
            "bake", "cake", "fake", "lake", "make", "rake", "take", "wake", "Jake",
            "came", "fame", "game", "name", "same", "tame",
            "cave", "gave", "save", "wave", "brave",
            "made", "fade", "wade", "shade", "grade",
            "late", "gate", "date", "mate", "plate", "skate",
            # i_e words
            "bike", "hike", "like", "Mike", "spike",
            "dine", "fine", "line", "mine", "nine", "pine", "vine", "shine",
            "hide", "ride", "side", "wide", "glide", "slide", "pride",
            "bite", "kite", "white", "quite",
            "dive", "five", "hive", "drive",
            "time", "dime", "lime", "chime",
            # o_e words
            "bone", "cone", "tone", "zone", "stone", "phone",
            "home", "dome", "gnome",
            "hope", "rope", "scope",
            "hole", "mole", "pole", "role", "stole", "whole",
            "nose", "rose", "those", "chose", "close",
            "woke", "broke", "spoke", "joke", "poke", "smoke",
            "note", "vote", "wrote",
            # u_e words
            "cube", "tube",
            "cute", "mute",
            "huge", "fuse",
            "rule", "June", "tune", "prune", "dune",
        ],
        sight_words=[
            "the", "a", "is", "was", "to", "and", "he", "she", "they", "said",
            "I", "you", "my", "me", "we", "be", "have", "are", "were", "there",
            "what", "when", "where", "who", "why", "how", "one", "two"
        ],
        max_words=180,
        target_decodability=0.85,
    ),

    "C1": LevelSpec(
        level="C1",
        band="C",
        skill="Silent Letters",
        skill_description="Silent letter patterns: kn-, wr-, gn-, -mb, gh",
        phonics_patterns=["kn-", "wr-", "gn-", "-mb", "gh"],
        word_families=["-ight", "-ough"],
        decodable_words=[
            "knight", "knife", "knit", "knot", "knock", "knee", "knew", "know",
            "write", "written", "wrong", "wrap", "wrist", "wreck",
            "gnome", "gnat", "gnaw", "sign", "design",
            "lamb", "climb", "thumb", "comb", "crumb", "numb",
            "night", "right", "light", "bright", "might", "sight", "fight", "tight",
            "thought", "through", "though", "enough"
        ],
        sight_words=[
            "thought", "through", "eight", "enough", "know", "write",
            "the", "a", "is", "was", "to", "and", "he", "she", "they", "said"
        ],
        max_words=200,
        target_decodability=0.75,
    ),
}


# =============================================================================
# STORY MODES
# =============================================================================

@dataclass
class StoryMode:
    """Creative mode for the story."""
    name: str
    description: str
    prompt_guidance: str


STORY_MODES = {
    "narrative": StoryMode(
        name="narrative",
        description="Traditional story with tension and resolution",
        prompt_guidance="""
Write a narrative story with:
- A character who WANTS something
- ONE moment of genuine tension
- Physical action and sensory details
- Resolution that feels earned
""",
    ),

    "poem": StoryMode(
        name="poem",
        description="Sound-focused poem, rhythm over plot",
        prompt_guidance="""
Write a mood poem that:
- Leans INTO the sounds of the phonics patterns
- Prioritizes rhythm and musicality
- Creates atmosphere over narrative
- Uses repetition purposefully
- May not have traditional plot
""",
    ),

    "lullaby": StoryMode(
        name="lullaby",
        description="Quiet, soothing, gentle rhythm",
        prompt_guidance="""
Write a lullaby-like story that:
- Has gentle, soothing rhythm
- Uses soft sounds and quiet moments
- Builds to rest, not excitement
- Feels like a warm blanket
""",
    ),

    "romp": StoryMode(
        name="romp",
        description="Energetic, playful, percussive",
        prompt_guidance="""
Write an energetic romp that:
- Uses percussive, punchy sounds
- Has physical energy and movement
- Feels playful and fun
- Makes kids want to move or laugh
""",
    ),

    "observation": StoryMode(
        name="observation",
        description="Quiet noticing, wonder at small things",
        prompt_guidance="""
Write a quiet observation piece that:
- Notices small, specific details
- Creates wonder without drama
- Slows down time
- Finds magic in ordinary moments
""",
    ),
}


# =============================================================================
# STORY SEEDS (test inputs)
# =============================================================================

@dataclass
class StorySeed:
    """Input seed for story generation."""
    id: str
    level: str
    mode: str
    setting: str
    anchor: str  # Real-world phenomenon to ground the story
    notes: Optional[str] = None


# Test seeds for the experiment
TEST_SEEDS = [
    StorySeed(
        id="seed_01",
        level="B5",
        mode="poem",
        setting="tide pools at dawn",
        anchor="Hermit crabs switching shells in a line (real behavior)",
        notes="sh sounds feel whispery - lean into quiet dawn mood",
    ),
    StorySeed(
        id="seed_02",
        level="B3",
        mode="narrative",
        setting="African riverbank",
        anchor="Plover birds cleaning crocodile teeth (symbiosis)",
        notes="Already have Pip and the Croc - test if we can match quality",
    ),
    StorySeed(
        id="seed_03",
        level="B5",
        mode="lullaby",
        setting="fishing village at night",
        anchor="Bioluminescent plankton glowing when disturbed",
        notes="sh/ng sounds can be soothing - shush, sing, shimmering",
    ),
    StorySeed(
        id="seed_04",
        level="C1",
        mode="observation",
        setting="grandmother's garden",
        anchor="How worms aerate soil (underground world)",
        notes="Silent letters: gnome, knight could be garden statues",
    ),
    StorySeed(
        id="seed_05",
        level="B3",
        mode="romp",
        setting="kitchen during breakfast",
        anchor="Toast popping, eggs sizzling - morning chaos",
        notes="Blend sounds are percussive: snap, crack, stomp, plop",
    ),
]


# =============================================================================
# API KEYS (from environment)
# =============================================================================

def get_api_keys():
    """Load API keys from environment."""
    return {
        "google": os.environ.get("GOOGLE_AI_API_KEY"),
        "anthropic": os.environ.get("ANTHROPIC_API_KEY"),
        "openai": os.environ.get("OPENAI_API_KEY"),
    }
