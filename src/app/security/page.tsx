"use client";

import { useState } from "react";
import Link from "next/link";
import {
  ShieldCheck,
  Lock,
  Key,
  Server,
  FileCheck,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  EyeOff,
  Database,
} from "lucide-react";
import { Navbar } from "@/components/navigation/navbar";
import { Footer } from "@/components/marketing/footer";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

export default function SecurityPage() {
  const [testInput, setTestInput] = useState("Atul Kumar | AI Workshop 2026 | Score 98%");
  const [isTampered, setIsTampered] = useState(false);

  // Simulated SHA-256 Hash display
  const originalHash = "9f83a21b48d0e74f32c1998e3b5062a7e112d8a41762c954b876a301ef6c4d92";
  const tamperedHash = "3c88019ab9403d19e001844b25697332c918ef002138947190d8a4192b950001";

  return (
    <div className="min-h-screen bg-[var(--color-background)] flex flex-col">
      <Navbar />

      <main className="flex-1">
        {/* Header */}
        <section className="py-20 border-b border-[var(--color-border)] bg-white text-center">
          <div className="container-marketing max-w-3xl space-y-4">
            <Badge variant="primary" className="text-[12px] px-3 py-1">
              Enterprise Trust & Architecture
            </Badge>
            <h1 className="text-[36px] sm:text-[48px] font-bold text-[var(--color-text)] tracking-tight">
              Cryptographic Integrity at Every Step
            </h1>
            <p className="text-[16px] text-[var(--color-text-secondary)] leading-relaxed">
              CertiFlow protects issuing organizations and recipients against credential forgery, credential theft, and unauthorized data leakage.
            </p>
          </div>
        </section>

        {/* Security Pillars */}
        <section className="py-20 container-marketing space-y-16">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="bg-white rounded-2xl border border-[var(--color-border)] p-6 space-y-4 shadow-2xs">
              <div className="w-12 h-12 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
                <Key className="w-6 h-6" />
              </div>
              <h3 className="text-[18px] font-bold text-gray-900">
                SHA-256 Cryptographic Signatures
              </h3>
              <p className="text-[14px] text-gray-600 leading-relaxed">
                Every certificate contains a deterministic digital fingerprint computed from recipient name, issue date, credential ID, and issuer secret. Any alteration to the certificate text invalidates the cryptographic signature.
              </p>
            </div>

            <div className="bg-white rounded-2xl border border-[var(--color-border)] p-6 space-y-4 shadow-2xs">
              <div className="w-12 h-12 rounded-xl bg-indigo-50 text-[var(--color-primary)] flex items-center justify-center">
                <EyeOff className="w-6 h-6" />
              </div>
              <h3 className="text-[18px] font-bold text-gray-900">
                Zero-Retention Processing
              </h3>
              <p className="text-[14px] text-gray-600 leading-relaxed">
                For organizations with strict student privacy requirements (FERPA, GDPR), spreadsheets are parsed directly inside client-side memory without ever hitting a persistent database.
              </p>
            </div>

            <div className="bg-white rounded-2xl border border-[var(--color-border)] p-6 space-y-4 shadow-2xs">
              <div className="w-12 h-12 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center">
                <ShieldCheck className="w-6 h-6" />
              </div>
              <h3 className="text-[18px] font-bold text-gray-900">
                Instant Revocation Engine
              </h3>
              <p className="text-[14px] text-gray-600 leading-relaxed">
                If a credential was issued in error or compromised, administrators can revoke it in one click. Public QR scans immediately display an official revocation notice with timestamp and reason.
              </p>
            </div>
          </div>

          {/* Interactive Cryptographic Demonstration */}
          <div className="bg-white rounded-2xl border border-[var(--color-border)] p-8 max-w-4xl mx-auto shadow-2xs space-y-6">
            <div className="flex items-center gap-2 text-[var(--color-primary)] font-bold text-[13px] uppercase tracking-wider">
              <Lock className="w-4 h-4" />
              Interactive Anti-Tamper Demonstration
            </div>

            <div>
              <h3 className="text-[20px] font-bold text-gray-900">
                How CertiFlow Stops Photoshop & PDF Forgery
              </h3>
              <p className="text-[13px] text-gray-500 mt-1">
                Toggle below to simulate an unauthorized attempt to alter the recipient name on an issued certificate.
              </p>
            </div>

            <div className="space-y-4">
              <div className="flex gap-2">
                <Button
                  size="sm"
                  variant={isTampered ? "secondary" : "primary"}
                  onClick={() => setIsTampered(false)}
                >
                  Authentic Issued Credential
                </Button>
                <Button
                  size="sm"
                  variant={isTampered ? "primary" : "secondary"}
                  onClick={() => setIsTampered(true)}
                  className={isTampered ? "bg-red-600 hover:bg-red-700" : ""}
                >
                  Simulate Modified/Forged Name
                </Button>
              </div>

              <div className="p-4 rounded-xl bg-gray-50 border border-gray-200 font-mono text-[13px] space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-500">Payload:</span>
                  <span className="font-bold text-gray-800">
                    {isTampered
                      ? "Fake Name Modified | AI Workshop 2026 | Score 98%"
                      : "Atul Kumar | AI Workshop 2026 | Score 98%"}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-500">Cryptographic Hash:</span>
                  <span className={`text-[12px] ${isTampered ? "text-red-600 font-bold" : "text-emerald-700"}`}>
                    {isTampered ? tamperedHash : originalHash}
                  </span>
                </div>
              </div>

              <div
                className={`p-4 rounded-xl border flex items-center gap-3 ${
                  isTampered
                    ? "bg-red-50 border-red-200 text-red-800"
                    : "bg-emerald-50 border-emerald-200 text-emerald-800"
                }`}
              >
                {isTampered ? (
                  <>
                    <AlertTriangle className="w-5 h-5 text-red-600 shrink-0" />
                    <div>
                      <p className="font-bold text-[13px]">VERIFICATION REJECTED: SIGNATURE MISMATCH</p>
                      <p className="text-[11px] text-red-700">
                        The hash stored in the QR code does not match the computed hash of the presented certificate. Forgery detected.
                      </p>
                    </div>
                  </>
                ) : (
                  <>
                    <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
                    <div>
                      <p className="font-bold text-[13px]">VERIFICATION PASSED: 100% AUTHENTIC</p>
                      <p className="text-[11px] text-emerald-700">
                        Cryptographic signature matches the public ledger registry. Credential is valid and unmodified.
                      </p>
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>
        </section>

        {/* Compliance Badges */}
        <section className="py-16 bg-white border-t border-[var(--color-border)] text-center">
          <div className="container-marketing max-w-3xl space-y-6">
            <h3 className="text-[20px] font-bold text-gray-900">Compliance & Certifications</h3>
            <div className="flex flex-wrap justify-center gap-4">
              {["SOC 2 Type II Certified", "GDPR & CCPA Compliant", "FERPA Compatible", "256-Bit TLS Encryption", "ISO 27001 Aligned"].map((b) => (
                <div key={b} className="px-4 py-2 rounded-xl bg-gray-50 border border-gray-200 text-[13px] font-semibold text-gray-700 flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  {b}
                </div>
              ))}
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}
