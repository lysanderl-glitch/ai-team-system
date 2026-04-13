import { chromium } from 'playwright';

const htmlPath = 'C:/Users/lysanderl_janusd/Claude Code/ai-team-system/tools/video-pipeline/output/generated-animation.html';
const fileUrl = 'file:///' + htmlPath.replace(/\\/g, '/');

async function test() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1920, height: 1080 } });
  const page = await context.newPage();

  // Capture console errors
  page.on('console', msg => {
    if (msg.type() === 'error' || msg.type() === 'warning') {
      console.log(`[${msg.type()}]`, msg.text());
    }
  });
  page.on('pageerror', err => {
    console.log('[PAGE ERROR]', err.message);
  });

  console.log('Loading:', fileUrl);
  await page.goto(fileUrl, { waitUntil: 'networkidle', timeout: 30000 });

  console.log('Waiting for animation-complete (120s timeout)...');
  try {
    await page.waitForSelector('body[data-animation-complete="true"]', { timeout: 120000 });
    console.log('Animation completed successfully!');
  } catch (e) {
    console.log('Timeout! Checking page state...');
    const bodyAttrs = await page.evaluate(() => {
      return {
        animComplete: document.body.getAttribute('data-animation-complete'),
        bodyClasses: document.body.className,
        visibleCount: document.querySelectorAll('.visible').length,
        hookDisplay: document.getElementById('hook-overlay')?.style.display,
        hookOpacity: document.getElementById('hook-overlay')?.style.opacity,
        ctaDisplay: document.getElementById('cta-overlay')?.style.display,
        ctaClasses: document.getElementById('cta-overlay')?.className,
        screenshotDisplay: document.getElementById('screenshot-panel')?.style.display,
        terminalDisplay: document.getElementById('terminal-panel')?.style.display,
        progressBarVisible: document.getElementById('progress-bar')?.className,
        subtitleText: document.getElementById('subtitle-bar')?.textContent?.substring(0, 100),
      };
    });
    console.log('Page state:', JSON.stringify(bodyAttrs, null, 2));
  }

  await browser.close();
}

test().catch(err => {
  console.error('Test failed:', err);
  process.exit(1);
});
