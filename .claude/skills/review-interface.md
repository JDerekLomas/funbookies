# Review Interface Skill

Generate review interfaces for assets (audio, images, icons) with thumbs up/down rating, notes, and JSON tracking.

## When to Use

Use this skill when the user wants to:
- Review generated assets (audio files, images, icons)
- Rate assets as approved/rejected with notes
- Track review iterations over time
- Regenerate rejected assets

## Usage

```
/review-interface <asset-type> <directory>
```

Examples:
- `/review-interface audio /public/audio/phonemes`
- `/review-interface images /public/activities/word-icons`
- `/review-interface covers /public/images/covers`

## How It Works

### 1. Scan the Directory

Find all assets of the specified type:
- `audio`: `.mp3`, `.wav`, `.ogg`
- `images`: `.png`, `.jpg`, `.jpeg`, `.webp`, `.svg`

### 2. Generate Review HTML

Create or update a review HTML file at `<directory>/review.html` with:

- Grid of asset cards
- Click to preview (play audio / view image)
- Thumbs up/down buttons on each card
- Optional note field for rejected items
- Filter buttons: All, Unreviewed, Approved, Needs Work
- Review summary textarea with Copy button
- Stats: total, approved, rejected, unreviewed

### 3. Save Reviews to JSON

Create/update `<directory>/reviews.json`:

```json
{
  "lastUpdated": "2025-01-11T14:30:00Z",
  "version": 1,
  "assetType": "audio",
  "totalAssets": 57,
  "reviews": {
    "asset-id": {
      "status": "approved" | "rejected",
      "note": "optional feedback",
      "reviewedAt": "2025-01-11T14:30:00Z"
    }
  },
  "iterations": [
    {
      "date": "2025-01-11",
      "action": "Initial generation",
      "approved": 45,
      "rejected": 12
    }
  ]
}
```

### 4. Review HTML Template

The generated HTML should:

```html
<!DOCTYPE html>
<html>
<head>
  <title>Review: [Asset Type] - [Directory Name]</title>
  <!-- Include shared.css if available -->
</head>
<body>
  <h1>[Asset Type] Review</h1>
  <p>Click to preview, thumbs up/down to rate.</p>

  <!-- Filter buttons -->
  <div class="filters">
    <button data-filter="all">All</button>
    <button data-filter="unreviewed">Unreviewed</button>
    <button data-filter="approved">Approved</button>
    <button data-filter="rejected">Needs Work</button>
  </div>

  <!-- Stats -->
  <div class="stats">
    Total: X | Approved: X | Rejected: X | Unreviewed: X
  </div>

  <!-- Asset grid -->
  <div class="grid">
    <!-- For each asset -->
    <div class="card" data-id="asset-id">
      <!-- Preview area (audio player or image) -->
      <div class="preview">...</div>
      <div class="name">asset-id</div>
      <!-- Rating buttons -->
      <div class="rating">
        <button class="approve">👍</button>
        <button class="reject">👎</button>
      </div>
      <!-- Note input (shown when rejected) -->
      <input class="note" placeholder="What's wrong?">
    </div>
  </div>

  <!-- Summary section -->
  <div class="summary">
    <h3>Review Summary</h3>
    <textarea readonly id="summary"></textarea>
    <button onclick="copySummary()">Copy to Clipboard</button>
    <button onclick="saveToFile()">Save to JSON</button>
  </div>

  <script>
    // Load reviews from localStorage AND reviews.json
    // Save to localStorage on each change
    // Provide "Save to JSON" that outputs the JSON for Claude to save
  </script>
</body>
</html>
```

### 5. After Review

When the user shares their review summary, help them:

1. **Analyze feedback** - Understand what's wrong with rejected items
2. **Suggest fixes** - Propose how to regenerate (different prompts, settings, etc.)
3. **Regenerate** - Create a script or commands to regenerate rejected items
4. **Update JSON** - Increment version, add iteration record

## Key Features

### LocalStorage Persistence
Reviews are saved to localStorage so they persist across page refreshes.

### JSON Export
The "Save to JSON" button generates JSON that can be saved to the repo for tracking.

### Iteration Tracking
Each regeneration cycle is logged with date, action, and counts.

### Summary Format
The summary textarea formats reviews for easy copy/paste:

```
# [Asset Type] Review

## Approved (X)
asset1, asset2, asset3...

## Needs Work (X)
- asset4: [note or "needs improvement"]
- asset5: [note]
```

## Example Workflow

1. User: `/review-interface audio /public/audio/phonemes`
2. Claude: Creates review.html and reviews.json
3. User: Opens review.html, rates sounds, copies summary
4. User: Pastes summary to Claude
5. Claude: Analyzes issues, regenerates bad sounds
6. User: Re-reviews, repeat until all approved
7. Claude: Updates reviews.json with final iteration

## Notes

- Always check if review.html already exists and preserve existing reviews
- The HTML should work standalone (no build step)
- Use vanilla JS, no frameworks
- Style consistently with the project's shared.css if available
