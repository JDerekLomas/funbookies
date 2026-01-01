# MuleRouter Skill Integration

The MuleRouter Agent Skill provides an alternative to our custom `image_gen.py` for generating images and videos.

## Installation

The skill needs to be installed in your Claude Code environment:

```bash
claude plugin install mulerouter-skills
```

Then restart Claude Code to load the skill.

## Configuration

The skill requires two environment variables (already set in `.env`):

```env
MULEROUTER_SITE=mulerouter
MULEROUTER_API_KEY=sk-mr-2dfbbdfe5bbd2e24235960b2d4f5b45bf1b59a087bc2524ff35c6c70a2657436
```

## Using the Skill via Claude Code

Within Claude Code sessions, you can invoke the skill directly:

```
/mulerouter-skills:mulerouter-skills
```

Or ask Claude to generate images:
```
Generate an image of a small lime-green gecko on a volcanic crater using MuleRouter
```

## Available Models

The skill supports multiple models from the Wan2.6 series and Nano Banana Pro:

- **Text-to-Image** - `nano-banana-pro` (current for book illustrations)
- **Image-to-Image** - Transform existing images
- **Text-to-Video** - Generate short videos
- **Image-to-Video** - Animate static images

## Advantages Over Custom image_gen.py

| Feature | Custom Script | Skill |
|---------|---------------|-------|
| Reliability | Good | Better (MuleRouter maintained) |
| Async Polling | Manual | Automatic |
| Error Handling | Basic | Robust |
| Video Support | No | Yes |
| Maintenance | Our responsibility | MuleRouter's responsibility |
| Integration | Direct Python | Via Claude Code |

## Use Cases for the Skill

### 1. Quick Image Generation in Claude Sessions
When working interactively in Claude Code:
```
Generate 5 illustrations of Rita and Rico rats for page 5 of the castle book
```

### 2. Batch Processing
Use the skill to regenerate multiple pages with better error handling:
```
Regenerate all POV images (pages 4, 6, 7, 8, 10, 11, 14, 15, 18)
for the volcano book using MuleRouter
```

### 3. Video Generation
The skill supports video generation - potential for:
- Animated book page previews
- Character animation clips
- Story walkthroughs

## Comparison: Custom Script vs Skill

### Using Custom image_gen.py (Current)
```python
from image_gen import ImageGenerator

gen = ImageGenerator(backend="mulerouter")
path = gen.generate(
    prompt="A small gecko on a volcano",
    filename="test"
)
```

### Using MuleRouter Skill (Future)
```
/mulerouter-skills:mulerouter-skills
Generate an image of a small gecko on a volcano.
Save to web/books/images/test.png
```

## Recommended Path Forward

1. **Current approach**: Keep using custom `image_gen.py` - it works well
2. **When regenerating large batches**: Use the skill via Claude Code for better reliability
3. **For video features**: Explore the skill's video generation capabilities
4. **Long-term**: Consider transitioning to the skill once we have more experience with it

## Example: Regenerating Volcano Book with Skill

```
Using the MuleRouter skill, regenerate all 24 pages of the volcano book.

For character pages, use detailed Gus gecko description.
For POV pages, use landscape/environment descriptions only.
Save all images to web/books/images/volcano_pageXX.png

Use the same master style for all:
"children's book illustration, simple flat cartoon style,
bold black outlines, bright saturated colors, age-appropriate for 6-7 year olds"
```

## Troubleshooting

**Skill not found:**
- Install it: `claude plugin install mulerouter-skills`
- Restart Claude Code
- Check that `MULEROUTER_SITE` and `MULEROUTER_API_KEY` are set

**API Key errors:**
- Verify key in `.env`: `MULEROUTER_API_KEY=sk-mr-...`
- Get new key from [MuleRouter dashboard](https://www.mulerouter.ai/app/api-keys)

**Timeout issues:**
- Use `--no-wait` flag to skip polling
- Check task status manually on MuleRouter dashboard

## References

- [MuleRouter Skills GitHub](https://github.com/openmule/mulerouter-skills/)
- [MuleRouter API Docs](https://www.mulerouter.ai)
- [MuleRouter Dashboard](https://www.mulerouter.ai/app/api-keys)
