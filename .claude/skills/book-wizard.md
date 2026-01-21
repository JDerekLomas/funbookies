# Book Wizard Skill

CLI-driven workflow that automates the FunBookies wizard UI, pausing at each phase for user review and approval.

## When to Use

Use `/book-wizard` when creating a new book through the wizard interface. This skill:
- Opens the wizard in Chrome
- Fills in form fields automatically
- Triggers generation steps
- Pauses at each checkpoint for user review
- Shows snapshots/screenshots of progress

## Usage

```
/book-wizard <level> "<concept>" "<setting>"
```

Examples:
- `/book-wizard B1 "A cat naps in the sun" "cozy house"`
- `/book-wizard B2 "A puppy finds a lost ball" "sunny backyard"`
- `/book-wizard B4 "A frog helps a crab" "mossy pond"`

## Prerequisites

1. Chrome browser must be open with DevTools debugging enabled
2. The chrome-devtools MCP server must be connected
3. User should be ready to review and approve each phase

## Workflow Steps

### Phase 1: Concept Input

1. Navigate to wizard:
```
mcp__chrome-devtools__navigate_page url="https://funbookies.com/wizard/"
```

2. Wait for page load, then take snapshot:
```
mcp__chrome-devtools__take_snapshot
```

3. Fill the form fields:
```
mcp__chrome-devtools__fill uid="<levelSelect uid>" value="<level>"
mcp__chrome-devtools__fill uid="<conceptInput uid>" value="<concept>"
mcp__chrome-devtools__fill uid="<settingInput uid>" value="<setting>"
```

4. Click "Generate Outline" button (look for button with text "Generate Outline")

5. Wait for loading to complete (loading spinner disappears, phase2 becomes visible)

6. **CHECKPOINT 1**: Take snapshot and ask user:
   - Show the generated outline
   - Ask: "Review the outline above. The title, character, setting, and story beats are shown. Would you like to proceed to expand this into a full story?"

### Phase 2: Outline Review

1. User can edit beats directly in the wizard UI if needed

2. When user approves, click "Expand to Full Story" button

3. Wait for loading (may take 10-20 seconds)

4. **CHECKPOINT 2**: Take snapshot showing the split view with story text and scene descriptions
   - Ask: "Review the story text and scene descriptions. Would you like to continue to reference image generation?"

### Phase 3: Story Review

1. User can edit text and scenes in the split view

2. When user approves, click "Continue to Reference" button

3. **CHECKPOINT 3**: Take snapshot of reference phase
   - Show the reference prompt that will be used
   - Ask: "Ready to generate the reference image? This will cost ~$0.15."

### Phase 4: Reference Image

The reference phase uses a **metaprompt system**:
- **Metaprompt Template**: Editable template with placeholders (`{title}`, `{name}`, `{description}`, etc.)
- **Extracted Story Data**: Character details auto-extracted from scene descriptions
- **Generated Prompt**: Final prompt = template filled with story data

1. Take snapshot and review the generated prompt
   - Expand "Metaprompt Template" to see/edit the template
   - Expand "Extracted Story Data" to verify character details
   - Check "Generated Prompt" for the final prompt

