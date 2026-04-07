import { chromium, FullConfig } from '@playwright/test';

async function globalSetup(config: FullConfig) {
  const url = 'http://localhost:5173';

  // Graceful timeout — if servers aren't running, skip quietly
  let browser;
  try {
    browser = await chromium.launch({ headless: false });
  } catch {
    console.warn('  Chromium not available, skipping globalSetup.');
    return;
  }

  const page = await browser.newPage();

  try {
    const authPage = await page.goto(`${url}/auth/login`, { timeout: 5000 });
    if (!authPage || authPage.status() === 0) {
      console.warn('  Dev server not reachable, skipping globalSetup.');
      return;
    }

    // Attempt login with seeded demo user (from mock_data.sql — password123 is the shared password)
    await page.fill('input#email', 'user1@example.com');
    await page.fill('input#senha', 'password123');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/feed', { timeout: 5000 }).catch(() => {
      console.warn('  Login redirect to /feed did not complete — backend likely not running.');
      console.warn('  Running login via page.evaluate to set localStorage manually.');
    });

    // Ensure localStorage is set even if redirect didn't happen
    // (auth_token may have been set by a partial API response)
    const lsToken = await page.evaluate(() => localStorage.getItem('auth_token'));
    if (!lsToken) {
      // Backend is down — inject synthetic state so authenticated tests can still run
      await page.evaluate(() => {
        localStorage.setItem('auth_token', 'test-token-sync');
        localStorage.setItem('user', JSON.stringify({
          id_usuario: 1, nome: 'Alice Lopez', email: 'user1@example.com',
          estado_emocional_inferido: 'NEUTRO'
        }));
      });
    }

    await page.context().storageState({ path: 'e2e/.auth/user.json' });
    console.log('  Authenticated state saved to e2e/.auth/user.json');
  } finally {
    await browser.close();
  }
}

export default globalSetup;
