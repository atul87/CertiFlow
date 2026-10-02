"use client";

import { useState } from "react";
import { Check, Minus, ArrowRight, ShieldCheck, Zap } from "lucide-react";
import { Button } from "@/components/ui/button";
import Link from "next/link";

interface ComparisonRow {
  category?: string;
  feature: string;
  free: string | boolean;
  pro: string | boolean;
  org: string | boolean;
}

const comparisonRows: ComparisonRow[] = [
  { feature: "Monthly Certificate Volume", free: "50 / mo", pro: "2,500 / mo", org: "50,000+ / mo" },
  { feature: "Active Certificate Templates", free: "1 template", pro: "Unlimited", org: "Unlimited" },
  { feature: "CSV / XLSX Web Worker Ingest", free: true, pro: true, org: true },
  { feature: "Smart Auto-Fit Dynamic Fields", free: true, pro: true, org: true },
  { feature: "High-DPI Vector PDF Output", free: true, pro: true, org: true },
  { feature: "Public QR Ledger Verification", free: true, pro: true, org: true },
  { feature: "SHA-256 PDF File Integrity Check", free: true, pro: true, org: true },
  { feature: "Transactional Email Outbox (SMTP)", free: false, pro: true, org: true },
  { feature: "High-Speed ARQ Worker Priority", free: false, pro: true, org: true },
  { feature: "Custom Branding & No Watermark", free: false, pro: true, org: true },
  { feature: "Scoped API Keys & Webhook Events", free: false, pro: true, org: true },
  { feature: "Multi-Seat Teams & RBAC (4 Roles)", free: false, pro: false, org: true },
  { feature: "W3C Verifiable Credentials (VC v2.0)", free: false, pro: false, org: true },
  { feature: "Custom DID & Verification Domain", free: false, pro: false, org: true },
  { feature: "Dedicated SLA & 24/7 Account Manager", free: false, pro: false, org: true },
];

