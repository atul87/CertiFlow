"use client";

import Link from "next/link";
import { Download, ExternalLink, RotateCcw, Award } from "lucide-react";
import { CertificateStatusBadge } from "./CertificateStatusBadge";
import type { Certificate } from "@/types";

interface CertificateTableProps {
  certificates: Certificate[];
  selected: Set<string>;
  onToggleSelect: (id: string) => void;
  onToggleSelectAll: () => void;
  onRevoke: (cert: Certificate) => void;
  onRestore: (cert: Certificate) => void;
  onSelectRow?: (cert: Certificate) => void;
}

export function CertificateTable({
  certificates,
  selected,
  onToggleSelect,
  onToggleSelectAll,
  onRevoke,
  onRestore,
  onSelectRow,
}: CertificateTableProps) {
  const allSelected = certificates.length > 0 && selected.size === certificates.length;

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-[13px]">
        <thead>
          <tr className="border-b border-[var(--color-border)] bg-gray-50/50 text-[11px] font-bold uppercase tracking-wider text-[var(--color-text-tertiary)]">
            <th className="py-3 px-4 w-10">
              <input
                type="checkbox"
                checked={allSelected}
                onChange={onToggleSelectAll}
                className="rounded border-gray-300 text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
              />
            </th>
            <th className="py-3 px-4">Certificate ID</th>
            <th className="py-3 px-4">Recipient</th>
            <th className="py-3 px-4">Program / Course</th>
            <th className="py-3 px-4">Issue Date</th>
            <th className="py-3 px-4">Status</th>
            <th className="py-3 px-4 text-right">Actions</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-[var(--color-border)] bg-white">
          {certificates.map((cert) => {
            const isChecked = selected.has(cert.id);

            return (
              <tr
                key={cert.id}
                onClick={() => onSelectRow?.(cert)}
                className={`hover:bg-gray-50/60 transition-colors cursor-pointer ${
                  isChecked ? "bg-indigo-50/30" : ""
                }`}
              >
                <td className="py-3 px-4" onClick={(e) => e.stopPropagation()}>
                  <input
                    type="checkbox"
                    checked={isChecked}
                    onChange={() => onToggleSelect(cert.id)}
                    className="rounded border-gray-300 text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
                  />
                </td>
                <td className="py-3 px-4">
                  <Link
                    href={`/app/certificates/${cert.id}`}
                    onClick={(e) => e.stopPropagation()}
                    className="font-mono font-semibold text-[var(--color-primary)] hover:underline flex items-center gap-1.5"
                  >
                    <Award className="w-3.5 h-3.5 text-[var(--color-primary)] shrink-0" />
                    {cert.certificate_number || cert.id.slice(0, 12)}
                  </Link>
                </td>
                <td className="py-3 px-4">
                  <div>
                    <p className="font-semibold text-[var(--color-text)]">{cert.recipient_name}</p>
                    <p className="text-[11px] text-[var(--color-text-tertiary)]">{cert.recipient_email}</p>
                  </div>
                </td>
                <td className="py-3 px-4 text-[var(--color-text-secondary)]">
                  {cert.program_name || "—"}
                </td>
                <td className="py-3 px-4 text-[var(--color-text-tertiary)] whitespace-nowrap">
                  {cert.issue_date || new Date(cert.created_at).toLocaleDateString()}
                </td>
                <td className="py-3 px-4">
                  <CertificateStatusBadge status={cert.status} />
                </td>
                <td className="py-3 px-4 text-right" onClick={(e) => e.stopPropagation()}>
                  <div className="flex items-center justify-end gap-1">
                    <Link
                      href={`/verify/${cert.id}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      title="Verify publicly"
                      className="p-1.5 rounded-lg text-gray-400 hover:text-gray-700 hover:bg-gray-100 transition-colors"
                    >
                      <ExternalLink className="w-3.5 h-3.5" />
                    </Link>

                    {cert.status === "active" ? (
                      <button
                        onClick={() => onRevoke(cert)}
                        title="Revoke Certificate"
                        className="p-1.5 rounded-lg text-red-500 hover:bg-red-50 transition-colors"
                      >
                        <RotateCcw className="w-3.5 h-3.5" />
                      </button>
                    ) : (
                      <button
                        onClick={() => onRestore(cert)}
                        title="Restore Certificate"
                        className="p-1.5 rounded-lg text-emerald-600 hover:bg-emerald-50 transition-colors"
                      >
                        <Award className="w-3.5 h-3.5" />
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
