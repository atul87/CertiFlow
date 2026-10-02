import { test, expect } from "@playwright/test";

test.describe("End-to-End Authentication System Verification", () => {
  test.setTimeout(60000);

  const testPassword = "SecurePassword2026!";

  test("1. Route Protection: Unauthenticated user accessing /app is redirected to /login", async ({ page }) => {
    // Clear any existing session
    await page.goto("/login");
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });

    // Try accessing protected dashboard
    await page.goto("/app");
    await page.waitForLoadState("networkidle");

    // Expect to be redirected to login with redirect parameter
    await expect(page).toHaveURL(/\/login/);
    await expect(page.getByRole("heading", { name: /Welcome back/i })).toBeVisible();
  });

  test("2. Signup Validation: Rejects passwords shorter than 8 chars or missing numbers", async ({ page }) => {
    await page.goto("/signup");
    await page.waitForLoadState("networkidle");

    await page.fill('input[placeholder="Atul Kumar"]', "Short Pass");
    await page.fill('input[type="email"]', "short@certiflow.io");
    await page.fill('input[type="password"]', "short");

    await page.getByRole("button", { name: /Create Account/i }).click();
    await expect(page.getByText(/Password must be at least 8 characters long/i)).toBeVisible();

    // Password with letters only (no digits)
    await page.fill('input[type="password"]', "allletterslongpassword");
    await page.getByRole("button", { name: /Create Account/i }).click();
    await expect(page.getByText(/Password must contain both letters and numbers/i)).toBeVisible();
  });

  test("3. Registration Flow: Creates new user and organization with live backend", async ({ page }) => {
    const uniqueEmail = `authtest_${Date.now()}_${Math.random().toString(36).substring(7)}@certiflow.io`;
    const uniqueName = `Test User ${Date.now()}`;

    await page.goto("/signup");
    await page.waitForLoadState("networkidle");

    await page.fill('input[placeholder="Atul Kumar"]', uniqueName);
    await page.fill('input[type="email"]', uniqueEmail);
    await page.fill('input[type="password"]', testPassword);
    await page.selectOption("select", "Bootcamp / Training Center");

    await page.getByRole("button", { name: /Create Account/i }).click();

    // Successfully creates account and lands on /app
    await expect(page).toHaveURL(/\/app/, { timeout: 15000 });
    await expect(page.getByRole("heading", { name: /Welcome back/i })).toBeVisible();
  });

  test("4. Login Validation: Handles invalid credentials with clear feedback", async ({ page }) => {
    await page.goto("/login");
    await page.waitForLoadState("networkidle");

    await page.fill('#login-email', "nonexistent.user.2026@certiflow.io");
    await page.fill('#login-password', "WrongPassword123!");

    await page.getByRole("button", { name: /Sign In with Backend/i }).click();
    await expect(page.getByText(/Authentication failed/i)).toBeVisible({ timeout: 10000 });
  });

  test("5. Registration and Login Sequence: Registers new user and signs in seamlessly", async ({ page }) => {
    const userEmail = `login_test_${Date.now()}_${Math.random().toString(36).substring(7)}@certiflow.io`;
    const userName = "Login Test User";

    // 1. Register user
    await page.goto("/signup");
    await page.waitForLoadState("networkidle");
    await page.fill('input[placeholder="Atul Kumar"]', userName);
    await page.fill('input[type="email"]', userEmail);
    await page.fill('input[type="password"]', testPassword);
    await page.getByRole("button", { name: /Create Account/i }).click();
    await expect(page).toHaveURL(/\/app/, { timeout: 15000 });

    // 2. Clear tokens to simulate returning session
    await page.goto("/login");
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
    await page.reload();
    await page.waitForLoadState("networkidle");

    // 3. Log in with registered credentials
    await page.fill('#login-email', userEmail);
    await page.fill('#login-password', testPassword);
    await page.getByRole("button", { name: /Sign In with Backend/i }).click();

    // Expect successful redirect to /app
    await expect(page).toHaveURL(/\/app/, { timeout: 15000 });
    await expect(page.getByRole("heading", { name: /Welcome back/i })).toBeVisible();
  });

  test("6. Forgot Password Flow: Sends enumeration-safe reset confirmation", async ({ page }) => {
    const forgotEmail = `forgot_${Date.now()}@certiflow.io`;
    await page.goto("/forgot-password");
    await page.waitForLoadState("networkidle");

    await expect(page.getByRole("heading", { name: /Reset Your Password/i })).toBeVisible();
    await page.fill('input[type="email"]', forgotEmail);
    await page.getByRole("button", { name: /Send Secure Reset Link/i }).click();

    await expect(page.getByText(/Reset Link Sent/i)).toBeVisible();
    await expect(page.getByText(forgotEmail)).toBeVisible();
  });

  test("7. Reset Password Flow: Validates password match and token form", async ({ page }) => {
    await page.goto("/reset-password");
    await page.waitForLoadState("networkidle");

    await expect(page.getByRole("heading", { name: /Set New Password/i })).toBeVisible();

    await page.fill('input[placeholder="Paste token from email"]', "sample_reset_token_xyz");
    const passwordInputs = page.locator('input[type="password"]');
    await passwordInputs.nth(0).fill("NewSecurePassword2026!");
    await passwordInputs.nth(1).fill("MismatchedPassword2026!");

    await page.getByRole("button", { name: /Update Account Password/i }).click();
    await expect(page.getByText(/Passwords do not match/i)).toBeVisible();
  });
});
