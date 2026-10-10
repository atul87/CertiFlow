export interface CertificateSignaturePayload {
  id: string;
  name: string;
  course: string;
  date: string;
  issuerId?: string;
}

/**
 * Computes deterministic SHA-256 digital signature for a certificate credential
 * using the standard Web Crypto API (browser and edge safe, zero Node.js polyfill bloat).
 */
export async function generateCertificateSignature(
  payload: CertificateSignaturePayload,
  secretKey: string
): Promise<string> {
  if (!secretKey) {
    throw new Error("Secret key is required for certificate signature generation");
  }

  const normalizedString = [
    payload.id.trim(),
    payload.name.trim(),
    payload.course.trim(),
    payload.date.trim(),
    payload.issuerId || "org-certiflow",
    secretKey,
  ].join("|");

  const msgUint8 = new TextEncoder().encode(normalizedString);
  const hashBuffer = await crypto.subtle.digest("SHA-256", msgUint8);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map((b) => b.toString(16).padStart(2, "0")).join("");
}

/**
 * Validates whether a provided digital signature matches the claimed payload
 */
export async function verifyCertificateSignature(
  payload: CertificateSignaturePayload,
  signature: string,
  secretKey: string
): Promise<{ isValid: boolean; computedHash: string }> {
  if (!secretKey) {
    throw new Error("Secret key is required for certificate signature verification");
  }

  const computedHash = await generateCertificateSignature(payload, secretKey);
  const isValid = computedHash.toLowerCase() === signature.trim().toLowerCase();

  return {
    isValid,
    computedHash,
  };
}
