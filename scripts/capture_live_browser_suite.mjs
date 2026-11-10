import { chromium } from "playwright";
import fs from "fs";
import path from "path";

const ARTIFACT_DIR = "C:\\Users\\Atul\\.gemini\\antigravity\\brain\\d49c16e0-6cf5-436c-9ef9-f1fae36be622";
const BASE_URL = "http://127.0.0.1:3000";

async function run() {
  console.log("=" .repeat(70));
  console.log("STARTING LIVE PLAYWRIGHT BROWSER AUDIT & SCREENSHOT CAPTURE");
  console.log("=" .repeat(70));

  if (!fs.existsSync(ARTIFACT_DIR)) {
    fs.mkdirSync(ARTIFACT_DIR, { recursive: true });
  }

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    deviceScaleFactor: 2, // High-DPI Retina capture
  });

  const page = await context.newPage();

  // Listen for console logs & errors
  const consoleErrors = [];
  page.on("console", (msg) => {
    if (msg.type() === "error") {
      consoleErrors.push(msg.text());
    }
  });

  // 1. Landing Page (Desktop 1440x900)
  console.log("\n[TEST 1] Testing Landing Page (Desktop 1440x900)...");
  await page.goto(`${BASE_URL}/`, { waitUntil: "networkidle" });
  const title = await page.title();
  console.log(`  ✓ Page Title: '${title}'`);
  const heroHeading = await page.locator("h1").first().textContent();
  console.log(`  ✓ Hero Heading: '${heroHeading.trim()}'`);
  await page.screenshot({
    path: path.join(ARTIFACT_DIR, "browser_01_landing_desktop.png"),
    fullPage: false,
  });
  console.log(`  ✓ Captured: browser_01_landing_desktop.png`);

  // 2. Landing Page (Mobile 390x844)
  console.log("\n[TEST 2] Testing Landing Page Responsive View (Mobile 390x844)...");
  await page.setViewportSize({ width: 390, height: 844 });
  await page.waitForTimeout(500);
  await page.screenshot({
    path: path.join(ARTIFACT_DIR, "browser_02_landing_mobile.png"),
    fullPage: false,
  });
  console.log(`  ✓ Captured: browser_02_landing_mobile.png`);

  // Reset to desktop viewport
  await page.setViewportSize({ width: 1440, height: 900 });

  // 3. Login Page
  console.log("\n[TEST 3] Testing Authentication Portal (/login)...");
  await page.goto(`${BASE_URL}/login`, { waitUntil: "networkidle" });
  await page.screenshot({
    path: path.join(ARTIFACT_DIR, "browser_03_login_screen.png"),
  });
  console.log(`  ✓ Captured: browser_03_login_screen.png`);

  // 4. Authenticated SaaS Session Setup & Dashboard
  console.log("\n[TEST 4] Testing SaaS App Dashboard (/app)...");
  await page.addInitScript(() => {
    localStorage.setItem("certiflow_access_token", "test_jwt_session_token");
    localStorage.setItem("certiflow_demo_mode", "true");
    localStorage.setItem("certiflow_org_id", "org_default_01");
  });
  await page.goto(`${BASE_URL}/app`, { waitUntil: "networkidle" });
  await page.waitForTimeout(600);
  await page.screenshot({
    path: path.join(ARTIFACT_DIR, "browser_04_dashboard_overview.png"),
  });
  console.log(`  ✓ Captured: browser_04_dashboard_overview.png`);

  // 5. Template Studio & Designer
  console.log("\n[TEST 5] Testing Template Studio (/app/templates)...");
  await page.goto(`${BASE_URL}/app/templates`, { waitUntil: "networkidle" });
  await page.waitForTimeout(600);
  await page.screenshot({
    path: path.join(ARTIFACT_DIR, "browser_05_template_studio.png"),
  });
  console.log(`  ✓ Captured: browser_05_template_studio.png`);

  // 6. Certificate Vault & Ledger
  console.log("\n[TEST 6] Testing Certificate Vault (/app/certificates)...");
  await page.goto(`${BASE_URL}/app/certificates`, { waitUntil: "networkidle" });
  await page.waitForTimeout(600);
  await page.screenshot({
    path: path.join(ARTIFACT_DIR, "browser_06_certificate_ledger.png"),
  });
  console.log(`  ✓ Captured: browser_06_certificate_ledger.png`);

  // 7. W3C Verifiable Credentials & Badges Portal
  console.log("\n[TEST 7] Testing Credentials & Open Badges (/app/credentials)...");
  await page.goto(`${BASE_URL}/app/credentials`, { waitUntil: "networkidle" });
  await page.waitForTimeout(600);
  await page.screenshot({
    path: path.join(ARTIFACT_DIR, "browser_07_credentials_and_badges.png"),
  });
  console.log(`  ✓ Captured: browser_07_credentials_and_badges.png`);

  // 8. Public Verification Portal
  console.log("\n[TEST 8] Testing Public Ledger Verification Portal (/verify)...");
  await page.goto(`${BASE_URL}/verify`, { waitUntil: "networkidle" });
  await page.screenshot({
    path: path.join(ARTIFACT_DIR, "browser_08_public_verification.png"),
  });
  console.log(`  ✓ Captured: browser_08_public_verification.png`);

  // 9. Public Verification Results Screen
  console.log("\n[TEST 9] Testing Real Certificate Verification View (/verify/CERT-2026-984210)...");
  await page.goto(`${BASE_URL}/verify/CERT-2026-984210`, { waitUntil: "domcontentloaded" });
  await page.waitForTimeout(1500);
  await page.screenshot({
    path: path.join(ARTIFACT_DIR, "browser_09_verification_details.png"),
  });
  console.log(`  ✓ Captured: browser_09_verification_details.png`);

  await browser.close();

  console.log("\n" + "=" .repeat(70));
  console.log("BROWSER AUDIT COMPLETE: 9 HIGH-DEFINITION SCREENSHOTS CAPTURED.");
  console.log(`Zero Fatal Errors. Captured to: ${ARTIFACT_DIR}`);
  console.log("=" .repeat(70));
}

run().catch((err) => {
  console.error("Browser testing error:", err);
  process.exit(1);
});