export function PricingSection() {
  const [billingCycle, setBillingCycle] = useState<"monthly" | "annual">("monthly");

  return (
    <section className="section-padding bg-white border-t border-[var(--color-border)]">
      <div className="container-marketing">
        {/* Section Header */}
        <div className="max-w-2xl mx-auto text-center mb-10">
          <p className="text-[13px] font-semibold uppercase tracking-[0.15em] text-[var(--color-primary)] mb-3">
            Transparent Plans
          </p>
          <h2 className="text-section text-[var(--color-text)] mb-3 font-bold">
            Predictable plans as your events scale
          </h2>
          <p className="text-body-lg text-[var(--color-text-secondary)]">
            Start completely free for your first batch. Upgrade only when you need high-throughput background generation, custom verification, or automated email dispatch.
          </p>

          {/* Billing Cycle Toggle */}
          <div className="inline-flex items-center gap-3 bg-[var(--color-background)] p-1.5 rounded-xl border border-[var(--color-border)] mt-8">
            <button
              type="button"
              onClick={() => setBillingCycle("monthly")}
              className={`px-4 py-1.5 rounded-lg text-[13px] font-semibold transition-all ${
                billingCycle === "monthly"
                  ? "bg-white text-[var(--color-text)] shadow-xs"
                  : "text-gray-500 hover:text-gray-900"
              }`}
            >
              Monthly Billing
            </button>
            <button
              type="button"
              onClick={() => setBillingCycle("annual")}
              className={`px-4 py-1.5 rounded-lg text-[13px] font-semibold transition-all flex items-center gap-1.5 ${
                billingCycle === "annual"
                  ? "bg-white text-[var(--color-primary)] shadow-xs"
                  : "text-gray-500 hover:text-gray-900"
              }`}
            >
              <span>Annual Billing</span>
              <span className="text-[10px] bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded-full font-bold">
                Save 17%
              </span>
            </button>
          </div>
        </div>

        {/* 3 Tier Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto mb-16">
          {/* FREE TIER */}
          <div className="rounded-2xl border border-[var(--color-border)] bg-[var(--color-background)] p-7 flex flex-col justify-between">
            <div>
              <span className="text-[12px] font-bold text-gray-500 uppercase tracking-wider block mb-1">
                Tier 01
              </span>
              <h3 className="text-[22px] font-bold text-[var(--color-text)]">Starter</h3>
              <p className="text-[14px] text-[var(--color-text-secondary)] mt-1 mb-6">
                For workshops, small meetups, and testing CertiFlow
              </p>
              <div className="text-[36px] font-bold text-[var(--color-text)] mb-2 font-mono">
                ₹0
                <span className="text-[13px] text-gray-500 font-sans font-normal"> / forever</span>
              </div>
              <p className="text-[12px] text-gray-500 mb-6">Includes 50 certificates / month with public QR verification</p>

              <ul className="space-y-2.5 text-[13px] text-[var(--color-text-secondary)] mb-6 border-t border-[var(--color-border)] pt-5">
                <li className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-emerald-600 shrink-0" />
                  <span>50 certificates / month</span>
                </li>
                <li className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-emerald-600 shrink-0" />
                  <span>1 active design template</span>
                </li>
                <li className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-emerald-600 shrink-0" />
                  <span>Public QR code verification</span>
                </li>
                <li className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-emerald-600 shrink-0" />
                  <span>SHA-256 PDF file checksum</span>
                </li>
              </ul>
            </div>
            <Button variant="secondary" className="w-full justify-center" asChild>
              <Link href="/signup">Start Free</Link>
            </Button>
          </div>

          {/* PRO TIER */}
          <div className="rounded-2xl border-2 border-[var(--color-primary)] bg-white p-7 shadow-xl flex flex-col justify-between relative ring-4 ring-indigo-50">
            <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-[var(--color-primary)] text-white text-[11px] font-bold px-3.5 py-0.5 rounded-full uppercase tracking-wider shadow-sm flex items-center gap-1">
              <Zap className="w-3 h-3 fill-current" />
              Most Popular
            </div>
            <div>
              <span className="text-[12px] font-bold text-[var(--color-primary)] uppercase tracking-wider block mb-1">
                Tier 02
              </span>
              <h3 className="text-[22px] font-bold text-[var(--color-text)]">Pro Growth</h3>
              <p className="text-[14px] text-[var(--color-text-secondary)] mt-1 mb-6">
                For training bootcamps, academies, and frequent issuers
              </p>
              <div className="text-[36px] font-bold text-[var(--color-text)] mb-2 font-mono">
                {billingCycle === "monthly" ? "₹1,999" : "₹1,660"}
                <span className="text-[13px] text-gray-500 font-sans font-normal"> / month</span>
              </div>
              <p className="text-[12px] text-emerald-600 font-medium mb-6">
                {billingCycle === "annual" ? "Billed annually at ₹19,990 / year" : "Billed monthly • Cancel anytime"}
              </p>

              <ul className="space-y-2.5 text-[13px] text-[var(--color-text-secondary)] mb-6 border-t border-[var(--color-border)] pt-5">
                <li className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-emerald-600 shrink-0" />
                  <strong className="text-[var(--color-text)]">2,500 certificates / month</strong>
                </li>
                <li className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-emerald-600 shrink-0" />
                  <span>Unlimited design templates</span>
                </li>
                <li className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-emerald-600 shrink-0" />
                  <span>Transactional SMTP email delivery</span>
                </li>
                <li className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-emerald-600 shrink-0" />
                  <span>High-speed ARQ background priority</span>
                </li>
                <li className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-emerald-600 shrink-0" />
                  <span>Custom branding (remove watermark)</span>
                </li>
              </ul>
            </div>
            <Button className="w-full justify-center shadow-md" asChild>
              <Link href="/signup">
                Start 14-Day Pro Trial
                <ArrowRight className="w-4 h-4 ml-1.5" />
              </Link>
            </Button>
          </div>

          {/* ORGANIZATION TIER */}
          <div className="rounded-2xl border border-[var(--color-border)] bg-[var(--color-background)] p-7 flex flex-col justify-between">
            <div>
              <span className="text-[12px] font-bold text-gray-500 uppercase tracking-wider block mb-1">
                Tier 03
              </span>
              <h3 className="text-[22px] font-bold text-[var(--color-text)]">Enterprise</h3>
              <p className="text-[14px] text-[var(--color-text-secondary)] mt-1 mb-6">
                For universities, government bodies, and global certification providers
              </p>
              <div className="text-[36px] font-bold text-[var(--color-text)] mb-2 font-mono">
                Custom
                <span className="text-[13px] text-gray-500 font-sans font-normal"> / annual contract</span>
              </div>
              <p className="text-[12px] text-gray-500 mb-6">Tailored volume tiers (50,000 to 1,000,000+ certificates)</p>

              <ul className="space-y-2.5 text-[13px] text-[var(--color-text-secondary)] mb-6 border-t border-[var(--color-border)] pt-5">
                <li className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-emerald-600 shrink-0" />
                  <strong className="text-[var(--color-text)]">Unlimited & high-scale batches</strong>
                </li>
                <li className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-emerald-600 shrink-0" />
                  <span>W3C Verifiable Credentials (VC v2.0)</span>
                </li>
                <li className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-emerald-600 shrink-0" />
                  <span>Custom verification domain (did:web)</span>
                </li>
                <li className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-emerald-600 shrink-0" />
                  <span>Multi-seat teams & granular RBAC</span>
                </li>
                <li className="flex items-center gap-2">
                  <Check className="w-4 h-4 text-emerald-600 shrink-0" />
                  <span>Dedicated ARQ worker cluster & 99.9% SLA</span>
                </li>
              </ul>
            </div>
            <Button variant="secondary" className="w-full justify-center" asChild>
              <Link href="/contact">Talk to Enterprise Team</Link>
            </Button>
          </div>
        </div>

        {/* Feature Comparison Matrix Table */}
        <div className="max-w-4xl mx-auto rounded-2xl border border-[var(--color-border)] bg-white overflow-hidden shadow-sm">
          <div className="p-5 border-b border-[var(--color-border)] bg-gray-50 flex items-center justify-between">
            <h4 className="text-[16px] font-bold text-[var(--color-text)]">Comprehensive Feature Matrix</h4>
            <span className="text-[12px] text-gray-500 font-medium">15 Platform Capabilities Compared</span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-[14px]">
              <thead>
                <tr className="border-b border-[var(--color-border)] text-[12px] uppercase font-bold text-gray-500 bg-gray-50/50">
                  <th className="p-4 sm:p-5">Platform Capability</th>
                  <th className="p-4 sm:p-5 text-center w-32">Starter</th>
                  <th className="p-4 sm:p-5 text-center w-32 text-[var(--color-primary)] bg-indigo-50/50">Pro Growth</th>
                  <th className="p-4 sm:p-5 text-center w-36">Enterprise</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--color-border)] font-medium">
                {comparisonRows.map((r) => (
                  <tr key={r.feature} className="hover:bg-gray-50/50 transition-colors">
                    <td className="p-4 sm:p-5 text-[var(--color-text)] font-semibold">{r.feature}</td>
                    
                    <td className="p-4 sm:p-5 text-center text-[13px] text-gray-600">
                      {typeof r.free === "string" ? (
                        <span className="font-mono">{r.free}</span>
                      ) : r.free ? (
                        <Check className="w-4 h-4 text-emerald-600 mx-auto" />
                      ) : (
                        <Minus className="w-4 h-4 text-gray-300 mx-auto" />
                      )}
                    </td>

                    <td className="p-4 sm:p-5 text-center text-[13px] text-[var(--color-primary)] bg-indigo-50/20 font-semibold">
                      {typeof r.pro === "string" ? (
                        <span className="font-mono">{r.pro}</span>
                      ) : r.pro ? (
                        <Check className="w-4 h-4 text-emerald-600 mx-auto" />
                      ) : (
                        <Minus className="w-4 h-4 text-gray-300 mx-auto" />
                      )}
                    </td>

                    <td className="p-4 sm:p-5 text-center text-[13px] text-gray-800">
                      {typeof r.org === "string" ? (
                        <span className="font-mono font-bold">{r.org}</span>
                      ) : r.org ? (
                        <Check className="w-4 h-4 text-emerald-600 mx-auto" />
                      ) : (
                        <Minus className="w-4 h-4 text-gray-300 mx-auto" />
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Security Reassurance Footnote */}
        <div className="max-w-2xl mx-auto text-center mt-10 text-[12px] text-gray-500 flex items-center justify-center gap-2">
          <ShieldCheck className="w-4 h-4 text-emerald-600 shrink-0" />
          <span>All plans include TLS 1.3 encryption, ISO-compliant data isolation, and GDPR-ready consent management.</span>
        </div>
      </div>
    </section>
  );
}
