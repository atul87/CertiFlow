import { test, expect } from "@playwright/test";
import * as fs from "fs";
import * as path from "path";

test.describe("Security: XSS, Input Sanitization & Secret Leak Prevention", () => {
  test("escapes script tags and prevents DOM XSS injection on preview page", async ({ page }) => {
    // Listen for unexpected alert dialogs that would indicate script execution
    let alertTriggered = false;
    page.on("dialog", async (dialog) => {
      alertTriggered = true;
      await dialog.dismiss();
    });

    await page.goto("/verify/%3Cscript%3Ealert(1)%3C%2Fscript%3E");
    await page.waitForLoadState("domcontentloaded");

    // Ensure raw <script> does not execute and alert was not fired
    expect(alertTriggered).toBe(false);

    // Verify rendered content is safe text rather than raw executable HTML
    const content = await page.content();
    expect(content).not.toContain("<script>alert(1)</script>");
  });

  test("escapes img onerror XSS payloads in certificate verification URL", async ({ page }) => {
    let alertTriggered = false;
    page.on("dialog", async (dialog) => {
      alertTriggered = true;
      await dialog.dismiss();
    });

    await page.goto('/verify/%3Cimg%20src=x%20onerror=alert(1)%3E');
    await page.waitForLoadState("domcontentloaded");

    expect(alertTriggered).toBe(false);
  });

  test("handles arbitrary non-existent or tampered certificate IDs gracefully", async ({ page }) => {
    await page.goto("/verify/TAMPERED-FAKE-ID-99999");
    await page.waitForLoadState("domcontentloaded");

    // Page must load safely without 500 error or crash
    await expect(page.getByText("Public Ledger Active")).toBeVisible();
    await expect(page.getByText("TAMPERED-FAKE-ID-99999")).toBeVisible();
  });

  test("scans production source code for accidental client-side secret/private key leaks", () => {
    // Scan all client-facing files in src/
    const srcDir = path.resolve(process.cwd(), "src");

    const sensitivePatterns = [
      /sk_live_[0-9a-zA-Z]{24,}/i,
      /ghp_[0-9a-zA-Z]{36}/i,
      /AIzaSy[0-9A-Za-z-_]{33}/i,
      /-----BEGIN RSA PRIVATE KEY-----/i,
      /-----BEGIN PRIVATE KEY-----/i,
      /aws_secret_access_key/i,
    ];

    function scanDirectory(dir: string) {
      const entries = fs.readdirSync(dir, { withFileTypes: true });
      for (const entry of entries) {
        const fullPath = path.join(dir, entry.name);
        if (entry.isDirectory()) {
          scanDirectory(fullPath);
        } else if (/\.(tsx|ts|js|jsx|json)$/.test(entry.name)) {
          const content = fs.readFileSync(fullPath, "utf-8");
          for (const pattern of sensitivePatterns) {
            const match = pattern.test(content);
            expect(match).toBe(false);
          }
        }
      }
    }

    scanDirectory(srcDir);
  });
});
