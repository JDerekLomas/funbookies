#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

// Book registry - based on reader.html
const bookRegistry = {
  dog_pink: {
    jsonFile: 'dog_pink.json',
    imageFolder: 'images',
    imagePrefix: 'dog_pink_page',
  },
  pig_yellow: {
    jsonFile: 'pig_yellow.json',
    imageFolder: 'images',
    imagePrefix: 'pig_yellow_page',
  },
  volcano: {
    jsonFile: 'volcano.json',
    imageFolder: 'volcano_images',
    imagePrefix: 'page_',
  },
  castle: {
    jsonFile: 'castle.json',
    imageFolder: 'castle_images',
    imagePrefix: 'page_',
  },
  elephant_red: {
    jsonFile: 'elephant_red.json',
    imageFolder: 'images',
    imagePrefix: 'elephant_red_page',
  },
  fox_purple: {
    jsonFile: 'fox_purple.json',
    imageFolder: 'images',
    imagePrefix: 'fox_purple_page',
  },
  snail_blue: {
    jsonFile: 'snail_blue.json',
    imageFolder: 'images',
    imagePrefix: 'snail_blue_page',
  },
  owl_green: {
    jsonFile: 'owl_green.json',
    imageFolder: 'images',
    imagePrefix: 'owl_green_page',
  },
  mouse_gold: {
    jsonFile: 'mouse_gold.json',
    imageFolder: 'images',
    imagePrefix: 'mouse_gold_page',
  },
};

const BOOKS_DIR = path.join(__dirname, 'public', 'books');
const REQUIRED_VERSIONS = ['1x', '2x', '3x', '4x'];
const FORMATS = ['webp', 'png'];

// Helper to get all files in a directory
function getAllFiles(dir) {
  if (!fs.existsSync(dir)) {
    return [];
  }
  return fs.readdirSync(dir);
}

// Helper to format page number with leading zeros
function formatPageNumber(pageNum, width = 2) {
  return String(pageNum).padStart(width, '0');
}

