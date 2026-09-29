"use client";

import { useState } from "react";
import { AlertTriangle, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import type { Certificate } from "@/types";

interface CertificateRevokeModalProps {
  certificate: Certificate | null;
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (id: string, reason: string) => Promise<void>;
  loading: boolean;
}

export function CertificateRevokeModal({
  certificate,
  isOpen,
  onClose,
  onConfirm,
  loading,
}: CertificateRevokeModalProps) {
  const [reason, setReason] = useState("");

  if (!isOpen || !certificate) return null;

  const handleRevoke = async (e: React.FormEvent) => {
    e.preventDefault();
    await onConfirm(certificate.id, reason || "Administrative revocation");
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl border border-[var(--color-border)] shadow-2xl max-w-md w-full overflow-hidden animate-in fade-in-50 zoom-in-95">
        <div className="p-6 space-y-4">
          <div className="w-12 h-12 rounded-2xl bg-red-100 flex items-center justify-center text-red-600">
            <AlertTriangle className="w-6 h-6" />
          </div>

          <div>
            <h2 className="text-[18px] font-bold text-[var(--color-text)]">Revoke Certificate</h2>
            <p className="text-[13px] text-[var(--color-text-secondary)] mt-1">
              Are you sure you want to revoke certificate{" "}
              <strong className="font-mono text-gray-900">{certificate.certificate_number || certificate.id}</strong>{" "}
              issued to <strong>{certificate.recipient_name}</strong>?
            </p>
          </div>

          <div className="p-3 bg-red-50 border border-red-200 rounded-xl text-[12px] text-red-700">
            This will invalidate public QR code verification and flag this credential as revoked in cryptographic registries.
          </div>

          <form onSubmit={handleRevoke} className="space-y-4 pt-1">
            <div>
              <label className="block text-[12px] font-semibold text-[var(--color-text)] mb-1.5">
                Revocation Reason
              </label>
              <textarea
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                rows={3}
                placeholder="e.g., Course requirement non-compliance or error in issuance"
                className="w-full px-3 py-2 rounded-xl border border-[var(--color-border)] text-[13px] bg-white focus:outline-none focus:border-red-500 transition-colors resize-none"
              />
            </div>

            <div className="flex items-center justify-end gap-2 pt-2">
              <Button type="button" variant="outline" onClick={onClose} disabled={loading}>
                Cancel
              </Button>
              <Button type="submit" loading={loading} className="bg-red-600 hover:bg-red-700 text-white">
                Confirm Revocation
              </Button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
