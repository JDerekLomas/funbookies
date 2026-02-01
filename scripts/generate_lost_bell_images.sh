#!/bin/bash
# Generate all page images for "The Lost Bell" using wan2.6-image
# Reference: the-lost-bell_reference.png (Ben version)

set -e

SKILL_DIR="/Users/dereklomas/.claude/plugins/cache/mulerouter-skills/mulerouter-skills/1.0.0/skills/mulerouter-skills"
BOOK_DIR="/Users/dereklomas/lilbookies/public/books/images/b3-the-lost-bell"
REF_URL="https://mule-router-assets.muleusercontent.com/router_public/production/ephemeral/5cc014fb-5967-4a79-953a-31c625b7a1f9/result_00.png"
NEG_PROMPT="text, words, letters, writing, captions, titles, watermark, signature, grid, panels, comic panels, split image, multiple panels"

source /Users/dereklomas/lilbookies/.env
mkdir -p "$BOOK_DIR"

cd "$SKILL_DIR"

CHARACTER_BLOCK="CHARACTERS (draw EXACTLY as described - these features are KEY):
- Ben: small boy (5-6), short messy brown hair, round face, red tunic shirt, brown shorts, brown lace-up boots

COMPOSITION: One cohesive illustration filling the entire canvas. Full-bleed image with the scene filling edge to edge.
STYLE: Rich watercolor with warm stone textures.
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

    # Extract URL from result
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
generate_page 1 "1280*1280" "A small boy with short messy brown hair wearing a red tunic shirt, brown shorts, and brown boots, standing on a grassy hilltop holding an old bronze bell. Behind him a medieval castle — the left half is a mossy crumbling ruin, the right half glows golden with colourful banners and torchlight as if alive. Rich watercolor style."

# Story pages (pages 5-18) - landscape
generate_page 5 "1280*960" "A small boy with short messy brown hair, red tunic shirt, brown shorts, and brown boots, walking up a grassy hill path alone. At the hilltop a crumbling medieval stone castle covered in moss and ivy, broken walls, empty dark windows. Overcast grey sky. Quiet and still. Muted grey-green watercolor palette."

generate_page 6 "1280*960" "A small boy with short messy brown hair and red tunic shirt walking along the edge of a dark still pond surrounded by reeds and fallen stones. The pond reflects a crumbling castle wall behind it. Murky green water, algae on the surface. Damp misty atmosphere. Muted grey-green watercolor."

generate_page 7 "1280*960" "Close view of a small boy with short messy brown hair and red tunic shirt crouching on sandy ground, brushing sand off a tarnished green-brown bronze bell half buried in the dirt. A moss-covered castle wall rises behind him. The boy looks down at the bell with wide curious eyes. Soft grey light. Watercolor."

generate_page 8 "1280*960" "A small boy with short messy brown hair and red tunic shirt standing and holding a bronze bell high above his head with both hands. Bright golden light bursts outward from the bell in all directions like a shockwave. His hair blows back from the force. The grey castle ruin behind him begins to glow warm gold. Dramatic burst of gold against grey-green background. Watercolor."

generate_page 9 "1280*960" "A grand medieval castle with tall intact stone walls, bright red and gold banners hanging from the battlements, flags fluttering in the wind. A clear blue moat surrounds the castle. Bright blue sky, warm golden sunlight. A small boy with short messy brown hair and red tunic shirt stands in the foreground looking up with his mouth wide open in amazement. Vivid warm watercolor."

generate_page 10 "1280*960" "Three medieval soldiers in leather tunics standing on top of a castle wall battlement, silhouetted against a bright sky, looking outward over vast green rolling hills and farmland. One soldier points into the distance. Colourful banners flutter beside them. View from below looking up at them. Warm golden sunlight. Watercolor."

generate_page 11 "1280*960" "A massive wooden castle gate with iron studs and heavy iron hinges, closed shut in a thick stone archway. Two medieval guards in leather tunics stand on either side of the gate holding spears. The stone archway is solid and imposing. Warm torchlight on the stone walls. A small boy with short messy brown hair and red tunic shirt looks up at the enormous gate. Warm watercolor."

generate_page 12 "1280*960" "A medieval woman in a plain linen dress and headscarf standing at a stone well in the centre of a sunny cobblestone castle courtyard, lowering a wooden bucket on a rope down into the well. A small boy with short messy brown hair and red tunic shirt stands beside her, leaning over the well edge and peering down into the darkness. Castle walls and a tower in the background. Warm afternoon sunlight. Watercolor."

generate_page 13 "1280*960" "A wooden bucket overflowing with clear sparkling water being pulled up over the rim of a stone well by a medieval woman. Water droplets catch the sunlight. A small boy with short messy brown hair and red tunic shirt reaches out one hand to touch the water, smiling. Sunny cobblestone courtyard. Warm watercolor with bright sparkling water details."

generate_page 14 "1280*960" "A small boy with short messy brown hair and red tunic shirt standing on top of a castle wall battlement walkway, his hair and shirt blown sideways by strong wind. He grips the stone wall with one hand. Vast green landscape stretches to the horizon — fields, forest, a winding river. Bright blue sky with white clouds. Golden sunlight. Watercolor."

generate_page 15 "1280*960" "A panoramic landscape view from the top of castle battlements: a clear blue moat circling below, a green hill, patchwork farmland with golden wheat fields, tiny cottages, and distant blue mountains. Stone parapet wall in the foreground. Warm golden-hour light across the entire landscape. Watercolor."

generate_page 16 "1280*960" "A small boy with short messy brown hair and red tunic shirt on top of castle battlements, gripping the stone wall with both hands as golden light bursts from a bronze bell beside him. The castle stones around him are cracking and crumbling. Colourful banners are fading into grey mist. Half the image is warm gold, half is grey-green fog. Dramatic watercolor."

generate_page 17 "1280*960" "A small boy with short messy brown hair and red tunic shirt standing alone in an overgrown castle courtyard, holding the bronze bell, looking around. Crumbling stone walls covered in thick moss and ivy. Grass growing between cobblestones. Empty arched doorways. Overcast grey sky. A small bird perched on a fallen stone. Quiet and still. Muted grey-green watercolor."

generate_page 18 "1280*960" "A small boy with short messy brown hair and red tunic shirt walking down a grassy hillside path, holding a bronze bell pressed against his chest with both arms. A gentle smile on his round face. The crumbling castle ruin sits on the hilltop behind him. Golden sunset light breaks through clouds, illuminating the boy. Wildflowers along the path. Warm watercolor."

# End page (page 19) - landscape
generate_page 19 "1280*960" "A small boy with short messy brown hair and red tunic shirt sitting on a bed in a cozy bedroom at night. An old bronze bell sits on the bedside table next to a glowing lamp. The boy looks at the bell with a small knowing smile. Through the bedroom window, the dark silhouette of a castle on a distant hill against a starry night sky. Warm cozy lamplight. Watercolor."

echo ""
echo "=== DONE ==="
ls -la "$BOOK_DIR"/
