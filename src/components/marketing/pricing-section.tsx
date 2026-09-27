"use client";

import { Check, Minus, ArrowRight, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import Link from "next/link";

const comparisonRows = [
  { feature: "Certificates", free: true, pro: true, org: true },
  { feature: "Templates", free: true, pro: true, org: true },
  { feature: "CSV Import", free: true, pro: true, org: true },
  { feature: "Bulk Generation", free: true, pro: true, org: true },
  { feature: "QR Verification", free: false, pro: true, org: true },
  { feature: "Email Delivery", free: false, pro: true, org: true },
  { feature: "Multi-Seat Teams", free: false, pro: false, org: true },
  { feature: "High-Throughput API", free: false, pro: false, org: true },
];

export function PricingSection() {
  return (
    <section className="section-padding bg-white border-t border-[var(--color-border)]">
      <div className="container-marketing">
        {/* Section Header */}
        <div className="max-w-2xl mx-auto text-center mb-16">
          <p className="text-[13px] font-semibold uppercase tracking-[0.15em] text-[var(--color-primary)] mb-3">
            Transparent Plans
          </p>
          <h2 className="text-section text-[var(--color-text)] mb-3">
            Predictable plans as your events scale
          </h2>
          <p className="text-body-lg text-[var(--color-text-secondary)]">
            Start completely free for your first batch. Upgrade only when you need custom verification or automated email delivery.
          </p>
        </div>

        {/* 3 Tier Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto mb-16">
          {/* FREE */}
          <div className="rounded-2xl border border-[var(--color-border)] bg-[var(--color-background)] p-7 flex flex-col justify-between">
            <div>
              <span className="text-[12px] font-bold text-gray-500 uppercase tracking-wider block mb-1">
                Tier 01
              </span>
              <h3 className="text-[22px] font-bold text-[var(--color-text)]">FREE</h3>
              <p className="text-[14px] text-[var(--color-text-secondary)] mt-1 mb-6">
                For trying CertiFlow and small private events
              </p>
              <div className="text-[32px] font-bold text-[var(--color-text)] mb-6">
                ₹0
                <span className="text-[13px] text-gray-500 font-normal"> / forever</span>
              </div>
            </div>
            <Button variant="secondary" className="w-full justify-center" asChild>
              <Link href="/signup">Start Free</Link>
            </Button>
          </div>

          {/* PRO */}
          <div className="rounded-2xl border-2 border-[var(--color-primary)] bg-white p-7 shadow-lg flex flex-col justify-between relative">
            <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-[var(--color-primary)] text-white text-[11px] font-bold px-3 py-0.5 rounded-full uppercase tracking-wider">
              Most Popular
            </div>
            <div>
              <span className="text-[12px] font-bold text-[var(--color-primary)] uppercase tracking-wider block mb-1">
                Tier 02
              </span>
              <h3 className="text-[22px] font-bold text-[var(--color-text)]">PRO</h3>
              <p className="text-[14px] text-[var(--color-text-secondary)] mt-1 mb-6">
                For regular certificate workflows and training programs
              </p>
              <div className="text-[32px] font-bold text-[var(--color-text)] mb-6">
                Starting at ₹—
                <span className="text-[13px] text-gray-500 font-normal"> / month</span>
              </div>
            </div>
            <Button className="w-full justify-center" asChild>
              <Link href="/signup">
                Start Pro Trial
                <ArrowRight className="w-4 h-4 ml-1.5" />
              </Link>
            </Button>
          </div>

          {/* ORGANIZATION */}
          <div className="rounded-2xl border border-[var(--color-border)] bg-[var(--color-background)] p-7 flex flex-col justify-between">
            <div>
              <span className="text-[12px] font-bold text-gray-500 uppercase tracking-wider block mb-1">
                Tier 03
              </span>
              <h3 className="text-[22px] font-bold text-[var(--color-text)]">ORGANIZATION</h3>
              <p className="text-[14px] text-[var(--color-text-secondary)] mt-1 mb-6">
                For teams, universities, and institutions
              </p>
              <div className="text-[32px] font-bold text-[var(--color-text)] mb-6">
                Custom
                <span className="text-[13px] text-gray-500 font-normal"> / annual agreement</span>
              </div>
            </div>
            <Button variant="secondary" className="w-full justify-center" asChild>
              <Link href="/contact">Contact Sales</Link>
            </Button>
          </div>
        </div>

        {/* Feature Comparison Matrix Table */}
        <div className="max-w-4xl mx-auto rounded-2xl border border-[var(--color-border)] bg-white overflow-hidden shadow-2xs">
          <div className="p-5 border-b border-[var(--color-border)] bg-gray-50">
            <h4 className="text-[16px] font-bold text-[var(--color-text)]">Feature Comparison Matrix</h4>
          </div>
          <table className="w-full text-left text-[14px]">
            <thead>
              <tr className="border-b border-[var(--color-border)] text-[12px] uppercase font-bold text-gray-400">
                <th className="p-4 sm:p-5">Feature</th>
                <th className="p-4 sm:p-5 text-center">Free</th>
                <th className="p-4 sm:p-5 text-center text-[var(--color-primary)]">Pro</th>
                <th className="p-4 sm:p-5 text-center">Organization</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--color-border)] font-medium">
              {comparisonRows.map((r) => (
                <tr key={r.feature} className="hover:bg-gray-50/50 transition-colors">
                  <td className="p-4 sm:p-5 text-[var(--color-text)]">{r.feature}</td>
                  <td className="p-4 sm:p-5 text-center">
                    {r.free ? <Check className="w-4 h-4 text-emerald-600 mx-auto" /> : <Minus className="w-4 h-4 text-gray-300 mx-auto" />}
                  </td>
                  <td className="p-4 sm:p-5 text-center">
                    {r.pro ? <Check className="w-4 h-4 text-emerald-600 mx-auto" /> : <Minus className="w-4 h-4 text-gray-300 mx-auto" />}
                  </td>
                  <td className="p-4 sm:p-5 text-center">
                    {r.org ? <Check className="w-4 h-4 text-emerald-600 mx-auto" /> : <Minus className="w-4 h-4 text-gray-300 mx-auto" />}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}
