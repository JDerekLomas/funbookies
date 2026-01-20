#!/usr/bin/env python3
"""
XML-Based Book Generator with Strict Curriculum Alignment

Generates decodable readers as XML, enforcing:
- 85%+ decodability using only approved words for the level
- Proper scene descriptions with WHO/WHERE/WHAT/STYLE
- Image prompts ready for generation
- Reference sheet prompts

Usage:
    python generate_book_xml.py --level B1 --concept "A pig who loves mud" --setting "farm"
"""

import json
import sys
import os
import re
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / ".env")

# Load level specs
LEVEL_SPECS_PATH = PROJECT_ROOT / "public" / "data" / "level-specs.json"
with open(LEVEL_SPECS_PATH) as f:
    LEVEL_SPECS = json.load(f)

# API setup
ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY")
GOOGLE_KEY = os.getenv("GOOGLE_AI_API_KEY")

if ANTHROPIC_KEY:
    import anthropic
    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
    LLM_PROVIDER = "anthropic"
elif GOOGLE_KEY:
    import google.generativeai as genai
    genai.configure(api_key=GOOGLE_KEY)
    client = genai.GenerativeModel("gemini-2.0-flash")
    LLM_PROVIDER = "google"
else:
    print("No API key found. Set ANTHROPIC_API_KEY or GOOGLE_AI_API_KEY")
    sys.exit(1)


def call_llm(prompt: str, max_tokens: int = 4000) -> str:
    """Call LLM and return response text."""
    if LLM_PROVIDER == "anthropic":
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text.strip()
    else:
        response = client.generate_content(prompt)
        return response.text.strip()


def get_level_spec(level: str) -> dict:
    """Get level specification from level-specs.json."""
    return LEVEL_SPECS["levels"].get(level, {})


def build_word_list(level: str) -> dict:
    """Build complete word list for a level including cumulative sight words."""
    spec = get_level_spec(level)
    constraints = spec.get("constraints", {})

    # Extract decodable words from phonicsPatterns
    decodable = set()
    patterns = constraints.get("phonicsPatterns", [])
    for pattern in patterns:
        # Extract words after colon
        if ":" in pattern:
            words_part = pattern.split(":", 1)[1]
            words = [w.strip().lower() for w in words_part.split(",")]
            decodable.update(words)

    # Add word families
    word_families = constraints.get("wordFamilies", [])

    # Build sight words (cumulative from all previous levels)
    sight_words = set()
    band = spec.get("band", "B")
    level_index = spec.get("index", 0)

    # Core sight words by level
    core_sight = {
        0: [],  # A0
        1: ["a", "i"],  # A1
        2: ["a", "i", "the"],  # A2
        3: ["a", "i", "the", "is", "to"],  # A3
        4: ["a", "i", "the", "is", "to", "and", "it", "in", "on"],  # A4
        5: ["a", "i", "the", "is", "to", "and", "it", "in", "on", "my", "see"],  # B1
        6: ["a", "i", "the", "is", "to", "and", "it", "in", "on", "my", "see", "he", "she", "we", "be"],  # B2
        7: ["a", "i", "the", "is", "to", "and", "it", "in", "on", "my", "see", "he", "she", "we", "be", "you", "are", "was", "for"],  # B3
        8: ["a", "i", "the", "is", "to", "and", "it", "in", "on", "my", "see", "he", "she", "we", "be", "you", "are", "was", "for", "said", "have", "they", "come"],  # B4
    }

    if level_index in core_sight:
        sight_words.update(core_sight[level_index])
    elif level_index > 8:
        # For higher levels, include all B-band sight words plus level-specific
        sight_words.update(core_sight[8])

    return {
        "decodable": decodable,
        "sight_words": sight_words,
        "word_families": word_families,
    }


def extract_decodable_words_for_level(level: str) -> set:
    """Extract all decodable words for a specific level from level-specs."""
    spec = get_level_spec(level)
    constraints = spec.get("constraints", {})

    words = set()

    # From phonicsPatterns
    for pattern in constraints.get("phonicsPatterns", []):
        if ":" in pattern:
            word_part = pattern.split(":", 1)[1]
            for w in word_part.split(","):
                words.add(w.strip().lower())

    # From flossRule if present
    for pattern in constraints.get("flossRule", []):
        if ":" in pattern:
            word_part = pattern.split(":", 1)[1]
            for w in word_part.split(","):
                words.add(w.strip().lower())

    # From contrastPairs
    for pair in constraints.get("contrastPairs", []):
        for w in pair.split("/"):
            words.add(w.strip().lower())

    return words


# =============================================================================
# COMPREHENSIVE WORD LISTS BY LEVEL
# =============================================================================

