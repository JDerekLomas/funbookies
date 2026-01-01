"""
Regenerate specific pages as POV shots (no character in frame).
"""

import sys
import time
sys.path.insert(0, '/Users/dereklomas/minibooks/src')

from image_gen import ImageGenerator
from character_gen import VOLCANO_PAGES, MASTER_STYLE, build_consistent_prompt

# Pages to regenerate as POV (include_char: False in VOLCANO_PAGES)
POV_PAGES = [p for p in VOLCANO_PAGES if not p.get("include_char", True)]

def regenerate_pov_pages():
    gen = ImageGenerator(backend="mulerouter")
    gen.output_dir = gen.output_dir.parent.parent / "web" / "books" / "images"
    gen.output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Regenerating {len(POV_PAGES)} POV pages...\n")

    for page in POV_PAGES:
        page_num = page["page"]
        scene = page["scene"]

        # Build POV prompt (no character description)
        prompt = f"""SCENE: {scene}

STYLE: {MASTER_STYLE}"""

        filename = f"volcano_page{page_num:02d}"

        print(f"Page {page_num}: {scene[:50]}...")

        try:
            path = gen.generate(prompt=prompt, filename=filename, style="")
            print(f"  OK: {path}")
        except Exception as e:
            print(f"  FAIL: {e}")

        # Delay between requests to avoid rate limiting
        time.sleep(3)

    print("\nDone!")

if __name__ == "__main__":
    regenerate_pov_pages()
