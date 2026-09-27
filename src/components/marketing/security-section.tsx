"use client";

import { ShieldCheck, Lock, HardDrive, CheckCircle2 } from "lucide-react";

const privacyPillars = [
  {
    icon: Lock,
    title: "Private projects",
    description: "Control who can access your certificates. Keep templates, recipient databases, and issued credentials private to your organization.",
  },
  {
    icon: ShieldCheck,
    title: "Secure files",
    description: "Protect templates, data, and generated documents with end-to-end encrypted storage and strict tenant separation.",
  },
  {
    icon: HardDrive,
    title: "Flexible processing",
    description: "Generate documents locally in your browser memory when privacy is the highest priority, without sending CSV rosters to cloud servers.",
  },
];

export function SecuritySection() {
  return (
    <section className="section-padding bg-[#FAFAF8] border-t border-[var(--color-border)]">
      <div className="container-marketing">
        {/* Section Header */}
        <div className="max-w-2xl mx-auto text-center mb-16">
          <p className="text-[13px] font-semibold uppercase tracking-[0.15em] text-[var(--color-primary)] mb-3">
            Data Governance
          </p>
          <h2 className="text-section text-[var(--color-text)] mb-3">
            Built with data privacy in mind.
          </h2>
          <p className="text-body-lg text-[var(--color-text-secondary)]">
            Your participant spreadsheets and intellectual property remain strictly yours.
          </p>
        </div>

        {/* 3 Privacy Pillars */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          {privacyPillars.map((p) => (
            <div
              key={p.title}
              className="rounded-2xl border border-[var(--color-border)] bg-white p-8 shadow-2xs hover:shadow-xs transition-shadow"
            >
              <div className="w-11 h-11 rounded-xl bg-[var(--color-background)] border border-[var(--color-border)] flex items-center justify-center text-[var(--color-primary)] mb-6 shadow-2xs">
                <p.icon className="w-5 h-5" />
              </div>
              <h3 className="text-[18px] font-bold text-[var(--color-text)] mb-2">
                {p.title}
              </h3>
              <p className="text-[14px] text-[var(--color-text-secondary)] leading-relaxed">
                {p.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