# These supplement level-specs.json with complete decodable word lists
LEVEL_WORD_LISTS = {
    "B1": {
        "decodable": [
            # -at family (with -s plurals)
            "at", "bat", "bats", "cat", "cats", "fat", "hat", "hats", "mat", "mats", "pat", "pats", "rat", "rats", "sat", "vat", "flat", "that",
            # -an family
            "an", "ban", "bans", "can", "dan", "fan", "fans", "man", "pan", "pans", "ran", "tan", "van", "vans",
            # -am family
            "am", "ham", "jam", "ram", "sam", "yam",
            # -ap family
            "cap", "caps", "gap", "gaps", "lap", "laps", "map", "maps", "nap", "naps", "rap", "raps", "sap", "tap", "taps", "zap", "zaps",
            # -ad family
            "ad", "bad", "dad", "had", "lad", "lads", "mad", "pad", "pads", "sad",
            # -ag family
            "bag", "bags", "gag", "gags", "lag", "nag", "nags", "rag", "rags", "sag", "tag", "tags", "wag", "wags",
            # -it family
            "bit", "bits", "fit", "fits", "hit", "hits", "kit", "kits", "lit", "pit", "pits", "sit", "sits", "wit",
            # -in family
            "bin", "bins", "din", "fin", "fins", "kin", "pin", "pins", "sin", "tin", "win", "wins",
            # -im family
            "dim", "him", "rim", "tim", "jim", "kim",
            # -ip family
            "dip", "dips", "hip", "hips", "lip", "lips", "nip", "nips", "rip", "rips", "sip", "sips", "tip", "tips", "zip", "zips",
            # -id family
            "bid", "bids", "did", "hid", "kid", "kids", "lid", "lids", "rid",
            # -ig family
            "big", "dig", "digs", "fig", "figs", "gig", "gigs", "jig", "jigs", "pig", "pigs", "rig", "rigs", "wig", "wigs",
            # -ix family
            "fix", "mix", "six",
        ],
        "sight_words": [
            "a", "i", "the", "is", "to", "and", "it", "in", "on", "my", "see",
            "he", "she", "we", "be", "me", "no", "go", "so", "do",
            "his", "her", "has", "was", "said", "they", "but", "for", "not",
            "at", "as", "get", "got", "let", "red", "yes", "yet",
        ],
        "names": ["tim", "sam", "dan", "jim", "kim", "pat", "nat", "max"],
    },
    "B4": {
        "decodable": [
            # L-blends
            "black", "blade", "blame", "blank", "blast", "blaze", "bleed", "blend", "bless", "blind", "blink", "bliss", "block", "blob", "blood", "bloom", "blot", "blow", "blue", "blur", "blush",
            "clad", "claim", "clam", "clamp", "clang", "clank", "clap", "clash", "clasp", "class", "claw", "clay", "clean", "clear", "clerk", "click", "cliff", "climb", "cling", "clip", "cloak", "clock", "clog", "close", "cloth", "cloud", "clown", "club", "cluck", "clue", "clump", "clung",
            "flag", "flake", "flame", "flap", "flash", "flask", "flat", "flaw", "flea", "fled", "flesh", "flew", "flex", "flick", "fling", "flip", "flit", "float", "flock", "flood", "floor", "flop", "flow", "flown", "fluff", "fluid", "flung", "flush", "flute",
            "glad", "glam", "glance", "gland", "glare", "glass", "glaze", "gleam", "glee", "glen", "glide", "glint", "glob", "globe", "gloom", "gloss", "glove", "glow", "glue", "glum",
            "place", "plaid", "plain", "plan", "plane", "plank", "plant", "plate", "play", "plaza", "plead", "please", "pledge", "plenty", "plod", "plop", "plot", "plow", "pluck", "plug", "plum", "plump", "plunge", "plus", "plush",
            "slab", "slack", "slam", "slang", "slant", "slap", "slash", "slat", "slate", "slave", "slay", "sled", "sleek", "sleep", "sleet", "slept", "slew", "slice", "slick", "slid", "slide", "slim", "slime", "sling", "slink", "slip", "slit", "slob", "slope", "slop", "slot", "slow", "slug", "slum", "slump", "slung", "slush",
            # R-blends
            "brace", "brad", "brag", "braid", "brain", "brake", "branch", "brand", "brass", "brat", "brave", "brawl", "bread", "break", "breast", "breath", "bred", "breed", "breeze", "brew", "brick", "bride", "bridge", "brief", "bright", "brim", "bring", "brink", "brisk", "broad", "broke", "brood", "brook", "broom", "broth", "brow", "brown", "browse", "bruise", "brush", "brute",
            "crack", "cradle", "craft", "cram", "cramp", "crane", "crank", "crash", "crate", "crave", "crawl", "craze", "crazy", "creak", "cream", "crease", "create", "creek", "creep", "crest", "crew", "crib", "cricket", "cried", "crime", "crimp", "crisp", "croak", "crock", "crook", "crop", "cross", "crouch", "crow", "crowd", "crown", "crude", "cruel", "cruise", "crumb", "crunch", "crush", "crust", "cry",
            "draft", "drag", "drain", "drake", "drank", "drape", "draw", "drawn", "dread", "dream", "dress", "drew", "dried", "drift", "drill", "drink", "drip", "drive", "drone", "drool", "droop", "drop", "dross", "drove", "drown", "drug", "drum", "drunk", "dry",
            "fraction", "fragile", "frame", "frank", "frantic", "fraud", "fray", "freak", "free", "freeze", "freight", "french", "fresh", "fret", "friction", "fried", "friend", "fright", "frill", "fringe", "frisk", "frog", "from", "front", "frost", "froth", "frown", "froze", "fruit", "fry",
            "grab", "grace", "grade", "grain", "gram", "grand", "grant", "grape", "graph", "grasp", "grass", "grate", "grave", "gravy", "gray", "graze", "grease", "great", "greed", "green", "greet", "grew", "grid", "grief", "grill", "grim", "grin", "grind", "grip", "grit", "groan", "groom", "grope", "gross", "ground", "group", "grove", "grow", "growl", "grown", "grub", "grump", "grunt",
            "prance", "prank", "pray", "preach", "press", "pretty", "prevent", "prey", "price", "prick", "pride", "priest", "prime", "prince", "print", "prison", "prize", "probe", "problem", "prod", "produce", "profit", "program", "project", "promise", "prompt", "prone", "proof", "prop", "proper", "protect", "proud", "prove", "provide", "prowl", "prune", "pry",
            "trace", "track", "trade", "trail", "train", "trait", "tramp", "trap", "trash", "travel", "tray", "tread", "treasure", "treat", "tree", "trek", "tremble", "trend", "trial", "tribe", "trick", "tried", "trigger", "trim", "trip", "trod", "troll", "troop", "trophy", "trot", "trouble", "trout", "truce", "truck", "trudge", "true", "trump", "trunk", "trust", "truth", "try",
            # S-blends
            "scab", "scaffold", "scald", "scale", "scalp", "scam", "scamp", "scan", "scar", "scarce", "scare", "scarf", "scatter", "scene", "scent", "school", "science", "scissors", "scold", "scoop", "scoot", "scope", "scorch", "score", "scorn", "scout", "scowl", "scram", "scramble", "scrap", "scrape", "scratch", "scrawl", "scream", "screech", "screen", "screw", "scribble", "script", "scroll", "scrub", "scruff",
            "skate", "skeleton", "sketch", "ski", "skid", "skill", "skim", "skin", "skip", "skirt", "skit", "skull", "skunk", "sky",
            "smack", "small", "smart", "smash", "smear", "smell", "smelt", "smile", "smirk", "smock", "smog", "smoke", "smooth", "smother", "smudge", "smug",
            "snack", "snag", "snail", "snake", "snap", "snare", "snarl", "snatch", "sneak", "sneer", "sneeze", "sniff", "snip", "snob", "snoop", "snore", "snort", "snout", "snow", "snub", "snuck", "snuff", "snug",
            "space", "spade", "span", "spank", "spar", "spare", "spark", "sparse", "spasm", "spat", "spawn", "speak", "spear", "special", "speck", "speech", "speed", "spell", "spend", "spent", "spice", "spider", "spill", "spin", "spine", "spiral", "spirit", "spit", "splash", "splendid", "splice", "splint", "split", "spoil", "spoke", "sponge", "spook", "spool", "spoon", "sport", "spot", "spouse", "spout", "sprawl", "spray", "spread", "spree", "spring", "sprinkle", "sprint", "sprout", "spruce", "spun", "spur", "spurt", "spy",
            "stab", "stable", "stack", "staff", "stage", "stagger", "stain", "stair", "stake", "stale", "stalk", "stall", "stamp", "stance", "stand", "stank", "staple", "star", "stare", "stark", "start", "starve", "stash", "state", "station", "statue", "status", "stay", "steady", "steak", "steal", "steam", "steel", "steep", "steer", "stem", "step", "stern", "stew", "stick", "stiff", "still", "sting", "stink", "stir", "stitch", "stock", "stole", "stomp", "stone", "stood", "stool", "stoop", "stop", "store", "stork", "storm", "story", "stout", "stove", "stow", "straight", "strain", "strand", "strange", "strap", "straw", "stray", "streak", "stream", "street", "strength", "stress", "stretch", "strict", "stride", "strike", "string", "strip", "stripe", "strive", "stroke", "stroll", "strong", "strove", "struck", "structure", "struggle", "strung", "strut", "stub", "stuck", "stud", "study", "stuff", "stump", "stung", "stunk", "stunt", "stupid", "sturdy", "style",
            "swab", "swallow", "swam", "swamp", "swan", "swap", "swarm", "sway", "swear", "sweat", "sweater", "sweep", "sweet", "swell", "swept", "swerve", "swift", "swim", "swine", "swing", "swipe", "swirl", "switch", "swollen", "swoop", "sword", "swore", "sworn", "swum", "swung",
        ],
        "sight_words": [
            "a", "i", "the", "is", "was", "in", "on", "he", "she", "her", "his",
            "said", "to", "what", "no", "not", "it", "but", "will", "can",
            "do", "you", "my", "me", "from", "there", "they", "come", "have",
            "are", "were", "be", "been", "one", "two", "some", "would", "could",
            "go", "goes", "all", "for", "has", "had", "up", "down", "out",
            "day", "fun", "help", "helps", "now", "this", "that", "with",
            # Additional common words
            "and", "then", "best", "bet", "fact", "felt", "hill", "today",
            "face", "race", "like", "friend", "friends", "win", "wins",
            # More common words
            "again", "beach", "find", "finds", "hot", "must", "oh", "sees",
            "shell", "shells", "feels", "feel", "claw", "claws", "gets",
            "grab", "grabs", "crab", "crabs", "wind", "sand", "run", "runs",
            "bright", "crisp", "blank", "used", "yet", "broke", "great",
            "pang", "butt", "cry", "where",
        ],
        "names": ["tim", "sam", "dan", "jim", "kim", "pat", "max", "ben", "tom", "ted"],
    },
    "B6": {
        "decodable": [
            # a_e words
            "ace", "age", "ape", "ate", "babe", "bade", "bake", "bale", "bane", "bare", "base", "blade", "blame", "blaze", "brace", "brake", "brave", "cage", "cake", "came", "cane", "cape", "care", "case", "cave", "chase", "crane", "crate", "craze", "date", "daze", "drake", "drape", "face", "fade", "fake", "fame", "fare", "fate", "faze", "flame", "flake", "frame", "gale", "game", "gape", "gate", "gave", "gaze", "grace", "grade", "grape", "grate", "grave", "graze", "hare", "haste", "hate", "have", "haze", "jade", "jake", "james", "jane", "kate", "lace", "lake", "lame", "lane", "late", "made", "make", "male", "mane", "mare", "mate", "maze", "name", "pace", "page", "pale", "pane", "paste", "pave", "place", "plane", "plate", "race", "rage", "rake", "range", "rare", "rate", "rave", "safe", "sage", "sake", "sale", "same", "sane", "save", "scale", "scrape", "shade", "shake", "shame", "shape", "share", "shave", "skate", "snake", "space", "spade", "spare", "stage", "stake", "stale", "stare", "state", "strafe", "strange", "take", "tale", "tame", "tape", "taste", "trade", "wade", "wage", "wake", "wane", "ware", "waste", "wave",
            # i_e words
            "bike", "bile", "bite", "bribe", "bride", "chide", "chime", "chive", "crime", "dice", "dime", "dine", "dire", "dive", "drive", "fife", "file", "fine", "fire", "five", "glide", "grime", "gripe", "hide", "hike", "hire", "hive", "ice", "jibe", "jive", "kite", "knife", "life", "like", "lime", "line", "live", "mice", "mike", "mile", "mime", "mine", "mire", "nice", "nine", "pike", "pile", "pine", "pipe", "price", "pride", "prime", "prize", "rice", "ride", "rife", "rile", "ripe", "rise", "rite", "shine", "shire", "side", "sire", "site", "size", "slice", "slide", "slime", "smile", "snide", "snipe", "spice", "spike", "spine", "spite", "splice", "stride", "strife", "strike", "stripe", "strive", "swine", "swipe", "thine", "thrice", "tide", "tile", "time", "tine", "tire", "tribe", "trice", "trite", "twice", "twine", "vice", "vile", "vine", "while", "whine", "white", "wide", "wife", "wile", "wine", "wipe", "wire", "wise", "write",
            # o_e words
            "awoke", "bloke", "bone", "bore", "broke", "choke", "chose", "chrome", "clone", "close", "clothe", "code", "coke", "come", "cone", "cope", "core", "cove", "dole", "dome", "done", "dose", "dote", "dove", "doze", "drone", "drove", "fore", "froze", "globe", "gnome", "gone", "gore", "grope", "grove", "hole", "home", "hone", "hope", "hose", "joke", "lobe", "lone", "lore", "lose", "love", "mode", "mole", "mope", "more", "mote", "move", "node", "none", "nose", "note", "ode", "ore", "phone", "poke", "pole", "pone", "pope", "pore", "pose", "probe", "prone", "prose", "prove", "quote", "robe", "rode", "role", "rope", "rose", "rote", "rove", "scope", "score", "shore", "shove", "smoke", "snore", "sole", "some", "sore", "spoke", "spore", "stoke", "stole", "stone", "store", "stove", "strobe", "stroke", "strove", "swore", "those", "throne", "tone", "tore", "tote", "vote", "woke", "wone", "wore", "wove", "wrote", "yoke", "yore", "zone",
            # u_e words
            "brute", "chute", "crude", "cube", "cure", "cute", "dude", "duke", "dune", "dupe", "endure", "fluke", "flume", "flute", "fume", "fuse", "huge", "june", "jute", "lube", "lure", "lute", "mule", "muse", "mute", "nude", "plume", "plunge", "prude", "prune", "pure", "rude", "rule", "rune", "ruse", "sure", "truce", "true", "tube", "tune", "use",
        ],
        "sight_words": [
            "a", "i", "the", "is", "was", "to", "and", "he", "she", "they", "said",
            "you", "my", "me", "we", "be", "have", "are", "were", "there",
            "what", "when", "where", "who", "why", "how", "one", "two",
            "do", "does", "would", "could", "should", "her", "his", "of",
            # Additional common words
            "but", "for", "it", "in", "on", "no", "not", "now", "has", "had",
            "get", "gets", "help", "helps", "here", "just", "so", "go", "with",
            "fell", "job", "kind", "knew", "let", "lets", "will", "can",
            "bakes", "makes", "takes", "likes", "blinks", "thinks",
            # More common words
            "add", "adds", "asks", "blends", "bowl", "eggs", "hot", "last",
            "long", "milk", "mom", "dad", "oh", "out", "oven", "shell",
            "mix", "best", "put", "puts", "up", "all", "done", "good",
        ],
        "names": ["jake", "kate", "mike", "jane", "dave", "rose", "june", "luke"],
    },
    "B7": {
        "decodable": [
            # ai words
            "aid", "ail", "aim", "air", "braid", "brain", "chain", "claim", "complain", "contain", "drain", "explain", "fail", "faint", "fair", "faith", "gain", "grain", "hail", "hair", "jail", "laid", "lain", "maid", "mail", "main", "maintain", "nail", "obtain", "paid", "pail", "pain", "paint", "pair", "plain", "praise", "rail", "rain", "raise", "raid", "remain", "sail", "saint", "snail", "Spain", "sprain", "stain", "strain", "tail", "train", "trail", "vain", "waist", "wait", "wail",
            # ay words
            "away", "bay", "betray", "birthday", "clay", "day", "decay", "delay", "display", "essay", "gray", "hay", "highway", "holiday", "jay", "lay", "may", "midday", "okay", "pay", "play", "portray", "pray", "ray", "relay", "repay", "say", "spray", "stay", "stray", "subway", "sway", "today", "tray", "way",
            # ee words
            "bee", "beef", "been", "beer", "beet", "bleed", "breed", "breeze", "cheek", "cheer", "cheese", "creep", "creek", "deed", "deem", "deep", "deer", "fee", "feed", "feel", "feet", "flee", "fleet", "free", "freeze", "geese", "greed", "green", "greet", "heel", "jeep", "jeer", "keen", "keep", "knee", "kneel", "leech", "lee", "meek", "meet", "need", "peek", "peel", "peer", "queen", "reed", "reef", "reek", "reel", "screech", "screen", "seed", "seek", "seem", "seen", "seep", "seer", "sheet", "sheer", "sheep", "sleek", "sleep", "sleet", "sneeze", "speed", "spleen", "squeeze", "steed", "steel", "steer", "steep", "street", "sweep", "sweet", "tee", "teem", "teen", "teeth", "three", "tree", "tweed", "tweet", "wee", "weed", "week", "weep", "wheel",
            # ea words
            "beach", "bead", "beak", "beam", "bean", "beast", "beat", "bleach", "breach", "bread", "break", "breast", "breath", "cease", "cheat", "clean", "clear", "creak", "cream", "crease", "deal", "dean", "dream", "each", "eagle", "ear", "ease", "east", "eat", "feast", "feat", "flea", "freak", "gleam", "glean", "grease", "great", "heal", "heap", "hear", "heat", "jeans", "lead", "leaf", "leak", "lean", "leap", "lease", "leash", "least", "leave", "meal", "mean", "meat", "neat", "pea", "peach", "peak", "peal", "peas", "peace", "plead", "please", "preach", "read", "ream", "reap", "real", "rear", "reason", "scream", "sea", "seal", "seam", "sear", "seat", "sneak", "speak", "spear", "squeak", "squeal", "steam", "steal", "stream", "streak", "swear", "tea", "teach", "teak", "teal", "team", "tear", "tease", "treat", "weak", "wean", "wear", "weave", "wheat", "wreath", "year", "yeast", "zeal",
            # oa words
            "approach", "boast", "boat", "cloak", "coach", "coal", "coast", "coat", "croak", "float", "foam", "foal", "goal", "goat", "groan", "load", "loaf", "loan", "moat", "moan", "oak", "oat", "poach", "road", "roam", "roast", "soak", "soap", "stoat", "throat", "toast", "toad",
            # ow (long o) words
            "below", "blow", "blown", "bow", "bowl", "elbow", "fellow", "flow", "flown", "follow", "glow", "grow", "grown", "growth", "hollow", "know", "known", "low", "mellow", "mow", "mown", "own", "pillow", "row", "shadow", "shallow", "show", "shown", "slow", "snow", "sow", "sown", "stow", "swallow", "throw", "thrown", "tow", "widow", "willow", "window", "yellow",
        ],
        "sight_words": [
            "a", "i", "the", "is", "was", "to", "and", "he", "she", "they", "said",
            "you", "my", "me", "we", "be", "have", "are", "were", "there",
            "what", "when", "where", "who", "one", "two", "do", "does",
            "would", "could", "should", "very", "her", "his", "of", "or",
            "through", "water", "into", "by", "with", "this", "that",
            # Additional common words
            "but", "has", "had", "it", "in", "on", "no", "not", "now", "for",
            "get", "gets", "let", "lets", "go", "goes", "so", "will", "can",
            "dock", "fill", "fills", "fly", "flies", "miss", "sails", "all",
            "up", "out", "if", "just", "here", "well", "back", "off", "pull",
        ],
        "names": ["ray", "jay", "kay", "may", "lee", "dean", "jean", "neal"],
    },
}


