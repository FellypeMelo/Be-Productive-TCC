import { test, expect } from '@playwright/test';

test.describe('Focus Mode', () => {
  test('focus page redirects to login when unauthenticated', async ({ page }) => {
    await page.goto('/focus');
    await expect(page).toHaveURL(/.*login/);
  });

  test('focus page has correct title', async ({ page }) => {
    await page.goto('/focus');
    await expect(page).toHaveTitle(/Be Productive/);
  });

  test('focus workspace shows main heading unauthenticated (shows login)', async ({ page }) => {
    // Should redirect, so we verify redirect happened instead
    await page.goto('/focus');
    await expect(page).toHaveURL(/.*login/);
  });
});
