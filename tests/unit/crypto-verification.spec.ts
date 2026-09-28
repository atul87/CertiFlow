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

  test("generates deterministic 64-character SHA-256 hex signature", () => {
    const sig1 = generateCertificateSignature(samplePayload);
    const sig2 = generateCertificateSignature(samplePayload);

    expect(sig1).toHaveLength(64);
    expect(sig1).toBe(sig2); // Deterministic
    expect(/^[a-f0-9]{64}$/.test(sig1)).toBe(true);
  });

  test("successfully validates an authentic certificate signature", () => {
    const signature = generateCertificateSignature(samplePayload);
    const result = verifyCertificateSignature(samplePayload, signature);

    expect(result.isValid).toBe(true);
    expect(result.computedHash).toBe(signature);
  });

  test("detects tampering when recipient name is modified", () => {
    const originalSignature = generateCertificateSignature(samplePayload);
    const tamperedPayload = {
      ...samplePayload,
      name: "Atul Kumar Fraudulent",
    };

    const result = verifyCertificateSignature(tamperedPayload, originalSignature);
    expect(result.isValid).toBe(false);
  });

  test("detects tampering when course title is modified", () => {
    const originalSignature = generateCertificateSignature(samplePayload);
    const tamperedPayload = {
      ...samplePayload,
      course: "Doctor of Philosophy",
    };

    const result = verifyCertificateSignature(tamperedPayload, originalSignature);
    expect(result.isValid).toBe(false);
  });

  test("detects tampering when issue date is modified", () => {
    const originalSignature = generateCertificateSignature(samplePayload);
    const tamperedPayload = {
      ...samplePayload,
      date: "September 29, 2026",
    };

    const result = verifyCertificateSignature(tamperedPayload, originalSignature);
    expect(result.isValid).toBe(false);
  });

  test("detects tampering when certificate ID is manipulated", () => {
    const originalSignature = generateCertificateSignature(samplePayload);
    const tamperedPayload = {
      ...samplePayload,
      id: "CERT-AF72K0",
    };

    const result = verifyCertificateSignature(tamperedPayload, originalSignature);
    expect(result.isValid).toBe(false);
  });

  test("rejects verification when using mismatched secret key", () => {
    const signature = generateCertificateSignature(samplePayload, "issuer_secret_A");
    const result = verifyCertificateSignature(samplePayload, signature, "issuer_secret_B");

    expect(result.isValid).toBe(false);
  });
});