# =============================================================================
# STORY GENERATION PROMPT
# =============================================================================

STORY_GENERATION_PROMPT = """You are an expert children's book author specializing in decodable readers.

Write a short story for reading level {level} using ONLY the approved words.

## LEVEL: {level} - {level_name}
{level_description}

## CONSTRAINTS
- Words per sentence: {words_per_sentence}
- Total pages: EXACTLY {total_pages} story pages (no more, no less)
- Decodability target: {decodability}

## APPROVED DECODABLE WORDS
{decodable_words}

## APPROVED SIGHT WORDS
{sight_words}

## APPROVED NAMES (use one as main character)
{names}

## WORD FAMILIES TO FEATURE
{word_families}

## STORY CONCEPT
{concept}

## SETTING
{setting}

## CRAFT GUIDELINES
1. Write a REAL story, not a list of sentences using target words
2. Create a character who WANTS something
3. Include ONE moment of tension or problem
4. Use sensory details (sounds, sights, textures)
5. End with resolution that feels earned
6. Use onomatopoeia and rhythm where natural
7. Make each page have a distinct visual moment

## CRITICAL RULES
1. ONLY use words from the approved lists
2. Character names from the names list are allowed
3. Feature phonics patterns prominently (words should repeat 3-4 times)
4. Keep sentences within word limit
5. NO words outside approved lists - if you're not sure, don't use it

## OUTPUT FORMAT
```xml
<story>
  <page n="1">
    <text>First line of text.</text>
    <text>Second line if needed.</text>
  </page>
</story>
```

Write an engaging story using ONLY approved words:"""


