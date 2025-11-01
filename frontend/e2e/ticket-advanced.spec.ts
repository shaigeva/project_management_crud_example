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

  test('filtering and sorting tickets', async ({ page }) => {
    // Get auth token for API calls
    const authState = await page.evaluate(() => localStorage.getItem('auth_state'));
    const { token } = JSON.parse(authState || '{}');

    // Create a variety of tickets to test filtering and sorting
    // 1. TODO ticket with HIGH priority
    const todoHighTitle = `TODO High ${Date.now()}`;
    await page.request.post(`${TEST_CONFIG.API_BASE_URL}/api/tickets?project_id=${projectId}`, {
      headers: { Authorization: `Bearer ${token}` },
      data: { title: todoHighTitle, description: 'TODO high priority', priority: 'HIGH' },
    });

    // 2. IN_PROGRESS ticket with LOW priority
    const inProgressLowTitle = `InProgress Low ${Date.now()}`;
    const inProgressResponse = await page.request.post(
      `${TEST_CONFIG.API_BASE_URL}/api/tickets?project_id=${projectId}`,
      {
        headers: { Authorization: `Bearer ${token}` },
        data: { title: inProgressLowTitle, description: 'In progress low', priority: 'LOW' },
      }
    );
    const inProgressTicket = await inProgressResponse.json();
    await page.request.put(`${TEST_CONFIG.API_BASE_URL}/api/tickets/${inProgressTicket.id}/status`, {
      headers: { Authorization: `Bearer ${token}` },
      data: { status: 'IN_PROGRESS' },
    });

    // 3. TODO ticket with CRITICAL priority
    const todoCriticalTitle = `TODO Critical ${Date.now()}`;
    await page.request.post(`${TEST_CONFIG.API_BASE_URL}/api/tickets?project_id=${projectId}`, {
      headers: { Authorization: `Bearer ${token}` },
      data: { title: todoCriticalTitle, description: 'Critical ticket', priority: 'CRITICAL' },
    });

    // 4. Alphabetically named tickets for title sorting
    await page.request.post(`${TEST_CONFIG.API_BASE_URL}/api/tickets?project_id=${projectId}`, {
      headers: { Authorization: `Bearer ${token}` },
      data: { title: 'Zebra Ticket', description: 'Z ticket', priority: 'MEDIUM' },
    });
    await page.request.post(`${TEST_CONFIG.API_BASE_URL}/api/tickets?project_id=${projectId}`, {
      headers: { Authorization: `Bearer ${token}` },
      data: { title: 'Alpha Ticket', description: 'A ticket', priority: 'MEDIUM' },
    });

    // Reload page to see all tickets
    await page.reload();

    // Test 1: Filter by status TODO
    await page.locator('#filter-status').selectOption('TODO');
    await page.waitForTimeout(300);
    await expect(page.getByText(todoHighTitle)).toBeVisible();
    await expect(page.getByText(inProgressLowTitle)).not.toBeVisible();

    // Test 2: Filter by status IN_PROGRESS
    await page.locator('#filter-status').selectOption('IN_PROGRESS');
    await page.waitForTimeout(300);
    await expect(page.getByText(todoHighTitle)).not.toBeVisible();
    await expect(page.getByText(inProgressLowTitle)).toBeVisible();

    // Test 3: Clear status filter, then filter by priority HIGH
    await page.locator('#filter-status').selectOption('');
    await page.waitForTimeout(300);
    await page.locator('#filter-priority').selectOption('HIGH');
    await page.waitForTimeout(300);
    await expect(page.getByText(todoHighTitle)).toBeVisible();
    await expect(page.getByText(todoCriticalTitle)).not.toBeVisible();

    // Test 4: Filter by priority CRITICAL
    await page.locator('#filter-priority').selectOption('CRITICAL');
    await page.waitForTimeout(300);
    await expect(page.getByText(todoHighTitle)).not.toBeVisible();
    await expect(page.getByText(todoCriticalTitle)).toBeVisible();

    // Test 5: Clear filters and sort by priority
    await page.locator('#filter-priority').selectOption('');
    await page.waitForTimeout(300);
    await page.locator('#sort-by').selectOption('priority');
    await page.waitForTimeout(300);

    const ticketLinks = page.locator('.ticket-link');
    await expect(ticketLinks.first()).toBeVisible();
    let tickets = await ticketLinks.allTextContents();

    // Filter to only the tickets we created for this test
    const testTicketIndices = {
      critical: tickets.findIndex(t => t.includes('Critical')),
      high: tickets.findIndex(t => t.includes('High')),
      low: tickets.findIndex(t => t.includes('Low')),
    };

    // CRITICAL should come before HIGH, and HIGH before LOW (when they exist)
    if (testTicketIndices.critical >= 0 && testTicketIndices.high >= 0) {
      expect(testTicketIndices.critical).toBeLessThan(testTicketIndices.high);
    }
    if (testTicketIndices.high >= 0 && testTicketIndices.low >= 0) {
      expect(testTicketIndices.high).toBeLessThan(testTicketIndices.low);
    }

    // Test 6: Sort by title (alphabetically)
    await page.locator('#sort-by').selectOption('title');
    await page.waitForTimeout(300);
    tickets = await ticketLinks.allTextContents();

    const alphaIndex = tickets.findIndex(t => t.includes('Alpha'));
    const zebraIndex = tickets.findIndex(t => t.includes('Zebra'));
    expect(alphaIndex).toBeLessThan(zebraIndex);
  });
});
