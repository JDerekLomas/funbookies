#!/usr/bin/env python3
"""
Generate blend, digraph, and vowel team sounds using ElevenLabs with IPA phoneme tags.

Uses SSML phoneme tags for precise pronunciation control.
Requires eleven_turbo_v2 model (phoneme tags don't work with v2.5).

IPA Reference:
- /ʃ/ = sh (ship)
- /tʃ/ = ch (chip)
- /θ/ = th voiceless (thin)
- /ð/ = th voiced (this)
- /ŋ/ = ng (ring)
- /eɪ/ = long a (cake)
- /aɪ/ = long i (bike)
- /oʊ/ = long o (home)
- /ju/ = long u (cute)
"""

import os
import requests
from pathlib import Path
from time import sleep

# API Key
ELEVENLABS_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
if not ELEVENLABS_KEY:
    print("Error: ELEVENLABS_API_KEY environment variable not set")
    print("Set it with: export ELEVENLABS_API_KEY='your-key'")
    exit(1)

# Voice - use a clear American voice
# Rachel is a clear, neutral American voice good for education
VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Rachel

# Output directory
OUTPUT_DIR = Path(__file__).parent.parent / "public" / "audio" / "phonemes"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Phoneme definitions with IPA
# Format: filename -> (SSML with phoneme tag, description)
PHONEMES = {
    # === CONSONANT BLENDS ===
    # These blend two consonant sounds together
    "bl": ('<phoneme alphabet="ipa" ph="bl">bl</phoneme>', "bl as in blue"),
    "br": ('<phoneme alphabet="ipa" ph="bɹ">br</phoneme>', "br as in brown"),
    "cl": ('<phoneme alphabet="ipa" ph="kl">cl</phoneme>', "cl as in clap"),
    "cr": ('<phoneme alphabet="ipa" ph="kɹ">cr</phoneme>', "cr as in crab"),
    "dr": ('<phoneme alphabet="ipa" ph="dɹ">dr</phoneme>', "dr as in drum"),
    "fl": ('<phoneme alphabet="ipa" ph="fl">fl</phoneme>', "fl as in flag"),
    "fr": ('<phoneme alphabet="ipa" ph="fɹ">fr</phoneme>', "fr as in frog"),
    "gl": ('<phoneme alphabet="ipa" ph="ɡl">gl</phoneme>', "gl as in glass"),
    "gr": ('<phoneme alphabet="ipa" ph="ɡɹ">gr</phoneme>', "gr as in green"),
    "pl": ('<phoneme alphabet="ipa" ph="pl">pl</phoneme>', "pl as in plum"),
    "pr": ('<phoneme alphabet="ipa" ph="pɹ">pr</phoneme>', "pr as in pretty"),
    "sk": ('<phoneme alphabet="ipa" ph="sk">sk</phoneme>', "sk as in skip"),
    "sl": ('<phoneme alphabet="ipa" ph="sl">sl</phoneme>', "sl as in sled"),
    "sm": ('<phoneme alphabet="ipa" ph="sm">sm</phoneme>', "sm as in smile"),
    "sn": ('<phoneme alphabet="ipa" ph="sn">sn</phoneme>', "sn as in snap"),
    "sp": ('<phoneme alphabet="ipa" ph="sp">sp</phoneme>', "sp as in spin"),
    "st": ('<phoneme alphabet="ipa" ph="st">st</phoneme>', "st as in stop"),
    "sw": ('<phoneme alphabet="ipa" ph="sw">sw</phoneme>', "sw as in swim"),
    "tr": ('<phoneme alphabet="ipa" ph="tɹ">tr</phoneme>', "tr as in tree"),
    "tw": ('<phoneme alphabet="ipa" ph="tw">tw</phoneme>', "tw as in twin"),

    # === DIGRAPHS ===
    # Two letters that make ONE sound
    "sh": ('<phoneme alphabet="ipa" ph="ʃ">sh</phoneme>', "sh as in ship"),
    "ch": ('<phoneme alphabet="ipa" ph="tʃ">ch</phoneme>', "ch as in chip"),
    "th_voiceless": ('<phoneme alphabet="ipa" ph="θ">th</phoneme>', "th as in thin"),
    "th_voiced": ('<phoneme alphabet="ipa" ph="ð">th</phoneme>', "th as in this"),
    "wh": ('<phoneme alphabet="ipa" ph="w">wh</phoneme>', "wh as in what"),
    "ph": ('<phoneme alphabet="ipa" ph="f">ph</phoneme>', "ph as in phone"),
    "ng": ('<phoneme alphabet="ipa" ph="ŋ">ng</phoneme>', "ng as in ring"),
    "ck": ('<phoneme alphabet="ipa" ph="k">ck</phoneme>', "ck as in duck"),
    "qu": ('<phoneme alphabet="ipa" ph="kw">qu</phoneme>', "qu as in queen"),
    "nk": ('<phoneme alphabet="ipa" ph="ŋk">nk</phoneme>', "nk as in sink"),

    # === R-CONTROLLED VOWELS ===
    "ar": ('<phoneme alphabet="ipa" ph="ɑɹ">ar</phoneme>', "ar as in car"),
    "er": ('<phoneme alphabet="ipa" ph="ɝ">er</phoneme>', "er as in her"),
    "ir": ('<phoneme alphabet="ipa" ph="ɝ">ir</phoneme>', "ir as in bird"),
    "or": ('<phoneme alphabet="ipa" ph="ɔɹ">or</phoneme>', "or as in corn"),
    "ur": ('<phoneme alphabet="ipa" ph="ɝ">ur</phoneme>', "ur as in burn"),

    # === VOWEL TEAMS ===
    # Two vowels that make one sound
    "ai": ('<phoneme alphabet="ipa" ph="eɪ">ai</phoneme>', "ai as in rain"),
    "ay": ('<phoneme alphabet="ipa" ph="eɪ">ay</phoneme>', "ay as in day"),
    "ea": ('<phoneme alphabet="ipa" ph="i">ea</phoneme>', "ea as in read"),
    "ee": ('<phoneme alphabet="ipa" ph="i">ee</phoneme>', "ee as in tree"),
    "ie": ('<phoneme alphabet="ipa" ph="aɪ">ie</phoneme>', "ie as in pie"),
    "igh": ('<phoneme alphabet="ipa" ph="aɪ">igh</phoneme>', "igh as in night"),
    "oa": ('<phoneme alphabet="ipa" ph="oʊ">oa</phoneme>', "oa as in boat"),
    "oe": ('<phoneme alphabet="ipa" ph="oʊ">oe</phoneme>', "oe as in toe"),
    "oo_long": ('<phoneme alphabet="ipa" ph="u">oo</phoneme>', "oo as in moon"),
    "oo_short": ('<phoneme alphabet="ipa" ph="ʊ">oo</phoneme>', "oo as in book"),
    "ou": ('<phoneme alphabet="ipa" ph="aʊ">ou</phoneme>', "ou as in out"),
    "ow_long": ('<phoneme alphabet="ipa" ph="oʊ">ow</phoneme>', "ow as in snow"),
    "ow_short": ('<phoneme alphabet="ipa" ph="aʊ">ow</phoneme>', "ow as in cow"),
    "ue": ('<phoneme alphabet="ipa" ph="u">ue</phoneme>', "ue as in blue"),
    "ui": ('<phoneme alphabet="ipa" ph="u">ui</phoneme>', "ui as in fruit"),

    # === SPLIT DIGRAPHS (Magic E) ===
    # Long vowel sounds
    "a_e": ('<phoneme alphabet="ipa" ph="eɪ">a e</phoneme>', "a-e as in cake"),
    "e_e": ('<phoneme alphabet="ipa" ph="i">e e</phoneme>', "e-e as in Pete"),
    "i_e": ('<phoneme alphabet="ipa" ph="aɪ">i e</phoneme>', "i-e as in bike"),
    "o_e": ('<phoneme alphabet="ipa" ph="oʊ">o e</phoneme>', "o-e as in home"),
    "u_e": ('<phoneme alphabet="ipa" ph="ju">u e</phoneme>', "u-e as in cute"),

    # === SHORT VOWELS (for reference/consistency) ===
    "short_a": ('<phoneme alphabet="ipa" ph="æ">a</phoneme>', "short a as in cat"),
    "short_e": ('<phoneme alphabet="ipa" ph="ɛ">e</phoneme>', "short e as in bed"),
    "short_i": ('<phoneme alphabet="ipa" ph="ɪ">i</phoneme>', "short i as in pig"),
    "short_o": ('<phoneme alphabet="ipa" ph="ɑ">o</phoneme>', "short o as in hot"),
    "short_u": ('<phoneme alphabet="ipa" ph="ʌ">u</phoneme>', "short u as in cup"),
}


