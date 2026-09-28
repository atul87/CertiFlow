"use client";

import { useState } from "react";
import Link from "next/link";
import { Check, Sparkles, Calculator, ArrowRight, ShieldCheck, HelpCircle } from "lucide-react";
import { Navbar } from "@/components/navigation/navbar";
import { Footer } from "@/components/marketing/footer";
import { PricingSection } from "@/components/marketing/pricing-section";
import { FAQSection } from "@/components/marketing/faq-section";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

export default function PricingPage() {
  const [certsPerMonth, setCertsPerMonth] = useState(500);

  // ROI Calculator Math:
  // Manual time: 3 mins per cert in Canva/Photoshop
  // Total manual hours = (certs * 3) / 60
  // Value of designer/coordinator time = $35/hr
  const manualHours = Math.round((certsPerMonth * 3) / 60);
  const manualCost = manualHours * 35;
  const certiflowCost = 39; // Pro plan
  const monthlySavings = Math.max(0, manualCost - certiflowCost);
  const annualSavings = monthlySavings * 12;

  return (
    <div className="min-h-screen bg-[var(--color-background)] flex flex-col">
      <Navbar />

      <main className="flex-1">
        {/* Header */}
        <section className="py-16 text-center border-b border-[var(--color-border)] bg-white">
          <div className="container-marketing max-w-3xl space-y-4">
            <Badge variant="primary" className="text-[12px] px-3 py-1">
              Transparent, Value-Based Pricing
            </Badge>
            <h1 className="text-[36px] sm:text-[48px] font-bold text-[var(--color-text)] tracking-tight">
              Pay for Automated Delivery, Not Manual Hours
            </h1>
            <p className="text-[16px] text-[var(--color-text-secondary)] leading-relaxed">
              Start free with no credit card required. Upgrade as your certification volume grows.
            </p>
          </div>
        </section>

        {/* ROI Savings Calculator */}
        <section className="py-12 bg-indigo-50/40 border-b border-indigo-100">
          <div className="container-marketing max-w-4xl">
            <div className="bg-white rounded-2xl border border-indigo-100 p-6 sm:p-8 shadow-2xs">
              <div className="flex items-center gap-2 text-[var(--color-primary)] font-bold text-[13px] uppercase tracking-wider mb-2">
                <Calculator className="w-4 h-4" />
                CertiFlow ROI & Efficiency Calculator
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center mt-4">
                <div className="space-y-4">
                  <h3 className="text-[18px] font-bold text-gray-900">
                    How many certificates do you issue per month?
                  </h3>
                  <div className="space-y-2">
                    <div className="flex justify-between text-[14px] font-bold text-gray-800">
                      <span>Volume:</span>
                      <span className="font-mono text-[var(--color-primary)] text-[16px]">
                        {certsPerMonth.toLocaleString()} recipients / month
                      </span>
                    </div>
                    <input
                      type="range"
                      min="50"
                      max="5000"
                      step="50"
                      value={certsPerMonth}
                      onChange={(e) => setCertsPerMonth(Number(e.target.value))}
                      className="w-full accent-[var(--color-primary)] cursor-pointer"
                    />
                    <div className="flex justify-between text-[11px] text-gray-400 font-mono">
                      <span>50</span>
                      <span>1,000</span>
                      <span>2,500</span>
                      <span>5,000+</span>
                    </div>
                  </div>
                </div>

                <div className="p-5 rounded-xl bg-gray-50 border border-gray-200/80 space-y-3">
                  <div className="flex justify-between text-[13px]">
                    <span className="text-gray-500">Manual Hours Saved:</span>
                    <span className="font-bold text-gray-800">{manualHours} hours / month</span>
                  </div>
                  <div className="flex justify-between text-[13px]">
                    <span className="text-gray-500">Estimated Annual Cost Savings:</span>
                    <span className="font-bold text-emerald-600 text-[18px]">
                      ${annualSavings.toLocaleString()} / year
                    </span>
                  </div>
                  <p className="text-[11px] text-gray-400 border-t border-gray-200 pt-2">
                    Calculated against standard 3-min manual Photoshop/Canva export workflow at $35/hr labor value.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Pricing Cards & Comparison Table */}
        <PricingSection />

        {/* FAQ Section */}
        <FAQSection />
      </main>

      <Footer />
    </div>
  );
}
