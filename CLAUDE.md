# Claude Code Instructions for LilBookies

## Documentation Index

| Doc | Purpose | Read When |
|-----|---------|-----------|
| **[PROMPTING_CHEATSHEET.md](PROMPTING_CHEATSHEET.md)** | Quick reference for all prompting rules | First stop for any prompting question |
| [BOOK_CREATION_PROCESS.md](BOOK_CREATION_PROCESS.md) | 4-checkpoint workflow, validation | Starting a new book |
| [STORY_CONTENT_GUIDE.md](STORY_CONTENT_GUIDE.md) | Narrative principles, word categories | Writing story text |
| [STORY_RUBRIC.md](STORY_RUBRIC.md) | Quality checklist, dialogue rules | Reviewing story quality |
| [IMAGE_GENERATION_WORKFLOW.md](IMAGE_GENERATION_WORKFLOW.md) | Multi-ref architecture, models | Understanding image pipeline |
| [REFERENCE_IMAGE_PROMPTS.md](REFERENCE_IMAGE_PROMPTS.md) | 9-panel templates by level | Creating reference sheets |
| [BOOK_GENERATION_GUIDE.md](BOOK_GENERATION_GUIDE.md) | Conversational workflow | Step-by-step with checkpoints |

### The Five Golden Rules
1. **Never use negations** - "no ball" generates a ball
2. **Physical over emotional** - "eyes wide" not "scared"
3. **Explicit character presence** - say who IS and ISN'T there
4. **Single scene emphasis** - "One cohesive illustration filling the entire canvas"
5. **NO TEXT in every prompt** - always end with "NO TEXT, NO WORDS, NO LETTERS"

---

## Session Documentation

After completing work, document changes in `DEVLOG.md` with:
- Date and brief title
- Commit hash
- What was changed and why
- Files affected
- Any relevant notes for future sessions

## Links and File Access

When providing links to the user:

1. **Web URLs** - Put on their own line so they're clickable:
   ```
   https://funbookies.com/reader.html?book=d1-the-lighthouse-keeper
   ```

2. **Local files** - Use `file://` URLs (right-click → Open URL):
   ```
   file:///Users/dereklomas/lilbookies/public/books/references/example.png
   ```

3. **Or offer to open directly** - Use `open` command:
   ```bash
   open /path/to/file.png           # Opens in default app
   open https://funbookies.com      # Opens in browser
   ```

Always prefer giving the user clickable links rather than just file paths.

## Project Structure

- `/public/books/` - Book JSON files and assets
- `/public/books/references/` - 9-panel style reference images
- `/public/books/images/` - Generated page images
- `/public/images/covers/` - Cover images
- `/scripts/` - Python generation scripts

## Book Creation Process

**CRITICAL: Read `BOOK_CREATION_PROCESS.md` before creating any book images.**

The process has 4 checkpoints - NEVER skip them:

```
Story → Scene Descriptions → Reference Image → Page Images
          ↓                      ↓                 ↓
      CHECKPOINT 2          CHECKPOINT 3      CHECKPOINT 4
```

### Common Mistakes to Avoid

1. **Placeholder scenes** - Never run image generation if scenes say "Illustration for:"
   - Fix with: `python scripts/generate_scene_descriptions.py <slug>`
   - Validate with: `python scripts/validate_book_for_images.py <slug>`

2. **Grid output** - Reference is 9-panel, model will copy layout without instructions
   - `generate_page_images.py` now adds "Single scene illustration" automatically
   - Never say "not a grid" (activates "grid") - say "one cohesive illustration"

3. **Negations** - Don't say what ISN'T there
   - "no ball" → model generates a ball
   - Only describe what you WANT to see

4. **Missing character details** - Scene must include WHO/WHERE/WHAT/STYLE

### Book Image Generation Commands

```bash
# 1. After story generation, create proper scene descriptions
python scripts/generate_scene_descriptions.py the-big-pig

# 2. Validate before spending credits
python scripts/validate_book_for_images.py the-big-pig

# 3. Generate images (runs validation first)
python scripts/generate_page_images.py the-big-pig --provider mulerouter
```

## Image Generation Technical Details

See `IMAGE_GENERATION_WORKFLOW.md` for the full pipeline:
1. Reference sheets (nano-banana-pro) → style guide
2. Covers/pages (wan2.6-image) → style transfer from reference

## Key URLs

- Production: https://funbookies.com
- Reader: https://funbookies.com/reader.html?book={slug}
- Edit mode: https://funbookies.com/reader.html?book={slug}&mode=edit

## API Keys & Services

Environment variables stored in `.env` and Vercel:

### OpenAI (`OPENAI_API_KEY`)
- **TTS**: Generate voice audio (Nova voice for instructions, letter sounds)
- **GPT-4**: Book content generation, prompts
- **Scripts**: `generate_instruction_audio.py`, `regenerate_letter_sounds_openai.py`

### ElevenLabs (`ELEVENLABS_API_KEY`)
- **TTS with IPA phoneme tags**: Precise phoneme pronunciation
- **Models**: Use `eleven_turbo_v2` for phoneme tag support (NOT v2.5)
- **Voices**: Rachel (21m00Tcm4TlvDq8ikWAM) for American, Alice for British
- **Scripts**: `generate_phoneme_sounds.py`, `generate_all_letter_sounds.py`
- **SSML syntax**: `<phoneme alphabet="ipa" ph="ʃ">sh</phoneme>`

### MuleRouter/MuleRun (`MULEROUTER_API_KEY`)
- **Image generation**: Book covers, page illustrations
- **Video generation**: Animations
- **Models**: wan2.6-t2i, wan2.6-i2v, nano-banana-pro
- **Scripts**: Via mulerouter-skills plugin

## Audio File Locations

| Type | Path | Generated By |
|------|------|--------------|
| Letter sounds (a-z) | `/activities/letter-sounds/openai-us/sounds/` | OpenAI TTS |
| Letter names (A-Z) | `/activities/letter-sounds/openai-us/names/` | OpenAI TTS |
| Phonemes (blends, digraphs) | `/audio/phonemes/` | ElevenLabs IPA |
| Activity instructions | `/audio/instructions/` | OpenAI TTS |
| Coaching audio | `/audio/coaching/` | OpenAI TTS |

## Review Interfaces

- Phoneme sounds: `/activities/review/phoneme-sounds.html`
- (Add more review interfaces as needed)

## Useful Scripts

```bash
# Generate phoneme sounds (blends, digraphs, vowel teams)
uv run python scripts/generate_phoneme_sounds.py

# Generate activity instruction audio
uv run python scripts/generate_instruction_audio.py

# Generate letter sounds (both OpenAI and ElevenLabs)
uv run python scripts/generate_all_letter_sounds.py
```