def generate_with_phoneme(ssml_text: str, output_path: Path, voice_id: str = VOICE_ID) -> bool:
    """Generate audio using ElevenLabs with SSML phoneme tags."""
    # Must use eleven_turbo_v2 for phoneme tag support (not v2.5!)
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    headers = {
        "xi-api-key": ELEVENLABS_KEY,
        "Content-Type": "application/json"
    }

    data = {
        "text": ssml_text,
        "model_id": "eleven_turbo_v2",  # Required for phoneme tags!
        "voice_settings": {
            "stability": 0.75,
            "similarity_boost": 0.75,
            "style": 0.0,
            "use_speaker_boost": True
        }
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            return True
        else:
            print(f"  Error {response.status_code}: {response.text[:100]}")
            return False
    except Exception as e:
        print(f"  Error: {e}")
        return False


def main():
    print("=" * 60)
    print("GENERATING PHONEME SOUNDS WITH ELEVENLABS IPA TAGS")
    print("=" * 60)
    print(f"Output: {OUTPUT_DIR}")
    print(f"Total phonemes: {len(PHONEMES)}")
    print()

    success = 0
    failed = 0

    for filename, (ssml, description) in PHONEMES.items():
        output_path = OUTPUT_DIR / f"{filename}.mp3"

        # Skip if already exists
        if output_path.exists():
            print(f"  {filename}: SKIP (exists)")
            success += 1
            continue

        print(f"  {filename}: {description}", end=" ... ")

        if generate_with_phoneme(ssml, output_path):
            print("OK")
            success += 1
        else:
            print("FAILED")
            failed += 1

        # Rate limiting
        sleep(0.3)

    print()
    print("=" * 60)
    print(f"Done! Success: {success}, Failed: {failed}")
    print(f"Files saved to: {OUTPUT_DIR}")
    print()
    print("To use in activities, update AudioUtils to check /audio/phonemes/")


if __name__ == "__main__":
    main()
