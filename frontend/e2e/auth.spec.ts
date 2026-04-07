import { test, expect } from '@playwright/test';

test.describe('Authentication', () => {
  test('redirects to login when accessing feed unauthenticated', async ({ page }) => {
    await page.goto('/feed');
    await expect(page).toHaveURL(/.*login/);
  });

  test('redirects to login when accessing focus unauthenticated', async ({ page }) => {
    await page.goto('/focus');
    await expect(page).toHaveURL(/.*login/);
  });

  test('login page has correct title and form', async ({ page }) => {
    await page.goto('/auth/login');
    await expect(page).toHaveTitle(/Be Productive/);
    await expect(page.getByLabel('Email')).toBeVisible();
    await expect(page.getByLabel('Senha')).toBeVisible();
    await expect(page.getByRole('button', { name: /login/i })).toBeVisible();
  });

  test('register page has correct form', async ({ page }) => {
    await page.goto('/auth/register');
    await expect(page).toHaveTitle(/Be Productive/);
    await expect(page.getByLabel('Nome')).toBeVisible();
    await expect(page.getByLabel('Email')).toBeVisible();
    await expect(page.getByLabel('Senha')).toBeVisible();
  });
});