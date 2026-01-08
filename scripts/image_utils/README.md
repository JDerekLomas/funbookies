# Image Utility Scripts

This directory contains utilities for managing book images and responsive versions.

## Scripts

### 1. `generate_used_images.js`
Generates a comprehensive list of all images that should exist based on the book registry.

**Usage:**
```bash
node scripts/image_utils/generate_used_images.js
```

**Outputs:**
- `used-images.json` - Detailed report with images per book
- `used-images-flat.json` - Flattened list for easy processing
- `used-images-list.txt` - Simple text list for scripting

---

### 2. `find_unused_images.js`
Finds images that exist in the filesystem but aren't referenced by any book.

**Prerequisites:** Run `generate_used_images.js` first

**Usage:**
```bash
node scripts/image_utils/find_unused_images.js
```

**Outputs:**
- `unused-images.json` - List of unused images by folder
- `unused-images-list.txt` - Simple text list

---

### 3. `analyze_images.js`
Analyzes each book's images for completeness - checks if all required responsive versions exist.

**Usage:**
```bash
node scripts/image_utils/analyze_images.js
```

**Output:** Console report showing:
- Missing images
- Incomplete responsive versions (missing 1x, 2x, 3x, 4x, or thumb)
- Summary statistics per book

---

### 4. `delete_unused_images.js`
Safely deletes unused responsive versions and thumbnails (preserves originals).

**Prerequisites:** Run `find_unused_images.js` first

**Usage:**
```bash
# Dry run (preview what would be deleted)
node scripts/image_utils/delete_unused_images.js

# Actually delete files
node scripts/image_utils/delete_unused_images.js --confirm
```

**Outputs:**
- `unused-images-deleted.json` - Record of deleted files

---

## Typical Workflow

1. **Generate list of expected images:**
   ```bash
   node scripts/image_utils/generate_used_images.js
   ```

2. **Find unused images:**
   ```bash
   node scripts/image_utils/find_unused_images.js
   ```

3. **Analyze image completeness:**
   ```bash
   node scripts/image_utils/analyze_images.js
   ```

4. **Clean up unused files (optional):**
   ```bash
   # Preview first
   node scripts/image_utils/delete_unused_images.js

   # Then delete
   node scripts/image_utils/delete_unused_images.js --confirm
   ```

## Path Configuration

All scripts automatically detect the project root directory (`../../` from this folder) and work correctly regardless of where they're run from.

## Output Files

All output files are saved to the project root directory:
- `used-images.json`
- `used-images-flat.json`
- `used-images-list.txt`
- `unused-images.json`
- `unused-images-list.txt`
- `unused-images-deleted.json`
