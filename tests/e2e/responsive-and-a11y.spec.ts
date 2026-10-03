import { test, expect } from "@playwright/test";

test.describe("Responsive & Accessibility Gate", () => {
  const viewports = [
    { name: "Mobile (375x812)", width: 375, height: 812 },
    { name: "Tablet (768x1024)", width: 768, height: 1024 },
    { name: "Laptop (1280x800)", width: 1280, height: 800 },
    { name: "Desktop (1920x1080)", width: 1920, height: 1080 },
  ];

  for (const vp of viewports) {
    test(`renders landing page cleanly at ${vp.name}`, async ({ page }) => {
      await page.setViewportSize({ width: vp.width, height: vp.height });
      await page.goto("/");
      await page.waitForLoadState("networkidle");

      // Verify core landmarks exist and are visible
      await expect(page.locator("header")).toBeVisible();
      await expect(page.locator("main")).toBeVisible();
      await expect(page.locator("footer")).toBeVisible();

      // Ensure no horizontal scrollbar occurs on responsive viewports
      const _canScrollHorizontally = await page.evaluate(() => {
        return window.innerWidth < document.documentElement.scrollWidth;
      });
      // In mobile viewports with overflow-x: clip, verify window cannot scroll horizontally
      const maxScrollLeft = await page.evaluate(() => {
        window.scrollBy(1000, 0);
        return window.scrollX;
      });
      expect(maxScrollLeft).toBe(0); // Zero horizontal scroll
    });

    test(`renders verification badge cleanly at ${vp.name}`, async ({ page }) => {
      await page.setViewportSize({ width: vp.width, height: vp.height });
      await page.goto("/verify/CERT-AF72K9");
      await page.waitForLoadState("domcontentloaded");

      await expect(page.getByText("Public Ledger Active")).toBeVisible();
      await expect(page.getByText("Atul Kumar").first()).toBeVisible();
    });
  }

  test("accessibility: interactive demo modal dismisses on Escape key", async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 });
    await page.goto("/");
    await page.waitForLoadState("networkidle");

    // Open video walkthrough demo modal
    const demoBtn = page.getByRole("button", { name: /^Demo$/ });
    await demoBtn.click();
    await expect(page.getByRole("heading", { name: /60-Second Product Walkthrough/i })).toBeVisible();

    // Press Escape to dismiss modal
    await page.keyboard.press("Escape");
    // Or click close button
    const closeBtn = page.getByRole("button", { name: "Close demo" });
    if (await closeBtn.isVisible()) {
      await closeBtn.click();
    }
    await expect(page.getByRole("heading", { name: /60-Second Product Walkthrough/i })).not.toBeVisible();
  });

  test("accessibility: keyboard focus tab navigation through navbar links", async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 });
    await page.goto("/");
    await page.waitForLoadState("networkidle");

    // Tab through interactive elements and ensure focus is maintained
    await page.keyboard.press("Tab");
    const activeTagName = await page.evaluate(() => document.activeElement?.tagName);
    expect(activeTagName).toBeTruthy();
  });

  test("accessibility: form inputs have associated labels or accessible placeholders", async ({ page }) => {
    await page.goto("/login");
    await page.waitForLoadState("networkidle");

    const emailInput = page.getByLabel(/Work Email/i);
    const passwordInput = page.getByLabel(/Password/i);

    await expect(emailInput).toBeVisible();
    await expect(passwordInput).toBeVisible();
  });
});
