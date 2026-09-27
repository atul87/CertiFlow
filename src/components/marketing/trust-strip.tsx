"use client";

import {
  GraduationCap,
  Trophy,
  Code,
  BookOpen,
  Users,
  Building2,
} from "lucide-react";

const audiences = [
  { icon: GraduationCap, label: "Education" },
  { icon: Trophy, label: "Events" },
  { icon: Code, label: "Hackathons" },
  { icon: BookOpen, label: "Training" },
  { icon: Users, label: "Conferences" },
  { icon: Building2, label: "Organizations" },
];

export function TrustStrip() {
  return (
    <section className="py-10 border-y border-[var(--color-border)] bg-white/60">
      <div className="container-marketing">
        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          <p className="text-[13px] font-semibold text-[var(--color-text-tertiary)] uppercase tracking-wider shrink-0">
            Built for
          </p>

          <div className="flex flex-wrap items-center justify-center md:justify-end gap-x-8 gap-y-4">
            {audiences.map(({ icon: Icon, label }) => (
              <div
                key={label}
                className="flex items-center gap-2 text-[var(--color-text-secondary)] hover:text-[var(--color-text)] transition-colors"
              >
                <div className="w-7 h-7 rounded-lg bg-[var(--color-background)] border border-[var(--color-border)] flex items-center justify-center text-[var(--color-primary)]">
                  <Icon className="w-3.5 h-3.5" />
                </div>
                <span className="text-[13px] font-medium">{label}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
