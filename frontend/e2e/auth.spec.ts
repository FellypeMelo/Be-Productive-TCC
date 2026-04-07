import { test, expect } from '@playwright/test';

test.describe('Authentication', () => {
  test('login page has correct title and form', async ({ page }) => {
    await page.goto('/auth/login');
    await expect(page).toHaveTitle(/Be Productive/);
    await expect(page.getByLabel('Email Address')).toBeVisible();
    await expect(page.getByLabel('Password')).toBeVisible();
    await expect(page.getByRole('button', { name: /login/i })).toBeVisible();
  });

  test('register page has correct form', async ({ page }) => {
    await page.goto('/auth/register');
    await expect(page).toHaveTitle(/Be Productive/);
    await expect(page.getByLabel('Full Name')).toBeVisible();
    await expect(page.getByLabel('Email Address')).toBeVisible();
    await expect(page.getByLabel('Confirm Password')).toBeVisible();
  });
});
