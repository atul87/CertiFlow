"use client";

import { forwardRef, type HTMLAttributes } from "react";

/* ─────────────────────────────────────────────
   BADGE — Small status / label component
   ───────────────────────────────────────────── */

type BadgeVariant = "default" | "primary" | "success" | "warning" | "danger" | "outline";

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: BadgeVariant;
}

const variantStyles: Record<BadgeVariant, string> = {
  default: "bg-[var(--color-border)] text-[var(--color-text-secondary)]",
  primary: "bg-[var(--color-primary-light)] text-[var(--color-primary)]",
  success: "bg-[var(--color-success-light)] text-[var(--color-success)]",
  warning: "bg-[var(--color-warning-light)] text-[var(--color-warning)]",
  danger: "bg-[var(--color-danger-light)] text-[var(--color-danger)]",
  outline: "border border-[var(--color-border)] text-[var(--color-text-secondary)]",
};

const Badge = forwardRef<HTMLSpanElement, BadgeProps>(
  ({ variant = "default", className = "", children, ...props }, ref) => {
    return (
      <span
        ref={ref}
        className={`
          inline-flex items-center gap-1
          px-2.5 py-0.5 text-[12px] font-medium leading-5
          rounded-full whitespace-nowrap
          ${variantStyles[variant]}
          ${className}
        `}
        {...props}
      >
        {children}
      </span>
    );
  }
);

Badge.displayName = "Badge";

export { Badge, type BadgeProps };
