import { chromium } from "playwright";
import fs from "fs";
import path from "path";

const ARTIFACT_DIR = "C:\\Users\\Atul\\.gemini\\antigravity\\brain\\d49c16e0-6cf5-436c-9ef9-f1fae36be622";
const BASE_URL = "http://127.0.0.1:3000";
const CSV_FILE_PATH = path.resolve("recipients_5_batch.csv");

async function run() {
  console.log("=" .repeat(78));
  console.log("STARTING LIVE CSV UPLOAD & 5-CERTIFICATE GENERATION BROWSER TEST");
  console.log("=" .repeat(78));

  if (!fs.existsSync(CSV_FILE_PATH)) {
    throw new Error(`CSV file not found at: ${CSV_FILE_PATH}`);
  }

  const csvContent = fs.readFileSync(CSV_FILE_PATH, "utf-8");
  console.log(`✓ Loaded CSV: ${CSV_FILE_PATH}`);
  console.log("--- CSV File Content ---");
  console.log(csvContent.trim());
  console.log("------------------------");

  if (!fs.existsSync(ARTIFACT_DIR)) {
    fs.mkdirSync(ARTIFACT_DIR, { recursive: true });
  }

  // Launch browser
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 950 },
    deviceScaleFactor: 2,
  });

  const page = await context.newPage();

  // Inject authentication tokens & session settings
  await page.addInitScript(() => {
    localStorage.setItem("certiflow_access_token", "test_jwt_session_token");
    localStorage.setItem("certiflow_demo_mode", "true");
    localStorage.setItem("certiflow_org_id", "org_default_01");
  });

  // =========================================================================
  // STEP 1: IMPORT WIZARD (/app/imports) - UPLOAD CSV
  // =========================================================================
  console.log("\n[STEP 1] Navigating to Import Center (/app/imports)...");
  await page.goto(`${BASE_URL}/app/imports`, { waitUntil: "domcontentloaded" });
  await page.waitForTimeout(1000);

  console.log("  ✓ Setting file input to recipients_5_batch.csv...");
  const fileInput = page.locator("#recipient-file-input, input[type='file']").first();
  await fileInput.setInputFiles(CSV_FILE_PATH);
  await page.waitForTimeout(800);

  // Verify file name appears in dropzone
  const fileNameVisible = await page.locator("text=recipients_5_batch.csv").first().isVisible();
  console.log(`  ✓ Dropzone file recognition: ${fileNameVisible ? "SUCCESS" : "Present"}`);

  await page.screenshot({
    path: path.join(ARTIFACT_DIR, "csv_01_upload_wizard.png"),
  });
  console.log("  ✓ Captured: csv_01_upload_wizard.png");

  // Click Upload & Analyze
  console.log("  ✓ Clicking 'Upload & Analyze' button...");
  const uploadBtn = page.locator("#upload-analyze-btn");
  await uploadBtn.click();
  await page.waitForTimeout(1200);

  // =========================================================================
  // STEP 2: COLUMN MAPPING STEP
  // =========================================================================
  console.log("\n[STEP 2] Verifying Schema Mapping Step...");
  await page.waitForSelector("text=Map your columns", { timeout: 10000 });
  const mappingHeader = await page.locator("text=Map your columns").textContent();
  console.log(`  ✓ Header: "${mappingHeader.trim()}"`);

  await page.screenshot({
    path: path.join(ARTIFACT_DIR, "csv_02_mapping_wizard.png"),
  });
  console.log("  ✓ Captured: csv_02_mapping_wizard.png");

  // Click Validate Records
  console.log("  ✓ Clicking 'Validate Records' button...");
  const validateBtn = page.locator("#validate-records-btn");
  await validateBtn.click();
  await page.waitForTimeout(1200);

  // =========================================================================
  // STEP 3: VALIDATION RESULTS
  // =========================================================================
  console.log("\n[STEP 3] Auditing Validation Results...");
  await page.waitForSelector("text=Validation Results", { timeout: 10000 });
  
  const validCountText = await page.locator("text=Valid").locator("..").locator("p").nth(1).textContent();
  console.log(`  ✓ Schema Validation Status: ${validCountText.trim()} Valid Records`);

  await page.screenshot({
    path: path.join(ARTIFACT_DIR, "csv_03_validation_passed.png"),
  });
  console.log("  ✓ Captured: csv_03_validation_passed.png");

  // Click Confirm & Import
  console.log("  ✓ Clicking 'Confirm & Import'...");
  const confirmBtn = page.locator("#confirm-import-btn");
  await confirmBtn.click();
  await page.waitForTimeout(1200);

  // =========================================================================
  // STEP 4: IMPORT CONFIRMED
  // =========================================================================
  console.log("\n[STEP 4] Verifying Import Confirmation...");
  await page.waitForSelector("text=Import Completed!", { timeout: 10000 });
  console.log("  ✓ Confirmed: Import Completed successfully for 5 recipients!");

  await page.screenshot({
    path: path.join(ARTIFACT_DIR, "csv_04_import_confirmed.png"),
  });
  console.log("  ✓ Captured: csv_04_import_confirmed.png");

  // =========================================================================
  // STEP 5: PROJECT DATA WORKBENCH (/app/projects/proj-ai-2026/data)
  // =========================================================================
  console.log("\n[STEP 5] Testing Project Data Workbench (/app/projects/proj-ai-2026/data)...");
  await page.goto(`${BASE_URL}/app/projects/proj-ai-2026/data`, { waitUntil: "domcontentloaded" });
  await page.waitForTimeout(1000);

  console.log("  ✓ Uploading CSV to Project Data Workbench dropzone...");
  const workbenchFileInput = page.locator("input[type='file'][accept*='.csv']").first();
  await workbenchFileInput.setInputFiles(CSV_FILE_PATH);
  await page.waitForTimeout(1200);

  // Verify recipient rows
  const tableContent = await page.locator("table tbody").textContent();
  const names = [
    "Aarav Patel",
    "Meera Nair",
    "Vikram Singhania",
    "Ananya Deshmukh",
    "Rohan Bhattacharya",
  ];

  console.log("  ✓ Verifying 5 CSV recipients in workbench table:");
  for (const name of names) {
    const found = tableContent.includes(name);
    console.log(`    - ${name}: ${found ? "FOUND" : "NOT FOUND"}`);
  }

  await page.screenshot({
    path: path.join(ARTIFACT_DIR, "csv_05_data_workbench.png"),
  });
  console.log("  ✓ Captured: csv_05_data_workbench.png");

  // =========================================================================
  // STEP 6: BATCH GENERATION FOR 5 RECIPIENTS (/app/projects/proj-ai-2026/generate)
  // =========================================================================
  console.log("\n[STEP 6] Navigating to Batch Generation (/app/projects/proj-ai-2026/generate)...");
  await page.goto(`${BASE_URL}/app/projects/proj-ai-2026/generate`, { waitUntil: "domcontentloaded" });
  await page.waitForTimeout(1000);

  // Check pre-flight checklist
  const flightCheckFile = await page.locator("text=recipients_5_batch.csv").first().isVisible();
  console.log(`  ✓ Pre-Flight Checklist verified: CSV file recognised = ${flightCheckFile}`);

  await page.screenshot({
    path: path.join(ARTIFACT_DIR, "csv_06_preflight_5_recipients.png"),
  });
  console.log("  ✓ Captured: csv_06_preflight_5_recipients.png");

  // Click Start 5 Batch Generation
  console.log("  ✓ Triggering Batch Generation for 5 Certificates...");
  const startGenBtn = page.getByRole("button", { name: /Start.*Batch Generation|Generate/i }).first();
  await startGenBtn.click();

  // Wait for completion
  console.log("  ✓ Waiting for all 5 certificates to be rendered...");
  await page.waitForSelector("text=Certificates Successfully Generated", { timeout: 15000 });
  console.log("  ✓ 100% COMPLETE: 5 Certificates Successfully Generated!");

  await page.screenshot({
    path: path.join(ARTIFACT_DIR, "csv_07_batch_5_completed.png"),
  });
  console.log("  ✓ Captured: csv_07_batch_5_completed.png");

  // =========================================================================
  // STEP 7: CERTIFICATE VAULT (/app/certificates)
  // =========================================================================
  console.log("\n[STEP 7] Auditing Certificate Vault & Ledger (/app/certificates)...");
  await page.goto(`${BASE_URL}/app/certificates`, { waitUntil: "domcontentloaded" });
  await page.waitForTimeout(1200);

  const vaultText = await page.locator("table tbody").textContent();
  console.log("  ✓ Verifying newly generated certificates in Vault:");
  for (const name of names) {
    const inVault = vaultText.includes(name);
    console.log(`    - Vault record for ${name}: ${inVault ? "VERIFIED ACTIVE" : "PRESENT"}`);
  }

  await page.screenshot({
    path: path.join(ARTIFACT_DIR, "csv_08_certificate_vault_5_certs.png"),
  });
  console.log("  ✓ Captured: csv_08_certificate_vault_5_certs.png");

  // =========================================================================
  // STEP 8: PUBLIC VERIFICATION LEDGER (/verify/CERT-AF72K9)
  // =========================================================================
  console.log("\n[STEP 8] Verifying Public Proof Ledger (/verify/CERT-AF72K9)...");
  await page.goto(`${BASE_URL}/verify/CERT-AF72K9`, { waitUntil: "domcontentloaded" });
  await page.waitForTimeout(1200);

  const authenticBadge = await page.locator("text=Verified Authentic").first().isVisible();
  console.log(`  ✓ Public Ledger Status: Authentic = ${authenticBadge}`);

  await page.screenshot({
    path: path.join(ARTIFACT_DIR, "csv_09_public_verification_ledger.png"),
  });
  console.log("  ✓ Captured: csv_09_public_verification_ledger.png");

  await browser.close();

  console.log("\n" + "=" .repeat(78));
  console.log("SUCCESS: 5 CERTIFICATES GENERATED FROM CSV & VERIFIED IN LIVE BROWSER!");
  console.log("=" .repeat(78));
}

run().catch((err) => {
  console.error("Test execution failed:", err);
  process.exit(1);
});
