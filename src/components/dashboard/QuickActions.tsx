"use client";

import Link from "next/link";
import { FileText, Upload, Zap, ShieldCheck, ArrowRight } from "lucide-react";

export function QuickActions() {
  const actions = [
    {
      title: "Design Template",
      description: "Visual canvas with drag-and-drop dynamic tags",
      href: "/app/templates?create=1",
      icon: FileText,
      color: "text-blue-600",
      bg: "bg-blue-50",
      hoverBorder: "hover:border-blue-200",
    },
    {
      title: "Import Recipients",
      description: "Upload CSV/XLSX with smart AI column mapping",
      href: "/app/imports",
      icon: Upload,
      color: "text-emerald-600",
      bg: "bg-emerald-50",
      hoverBorder: "hover:border-emerald-200",
    },
    {
      title: "Run Batch Issuance",
      description: "Generate and distribute signed certificates",
      href: "/app/issuance?create=1",
      icon: Zap,
      color: "text-violet-600",
      bg: "bg-violet-50",
      hoverBorder: "hover:border-violet-200",
    },
    {
      title: "Verify Public Credential",
      description: "Cryptographic SHA-256 and QR code proof audit",
      href: "/verify/demo",
      icon: ShieldCheck,
      color: "text-amber-600",
      bg: "bg-amber-50",
      hoverBorder: "hover:border-amber-200",
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {actions.map((act) => (
        <Link
          key={act.title}
          href={act.href}
          className={`bg-white rounded-2xl border border-[var(--color-border)] p-5 transition-all duration-150 shadow-xs hover:shadow-md ${act.hoverBorder} group block`}
        >
          <div className="flex items-center justify-between mb-3">
            <div className={`w-10 h-10 rounded-xl ${act.bg} flex items-center justify-center transition-transform group-hover:scale-105`}>
              <act.icon className={`w-5 h-5 ${act.color}`} />
            </div>
            <ArrowRight className="w-4 h-4 text-gray-300 group-hover:text-[var(--color-primary)] group-hover:translate-x-0.5 transition-all" />
          </div>
          <h4 className="text-[14px] font-bold text-[var(--color-text)] group-hover:text-[var(--color-primary)] transition-colors">
            {act.title}
          </h4>
          <p className="text-[12px] text-[var(--color-text-secondary)] mt-1 line-clamp-2">
            {act.description}
          </p>
        </Link>
      ))}
    </div>
  );
}
