#!/bin/bash
# Quick comparison using mulerouter-skills directly

cd /Users/dereklomas/mulerouter-skills-dev/skills/mulerouter-skills
export MULEROUTER_SITE="mulerouter"
export MULEROUTER_API_KEY="sk-mr-2dfbbdfe5bbd2e24235960b2d4f5b45bf1b59a087bc2524ff35c6c70a2657436"

OUTPUT_DIR="/Users/dereklomas/minibooks/experiments/images"

CHARACTER="A small bright lime-green gecko with big round friendly eyes, yellow-green belly, curled striped tail, four stubby legs, cute cartoonish style, standing upright"
STYLE="children's book illustration, simple flat cartoon style, bold black outlines, bright saturated colors, no text"

echo "=== COMPARISON EXPERIMENT ==="
echo ""

# Scene 1: Volcano
echo "--- Scene 1: Volcano ---"
SCENE="standing on a grassy hill looking at a distant smoking volcano, sunny day"

echo "Wan2.6 T2I..."
uv run python models/alibaba/wan2.6-t2i/generation.py --prompt "$CHARACTER, $SCENE, $STYLE" --n 1 2>&1 | tee /tmp/wan26_volcano.log
URL=$(grep "result_00.png" /tmp/wan26_volcano.log | head -1 | awk '{print $2}')
[ -n "$URL" ] && curl -s -o "$OUTPUT_DIR/cmp_wan26_volcano.png" "$URL" && echo "  Saved: cmp_wan26_volcano.png"

echo ""
echo "Nano Banana Pro..."
uv run python models/google/nano-banana-pro/generation.py --prompt "$CHARACTER, $SCENE, $STYLE" 2>&1 | tee /tmp/nano_volcano.log
URL=$(grep "result" /tmp/nano_volcano.log | grep "http" | head -1 | awk '{print $2}')
[ -n "$URL" ] && curl -s -o "$OUTPUT_DIR/cmp_nano_volcano.png" "$URL" && echo "  Saved: cmp_nano_volcano.png"

echo ""
echo "Wan2.5 I2I..."
uv run python models/alibaba/wan2.5-i2i-preview/generation.py --prompt "Transform into scene: $SCENE. Keep exact gecko appearance. $STYLE" --images '["https://funbookies.vercel.app/experiments/images/gus_wan26_hero_1.png"]' --n 1 2>&1 | tee /tmp/wan25_volcano.log
URL=$(grep "result" /tmp/wan25_volcano.log | grep "http" | head -1 | awk '{print $2}')
[ -n "$URL" ] && curl -s -o "$OUTPUT_DIR/cmp_wan25i2i_volcano.png" "$URL" && echo "  Saved: cmp_wan25i2i_volcano.png"

# Scene 2: Running
echo ""
echo "--- Scene 2: Running ---"
SCENE="running excitedly up a rocky mountain slope"

echo "Wan2.6 T2I..."
uv run python models/alibaba/wan2.6-t2i/generation.py --prompt "$CHARACTER, $SCENE, $STYLE" --n 1 2>&1 | tee /tmp/wan26_running.log
URL=$(grep "result_00.png" /tmp/wan26_running.log | head -1 | awk '{print $2}')
[ -n "$URL" ] && curl -s -o "$OUTPUT_DIR/cmp_wan26_running.png" "$URL" && echo "  Saved: cmp_wan26_running.png"

echo ""
echo "Nano Banana Pro..."
uv run python models/google/nano-banana-pro/generation.py --prompt "$CHARACTER, $SCENE, $STYLE" 2>&1 | tee /tmp/nano_running.log
URL=$(grep "result" /tmp/nano_running.log | grep "http" | head -1 | awk '{print $2}')
[ -n "$URL" ] && curl -s -o "$OUTPUT_DIR/cmp_nano_running.png" "$URL" && echo "  Saved: cmp_nano_running.png"

echo ""
echo "Wan2.5 I2I..."
uv run python models/alibaba/wan2.5-i2i-preview/generation.py --prompt "Transform into scene: $SCENE. Keep exact gecko appearance. $STYLE" --images '["https://funbookies.vercel.app/experiments/images/gus_wan26_hero_1.png"]' --n 1 2>&1 | tee /tmp/wan25_running.log
URL=$(grep "result" /tmp/wan25_running.log | grep "http" | head -1 | awk '{print $2}')
[ -n "$URL" ] && curl -s -o "$OUTPUT_DIR/cmp_wan25i2i_running.png" "$URL" && echo "  Saved: cmp_wan25i2i_running.png"

# Scene 3: Crater
echo ""
echo "--- Scene 3: Crater ---"
SCENE="standing at edge of volcanic crater looking down with wonder, steam rising"

echo "Wan2.6 T2I..."
uv run python models/alibaba/wan2.6-t2i/generation.py --prompt "$CHARACTER, $SCENE, $STYLE" --n 1 2>&1 | tee /tmp/wan26_crater.log
URL=$(grep "result_00.png" /tmp/wan26_crater.log | head -1 | awk '{print $2}')
[ -n "$URL" ] && curl -s -o "$OUTPUT_DIR/cmp_wan26_crater.png" "$URL" && echo "  Saved: cmp_wan26_crater.png"

echo ""
echo "Nano Banana Pro..."
uv run python models/google/nano-banana-pro/generation.py --prompt "$CHARACTER, $SCENE, $STYLE" 2>&1 | tee /tmp/nano_crater.log
URL=$(grep "result" /tmp/nano_crater.log | grep "http" | head -1 | awk '{print $2}')
[ -n "$URL" ] && curl -s -o "$OUTPUT_DIR/cmp_nano_crater.png" "$URL" && echo "  Saved: cmp_nano_crater.png"

echo ""
echo "Wan2.5 I2I..."
uv run python models/alibaba/wan2.5-i2i-preview/generation.py --prompt "Transform into scene: $SCENE. Keep exact gecko appearance. $STYLE" --images '["https://funbookies.vercel.app/experiments/images/gus_wan26_hero_1.png"]' --n 1 2>&1 | tee /tmp/wan25_crater.log
URL=$(grep "result" /tmp/wan25_crater.log | grep "http" | head -1 | awk '{print $2}')
[ -n "$URL" ] && curl -s -o "$OUTPUT_DIR/cmp_wan25i2i_crater.png" "$URL" && echo "  Saved: cmp_wan25i2i_crater.png"

echo ""
echo "=== DONE ==="
ls -la $OUTPUT_DIR/cmp_*.png 2>/dev/null