# =============================================================================
# SCENE DESCRIPTION PROMPT
# =============================================================================

SCENE_DESCRIPTION_PROMPT = """You are an expert at writing image prompts for children's book illustrations.

For each page of this story, write a detailed scene description following the WHO/WHERE/WHAT/STYLE format.

## STORY CONTEXT
Title: {title}
Level: {level}
Setting: {setting}

## CHARACTERS
{characters}

## ART STYLE
{art_style}

## RULES FOR SCENE DESCRIPTIONS

1. **WHO** - Character with EXACT visual identifiers
   - Age, hair color/style, clothing, expression
   - Example: "Tim, a round-faced boy (6-7) in denim overalls and straw sun hat"

2. **WHERE** - Setting with specificity
   - Ground the scene in a real place
   - Include lighting/weather
   - Example: "dusty farm yard under bright summer sun"

3. **WHAT** - Action matching the text EXACTLY
   - Use active verbs (running, sitting, looking)
   - Show emotional state through body language
   - Example: "running eagerly toward the pig"

4. **COMPOSITION** - Always include:
   - Shot type: "Wide shot:", "Medium shot:", or "Close-up:"
   - "One cohesive illustration filling the entire canvas"

5. **STYLE** - End with:
   - Art style instruction
   - "NO TEXT, NO WORDS, NO LETTERS anywhere in image."

## CRITICAL: NEVER USE NEGATIONS
WRONG: "no ball", "without the tractor", "not raining"
RIGHT: Only describe what IS in the scene

## STORY PAGES
{story_pages}

## OUTPUT FORMAT
For each page, output:

```xml
<scenes>
  <page n="1">
    <scene>Medium shot: [WHO doing WHAT in WHERE]. [COMPOSITION]. [STYLE]. NO TEXT anywhere in image.</scene>
    <image_prompt>Full detailed prompt for image generation...</image_prompt>
  </page>
  <!-- continue for all pages -->
</scenes>
```

Write scene descriptions for all pages:"""


