import { expect, test } from '@playwright/test';

test('homepage loads with title and sections', async ({ page }) => {
    await page.goto('/en/');
    await expect(page).toHaveURL(/\/en\/$/);
    await expect(
        page.getByRole('heading', { name: /Wagtail User Guide/i }),
    ).toBeVisible();
    await expect(
        page.getByRole('link', { name: /Tutorial/i }).first(),
    ).toBeVisible();
});

test('tutorial section page loads', async ({ page }) => {
    const response = await page.goto('/en/tutorial/');
    expect(response?.status()).toBe(200);
    await expect(
        page.getByRole('heading', { name: /Tutorial/i }).first(),
    ).toBeVisible();
});

test('tutorial subpage loads', async ({ page }) => {
    const response = await page.goto('/en/tutorial/getting-started/');
    expect(response?.status()).toBe(200);
});

test('how-to subpage loads', async ({ page }) => {
    const response = await page.goto('/en/how-to/add-a-user/');
    expect(response?.status()).toBe(200);
});

test('unknown page returns 404', async ({ request }) => {
    const response = await request.get('/en/does-not-exist/');
    expect(response.status()).toBe(404);
});

test('dutch locale loads', async ({ page }) => {
    const response = await page.goto('/nl/');
    expect(response?.status()).toBe(200);
});
