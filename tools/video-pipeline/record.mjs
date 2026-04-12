/**
 * Video Tutorial Pipeline - Playwright HTML Animation Recorder
 *
 * Records an HTML animation page to WebM video using Playwright.
 *
 * Usage:
 *   node record.mjs --html path/to/animation.html --output output/recording.webm
 *   node record.mjs --html page.html --width 1920 --height 1080
 *   node record.mjs path/to/animation.html   (legacy positional arg)
 *
 * Defaults:
 *   --html    obs/03-process-knowledge/spe-video-animation.html
 *   --output  output/recording.webm
 *   --width   1920
 *   --height  1080
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

// ---------------------------------------------------------------------------
// Argument parsing
// ---------------------------------------------------------------------------

function parseArgs(argv) {
  const args = {
    html: null,
    output: null,
    width: 1920,
    height: 1080,
  };

  let i = 0;
  while (i < argv.length) {
    const arg = argv[i];
    if (arg === '--html' && i + 1 < argv.length) {
      args.html = argv[++i];
    } else if (arg === '--output' && i + 1 < argv.length) {
      args.output = argv[++i];
    } else if (arg === '--width' && i + 1 < argv.length) {
      args.width = parseInt(argv[++i], 10);
    } else if (arg === '--height' && i + 1 < argv.length) {
      args.height = parseInt(argv[++i], 10);
    } else if (!arg.startsWith('--') && !args.html) {
      // Legacy positional argument
      args.html = arg;
    }
    i++;
  }

  return args;
}

// ---------------------------------------------------------------------------
// Recorder
// ---------------------------------------------------------------------------

async function record(options) {
  const htmlPath = path.resolve(options.html || DEFAULT_HTML);
  const outputDir = options.output
    ? path.dirname(path.resolve(options.output))
    : path.join(__dirname, 'output');
  const outputName = options.output
    ? path.basename(options.output)
    : 'recording.webm';
  const finalPath = path.join(outputDir, outputName);
  const width = options.width || 1920;
  const height = options.height || 1080;

  if (!fs.existsSync(htmlPath)) {
    console.error(`ERROR: HTML file not found: ${htmlPath}`);
    console.error('Please provide a valid path with --html or as a positional argument.');
    process.exit(1);
  }

  // Ensure output directory exists
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  // Convert to file:// URL (works on both Windows and Linux)
  const fileUrl = `file:///${htmlPath.replace(/\\/g, '/')}`;

  console.log('=== Video Recorder ===');
  console.log(`HTML source: ${htmlPath}`);
  console.log(`Output:      ${finalPath}`);
  console.log(`Resolution:  ${width}x${height}`);
  console.log(`URL:         ${fileUrl}`);
  console.log('');

  console.log('[1/5] Launching browser...');
  const browser = await chromium.launch({
    headless: true,
  });

  console.log('[2/5] Creating context with video recording...');
  const context = await browser.newContext({
    viewport: { width, height },
    recordVideo: {
      dir: outputDir,
      size: { width, height },
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
      timeout: 300000, // 5 minutes
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

  // Rename the video file to the desired output name
  if (fs.existsSync(finalPath) && finalPath !== videoPath) {
    fs.unlinkSync(finalPath);
  }
  if (videoPath !== finalPath) {
    fs.renameSync(videoPath, finalPath);
  }

  console.log('');
  console.log(`Recording saved: ${finalPath}`);
  console.log('=== Recording Complete ===');

  return finalPath;
}

// Run
const args = parseArgs(process.argv.slice(2));
record(args).catch((err) => {
  console.error('Recording failed:', err);
  process.exit(1);
});
