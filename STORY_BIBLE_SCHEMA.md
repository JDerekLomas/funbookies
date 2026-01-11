# Story Bible Schema

The `story_bible` field in book JSON captures the rich narrative intent before level adaptation. This allows sophisticated stories to be told simply, rather than simple stories being told simply.

## Schema Definition

```json
{
  "story_bible": {
    "premise": "string - The core story concept in 2-3 sentences",
    "themes": ["string - List of themes explored"],
    "character_arcs": {
      "CharacterName": "string - Arc description: Starting state → Transformation → End state"
    },
    "setting": "string - Rich description of time, place, and atmosphere",
    "plot_summary": "string - Full plot in narrative form (can be multiple paragraphs)",
    "emotional_beats": [
      {
        "page": "number - Story page number",
        "beat": "string - The emotional moment or turning point"
      }
    ],
    "level_adaptation": "string - Notes on how the story was simplified for this reading level",
    "visual_style": "string - Art direction notes for consistency",
    "key_vocabulary": ["string - Important words that should appear regardless of level"]
  }
}
```

## Field Descriptions

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `premise` | string | The core story concept. What is this story fundamentally about? |
| `themes` | string[] | Key themes explored (e.g., "friendship", "overcoming fear", "family bonds") |
| `character_arcs` | object | Maps character names to their transformation journey |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `setting` | string | Rich description of where and when the story takes place |
| `plot_summary` | string | Full narrative plot (not level-constrained) |
| `emotional_beats` | object[] | Key emotional moments mapped to pages |
| `level_adaptation` | string | How the story was simplified for the target reading level |
| `visual_style` | string | Art direction and style consistency notes |
| `key_vocabulary` | string[] | Words that must appear regardless of level simplification |

## Example: Band B Book

```json
{
  "title": "Pup in the Mud",
  "band": "B",
  "story_bible": {
    "premise": "A playful puppy discovers the joy of mud puddles, makes an unexpected friend, and learns that the best adventures end with a warm bath and a hug.",
    "themes": ["joy of play", "unexpected friendship", "comfort after adventure"],
    "character_arcs": {
      "Pup": "Restless and hot → Discovers the joy of mud → Finds friendship → Content and loved",
      "Jen": "Caring owner → Concerned about mess → Embraces the chaos → Shows unconditional love"
    },
    "setting": "A sunny backyard on a hot summer day. The grass is green, there's a big brown mud puddle near the garden, and a cozy house with a bathtub inside.",
    "plot_summary": "On a hot summer day, Pup is sitting in the sun feeling uncomfortable. She spots a mud puddle and can't resist—she runs and jumps in! The cool mud feels amazing. While playing, she discovers a friendly bug and then meets a puppy friend who joins her. They play together, getting gloriously muddy. When Jen finds them, instead of being upset, she prepares a warm bath. The story ends with clean, happy animals getting hugs and cuddles—the perfect end to a perfect day.",
    "emotional_beats": [
      {"page": 1, "beat": "Discomfort - Pup is too hot"},
      {"page": 3, "beat": "Excitement - Spotting the mud puddle"},
      {"page": 5, "beat": "Joy - The relief and fun of cool mud"},
      {"page": 8, "beat": "Surprise - Meeting a new friend"},
      {"page": 10, "beat": "Connection - Playing together"},
      {"page": 12, "beat": "Comfort - The warm bath"},
      {"page": 14, "beat": "Love - Hugs and contentment"}
    ],
    "level_adaptation": "Simplified to CVC words (mud, sun, run, hug, tub) while preserving the emotional arc. Each page has one simple sentence but the illustrations carry the rich emotional content.",
    "visual_style": "Warm watercolor style with soft edges. Pup is round and expressive with big eyes. Color palette shifts from hot yellows to cool browns to warm pinks.",
    "key_vocabulary": ["pup", "mud", "sun", "fun", "hug"]
  }
}
```

## Example: Band D Book

```json
{
  "title": "The Lighthouse Keeper",
  "band": "D",
  "story_bible": {
    "premise": "A skeptical girl spending summer at her grandmother's lighthouse discovers that her grandmother's fantastical stories about the light saving ships might actually be true—and that she's inherited a magical connection to the sea.",
    "themes": ["family legacy", "believing the impossible", "connection across generations", "responsibility"],
    "character_arcs": {
      "Maya": "Skeptical city girl who dismisses grandmother's stories → Curious when she sees unexplained lights → Believing when she saves a ship → Embracing her role as future keeper",
      "Grandmother": "Mysterious keeper of secrets → Guides without forcing → Passes the torch",
      "The Lighthouse": "Old building needing repairs → Revealed as magical artifact → Living connection to family history"
    },
    "setting": "A weathered lighthouse on a rocky coast, summer storms gathering. The lighthouse has a warm keeper's cottage with old photographs and mysterious artifacts. The sea is sometimes calm, sometimes wild, always full of secrets.",
    "plot_summary": "Maya has always dismissed her grandmother's stories about the lighthouse having 'special light' that guides ships through impossible storms. But this summer is different—Grandmother is getting older, and there are hints that Maya is meant to inherit something more than just a building.\n\nWhen Maya sees lights in the storm that don't match the lighthouse beam, her skepticism cracks. She discovers her grandmother's journals, filled with accounts of impossible rescues. Then a massive storm hits, the electric power fails, and Maya instinctively knows what to do—she climbs the tower and somehow, through sheer will and an inexplicable connection, the old light blazes to life.\n\nIn the morning, a ship's captain comes to thank them. He'd been lost in impossible fog when a brilliant light appeared exactly where he needed it. Maya and her grandmother exchange a look—the legacy has been passed.",
    "emotional_beats": [
      {"page": 4, "beat": "Dismissal - Maya rolls her eyes at another 'magic' story"},
      {"page": 12, "beat": "Crack in skepticism - She sees unexplained lights"},
      {"page": 18, "beat": "Discovery - Finding grandmother's journals"},
      {"page": 25, "beat": "Crisis - Storm hits, power fails"},
      {"page": 32, "beat": "Transformation - Maya chooses to believe and act"},
      {"page": 38, "beat": "Triumph - The light blazes, ship is saved"},
      {"page": 44, "beat": "Acceptance - Captain's visit confirms everything"},
      {"page": 48, "beat": "Legacy - The knowing look between generations"}
    ],
    "level_adaptation": "Band D allows for complex sentences and vocabulary. Focused on 'ight' word family (light, night, sight, right, bright, might) woven naturally into the narrative. Maintained the mystery and emotional complexity while keeping sentences accessible.",
    "visual_style": "Atmospheric watercolors with dramatic lighting. Storm scenes use deep blues and grays with brilliant light breaking through. Lighthouse is a character—shown from different angles, in different weather. Maya's expressions key to showing her transformation.",
    "key_vocabulary": ["lighthouse", "light", "night", "storm", "bright", "sight"]
  }
}
```

## Workflow

1. **Story Bible First**: Write the rich narrative without level constraints
2. **Level Adaptation**: Simplify text while preserving emotional beats
3. **Scene Descriptions**: Generate image prompts from story bible, not simplified text
4. **Reference Image**: Use visual_style notes for art direction

## Benefits

- **Better Images**: Scene prompts based on rich descriptions, not "Pup ran"
- **Consistent Characters**: Character arc informs expression across pages
- **Emotional Resonance**: Simple text + rich illustrations = sophisticated storytelling
- **Multi-Level Potential**: Same story bible can generate A, B, C, D versions
