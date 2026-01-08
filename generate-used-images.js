#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

// Book registry - based on reader.html
const bookRegistry = {
    'dog_pink': { jsonFile: 'dog_pink.json', imageFolder: 'images', imagePrefix: 'dog_pink_page' },
    'pig_yellow': { jsonFile: 'pig_yellow.json', imageFolder: 'images', imagePrefix: 'pig_yellow_page' },
    'volcano': { jsonFile: 'volcano.json', imageFolder: 'volcano_images', imagePrefix: 'page_' },
    'castle': { jsonFile: 'castle.json', imageFolder: 'castle_images', imagePrefix: 'page_' },
    'elephant_red': { jsonFile: 'elephant_red.json', imageFolder: 'images', imagePrefix: 'elephant_red_page' },
    'fox_purple': { jsonFile: 'fox_purple.json', imageFolder: 'images', imagePrefix: 'fox_purple_page' },
    'snail_blue': { jsonFile: 'snail_blue.json', imageFolder: 'images', imagePrefix: 'snail_blue_page' },
    'owl_green': { jsonFile: 'owl_green.json', imageFolder: 'images', imagePrefix: 'owl_green_page' },
    'mouse_gold': { jsonFile: 'mouse_gold.json', imageFolder: 'images', imagePrefix: 'mouse_gold_page' }
};

const BOOKS_DIR = path.join(__dirname, 'public', 'books');
const REQUIRED_VERSIONS = ['1x', '2x', '3x', '4x'];
const FORMATS = ['webp', 'png'];

// Helper to format page number with leading zeros
function formatPageNumber(pageNum, width = 2) {
    return String(pageNum).padStart(width, '0');
}

// Get all expected image paths for a book
function getBookImagePaths(bookId, config) {
    const jsonPath = path.join(BOOKS_DIR, config.jsonFile);

    if (!fs.existsSync(jsonPath)) {
        console.error(`Warning: JSON file not found: ${jsonPath}`);
        return [];
    }

    const bookData = JSON.parse(fs.readFileSync(jsonPath, 'utf8'));
    const pages = bookData.pages || [];
    const imagePaths = [];

    pages.forEach(page => {
        if (page.page !== undefined) {
            let baseName;

            // Check if the page has an explicit image path
            if (page.image) {
                // Extract base name from image path
                const imagePath = page.image;
                const parts = imagePath.split('/');
                const filename = parts[parts.length - 1];
                baseName = filename.replace(/\.png$/, '');
            } else {
                // Construct from page number (animal books style)
                const pageNum = formatPageNumber(page.page);
                baseName = `${config.imagePrefix}${pageNum}`;
            }

            // Generate all expected file paths
            const imageFolder = config.imageFolder;

            // Original PNG
            imagePaths.push(`${imageFolder}/${baseName}.png`);

            // Responsive versions
            REQUIRED_VERSIONS.forEach(version => {
                FORMATS.forEach(format => {
                    imagePaths.push(`${imageFolder}/${baseName}_${version}.${format}`);
                });
            });

            // Thumbnail
            imagePaths.push(`${imageFolder}/${baseName}_thumb.webp`);
        }
    });

    return imagePaths;
}

// Main execution
function main() {
    console.log('🔍 Generating list of used images...\n');

    const result = {
        generated_at: new Date().toISOString(),
        description: 'List of all image paths used by FunBookies books',
        books: {},
        all_paths: [],
        stats: {
            total_books: 0,
            total_images: 0,
            total_files: 0
        }
    };

    // Collect images per book
    Object.keys(bookRegistry).forEach(bookId => {
        const config = bookRegistry[bookId];
        console.log(`Processing: ${bookId}...`);

        const imagePaths = getBookImagePaths(bookId, config);

        result.books[bookId] = {
            json_file: config.jsonFile,
            image_folder: config.imageFolder,
            image_prefix: config.imagePrefix,
            image_count: imagePaths.length / 10, // Each image has 10 files
            total_files: imagePaths.length,
            paths: imagePaths
        };

        result.all_paths.push(...imagePaths);
        result.stats.total_images += imagePaths.length / 10;
        result.stats.total_files += imagePaths.length;
    });

    result.stats.total_books = Object.keys(bookRegistry).length;

    // Remove duplicates from all_paths
    result.all_paths = [...new Set(result.all_paths)].sort();

    // Create a flattened version for easier grep/search
    const flatResult = {
        generated_at: result.generated_at,
        description: result.description,
        stats: result.stats,
        used_image_paths: result.all_paths
    };

    // Save detailed version
    const outputPath = path.join(__dirname, 'used-images.json');
    fs.writeFileSync(outputPath, JSON.stringify(result, null, 2));
    console.log(`\n✅ Detailed report saved to: ${outputPath}`);

    // Save flat version
    const flatOutputPath = path.join(__dirname, 'used-images-flat.json');
    fs.writeFileSync(flatOutputPath, JSON.stringify(flatResult, null, 2));
    console.log(`✅ Flat list saved to: ${flatOutputPath}`);

    // Save simple text list for easy scripting
    const textOutputPath = path.join(__dirname, 'used-images-list.txt');
    fs.writeFileSync(textOutputPath, result.all_paths.join('\n'));
    console.log(`✅ Text list saved to: ${textOutputPath}`);

    // Print summary
    console.log('\n' + '='.repeat(60));
    console.log('📊 SUMMARY');
    console.log('='.repeat(60));
    console.log(`Total books: ${result.stats.total_books}`);
    console.log(`Total unique images: ${result.stats.total_images}`);
    console.log(`Total unique files (including responsive versions): ${result.all_paths.length}`);
    console.log(`Expected total files (if no duplicates): ${result.stats.total_files}`);

    console.log('\n💡 Usage examples:');
    console.log('  • View all used images: cat used-images-list.txt');
    console.log('  • Check if an image is used: grep "dog_pink_page01" used-images-list.txt');
    console.log('  • Find unused images in a folder:');
    console.log('    comm -23 <(ls public/books/images | sort) <(cat used-images-list.txt | xargs -n1 basename | sort)');
    console.log('');
}

main();
