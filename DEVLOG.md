# FunBookies Development Log

Development session notes and changes.

---

## 2025-01-18: Book Editor Improvements

**Commit:** `6f79f9a`

### Changes

**Text Editor Panel**
- Added "Page Text" section above image prompt editor in edit mode
- Users can now edit and save story text directly
- Only shows on story pages (hidden on covers, copyright, etc.)

**Save Button Visibility**
- Save Prompt button is now always visible (terracotta color)
- Previously only appeared on hover
- Status messages appear directly under each save button

**Image Version History**
- When clicking "Use as Current Image", the old image is archived to version history
- Past versions show in "Page Image Versions" section
- Hover over thumbnails to see metadata (prompt, model, timestamp)
- Click any version to restore it as current
- Info icon indicates versions with metadata

### Files Changed
- `public/reader.html` - Editor UI and version tracking logic

### Notes
- Version history only tracks images that were actually used as "current", not every generation attempt
- Existing pages won't have version history until the next time an image is replaced
