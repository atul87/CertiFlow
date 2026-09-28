"use client";

import { useState } from "react";
import Link from "next/link";
import { ArrowLeft, Lock, CheckCircle2 } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function ResetPasswordPage() {
  const [success, setSuccess] = useState(false);
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (password !== confirmPassword) return;
    setIsSubmitting(true);
    setTimeout(() => {
      setIsSubmitting(false);
      setSuccess(true);
    }, 800);
  };

  return (
    <div className="min-h-screen bg-[var(--color-background)] flex flex-col justify-center items-center p-4">
      <div className="w-full max-w-md bg-white rounded-2xl border border-[var(--color-border)] p-8 shadow-sm space-y-6">
        <div className="text-center space-y-2">
          <Link href="/" className="inline-flex items-center gap-2 font-bold text-[18px]">
            <span className="text-[var(--color-primary)]">✦</span> CERTIFLOW
          </Link>
          <h1 className="text-[22px] font-bold text-gray-900">Set New Password</h1>
          <p className="text-[13px] text-gray-500">
            Please enter your new password below to secure your CertiFlow account.
          </p>
        </div>

        {success ? (
          <div className="text-center space-y-4 py-4">
            <div className="w-12 h-12 rounded-full bg-emerald-50 text-emerald-600 flex items-center justify-center mx-auto">
              <CheckCircle2 className="w-6 h-6" />
            </div>
            <div>
              <p className="font-bold text-[15px] text-gray-900">Password Updated</p>
              <p className="text-[13px] text-gray-500 mt-1">
                Your password has been reset successfully. You can now log into your dashboard.
              </p>
            </div>
            <Button className="w-full" asChild>
              <Link href="/login">Proceed to Login</Link>
            </Button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-[12px] font-semibold text-gray-700 mb-1">
                New Password (Min. 8 characters)
              </label>
              <input
                required
                minLength={8}
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••••"
                className="w-full px-3.5 py-2.5 rounded-xl border border-[var(--color-border)] text-[14px]"
              />
            </div>

            <div>
              <label className="block text-[12px] font-semibold text-gray-700 mb-1">
                Confirm New Password
              </label>
              <input
                required
                minLength={8}
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="••••••••••••"
                className="w-full px-3.5 py-2.5 rounded-xl border border-[var(--color-border)] text-[14px]"
              />
            </div>

            <Button type="submit" disabled={isSubmitting} className="w-full justify-center h-11">
              {isSubmitting ? "Updating Password..." : "Save New Password"}
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
