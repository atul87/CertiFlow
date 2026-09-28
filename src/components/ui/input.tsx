"use client";

import { forwardRef, type InputHTMLAttributes } from "react";

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  error?: string;
  label?: string;
  hint?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, hint, className = "", id, ...props }, ref) => {
    return (
      <div className="w-full space-y-1.5">
        {label && (
          <label htmlFor={id} className="block text-[13px] font-medium text-[var(--color-text)]">
            {label}
          </label>
        )}
        <input
          ref={ref}
          id={id}
          className={`
            w-full h-10 px-3.5 rounded-lg border text-[14px]
            bg-[var(--color-background)] text-[var(--color-text)]
            placeholder:text-[var(--color-text-tertiary)]
            transition-colors duration-150
            focus:outline-none focus:bg-white focus:border-[var(--color-primary)] focus:ring-1 focus:ring-[var(--color-primary)]
            disabled:opacity-50 disabled:pointer-events-none
            ${error ? "border-red-500 focus:border-red-500 focus:ring-red-500" : "border-[var(--color-border)]"}
            ${className}
          `.trim()}
          {...props}
        />
        {hint && !error && (
          <p className="text-[12px] text-[var(--color-text-tertiary)]">{hint}</p>
        )}
        {error && (
          <p className="text-[12px] text-red-600 font-medium">{error}</p>
        )}
      </div>
    );
  }
);
Input.displayName = "Input";