2. Click "Generate Reference" button (uid for #genRefBtn)

3. Wait for image generation (poll/watch for image to appear in #referenceImageContainer, typically 30-60 seconds)

4. **CHECKPOINT 4**: Take screenshot showing the reference image
   - Ask: "Review the reference image above. Does it capture the character and style correctly? Approve to continue."

5. When user approves, click "Approve & Continue" button (#approveRefBtn)

### Phase 5: Page Images

1. Take snapshot showing the page images grid

2. **CHECKPOINT 5**: Ask user:
   - "Ready to generate all page images? This will generate images for each story page (~$0.03 each)."

3. Click "Generate All Pages" button (#genAllPagesBtn)

4. Monitor progress (watch #pageProgress for updates)

5. **CHECKPOINT 6**: Take screenshot showing completed page images
   - Ask: "Review the generated page images. Continue to final review?"

6. Click "Continue to Review" button (#phase5NextBtn)

### Phase 6: Publish

1. Take snapshot showing review summary

2. **CHECKPOINT 7**: Show the quality checklist and ask:
   - "Review the book summary above. Ready to publish?"

3. Optionally open the reader preview:
```
# Get the readerLink href and navigate to it in a new tab
mcp__chrome-devtools__click uid="<readerLink uid>"
```

4. When user confirms, click "Complete & View Book" button

## Element Reference

### Phase 1 (Concept)
| Element | Type | Purpose |
|---------|------|---------|
| `#levelSelect` | select | Reading level dropdown |
| `#conceptInput` | textarea | Story concept |
| `#settingInput` | input | Story setting |
| `#wordInput` | input | Optional words to include |
| Button: "Generate Outline" | button | Start outline generation |

### Phase 2 (Outline)
| Element | Type | Purpose |
|---------|------|---------|
| `#outlineTitle` | input | Editable title |
| `#beatsList` | div | Container for story beats |
| Button: "Expand to Full Story" | button | Expand outline to full story |

### Phase 3 (Story)
| Element | Type | Purpose |
|---------|------|---------|
| `#editableTitle` | input | Title input |
| `#editablePages` | div | Editable story pages |
| `#sceneList` | div | Scene descriptions |
| Button: "Continue to Reference" | button | Proceed to reference phase |

### Phase 4 (Reference)
| Element | Type | Purpose |
|---------|------|---------|
| `#metapromptTemplate` | textarea | Metaprompt template (collapsible) |
| `#storyDataPreview` | pre | Extracted story data JSON |
| `#referencePrompt` | textarea | Generated prompt (editable) |
| `#genRefBtn` | button | Generate reference image |
| `#referenceImageContainer` | div | Reference image display |
| `#approveRefBtn` | button | Approve reference image |
| Button: "Apply Template" | button | Regenerate prompt from metaprompt |
| Button: "Reset to Default" | button | Reset metaprompt to default |

### Phase 5 (Pages)
| Element | Type | Purpose |
|---------|------|---------|
| `#pageImagesGrid` | div | Grid of page image cards |
| `#genAllPagesBtn` | button | Generate all page images |
| `#pageProgress` | span | Progress indicator |
| `#phase5NextBtn` | button | Continue to review |

### Phase 6 (Publish)
| Element | Type | Purpose |
|---------|------|---------|
| `#reviewSummary` | div | Book summary display |
| `#readerLink` | a | Preview link |
| `#editLink` | a | Edit mode link |
| Button: "Complete & View Book" | button | Finish and view book |

## Error Handling

### Loading States
- Phase 1 loading: `#phase1Loading` visible, `#phase1Form` hidden
- Phase 2 loading: `#phase2Loading` visible
- Phase 3 loading: `#phase3Loading` visible
- Phase 4 loading: `#phase4Loading` visible

### Detecting Completion
- Use `mcp__chrome-devtools__wait_for` to wait for specific text
- Take snapshots to verify state changes
- Check for loading spinners (`.spinner` class)

### Common Issues
1. **Page not loading**: Verify Chrome is connected and wizard URL is correct
2. **Button not clickable**: Wait for loading state to complete
3. **Image generation timeout**: Some images take 60+ seconds, use longer timeout
4. **Form validation errors**: Check for validation messages in `#validationMessages`

## Example Session

```
User: /book-wizard B1 "A cat naps in the sun" "cozy house"

Claude: I'll create a B1 level book about a cat napping. Let me open the wizard.

[Navigates to wizard]
[Fills in level=B1, concept, setting]
[Clicks Generate Outline]
[Waits for outline]

Here's the generated outline:

Title: "Cat Nap"
Character: Sunny the orange tabby cat
Setting: A cozy house with warm sunbeams

Beats:
1. INTRODUCE: Sunny the cat wakes up in her cozy bed
2. WANT: Sunny wants to find the perfect sunny spot
3. OBSTACLE: All the good spots are taken
...

Review the outline above. Would you like to proceed to expand this into a full story?

User: Yes, looks good!

Claude: [Clicks Expand to Full Story]
[Waits for expansion]

Here's the full story:

Page 1: "Sunny sat on the mat."
Scene: Orange tabby cat sitting on a woven mat in a sunlit room...

...

Review the story and scenes. Ready to generate the reference image?
```

## Tips

1. **Take snapshots frequently** - They show the user what's happening in the wizard
2. **Use wait_for judiciously** - Wait for specific text that indicates completion
3. **Respect user checkpoints** - Always pause and ask before expensive operations
4. **Handle timeouts gracefully** - Image generation can be slow, inform the user
