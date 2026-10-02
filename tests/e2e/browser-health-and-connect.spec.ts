import { test, expect } from "@playwright/test";
import path from "path";

test.describe("Browser Connectivity & Platform Validation", () => {
  test.setTimeout(90000);

  const ARTIFACT_DIR = "C:/Users/Atul/.gemini/antigravity-ide/brain/b270ac41-5078-4aeb-9804-1a78aed71f23";

  test("validates landing page, interactive demo, pricing, dashboard, templates, certificates and verification", async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 });

    // Step 1: Landing Page
    await page.goto("http://localhost:3000/");
    await page.waitForLoadState("networkidle");

    await expect(page).toHaveTitle(/CertiFlow/i);
    await expect(page.getByRole("heading", { name: /Create hundreds of personalized certificates/i })).toBeVisible();
    await page.screenshot({ path: path.join(ARTIFACT_DIR, "live_01_landing_hero.png") });

    // Step 2: Interactive Demo Section (directly below hero fold)
    const demoSection = page.locator("#demo");
    await expect(demoSection).toBeVisible();
    await demoSection.scrollIntoViewIfNeeded();
    await expect(page.getByRole("heading", { name: "Upload CSV" })).toBeVisible();
    await page.screenshot({ path: path.join(ARTIFACT_DIR, "live_02_interactive_demo.png") });

    // Step 3: Transparent Pricing Section with ₹1,999/mo and 15-capability matrix
    const pricingSection = page.locator("#pricing");
    await pricingSection.scrollIntoViewIfNeeded();
    await expect(page.getByText("₹1,999")).toBeVisible();
    await expect(page.getByText("Comprehensive Feature Matrix")).toBeVisible();
    await page.screenshot({ path: path.join(ARTIFACT_DIR, "live_03_pricing_matrix.png") });

    // Step 4: Enterprise Dashboard
    await page.addInitScript(() => {
      localStorage.setItem("certiflow_access_token", "test_jwt_session_token");
      localStorage.setItem("certiflow_demo_mode", "true");
      localStorage.setItem("certiflow_org_id", "org_default_01");
    });

    await page.goto("http://localhost:3000/app");
    await page.waitForLoadState("networkidle");

    // Assert dashboard elements
    await expect(page.getByRole("heading", { name: /Welcome back/i })).toBeVisible();
    await expect(page.getByText(/Total Certificates/i)).toBeVisible();
    await expect(page.getByText(/Issuance & Delivery Trend/i)).toBeVisible();
    await expect(page.getByText(/FastAPI: Connected/i)).toBeVisible();
    await page.screenshot({ path: path.join(ARTIFACT_DIR, "live_04_dashboard_overview.png") });

    // Step 5: Projects / Templates Studio
    await page.goto("http://localhost:3000/app/projects");
    await page.waitForLoadState("networkidle");
    await expect(page.getByText("AI Workshop 2026")).toBeVisible();
    await page.screenshot({ path: path.join(ARTIFACT_DIR, "live_05_projects_templates.png") });

    // Step 6: Certificate Vault
    await page.goto("http://localhost:3000/app/certificates");
    await page.waitForLoadState("networkidle");
    await expect(page.getByRole("heading", { name: "Certificate Vault" })).toBeVisible();
    await expect(page.getByText("Atul Kumar").first()).toBeVisible();
    await page.screenshot({ path: path.join(ARTIFACT_DIR, "live_06_certificate_vault.png") });

    // Step 7: Public Credential Verification Portal
    await page.goto("http://localhost:3000/verify/CERT-AF72K9");
    await page.waitForLoadState("networkidle");
    await expect(page.getByText(/Verified Authentic/i).first()).toBeVisible();
    await expect(page.getByRole("heading", { name: "Official Credential Verification" })).toBeVisible();
    await expect(page.getByText("Atul Kumar").first()).toBeVisible();
    await expect(page.getByText("AI Workshop 2026").first()).toBeVisible();
    await expect(page.getByText(/SHA-256 Signature/i)).toBeVisible();
    await expect(page.getByRole("button", { name: /Download Verified PDF/i })).toBeVisible();
    await page.screenshot({ path: path.join(ARTIFACT_DIR, "live_07_public_verification.png") });
  });
});
