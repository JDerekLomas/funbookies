"""
Word Banks for Funbookies Story Generation

Provides phonics-aligned word lists, sight words, and validation
for decodable book creation.

Usage:
    from word_banks import WordBanks

    wb = WordBanks()

    # Check if a word is decodable at a given level
    wb.is_decodable("cat", level="orange")  # True
    wb.is_decodable("cake", level="orange")  # False (needs magic e)
    wb.is_decodable("cake", level="purple")  # True

    # Get words for a phonics pattern
    wb.get_cvc_words("short_a")  # ["cat", "hat", "bat", ...]

    # Validate a story's word list
    wb.validate_story_words(story_json, level="orange")

    # Get sight words for a level
    wb.get_sight_words(level="pre_primer")

    # Check if word is a heart word (irregular)
    wb.is_heart_word("said")  # True
    wb.get_heart_word_info("said")  # {"tricky": "ai", "sounds_like": "sed", ...}
"""

import json
from pathlib import Path
from typing import Optional


class WordBanks:
    def __init__(self, json_path: Optional[str] = None):
        if json_path is None:
            json_path = Path(__file__).parent / "word_banks.json"

        with open(json_path, 'r') as f:
            self.data = json.load(f)

        # Build lookup sets for fast validation
        self._build_lookups()

    def _build_lookups(self):
        """Build fast lookup structures from the word bank data."""

        # All CVC words as a set
        self.cvc_words = set()
        for vowel_words in self.data["decodable"]["cvc"].values():
            self.cvc_words.update(word.lower() for word in vowel_words)

        # All digraph words
        self.digraph_words = set()
        for pattern_data in self.data["decodable"]["digraphs"].values():
            if isinstance(pattern_data, dict):
                for position_words in pattern_data.values():
                    if isinstance(position_words, list):
                        self.digraph_words.update(word.lower() for word in position_words)
            elif isinstance(pattern_data, list):
                self.digraph_words.update(word.lower() for word in pattern_data)

        # All blend words
        self.blend_words = set()
        for category in self.data["decodable"]["blends"].values():
            if isinstance(category, dict):
                for words in category.values():
                    self.blend_words.update(word.lower() for word in words)
            elif isinstance(category, list):
                self.blend_words.update(word.lower() for word in category)

        # All magic e words
        self.magic_e_words = set()
        for vowel_words in self.data["decodable"]["magic_e"].values():
            self.magic_e_words.update(word.lower() for word in vowel_words)

        # Sight words by level
        self.sight_words = {
            "pre_primer": set(w.lower() for w in self.data["sight_words"]["dolch"]["pre_primer"]),
            "primer": set(w.lower() for w in self.data["sight_words"]["dolch"]["primer"]),
            "first_grade": set(w.lower() for w in self.data["sight_words"]["dolch"]["first_grade"]),
            "second_grade": set(w.lower() for w in self.data["sight_words"]["dolch"]["second_grade"]),
        }

        # Heart words lookup
        self.heart_words = {
            item["word"].lower(): item
            for item in self.data["heart_words"]["words"]
        }

        # Combined decodable sets by level
        self.level_decodable = {
            "yellow": self.cvc_words,
            "orange": self.cvc_words | self.digraph_words,
            "red": self.cvc_words | self.digraph_words | self.blend_words,
            "purple": self.cvc_words | self.digraph_words | self.blend_words | self.magic_e_words,
        }

        # All sight words combined (any level) for general lookup
        self.all_sight_words = set()
        for level_words in self.sight_words.values():
            self.all_sight_words.update(level_words)

        # Common exclamations and interjections (not in standard lists but OK)
        self.exclamations = {"wow", "oh", "ooh", "ah", "uh", "hey", "yay", "boo", "ow", "oof", "whoa", "yikes", "oops", "phew", "hmm", "shh", "psst"}

        # Sight words allowed by level (cumulative - each level includes previous)
        self.level_sight_words = {
            "yellow": self.sight_words["pre_primer"],
            "orange": self.sight_words["pre_primer"] | self.sight_words["primer"],
            "red": self.sight_words["pre_primer"] | self.sight_words["primer"] | self.sight_words["first_grade"],
            "purple": self.sight_words["pre_primer"] | self.sight_words["primer"] | self.sight_words["first_grade"] | self.sight_words["second_grade"],
        }

    # -------------------------------------------------------------------------
    # Word Validation
    # -------------------------------------------------------------------------

    def is_decodable(self, word: str, level: str = "orange") -> bool:
        """Check if a word is decodable at the given level."""
        word = word.lower().strip()
        return word in self.level_decodable.get(level, self.level_decodable["orange"])

    def is_sight_word(self, word: str, level: str = "pre_primer") -> bool:
        """Check if a word is in the sight word list for the given level."""
        word = word.lower().strip()

        if level in self.sight_words:
            return word in self.sight_words[level]
        elif level in self.level_sight_words:
            return word in self.level_sight_words[level]
        return False

    def is_heart_word(self, word: str) -> bool:
        """Check if a word is a heart word (has irregular parts)."""
        return word.lower().strip() in self.heart_words

    def get_heart_word_info(self, word: str) -> Optional[dict]:
        """Get information about a heart word's tricky parts."""
        return self.heart_words.get(word.lower().strip())

    def classify_word(self, word: str, level: str = "orange", character_names: list = None) -> dict:
        """
        Classify a word into its type for the given level.

        Returns dict with:
            - type: "decodable", "sight_word", "heart_word", "exclamation", "character", "vocabulary", "unknown"
            - decodable_at_level: bool
            - pattern: phonics pattern if decodable
            - heart_info: dict if heart word
        """
        word = word.lower().strip()
        character_names = [n.lower() for n in (character_names or [])]

        result = {
            "word": word,
            "type": "unknown",
            "decodable_at_level": False,
            "pattern": None,
            "heart_info": None
        }

        # Check if it's a character name (always allowed)
        if word in character_names:
            result["type"] = "character"
            result["decodable_at_level"] = True  # Characters are always OK
            return result

        # Check if exclamation (always allowed)
        if word in self.exclamations:
            result["type"] = "exclamation"
            result["decodable_at_level"] = True  # Exclamations are always OK
            return result

        # Check if decodable at this level
        if self.is_decodable(word, level):
            result["type"] = "decodable"
            result["decodable_at_level"] = True
            result["pattern"] = self._get_pattern(word)
            return result

        # Check if sight word at this level
        if word in self.level_sight_words.get(level, set()):
            result["type"] = "sight_word"

            # Also check if it's a heart word
            if self.is_heart_word(word):
                result["heart_info"] = self.get_heart_word_info(word)
                result["type"] = "heart_word"

            return result

        # Check if heart word (even if not in level's sight word list)
        if self.is_heart_word(word):
            result["type"] = "heart_word"
            result["heart_info"] = self.get_heart_word_info(word)
            return result

        # Check if it's a sight word at ANY level
        if word in self.all_sight_words:
            result["type"] = "sight_word"
            return result

        # Check if decodable at a higher level
        for check_level in ["orange", "red", "purple"]:
            if self.is_decodable(word, check_level):
                result["type"] = "decodable"
                result["decodable_at_level"] = False
                result["pattern"] = self._get_pattern(word)
                result["requires_level"] = check_level
                return result

        # Unknown word - treat as vocabulary (topic word)
        result["type"] = "vocabulary"
        return result

    def _get_pattern(self, word: str) -> str:
        """Determine the phonics pattern of a decodable word."""
        word = word.lower()

        if word in self.cvc_words:
            return "cvc"
        if word in self.digraph_words:
            return "digraph"
        if word in self.blend_words:
            return "blend"
        if word in self.magic_e_words:
            return "magic_e"
        return "unknown"

    # -------------------------------------------------------------------------
    # Word Retrieval
    # -------------------------------------------------------------------------

    def get_cvc_words(self, vowel: str = None) -> list:
        """Get CVC words, optionally filtered by vowel (short_a, short_e, etc.)."""
        if vowel:
            return list(self.data["decodable"]["cvc"].get(vowel, []))
        return list(self.cvc_words)

    def get_digraph_words(self, digraph: str = None) -> list:
        """Get digraph words, optionally filtered by digraph (ch, sh, th, etc.)."""
        if digraph:
            pattern_data = self.data["decodable"]["digraphs"].get(digraph, {})
            words = []
            if isinstance(pattern_data, dict):
                for position_words in pattern_data.values():
                    words.extend(position_words)
            return words
        return list(self.digraph_words)

    def get_blend_words(self, blend_type: str = None) -> list:
        """Get blend words, optionally filtered by type (initial_l, initial_r, etc.)."""
        if blend_type:
            category = self.data["decodable"]["blends"].get(blend_type, {})
            words = []
            if isinstance(category, dict):
                for blend_words in category.values():
                    words.extend(blend_words)
            return words
        return list(self.blend_words)

    def get_magic_e_words(self, vowel: str = None) -> list:
        """Get magic e words, optionally filtered by vowel (a_e, i_e, etc.)."""
        if vowel:
            return list(self.data["decodable"]["magic_e"].get(vowel, []))
        return list(self.magic_e_words)

    def get_sight_words(self, level: str = "pre_primer") -> list:
        """Get sight words for a given level."""
        if level in self.sight_words:
            return list(self.sight_words[level])
        return []

    def get_all_sight_words_up_to(self, level: str) -> list:
        """Get all sight words up to and including the given level."""
        levels = ["pre_primer", "primer", "first_grade", "second_grade"]
        try:
            idx = levels.index(level)
            words = set()
            for l in levels[:idx + 1]:
                words.update(self.sight_words[l])
            return list(words)
        except ValueError:
            return list(self.sight_words.get("pre_primer", []))

    def get_sound_effects(self, category: str = None) -> list:
        """Get onomatopoeia/sound effect words."""
        if category:
            return self.data["sound_effects"].get(category, [])

        all_sounds = []
        for cat, words in self.data["sound_effects"].items():
            if cat != "_note":
                all_sounds.extend(words)
        return all_sounds

    def get_topic_vocabulary(self, category: str, subcategory: str = None) -> list:
        """Get topic vocabulary words."""
        cat_data = self.data["topic_vocabulary"].get(category, {})

        if isinstance(cat_data, list):
            return cat_data

        if subcategory:
            return cat_data.get(subcategory, [])

        # Return all words in category
        words = []
        for key, val in cat_data.items():
            if key != "_note" and isinstance(val, list):
                words.extend(val)
        return words

    # -------------------------------------------------------------------------
    # Story Validation
    # -------------------------------------------------------------------------

    def validate_story_words(self, story_json: dict, level: str = "orange",
                              character_names: list = None, topic_words: list = None) -> dict:
        """
        Validate all words in a story against the phonics level.

        Args:
            story_json: Story data with pages
            level: Phonics level ("yellow", "orange", "red", "purple")
            character_names: List of character names (always allowed)
            topic_words: List of topic vocabulary words (allowed but tracked separately)

        Returns:
            {
                "valid": bool,
                "level": str,
                "total_words": int,
                "decodable_count": int,
                "sight_word_count": int,
                "heart_word_count": int,
                "exclamation_count": int,
                "character_count": int,
                "vocabulary_count": int,
                "unknown_count": int,
                "accessible_percent": float (decodable + sight + heart + exclamations + characters),
                "strict_decodable_percent": float (only decodable words),
                "issues": [{"word": str, "issue": str, "page": int}, ...],
                "word_breakdown": {word: classification, ...}
            }
        """
        # Auto-detect character names from story if not provided
        if character_names is None:
            character_names = []
            char_data = story_json.get("character", {})
            if isinstance(char_data, dict) and "name" in char_data:
                character_names.append(char_data["name"])
            elif isinstance(char_data, str):
                # Try to extract first word as name
                first_word = char_data.split()[0] if char_data else ""
                if first_word and first_word[0].isupper():
                    character_names.append(first_word)

        # Auto-detect topic words from word_list if present
        if topic_words is None:
            topic_words = []
            word_list = story_json.get("word_list", {})
            if isinstance(word_list, dict):
                topic_words.extend(word_list.get("new", []))
                vocab = word_list.get("vocabulary", {})
                if isinstance(vocab, dict):
                    topic_words.extend(vocab.get("topic", []))

        topic_words_lower = [w.lower() for w in topic_words]

        result = {
            "valid": True,
            "level": level,
            "total_words": 0,
            "decodable_count": 0,
            "sight_word_count": 0,
            "heart_word_count": 0,
            "exclamation_count": 0,
            "character_count": 0,
            "vocabulary_count": 0,
            "unknown_count": 0,
            "accessible_percent": 0.0,
            "strict_decodable_percent": 0.0,
            "issues": [],
            "word_breakdown": {}
        }

        # Extract all words from story
        all_words = []
        for page in story_json.get("pages", []):
            text = page.get("text", "")
            if text and page.get("type") in ["story", "cover"]:
                # Extract words (remove punctuation)
                words = self._extract_words(text)
                for word in words:
                    all_words.append({"word": word, "page": page.get("page", 0)})

        result["total_words"] = len(all_words)

        # Classify each word
        for item in all_words:
            word = item["word"]
            page = item["page"]

            classification = self.classify_word(word, level, character_names)
            result["word_breakdown"][word] = classification

            word_type = classification["type"]

            if word_type == "decodable":
                if classification["decodable_at_level"]:
                    result["decodable_count"] += 1
                else:
                    result["issues"].append({
                        "word": word,
                        "issue": f"Requires level '{classification.get('requires_level', 'higher')}'",
                        "page": page
                    })
                    result["unknown_count"] += 1
            elif word_type == "sight_word":
                result["sight_word_count"] += 1
            elif word_type == "heart_word":
                result["heart_word_count"] += 1
            elif word_type == "exclamation":
                result["exclamation_count"] += 1
            elif word_type == "character":
                result["character_count"] += 1
            elif word_type == "vocabulary":
                # Check if it's a known topic word (acceptable)
                if word.lower() in topic_words_lower:
                    result["vocabulary_count"] += 1
                else:
                    result["vocabulary_count"] += 1
                    # Only flag as issue if it's not a recognized topic word
                    # result["issues"].append({
                    #     "word": word,
                    #     "issue": "Unknown vocabulary word",
                    #     "page": page
                    # })
            else:
                result["unknown_count"] += 1
                result["issues"].append({
                    "word": word,
                    "issue": "Unknown word - not in any word bank",
                    "page": page
                })

        # Calculate percentages
        if result["total_words"] > 0:
            # Accessible = everything a beginning reader can handle
            accessible = (result["decodable_count"] + result["sight_word_count"] +
                         result["heart_word_count"] + result["exclamation_count"] +
                         result["character_count"])
            result["accessible_percent"] = (accessible / result["total_words"]) * 100

            # Strict = only phonetically decodable words
            result["strict_decodable_percent"] = (result["decodable_count"] / result["total_words"]) * 100

        # Set valid flag (aim for 70%+ accessible)
        # Vocabulary words are OK if they're topic words (lava, volcano, etc.)
        # They'll be taught with pictures
        if result["accessible_percent"] < 60:
            result["valid"] = False
            result["issues"].append({
                "word": None,
                "issue": f"Only {result['accessible_percent']:.1f}% accessible (target: 60%+)",
                "page": None
            })

        return result

    def _extract_words(self, text: str) -> list:
        """Extract words from text, removing punctuation."""
        import re
        # Remove punctuation except apostrophes in contractions
        text = re.sub(r'[^\w\s\']', ' ', text)
        words = text.lower().split()
        # Filter out empty strings and pure punctuation
        return [w.strip("'") for w in words if w.strip("'")]

    def suggest_alternatives(self, word: str, level: str = "orange") -> list:
        """
        Suggest decodable alternatives for a word that's too advanced.

        Returns list of simpler synonyms or related words.
        """
        # Simple synonym mapping
        synonyms = {
            "beautiful": ["nice", "pretty"],
            "happy": ["glad"],
            "scared": ["sad"],
            "quickly": ["fast"],
            "slowly": ["slow"],
            "large": ["big"],
            "small": ["little"],
            "begin": ["start"],
            "finish": ["end", "stop"],
            "want": ["wish"],
            "because": ["so"],
        }

        word = word.lower()
        suggestions = synonyms.get(word, [])

        # Filter to only include words decodable at level
        return [s for s in suggestions if self.is_decodable(s, level) or self.is_sight_word(s, level)]

    # -------------------------------------------------------------------------
    # Story Generation Helpers
    # -------------------------------------------------------------------------

    def get_words_for_story(self, level: str, count: int = 20) -> dict:
        """
        Get a balanced set of words suitable for a story at the given level.

        Returns dict with:
            - decodable: list of decodable words
            - sight: list of sight words
            - sound_effects: list of onomatopoeia
        """
        import random

        decodable_pool = list(self.level_decodable.get(level, self.cvc_words))
        sight_pool = list(self.level_sight_words.get(level, self.sight_words["pre_primer"]))
        sound_pool = self.get_sound_effects()

        return {
            "decodable": random.sample(decodable_pool, min(count, len(decodable_pool))),
            "sight": random.sample(sight_pool, min(count // 2, len(sight_pool))),
            "sound_effects": random.sample(sound_pool, min(5, len(sound_pool)))
        }

    def get_rhyming_words(self, word: str, level: str = "orange") -> list:
        """Find words that rhyme with the given word at the specified level."""
        word = word.lower()

        # Simple rhyme detection: same ending
        if len(word) < 2:
            return []

        ending = word[-2:]  # Last two letters
        rhymes = []

        for w in self.level_decodable.get(level, self.cvc_words):
            if w != word and w.endswith(ending):
                rhymes.append(w)

        return rhymes[:10]  # Limit results

    def get_word_family(self, pattern: str) -> list:
        """Get all words in a word family (e.g., '-at', '-op', '-ug')."""
        family = []

        for word in self.cvc_words:
            if word.endswith(pattern):
                family.append(word)

        return sorted(family)

    # -------------------------------------------------------------------------
    # Prompt Generation
    # -------------------------------------------------------------------------

    def get_prompt_constraints(self, level: str = "orange") -> str:
        """Generate phonics constraint text for LLM prompts."""
        constraints = {
            "yellow": """
PHONICS LEVEL: Yellow (CVC Only)
- Use ONLY simple CVC words (consonant-vowel-consonant): cat, run, hot, big, etc.
- NO blends (no 'st', 'cr', 'bl', etc.)
- NO digraphs except as sight words
- Sight words allowed: {sight_words}
""",
            "orange": """
PHONICS LEVEL: Orange (CVC + Digraphs)
- CVC words: cat, run, hot, big, etc.
- Digraphs OK: sh, ch, th, ck, wh (ship, chat, with, back)
- NO blends yet (no 'st', 'cr', 'bl', etc.)
- Sight words allowed: {sight_words}
""",
            "red": """
PHONICS LEVEL: Red (CVC + Digraphs + Blends)
- CVC words: cat, run, hot, big, etc.
- Digraphs OK: sh, ch, th, ck, wh
- Blends OK: st, cr, bl, sp, tr, etc. (stop, crab, blue, spin, trip)
- NO magic e yet (no 'cake', 'bike', 'home')
- Sight words allowed: {sight_words}
""",
            "purple": """
PHONICS LEVEL: Purple (CVC + Digraphs + Blends + Magic E)
- CVC words: cat, run, hot, big, etc.
- Digraphs OK: sh, ch, th, ck, wh
- Blends OK: st, cr, bl, sp, tr, etc.
- Magic E OK: cake, bike, home, cute, etc.
- Sight words allowed: {sight_words}
"""
        }

        template = constraints.get(level, constraints["orange"])
        sight_list = ", ".join(sorted(self.level_sight_words.get(level, []))[:30]) + "..."

        return template.format(sight_words=sight_list)

    def get_word_list_for_prompt(self, level: str, target_words: list = None) -> str:
        """
        Generate a word list section for LLM prompts.

        If target_words provided, includes them with their classifications.
        """
        lines = [f"APPROVED WORD LIST FOR LEVEL '{level.upper()}':", ""]

        # Sample CVC words
        cvc_sample = list(self.cvc_words)[:30]
        lines.append(f"CVC words: {', '.join(sorted(cvc_sample))}")

        if level in ["orange", "red", "purple"]:
            digraph_sample = list(self.digraph_words)[:20]
            lines.append(f"Digraph words: {', '.join(sorted(digraph_sample))}")

        if level in ["red", "purple"]:
            blend_sample = list(self.blend_words)[:20]
            lines.append(f"Blend words: {', '.join(sorted(blend_sample))}")

        if level == "purple":
            magic_sample = list(self.magic_e_words)[:20]
            lines.append(f"Magic E words: {', '.join(sorted(magic_sample))}")

        sight = list(self.level_sight_words.get(level, []))
        lines.append(f"Sight words: {', '.join(sorted(sight))}")

        # Heart words with notes
        lines.append("")
        lines.append("HEART WORDS (memorize tricky parts):")
        for hw in list(self.heart_words.values())[:10]:
            lines.append(f"  - {hw['word']}: '{hw['tricky']}' is tricky, sounds like '{hw['sounds_like']}'")

        return "\n".join(lines)


# Convenience function for quick access
def load_word_banks() -> WordBanks:
    """Load and return a WordBanks instance."""
    return WordBanks()


if __name__ == "__main__":
    # Demo usage
    wb = WordBanks()

    print("=== Word Banks Demo ===\n")

    # Test classification
    test_words = ["cat", "ship", "stop", "cake", "said", "volcano", "the"]
    print("Word Classifications (level: orange):")
    for word in test_words:
        c = wb.classify_word(word, "orange")
        print(f"  {word}: {c['type']}", end="")
        if c.get('heart_info'):
            print(f" (tricky: {c['heart_info']['tricky']})", end="")
        if not c.get('decodable_at_level') and c.get('requires_level'):
            print(f" (needs level: {c['requires_level']})", end="")
        print()

    print("\n" + "="*50)

    # Test rhymes
    print("\nWords that rhyme with 'cat':")
    print(f"  {wb.get_rhyming_words('cat')}")

    print("\nWord family '-op':")
    print(f"  {wb.get_word_family('op')}")

    print("\n" + "="*50)

    # Test story validation
    sample_story = {
        "pages": [
            {"page": 1, "type": "cover", "text": "Gus and the Volcano"},
            {"page": 3, "type": "story", "text": "Gus ran up the hill."},
            {"page": 4, "type": "story", "text": "Gus saw a big hole."},
            {"page": 5, "type": "story", "text": "Red! Hot! Lava!"},
        ]
    }

    print("\nStory Validation:")
    result = wb.validate_story_words(sample_story, "orange")
    print(f"  Valid: {result['valid']}")
    print(f"  Decodable: {result['decodable_percent']:.1f}%")
    print(f"  Issues: {len(result['issues'])}")
    for issue in result['issues']:
        print(f"    - {issue}")
