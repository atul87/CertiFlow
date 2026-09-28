import { createHash } from "crypto";

export interface CertificateSignaturePayload {
  id: string;
  name: string;
  course: string;
  date: string;
  issuerId?: string;
}

/**
 * Computes deterministic SHA-256 HMAC digital signature for a certificate credential
 */
export function generateCertificateSignature(
  payload: CertificateSignaturePayload,
  secretKey: string = "certiflow_default_issuer_secret_2026"
): string {
  const normalizedString = [
    payload.id.trim(),
    payload.name.trim(),
    payload.course.trim(),
    payload.date.trim(),
    payload.issuerId || "org-certiflow",
    secretKey,
  ].join("|");

  return createHash("sha256").update(normalizedString, "utf8").digest("hex");
}

/**
 * Validates whether a provided digital signature matches the claimed payload
 */
export function verifyCertificateSignature(
  payload: CertificateSignaturePayload,
  signature: string,
  secretKey: string = "certiflow_default_issuer_secret_2026"
): { isValid: boolean; computedHash: string } {
  const computedHash = generateCertificateSignature(payload, secretKey);
  const isValid = computedHash.toLowerCase() === signature.trim().toLowerCase();

  return {
    isValid,
    computedHash,
  };
}
