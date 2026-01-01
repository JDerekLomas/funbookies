"""
Generate images for Rats in the Castle book.
"""

import sys
import time
sys.path.insert(0, '/Users/dereklomas/minibooks/src')

from image_gen import ImageGenerator
from character_gen import CASTLE_PAGES, CHARACTERS, MASTER_STYLE, build_consistent_prompt

def generate_castle_book():
    gen = ImageGenerator(backend="mulerouter")
    gen.output_dir = gen.output_dir.parent.parent / "web" / "books" / "images"
    gen.output_dir.mkdir(parents=True, exist_ok=True)

    char = CHARACTERS["rita_rico_rats"]

    print(f"Generating {len(CASTLE_PAGES)} pages for Rats in the Castle...")
    print(f"Characters: {char['name']}")
    print(f"Description: {char['description'][:100]}...\n")

    failed_pages = []

    for page in CASTLE_PAGES:
        page_num = page["page"]
        scene = page["scene"]
        include_char = page.get("include_char", True)

        # Build prompt
        if include_char:
            prompt = f"""{char['description']}

SCENE: {char['name']} {scene}

STYLE: {MASTER_STYLE}, {char['style_ref']}"""
        else:
            prompt = f"""SCENE: {scene}

STYLE: {MASTER_STYLE}"""

        filename = f"castle_page{page_num:02d}"

        print(f"Page {page_num}...", end=" ", flush=True)

        try:
            path = gen.generate(prompt=prompt, filename=filename, style="")
            print("OK")
        except Exception as e:
            print(f"FAIL: {str(e)[:80]}")
            failed_pages.append(page)

        # Delay between requests
        time.sleep(3)

    # Retry failed pages
    if failed_pages:
        print(f"\nRetrying {len(failed_pages)} failed pages with longer delay...")
        time.sleep(10)

        for page in failed_pages:
            page_num = page["page"]
            scene = page["scene"]
            include_char = page.get("include_char", True)

            if include_char:
                prompt = f"""{char['description']}

SCENE: {char['name']} {scene}

STYLE: {MASTER_STYLE}, {char['style_ref']}"""
            else:
                prompt = f"""SCENE: {scene}

STYLE: {MASTER_STYLE}"""

            filename = f"castle_page{page_num:02d}"

            print(f"Page {page_num}...", end=" ", flush=True)

            try:
                path = gen.generate(prompt=prompt, filename=filename, style="")
                print("OK")
            except Exception as e:
                print(f"FAIL: {str(e)[:80]}")

            time.sleep(5)

    print("\nDone!")

if __name__ == "__main__":
    generate_castle_book()
