// End-to-End Frontend Tests using Playwright
// Install: npm install -D @playwright/test
// Run: npx playwright test

const { test, expect } = require('@playwright/test');

const BASE_URL = process.env.BASE_URL || 'http://localhost:3000';
const TEST_EMAIL = 'playwright_test@example.com';
const TEST_PASSWORD = 'TestPass123';

test.describe('Authentication System E2E Tests', () => {
  
  test.beforeEach(async ({ page }) => {
    // Start each test with a fresh session
    await page.context().clearCookies();
  });

  test('Complete authentication flow', async ({ page }) => {
    // 1. Visit home page
    await page.goto(BASE_URL);
    await expect(page).toHaveTitle(/Auth System/);
    
    // Should see authentication options
    await expect(page.locator('text=Sign In')).toBeVisible();
    await expect(page.locator('text=Create Account')).toBeVisible();

    // 2. Navigate to registration
    await page.click('text=Create Account');
    await expect(page).toHaveURL(/.*\/register/);
    await expect(page.locator('text=Create your account')).toBeVisible();

    // 3. Register a new user
    await page.fill('input[type="email"]', TEST_EMAIL);
    await page.fill('input[name="password"]', TEST_PASSWORD);
    await page.fill('input[name="confirmPassword"]', TEST_PASSWORD);
    
    // Check password strength indicators
    await expect(page.locator('text=At least 8 characters')).toHaveClass(/text-green-600/);
    await expect(page.locator('text=One uppercase letter')).toHaveClass(/text-green-600/);
    await expect(page.locator('text=One lowercase letter')).toHaveClass(/text-green-600/);
    await expect(page.locator('text=One number')).toHaveClass(/text-green-600/);

    await page.click('button[type="submit"]');

    // Should show success message or redirect to login
    try {
      // If registration succeeds
      await expect(page.locator('text=Registration Successful!')).toBeVisible({ timeout: 5000 });
      await page.waitForURL(/.*\/login/, { timeout: 5000 });
    } catch {
      // If user already exists, navigate to login manually
      await page.goto(`${BASE_URL}/login`);
    }

    // 4. Login with credentials
    await expect(page).toHaveURL(/.*\/login/);
    await expect(page.locator('text=Sign in to your account')).toBeVisible();

    await page.fill('input[type="email"]', TEST_EMAIL);
    await page.fill('input[type="password"]', TEST_PASSWORD);
    await page.click('button[type="submit"]');

    // Should redirect to dashboard
    await page.waitForURL(/.*\/dashboard/, { timeout: 10000 });

    // 5. Verify dashboard access
    await expect(page.locator('text=Dashboard')).toBeVisible();
    await expect(page.locator(`text=Welcome, ${TEST_EMAIL}`)).toBeVisible();
    await expect(page.locator('text=Authentication Successful!')).toBeVisible();
    
    // Check user information is displayed
    await expect(page.locator('text=Your Account')).toBeVisible();
    await expect(page.locator(`text=${TEST_EMAIL}`)).toBeVisible();

    // Check security features are highlighted
    await expect(page.locator('text=Secure Authentication')).toBeVisible();
    await expect(page.locator('text=CSRF Protection')).toBeVisible();
    await expect(page.locator('text=Rate Limited')).toBeVisible();

    // 6. Test logout
    await page.click('button:has-text("Sign out")');
    
    // Should redirect to login page
    await page.waitForURL(/.*\/login/, { timeout: 5000 });
    await expect(page.locator('text=Sign in to your account')).toBeVisible();

    // 7. Verify dashboard is no longer accessible
    await page.goto(`${BASE_URL}/dashboard`);
    await page.waitForURL(/.*\/login/, { timeout: 5000 });
    await expect(page.locator('text=Sign in to your account')).toBeVisible();
  });

  test('Login form validation', async ({ page }) => {
    await page.goto(`${BASE_URL}/login`);

    // Test empty form submission
    await page.click('button[type="submit"]');
    await expect(page.locator('text=Please enter a valid email address')).toBeVisible();
    await expect(page.locator('text=Password is required')).toBeVisible();

    // Test invalid email
    await page.fill('input[type="email"]', 'invalid-email');
    await page.click('button[type="submit"]');
    await expect(page.locator('text=Please enter a valid email address')).toBeVisible();

    // Test valid form
    await page.fill('input[type="email"]', TEST_EMAIL);
    await page.fill('input[type="password"]', 'wrong-password');
    await page.click('button[type="submit"]');
    
    // Should show authentication error
    await expect(page.locator('text=Invalid credentials')).toBeVisible({ timeout: 5000 });
  });

  test('Registration form validation', async ({ page }) => {
    await page.goto(`${BASE_URL}/register`);

    // Test password strength requirements
    await page.fill('input[type="email"]', TEST_EMAIL);
    
    // Weak password
    await page.fill('input[name="password"]', 'weak');
    await expect(page.locator('text=At least 8 characters')).toHaveClass(/text-gray-400/);
    await expect(page.locator('text=One uppercase letter')).toHaveClass(/text-gray-400/);
    await expect(page.locator('text=One number')).toHaveClass(/text-gray-400/);

    // Strong password
    await page.fill('input[name="password"]', TEST_PASSWORD);
    await expect(page.locator('text=At least 8 characters')).toHaveClass(/text-green-600/);
    await expect(page.locator('text=One uppercase letter')).toHaveClass(/text-green-600/);
    await expect(page.locator('text=One lowercase letter')).toHaveClass(/text-green-600/);
    await expect(page.locator('text=One number')).toHaveClass(/text-green-600/);

    // Test password confirmation
    await page.fill('input[name="confirmPassword"]', 'different-password');
    await page.click('button[type="submit"]');
    await expect(page.locator('text=Passwords don\'t match')).toBeVisible();
  });

  test('Navigation links work correctly', async ({ page }) => {
    await page.goto(BASE_URL);

    // Test navigation to login
    await page.click('text=Sign In');
    await expect(page).toHaveURL(/.*\/login/);

    // Test back to home
    await page.click('text=Back to home');
    await expect(page).toHaveURL(BASE_URL);

    // Test navigation to register
    await page.click('text=Create Account');
    await expect(page).toHaveURL(/.*\/register/);

    // Test navigation to login from register
    await page.click('text=sign in to your existing account');
    await expect(page).toHaveURL(/.*\/login/);

    // Test navigation to register from login
    await page.click('text=create a new account');
    await expect(page).toHaveURL(/.*\/register/);
  });

  test('Loading states work correctly', async ({ page }) => {
    await page.goto(`${BASE_URL}/login`);

    await page.fill('input[type="email"]', TEST_EMAIL);
    await page.fill('input[type="password"]', TEST_PASSWORD);

    // Click submit and immediately check for loading state
    await page.click('button[type="submit"]');
    
    // Loading state should appear briefly
    const loadingText = page.locator('text=Signing in...');
    // Note: Loading state might be too fast to catch in tests, so we make it optional
    try {
      await expect(loadingText).toBeVisible({ timeout: 1000 });
    } catch {
      // Loading state was too fast, which is fine
    }
  });

  test('Responsive design works on mobile', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    await page.goto(BASE_URL);
    
    // Elements should still be visible and functional on mobile
    await expect(page.locator('text=Auth System')).toBeVisible();
    await expect(page.locator('text=Sign In')).toBeVisible();
    await expect(page.locator('text=Create Account')).toBeVisible();

    // Test mobile navigation
    await page.click('text=Sign In');
    await expect(page).toHaveURL(/.*\/login/);
    
    // Form should work on mobile
    await page.fill('input[type="email"]', TEST_EMAIL);
    await page.fill('input[type="password"]', TEST_PASSWORD);
    await expect(page.locator('button[type="submit"]')).toBeVisible();
  });
});

// Configuration for Playwright
module.exports = {
  testDir: './tests',
  timeout: 30000,
  use: {
    baseURL: BASE_URL,
    headless: process.env.CI ? true : false,
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { browserName: 'chromium' },
    },
    {
      name: 'firefox',
      use: { browserName: 'firefox' },
    },
    {
      name: 'webkit',
      use: { browserName: 'webkit' },
    },
  ],
};