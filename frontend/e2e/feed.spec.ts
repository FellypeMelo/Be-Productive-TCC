import { test, expect } from '@playwright/test';

test.describe('Feed', () => {
  test('feed page loads for unauthenticated user', async ({ page }) => {
    await page.goto('/feed');
    await expect(page).toHaveTitle(/Feed.*Be Productive/);
    await expect(page.getByRole('heading', { name: 'Your Feed' })).toBeVisible({ timeout: 10000 });
  });

  test('feed page has correct title tag', async ({ page }) => {
    await page.goto('/feed');
    await expect(page).toHaveTitle(/Be Productive/);
  });
});

// Authenticated tests — only run when storageState is available
test.describe('Feed (authenticated)', () => {
  test.beforeEach(async ({ context }) => {
    // Guard: skip if auth state was not loaded (no server during setup)
    const storage = await context.storageState().catch(() => null);
    if (!storage || !storage.origins || storage.origins.length === 0) {
      test.skip(true, 'No authenticated state available — globalSetup may have been skipped');
    }
  });

  test('feed grid skeleton appears during loading', async ({ page }) => {
    await page.route('**/api/v1/feed*', async (route) => {
      await new Promise((r) => setTimeout(r, 2000));
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          data: { content_ids: [], scores: {}, items: [], friction_level: 'none' },
        }),
      });
    });

    await page.goto('/feed');
    await expect(page.locator('.animate-pulse').first()).toBeVisible();
  });

  test('category filter buttons exist', async ({ page }) => {
    await page.route('**/api/v1/feed*', async (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          data: {
            content_ids: [1], scores: {},
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
    await expect(page.getByRole('button', { name: 'All', exact: true })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Productivity' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Entertainment' })).toBeVisible();
  });

  test('topic browser is visible', async ({ page }) => {
    await page.route('**/api/v1/feed*', async (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          data: {
            content_ids: [1], scores: {},
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
    await expect(page.getByRole('button', { name: 'All For You' })).toBeVisible();
  });

  test('empty feed shows no content cards', async ({ page }) => {
    await page.route('**/api/v1/feed*', async (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          data: { content_ids: [], scores: {}, items: [], friction_level: 'none' },
        }),
      });
    });

    await page.goto('/feed');
    // Feed renders nothing when empty — verify no article cards exist
    await expect(page.locator('a.block.group')).toHaveCount(0, { timeout: 5000 });
  });

  test('feed shows content items', async ({ page }) => {
    await page.route('**/api/v1/feed*', async (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          data: {
            content_ids: [1], scores: {},
            items: [{
              id_conteudo: 1, titulo: 'Mocked Content', categoria: 'PRODUTIVIDADE',
              tipo_de_midia: 'VIDEO', autor_id: 1, data_publicacao: '2026-01-01',
              score_de_qualidade: 0.9, corpo: '', tags_relevantes: '',
            }],
            friction_level: 'none',
          },
        }),
      });
    });

    await page.goto('/feed');
    // Wait for the feed to render (content cards appear after API response)
    await expect(page.locator('h3').first()).toBeVisible({ timeout: 10000 });
  });
});
