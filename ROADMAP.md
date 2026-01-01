# Funbookies Roadmap

> Little books, big adventures - Pixi-style books for beginning readers in the Netherlands and beyond.

## Vision

Create affordable, colorful mini-books (like German Pixi books) for beginning readers ages 6-7, with an automated AI-powered pipeline from story generation to print-on-demand fulfillment.

## Goals

1. **Quality Content**: Research-backed early reader stories using Science of Reading principles
2. **Visual Consistency**: AI-generated illustrations with consistent characters across pages
3. **Print-Ready**: 10x10cm Pixi format, saddle-stitched, professional quality
4. **Affordable**: Low per-unit cost through print-on-demand, no inventory
5. **Automated**: End-to-end pipeline via Claude Code skill

---

## Current Status

### Completed
- [x] Book format: 10x10cm, 24 pages, saddle-stitch spec
- [x] Story generation with decodable text (CVC words, sight words)
- [x] Image generation via MuleRouter API
- [x] Character consistency system (Gus gecko, Rita/Rico rats, Zee sloth)
- [x] POV shot framework (mix of character shots and first-person views)
- [x] Web reader at funbookies.com
- [x] Print preview layout (70% image / 30% opaque text)
- [x] PDF generator for print-ready files

### Books Ready
| Book | Story | Images | JSON | Print PDF |
|------|-------|--------|------|-----------|
| Gus and the Volcano | Yes | Yes (24) | Yes | Yes |
| Rats in the Castle | Yes | Yes (18) | Yes | Yes |
| Zee and the Jungle | Yes | No | Yes | Needs images |

### Needs Work
- [ ] Generate jungle book images with consistent Zee sloth
- [ ] Review all images for character consistency
- [ ] Test print with actual print shop
- [ ] Integrate print-on-demand API

---

## Print-on-Demand Options

### Netherlands-Based (Recommended for EU)

| Service | API | Notes |
|---------|-----|-------|
| [Print API](https://www.printapi.io/) | REST | Netherlands gateway to EU, 5-day delivery, no monthly fees |
| [Print&Bind](https://www.printenbind.nl/en/order-api) | REST | Dutch, webshop integration |
| [Peecho](https://www.peecho.com/solutions/print-api) | REST | Amsterdam HQ, global network, photo books |

### Global with EU Fulfillment

| Service | API | Notes |
|---------|-----|-------|
| [Lulu](https://developers.lulu.com/) | REST | 3000+ formats, children's book personalization, ships to 150 countries |
| [Prodigi](https://www.prodigi.com/print-api/) | REST | UK/EU production, global partners |
| [Bookvault](https://bookvault.app/) | REST | UK-based, direct API fulfillment |
| [Blurb](https://www.blurb.com/print-api-software) | REST | Trade books, photo books |

### Recommended Path
1. **Development**: Lulu (best docs, free tier, children's book support)
2. **Production EU**: Print API or Peecho (closer to Netherlands)
3. **Scale**: Multi-provider for regional fulfillment

---

## Claude Code Skill Roadmap

### Phase 1: Book Generation Skill
```
/funbookies create "topic" --character "name and description"
```
- Generate story with word lists
- Create image prompts
- Generate images via MuleRouter
- Output JSON book file

### Phase 2: Image Refinement
```
/funbookies regenerate book.json --pages 3,5,7 --pov
```
- Regenerate specific pages
- Toggle POV vs character shots
- Apply character consistency

### Phase 3: Print Production
```
/funbookies print book.json --service lulu --quantity 10
```
- Generate print PDF
- Upload to print-on-demand API
- Track order status

### Phase 4: Full Automation
```
/funbookies publish "My Adventure" --print 50 --digital
```
- End-to-end: topic to printed books
- Digital distribution (EPUB, web)
- Print fulfillment
- Sales tracking

---

## Technical Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Claude Code Skill                     │
├─────────────────────────────────────────────────────────┤
│  /funbookies create | regenerate | print | publish      │
└─────────────────────────────────────────────────────────┘
                            │
            ┌───────────────┼───────────────┐
            ▼               ▼               ▼
    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │ Story Gen    │ │ Image Gen    │ │ Print Gen    │
    │ (LLM API)    │ │ (MuleRouter) │ │ (fpdf2)      │
    └──────────────┘ └──────────────┘ └──────────────┘
            │               │               │
            ▼               ▼               ▼
    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │ book.json    │ │ images/*.png │ │ book.pdf     │
    └──────────────┘ └──────────────┘ └──────────────┘
                            │
            ┌───────────────┴───────────────┐
            ▼                               ▼
    ┌──────────────┐               ┌──────────────┐
    │ Web Reader   │               │ Print API    │
    │ funbookies.  │               │ (Lulu/Peecho)│
    │ com          │               │              │
    └──────────────┘               └──────────────┘
```

---

## File Structure

```
minibooks/
├── src/
│   ├── book_maker.py      # End-to-end pipeline
│   ├── story_gen.py       # LLM story generation
│   ├── image_gen.py       # MuleRouter image generation
│   ├── character_gen.py   # Character consistency
│   ├── epub_generator.py  # EPUB creation
│   ├── pdf_generator.py   # Print PDF creation
│   └── config.py          # Pixi specs, brand info
├── web/
│   ├── index.html         # Book library
│   ├── print-preview.html # Print layout preview
│   └── books/
│       ├── *.json         # Book data
│       └── images/*.png   # Page images
├── output/
│   └── print/*.pdf        # Print-ready PDFs
├── docs/
│   └── character-consistency.md
└── ROADMAP.md             # This file
```

---

## Next Steps

1. **Immediate**: Generate Zee sloth images for jungle book
2. **This Week**: Test print with Print API or Lulu
3. **This Month**: Build basic Claude Code skill
4. **Q1 2025**: Launch first physical books for sale

---

## Resources

- [Lulu Print API Docs](https://developers.lulu.com/)
- [Peecho API Docs](https://www.peecho.com/print-api-documentation)
- [Print API (NL)](https://www.printapi.io/)
- [Midjourney Character Reference](https://docs.midjourney.com/hc/en-us/articles/32162917505293-Character-Reference)
- [Science of Reading](https://www.readingrockets.org/topics/about-reading/articles/science-reading-basics)
