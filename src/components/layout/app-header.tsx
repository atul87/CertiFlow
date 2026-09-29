"use client";

import { Menu, Search } from "lucide-react";
import { NotificationBell } from "@/components/ui/notifications";

interface AppHeaderProps {
  onOpenMobileSidebar: () => void;
  onOpenCommandPalette: () => void;
}

export function AppHeader({
  onOpenMobileSidebar,
  onOpenCommandPalette,
}: AppHeaderProps) {
  return (
    <header className="h-16 border-b border-[var(--color-border)] bg-white/80 backdrop-blur-md sticky top-0 z-30 flex items-center px-4 lg:px-6 gap-4">
      {/* Mobile Menu Button */}
      <button
        onClick={onOpenMobileSidebar}
        aria-label="Open navigation menu"
        className="lg:hidden p-2 rounded-lg border border-[var(--color-border)] text-gray-600 hover:bg-gray-50 transition-colors"
      >
        <Menu className="w-4 h-4" />
      </button>

      {/* Global Search Trigger (Cmd + K) */}
      <div className="flex-1 max-w-md">
        <button
          id="command-palette-trigger"
          data-testid="command-palette-trigger"
          onClick={onOpenCommandPalette}
          className="flex items-center gap-2.5 w-full px-3.5 py-2 rounded-xl border border-[var(--color-border)] bg-[var(--color-background)] text-[13px] text-[var(--color-text-secondary)] hover:border-[var(--color-border-hover)] transition-colors text-left group shadow-xs"
        >
          <Search className="w-3.5 h-3.5 shrink-0 text-gray-400 group-hover:text-gray-600" />
          <span className="truncate">Search certificates, templates, recipients…</span>
          <kbd className="ml-auto text-[11px] bg-gray-100 text-gray-400 border border-gray-200 px-1.5 py-0.5 rounded font-mono hidden sm:inline">
            ⌘K
          </kbd>
        </button>
      </div>

      <div className="flex items-center gap-3 ml-auto">
        {/* Real-time Notification Center */}
        <NotificationBell />
      </div>
    </header>
  );
}
