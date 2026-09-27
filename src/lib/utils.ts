/* ─────────────────────────────────────────────
   CERTIFLOW — Utility helpers
   ───────────────────────────────────────────── */

export type ClassValue =
  | string
  | number
  | boolean
  | undefined
  | null
  | ClassValue[]
  | Record<string, unknown>;

/* Tiny inline clsx implementation (no external dep needed) */
function clsx(...args: ClassValue[]): string {
  const classes: string[] = [];
  for (const arg of args) {
    if (!arg) continue;
    if (typeof arg === "string") {
      classes.push(arg);
    } else if (Array.isArray(arg)) {
      const inner = clsx(...arg);
      if (inner) classes.push(inner);
    } else if (typeof arg === "object") {
      for (const [key, value] of Object.entries(arg)) {
        if (value) classes.push(key);
      }
    }
  }
  return classes.join(" ");
}

export function cn(...inputs: ClassValue[]): string {
  return clsx(inputs);
}
