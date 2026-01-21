# FunBookies Reference Image Prompts

9-panel reference sheets for AI image generation consistency.

## Metaprompt System

The wizard uses a **metaprompt** architecture for generating reference prompts:

### How It Works

```
┌─────────────────────────────────────────┐
│ Metaprompt Template (editable)          │
│                                         │
│ "Create a 3x3 grid for {title}:         │
│  CHARACTER: {name} - {description}..."  │
└─────────────────────────────────────────┘
                    ↓
            + Story Data (extracted)
                    ↓
┌─────────────────────────────────────────┐
│ Generated Prompt (sent to AI)           │
│                                         │
│ "Create a 3x3 grid for Spot Finds Sun:  │
│  CHARACTER: Spot - fluffy gray cat..."  │
└─────────────────────────────────────────┘
```

### Placeholders

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{title}` | Book title | "Spot Finds Sun" |
| `{name}` | Character name | "Spot" |
| `{NAME}` | Character name (uppercase) | "SPOT" |
| `{description}` | Character description | "fluffy gray and white cat with distinctive black spots" |
| `{traits}` | Physical traits | "amber eyes, pink nose, fluffy belly" |
| `{setting}` | Story setting | "cozy house" |

### Data Extraction

Story data is automatically extracted from scene descriptions:
- **Character name**: Parsed from first scene (e.g., "Wide shot: **Spot**, fluffy gray...")
- **Description**: Character details after name in scene
- **Traits**: Physical features found across all scenes (eyes, nose, fur patterns)
- **Setting**: From book metadata

### Wizard UI

In Phase 4 (Reference), users can:
1. **View/edit the metaprompt template** - Customize the structure
2. **See extracted story data** - Verify what placeholders will contain
3. **Preview generated prompt** - Final prompt before sending to AI
4. **Apply Template** - Regenerate from edited metaprompt
5. **Reset to Default** - Restore the default metaprompt

---

## Style Block (Use for All)

```
STYLE: Warm watercolor children's book illustration. Soft painterly edges,
no hard outlines. Muted earthy palette: sage green (#9FC7AA), terracotta
(#EFA487), warm cream (#FAF8F5), soft gold, dusty blue (#7BA3B4).
Friendly rounded character shapes with expressive simple faces.
Gentle natural lighting. Age-appropriate for 5-7 year olds.
Emotionally warm and inviting.

FORMAT: Square 1:1 aspect ratio, 3x3 grid, each panel clearly separated
with thin white borders. Consistent style across all panels.
```

---

## 1. A0: LOOK! (Pre-Reader)

**Theme:** Simple shapes, visual tracking, concept of print

```
9-panel children's book reference sheet, grid layout (3x3), consistent warm
watercolor style throughout all panels:

Row 1 - Core Visual Elements:
[1] A single friendly eye, wide and curious, looking at viewer,
    simple round shape, cream background
[2] Three round oranges in a row, bold simple shapes, warm orange color,
    clean background
[3] Cute owl face, two big round eyes (OO shape), simple friendly expression,
    soft brown and cream colors

Row 2 - Objects & Shapes:
[4] A tall simple tree with one small bird, emphasizing vertical (LI) shapes,
    green and brown
[5] One big full moon, perfectly round, glowing softly in dark blue sky
[6] Three floating bubbles, round and shiny, ascending upward,
    light blue iridescent

Row 3 - Scenes & Moments:
[7] A young child pointing upward at the sky with wonder, simple pose,
    back/side view
[8] A smiling sun, simple radiating design, warm yellow and orange
[9] Child's hands holding open a book, simple composition, inviting

STYLE: Warm watercolor, very simple bold shapes, minimal detail,
muted palette (sage, terracotta, cream, soft gold), no outlines,
suitable for pre-readers. Each panel clearly separated with thin white borders.
Square format, 3x3 grid.
```

---

## 2. A3: The Cat Is Here

**Characters:** Orange tabby cat, young child
**Setting:** Cozy home interior

```
9-panel children's book reference sheet, grid layout (3x3), consistent warm
watercolor style throughout all panels:

Row 1 - Cat Character:
[1] Orange tabby cat, friendly round face, sitting upright, front view,
    bright green eyes, white chest patch, cream background
[2] Same orange tabby walking, side view, tail up in happy curve,
    curious posture, fluffy fur texture
[3] Same cat curled up sleeping, peaceful expression, paws tucked under,
    soft cozy pose

Row 2 - Child & Objects:
[4] Young child (5-6 years old), round friendly face, short brown hair,
    wearing simple blue shirt, pointing excitedly, front view
[5] Colorful woven mat/rug, warm reds and oranges, soft texture,
    rectangular shape
[6] Simple hat on a wooden table, floppy brim, warm brown/tan color

Row 3 - Settings & Moments:
[7] Cozy living room corner, soft armchair, small houseplant,
    warm natural light from window
[8] Cat sitting proudly on top of the hat, pleased expression,
    looking at viewer
[9] Child hugging the cat, both happy, warm embrace, joyful moment

STYLE: Warm watercolor, soft edges, muted palette (sage, terracotta, cream,
soft gold), no hard outlines, friendly rounded shapes, simple expressive faces.
Each panel clearly separated with thin white borders.
Square format, 3x3 grid.
```

---

## 3. A4: Sam and the Hat

**Characters:** Sam the orange cat (main character)
**Setting:** Home with shelf/furniture

```
9-panel children's book reference sheet, grid layout (3x3), consistent warm
watercolor style throughout all panels:

Row 1 - Sam the Cat:
[1] Sam the orange cat, friendly determined expression, sitting upright,
    bright eyes looking up, white whiskers, cream background
[2] Sam walking/running, side view, tail streaming behind,
    athletic pose, eager expression
[3] Sam standing on hind legs, reaching upward, stretching tall,
    determined face

Row 2 - Objects & Props:
[4] Colorful hat, floppy wide brim, purple/blue with pattern,
    sitting on surface, inviting
[5] Tall wooden shelf/bookcase, hat visible on top shelf,
    out of reach, warm wood tones
[6] Colorful woven mat, Sam's home base, warm oranges and reds

Row 3 - Settings & Key Moments:
[7] Sam looking up at high shelf, longing expression,
    hat visible above, challenge established
[8] Sam mid-jump, athletic leap, reaching toward hat,
    dynamic action pose
[9] Sam wearing the hat proudly, triumphant expression,
    sitting on mat, mission accomplished

STYLE: Warm watercolor, soft edges, muted palette (sage, terracotta, cream,
soft gold), no hard outlines, friendly rounded shapes, expressive cat faces.
Each panel clearly separated with thin white borders.
Square format, 3x3 grid.
```

---

## 4. B1: Sam and the Cat

**Characters:** Sam (6-year-old child), orange tabby cat
**Setting:** Home interior, colorful mat

```
9-panel children's book reference sheet, grid layout (3x3), consistent warm
watercolor style throughout all panels:

Row 1 - Sam the Child:
[1] Sam, cheerful 6-year-old child, messy brown hair, wearing striped
    blue and white shirt, friendly round face, front view, cream background
[2] Sam sitting cross-legged, relaxed happy pose, hands on knees,
    content expression
[3] Sam running/moving, side view, arms out, joyful motion,
    energetic pose

Row 2 - Cat Character:
[4] Plump orange tabby cat, content expression, sitting,
    fluffy fur, white chest, bright green eyes
[5] Same cat curled up napping in a metal pan/pot, cozy pose,
    peaceful sleeping face
[6] Cat sitting on top of a hat, pleased mischievous expression,
    tail wrapped around

Row 3 - Settings & Moments:
[7] Colorful woven mat on floor, warm reds/oranges/yellows,
    cozy home setting
[8] Sam and cat together on mat, Sam petting the cat,
    warm bonding moment
[9] Sam hugging the plump cat, both happy, loving embrace,
    heartwarming finale

STYLE: Warm watercolor, soft edges, muted palette (sage, terracotta, cream,
soft gold), no hard outlines, friendly rounded shapes, expressive faces.
Each panel clearly separated with thin white borders.
Square format, 3x3 grid.
```

---

## 5. B4: Frog and Crab

**Characters:** Green frog, orange crab
**Setting:** Pond, grass, tree stump

```
9-panel children's book reference sheet, grid layout (3x3), consistent warm
watercolor style throughout all panels:

Row 1 - Frog Character:
[1] Friendly green frog, big expressive eyes, sitting upright,
    webbed feet visible, happy wide smile, cream background
[2] Same frog mid-hop, side view, legs extended, athletic pose,
    joyful expression
[3] Frog reaching out hand/arm to help, caring expression,
    heroic helpful pose

Row 2 - Crab Character:
[4] Orange crab, friendly face, two big claws raised cheerfully,
    multiple legs visible, happy expression, front view
[5] Same crab scuttling sideways, side view, legs in motion,
    playful movement
[6] Crab stuck in tree stump, worried expression, claws waving,
    needing help

Row 3 - Settings & Moments:
[7] Peaceful pond scene, blue water, lily pads, cattails,
    flat rock in foreground, sunny day
[8] Grassy area near pond, wildflowers, tree with blue flag,
    old tree stump visible
[9] Frog and Crab together on flat rock, best friends,
    clapping/celebrating, sunset light

STYLE: Warm watercolor, soft edges, muted palette (sage, terracotta, cream,
soft gold, pond blue), no hard outlines, friendly animal characters.
Each panel clearly separated with thin white borders.
Square format, 3x3 grid.
```

---

## 6. B5: The Ship in the Shell

**Characters:** Chuck (7-year-old boy), Beth (7-year-old girl)
**Setting:** Beach, sand, ocean

```
9-panel children's book reference sheet, grid layout (3x3), consistent warm
watercolor style throughout all panels:

Row 1 - Chuck:
[1] Chuck, 7-year-old boy, short dark hair, curious expression,
    wearing blue t-shirt and khaki shorts, front view, cream background
[2] Chuck kneeling in sand, reaching forward excitedly,
    side view, discovering something
[3] Chuck holding shell up to ear, wonder on face,
    listening intently

Row 2 - Beth:
[4] Beth, 7-year-old girl, brown hair in two braids, kind smile,
    wearing yellow sundress, front view, cream background
[5] Beth peering into something with curiosity, leaning forward,
    fascinated expression
[6] Beth with eyes closed, hands clasped, making a wish,
    peaceful hopeful expression

Row 3 - Objects & Settings:
[7] Large pink conch shell, pearlescent surface, detailed spiral,
    beautiful and magical
[8] Tiny ornate ship inside shell, glowing softly, golden details,
    flag with ring symbol, magical sparkles
[9] Sandy beach scene, gentle turquoise waves, warm sunset light,
    shells scattered on sand, peaceful

STYLE: Warm watercolor, soft edges, muted palette (sage, terracotta, cream,
soft gold, ocean blue, sunset pink), no hard outlines, friendly faces.
Each panel clearly separated with thin white borders.
Square format, 3x3 grid.
```

---

## 7. B7: The Rain and the Snow

**Characters:** Jean (7-year-old girl), Gray the goat
**Setting:** Home, snowy countryside, barn

```
9-panel children's book reference sheet, grid layout (3x3), consistent warm
watercolor style throughout all panels:

Row 1 - Jean:
[1] Jean, 7-year-old girl, wavy auburn hair, hopeful expression,
    wearing cozy sweater, front view, cream background
[2] Jean in winter coat, red scarf and mittens, ready for snow,
    excited expression, bundled up warm
[3] Jean looking out window, contemplative, hand on glass,
    watching weather change

Row 2 - Gray the Goat:
[4] Gray, friendly gray goat, soft fluffy coat, gentle eyes,
    small curved horns, standing, front view
[5] Same goat eating hay, content expression, munching happily,
    side view
[6] Gray walking through snow, careful steps, fur dusted white,
    patient expression

Row 3 - Weather & Settings:
[7] Rainy scene, raindrops on window, gray sky, puddles forming,
    cozy interior visible
[8] Snowy landscape, white snow falling, bare trees, magical
    transformation, soft and peaceful
[9] Jean and Gray together in snow, footprints behind them,
    sunset glow on snow, warm friendship moment

STYLE: Warm watercolor, soft edges, muted palette (sage, terracotta, cream,
soft gray, snow white, sunset gold), no hard outlines, cozy feeling.
Each panel clearly separated with thin white borders.
Square format, 3x3 grid.
```

---

## 8. B9: A Star at the Farm

**Characters:** Fern (8-year-old farm girl), horse, birds, turtle
**Setting:** Farm, barn, river, night sky

```
9-panel children's book reference sheet, grid layout (3x3), consistent warm
watercolor style throughout all panels:

Row 1 - Fern:
[1] Fern, 8-year-old farm girl, curly red hair, freckles, kind eyes,
    wearing overalls and boots, front view, cream background
[2] Fern running through rain, determined expression, protecting animals,
    action pose, mud on boots
[3] Fern sitting peacefully, looking up at sky, contemplative,
    gentle smile, starlight on face

Row 2 - Farm Animals:
[4] Short brown horse, gentle dark eyes, white blaze on nose,
    standing in barn doorway, patient expression
[5] Purple turtle, distinctive shell pattern, small and cute,
    curled partially, on wooden surface
[6] Small colorful birds (2-3), chirping, perched on fence post,
    cheerful, varied colors

Row 3 - Farm Settings:
[7] Red barn with farmhouse, green rolling hills, river nearby,
    peaceful sunny day, classic farm scene
[8] Storm scene, dark dramatic clouds, rain falling on farm,
    wind bending trees, dramatic but not scary
[9] Night sky over farm, one bright star prominent in north,
    barn silhouette, peaceful after storm, magical glow

STYLE: Warm watercolor, soft edges, muted palette (sage, terracotta, cream,
barn red, storm gray, starlight gold), no hard outlines, rural warmth.
Each panel clearly separated with thin white borders.
Square format, 3x3 grid.
```

---

## 9. C1: The Knight's Quest

**Characters:** Sir Knight, friendly gnome
**Setting:** Castle, forest, mountain

```
9-panel children's book reference sheet, grid layout (3x3), consistent warm
watercolor style throughout all panels:

Row 1 - Sir Knight:
[1] Noble knight, silver armor with blue accents, kind face visible,
    standing proud, holding sword at side, front view
[2] Knight on horseback, brown horse, traveling through forest,
    determined expression, cape flowing
[3] Knight kneeling respectfully, one knee down, humble pose,
    receiving blessing or gift

Row 2 - Gnome & Objects:
[4] Friendly gnome, long white beard, red pointed hat, twinkling eyes,
    sitting by campfire, small and wise, warm expression
[5] Ornate ceremonial knife, magical glow, intricate patterns on blade,
    special and powerful looking
[6] Ancient stone wall with mysterious symbols/writing, torch light,
    mysterious but not scary

Row 3 - Settings:
[7] Stone castle on hilltop, dawn light, flags flying,
    impressive but welcoming, blue sky
[8] Misty forest at night, tall trees, single glowing light ahead,
    mysterious path, magical atmosphere
[9] Mountain summit at sunrise, eight knights in circle,
    epic and triumphant, golden light

STYLE: Warm watercolor, soft edges, muted palette (sage, terracotta, cream,
stone gray, knight silver, forest green), no hard outlines, fantasy but friendly.
Each panel clearly separated with thin white borders.
Square format, 3x3 grid.
```

---

## 10. C3: The Kitten in the Basket

**Characters:** Mittens (orange kitten), brown rabbit
**Setting:** Cozy home, kitchen, garden

```
9-panel children's book reference sheet, grid layout (3x3), consistent warm
watercolor style throughout all panels:

Row 1 - Mittens the Kitten:
[1] Mittens, fluffy orange kitten, big round eyes, pink nose,
    white paws, curious expression, sitting, front view
[2] Same kitten in playful pose, paw raised, tail up,
    about to pounce, energetic and cute
[3] Kitten curled up sleeping, peaceful expression, fluffy ball,
    soft and cozy

Row 2 - Rabbit & Props:
[4] Brown rabbit, soft fluffy fur, long ears, twitching nose,
    calm gentle expression, sitting, front view
[5] Large woven basket, cozy blanket inside, warm and inviting,
    perfect for two small animals
[6] Carrot and lettuce, fresh vegetables, rabbit's favorite food,
    simple still life

Row 3 - Settings & Moments:
[7] Sunny kitchen, open window, wooden ladder against wall,
    homey and bright, warm light streaming in
[8] Garden view through window, rosebush, puppy running past,
    outdoor scene, sunny day
[9] Kitten and rabbit curled up together in basket, best friends,
    both sleeping peacefully, heartwarming

STYLE: Warm watercolor, soft edges, muted palette (sage, terracotta, cream,
soft gold, bunny brown), no hard outlines, extra fluffy and cute.
Each panel clearly separated with thin white borders.
Square format, 3x3 grid.
```

---

## 11. C5: The Treehouse Mystery

**Characters:** Maya (8-year-old girl), Ben (10-year-old brother), Biscuit (golden retriever)
**Setting:** Home, backyard, treehouse

```
9-panel children's book reference sheet, grid layout (3x3), consistent warm
watercolor style throughout all panels:

Row 1 - Maya:
[1] Maya, 8-year-old girl, dark curly hair in ponytail, determined expression,
    wearing purple t-shirt and jeans, front view, cream background
[2] Maya searching, looking under things, worried but active,
    problem-solving pose
[3] Maya laughing with relief, happy surprised expression,
    mystery solved moment

Row 2 - Ben & Biscuit:
[4] Ben, 10-year-old boy, short brown hair, kind supportive expression,
    wearing green shirt, big brother energy, front view
[5] Biscuit, golden retriever, fluffy golden fur, happy tongue out,
    loyal friendly expression, sitting
[6] Biscuit holding backpack in mouth, guilty but happy expression,
    tail wagging, caught in the act

Row 3 - Settings:
[7] Wooden treehouse in large oak tree, rope ladder,
    cozy adventure space, dappled sunlight
[8] Backyard garden, rosebush, green lawn, sunshine,
    family home in background
[9] Family at kitchen table, sandwiches and brownies,
    happy together, warm home scene

STYLE: Warm watercolor, soft edges, muted palette (sage, terracotta, cream,
soft gold, treehouse brown), no hard outlines, family warmth, cozy home feeling.
Each panel clearly separated with thin white borders.
Square format, 3x3 grid.
```

---

## Usage Instructions

### Generating Reference Sheets

1. Use these prompts with image generation AI (Midjourney, DALL-E, Stable Diffusion, etc.)
2. Generate at 1024x1024 or higher resolution
3. Save as `{book-id}_reference.png` (e.g., `b5-the-ship-in-the-shell_reference.png`)
4. Store in `/public/books/references/` directory

### Using Reference Sheets for Page Generation

When generating individual story pages, include the reference image and prompt like:

```
Using the attached reference sheet for character design, color palette,
and art style consistency:

[Insert scene description from book JSON]

Match the character appearances, watercolor style, and color palette exactly
from the reference sheet. Square format, character-focused composition.
```

### Consistency Tips

- Always reference specific panels: "Use Chuck's appearance from panel 1-2"
- Maintain the muted earthy palette across all generations
- Keep character proportions consistent (reference the character panels)
- Match lighting warmth to the reference sheet's overall tone

---

## Automated Image Generation

### Scripts

Three Python scripts automate the image generation workflow:

| Script | Purpose |
|--------|---------|
| `scripts/generate_references.py` | Generate 9-panel reference sheets for UFLI curriculum books |
| `scripts/generate_legacy_refs.py` | Generate reference sheets for legacy books with custom styles |
| `scripts/generate_covers.py` | Generate covers from reference images using image-to-image |

### Running the Scripts

```bash
# From the mulerouter skill directory
cd /path/to/mulerouter-skills

# Generate reference images
uv run python /path/to/lilbookies/scripts/generate_references.py

# Generate covers from references
uv run python /path/to/lilbookies/scripts/generate_covers.py
```

### No-Text Policy for Covers

**IMPORTANT:** Cover images should NOT contain any text, titles, or words.

The prompts explicitly instruct:
```
IMPORTANT: Do NOT include any text, titles, words, or letters in the image.
Pure illustration only.
```

Text overlays (book titles) are added dynamically by the reader UI, not baked into images. This allows:
- Consistent typography across all books
- Easy title updates without regenerating images
- Cleaner illustrations

### Image Paths

| Type | Path | Example |
|------|------|---------|
| Reference | `/books/references/{slug}_reference.png` | `/books/references/a0-look_reference.png` |
| Cover | `/images/covers/{slug}.png` | `/images/covers/a0-look.png` |
| Page | `/books/images/{slug}_page{NN}.png` | `/books/images/a0-look_page02.png` |

---

## Reader/Editor URLs

Books can be viewed in two modes:

| Mode | URL | Description |
|------|-----|-------------|
| Read | `/reader.html?book={slug}` | Full-screen reading experience |
| Edit | `/reader.html?book={slug}&mode=edit` | Side-by-side with reference image |

### Edit Mode Features

- Shows 9-panel reference image alongside book page
- Displays current page scene description
- Shows book metadata (slug, level)
- Toggle button to switch between modes
