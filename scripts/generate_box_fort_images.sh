#!/bin/bash
# Generate all page images for "The Box Fort" using wan2.6-image

set -e

SKILL_DIR="/Users/dereklomas/.claude/plugins/cache/mulerouter-skills/mulerouter-skills/1.0.0/skills/mulerouter-skills"
BOOK_DIR="/Users/dereklomas/lilbookies/public/books/images/a3-the-box-fort"
REF_URL="https://mule-router-assets.muleusercontent.com/router_public/production/ephemeral/420a0805-3065-4776-b370-fac3fd6eed8c/result_00.png"
NEG_PROMPT="text, words, letters, writing, captions, titles, watermark, signature, grid, panels, comic panels, split image, multiple panels"

source /Users/dereklomas/lilbookies/.env
mkdir -p "$BOOK_DIR"

cd "$SKILL_DIR"

CHARACTER_BLOCK="CHARACTERS (draw EXACTLY as described - these features are KEY):
- Max: boy (6), sandy brown messy hair, round face, blue t-shirt, grey shorts, barefoot
- Mika: toddler girl (2), dark curly hair in two small pigtails, chubby cheeks, purple shirt, green leggings, barefoot

COMPOSITION: One cohesive illustration filling the entire canvas. Full-bleed image with the scene filling edge to edge.
STYLE: Warm gouache watercolor with soft afternoon light.
CRITICAL: NO TEXT, NO WORDS, NO LETTERS anywhere. Pure illustration only."

generate_page() {
    local page_num=$1
    local size=$2
    local scene=$3
    local output="$BOOK_DIR/page$(printf '%02d' $page_num).png"

    if [ -f "$output" ]; then
        echo "SKIP page $page_num (already exists)"
        return
    fi

    local full_prompt="Single scene illustration: ${scene}

${CHARACTER_BLOCK}"

    echo "GENERATING page $page_num ($size)..."

    result=$(uv run python models/alibaba/wan2.6-image/generation.py \
        --prompt "$full_prompt" \
        --images "[\"$REF_URL\"]" \
        --negative-prompt "$NEG_PROMPT" \
        --size "$size" \
        --n 1 2>&1)

    url=$(echo "$result" | grep -o 'https://[^ ]*\.png' | head -1)

    if [ -z "$url" ]; then
        echo "FAILED page $page_num"
        echo "$result"
        return 1
    fi

    curl -sL "$url" -o "$output"
    echo "DONE page $page_num -> $output ($(du -h "$output" | cut -f1))"
}

# Cover (page 1) - square
generate_page 1 "1280*1280" "A boy (6) with sandy brown messy hair, blue t-shirt, grey shorts, barefoot, and a toddler girl (2) with dark curly hair in two small pigtails, purple shirt, green leggings, barefoot, both peeking out from inside a large cardboard box in a cozy living room. The box has a square hole cut in the side as a window. A red mat is visible inside. Couch cushion balanced on top as a roof. Warm afternoon sunlight from a window. Gouache watercolor style."

# Story pages (pages 5-14) - landscape
generate_page 5 "1280*960" "A boy (6) with sandy brown messy hair, blue t-shirt, grey shorts, barefoot, dragging a very large cardboard box across a wooden floor in a living room. The box is taller than him. He grips the edge and pulls with effort, leaning back. A colorful striped rug on the floor, a beige couch in the background. Warm afternoon sunlight through a window. Gouache watercolor."

generate_page 6 "1280*960" "A boy (6) with sandy brown messy hair, blue t-shirt, grey shorts, barefoot, pushing a large cardboard box onto a colorful striped rug in a living room. The box sits upright on its side with the open top facing the boy. Wooden floor, beige couch behind, warm afternoon light. Gouache watercolor."

generate_page 7 "1280*960" "A boy (6) with sandy brown messy hair, blue t-shirt, grey shorts, barefoot, leaning into a large cardboard box on a colorful rug, placing a red blanket on the floor inside the box. He is bent over the edge, his bare feet visible behind him. Living room with warm afternoon light. Gouache watercolor."

generate_page 8 "1280*960" "A boy (6) with sandy brown messy hair, blue t-shirt, grey shorts, barefoot, lifting a large beige couch cushion above his head and placing it on top of a big cardboard box as a roof. He stretches up on tiptoes to reach the top. The box sits on a colorful striped rug in a living room. Warm afternoon light. Gouache watercolor."

generate_page 9 "1280*960" "A toddler girl (2) with dark curly hair in two small pigtails, purple shirt, green leggings, barefoot, climbing into a large cardboard box with one leg over the edge. She has a big excited grin on her chubby face. A boy (6) with sandy brown messy hair and blue t-shirt stands behind her with his hands up in surprise, mouth open. The box has a red mat inside and a beige cushion on top. Living room. Warm light. Gouache watercolor."

generate_page 10 "1280*960" "A boy (6) with sandy brown messy hair, blue t-shirt, grey shorts, barefoot, reaching into a large cardboard box trying to lift out a toddler girl (2) with dark curly hair in two small pigtails, purple shirt, green leggings. The toddler clings to the edge of the box refusing to leave, laughing. The boy looks exasperated but amused. Red mat visible inside the box. Living room. Warm light. Gouache watercolor."

generate_page 11 "1280*960" "A boy (6) with sandy brown messy hair, blue t-shirt, grey shorts, barefoot, peeking through a square hole cut in the side of a large cardboard box. His face fills the window opening, grinning proudly. The box sits on a colorful rug with a beige cushion on top. Jagged cardboard edges around the cut-out window. A toddler girl (2) with dark curly pigtails and purple shirt sits on the floor beside the box watching. Living room. Warm light. Gouache watercolor."

generate_page 12 "1280*960" "A boy (6) with sandy brown messy hair, blue t-shirt, grey shorts, barefoot, placing a small blue cup and a cloth bag inside a large cardboard box through the open end. Inside the box a red mat is visible with a few items placed on it. A toddler girl (2) with dark curly pigtails and purple shirt sits nearby on the rug holding a stuffed bear, watching. The box has a beige cushion on top and a square window cut in the side. Living room. Warm light. Gouache watercolor."

generate_page 13 "1280*960" "A boy (6) with sandy brown messy hair, blue t-shirt, and a toddler girl (2) with dark curly pigtails, purple shirt, both crammed inside a large cardboard box together. Their bare feet stick out one end. The boy is squished against the side, the toddler sitting on his lap. Both are grinning. Red mat underneath them, a cup and bag visible inside. Beige cushion roof overhead. View from the open end of the box looking in. Warm golden light filtering through the cardboard. Gouache watercolor."

generate_page 14 "1280*960" "Inside a cardboard box fort: a toddler girl (2) with dark curly pigtails, purple shirt, hugging a boy (6) with sandy brown messy hair and blue t-shirt. Both sitting on a red mat, warm golden light filtering through a square window and gaps in the cardboard walls. A blue cup, cloth bag, and brown stuffed bear around them. The toddler squeezes tight with her chubby arms, the boy smiling warmly. Cozy and intimate. View from inside the box. Gouache watercolor."

# End page (page 15) - landscape
generate_page 15 "1280*960" "Wide view of a cozy living room with a large cardboard box fort in the center on a colorful striped rug. A beige cushion sits on top as a roof, a square window is cut in the side. Two pairs of bare feet stick out one end — larger boy feet and tiny toddler feet. A stuffed bear peeks out the window. Warm golden sunset light through the living room window. Pillows and cushions scattered on the floor around the box. Peaceful, cozy scene. Gouache watercolor."

echo ""
echo "=== DONE ==="
ls -la "$BOOK_DIR"/
