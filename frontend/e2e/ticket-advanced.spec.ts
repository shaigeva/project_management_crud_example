import { test, expect } from '@playwright/test';
import { TEST_CONFIG } from './utils/test-config';

test.describe('Ticket Advanced Features', () => {
  let projectId: string;
  let username: string;

  test.beforeEach(async ({ page }) => {
    // Login as super admin
    await page.goto('/login');
    await page.getByRole('textbox', { name: 'Username' }).fill('admin');
    await page.getByRole('textbox', { name: 'Password' }).fill('SuperAdmin123!');
    await page.getByRole('button', { name: 'Login' }).click();
    await expect(page).toHaveURL('/projects');

    // Get auth token from localStorage
    const authState = await page.evaluate(() => localStorage.getItem('auth_state'));
    const { token } = JSON.parse(authState || '{}');

    // Create an organization via API
    const orgResponse = await page.request.post(`${TEST_CONFIG.API_BASE_URL}/api/organizations`, {
      headers: { Authorization: `Bearer ${token}` },
      data: {
        name: `Test Org ${Date.now()}`,
        description: 'E2E test organization',
      },
    });

    const org = await orgResponse.json();

    // Create a user with project_manager role
    const timestamp = Date.now();
    username = `pm${timestamp}`;

    const userResponse = await page.request.post(
      `${TEST_CONFIG.API_BASE_URL}/api/users?organization_id=${org.id}&role=project_manager`,
      {
        headers: { Authorization: `Bearer ${token}` },
        data: {
          username,
          email: `${username}@example.com`,
          full_name: 'PM User',
        },
      }
    );

    const userData = await userResponse.json();
    const password = userData.generated_password;

    // Logout super admin
    await page.getByRole('button', { name: 'Logout' }).click();
    await expect(page).toHaveURL('/login');

    // Login as project manager
    await page.getByRole('textbox', { name: 'Username' }).fill(username);
    await page.getByRole('textbox', { name: 'Password' }).fill(password);
    await page.getByRole('button', { name: 'Login' }).click();
    await expect(page).toHaveURL('/projects');

    // Create a project
    await page.getByRole('button', { name: 'New Project' }).click();
    const projectName = `Test Project ${Date.now()}`;
    await page.locator('#project-name').fill(projectName);
    await page.locator('#project-description').fill('Test project description');
    await page.getByRole('button', { name: 'Create Project' }).click();

    // Wait for modal to close and project to appear
    await expect(page.getByRole('heading', { name: 'Create New Project' })).not.toBeVisible();
    await expect(page.getByText(projectName)).toBeVisible();

    // Extract project ID from the link
    const projectLink = page.locator('.project-link').filter({ hasText: projectName });
    const href = await projectLink.getAttribute('href');
    projectId = href?.split('/').pop() || '';

    // Navigate to project details
    await projectLink.click();
    await expect(page).toHaveURL(`/projects/${projectId}`);
  });

  test('can assign ticket to user when creating', async ({ page }) => {
    // Click New Ticket button
    await page.getByRole('button', { name: 'New Ticket' }).click();

    // Create ticket with assignee
    const ticketTitle = `Assigned Ticket ${Date.now()}`;
    await page.locator('#ticket-title').fill(ticketTitle);
    await page.locator('#ticket-description').fill('This ticket is assigned');
    // Select the option containing "PM User"
    const options = await page.locator('#ticket-assignee option').allTextContents();
    const pmUserOption = options.find(opt => opt.includes('PM User'));
    if (pmUserOption) {
      await page.locator('#ticket-assignee').selectOption({ label: pmUserOption });
    }

    await page.getByRole('button', { name: 'Create Ticket' }).click();

    // Ticket should show the assignee
    await expect(page.getByText(ticketTitle)).toBeVisible();
    const ticketRow = page.locator('tr').filter({ hasText: ticketTitle });
    await expect(ticketRow.locator('td').nth(3)).toContainText('PM User');
  });

  test('can create unassigned ticket', async ({ page }) => {
    // Create ticket without assignee
    await page.getByRole('button', { name: 'New Ticket' }).click();
    const ticketTitle = `Unassigned Ticket ${Date.now()}`;
    await page.locator('#ticket-title').fill(ticketTitle);
    await page.getByRole('button', { name: 'Create Ticket' }).click();

    // Ticket should show "Unassigned"
    await expect(page.getByText(ticketTitle)).toBeVisible();
    const ticketRow = page.locator('tr').filter({ hasText: ticketTitle });
    await expect(ticketRow.locator('td').nth(3)).toContainText('Unassigned');
  });

  test('can update ticket status in details page', async ({ page }) => {
    // Create a ticket
    await page.getByRole('button', { name: 'New Ticket' }).click();
    const ticketTitle = `Status Update Ticket ${Date.now()}`;
    await page.locator('#ticket-title').fill(ticketTitle);
    await page.getByRole('button', { name: 'Create Ticket' }).click();
    await expect(page.getByText(ticketTitle)).toBeVisible();

    // Navigate to ticket details
    await page.locator('.ticket-link').filter({ hasText: ticketTitle }).click();

    // Initial status should be TODO
    await expect(page.locator('.status-select')).toHaveValue('TODO');

    // Change status to IN_PROGRESS
    await page.locator('.status-select').selectOption('IN_PROGRESS');

    // Wait a moment for the update
    await page.waitForTimeout(500);

    // Status should be updated
    await expect(page.locator('.status-select')).toHaveValue('IN_PROGRESS');

    // Go back to project and verify status changed
    await page.getByRole('link', { name: '← Back to Project' }).click();
    const ticketRow = page.locator('tr').filter({ hasText: ticketTitle });
    await expect(ticketRow).toContainText('IN_PROGRESS');
  });

  test('can update ticket assignee in details page', async ({ page }) => {
    // Create an unassigned ticket
    await page.getByRole('button', { name: 'New Ticket' }).click();
    const ticketTitle = `Assignee Update Ticket ${Date.now()}`;
    await page.locator('#ticket-title').fill(ticketTitle);
    await page.getByRole('button', { name: 'Create Ticket' }).click();
    await expect(page.getByText(ticketTitle)).toBeVisible();

    // Navigate to ticket details
    await page.locator('.ticket-link').filter({ hasText: ticketTitle }).click();

    // Initially unassigned
    await expect(page.locator('.assignee-select')).toHaveValue('');

    // Assign to PM User
    const assigneeOptions = await page.locator('.assignee-select option').allTextContents();
    const pmUserAssigneeOption = assigneeOptions.find(opt => opt.includes('PM User'));
    if (pmUserAssigneeOption) {
      await page.locator('.assignee-select').selectOption({ label: pmUserAssigneeOption });
    }

    // Wait a moment for the update
    await page.waitForTimeout(500);

    // Assignee should be updated
    const assigneeSelect = page.locator('.assignee-select');
    const selectedValue = await assigneeSelect.inputValue();
    expect(selectedValue).not.toBe('');

    // Go back to project and verify assignee changed
    await page.getByRole('link', { name: '← Back to Project' }).click();
    const ticketRow = page.locator('tr').filter({ hasText: ticketTitle });
    await expect(ticketRow).toContainText('PM User');
  });

  test('can filter tickets by status', async ({ page }) => {
    // Create tickets with different statuses via API
    const authState = await page.evaluate(() => localStorage.getItem('auth_state'));
    const { token } = JSON.parse(authState || '{}');

    // Create TODO ticket
    const todoTitle = `TODO Ticket ${Date.now()}`;
    await page.request.post(`${TEST_CONFIG.API_BASE_URL}/api/tickets?project_id=${projectId}`, {
      headers: { Authorization: `Bearer ${token}` },
      data: { title: todoTitle, description: 'TODO ticket' },
    });

    // Create IN_PROGRESS ticket
    const inProgressTitle = `InProgress Ticket ${Date.now()}`;
    const inProgressResponse = await page.request.post(
      `${TEST_CONFIG.API_BASE_URL}/api/tickets?project_id=${projectId}`,
      {
        headers: { Authorization: `Bearer ${token}` },
        data: { title: inProgressTitle, description: 'In progress ticket' },
      }
    );
    const inProgressTicket = await inProgressResponse.json();

    // Update status to IN_PROGRESS
    await page.request.put(`${TEST_CONFIG.API_BASE_URL}/api/tickets/${inProgressTicket.id}/status`, {
      headers: { Authorization: `Bearer ${token}` },
      data: { status: 'IN_PROGRESS' },
    });

    // Refresh page
    await page.reload();

    // Both tickets should be visible initially
    await expect(page.getByText(todoTitle)).toBeVisible();
    await expect(page.getByText(inProgressTitle)).toBeVisible();

    // Filter by TODO
    await page.locator('#filter-status').selectOption('TODO');
    await page.waitForTimeout(300);

    // Only TODO ticket should be visible
    await expect(page.getByText(todoTitle)).toBeVisible();
    await expect(page.getByText(inProgressTitle)).not.toBeVisible();

    // Filter by IN_PROGRESS
    await page.locator('#filter-status').selectOption('IN_PROGRESS');
    await page.waitForTimeout(300);

    // Only IN_PROGRESS ticket should be visible
    await expect(page.getByText(todoTitle)).not.toBeVisible();
    await expect(page.getByText(inProgressTitle)).toBeVisible();

    // Clear filter
    await page.locator('#filter-status').selectOption('');
    await page.waitForTimeout(300);

    // Both should be visible again
    await expect(page.getByText(todoTitle)).toBeVisible();
    await expect(page.getByText(inProgressTitle)).toBeVisible();
  });

  test('can filter tickets by priority', async ({ page }) => {
    // Create tickets with different priorities
    await page.getByRole('button', { name: 'New Ticket' }).click();
    const highTitle = `High Priority ${Date.now()}`;
    await page.locator('#ticket-title').fill(highTitle);
    await page.locator('#ticket-priority').selectOption('HIGH');
    await page.getByRole('button', { name: 'Create Ticket' }).click();
    await expect(page.getByText(highTitle)).toBeVisible();

    await page.getByRole('button', { name: 'New Ticket' }).click();
    const lowTitle = `Low Priority ${Date.now()}`;
    await page.locator('#ticket-title').fill(lowTitle);
    await page.locator('#ticket-priority').selectOption('LOW');
    await page.getByRole('button', { name: 'Create Ticket' }).click();
    await expect(page.getByText(lowTitle)).toBeVisible();

    // Both should be visible
    await expect(page.getByText(highTitle)).toBeVisible();
    await expect(page.getByText(lowTitle)).toBeVisible();

    // Filter by HIGH
    await page.locator('#filter-priority').selectOption('HIGH');
    await page.waitForTimeout(300);

    // Only high priority should be visible
    await expect(page.getByText(highTitle)).toBeVisible();
    await expect(page.getByText(lowTitle)).not.toBeVisible();

    // Filter by LOW
    await page.locator('#filter-priority').selectOption('LOW');
    await page.waitForTimeout(300);

    // Only low priority should be visible
    await expect(page.getByText(highTitle)).not.toBeVisible();
    await expect(page.getByText(lowTitle)).toBeVisible();
  });

  test('can sort tickets by priority', async ({ page }) => {
    // Create tickets with different priorities
    await page.getByRole('button', { name: 'New Ticket' }).click();
    await page.locator('#ticket-title').fill('Low Priority Ticket');
    await page.locator('#ticket-priority').selectOption('LOW');
    await page.getByRole('button', { name: 'Create Ticket' }).click();

    await page.getByRole('button', { name: 'New Ticket' }).click();
    await page.locator('#ticket-title').fill('Critical Priority Ticket');
    await page.locator('#ticket-priority').selectOption('CRITICAL');
    await page.getByRole('button', { name: 'Create Ticket' }).click();

    await page.getByRole('button', { name: 'New Ticket' }).click();
    await page.locator('#ticket-title').fill('Medium Priority Ticket');
    await page.locator('#ticket-priority').selectOption('MEDIUM');
    await page.getByRole('button', { name: 'Create Ticket' }).click();

    // Sort by priority
    await page.locator('#sort-by').selectOption('priority');
    await page.waitForTimeout(300);

    // Get all ticket titles in order
    const tickets = await page.locator('.ticket-link').allTextContents();

    // Critical should be first, then Medium, then Low
    expect(tickets[0]).toContain('Critical');
    expect(tickets[1]).toContain('Medium');
    expect(tickets[2]).toContain('Low');
  });

  test('can sort tickets by title', async ({ page }) => {
    // Create tickets with different titles
    await page.getByRole('button', { name: 'New Ticket' }).click();
    await page.locator('#ticket-title').fill('Zebra Ticket');
    await page.getByRole('button', { name: 'Create Ticket' }).click();

    await page.getByRole('button', { name: 'New Ticket' }).click();
    await page.locator('#ticket-title').fill('Alpha Ticket');
    await page.getByRole('button', { name: 'Create Ticket' }).click();

    await page.getByRole('button', { name: 'New Ticket' }).click();
    await page.locator('#ticket-title').fill('Mu Ticket');
    await page.getByRole('button', { name: 'Create Ticket' }).click();

    // Sort by title
    await page.locator('#sort-by').selectOption('title');
    await page.waitForTimeout(300);

    // Get all ticket titles in order
    const tickets = await page.locator('.ticket-link').allTextContents();

    // Should be alphabetical
    expect(tickets[0]).toContain('Alpha');
    expect(tickets[1]).toContain('Mu');
    expect(tickets[2]).toContain('Zebra');
  });
});
