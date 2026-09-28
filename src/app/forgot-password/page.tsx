"use client";

import { useState } from "react";
import Link from "next/link";
import { ArrowLeft, Mail, CheckCircle2, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function ForgotPasswordPage() {
  const [submitted, setSubmitted] = useState(false);
  const [email, setEmail] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setTimeout(() => {
      setIsSubmitting(false);
      setSubmitted(true);
    }, 800);
  };

  return (
    <div className="min-h-screen bg-[var(--color-background)] flex flex-col justify-center items-center p-4">
      <div className="w-full max-w-md bg-white rounded-2xl border border-[var(--color-border)] p-8 shadow-sm space-y-6">
        <div className="text-center space-y-2">
          <Link href="/" className="inline-flex items-center gap-2 font-bold text-[18px]">
            <span className="text-[var(--color-primary)]">✦</span> CERTIFLOW
          </Link>
          <h1 className="text-[22px] font-bold text-gray-900">Reset Your Password</h1>
          <p className="text-[13px] text-gray-500">
            Enter your email and we&apos;ll send you a secure link to reset your account credentials.
          </p>
        </div>

        {submitted ? (
          <div className="text-center space-y-4 py-4">
            <div className="w-12 h-12 rounded-full bg-emerald-50 text-emerald-600 flex items-center justify-center mx-auto">
              <CheckCircle2 className="w-6 h-6" />
            </div>
            <div>
              <p className="font-bold text-[15px] text-gray-900">Reset Link Sent</p>
              <p className="text-[13px] text-gray-500 mt-1">
                We sent a password reset link to <strong>{email}</strong>. Check your inbox and spam folder.
              </p>
            </div>
            <Button variant="secondary" className="w-full" asChild>
              <Link href="/login">Return to Login</Link>
            </Button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-[12px] font-semibold text-gray-700 mb-1">
                Account Email Address
              </label>
              <input
                required
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@organization.edu"
                className="w-full px-3.5 py-2.5 rounded-xl border border-[var(--color-border)] text-[14px]"
              />
            </div>

            <Button type="submit" disabled={isSubmitting} className="w-full justify-center h-11">
              {isSubmitting ? "Sending Reset Email..." : "Send Reset Link"}
            </Button>

            <div className="text-center pt-2">
              <Link
                href="/login"
                className="text-[13px] text-gray-500 hover:text-black inline-flex items-center gap-1 font-medium transition-colors"
              >
                <ArrowLeft className="w-3.5 h-3.5" /> Back to login
              </Link>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
