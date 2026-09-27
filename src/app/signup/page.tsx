"use client";

import { useState } from "react";
import Link from "next/link";
import { Award, ArrowRight, ShieldCheck, Check, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function SignupPage() {
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [orgType, setOrgType] = useState("University / College");
  const [loading, setLoading] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setTimeout(() => {
      window.location.href = "/app";
    }, 800);
  };

  return (
    <div className="min-h-screen flex flex-col justify-center bg-[var(--color-background)] p-4 sm:p-8">
      <div className="max-w-md w-full mx-auto">
        {/* Brand header */}
        <div className="text-center mb-8">
          <Link href="/" className="inline-flex items-center gap-2 mb-3 group">
            <div className="w-9 h-9 rounded-xl bg-[var(--color-primary)] text-white flex items-center justify-center shadow-sm group-hover:scale-105 transition-transform">
              <Award className="w-5 h-5" />
            </div>
            <span className="text-[20px] font-bold tracking-tight text-[var(--color-text)]">
              CertiFlow
            </span>
          </Link>
          <h1 className="text-[24px] font-bold text-[var(--color-text)]">Start creating free</h1>
          <p className="text-[14px] text-[var(--color-text-secondary)] mt-1">
            Turn spreadsheets into hundreds of credentials in minutes
          </p>
        </div>

        {/* Card */}
        <div className="bg-white border border-[var(--color-border)] rounded-2xl p-6 sm:p-8 shadow-sm">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-[13px] font-medium text-[var(--color-text)] mb-1.5">
                Full Name
              </label>
              <input
                type="text"
                required
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="Atul Kumar"
                className="w-full px-3.5 py-2.5 rounded-lg border border-[var(--color-border)] bg-[var(--color-background)] text-[14px] focus:outline-none focus:border-[var(--color-primary)] focus:bg-white transition-colors"
              />
            </div>

            <div>
              <label className="block text-[13px] font-medium text-[var(--color-text)] mb-1.5">
                Work Email
              </label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="atul@university.edu"
                className="w-full px-3.5 py-2.5 rounded-lg border border-[var(--color-border)] bg-[var(--color-background)] text-[14px] focus:outline-none focus:border-[var(--color-primary)] focus:bg-white transition-colors"
              />
            </div>

            <div>
              <label className="block text-[13px] font-medium text-[var(--color-text)] mb-1.5">
                Organization Type
              </label>
              <select
                value={orgType}
                onChange={(e) => setOrgType(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-lg border border-[var(--color-border)] bg-[var(--color-background)] text-[14px] focus:outline-none focus:border-[var(--color-primary)] focus:bg-white transition-colors"
              >
                <option>University / College</option>
                <option>School / K-12</option>
                <option>Hackathon / Tech Event</option>
                <option>Bootcamp / Training Center</option>
                <option>Corporate Enterprise</option>
                <option>Independent Creator</option>
              </select>
            </div>

            <div>
              <label className="block text-[13px] font-medium text-[var(--color-text)] mb-1.5">
                Password
              </label>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="At least 8 characters"
                className="w-full px-3.5 py-2.5 rounded-lg border border-[var(--color-border)] bg-[var(--color-background)] text-[14px] focus:outline-none focus:border-[var(--color-primary)] focus:bg-white transition-colors"
              />
            </div>

            <Button type="submit" loading={loading} size="lg" className="w-full justify-center mt-2">
              <Sparkles className="w-4 h-4 mr-1.5" />
              Create Free Account
            </Button>
          </form>

          <div className="mt-5 space-y-2 text-[12px] text-[var(--color-text-secondary)]">
            <div className="flex items-center gap-2">
              <Check className="w-3.5 h-3.5 text-emerald-600" />
              <span>100 certificates included free every month</span>
            </div>
            <div className="flex items-center gap-2">
              <Check className="w-3.5 h-3.5 text-emerald-600" />
              <span>No credit card required to start</span>
            </div>
          </div>

          <div className="mt-6 pt-6 border-t border-[var(--color-border)] text-center text-[13px] text-[var(--color-text-secondary)]">
            Already have an account?{" "}
            <Link href="/login" className="text-[var(--color-primary)] font-semibold hover:underline">
              Log in
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
