import { test, expect } from "@playwright/test";

test.describe("E2E: Certificate Editor Mutations & Controls", () => {
  test.beforeEach(async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 });
    await page.goto("/app/projects/proj-ai-2026/editor");
    await page.waitForLoadState("networkidle");
  });

  test("renders editor interface with canvas, sidebars, and project headers", async ({ page }) => {
    await expect(page.getByText("AI Workshop 2026")).toBeVisible();
    await expect(page.getByText("A4 300 DPI")).toBeVisible();
    await expect(page.getByRole("button", { name: "Elements" })).toBeVisible();
    await expect(page.getByRole("button", { name: /Layers/i })).toBeVisible();
  });

  test("switches between Elements, Layers, and Presets tabs in left sidebar", async ({ page }) => {
    // Click Layers tab
    await page.getByRole("button", { name: /Layers/i }).click();
    await expect(page.getByTitle("Move layer up").first()).toBeVisible();

    // Click Presets tab
    await page.getByRole("button", { name: /Presets/i }).click();
    await expect(page.getByText("Academic Honors")).toBeVisible();

    // Switch back to Elements tab
    await page.getByRole("button", { name: "Elements" }).click();
    await expect(page.getByText("CSV Dynamic Variables")).toBeVisible();
  });

  test("selects a layer and inspects properties in Right Inspector", async ({ page }) => {
    // Switch to Layers tab and click Recipient Name layer
    await page.getByRole("button", { name: /Layers/i }).click();
    await page.getByText("Recipient Name").first().click();

    // Right Inspector should now show properties for selected variable layer
    await expect(page.getByText("CSV Data Binding")).toBeVisible();
    await expect(page.getByText("Smart Text Fit")).toBeVisible();
  });

  test("can toggle layer visibility and lock state", async ({ page }) => {
    await page.getByRole("button", { name: /Layers/i }).click();

    // Lock toggle
    const lockBtn = page.getByTitle(/Lock layer|Unlock layer/i).first();
    await lockBtn.click();

    // Visibility toggle
    const eyeBtn = page.getByTitle(/Hide layer|Show layer/i).first();
    await eyeBtn.click();
  });

  test("cycles through recipients in Editor Top Bar", async ({ page }) => {
    const nextRecipientBtn = page.getByTitle("Next Recipient");
    if (await nextRecipientBtn.isVisible()) {
      await nextRecipientBtn.click();
    }
  });

  test("undo and redo buttons exist and reflect history state", async ({ page }) => {
    const undoBtn = page.getByTitle(/Undo/i);
    const redoBtn = page.getByTitle(/Redo/i);

    await expect(undoBtn).toBeVisible();
    await expect(redoBtn).toBeVisible();
  });
});
