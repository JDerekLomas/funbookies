# FunBookies Brand Guide

## Brand Assets

### Logo System

| Asset | File | Usage |
|-------|------|-------|
| **Full Logo** | `funbookies_logo.png` | Hero sections, marketing, large displays |
| **Logomark** | `funbookies_icon.png` | Headers, favicons, app icons, small spaces |
| **Wordmark** | CSS text "FunBookies" | When icon is present, text-only contexts |

### Logo Usage Rules

- **Header**: Use logomark (icon only) + text "FunBookies" in CSS
- **Footer**: Full logo or logomark + wordmark
- **Favicon**: Logomark only
- **App Icon**: Logomark only
- **Marketing**: Full logo

---

## Colors

### Primary Palette

| Name | Hex | Usage |
|------|-----|-------|
| **Purple** | `#667eea` | Primary brand, headers, buttons |
| **Purple Dark** | `#764ba2` | Gradients, accents |
| **Orange** | `#FF9800` | Secondary, CTAs, highlights |
| **Yellow** | `#FFC107` | Accents, success states |

### Gradient

```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

### Activity Colors

| Activity | Color |
|----------|-------|
| Assessments | Purple `#667eea` |
| Word Builder | Orange `#FF9800` |
| Sight Words | Green `#4CAF50` |
| Rhyme Match | Pink `#E91E63` |
| Word Families | Blue `#2196F3` |
| Blend It | Teal `#009688` |

### Book Level Colors

| Level | Color | Skill |
|-------|-------|-------|
| 0 | Pink | Pre-reader |
| 1 | Yellow | Short vowels |
| 2-3 | Orange | CVC words |
| 4 | Red | Ending blends |
| 5 | Purple | Digraphs |
| 6 | Blue | Silent e |
| 7 | Green | Vowel teams |
| 8 | Gold | R-controlled |

---

## Typography

### Font Family

**Nunito** - Primary font for all text
- Headers: 700-900 weight
- Body: 400-600 weight

**Fredoka** - Display font for hero headlines

```css
font-family: 'Nunito', sans-serif;
```

### Type Scale

| Element | Size | Weight |
|---------|------|--------|
| H1 (Hero) | 3.5rem | 700 |
| H2 | 2.5rem | 700 |
| H3 | 1.5rem | 600 |
| Body | 1rem | 400 |
| Small | 0.875rem | 400 |

---

## Component Styles

### Buttons

**Primary (Yellow CTA)**
```css
background: #FFC107;
color: #333;
border-radius: 30px;
padding: 15px 35px;
font-weight: 700;
```

**Secondary (Purple outline)**
```css
background: rgba(255,255,255,0.1);
border: 2px solid white;
color: white;
border-radius: 30px;
```

### Cards

```css
background: white;
border-radius: 20px;
box-shadow: 0 10px 40px rgba(0,0,0,0.15);
```

### Gradients for Activities

```css
/* Purple */ linear-gradient(135deg, #667eea 0%, #764ba2 100%)
/* Green */  linear-gradient(135deg, #4CAF50 0%, #8BC34A 100%)
/* Orange */ linear-gradient(135deg, #FF9800 0%, #FFC107 100%)
/* Blue */   linear-gradient(135deg, #2196F3 0%, #03A9F4 100%)
/* Pink */   linear-gradient(135deg, #E91E63 0%, #FF5722 100%)
/* Teal */   linear-gradient(135deg, #009688 0%, #4DB6AC 100%)
```

---

## Voice & Tone

- **Friendly** - Warm, encouraging, never condescending
- **Simple** - Clear language parents and kids understand
- **Playful** - Fun without being childish
- **Supportive** - Celebrate progress, normalize mistakes

### Example Copy

**Good**: "Find the perfect books for your reader"
**Avoid**: "Optimize your child's literacy development"

**Good**: "Try again!"
**Avoid**: "Incorrect answer"

---

## File Organization

```
/images/
  funbookies_logo.png      # Full logo (icon + text)
  funbookies_icon.png      # Logomark only (for header)
  funbookies_logo_01-04.png # Logo variations (archive)
  funbookies_icon_01-04.png # Icon variations (archive)
/favicon.svg               # SVG favicon
```
