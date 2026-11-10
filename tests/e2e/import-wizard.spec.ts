import { test, expect } from "@playwright/test";
import * as path from "path";
import * as fs from "fs";

const ARTIFACT_DIR = path.resolve(process.cwd(), "test-results", "artifacts");
if (!fs.existsSync(ARTIFACT_DIR)) {
  fs.mkdirSync(ARTIFACT_DIR, { recursive: true });
}
const SAMPLE_CSV = path.resolve(process.cwd(), "sample_recipients.csv");

test.describe("E2E: Import Wizard End-to-End Flow", () => {
  test.beforeEach(async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 });
    await page.addInitScript(() => {
      localStorage.setItem("certiflow_access_token", "demo_access_token_2026");
      localStorage.setItem("certiflow_demo_mode", "true");
      localStorage.setItem("certiflow_org_id", "org_demo_01");
    });
  });

  test("completes the 4-step import lifecycle: Upload -> Mapping -> Validation -> Confirm -> Reset", async ({ page }) => {
    // 1. Navigate to Imports Center
    await page.goto("/app/imports");
    await page.waitForLoadState("networkidle");

    // Verify page header and wizard container
    await expect(page.getByRole("heading", { name: /Import Center/i })).toBeVisible();
    await expect(page.getByText("Upload your recipient list")).toBeVisible();

    // Verify Step 0 is active
    const uploadStep = page.locator("span", { hasText: "Upload" }).first();
    await expect(uploadStep).toBeVisible();

    // Upload button should initially be disabled before file selection
    const uploadBtn = page.locator("#upload-analyze-btn");
    await expect(uploadBtn).toBeDisabled();

    // Screenshot initial upload screen
    await page.screenshot({ path: `${ARTIFACT_DIR}/step0_upload_initial.png` });

    // 2. Select Template & Upload CSV
    const templateSelect = page.locator("#template-select");
    await expect(templateSelect).toBeVisible();
    const options = await templateSelect.locator("option").all();
    if (options.length > 1) {
      const val = await options[1].getAttribute("value");
      if (val) await templateSelect.selectOption(val);
    }

    // Attach sample recipients CSV
    const fileInput = page.locator("#recipient-file-input");
    await fileInput.setInputFiles(SAMPLE_CSV);

    // Verify file is shown in dropzone
    await expect(page.getByText("sample_recipients.csv")).toBeVisible();
    await expect(uploadBtn).toBeEnabled();

    // Screenshot after file attached
    await page.screenshot({ path: `${ARTIFACT_DIR}/step0_file_selected.png` });

    // 3. Click Upload & Analyze -> Transition to Step 1 (Mapping)
    await uploadBtn.click();

    // Wait for Step 1 Mapping view
    await expect(page.getByRole("heading", { name: /Map your columns/i })).toBeVisible();
    await expect(page.getByText(/We detected/i)).toBeVisible();

    // Verify mapping table columns
    await expect(page.getByText("CSV Column")).toBeVisible();
    await expect(page.getByText("CertiFlow Field")).toBeVisible();
    await expect(page.getByText("Confidence")).toBeVisible();

    // Verify fields like Recipient Name and Email Address are mapped
    await expect(page.locator("span", { hasText: /^Recipient Name/ }).first()).toBeVisible();
    await expect(page.locator("span", { hasText: /^Email Address/ }).first()).toBeVisible();

    // Screenshot mapping step
    await page.screenshot({ path: `${ARTIFACT_DIR}/step1_mapping.png` });

    // 4. Click Validate Records -> Transition to Step 2 (Validation)
    const validateBtn = page.locator("#validate-records-btn");
    await expect(validateBtn).toBeEnabled();
    await validateBtn.click();

    // Wait for Step 2 Validation view
    await expect(page.getByRole("heading", { name: /Validation Results/i })).toBeVisible();

    // Verify Metric Cards: Total Rows, Valid, Errors
    await expect(page.getByText("Total Rows")).toBeVisible();
    await expect(page.locator("p", { hasText: /^Valid$/ })).toBeVisible();
    await expect(page.locator("p", { hasText: /^Errors$/ })).toBeVisible();

    // Verify error report or confirmation summary
    const confirmBtn = page.locator("#confirm-import-btn");
    await expect(confirmBtn).toBeVisible();
    await expect(confirmBtn).toBeEnabled();

    // Screenshot validation step
    await page.screenshot({ path: `${ARTIFACT_DIR}/step2_validation.png` });

    // Test back button to Mapping and forward again
    const backToMappingBtn = page.locator("#validation-back-btn");
    await expect(backToMappingBtn).toBeVisible();
    await backToMappingBtn.click();
    await expect(page.getByRole("heading", { name: /Map your columns/i })).toBeVisible();

    // Return to Validation
    await page.locator("#validate-records-btn").click();
    await expect(page.getByRole("heading", { name: /Validation Results/i })).toBeVisible();

    // 5. Confirm & Import Records -> Transition to Step 3 (Confirm)
    await page.locator("#confirm-import-btn").click();

    // Wait for Step 3 Completion screen
    await expect(page.getByRole("heading", { name: /Import Completed!/i })).toBeVisible();
    await expect(page.getByText(/Successfully imported/i)).toBeVisible();
    await expect(page.getByText(/Ready for batch issuance/i)).toBeVisible();

    // Verify action buttons
    const importAnotherBtn = page.locator("#import-another-btn");
    const launchIssuanceBtn = page.locator("#launch-issuance-btn");
    await expect(importAnotherBtn).toBeVisible();
    await expect(launchIssuanceBtn).toBeVisible();

    // Screenshot confirmation step
    await page.screenshot({ path: `${ARTIFACT_DIR}/step3_confirm.png` });

    // 6. Test Reset Flow ("Import Another File")
    await importAnotherBtn.click();

    // Wizard should return to Step 0
    await expect(page.getByText("Upload your recipient list")).toBeVisible();
    await expect(page.locator("#upload-analyze-btn")).toBeDisabled();

    // Screenshot reset state
    await page.screenshot({ path: `${ARTIFACT_DIR}/step0_reset.png` });
  });

  test("verifies unauthenticated user gets redirected to login and demo button navigates back", async ({ browser }) => {
    // Isolated context with NO tokens
    const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    const page = await context.newPage();

    // Navigate to protected imports route -> redirects to /login?redirect=%2Fapp%2Fimports
    await page.goto("/app/imports");
    await page.waitForLoadState("networkidle");

    // Verify redirected to login page with redirect param
    await expect(page).toHaveURL(/.*\/login\?redirect=%2Fapp%2Fimports/);
    await expect(page.getByRole("heading", { name: /Welcome back/i })).toBeVisible();

    // Screenshot login redirection
    await page.screenshot({ path: `${ARTIFACT_DIR}/login_redirect.png` });

    // Click demo mode button
    const demoBtn = page.getByText(/Or explore in Offline \/ Demo Mode/i);
    await expect(demoBtn).toBeVisible();
    await demoBtn.click();

    // Verify redirected back to /app/imports
    await expect(page.getByRole("heading", { name: /Import Center/i })).toBeVisible({ timeout: 15000 });

    await context.close();
  });
});
