"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { AlertTriangle, RefreshCw, Home, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  const router = useRouter();
  useEffect(() => {
    // Log to your error monitoring service (Sentry, etc.)
    console.error("[CertiFlow Error]", error);
  }, [error]);

  const isNetworkError =
    error.message?.toLowerCase().includes("fetch") ||
    error.message?.toLowerCase().includes("network") ||
    error.message?.toLowerCase().includes("failed");

  const isAuthError =
    error.message?.toLowerCase().includes("401") ||
    error.message?.toLowerCase().includes("unauthorized");

  const title = isAuthError
    ? "Session expired"
    : isNetworkError
    ? "Connection problem"
    : "Something went wrong";

  const description = isAuthError
    ? "Your session has expired. Please log in again to continue."
    : isNetworkError
    ? "We couldn't reach the CertiFlow servers. Check your internet connection and try again."
    : "An unexpected error occurred. We've been notified and are looking into it.";

  return (
    <div className="min-h-[60vh] flex flex-col items-center justify-center p-8 text-center">
      {/* Error icon */}
      <div className="w-16 h-16 rounded-2xl bg-red-50 border border-red-100 flex items-center justify-center mb-5 shadow-sm">
        <AlertTriangle className="w-8 h-8 text-red-500" />
      </div>

      {/* Title */}
      <h2 className="text-[22px] font-bold text-[var(--color-text)] mb-2 tracking-tight">{title}</h2>
      <p className="text-[14px] text-[var(--color-text-secondary)] max-w-md leading-relaxed mb-6">{description}</p>

      {/* Error details (dev-friendly) */}
      {error.message && !isAuthError && (
        <details className="mb-6 text-left max-w-md w-full">
          <summary className="text-[12px] font-semibold text-[var(--color-text-tertiary)] cursor-pointer hover:text-[var(--color-text)] transition-colors mb-2">
            Show error details
          </summary>
          <div className="bg-gray-900 rounded-xl p-4">
            <code className="text-[11px] font-mono text-red-400 break-all leading-relaxed">
              {error.message}
              {error.digest && <><br /><span className="text-gray-500">Digest: {error.digest}</span></>}
            </code>
          </div>
        </details>
      )}

      {/* Actions */}
      <div className="flex flex-col sm:flex-row items-center gap-3">
        <Button onClick={reset} className="gap-2">
          <RefreshCw className="w-4 h-4" />
          {isNetworkError ? "Retry" : "Try again"}
        </Button>
        <Button
          variant="secondary"
          onClick={() => router.push("/app")}
          className="gap-2"
        >
          <Home className="w-4 h-4" />
          Back to Dashboard
        </Button>
        {isAuthError && (
          <Button
            variant="secondary"
            onClick={() => router.push("/login")}
            className="gap-2"
          >
            Log in again <ChevronRight className="w-4 h-4" />
          </Button>
        )}
      </div>

      {/* Support link */}
      <p className="text-[12px] text-[var(--color-text-tertiary)] mt-6">
        Persistent issue?{" "}
        <a
          href="mailto:support@certiflow.io"
          className="text-[var(--color-primary)] hover:underline"
        >
          Contact support
        </a>
      </p>
    </div>
  );
}
