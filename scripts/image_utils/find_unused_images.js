#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

// Get project root directory (2 levels up from scripts/image_utils)
const PROJECT_ROOT = path.resolve(__dirname, '..', '..');
const BOOKS_DIR = path.join(PROJECT_ROOT, 'public', 'books');
const USED_IMAGES_FILE = path.join(PROJECT_ROOT, 'used-images-flat.json');

// Image folders to check
const IMAGE_FOLDERS = [
    'images',
    'volcano_images',
    'castle_images',
    'images_v2',
    'pip_well_images',
    'fern_gust_images',
    'sol_stone_images',
    'pig_mud_images'
];

function getAllFilesInFolder(folderPath) {
    if (!fs.existsSync(folderPath)) {
        return [];
    }

    const files = [];
    const items = fs.readdirSync(folderPath);

    items.forEach(item => {
        const fullPath = path.join(folderPath, item);
        const stat = fs.statSync(fullPath);

        if (stat.isFile()) {
            files.push(item);
        }
    });

    return files;
}

function main() {
    // Check if used images file exists
    if (!fs.existsSync(USED_IMAGES_FILE)) {
        console.error('❌ Error: used-images-flat.json not found!');
        console.error('Please run: node generate-used-images.js first\n');
        process.exit(1);
    }

    // Load used images
    const usedImagesData = JSON.parse(fs.readFileSync(USED_IMAGES_FILE, 'utf8'));
    const usedPaths = new Set(usedImagesData.used_image_paths);

    // Create a set of just filenames (without folder path) for easier matching
    const usedFilenames = new Set();
    usedImagesData.used_image_paths.forEach(p => {
        const filename = path.basename(p);
        usedFilenames.add(filename);
    });

    console.log('🔍 FINDING UNUSED IMAGES\n');
    console.log('=' .repeat(80));

    let totalFiles = 0;
    let totalUsed = 0;
    let totalUnused = 0;
    const unusedByFolder = {};

    // Check each folder
    IMAGE_FOLDERS.forEach(folder => {
        const folderPath = path.join(BOOKS_DIR, folder);

        if (!fs.existsSync(folderPath)) {
            console.log(`⚠️  Folder not found: ${folder}`);
            return;
        }

        console.log(`\n📁 Checking folder: ${folder}`);
        console.log('-'.repeat(80));

        const files = getAllFilesInFolder(folderPath);
        const unusedFiles = [];

        files.forEach(file => {
            // Skip hidden files and .DS_Store
            if (file.startsWith('.') || file === '.DS_Store' || file === '.gitignore') {
                return;
            }

            const relativePath = `${folder}/${file}`;

            // Check if this file is in the used list
            if (!usedPaths.has(relativePath)) {
                unusedFiles.push(file);
            }
        });

        const usedCount = files.length - unusedFiles.length;
        totalFiles += files.length;
        totalUsed += usedCount;
        totalUnused += unusedFiles.length;

        console.log(`Total files: ${files.length}`);
        console.log(`Used: ${usedCount}`);
        console.log(`Unused: ${unusedFiles.length}`);

        if (unusedFiles.length > 0) {
            unusedByFolder[folder] = unusedFiles;
            console.log(`\nUnused files in ${folder}:`);
            unusedFiles.slice(0, 10).forEach(file => {
                console.log(`  - ${file}`);
            });
            if (unusedFiles.length > 10) {
                console.log(`  ... and ${unusedFiles.length - 10} more`);
            }
        }
    });

    // Summary
    console.log('\n' + '='.repeat(80));
    console.log('📊 SUMMARY');
    console.log('='.repeat(80));
    console.log(`Total files scanned: ${totalFiles}`);
    console.log(`Used files: ${totalUsed}`);
    console.log(`Unused files: ${totalUnused}`);

    if (totalUnused > 0) {
        const unusedSize = calculateUnusedSize(unusedByFolder);
        console.log(`\n💾 Potential space savings: ~${(unusedSize / 1024 / 1024).toFixed(2)} MB`);
    }

    // Save unused files list
    if (totalUnused > 0) {
        const unusedList = {
            generated_at: new Date().toISOString(),
            total_unused: totalUnused,
            folders: unusedByFolder
        };

        const outputPath = path.join(PROJECT_ROOT, 'unused-images.json');
        fs.writeFileSync(outputPath, JSON.stringify(unusedList, null, 2));
        console.log(`\n✅ Unused images list saved to: ${outputPath}`);

        // Also save a simple text list for scripting
        const unusedPaths = [];
        Object.keys(unusedByFolder).forEach(folder => {
            unusedByFolder[folder].forEach(file => {
                unusedPaths.push(`public/books/${folder}/${file}`);
            });
        });

        const textOutputPath = path.join(PROJECT_ROOT, 'unused-images-list.txt');
        fs.writeFileSync(textOutputPath, unusedPaths.join('\n'));
        console.log(`✅ Text list saved to: ${textOutputPath}`);

        console.log('\n⚠️  CAUTION: Review the unused-images.json file before deleting!');
        console.log('Some images might be used elsewhere or needed for future books.\n');
        console.log('💡 To delete unused images (CAREFUL!):');
        console.log('   node delete-unused-images.js --confirm\n');
    } else {
        console.log('\n✨ No unused images found! Everything is being used.\n');
    }
}

function calculateUnusedSize(unusedByFolder) {
    let totalSize = 0;

    Object.keys(unusedByFolder).forEach(folder => {
        const folderPath = path.join(BOOKS_DIR, folder);
        unusedByFolder[folder].forEach(file => {
            const filePath = path.join(folderPath, file);
            if (fs.existsSync(filePath)) {
                const stat = fs.statSync(filePath);
                totalSize += stat.size;
            }
        });
    });

    return totalSize;
}

main();
