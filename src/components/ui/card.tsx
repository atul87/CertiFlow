"use client";

import { forwardRef, type HTMLAttributes } from "react";

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "elevated" | "interactive";
}

export const Card = forwardRef<HTMLDivElement, CardProps>(
  ({ variant = "default", className = "", children, ...props }, ref) => {
    const base = "rounded-2xl border border-[var(--color-border)] bg-white transition-all";
    const variants = {
      default: "shadow-2xs",
      elevated: "shadow-md hover:shadow-lg",
      interactive: "shadow-2xs hover:shadow-md hover:border-[var(--color-border-hover)] hover:-translate-y-0.5 cursor-pointer",
    };

    return (
      <div
        ref={ref}
        className={`${base} ${variants[variant]} ${className}`}
        {...props}
      >
        {children}
      </div>
    );
  }
);
Card.displayName = "Card";

export function CardHeader({ className = "", children, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={`p-6 border-b border-[var(--color-border)] ${className}`} {...props}>
      {children}
    </div>
  );
}

export function CardTitle({ className = "", children, ...props }: HTMLAttributes<HTMLHeadingElement>) {
  return (
    <h3 className={`text-[18px] font-bold text-[var(--color-text)] tracking-tight ${className}`} {...props}>
      {children}
    </h3>
  );
}

export function CardDescription({ className = "", children, ...props }: HTMLAttributes<HTMLParagraphElement>) {
  return (
    <p className={`text-[13px] text-[var(--color-text-secondary)] mt-1 ${className}`} {...props}>
      {children}
    </p>
  );
}

export function CardContent({ className = "", children, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={`p-6 ${className}`} {...props}>
      {children}
    </div>
  );
}

export function CardFooter({ className = "", children, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={`p-6 border-t border-[var(--color-border)] bg-[#FAFAF8]/50 flex items-center justify-between ${className}`} {...props}>
      {children}
    </div>
  );
}
