import { test, expect } from "@playwright/test";
import {
  generateCertificateSignature,
  verifyCertificateSignature,
} from "../../src/lib/crypto-verification";

test.describe("Unit: Cryptographic Verification Engine", () => {
  const samplePayload = {
    id: "CERT-AF72K9",
    name: "Atul Kumar",
    course: "Executive AI & Cloud Architecture",
    date: "September 28, 2026",
    issuerId: "org-stanford-ai",
  };
  const testSecret = "unit_test_issuer_secret_key_12345";

  test("generates deterministic 64-character SHA-256 hex signature", async () => {
    const sig1 = await generateCertificateSignature(samplePayload, testSecret);
    const sig2 = await generateCertificateSignature(samplePayload, testSecret);

    expect(sig1).toHaveLength(64);
    expect(sig1).toBe(sig2); // Deterministic
    expect(/^[a-f0-9]{64}$/.test(sig1)).toBe(true);
  });

  test("successfully validates an authentic certificate signature", async () => {
    const signature = await generateCertificateSignature(samplePayload, testSecret);
    const result = await verifyCertificateSignature(samplePayload, signature, testSecret);

    expect(result.isValid).toBe(true);
    expect(result.computedHash).toBe(signature);
  });

  test("detects tampering when recipient name is modified", async () => {
    const originalSignature = await generateCertificateSignature(samplePayload, testSecret);
    const tamperedPayload = {
      ...samplePayload,
      name: "Atul Kumar Fraudulent",
    };

    const result = await verifyCertificateSignature(tamperedPayload, originalSignature, testSecret);
    expect(result.isValid).toBe(false);
  });

  test("detects tampering when course title is modified", async () => {
    const originalSignature = await generateCertificateSignature(samplePayload, testSecret);
    const tamperedPayload = {
      ...samplePayload,
      course: "Doctor of Philosophy",
    };

    const result = await verifyCertificateSignature(tamperedPayload, originalSignature, testSecret);
    expect(result.isValid).toBe(false);
  });

  test("detects tampering when issue date is modified", async () => {
    const originalSignature = await generateCertificateSignature(samplePayload, testSecret);
    const tamperedPayload = {
      ...samplePayload,
      date: "September 29, 2026",
    };

    const result = await verifyCertificateSignature(tamperedPayload, originalSignature, testSecret);
    expect(result.isValid).toBe(false);
  });

  test("detects tampering when certificate ID is manipulated", async () => {
    const originalSignature = await generateCertificateSignature(samplePayload, testSecret);
    const tamperedPayload = {
      ...samplePayload,
      id: "CERT-AF72K0",
    };

    const result = await verifyCertificateSignature(tamperedPayload, originalSignature, testSecret);
    expect(result.isValid).toBe(false);
  });

  test("rejects verification when using mismatched secret key", async () => {
    const signature = await generateCertificateSignature(samplePayload, "issuer_secret_A");
    const result = await verifyCertificateSignature(samplePayload, signature, "issuer_secret_B");

    expect(result.isValid).toBe(false);
  });

  test("throws error if secret key is missing", async () => {
    await expect(generateCertificateSignature(samplePayload, "")).rejects.toThrow();
    await expect(verifyCertificateSignature(samplePayload, "sig", "")).rejects.toThrow();
  });
});
