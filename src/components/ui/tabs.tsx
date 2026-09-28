"use client";

import { createContext, useContext, useState, type ReactNode } from "react";

interface TabsContextType {
  value: string;
  onValueChange: (val: string) => void;
}

const TabsContext = createContext<TabsContextType | null>(null);

export function Tabs({
  value,
  defaultValue,
  onValueChange,
  children,
  className = "",
}: {
  value?: string;
  defaultValue?: string;
  onValueChange?: (val: string) => void;
  children: ReactNode;
  className?: string;
}) {
  const [internalValue, setInternalValue] = useState(defaultValue || "");
  const activeValue = value !== undefined ? value : internalValue;

  const handleValueChange = (newVal: string) => {
    if (value === undefined) setInternalValue(newVal);
    onValueChange?.(newVal);
  };

  return (
    <TabsContext.Provider value={{ value: activeValue, onValueChange: handleValueChange }}>
      <div className={`w-full ${className}`}>{children}</div>
    </TabsContext.Provider>
  );
}

export function TabsList({
  children,
  className = "",
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <div
      className={`inline-flex items-center gap-1 p-1 rounded-xl bg-[var(--color-background)] border border-[var(--color-border)] ${className}`}
    >
      {children}
    </div>
  );
}

export function TabsTrigger({
  value,
  children,
  className = "",
}: {
  value: string;
  children: ReactNode;
  className?: string;
}) {
  const context = useContext(TabsContext);
  if (!context) throw new Error("TabsTrigger must be used within Tabs");
  const isActive = context.value === value;

  return (
    <button
      type="button"
      onClick={() => context.onValueChange(value)}
      className={`
        px-3.5 py-1.5 text-[13px] font-medium rounded-lg transition-all select-none cursor-pointer
        ${
          isActive
            ? "bg-white text-[var(--color-text)] shadow-2xs font-semibold"
            : "text-[var(--color-text-secondary)] hover:text-[var(--color-text)]"
        }
        ${className}
      `.trim()}
    >
      {children}
    </button>
  );
}

export function TabsContent({
  value,
  children,
  className = "",
}: {
  value: string;
  children: ReactNode;
  className?: string;
}) {
  const context = useContext(TabsContext);
  if (!context) throw new Error("TabsContent must be used within Tabs");
  if (context.value !== value) return null;

  return <div className={`mt-4 ${className}`}>{children}</div>;
}
