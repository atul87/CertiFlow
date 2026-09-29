import { test, expect } from "@playwright/test";

test.describe("P12: CertiFlow SaaS Golden Path", () => {
  test("P12.4 Auth Guard: unauthenticated request to /app redirects to /login", async ({ page }) => {
    await page.goto("/app");
    await page.waitForURL(/\/login/);
    await expect(page).toHaveURL(/\/login/);
    await expect(page.getByRole("heading", { name: /Welcome back/i })).toBeVisible();
  });

  test("P12.2-P12.36 Authenticated SaaS Shell, Dashboard Widgets, and Route Matrix", async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 });

    // Seed authenticated session in localStorage
    await page.addInitScript(() => {
      localStorage.setItem("certiflow_access_token", "test_jwt_session_token");
      localStorage.setItem("certiflow_org_id", "org_default_01");
    });

    // 1. Visit SaaS Dashboard
    await page.goto("/app");
    await page.waitForLoadState("domcontentloaded");

    // Verify App Shell Branding & Header
    await expect(page.getByText("CertiFlow").first()).toBeVisible({ timeout: 10000 });
    await expect(page.getByText("Welcome back").first()).toBeVisible({ timeout: 10000 });

    // 2. Test Command Palette
    const searchTrigger = page.locator('[data-testid="command-palette-trigger"]');
    await expect(searchTrigger).toBeVisible();
    await searchTrigger.click();

    // Verify Command Palette input is open
    const paletteInput = page.locator('[data-testid="command-palette-input"]');
    await expect(paletteInput).toBeVisible({ timeout: 5000 });

    // Type query and close with Escape
    await paletteInput.fill("Templates");
    await page.keyboard.press("Escape");
    await expect(paletteInput).not.toBeVisible();

    // 3. Test Notification Center
    const bellBtn = page.locator("#notification-bell");
    await expect(bellBtn).toBeVisible();
    await bellBtn.click({ force: true });
    await expect(page.getByRole("heading", { name: "Notifications" })).toBeVisible();
    await page.keyboard.press("Escape");

    // 4. Verify Dashboard Widgets
    await expect(page.getByText("Total Certificates").first()).toBeVisible();
    await expect(page.getByText("Verification Rate").first()).toBeVisible();
    await expect(page.getByText("Email Delivery Rate").first()).toBeVisible();
    await expect(page.getByText("Issuance & Delivery Trend").first()).toBeVisible();
    await expect(page.getByText("Active Issuance Jobs").first()).toBeVisible();
    await expect(page.getByText("Plan Quota & Usage").first()).toBeVisible();

    // 5. Navigate to Templates
    await page.goto("/app/templates");
    await page.waitForLoadState("domcontentloaded");
    await expect(page.getByText("Templates").first()).toBeVisible();

    // 6. Navigate to Imports
    await page.goto("/app/imports");
    await page.waitForLoadState("domcontentloaded");
    await expect(page.getByText("Import Center").first()).toBeVisible();

    // 7. Navigate to Issuance
    await page.goto("/app/issuance");
    await page.waitForLoadState("domcontentloaded");
    await expect(page.getByText("Issuance").first()).toBeVisible();

    // 8. Navigate to Certificates Vault
    await page.goto("/app/certificates");
    await page.waitForLoadState("domcontentloaded");
    await expect(page.getByText("Certificate Vault").first()).toBeVisible();

    // 9. Navigate to Digital Credentials
    await page.goto("/app/credentials");
    await page.waitForLoadState("domcontentloaded");
    await expect(page.getByText("Digital Credentials").first()).toBeVisible();

    // 10. Navigate to Email Center
    await page.goto("/app/email");
    await page.waitForLoadState("domcontentloaded");
    await expect(page.getByText("Email Center").first()).toBeVisible();

    // 11. Navigate to Analytics
    await page.goto("/app/analytics");
    await page.waitForLoadState("domcontentloaded");
    await expect(page.getByText("Analytics").first()).toBeVisible();

    // 12. Navigate to Team & RBAC
    await page.goto("/app/team");
    await page.waitForLoadState("domcontentloaded");
    await expect(page.getByText("Team Management").first()).toBeVisible();

    // 13. Navigate to Developer Portal
    await page.goto("/app/developer");
    await page.waitForLoadState("domcontentloaded");
    await expect(page.getByText("Developer Portal").first()).toBeVisible();

    // 14. Navigate to Billing
    await page.goto("/app/billing");
    await page.waitForLoadState("domcontentloaded");
    await expect(page.getByText("Billing").first()).toBeVisible();

    // 15. Navigate to Settings
    await page.goto("/app/settings");
    await page.waitForLoadState("domcontentloaded");
    await expect(page.getByText("Settings").first()).toBeVisible();

    // 16. Verify Public Verification Portal
    await page.goto("/verify/demo");
    await page.waitForLoadState("domcontentloaded");
    await expect(page.getByText("CertiFlow").first()).toBeVisible();
  });
});
