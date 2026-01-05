#!/bin/bash
# FunBookies Batch Image Generator
# Usage: ./generate_images.sh <book_slug> [--pages 6,7,8] [--style classic]

set -e

BOOK_SLUG="${1:-}"
PAGES_ARG=""
STYLE="classic"
SEED_BASE=100

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --pages)
            PAGES_ARG="$2"
            shift 2
            ;;
        --style)
            STYLE="$2"
            shift 2
            ;;
        --seed)
            SEED_BASE="$2"
            shift 2
            ;;
        *)
            if [[ -z "$BOOK_SLUG" ]]; then
                BOOK_SLUG="$1"
            fi
            shift
            ;;
    esac
done

if [[ -z "$BOOK_SLUG" ]]; then
    echo "Usage: $0 <book_slug> [--pages 6,7,8] [--style classic] [--seed 100]"
    echo ""
    echo "Generates images for all story pages in a FunBookies book."
    echo ""
    echo "Options:"
    echo "  --pages    Comma-separated list of page numbers to generate"
    echo "  --style    Art style: classic, adventure, nature, silly, cozy"
    echo "  --seed     Base seed for reproducibility"
    exit 1
fi

# Paths
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BOOK_JSON="$PROJECT_ROOT/public/books/${BOOK_SLUG}.json"
OUTPUT_DIR="$PROJECT_ROOT/public/books/${BOOK_SLUG}_images"
MULEROUTER_SCRIPT_DIR="$HOME/.claude/plugins/cache/mulerouter-skills/mulerouter-skills/1.0.0/skills/mulerouter-skills"

# Check book exists
if [[ ! -f "$BOOK_JSON" ]]; then
    echo "Error: Book not found: $BOOK_JSON"
    exit 1
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Style suffixes
declare -A STYLE_SUFFIXES
STYLE_SUFFIXES[classic]="Warm soft watercolor style, child-friendly cute illustration."
STYLE_SUFFIXES[adventure]="Bold gouache illustration, dynamic composition, vibrant colors."
STYLE_SUFFIXES[nature]="Detailed botanical illustration style, soft greens and earth tones."
STYLE_SUFFIXES[silly]="Playful cartoon style with exaggerated expressions, bright colors."
STYLE_SUFFIXES[cozy]="Warm soft watercolor style, cozy atmosphere, soft pastels."

STYLE_SUFFIX="${STYLE_SUFFIXES[$STYLE]:-${STYLE_SUFFIXES[classic]}}"

echo "=========================================="
echo "FunBookies Image Generator"
echo "=========================================="
echo "Book: $BOOK_SLUG"
echo "Style: $STYLE"
echo "Output: $OUTPUT_DIR"
echo ""

# Check for required environment variables
if [[ -z "$MULEROUTER_API_KEY" ]]; then
    echo "Warning: MULEROUTER_API_KEY not set"
    echo "Set it with: export MULEROUTER_API_KEY=your-key"
fi

# Extract pages with image_prompt from JSON
# Using Python for reliable JSON parsing
PAGES_TO_GENERATE=$(python3 << EOF
import json
import sys

with open("$BOOK_JSON") as f:
    book = json.load(f)

pages_arg = "$PAGES_ARG"
if pages_arg:
    target_pages = [int(p.strip()) for p in pages_arg.split(",")]
else:
    target_pages = None

for page in book.get("pages", []):
    page_num = page.get("page")
    prompt = page.get("image_prompt")
    image_path = page.get("image", "")

    if prompt and (target_pages is None or page_num in target_pages):
        # Extract filename from image path
        filename = image_path.split("/")[-1] if image_path else f"page_{page_num:02d}.png"
        print(f"{page_num}|{filename}|{prompt}")
EOF
)

if [[ -z "$PAGES_TO_GENERATE" ]]; then
    echo "No pages to generate!"
    exit 0
fi

# Count pages
PAGE_COUNT=$(echo "$PAGES_TO_GENERATE" | wc -l | tr -d ' ')
echo "Generating $PAGE_COUNT images..."
echo ""

# Generate each image
CURRENT=0
echo "$PAGES_TO_GENERATE" | while IFS='|' read -r PAGE_NUM FILENAME PROMPT; do
    CURRENT=$((CURRENT + 1))
    OUTPUT_PATH="$OUTPUT_DIR/$FILENAME"
    SEED=$((SEED_BASE + PAGE_NUM))

    echo "[$CURRENT/$PAGE_COUNT] Page $PAGE_NUM: $FILENAME"

    # Skip if file already exists
    if [[ -f "$OUTPUT_PATH" ]]; then
        echo "  -> Already exists, skipping"
        continue
    fi

    # Build full prompt with style
    FULL_PROMPT="$PROMPT $STYLE_SUFFIX"

    echo "  -> Generating..."

    # Call MuleRouter
    RESULT=$(cd "$MULEROUTER_SCRIPT_DIR" && \
        MULEROUTER_SITE=mulerouter \
        MULEROUTER_API_KEY="${MULEROUTER_API_KEY}" \
        uv run python models/alibaba/wan2.6-t2i/generation.py \
        --prompt "$FULL_PROMPT" \
        --size "1024*820" \
        --n 1 \
        --seed "$SEED" \
        --quiet 2>&1) || true

    # Extract URL from result
    IMAGE_URL=$(echo "$RESULT" | grep -oE 'https://[^ ]+\.png' | head -1)

    if [[ -n "$IMAGE_URL" ]]; then
        curl -s -o "$OUTPUT_PATH" "$IMAGE_URL"
        echo "  -> Saved to $FILENAME"
    else
        echo "  -> Failed to generate"
        echo "$RESULT"
    fi

    # Rate limiting
    sleep 2
done

echo ""
echo "=========================================="
echo "Generation complete!"
echo "=========================================="
ls -la "$OUTPUT_DIR"