// Analyze a single book
function analyzeBook(bookId, config) {
  console.log(`\n${'='.repeat(80)}`);
  console.log(`📚 Analyzing: ${bookId.toUpperCase()}`);
  console.log('='.repeat(80));

  const jsonPath = path.join(BOOKS_DIR, config.jsonFile);
  const imageDir = path.join(BOOKS_DIR, config.imageFolder);

  if (!fs.existsSync(jsonPath)) {
    console.log(`❌ JSON file not found: ${jsonPath}`);
    return;
  }

  // Read JSON
  const bookData = JSON.parse(fs.readFileSync(jsonPath, 'utf8'));
  const pages = bookData.pages || [];

  console.log(`\nJSON File: ${config.jsonFile}`);
  console.log(`Image Folder: ${config.imageFolder}`);
  console.log(`Total Pages in JSON: ${pages.length}`);

  // Get expected images based on pages
  const expectedImages = new Set();
  const pageNumbers = [];

  pages.forEach((page) => {
    if (page.page !== undefined) {
      pageNumbers.push(page.page);

      let baseName;

      // Check if the page has an explicit image path
      if (page.image) {
        // Extract base name from image path
        // Example: "volcano_images/page_01_cover.png" -> "page_01_cover"
        const imagePath = page.image;
        const parts = imagePath.split('/');
        const filename = parts[parts.length - 1];
        baseName = filename.replace(/\.png$/, '');
      } else {
        // Construct from page number (animal books style)
        const pageNum = formatPageNumber(page.page);
        baseName = `${config.imagePrefix}${pageNum}`;
      }

      expectedImages.add(baseName);
    }
  });

  console.log(`\nExpected base images: ${expectedImages.size}`);

  // Get actual files in the image directory
  const actualFiles = getAllFiles(imageDir);
  const actualImagesByBase = new Map();

  // Group actual files by base name
  actualFiles.forEach((file) => {
    // Extract base name (without version suffix and extension)
    // Example: dog_pink_page01_1x.webp -> dog_pink_page01
    //          page_01_cover_2x.png -> page_01_cover
    const match = file.match(
      /^(.+?)(?:_(?:1x|2x|3x|4x|thumb))?\.(?:png|webp)$/
    );
    if (match) {
      const baseName = match[1];
      if (!actualImagesByBase.has(baseName)) {
        actualImagesByBase.set(baseName, []);
      }
      actualImagesByBase.get(baseName).push(file);
    }
  });

  // Check which expected images exist and have all required versions
  console.log('\n' + '-'.repeat(80));
  console.log('📋 IMAGES REFERENCED IN JSON:');
  console.log('-'.repeat(80));

  const missingImages = [];
  const incompleteImages = [];

  expectedImages.forEach((baseName) => {
    const files = actualImagesByBase.get(baseName) || [];
    const hasOriginalPng = files.some((f) => f === `${baseName}.png`);

    console.log(`\n${baseName}:`);

    if (files.length === 0) {
      console.log(`  ❌ COMPLETELY MISSING - No files found`);
      missingImages.push(baseName);
      return;
    }

    if (!hasOriginalPng) {
      console.log(`  ⚠️  Missing original: ${baseName}.png`);
    } else {
      console.log(`  ✓ Original: ${baseName}.png`);
    }

    // Check for each required version in each format
    const missingVersions = [];
    REQUIRED_VERSIONS.forEach((version) => {
      FORMATS.forEach((format) => {
        const versionFile = `${baseName}_${version}.${format}`;
        if (files.includes(versionFile)) {
          console.log(`  ✓ ${versionFile}`);
        } else {
          console.log(`  ❌ Missing: ${versionFile}`);
          missingVersions.push(versionFile);
        }
      });
    });

    // Check for thumbnail
    const thumbFile = `${baseName}_thumb.webp`;
    if (files.includes(thumbFile)) {
      console.log(`  ✓ ${thumbFile}`);
    } else {
      console.log(`  ❌ Missing: ${thumbFile}`);
      missingVersions.push(thumbFile);
    }

    if (missingVersions.length > 0) {
      incompleteImages.push({ baseName, missing: missingVersions });
    }
  });

  // Find unused images
  console.log('\n' + '-'.repeat(80));
  console.log(
    '🗑️  UNUSED IMAGES (exist in folder but not referenced in JSON):'
  );
  console.log('-'.repeat(80));

  // const unusedBases = [];
  // actualImagesByBase.forEach((files, baseName) => {
  //     if (!expectedImages.has(baseName)) {
  //         unusedBases.push(baseName);
  //     }
  // });

  // if (unusedBases.length === 0) {
  //     console.log('\n✓ No unused images found');
  // } else {
  //     unusedBases.forEach(baseName => {
  //         const files = actualImagesByBase.get(baseName);
  //         console.log(`\n${baseName}:`);
  //         files.forEach(file => {
  //             console.log(`  - ${file}`);
  //         });
  //     });
  // }

  // Summary
  console.log('\n' + '='.repeat(80));
  console.log('📊 SUMMARY:');
  console.log('='.repeat(80));
  console.log(`Total pages in JSON: ${pages.length}`);
  console.log(`Expected unique base images: ${expectedImages.size}`);
  console.log(`Actual unique base images found: ${actualImagesByBase.size}`);
  console.log(`Completely missing images: ${missingImages.length}`);
  console.log(`Images with incomplete versions: ${incompleteImages.length}`);
  // console.log(`Unused image bases: ${unusedBases.length}`);

  if (missingImages.length > 0) {
    console.log('\n❌ Completely missing images:');
    missingImages.forEach((img) => console.log(`  - ${img}`));
  }

  if (incompleteImages.length > 0) {
    console.log('\n⚠️  Images with incomplete responsive versions:');
    incompleteImages.forEach(({ baseName, missing }) => {
      console.log(`  ${baseName}: missing ${missing.length} files`);
    });
  }

  return {
    bookId,
    totalPages: pages.length,
    expectedImages: expectedImages.size,
    actualImages: actualImagesByBase.size,
    missingImages: missingImages.length,
    incompleteImages: incompleteImages.length,
    unusedImages: unusedBases.length,
  };
}

// Main execution
function main() {
  console.log('\n📸 IMAGE USAGE ANALYSIS');
  console.log('='.repeat(80));
  console.log(
    'Checking all books for image usage and responsive versions...\n'
  );

  const results = [];

  Object.keys(bookRegistry).forEach((bookId) => {
    const config = bookRegistry[bookId];
    const result = analyzeBook(bookId, config);
    if (result) {
      results.push(result);
    }
  });

  // Overall summary
  console.log('\n\n' + '='.repeat(80));
  console.log('🎯 OVERALL SUMMARY FOR ALL BOOKS');
  console.log('='.repeat(80));
  console.log(
    '\nBook                | Pages | Expected | Actual | Missing | Incomplete | Unused'
  );
  console.log('-'.repeat(80));

  results.forEach((r) => {
    const bookName = r.bookId.padEnd(18);
    const pages = String(r.totalPages).padStart(5);
    const expected = String(r.expectedImages).padStart(8);
    const actual = String(r.actualImages).padStart(6);
    const missing = String(r.missingImages).padStart(7);
    const incomplete = String(r.incompleteImages).padStart(10);
    const unused = String(r.unusedImages).padStart(6);

    console.log(
      `${bookName} | ${pages} | ${expected} | ${actual} | ${missing} | ${incomplete} | ${unused}`
    );
  });

  console.log('\n✨ Analysis complete!\n');
  console.log('💡 Tip: To save this report to a file, run:');
  console.log('   node analyze-images.js > image-report.txt\n');
}

main();
