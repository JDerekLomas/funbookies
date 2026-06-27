#!/bin/bash
# Generate art style preview images for wizard

cd /Users/dereklomas/.claude/plugins/cache/mulerouter-skills/mulerouter-skills/1.0.0/skills/mulerouter-skills
source /Users/dereklomas/lilbookies/.env

OUTPUT_DIR="/Users/dereklomas/lilbookies/public/images/art-styles"
mkdir -p "$OUTPUT_DIR"

generate_style() {
    local id=$1
    local prompt=$2
    echo "Generating $id..."

    result=$(uv run python models/alibaba/wan2.6-t2i/generation.py \
        --prompt "$prompt" \
        --size "768*768" \
        --n 1 \
        --max-wait 300 2>&1)

    # Extract URL from result
    url=$(echo "$result" | grep -oE 'https://[^ ]+\.png' | head -1)

    if [ -n "$url" ]; then
        curl -s "$url" -o "$OUTPUT_DIR/$id.png"
        echo "  Downloaded $id.png"
    else
        echo "  Failed to generate $id"
        echo "$result"
    fi
}

# Generate all styles
generate_style "bold-graphic" "A friendly cat sitting, bold graphic illustration, simple geometric shapes, strong primary colors, clean black outlines, minimal detail, modern children's book style"
generate_style "collage" "A friendly cat sitting, paper collage illustration, cut and layered tissue paper textures, vibrant colors, handmade tactile quality, Eric Carle inspired"
generate_style "sketchy-whimsical" "A friendly cat sitting, loose sketchy ink illustration with watercolor washes, energetic expressive lines, whimsical proportions, Quentin Blake inspired"
generate_style "retro-midcentury" "A friendly cat sitting, mid-century modern illustration, limited color palette, stylized geometric shapes, vintage 1950s children's book aesthetic"
generate_style "cozy-detailed" "A friendly cat sitting, detailed cozy illustration, intricate patterns, rich warm colors, inviting scene full of small details, Jan Brett inspired"
generate_style "soft-digital" "A friendly cat sitting, soft digital illustration, gentle gradients, rounded friendly forms, warm lighting, contemporary children's book"
generate_style "minimalist" "A friendly cat sitting, minimalist illustration, simple shapes on white background, essential elements only, bold color accents, plenty of negative space"
generate_style "folk-art" "A friendly cat sitting, folk art illustration, traditional patterns and motifs, warm earthy colors, handcrafted naive quality, decorative"
generate_style "dreamy-magical" "A friendly cat sitting, dreamy magical illustration, soft glowing light, ethereal atmosphere, fantasy quality, rich shadows and highlights"
generate_style "cheerful-cartoon" "A friendly cat sitting, cheerful cartoon illustration, bright saturated colors, expressive character, bold clean outlines, fun energetic style"
generate_style "nature-realistic" "A friendly cat sitting, naturalistic children's book illustration, detailed flora, accurate but softened for children, gentle realism"

echo "Done! Generated $(ls -1 $OUTPUT_DIR/*.png 2>/dev/null | wc -l) images"
