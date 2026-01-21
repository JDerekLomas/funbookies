# Wizard Automation Session - 2026-01-21

## What We Did

### 1. Added Model Selector to Multi-Ref View
- **Problem**: nano-banana-pro service was unavailable (error 3002), but multi-ref had no way to switch models
- **Solution**: Added `#multiRefModelSelect` dropdown to multi-ref view in index.html
- **Files**: `public/wizard/index.html:433-440`, `public/wizard/wizard.js:1701`

### 2. Fixed Cascade Error Handling
- **Problem**: When styleGuide generation failed, the cascade continued trying openingScenes/closingScenes
- **Solution**: Re-throw errors from `generateMultiRefSheet()` so `generateAllMultiRefs()` catch block stops the cascade
- **Files**: `public/wizard/wizard.js:1771` (added `throw error`)

### 3. Fixed localStorage Quota Issues
- **Problem**: `QuotaExceededError` when saving wizard state with large image data
- **Solution**: Wrap localStorage in try-catch, clear old wizard states on quota error, fall back to Supabase
- **Files**: `public/wizard/wizard.js:124-152`

### 4. Fixed Phase Loading Indicators
- **Problem**: `generateAllMultiRefs()` was referencing `phase3Loading` but it's in Phase 4
- **Solution**: Changed to `phase4Loading` and `phase4LoadingText`

## Key Learnings

### Service Reliability
- **nano-banana-pro** can go down (error 3002: "Service temporary unavailable")
- Always provide model selection dropdown as fallback
- **gemini-flash** ($0.04) is a reliable alternative to nano-banana-pro ($0.15)

### Error Handling Patterns
```javascript
// In inner function - show alert AND re-throw
} catch (error) {
    alert(`Failed: ${error.message}`);
    throw error; // Critical for cascade control
}

// In outer function - catch stops cascade
try {
    await step1();  // If this throws, step2/step3 won't run
    await step2();
    await step3();
} catch (error) {
    // Cascade stopped
}
```

### localStorage Strategy
- Wizard state can get large (images, prompts, book data)
- localStorage has ~5MB limit per origin
- Strategy: Try localStorage → Clear old states → Fall back to Supabase
- Supabase is the source of truth for cross-device sync

## Commits
- `7069511` - Add model selector to multi-ref view
- `d9c5b35` - Fix cascade error handling and localStorage quota

---

# Guide: Automating Book Creation with Claude Code

## Prerequisites

1. Chrome browser with DevTools debugging enabled
2. chrome-devtools MCP server connected
3. FunBookies wizard at https://funbookies.com/wizard/

## The `/book-wizard` Skill

Located at `.claude/skills/book-wizard.md`, this skill automates the 6-phase wizard workflow.

### Invocation
```
/book-wizard B2 "A puppy finds a lost ball" "sunny backyard"
```

### Workflow Overview

```
Phase 1: Concept Input    → Fill form, generate outline
Phase 2: Outline Review   → Review beats, expand to story
Phase 3: Story Review     → Edit text/scenes, approve
Phase 4: Reference Image  → Generate style reference (MOST COMPLEX)
Phase 5: Page Images      → Generate all page illustrations
Phase 6: Publish          → Review and publish book
```

## Phase-by-Phase Automation

### Phase 1: Concept Input

```javascript
// Navigate and fill form
mcp__chrome-devtools__navigate_page({ url: "https://funbookies.com/wizard/" })
mcp__chrome-devtools__take_snapshot()

// Find elements by their IDs
mcp__chrome-devtools__fill({ uid: "<levelSelect uid>", value: "B2" })
mcp__chrome-devtools__fill({ uid: "<conceptInput uid>", value: "A puppy finds a lost ball" })
mcp__chrome-devtools__fill({ uid: "<settingInput uid>", value: "sunny backyard" })

// Click generate
mcp__chrome-devtools__click({ uid: "<Generate Outline button uid>" })

// Wait for loading to complete
mcp__chrome-devtools__wait_for({ text: "Story Beats" })
```

**Checkpoint 1**: Show outline to user, ask approval

### Phase 2: Outline Review