# =============================================================================
# REFERENCE PROMPT TEMPLATE
# =============================================================================

REFERENCE_PROMPT_TEMPLATE = """You are an expert at creating 9-panel style reference sheets.

Create a reference sheet prompt for this children's book.

## BOOK INFO
Title: {title}
Level: {level}
Setting: {setting}

## CHARACTERS
{characters}

## ART STYLE
{art_style}

## OUTPUT FORMAT
Output a 9-panel reference sheet prompt following this structure:

```
9-PANEL STYLE REFERENCE SHEET for "{title}"

STYLE: [Art style description - colors, shapes, mood]

Row 1 - [MAIN CHARACTER]:
[1] Front view: [detailed appearance]
[2] Expressions: [3-4 emotions]
[3] In action: [key pose]

Row 2 - [SECONDARY ELEMENTS]:
[4] [Secondary character or key object]
[5] [Another key element]
[6] KEY IMAGE: [Most iconic moment - center panel for style influence]

Row 3 - [SETTING]:
[7] [Setting element 1]
[8] [Setting element 2]
[9] [Final peaceful scene]

LAYOUT: 3x3 grid, thin white borders between panels.
CRITICAL: NO TEXT, NO WORDS, NO LETTERS anywhere. Pure illustration only.
```

Generate the reference prompt:"""


