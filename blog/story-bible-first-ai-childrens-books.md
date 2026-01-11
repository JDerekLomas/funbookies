# Story Bible First: A New Workflow for AI-Generated Children's Books

*How we solved character consistency and narrative coherence by flipping the typical AI illustration workflow on its head.*

---

When we started building [FunBookies](https://funbookies.com), an AI-powered platform for decodable children's books, we ran into the same problem everyone does: **character consistency**.

Generate a cute cloud character for page 1. Generate it again for page 5. You get two completely different clouds. The rosy cheeks disappear. The expression changes. The art style drifts. For a children's book—where kids need to recognize and emotionally connect with characters across pages—this is a dealbreaker.

The standard solutions didn't quite fit our needs:

- **LoRA training**: Effective but slow. Train a model on 10-20 images, wait an hour, hope it works.
- **Character reference features**: Better, but optimized for maintaining appearance, not emotional range.
- **Detailed prompting**: Helps, but "small white fluffy cloud with rosy cheeks and big blue eyes" produces different results every time.

We needed something different. What we landed on combines two ideas that usually live separately: **story bibles** (from writing) and **reference sheets** (from illustration). The result is a workflow we call "Story Bible First."

## The Problem with "Text First" Workflows

Most AI children's book tools follow this pattern:

```
Write story text → Generate illustrations for each page
```

This creates two problems:

**1. Illustrations are an afterthought.** The AI sees "Pup ran to the mud" and generates *something*—but without understanding where this moment fits in the emotional arc, what came before, or what comes after.

**2. Simplified text = simplified images.** When you're writing for emergent readers (ages 4-6), text gets reduced to CVC words: "The pup is sad." The AI generates a generic sad puppy. But the *story* isn't generic—there's a reason the pup is sad, a journey that led here, and a resolution coming. That richness gets lost.

The result? Books that feel flat. Simple text, simple images, simple story.

## The Insight: Separate Narrative from Reading Level

Professional children's book authors don't write "simple stories." They write *sophisticated stories told simply*. The emotional arc, character development, and thematic depth of a great picture book rivals adult fiction—it's just expressed in fewer words.

Our insight was to separate these concerns:

1. **Story Bible**: The rich, unrestricted narrative (not constrained by reading level)
2. **Visual Reference**: Character design across emotional states (not just angles)
3. **Level Adaptation**: Simplify text while preserving emotional beats
4. **Page Generation**: Images generated from the rich story bible, not the simple text

## The Story Bible

Before writing a single word of child-readable text, we create a comprehensive story bible:

```json
{
  "story_bible": {
    "premise": "Clover is a small, fluffy cloud who loves floating peacefully
                in the blue sky. But whenever storm clouds gather and thunder
                rumbles, Clover hides behind the sun, terrified...",

    "themes": ["overcoming fear", "finding your purpose", "helping others"],

    "character_arcs": {
      "Clover": "Timid and fearful → Pushed to help → Terrified during storm
                → Sees flowers bloom → Proud and joyful"
    },

    "emotional_beats": [
      {"page": 1, "beat": "Peace - Clover floating happily"},
      {"page": 2, "beat": "Fear - Thunder sounds, Clover hides"},
      {"page": 7, "beat": "Empathy - Seeing the wilting flowers"},
      {"page": 10, "beat": "Terror - Thunder booms, eyes shut"},
      {"page": 12, "beat": "Joy - Seeing flowers bloom"},
      {"page": 14, "beat": "Pride - Clover loves storms now"}
    ],

    "visual_style": "Soft dreamy watercolor. Clover has big expressive eyes,
                     rosy pink cheeks. Sky transitions from sunny yellows to
                     storm purples to rainbow celebration."
  }
}
```

This document captures everything the simplified text cannot: *why* the character feels what they feel, *how* they transform, *what* the story is really about.

## The Reference Sheet: Emotional States, Not Camera Angles

Here's where our approach diverges from standard practice.

**Typical character reference sheets** show the same character from multiple angles—front view, side view, back view, 3/4 view. They're designed for 3D modeling and animation, ensuring the character looks consistent when rotated.

**Our reference sheets** show the same character across multiple *emotional states*—happy, scared, sad, determined, joyful, proud. They're designed for storytelling, ensuring the character looks consistent while *feeling* different things.

We generate a 9-panel grid where each panel corresponds to a key emotional beat from the story bible:

```
Panel 1: Clover happy in sunny blue sky
Panel 2: Clover scared, hiding behind sun
Panel 3: Clover sad and lonely
Panel 4: Gus (wind friend) encouraging Clover
Panel 5: Wilting flowers needing rain
Panel 6: Clover in storm, eyes shut, rain falling
Panel 7: Flowers blooming in the rain
Panel 8: Clover joyful, thunder as celebration
Panel 9: Happy ending with rainbow
```

![Reference sheet showing Clover the Cloud in 9 emotional states](/books/references/clover-the-cloud_reference.png)

This single image becomes the "source of truth" for the entire book—not just what the character looks like, but how they express the full range of emotions the story requires.

## The Generation Workflow

With story bible and reference sheet in hand, the actual page generation becomes straightforward:

```
For each page:
  1. Get the emotional beat from story bible
  2. Get the scene description (rich, detailed)
  3. Use reference sheet as style transfer input
  4. Generate image that matches the emotional beat
```

The key insight: **the image prompt comes from the story bible, not the simplified text.**

When we generate the image for "BOOM! Clover hid her eyes," the AI doesn't just see those five words. It sees:

> "Clover in the middle of the storm, eyes squeezed tightly shut, looking scared. Thunder visualized as golden zigzags around her. Rain beginning to fall from the bottom of her fluffy form. Dramatic moment but not terrifying."

Plus the reference sheet showing exactly what "scared Clover" looks like.

## The Results

This workflow produces books where:

1. **Characters stay consistent** across all pages—same rosy cheeks, same expressive eyes
2. **Emotional range is preserved** even when text is simplified to CVC words
3. **Art style remains unified** because every image uses the same reference
4. **Stories feel sophisticated** even when readable by 5-year-olds

Here's "Clover the Cloud"—a Band B decodable reader (ages 4-6) with text like "The pup got wet!" but illustrations that carry real emotional weight:

[View the book →](https://funbookies.com/reader.html?book=clover-the-cloud)

## Making It Transparent: Creation Notes

We've also added something unusual: a "Creation Notes" page visible in edit mode that shows the full story bible.

[View in edit mode →](https://funbookies.com/reader.html?book=clover-the-cloud&mode=edit)

Why expose the process? Because we think there's value in showing *how* AI-generated content was created. For educators, it demonstrates the intentionality behind the book. For other creators, it's a template they can learn from.

## The Workflow Script

We've open-sourced the workflow as a Python script. Given a premise and target reading level, it generates:

1. Prompts for creating a story bible
2. Prompts for level-appropriate text adaptation
3. Prompts for scene descriptions
4. The complete book JSON structure

```bash
python story_bible_workflow.py \
  --premise "A shy octopus learns to make friends" \
  --title "Otto Makes Friends" \
  --band B \
  --show-prompts
```

The script doesn't call an LLM directly—it generates the prompts you'd use with Claude, GPT-4, or any capable model. This keeps it flexible and avoids API lock-in.

## What We Learned

**1. Narrative structure matters more than we expected.**

The emotional beats in the story bible do more work than any prompt engineering. When you know *why* a character is scared on this page, the image captures it better.

**2. Reference sheets should match your use case.**

The 3D modeling community perfected turnaround sheets. But for illustrated books, emotional range matters more than viewing angles. Design your reference for what you actually need.

**3. Separating concerns enables quality at each layer.**

Story bible quality isn't constrained by reading level. Visual quality isn't constrained by simple text. Text quality isn't constrained by what's illustratable. Each layer can be optimized independently.

**4. The "simple" text isn't where the story lives.**

"The pup is sad" is just a reading exercise. The story lives in the illustrations, in the emotional arc, in the sophisticated narrative underneath. AI lets us have both—decodable text for learning to read, rich visuals for experiencing story.

## Try It Yourself

The full workflow is available in our GitHub repo:
- `STORY_BIBLE_SCHEMA.md` - The schema definition
- `scripts/story_bible_workflow.py` - The generation workflow
- `public/books/clover-the-cloud.json` - A complete example

We're also curious what others are doing in this space. If you've developed techniques for AI-generated children's books—especially around consistency and narrative coherence—we'd love to hear about it.

---

*FunBookies creates AI-powered decodable readers for early literacy. Our books combine phonics-focused text with rich, consistent illustrations generated using the Story Bible First workflow.*

*[funbookies.com](https://funbookies.com)*
