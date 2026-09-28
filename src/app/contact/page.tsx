"use client";

import { useState } from "react";
import Link from "next/link";
import {
  Mail,
  MessageSquare,
  Building,
  CheckCircle2,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  Clock,
} from "lucide-react";
import { Navbar } from "@/components/navigation/navbar";
import { Footer } from "@/components/marketing/footer";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

export default function ContactPage() {
  const [submitted, setSubmitted] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setTimeout(() => {
      setIsSubmitting(false);
      setSubmitted(true);
    }, 1000);
  };

  return (
    <div className="min-h-screen bg-[var(--color-background)] flex flex-col">
      <Navbar />

      <main className="flex-1">
        {/* Header */}
        <section className="py-20 border-b border-[var(--color-border)] bg-white text-center">
          <div className="container-marketing max-w-2xl space-y-4">
            <Badge variant="primary" className="text-[12px] px-3 py-1">
              Sales & Enterprise Support
            </Badge>
            <h1 className="text-[36px] sm:text-[48px] font-bold text-[var(--color-text)] tracking-tight">
              Let&apos;s Discuss Your Certification Needs
            </h1>
            <p className="text-[16px] text-[var(--color-text-secondary)] leading-relaxed">
              Whether you are issuing 100 certificates for a workshop or 50,000 for a global university, our engineering team is here to help.
            </p>
          </div>
        </section>

        {/* Content Section */}
        <section className="py-16 container-marketing max-w-5xl">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-start">
            {/* Left Column: Organization Benefits */}
            <div className="space-y-6">
              <h2 className="text-[22px] font-bold text-gray-900">
                Enterprise-Ready Credential Platform
              </h2>
              <p className="text-[14px] text-gray-600 leading-relaxed">
                Connect with our product specialists to see custom LMS integrations, volume discounts, custom domain setups, or bespoke security audits.
              </p>

              <div className="space-y-4 pt-2">
                {[
                  {
                    title: "Dedicated Technical Architect",
                    desc: "Assistance configuring webhooks, SSO (Okta, Azure AD), and automated CSV pipelines.",
                  },
                  {
                    title: "Custom SLA & High Volume",
                    desc: "Tailored 99.99% uptime guarantees and high-priority render queuing for batches > 10,000.",
                  },
                  {
                    title: "Custom White-Labeling",
                    desc: "Completely branded verification portal hosted on your custom educational or corporate domain.",
                  },
                ].map((item) => (
                  <div key={item.title} className="p-4 rounded-xl bg-white border border-[var(--color-border)] space-y-1">
                    <p className="text-[14px] font-bold text-gray-800 flex items-center gap-2">
                      <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                      {item.title}
                    </p>
                    <p className="text-[12px] text-gray-500 pl-6 leading-relaxed">{item.desc}</p>
                  </div>
                ))}
              </div>

              <div className="p-4 rounded-xl bg-indigo-50/60 border border-indigo-100 flex items-center gap-3 text-[13px] text-indigo-950">
                <Clock className="w-5 h-5 text-[var(--color-primary)] shrink-0" />
                <span>Typical enterprise response time is under <strong>2 hours</strong> during standard business days.</span>
              </div>
            </div>

            {/* Right Column: Contact Form */}
            <div className="bg-white rounded-2xl border border-[var(--color-border)] p-6 sm:p-8 shadow-2xs">
              {submitted ? (
                <div className="py-12 text-center space-y-4">
                  <div className="w-14 h-14 rounded-2xl bg-emerald-50 text-emerald-600 flex items-center justify-center mx-auto">
                    <CheckCircle2 className="w-8 h-8" />
                  </div>
                  <h3 className="text-[20px] font-bold text-gray-900">Thank you for reaching out!</h3>
                  <p className="text-[14px] text-gray-500 max-w-sm mx-auto leading-relaxed">
                    Our solutions team has received your message and will contact you shortly with custom pricing and setup guidance.
                  </p>
                  <Button variant="secondary" onClick={() => setSubmitted(false)}>
                    Send Another Message
                  </Button>
                </div>
              ) : (
                <form onSubmit={handleSubmit} className="space-y-4">
                  <h3 className="text-[18px] font-bold text-gray-900 mb-2">
                    Send Us a Message
                  </h3>

                  <div>
                    <label className="block text-[12px] font-semibold text-gray-700 mb-1">
                      Full Name *
                    </label>
                    <input
                      required
                      type="text"
                      placeholder="Jane Doe"
                      className="w-full px-3 py-2 rounded-xl border border-[var(--color-border)] text-[13px]"
                    />
                  </div>

                  <div>
                    <label className="block text-[12px] font-semibold text-gray-700 mb-1">
                      Work Email *
                    </label>
                    <input
                      required
                      type="email"
                      placeholder="jane@university.edu"
                      className="w-full px-3 py-2 rounded-xl border border-[var(--color-border)] text-[13px]"
                    />
                  </div>

                  <div>
                    <label className="block text-[12px] font-semibold text-gray-700 mb-1">
                      Organization / University *
                    </label>
                    <input
                      required
                      type="text"
                      placeholder="Stanford AI Institute"
                      className="w-full px-3 py-2 rounded-xl border border-[var(--color-border)] text-[13px]"
                    />
                  </div>

                  <div>
                    <label className="block text-[12px] font-semibold text-gray-700 mb-1">
                      Expected Certificate Volume
                    </label>
                    <select className="w-full px-3 py-2 rounded-xl border border-[var(--color-border)] text-[13px] bg-white text-gray-700">
                      <option value="500">Less than 500 certs / month</option>
                      <option value="2500">500 to 2,500 certs / month</option>
                      <option value="10000">2,500 to 10,000 certs / month</option>
                      <option value="50000">10,000+ certs / month (Enterprise)</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-[12px] font-semibold text-gray-700 mb-1">
                      Message / Project Details
                    </label>
                    <textarea
                      rows={3}
                      placeholder="Tell us about your upcoming event, conference, or certification pipeline..."
                      className="w-full px-3 py-2 rounded-xl border border-[var(--color-border)] text-[13px]"
                    />
                  </div>

                  <Button type="submit" disabled={isSubmitting} className="w-full justify-center h-11">
                    {isSubmitting ? (
                      <span className="flex items-center gap-2">
                        <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                        Submitting Inquiry...
                      </span>
                    ) : (
                      <span className="flex items-center gap-1.5">
                        Send Inquiry
                        <ArrowRight className="w-4 h-4" />
                      </span>
                    )}
                  </Button>
                </form>
              )}
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}
