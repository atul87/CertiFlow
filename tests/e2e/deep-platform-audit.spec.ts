import { test, expect } from "@playwright/test";

test.describe("Deep Platform Comprehensive Audit", () => {
  test.setTimeout(120000);

  const uncaughtPageErrors: { url: string; error: string }[] = [];

  test.beforeEach(async ({ page }) => {
    page.on("pageerror", (err) => {
      uncaughtPageErrors.push({ url: page.url(), error: err.message });
    });

    await page.setViewportSize({ width: 1440, height: 900 });
  });

  test("1. Comprehensive Audit: All Public Marketing Pages & Legal Pages", async ({ page }) => {
    const publicRoutes = [
      { path: "/", titleMatcher: /CertiFlow/i, headingMatcher: /personalized certificates|CertiFlow/i },
      { path: "/about", titleMatcher: /About|CertiFlow/i, headingMatcher: /About|Mission|CertiFlow/i },
      { path: "/contact", titleMatcher: /Contact|CertiFlow/i, headingMatcher: /Contact|Get in touch/i },
      { path: "/pricing", titleMatcher: /Pricing|CertiFlow/i, headingMatcher: /Pricing|Plans/i },
      { path: "/privacy", titleMatcher: /Privacy|CertiFlow/i, headingMatcher: /Privacy/i },
      { path: "/terms", titleMatcher: /Terms|CertiFlow/i, headingMatcher: /Terms/i },
      { path: "/security", titleMatcher: /Security|CertiFlow/i, headingMatcher: /Security/i },
      { path: "/resources", titleMatcher: /Resources|CertiFlow/i, headingMatcher: /Resources|Guides|Documentation/i },
      { path: "/templates", titleMatcher: /Templates|CertiFlow/i, headingMatcher: /Templates/i },
    ];

    for (const route of publicRoutes) {
      await page.goto(route.path);
      await page.waitForLoadState("domcontentloaded");
      await expect(page).toHaveTitle(route.titleMatcher);
      const heading = page.getByRole("heading", { level: 1 }).first();
      await expect(heading).toBeVisible();
    }
  });

  test("2. Comprehensive Audit: Interactive Marketing Features", async ({ page }) => {
    await page.goto("/");
    await page.waitForLoadState("networkidle");

    // Test Pricing Toggle
    const pricingSection = page.locator("#pricing");
    if (await pricingSection.isVisible()) {
      await pricingSection.scrollIntoViewIfNeeded();
      const annualToggle = page.getByRole("button", { name: /Yearly|Annual/i }).first();
      if (await annualToggle.isVisible()) {
        await annualToggle.click();
        await page.waitForTimeout(300);
      }
    }

    // Test Interactive Demo Recipient Switch
    const demo = page.locator("#demo");
    if (await demo.isVisible()) {
      await demo.scrollIntoViewIfNeeded();
      const recipientButtons = page.locator("#demo button");
      const count = await recipientButtons.count();
      if (count > 0) {
        await recipientButtons.first().click();
        await page.waitForTimeout(200);
      }
    }
  });

  test("3. Comprehensive Audit: All Authenticated SaaS Dashboard Routes", async ({ page }) => {
    await page.addInitScript(() => {
      localStorage.setItem("certiflow_access_token", "test_jwt_session_token");
      localStorage.setItem("certiflow_demo_mode", "true");
      localStorage.setItem("certiflow_org_id", "org_default_01");
    });

    const saasRoutes = [
      { path: "/app", expectedText: "Welcome back" },
      { path: "/app/projects", expectedText: "Projects" },
      { path: "/app/templates", expectedText: "Templates" },
      { path: "/app/imports", expectedText: "Import" },
      { path: "/app/issuance", expectedText: "Issuance" },
      { path: "/app/certificates", expectedText: "Certificate Vault" },
      { path: "/app/credentials", expectedText: "Digital Credentials" },
      { path: "/app/email", expectedText: "Email" },
      { path: "/app/analytics", expectedText: "Analytics" },
      { path: "/app/reports", expectedText: "Reports" },
      { path: "/app/team", expectedText: "Team" },
      { path: "/app/developer", expectedText: "Developer" },
      { path: "/app/billing", expectedText: "Billing" },
      { path: "/app/settings", expectedText: "Settings" },
    ];

    for (const route of saasRoutes) {
      await page.goto(route.path);
      await page.waitForLoadState("domcontentloaded");
      await expect(page.getByText(new RegExp(route.expectedText, "i")).first()).toBeVisible({ timeout: 10000 });
    }
  });

  test("4. Comprehensive Audit: Verification Edge Cases", async ({ page }) => {
    // 1. Valid Certificate
    await page.goto("/verify/CERT-AF72K9");
    await page.waitForLoadState("domcontentloaded");
    await expect(page.getByText(/Verified Authentic/i).first()).toBeVisible({ timeout: 10000 });

    // 2. Non-existent Certificate ID
    await page.goto("/verify/CERT-TOTALLY-INVALID-9999");
    await page.waitForLoadState("domcontentloaded");
    // Should show unverified or invalid message without crashing
    const invalidNotice = page.getByText(/Invalid|Not Found|Unverified|Verification Failed|Revoked/i).first();
    await expect(invalidNotice).toBeVisible({ timeout: 10000 });
  });

  test("5. Comprehensive Audit: Verify Zero Uncaught JavaScript Runtime Errors", async () => {
    if (uncaughtPageErrors.length > 0) {
      console.error("Uncaught Page Errors Logged:", uncaughtPageErrors);
    }
    expect(uncaughtPageErrors.length).toBe(0);
  });
});