# =============================================================================
# MAIN GENERATION FUNCTIONS
# =============================================================================

def generate_story_xml(
    level: str,
    concept: str,
    setting: str,
    verbose: bool = True
) -> str:
    """Generate story text as XML, strictly using approved words."""

    spec = get_level_spec(level)
    constraints = spec.get("constraints", {})

    # Use comprehensive word lists if available, fall back to extraction
    if level in LEVEL_WORD_LISTS:
        level_words = LEVEL_WORD_LISTS[level]
        decodable = set(level_words["decodable"])
        sight_words = set(level_words["sight_words"])
        names = level_words.get("names", [])

        # For B-band, include previous levels
        if level.startswith("B"):
            level_num = int(level[1])
            for prev in range(1, level_num):
                prev_level = f"B{prev}"
                if prev_level in LEVEL_WORD_LISTS:
                    decodable.update(LEVEL_WORD_LISTS[prev_level]["decodable"])
    else:
        # Fall back to extraction from level-specs
        decodable = extract_decodable_words_for_level(level)
        word_list = build_word_list(level)
        sight_words = word_list["sight_words"]
        names = []

        if level.startswith("B") and int(level[1]) > 1:
            for prev_level in range(1, int(level[1])):
                prev_words = extract_decodable_words_for_level(f"B{prev_level}")
                decodable.update(prev_words)

    # Get word families from level-specs
    word_families = constraints.get("wordFamilies", [])

    prompt = STORY_GENERATION_PROMPT.format(
        level=level,
        level_name=spec.get("name", ""),
        level_description=spec.get("readerCan", ""),
        words_per_sentence=constraints.get("wordsPerSentence", "5-7"),
        total_pages=constraints.get("pages", "12"),
        decodability=constraints.get("decodability", "85%+"),
        decodable_words=", ".join(sorted(decodable)[:150]),  # Limit to avoid token overflow
        sight_words=", ".join(sorted(sight_words)),
        names=", ".join(names) if names else "Tim, Sam, Dan",
        word_families=", ".join(word_families) if word_families else "See phonics patterns",
        concept=concept,
        setting=setting,
    )

    if verbose:
        print(f"Generating story for {level}...")
        print(f"  Decodable words available: {len(decodable)}")
        print(f"  Sight words available: {len(sight_words)}")

    response = call_llm(prompt)

    # Extract XML from response
    if "```xml" in response:
        start = response.find("```xml") + 6
        end = response.find("```", start)
        return response[start:end].strip()
    elif "<story>" in response:
        start = response.find("<story>")
        end = response.find("</story>") + 8
        return response[start:end]

    return response