```javascript
// User can edit beats in UI if needed
// When ready:
mcp__chrome-devtools__click({ uid: "<Expand to Full Story button uid>" })
mcp__chrome-devtools__wait_for({ text: "Scene Descriptions" })
```

**Checkpoint 2**: Show story and scenes to user

### Phase 3: Story Review

```javascript
// User reviews/edits text and scenes
mcp__chrome-devtools__click({ uid: "<Continue to Reference button uid>" })
```

**Checkpoint 3**: Confirm moving to image generation

### Phase 4: Reference Image (CRITICAL)

This is the most complex phase. Two strategies:

#### Single Reference (Simpler)
```javascript
// Check/edit the generated prompt
mcp__chrome-devtools__take_snapshot()
// Look for #referencePrompt textarea content

// Select model (important if nano-banana-pro is down!)
mcp__chrome-devtools__fill({ uid: "<refModelSelect uid>", value: "gemini-flash" })

// Generate
mcp__chrome-devtools__click({ uid: "<genRefBtn uid>" })

// Poll for completion (30-60 seconds)
// Watch for image in #referenceImageContainer
```

#### Multi-Reference Cascade
```javascript
// Switch to multi-ref view
mcp__chrome-devtools__click({ uid: "<Multi-Ref strategy button uid>" })

// Select fallback model if needed
mcp__chrome-devtools__fill({ uid: "<multiRefModelSelect uid>", value: "gemini-flash" })

// Generate cascade
mcp__chrome-devtools__click({ uid: "<genAllRefsBtn uid>" })

// This generates: styleGuide → openingScenes → closingScenes
// If styleGuide fails, cascade stops (fixed in d9c5b35)
```

**Checkpoint 4**: Show reference image(s), get approval

### Phase 5: Page Images

```javascript
mcp__chrome-devtools__click({ uid: "<approveRefBtn uid>" })
// Now in Phase 5

mcp__chrome-devtools__click({ uid: "<genAllPagesBtn uid>" })
// Watch #pageProgress for updates
// Each page takes ~30 seconds
```

**Checkpoint 5**: Show all page images

### Phase 6: Publish

```javascript
mcp__chrome-devtools__click({ uid: "<phase5NextBtn uid>" })
// Show review summary
// User checks quality checklist
mcp__chrome-devtools__click({ uid: "<Complete & View Book button uid>" })
```

## Error Handling

### Service Unavailable (3002)
```
{"code":3002,"title":"External service request failed","detail":"Service temporary unavailable."}
```
**Solution**: Switch to gemini-flash model in dropdown

### localStorage Quota
```
QuotaExceededError: Setting the value of 'wizard_state_xxx' exceeded the quota
```
**Solution**: Handled automatically now - clears old states

### Cascade Failures
If any step in multi-ref cascade fails, subsequent steps are skipped.
Check card status elements (`#statusStyleGuide`, etc.) for "Error" state.

## Element Reference

| Phase | Element | ID/Selector |
|-------|---------|-------------|
| 1 | Level dropdown | `#levelSelect` |
| 1 | Concept input | `#conceptInput` |
| 1 | Setting input | `#settingInput` |
| 4 | Single-ref model | `#refModelSelect` |
| 4 | Multi-ref model | `#multiRefModelSelect` |
| 4 | Generate ref button | `#genRefBtn` |
| 4 | Generate all refs | `#genAllRefsBtn` |
| 4 | Approve ref | `#approveRefBtn` |
| 5 | Generate all pages | `#genAllPagesBtn` |
| 5 | Page progress | `#pageProgress` |

## Best Practices

1. **Always take snapshots** before interacting - UIDs change between page loads
2. **Use wait_for** after clicking generation buttons
3. **Check model availability** - have gemini-flash as fallback
4. **Pause at checkpoints** - let user review before expensive operations
5. **Handle timeouts** - image generation can take 60+ seconds
6. **Save to Supabase** - call saveToSupabase() after major state changes for cross-device sync

## Cost Estimates

| Operation | Model | Cost |
|-----------|-------|------|
| Single reference | nano-banana-pro | $0.15 |
| Single reference | gemini-flash | $0.04 |
| Multi-ref cascade | nano + wan2.6 | $0.21 |
| Page image | wan2.6-image | $0.03 |
| 16-page book | Total | ~$0.60-0.80 |
