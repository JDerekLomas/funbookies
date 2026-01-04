# Funbookies Story Library

Phonics-based decodable readers for early literacy.

## Reading Level System

| Level | Color | File | Title | Character | Phonics Focus |
|-------|-------|------|-------|-----------|---------------|
| 0 | Pink | `dog_pink.json` | No, No, Dog! | Brown dog | Pre-reader (1-2 words) |
| 1 | Yellow | `pig_yellow.json` | Pig in Mud | Pink pig | CVC words |
| 2 | Orange | `volcano_v2.json` | Gus and the Volcano | Gus salamander | Digraphs (sh, ch, th) |
| 3 | Red | `elephant_red.json` | Stomp! Stomp! Elephant | Baby elephant | Blends (st, mp, nd) |
| 4 | Purple | `fox_purple.json` | The Cake Mistake | Fox | Magic E (cake, like) |
| 5 | Blue | `snail_blue.json` | The Sneaky Snail | Snail | Vowel teams (ee, ea, ai) |
| 6 | Green | `owl_green.json` | The First Star | Owl | R-controlled (ar, er, ir) |
| 7 | Gold | `mouse_gold.json` | Mouse in the House | Mouse | Diphthongs (oi, ou, ow) |
| 8 | Silver | `puppy_silver.json` | Puppy's Birthday | Puppy | Multisyllabic words |

## Story JSON Structure

```json
{
  "title": "Story Title",
  "version": "v2-riso",
  "level": "color_name",
  "level_number": 0-8,
  "level_description": "Phonics focus and word count",
  "riso_colors": {
    "black": "outlines",
    "color_a": {"name": "Color Name", "use": "character"},
    "color_b": {"name": "Color Name", "use": "accents"}
  },
  "character": {
    "name": "Character Name",
    "species": "animal type",
    "description": "Visual description for consistency"
  },
  "word_list": {
    "sound_out": ["decodable", "words"],
    "sight": ["high", "frequency", "words"],
    "new": ["vocabulary"]
  },
  "pages": [
    {"page": 1, "type": "cover|wordlist|story|end", "text": "...", "image_prompt": "..."}
  ]
}
```

## Character Reference Images

Located in `../reference_images/`:
- `dog_ref.png` - Brown fluffy dog
- `pig_ref.png` - Pink round pig
- `elephant_ref.png` - Gray baby elephant
- `fox_ref.png` - Orange fox with white chest
- `snail_ref.png` - Yellow snail with brown shell
- `owl_ref.png` - Brown owl with yellow eyes
- `mouse_ref.png` - Gray mouse
- `puppy_ref.png` - Yellow fluffy puppy
- `gus_ref_*.png` - Gus the orange salamander

## Riso Print Style

All images use a limited color palette suitable for Riso printing:
- Bold black outlines
- 2-3 spot colors per book
- Flat fills, no gradients
- Simple cartoon style

## Legacy Files

Other JSON files in this directory are experimental/legacy versions:
- `*_orange.json` - Earlier orange level experiments
- `*_story.json` - Original story drafts
- `*_curated.json` - Manually curated versions
