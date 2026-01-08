#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

// Get project root directory (2 levels up from scripts/image_utils)
const PROJECT_ROOT = path.resolve(__dirname, '..', '..');
const UNUSED_IMAGES_FILE = path.join(PROJECT_ROOT, 'unused-images.json');
const DRY_RUN = !process.argv.includes('--confirm');

// Helper function to check if a file is a responsive version or thumbnail
function isResponsiveOrThumbnail(filename) {
  const responsivePatterns = ['_1x.', '_2x.', '_3x.', '_4x.', '_thumb.'];
  return responsivePatterns.some(pattern => filename.includes(pattern));
}

function main() {
  console.log('🗑️  IMAGE CLEANUP SCRIPT - RESPONSIVE VERSIONS & THUMBNAILS ONLY\n');

  // Check if unused images file exists
  if (!fs.existsSync(UNUSED_IMAGES_FILE)) {
    console.error('❌ Error: unused-images.json not found!');
    console.error('Please run: node find-unused-images.js first\n');
    process.exit(1);
  }

  // Load unused images
  const unusedData = JSON.parse(fs.readFileSync(UNUSED_IMAGES_FILE, 'utf8'));

  if (DRY_RUN) {
    console.log('🔍 DRY RUN MODE - No files will be deleted');
    console.log('   Run with --confirm flag to actually delete files\n');
  } else {
    console.log('⚠️  WARNING: THIS WILL PERMANENTLY DELETE FILES!');
    console.log('   Make sure you have a backup or use version control.\n');
  }

  console.log('='.repeat(80));
  console.log(`Total unused files found: ${unusedData.total_unused}`);
  console.log(`Note: Only deleting responsive versions (_1x, _2x, _3x, _4x, _thumb)`);
  console.log(`Original images will be preserved`);
  console.log('='.repeat(80));

  let deletedCount = 0;
  let failedCount = 0;
  let totalSize = 0;
  let totalResponsiveFiles = 0;
  let totalOriginalFiles = 0;

  // Process each folder
  Object.keys(unusedData.folders).forEach((folder) => {
    const files = unusedData.folders[folder];

    // Filter to only responsive versions and thumbnails
    const responsiveFiles = files.filter(isResponsiveOrThumbnail);
    const skippedOriginals = files.length - responsiveFiles.length;

    totalResponsiveFiles += responsiveFiles.length;
    totalOriginalFiles += skippedOriginals;

    console.log(`\n📁 Processing folder: ${folder}`);
    console.log(`   Total unused files: ${files.length}`);
    console.log(`   Responsive/thumbnails to delete: ${responsiveFiles.length}`);
    console.log(`   Original images to keep: ${skippedOriginals}`);

    responsiveFiles.forEach((file) => {
      const filePath = path.join(PROJECT_ROOT, 'public', 'books', folder, file);

      if (!fs.existsSync(filePath)) {
        console.log(`   ⚠️  File not found: ${file}`);
        failedCount++;
        return;
      }

      // Get file size
      const stat = fs.statSync(filePath);
      totalSize += stat.size;

      if (DRY_RUN) {
        // Just report what would be deleted
        const sizeKB = (stat.size / 1024).toFixed(2);
        if (deletedCount < 5) {
          console.log(`   [DRY RUN] Would delete: ${file} (${sizeKB} KB)`);
        }
      } else {
        // Actually delete the file
        try {
          fs.unlinkSync(filePath);
          deletedCount++;
          if (deletedCount <= 5) {
            const sizeKB = (stat.size / 1024).toFixed(2);
            console.log(`   ✓ Deleted: ${file} (${sizeKB} KB)`);
          }
        } catch (error) {
          console.error(`   ❌ Failed to delete ${file}: ${error.message}`);
          failedCount++;
        }
      }
    });

    if (DRY_RUN && responsiveFiles.length > 5) {
      console.log(`   ... and ${responsiveFiles.length - 5} more files`);
    } else if (!DRY_RUN && responsiveFiles.length > 5) {
      console.log(`   ... deleted ${responsiveFiles.length - 5} more files`);
    }
  });

  // Summary
  console.log('\n' + '='.repeat(80));
  console.log('📊 SUMMARY');
  console.log('='.repeat(80));

  if (DRY_RUN) {
    console.log(`Responsive versions & thumbnails that would be deleted: ${totalResponsiveFiles}`);
    console.log(`Original images preserved: ${totalOriginalFiles}`);
    console.log(
      `Space that would be freed: ${(totalSize / 1024 / 1024).toFixed(2)} MB`
    );
    console.log(`\n✨ This was a dry run. No files were deleted.`);
    console.log(`\n💡 To actually delete these files, run:`);
    console.log(`   node delete-unused-images.js --confirm`);
  } else {
    console.log(`Responsive versions & thumbnails deleted: ${deletedCount}`);
    console.log(`Original images preserved: ${totalOriginalFiles}`);
    console.log(`Failed deletions: ${failedCount}`);
    console.log(`Space freed: ${(totalSize / 1024 / 1024).toFixed(2)} MB`);
    console.log(`\n✅ Cleanup complete!`);

    // Update the unused images file to mark it as processed
    const processedData = {
      ...unusedData,
      processed_at: new Date().toISOString(),
      deleted_count: deletedCount,
      failed_count: failedCount,
    };

    const backupPath = path.join(PROJECT_ROOT, 'unused-images-deleted.json');
    fs.writeFileSync(backupPath, JSON.stringify(processedData, null, 2));
    console.log(`\n📝 Deletion record saved to: unused-images-deleted.json`);
  }

  console.log('');
}

main();
