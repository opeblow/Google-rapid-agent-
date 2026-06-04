import { chromium } from 'playwright';
import { mkdirSync } from 'fs';
import { join } from 'path';

const PICTURES_DIR = 'C:\\Users\\USER\\Documents\\google rapid agent\\pictures';
const BASE_URL = 'http://localhost:5173';

mkdirSync(PICTURES_DIR, { recursive: true });

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({
  viewport: { width: 1280, height: 800 },
});

async function capture(page, url, filename) {
  console.log(`Capturing: ${url}`);
  await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });
  await page.waitForTimeout(2000);
  const filepath = join(PICTURES_DIR, filename);
  await page.screenshot({ path: filepath, fullPage: true });
  console.log(`  Saved: ${filename}`);
}

const page = await context.newPage();

await capture(page, BASE_URL, 'landing_page.png');
await capture(page, `${BASE_URL}/onboard`, 'onboarding_step1.png');
await capture(page, `${BASE_URL}/plans`, 'saved_plans.png');
await capture(page, `${BASE_URL}/dashboard/demo`, 'dashboard.png');

await browser.close();
console.log('\nAll screenshots captured!');
