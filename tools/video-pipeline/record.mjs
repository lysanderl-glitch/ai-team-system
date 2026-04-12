/**
 * SPE Video Tutorial - Playwright HTML Animation Recorder
 *
 * Records the SPE video animation HTML page to WebM video using Playwright.
 *
 * Usage:
 *   node record.mjs [path-to-html]
 *
 * Defaults to: obs/03-process-knowledge/spe-video-animation.html
 */

import { chromium } from 'playwright';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Resolve the project root (two levels up from tools/video-pipeline/)
const PROJECT_ROOT = path.resolve(__dirname, '..', '..');

// Default HTML animation file
const DEFAULT_HTML = path.join(
  PROJECT_ROOT,
  'obs',
  '03-process-knowledge',
  'spe-video-animation.html'
);

// Output directory
const OUTPUT_DIR = path.join(__dirname, 'output');

async function record(htmlPath) {
  const resolvedPath = path.resolve(htmlPath || DEFAULT_HTML);

  if (!fs.existsSync(resolvedPath)) {
    console.error(`ERROR: HTML file not found: ${resolvedPath}`);
    console.error('Please provide a valid path or ensure the default animation file exists.');
    process.exit(1);
  }

  // Ensure output directory exists
  if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  }

  // Convert to file:// URL (works on both Windows and Linux)
  const fileUrl = `file:///${resolvedPath.replace(/\\/g, '/')}`;

  console.log('=== SPE Video Recorder ===');
  console.log(`HTML source: ${resolvedPath}`);
  console.log(`Output dir:  ${OUTPUT_DIR}`);
  console.log(`URL:         ${fileUrl}`);
  console.log('');

  console.log('[1/5] Launching browser...');
  const browser = await chromium.launch({
    headless: true,
  });

  console.log('[2/5] Creating context with video recording...');
  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    recordVideo: {
      dir: OUTPUT_DIR,
      size: { width: 1920, height: 1080 },
    },
    // Disable animations that might interfere with controlled playback
    reducedMotion: null,
    colorScheme: 'dark',
  });

  const page = await context.newPage();

  console.log('[3/5] Loading HTML animation...');
  await page.goto(fileUrl, {
    waitUntil: 'networkidle',
    timeout: 60000,
  });

  console.log('[4/5] Waiting for animation to complete...');
  console.log('       (timeout: 5 minutes, watching for data-animation-complete="true" on body)');

  try {
    await page.waitForSelector('body[data-animation-complete="true"]', {
      timeout: 300000, // 5 minutes - animation is ~4 minutes
      state: 'attached',
    });
    console.log('       Animation completed!');
  } catch (err) {
    console.warn('       WARNING: Timed out waiting for animation completion signal.');
    console.warn('       The video will contain whatever was recorded up to this point.');
    console.warn('       Ensure the HTML sets data-animation-complete="true" on <body> when done.');
  }

  // Small delay to ensure the last frame is captured
  await page.waitForTimeout(2000);

  console.log('[5/5] Closing browser and saving video...');
  const videoPath = await page.video().path();
  await context.close();
  await browser.close();

  // Rename the video file to a predictable name
  const finalPath = path.join(OUTPUT_DIR, 'recording.webm');
  if (fs.existsSync(finalPath)) {
    fs.unlinkSync(finalPath);
  }
  fs.renameSync(videoPath, finalPath);

  console.log('');
  console.log(`Recording saved: ${finalPath}`);
  console.log('=== Recording Complete ===');

  return finalPath;
}

// Run
const htmlArg = process.argv[2];
record(htmlArg).catch((err) => {
  console.error('Recording failed:', err);
  process.exit(1);
});
