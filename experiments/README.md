# Character Consistency Experiments

Systematic testing of different approaches to maintaining character consistency in AI-generated children's book illustrations.

## Setup

### Required API Keys

Add these to your `.env` file:

```bash
# MuleRouter (current)
MULEROUTER_API_KEY=sk-mr-...

# fal.ai (Flux Kontext) - Recommended
# Get key at: https://fal.ai/dashboard/keys
FAL_KEY=...

# Replicate (Ideogram Character) - Optional
# Get token at: https://replicate.com/account/api-tokens
REPLICATE_API_TOKEN=...
```

### Install Dependencies

```bash
cd /Users/dereklomas/minibooks
source .venv/bin/activate
pip install fal-client httpx python-dotenv Pillow
```

## Running Experiments

### Quick Test (1 scene per provider)

```bash
python src/character_experiment.py --quick
```

### Full Test (5 scenes per provider)

```bash
python src/character_experiment.py
```

## Experiment Design

### Test Character: Gus the Gecko

A simple, distinctive character for testing:
- Bright lime-green color
- Large friendly eyes
- Curled tail with stripes
- Cartoon style

### Test Scenes (5 poses)

1. Standing on volcanic hill (confident)
2. Running up grassy slope (excited)
3. Peeking over crater edge (curious)
4. Jumping back in surprise (alarmed)
5. Walking toward sunset (content)

### Providers Tested

| Provider | Model | Method | Reference Support |
|----------|-------|--------|-------------------|
| MuleRouter | Nano Banana Pro | Text prompt | No |
| MuleRouter | Midjourney | --cref/--sref | Yes (if available) |
| fal.ai | Flux Kontext | image_url param | Yes |
| fal.ai | Flux Dev | Text prompt | No |
| Replicate | Ideogram Character | character_reference | Yes |

### Metrics

1. **Visual Consistency** (manual 1-5 rating)
   - Same body shape
   - Same color palette
   - Same facial features
   - Same style

2. **Generation Time** (ms)

3. **Cost** (USD per image)

4. **Success Rate** (%)

## Results Directory

```
experiments/
├── images/                    # Generated test images
│   ├── gus_gecko_mulerouter_scene01.png
│   ├── gus_gecko_fal_kontext_scene01.png
│   └── ...
├── *_results.json             # Detailed results
└── README.md                  # This file
```

## Evaluating Results

After running experiments:

1. Open all images for a provider in a grid view
2. Rate consistency 1-5:
   - 5: Identical character across all scenes
   - 4: Minor variations, clearly same character
   - 3: Moderate drift, recognizable
   - 2: Significant drift, barely recognizable
   - 1: Completely different character

3. Compare across providers

## Expected Outcomes

Based on research:

| Provider | Expected Consistency |
|----------|---------------------|
| Text-only (MuleRouter) | ★★★☆☆ |
| Flux Kontext (fal.ai) | ★★★★★ |
| Ideogram Character | ★★★★★ |
| Midjourney --cref | ★★★★★ |
| LoRA (trained) | ★★★★★ |

## Next Steps

1. Run baseline tests
2. Generate hero reference image
3. Test with character reference
4. Compare results
5. Choose best provider for production
6. Train LoRAs for recurring characters
