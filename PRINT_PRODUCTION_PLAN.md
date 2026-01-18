# FunBookies Print Production Plan

## Recommended Print Partner: Peecho (Amsterdam)

**Why Peecho:**
- Based in Amsterdam (EU fulfillment)
- Free API, no subscription fees
- Auto-generates bleed and spine
- 2-7 working days delivery in Western Europe
- Good for photo-heavy children's books

**Alternative: Bookvault (UK)**
- Specifically praised for children's book durability
- 150gsm coated paper recommended for children's books
- Custom sizes up to 297x297mm

---

## Book Specifications

### Trim Size: 8" x 8" (203mm x 203mm)

Square format is ideal for children's books. Closest matches:
| Service | Available Size |
|---------|---------------|
| Lulu | 8.5" x 8.5" (216mm) |
| Prodigi | 8.3" x 8.3" (210mm) |
| Bookvault | Custom 8" x 8" |
| Peecho | Check catalog |

### Page Count: 32 pages

- Industry standard for picture books
- Two 16-page signatures
- Usable narrative: 26-28 pages (after title, copyright, etc.)
- Must be multiple of 8 for cost efficiency

### Interior Pages

| Spec | Value |
|------|-------|
| Paper | 150-200 gsm coated gloss |
| Resolution | 300 DPI |
| Color | CMYK |
| Bleed | 0.125" (3mm) all sides |
| Safe margin | 0.375" from trim |

### Image Dimensions (at 300 DPI)

| Element | Pixels | Inches |
|---------|--------|--------|
| Page (no bleed) | 2400 x 2400 | 8" x 8" |
| Page (with bleed) | 2475 x 2475 | 8.25" x 8.25" |
| Spread (no bleed) | 4800 x 2400 | 16" x 8" |
| Spread (with bleed) | 4875 x 2475 | 16.25" x 8.25" |

---

## Cover Specifications

### Softcover (Perfect Bound)

**Spine Width Calculation:**
```
Spine = (Page Count ÷ PPI) + 0.0156"
```
For 32 pages on 150gsm paper (~400 PPI):
```
Spine = (32 ÷ 400) + 0.0156" = ~0.096" (2.4mm)
```

**Cover Flat Dimensions (8x8 book, 32 pages):**
```
Width = 8" + 0.096" + 8" + 0.25" bleed = 16.346"
Height = 8" + 0.25" bleed = 8.25"
```
At 300 DPI: **4904 x 2475 pixels**

### Hardcover (Case Wrap)

**Case extends 0.25" beyond pages on all sides**

Finished case size: 8.5" x 8.5"

**Cover Wrap Dimensions:**
- Includes 0.625" wrap on all edges
- Includes hinge allowance (0.4" each side of spine)

```
Width = 8.5" + 0.625" + 0.4" + spine + 0.4" + 8.5" + 0.625"
Height = 8.5" + 0.625" + 0.625" = 9.75"
```

---

## File Specifications

### PDF Export Settings

| Setting | Value |
|---------|-------|
| Format | PDF/X-4 (or PDF/X-1a for compatibility) |
| Color | CMYK |
| ICC Profile | FOGRA39 (Europe) or GRACoL2006 (US) |
| Resolution | 300 DPI |
| Fonts | Embedded |
| Transparency | Flattened (PDF/X-1a) or preserved (PDF/X-4) |

### File Structure

**Interior PDF:**
- Single PDF with all pages
- Pages in reading order (not spreads)
- Include bleed on all pages

**Cover PDF:**
- Single file: Back cover | Spine | Front cover
- OR three separate files (check with printer)

---

## Implementation Phases

### Phase 1: High-Resolution Image Pipeline

**Current state:** Images generated at web resolution (~1024px)

**Needed:**
1. Update `generate_page_images.py` to support `--resolution print` flag
2. Generate at 2475x2475px (8.25" with bleed at 300dpi)
3. Store print images in `/public/books/print/{slug}/`
4. Add `print_images` field to book JSON

**Script changes:**
```python
# Add to generate_page_images.py
RESOLUTIONS = {
    'web': 1024,
    'print': 2475  # 8.25" at 300dpi
}
```

### Phase 2: PDF Generation

**Option A: Server-side with Puppeteer**
- Create print layout HTML template
- Render to PDF with correct dimensions
- Add bleed, crop marks

**Option B: Client-side with jsPDF**
- Generate in browser
- Download button in edit mode

**Option C: Dedicated print service**
- Use Peecho/Bookvault API to generate print-ready files
- They handle bleed/spine automatically

**Recommended: Option C** - Let the print service handle PDF generation

### Phase 3: Print API Integration

1. **Set up Peecho account**
   - Register at peecho.com
   - Get API credentials

2. **Create `/api/print-order.js`**
   ```javascript
   // Endpoints needed:
   // POST /api/print-order - Create print order
   // GET /api/print-order/[id] - Check order status
   // GET /api/print-quote - Get pricing
   ```

3. **Add print UI**
   - "Order Print Copy" button in reader
   - Preview with pricing
   - Checkout flow

### Phase 4: Cover Generation

**Current covers:** Generated at web resolution

**Needed:**
1. Generate high-res cover images (2475x2475px front, same for back)
2. Create cover spread template with spine
3. Add barcode/ISBN area on back cover

**Cover spread generator:**
```javascript
// Inputs: front cover, back cover, spine width, ISBN
// Output: Single PDF with full cover spread
```

---

## Print API Comparison

| Feature | Peecho | Bookvault | Lulu |
|---------|--------|-----------|------|
| Location | Amsterdam | UK | Global |
| API Cost | Free | $20/format | Free |
| 8x8 Size | Check | Custom | 8.5x8.5 |
| Hardcover | Yes | Yes | Yes |
| Auto-bleed | Yes | No | Template |
| Spine calc | API endpoint | Manual | API/formula |
| EU delivery | 2-7 days | 3-5 days | 5-7 days |

---

## Cost Estimates (per book)

Based on 32-page, 8x8", full color:

| Type | Peecho | Bookvault | Lulu |
|------|--------|-----------|------|
| Softcover | ~€8-12 | ~£6-8 | ~$8-10 |
| Hardcover | ~€15-20 | ~£12-15 | ~$15-18 |

*Plus shipping. Volume discounts available.*

---

## Timeline

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Phase 1: Hi-res images | 1 week | Update generation scripts |
| Phase 2: PDF generation | 1 week | Phase 1 complete |
| Phase 3: Print API | 2 weeks | Account setup, API integration |
| Phase 4: Covers | 1 week | Spine calculator, barcode |

**Total: 5-6 weeks**

---

## Next Steps

1. [ ] Choose print partner (recommend Peecho for EU)
2. [ ] Set up account and get API credentials
3. [ ] Update image generation for print resolution
4. [ ] Create print cover template
5. [ ] Build PDF export functionality
6. [ ] Integrate print ordering API
7. [ ] Add UI for ordering prints

---

## Resources

- [Peecho API Docs](https://www.peecho.com/print-api-documentation)
- [Bookvault Help](https://help.bookvault.app/)
- [Lulu API](https://developers.lulu.com/)
- [PDF/X Standards](https://en.wikipedia.org/wiki/PDF/X)
