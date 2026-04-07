import { test, expect } from '@playwright/test';

test.describe('Feed', () => {
  test.beforeEach(async ({ page }) => {
    // Seed auth state: login, then save storage
    await page.goto('/auth/login');
  });

  test('feed page shows main elements unauthenticated', async ({ page }) => {
    // Should redirect to login when not authenticated
    await page.goto('/feed');
    await expect(page).toHaveURL(/.*login/);
  });

  test('feed page has correct title tag', async ({ page }) => {
    // Navigate to feed, which redirects to login
    await page.goto('/feed');
    await expect(page).toHaveTitle(/Be Productive/);
  });
});

test.describe('Feed (authenticated)', () => {
  test('feed grid skeleton appears during loading', async ({ page }) => {
    // Intercept feed API to simulate loading state
    await page.route('**/api/v1/feed*', async (route) => {
      // Delay response to show loading state
      await new Promise((r) => setTimeout(r, 2000));
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          data: {
            content_ids: [],
            scores: {},
            items: [],
            friction_level: 'none',
          },
        }),
      });
    });

    await page.goto('/feed');
    // Check for loading skeleton (animate-pulse class)
    await expect(page.locator('.animate-pulse')).toBeVisible();
  });

  test('category filter buttons exist', async ({ page }) => {
    await page.route('**/api/v1/feed*', async (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          data: {
            content_ids: [1],
            scores: {},
            items: [{
              id_conteudo: 1, titulo: 'Test', categoria: 'PRODUTIVIDADE',
              tipo_de_midia: 'VIDEO', autor_id: 1, data_publicacao: '2026-01-01',
              score_de_qualidade: 0.9, corpo: '', tags_relevantes: '',
            }],
            friction_level: 'none',
          },
        }),
      });
    });

    await page.goto('/feed');
    await expect(page.getByText('All')).toBeVisible();
    await expect(page.getByText('Productivity')).toBeVisible();
    await expect(page.getByText('Entertainment')).toBeVisible();
  });

  test('topic browser is visible', async ({ page }) => {
    await page.route('**/api/v1/feed*', async (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          data: {
            content_ids: [1],
            scores: {},
            items: [{
              id_conteudo: 1, titulo: 'Test', categoria: 'PRODUTIVIDADE',
              tipo_de_midia: 'VIDEO', autor_id: 1, data_publicacao: '2026-01-01',
              score_de_qualidade: 0.9, corpo: '', tags_relevantes: '',
            }],
            friction_level: 'none',
          },
        }),
      });
    });

    await page.goto('/feed');
    await expect(page.getByText('Browse your interests')).toBeVisible();
    await expect(page.getByText('All For You')).toBeVisible();
  });

  test('empty feed shows placeholder', async ({ page }) => {
    await page.route('**/api/v1/feed*', async (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          data: {
            content_ids: [],
            scores: {},
            items: [],
            friction_level: 'none',
          },
        }),
      });
    });

    await page.goto('/feed');
    await expect(page.getByText('No content available in this section.')).toBeVisible();
  });
});