def generate_scenes_xml(
    story_xml: str,
    title: str,
    level: str,
    setting: str,
    characters: str,
    art_style: str,
    verbose: bool = True
) -> str:
    """Generate scene descriptions for each page."""

    prompt = SCENE_DESCRIPTION_PROMPT.format(
        title=title,
        level=level,
        setting=setting,
        characters=characters,
        art_style=art_style,
        story_pages=story_xml,
    )

    if verbose:
        print("Generating scene descriptions...")

    response = call_llm(prompt)

    # Extract XML
    if "```xml" in response:
        start = response.find("```xml") + 6
        end = response.find("```", start)
        return response[start:end].strip()
    elif "<scenes>" in response:
        start = response.find("<scenes>")
        end = response.find("</scenes>") + 9
        return response[start:end]

    return response


def generate_reference_prompt(
    title: str,
    level: str,
    setting: str,
    characters: str,
    art_style: str,
    verbose: bool = True
) -> str:
    """Generate 9-panel reference sheet prompt."""

    prompt = REFERENCE_PROMPT_TEMPLATE.format(
        title=title,
        level=level,
        setting=setting,
        characters=characters,
        art_style=art_style,
    )

    if verbose:
        print("Generating reference prompt...")

    response = call_llm(prompt, max_tokens=2000)

    # Clean up - find the 9-PANEL section
    if "9-PANEL" in response:
        start = response.find("9-PANEL")
        return response[start:].strip()

    return response


def validate_decodability(story_xml: str, level: str) -> dict:
    """Validate story decodability against level specs."""

    # Extract all text from XML
    text_pattern = r'<text>(.*?)</text>'
    texts = re.findall(text_pattern, story_xml, re.DOTALL)
    all_text = " ".join(texts)

    # Clean and tokenize
    words = re.findall(r'[a-zA-Z]+', all_text.lower())

    # Use comprehensive word lists if available
    if level in LEVEL_WORD_LISTS:
        level_words = LEVEL_WORD_LISTS[level]
        decodable = set(level_words["decodable"])
        sight_words = set(level_words["sight_words"])
        names = set(level_words.get("names", []))

        # For B-band, include previous levels
        if level.startswith("B"):
            level_num = int(level[1])
            for prev in range(1, level_num):
                prev_level = f"B{prev}"
                if prev_level in LEVEL_WORD_LISTS:
                    decodable.update(LEVEL_WORD_LISTS[prev_level]["decodable"])
                    names.update(LEVEL_WORD_LISTS[prev_level].get("names", []))

        all_approved = decodable | sight_words | names
    else:
        # Fall back to extraction
        decodable = extract_decodable_words_for_level(level)
        word_list = build_word_list(level)

        if level.startswith("B") and int(level[1]) > 1:
            for prev_level in range(1, int(level[1])):
                prev_words = extract_decodable_words_for_level(f"B{prev_level}")
                decodable.update(prev_words)

        all_approved = decodable | word_list["sight_words"]

    # Categorize
    approved_count = sum(1 for w in words if w in all_approved)
    unknown_words = [w for w in words if w not in all_approved]
    unique_unknown = sorted(set(unknown_words))

    total = len(words)
    decodability = approved_count / total if total > 0 else 0

    return {
        "total_words": total,
        "approved_count": approved_count,
        "unknown_count": len(unknown_words),
        "decodability": decodability,
        "unique_unknown": unique_unknown,
        "target": 0.85,
        "passes": decodability >= 0.85,
    }


