"use client";

import { useState } from "react";
import Link from "next/link";
import { Award, ArrowRight, ShieldCheck, AlertCircle, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { api, ApiError, tokenStorage, orgStorage } from "@/lib/api-client";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrorMessage(null);

    const getRedirectUrl = () => {
      if (typeof window !== "undefined") {
        const params = new URLSearchParams(window.location.search);
        const red = params.get("redirect");
        if (red && red.startsWith("/")) return red;
      }
      return "/app";
    };

    try {
      // Authenticate with live FastAPI backend
      await api.auth.login({ email, password });
      window.location.href = getRedirectUrl();
    } catch (err: any) {
      if (err instanceof ApiError) {
        setErrorMessage(err.message || "Invalid email or password");
      } else {
        setErrorMessage("Unable to connect to backend server. Make sure FastAPI is running on port 8000.");
      }
      setLoading(false);
    }
  };

  const handleDemoMode = async () => {
    setLoading(true);
    setErrorMessage(null);
    try {
      await api.auth.demoSession();
      let target = "/app";
      if (typeof window !== "undefined") {
        const params = new URLSearchParams(window.location.search);
        const red = params.get("redirect");
        if (red && red.startsWith("/")) target = red;
      }
      window.location.href = target;
    } catch (err: any) {
      if (err instanceof ApiError && err.code === "DEMO_AUTH_DISABLED") {
        setErrorMessage("Demo mode is disabled in production environments. Please sign in with your credentials.");
      } else {
        setErrorMessage("Unable to establish demo session. Ensure FastAPI backend is running.");
      }
      setLoading(false);
    }
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
          <h1 className="text-[24px] font-bold text-[var(--color-text)]">Welcome back</h1>
          <p className="text-[14px] text-[var(--color-text-secondary)] mt-1">
            Log in to manage your certificate projects & batches
          </p>
        </div>

        {/* Error Alert */}
        {errorMessage && (
          <div className="mb-4 p-3.5 rounded-xl bg-red-50 border border-red-200 text-red-700 text-[13px] flex items-start gap-2.5">
            <AlertCircle className="w-4 h-4 mt-0.5 shrink-0 text-red-600" />
            <div className="flex-1">
              <p className="font-semibold">Authentication failed</p>
              <p className="text-[12px] text-red-600 mt-0.5">{errorMessage}</p>
            </div>
          </div>
        )}

        {/* Card */}
        <div className="bg-white border border-[var(--color-border)] rounded-2xl p-6 sm:p-8 shadow-sm">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="login-email" className="block text-[13px] font-medium text-[var(--color-text)] mb-1.5">
                Work Email
              </label>
              <input
                id="login-email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="admin@certiflow.io"
                className="w-full px-3.5 py-2.5 rounded-lg border border-[var(--color-border)] bg-[var(--color-background)] text-[14px] focus:outline-none focus:border-[var(--color-primary)] focus:bg-white transition-colors"
              />
            </div>

            <div>
              <div className="flex justify-between items-center mb-1.5">
                <label htmlFor="login-password" className="block text-[13px] font-medium text-[var(--color-text)]">
                  Password
                </label>
                <Link href="/forgot-password" className="text-[12px] text-[var(--color-primary)] hover:underline">
                  Forgot password?
                </Link>
              </div>
              <input
                id="login-password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full px-3.5 py-2.5 rounded-lg border border-[var(--color-border)] bg-[var(--color-background)] text-[14px] focus:outline-none focus:border-[var(--color-primary)] focus:bg-white transition-colors"
              />
            </div>

            <Button type="submit" loading={loading} size="lg" className="w-full justify-center mt-2">
              Sign In with Backend
              <ArrowRight className="w-4 h-4 ml-1.5" />
            </Button>

            <button
              type="button"
              onClick={handleDemoMode}
              className="w-full text-center text-[13px] text-gray-500 hover:text-gray-800 py-1 transition-colors flex items-center justify-center gap-1.5"
            >
              <Sparkles className="w-3.5 h-3.5 text-amber-500" />
              <span>Or explore in Offline / Demo Mode</span>
            </button>
          </form>

          <div className="mt-6 pt-6 border-t border-[var(--color-border)] text-center text-[13px] text-[var(--color-text-secondary)]">
            Don&apos;t have an account?{" "}
            <Link href="/signup" className="text-[var(--color-primary)] font-semibold hover:underline">
              Sign up free
            </Link>
          </div>
        </div>

        <div className="text-center mt-6 text-[12px] text-[var(--color-text-tertiary)] flex items-center justify-center gap-1.5">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
          <span>Encrypted with TLS 1.3 & Argon2id Hashing</span>
        </div>
      </div>
    </div>
  );
}
