import { test, expect } from "@playwright/test";

test.describe("E2E: CertiFlow Master Product Journey", () => {
  test.beforeEach(async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 });
  });

  test("executes complete flow: Landing -> Signup -> Onboarding -> Projects -> Data -> Mapping -> Editor -> Preview -> Generate -> Vault -> Verify", async ({ page }) => {
    // 1. Landing Page
    await page.goto("/");
    await page.waitForLoadState("networkidle");

    await expect(page).toHaveTitle(/CertiFlow/i);
    const heroCta = page.getByRole("link", { name: /Create Certificates Free/i }).first();
    await expect(heroCta).toBeVisible();

    // 2. Signup Page
    await page.goto("/signup");
    await page.waitForLoadState("networkidle");

    await expect(page.getByRole("heading", { name: /Start creating free/i })).toBeVisible();
    await page.fill('input[placeholder="Atul Kumar"]', "Atul Kumar");
    await page.fill('input[type="email"]', "atul.kumar@certiflow.test");
    await page.fill('input[type="password"]', "SuperSecurePass2026!");
    await page.selectOption("select", "University / College");

    // 3. Onboarding Flow
    await page.goto("/onboarding");
    await page.waitForLoadState("networkidle");

    await expect(page.getByRole("heading", { name: /Welcome to CertiFlow/i })).toBeVisible();
    await page.getByText("College / University").click();
    await page.getByRole("button", { name: /Continue/i }).click();

    await expect(page.getByRole("heading", { name: /What do you want to create/i })).toBeVisible();
    await page.getByText("Course Completion").click();
    await page.getByRole("button", { name: /Continue/i }).click();

    await expect(page.getByRole("heading", { name: /You're ready/i })).toBeVisible();
    await page.getByRole("button", { name: /Create Your First Project/i }).click();

    // 4. Projects Listing Dashboard
    await page.goto("/app/projects");
    await page.waitForLoadState("networkidle");
    await expect(page.getByText("AI Workshop 2026")).toBeVisible();

    // 5. Data Workbench (CSV Import & Validation)
    await page.goto("/app/projects/proj-ai-2026/data");
    await page.waitForLoadState("networkidle");

    await expect(page.getByRole("heading", { name: /Recipient Data Workbench/i })).toBeVisible();
    await expect(page.getByText("Rows Verified")).toBeVisible();
    await expect(page.getByText("Atul Kumar").first()).toBeVisible();

    // 6. Field Mapping Studio
    await page.goto("/app/projects/proj-ai-2026/mapping");
    await page.waitForLoadState("networkidle");

    await expect(page.getByRole("heading", { name: /Field Mapping Studio/i })).toBeVisible();
    await expect(page.getByText("{{NAME}}")).toBeVisible();
    await expect(page.getByText("{{COURSE}}")).toBeVisible();
    await expect(page.getByText("{{DATE}}")).toBeVisible();
    await expect(page.getByText("{{CERTIFICATE_ID}}")).toBeVisible();

    // Trigger Auto-Match All
    const autoMatchBtn = page.getByRole("button", { name: /Auto-Match All/i });
    if (await autoMatchBtn.isVisible()) {
      await autoMatchBtn.click();
    }

    // 7. Certificate Canvas Editor
    await page.goto("/app/projects/proj-ai-2026/editor");
    await page.waitForLoadState("networkidle");

    await expect(page.getByText("AI Workshop 2026")).toBeVisible();
    await expect(page.getByText("A4 300 DPI")).toBeVisible();

    // 8. Live Recipient Preview Switcher
    await page.goto("/app/projects/proj-ai-2026/preview");
    await page.waitForLoadState("networkidle");

    await expect(page.getByText("Live Recipient Preview Studio")).toBeVisible();
    // Switch to long recipient to verify Smart-Fit text auto-scaling in DOM
    await page.getByText("Dr. Vikramaditya Chandrasekharan").first().click();
    await expect(page.getByText(/Smart Text Fit: Scaled/i)).toBeVisible();

    // 9. Batch Generation Pipeline
    await page.goto("/app/projects/proj-ai-2026/generate");
    await page.waitForLoadState("networkidle");

    await expect(page.getByRole("heading", { name: /High-Throughput PDF Compiler/i })).toBeVisible();
    const startBatchBtn = page.getByRole("button", { name: /Start 500 Batch Generation/i });
    await expect(startBatchBtn).toBeVisible();
    await startBatchBtn.click();

    // Wait for the 4.5s simulation to reach 100% completion
    await expect(page.getByRole("button", { name: /Download ZIP/i })).toBeVisible({ timeout: 12000 });
    await expect(page.getByText(/Batch rendering completed/i)).toBeVisible();

    // 10. Certificate Vault
    await page.goto("/app/certificates");
    await page.waitForLoadState("networkidle");

    await expect(page.getByText("Credential Vault & Public Registry")).toBeVisible();
    await expect(page.getByText("Atul Kumar").first()).toBeVisible();
    await expect(page.getByText("CERT-AF72K9")).toBeVisible();

    // 11. Public Verification Portal
    await page.goto("/verify/CERT-AF72K9");
    await page.waitForLoadState("networkidle");

    await expect(page.getByText(/Verified Authentic/i).first()).toBeVisible();
    await expect(page.getByRole("heading", { name: "Official Credential Verification" })).toBeVisible();
    await expect(page.getByText("Atul Kumar").first()).toBeVisible();
    await expect(page.getByText("AI Workshop 2026").first()).toBeVisible();
    await expect(page.getByText(/SHA-256 Signature/i)).toBeVisible();
    await expect(page.getByRole("button", { name: /Download Verified PDF/i })).toBeVisible();
  });
});
