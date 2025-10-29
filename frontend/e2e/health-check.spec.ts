import { test, expect } from '@playwright/test';

test.describe('Health Check', () => {
  test('should display hello world message', async ({ page }) => {
    await page.goto('/');

    // Check for the main heading
    await expect(page.getByRole('heading', { name: 'Project Management System' })).toBeVisible();

    // Check for hello world message
    await expect(page.getByText('Hello World from Project Management App')).toBeVisible();
  });

  test('should connect to backend and show healthy status', async ({ page }) => {
    await page.goto('/');

    // Wait for the status to change from loading
    await page.waitForSelector('.status.connected, .status.disconnected', { timeout: 10000 });

    // Check that we have a connected status
    const statusElement = page.locator('.status');
    await expect(statusElement).toHaveClass(/connected/);

    // Check for the success message
    await expect(page.getByText(/Connected to backend/i)).toBeVisible();
  });

  test('should display frontend port information', async ({ page }) => {
    await page.goto('/');

    // Check for port information
    await expect(page.getByText(/Frontend running on port 3000/i)).toBeVisible();
  });
});