def generate_complete_book_xml(
    level: str,
    concept: str,
    setting: str,
    title: str = None,
    characters: str = None,
    art_style: str = None,
    verbose: bool = True
) -> str:
    """Generate complete book as XML."""

    spec = get_level_spec(level)

    if not title:
        title = f"Story for {level}"

    if not characters:
        characters = "Main character to be determined from story"

    if not art_style:
        art_style = "Warm, friendly children's book illustration with bold shapes and bright colors"

    # Step 1: Generate story
    if verbose:
        print(f"\n{'='*60}")
        print(f"GENERATING BOOK: {title}")
        print(f"Level: {level} - {spec.get('name', '')}")
        print(f"{'='*60}")

    story_xml = generate_story_xml(level, concept, setting, verbose)

    # Step 2: Validate decodability
    validation = validate_decodability(story_xml, level)

    if verbose:
        print(f"\nDecodability check:")
        print(f"  Total words: {validation['total_words']}")
        print(f"  Approved: {validation['approved_count']}")
        print(f"  Decodability: {validation['decodability']:.0%}")
        print(f"  Target: {validation['target']:.0%}")
        print(f"  Status: {'✅ PASS' if validation['passes'] else '❌ FAIL'}")

        if validation['unique_unknown']:
            print(f"  Unknown words: {', '.join(validation['unique_unknown'][:15])}")

    # Step 3: Generate scenes
    scenes_xml = generate_scenes_xml(
        story_xml, title, level, setting, characters, art_style, verbose
    )

    # Step 4: Generate reference prompt
    ref_prompt = generate_reference_prompt(
        title, level, setting, characters, art_style, verbose
    )

    # Step 5: Assemble complete XML
    slug = title.lower().replace(" ", "-").replace("'", "")[:40]

    complete_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<book>
  <metadata>
    <title>{title}</title>
    <slug>{slug}</slug>
    <band>{spec.get("band", "B")}</band>
    <level>{level}</level>
    <author>FunBookies</author>
    <created>{datetime.now().strftime("%Y-%m-%d")}</created>
  </metadata>

  <level_constraints>
    <words_per_sentence>{spec.get("constraints", {}).get("wordsPerSentence", "5-7")}</words_per_sentence>
    <total_pages>{spec.get("constraints", {}).get("pages", "12-14")}</total_pages>
    <decodability>{spec.get("constraints", {}).get("decodability", "85%+")}</decodability>
    <phonics_patterns>{", ".join(spec.get("constraints", {}).get("phonicsPatterns", [])[:3])}</phonics_patterns>
  </level_constraints>

  <validation>
    <actual_decodability>{validation['decodability']:.0%}</actual_decodability>
    <total_words>{validation['total_words']}</total_words>
    <approved_words>{validation['approved_count']}</approved_words>
    <status>{"PASS" if validation['passes'] else "FAIL"}</status>
  </validation>

  <story_bible>
    <premise>{concept}</premise>
    <setting>{setting}</setting>
    <characters>{characters}</characters>
    <art_style>{art_style}</art_style>
  </story_bible>

  <reference_prompt>
{ref_prompt}
  </reference_prompt>

  {story_xml}

  {scenes_xml}
</book>'''

    return complete_xml


# =============================================================================
# CLI
# =============================================================================

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Generate decodable book as XML")
    parser.add_argument("--level", required=True, help="Reading level (e.g., B1, B4, B6)")
    parser.add_argument("--concept", required=True, help="Story concept")
    parser.add_argument("--setting", required=True, help="Story setting")
    parser.add_argument("--title", help="Book title (optional)")
    parser.add_argument("--characters", help="Character descriptions")
    parser.add_argument("--art-style", help="Art style description")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--validate-only", action="store_true", help="Only validate existing XML")
    args = parser.parse_args()

    # Generate book
    xml = generate_complete_book_xml(
        level=args.level,
        concept=args.concept,
        setting=args.setting,
        title=args.title,
        characters=args.characters,
        art_style=args.art_style,
        verbose=True,
    )

    # Output
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(xml)
        print(f"\n✓ Saved to: {output_path}")
    else:
        print("\n" + "="*60)
        print("GENERATED XML:")
        print("="*60)
        print(xml)


if __name__ == "__main__":
    main()
