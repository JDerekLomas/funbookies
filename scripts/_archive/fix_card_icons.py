#!/usr/bin/env python3
"""
Fix icons that keep getting card containers - try 'logo/symbol' approach.
"""

import json
import subprocess
import requests
from pathlib import Path
from time import sleep

MULEROUTER_DIR = Path.home() / ".claude/plugins/cache/mulerouter-skills/mulerouter-skills/1.0.0/skills/mulerouter-skills"
OUTPUT_DIR = Path(__file__).parent.parent / "public" / "images" / "icons"

# Different approach - describe as logo/symbol, not icon
STYLE = """Simple minimalist logo design on plain cream background (#FAF8F5).
Just the symbol itself, no container, no app icon frame, no rounded square behind it.
Single sage green color (#9FC7AA).
The symbol floats directly on the plain background.
Like a simple SVG logo, not an app icon.
Clean, flat design. No gradients, no shadows, no borders."""

NEGATIVE = "app icon, iOS icon, Android icon, rounded square, rounded rectangle, container, frame, border, box behind, card, badge, multiple colors, gradient, 3D, shadow, realistic"

ICONS = {
    "icon-target": "Bullseye target symbol with arrow hitting center. Just concentric circles with arrow, no frame around it.",

    "icon-star": "Simple five-pointed star. Just the star shape floating on background, no square behind it.",

    "icon-syllable-clap": "Two hands clapping symbol with dots. Just the hands, no container.",

    "icon-letter-match": "Two letter A symbols with checkmark between them. Just the letters and check, no frame.",
}


def generate(name: str, desc: str) -> bool:
    prompt = f"{STYLE}\n\nSymbol: {desc}"
    output = OUTPUT_DIR / f"{name}.png"

    # Backup
    if output.exists():
        backup = OUTPUT_DIR / "backup" / f"{name}_v3.png"
        backup.parent.mkdir(exist_ok=True)
        import shutil
        shutil.copy(output, backup)

    print(f"  {name}...", end=" ", flush=True)

    cmd = [
        "uv", "run", "python",
        str(MULEROUTER_DIR / "models/alibaba/wan2.6-t2i/generation.py"),
        "--prompt", prompt,
        "--negative-prompt", NEGATIVE,
        "--size", "1024*1024",
        "--n", "1",
        "--json", "--quiet"
    ]

    try:
        result = subprocess.run(cmd, cwd=str(MULEROUTER_DIR),
                              capture_output=True, text=True, timeout=300)
        if result.returncode != 0:
            print("FAILED")
            return False

        data = json.loads(result.stdout)
        if data.get("results"):
            resp = requests.get(data["results"][0], timeout=60)
            if resp.status_code == 200:
                with open(output, 'wb') as f:
                    f.write(resp.content)
                print("OK")
                return True
        print("FAILED")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False


def main():
    print("Fixing icons with card containers...")
    print()

    for name, desc in ICONS.items():
        generate(name, desc)
        sleep(1)

    print("\nDone!")


if __name__ == "__main__":
    main()
