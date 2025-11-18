/**
 * Convert PNG/JPG images to WebP format
 * Run: node scripts/convert-images-to-webp.js
 */

import sharp from 'sharp';
import { readdirSync, statSync } from 'fs';
import { join, dirname, extname, basename } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const PUBLIC_DIR = join(__dirname, '..', 'public');
const IMAGE_EXTENSIONS = ['.png', '.jpg', '.jpeg'];

/**
 * Get all image files in a directory
 */
function getImageFiles(dir) {
  const files = [];
  try {
    const entries = readdirSync(dir);
    
    for (const entry of entries) {
      const fullPath = join(dir, entry);
      const stat = statSync(fullPath);
      
      if (stat.isFile()) {
        const ext = extname(entry).toLowerCase();
        if (IMAGE_EXTENSIONS.includes(ext)) {
          files.push(fullPath);
        }
      }
    }
  } catch (error) {
    console.error(`Error reading directory ${dir}:`, error.message);
  }
  
  return files;
}

/**
 * Convert an image to WebP
 */
async function convertToWebP(inputPath) {
  try {
    const ext = extname(inputPath);
    const baseName = basename(inputPath, ext);
    const dir = dirname(inputPath);
    const outputPath = join(dir, `${baseName}.webp`);
    
    await sharp(inputPath)
      .webp({ quality: 85, effort: 6 })
      .toFile(outputPath);
    
    const inputStats = statSync(inputPath);
    const outputStats = statSync(outputPath);
    const savings = ((1 - outputStats.size / inputStats.size) * 100).toFixed(1);
    
    console.log(`✓ Converted: ${basename(inputPath)} → ${baseName}.webp (${savings}% smaller)`);
    
    return { success: true, savings };
  } catch (error) {
    console.error(`✗ Failed to convert ${basename(inputPath)}:`, error.message);
    return { success: false, error: error.message };
  }
}

/**
 * Main function
 */
async function main() {
  console.log('Converting images to WebP format...\n');
  
  const imageFiles = getImageFiles(PUBLIC_DIR);
  
  if (imageFiles.length === 0) {
    console.log('No images found to convert.');
    return;
  }
  
  console.log(`Found ${imageFiles.length} image(s) to convert:\n`);
  
  let successCount = 0;
  let failCount = 0;
  let totalSavings = 0;
  
  for (const imagePath of imageFiles) {
    const result = await convertToWebP(imagePath);
    if (result.success) {
      successCount++;
      totalSavings += parseFloat(result.savings);
    } else {
      failCount++;
    }
  }
  
  console.log(`\n${'='.repeat(50)}`);
  console.log(`Conversion complete!`);
  console.log(`✓ Success: ${successCount}`);
  if (failCount > 0) {
    console.log(`✗ Failed: ${failCount}`);
  }
  if (successCount > 0) {
    console.log(`Average size reduction: ${(totalSavings / successCount).toFixed(1)}%`);
  }
}

main().catch(console.error);

