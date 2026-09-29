"use client";

import { forwardRef, isValidElement, cloneElement, type ButtonHTMLAttributes, type ReactElement } from "react";

/* ─────────────────────────────────────────────
   BUTTON — Primary UI component
   Variants: primary · secondary · ghost · destructive
   Sizes: sm · md · lg
   Supports asChild for clean Next.js <Link> integration
   ───────────────────────────────────────────── */

type ButtonVariant = "primary" | "secondary" | "outline" | "ghost" | "destructive";
type ButtonSize = "sm" | "md" | "lg";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  loading?: boolean;
  asChild?: boolean;
}

const variantStyles: Record<ButtonVariant, string> = {
  primary:
    "bg-[var(--color-primary)] text-white hover:bg-[var(--color-primary-hover)] shadow-sm active:scale-[0.98]",
  secondary:
    "bg-white text-[var(--color-text)] border border-[var(--color-border)] hover:border-[var(--color-border-hover)] hover:bg-gray-50 shadow-xs active:scale-[0.98]",
  outline:
    "bg-white text-[var(--color-text)] border border-[var(--color-border)] hover:border-[var(--color-border-hover)] hover:bg-gray-50 shadow-xs active:scale-[0.98]",
  ghost:
    "text-[var(--color-text-secondary)] hover:text-[var(--color-text)] hover:bg-black/[0.04]",
  destructive:
    "bg-[var(--color-danger)] text-white hover:bg-red-700 shadow-sm active:scale-[0.98]",
};

const sizeStyles: Record<ButtonSize, string> = {
  sm: "h-8 px-3 text-[13px] gap-1.5 rounded-[var(--radius-md)]",
  md: "h-10 px-4 text-[14px] gap-2 rounded-[var(--radius-lg)]",
  lg: "h-12 px-6 text-[15px] gap-2.5 rounded-[var(--radius-xl)]",
};

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = "primary",
      size = "md",
      loading,
      asChild = false,
      className = "",
      children,
      disabled,
      ...props
    },
    ref
  ) => {
    const combinedClassName = `
      inline-flex items-center justify-center font-medium
      transition-all duration-[var(--duration-micro)] ease-[var(--ease-out)]
      focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--color-primary)]
      disabled:opacity-50 disabled:pointer-events-none
      cursor-pointer select-none whitespace-nowrap
      ${variantStyles[variant]}
      ${sizeStyles[size]}
      ${className}
    `.trim();

    if (asChild && isValidElement(children)) {
      const child = children as ReactElement<{ className?: string }>;
      return cloneElement(child, {
        className: `${child.props.className || ""} ${combinedClassName}`.trim(),
        ...props,
      });
    }

    return (
      <button
        ref={ref}
        disabled={disabled || loading}
        className={combinedClassName}
        {...props}
      >
        {loading && (
          <svg
            className="animate-spin -ml-0.5 h-4 w-4"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
        )}
        {children}
      </button>
    );
  }
);

Button.displayName = "Button";

export { Button, type ButtonProps, type ButtonVariant, type ButtonSize };
