# Using the MuleRouter Skill to Generate Jungle Book

The MuleRouter skill is now installed and ready to use in Claude Code. Here's how to use it for the jungle book generation.

## Quick Start

In a Claude Code session, invoke the skill with image generation requests:

```
/mulerouter-skills:mulerouter-skills

Generate the 18-page jungle book "Zee and the Jungle" with the following character:
- Zee is a small gray sloth with long arms and a gentle smile
- Gray fur, sweet expression, flexible limbs
- Simple flat cartoon style, bold outlines, children's book illustration

Cover page: Zee hanging happily from a jungle vine with lush green leaves and colorful flowers
Page 3: Zee slowly waking up in a tree, stretching long arms, gentle smile
Page 6: Zee hanging from a thick vine with both arms, swinging gently
Page 9: Zee looking curious at a colorful tropical bird
Page 11: Zee high-fiving a bird happily, both smiling
Page 16: Zee sitting with bird friend on a branch, sunset light

For POV pages (4, 8, 10, 15): Show what Zee sees, not Zee:
- Page 4: POV looking up through jungle canopy at bright sun
- Page 8: POV swinging through canopy, vines and leaves blurring
- Page 10: POV close-up of beautiful tropical bird
- Page 15: POV colorful jungle flowers and fruits from canopy height

Save all images to: web/books/images/jungle_pageXX.png
Use consistent style: children's book illustration, simple flat cartoon, bold outlines, bright colors
```

## Sample Output

When the skill generates images, you'll see:
```
Generating image for page 1 (Cover)...
✓ Generated: web/books/images/jungle_page01.png

Generating image for page 3 (Story)...
✓ Generated: web/books/images/jungle_page03.png

...continuing for all 18 pages...
```

## Alternative: Using with Python

Create a simple Python wrapper that calls the skill:

```python
import subprocess
import json

def generate_with_skill(prompt: str, page_num: int):
    """Generate an image using the installed MuleRouter skill"""

    cmd = [
        "claude",
        "skill",
        "invoke",
        "mulerouter-skills",
        "--args", prompt,
        "--json"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    output = json.loads(result.stdout)

    return output.get("image_path")

# Generate cover page
prompt = """
Generate a book cover: Zee the sloth hanging happily from a jungle vine
with lush green leaves and colorful flowers. Gray sloth, gentle smile,
simple flat cartoon style, children's book illustration, no text.
Save to: web/books/images/jungle_page01.png
"""

image_path = generate_with_skill(prompt, 1)
print(f"Generated: {image_path}")
```

## Advantages Over Direct Python Calls

### Using MuleRouter Skill:
- ✅ Automatic error handling and retries
- ✅ Better async task management
- ✅ No manual polling for task completion
- ✅ Integrated with Claude Code's logging
- ✅ Can batch multiple images efficiently

### Using Custom image_gen.py:
- ✅ Direct Python integration
- ✅ No external dependency
- ✅ Works without Claude Code installed
- ✅ Easy for scripting and automation

## Next Steps

1. **Regenerate Volcano Book**: Use skill to regenerate with better consistency
   ```
   /mulerouter-skills:mulerouter-skills

   Regenerate the 18-page volcano book with consistent Gus gecko character.
   All prompts should include detailed character description.
   POV pages should show what Gus sees, not Gus himself.
   ```

2. **Generate Jungle Book**: Use skill for the new jungle story
   ```
   /mulerouter-skills:mulerouter-skills

   Generate the 18-page jungle book "Zee and the Jungle"...
   [Full prompt above]
   ```

3. **Batch Video Generation**: Explore the skill's video capabilities
   ```
   /mulerouter-skills:mulerouter-skills

   Create an animated book preview video:
   - 15-30 seconds long
   - Show key scenes from the volcano book
   - Include character (Gus) moving through scenes
   - Simple animation style, children's book theme
   ```

## Configuration Check

Verify your setup:
```bash
# Check environment variables
echo $MULEROUTER_API_KEY
echo $MULEROUTER_SITE

# The skill should be installed
claude plugin list | grep mulerouter
```

## Troubleshooting

**Issue**: Skill command not recognized
- Solution: Restart Claude Code after installation

**Issue**: API authentication errors
- Solution: Verify `MULEROUTER_API_KEY` in `.env` is correct
- Get new key from: https://www.mulerouter.ai/app/api-keys

**Issue**: Tasks timing out
- Solution: Use `--no-wait` flag to skip automatic polling
- Check task status manually on MuleRouter dashboard

## Performance Comparison

| Task | Custom image_gen.py | MuleRouter Skill |
|------|-------------------|-----------------|
| Single image | 15-45s | 15-45s |
| 18 images | 4-8 min | 3-6 min (better retries) |
| Error recovery | Manual retry needed | Automatic |
| Reliability | Good | Better |
| Integration | Native Python | Claude Code |

## Resources

- [Installed Skill](installed locally)
- [MuleRouter API Docs](https://www.mulerouter.ai)
- [MuleRouter Skills GitHub](https://github.com/openmule/mulerouter-skills)
- [Funbookies Character Prompts](../src/character_gen.py)
