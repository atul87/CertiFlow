"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Award, X, ChevronRight, Activity } from "lucide-react";
import { NAVIGATION_CONFIG, NavItemConfig } from "@/config/navigation";
import { OrganizationSwitcher } from "./organization-switcher";
import { UserMenu } from "./user-menu";
import { api } from "@/lib/api-client";

interface AppSidebarProps {
  onClose?: () => void;
}

function SidebarNavItem({
  item,
  onClick,
}: {
  item: NavItemConfig;
  onClick?: () => void;
}) {
  const pathname = usePathname();
  const isActive = item.exact
    ? pathname === item.href
    : pathname === item.href || pathname.startsWith(item.href + "/");

  const Icon = item.icon;

  return (
    <Link
      href={item.href}
      onClick={onClick}
      className={`
        flex items-center gap-2.5 px-3 py-2 rounded-lg text-[13px] font-medium transition-all duration-150 group
        ${
          isActive
            ? "bg-white/10 text-white shadow-xs"
            : "text-[#A0A0B0] hover:text-white hover:bg-white/6"
        }
      `}
    >
      <Icon
        className={`w-4 h-4 shrink-0 transition-colors ${
          isActive ? "text-white" : "text-[#6B6B80] group-hover:text-[#A0A0B0]"
        }`}
      />
      <span className="truncate">{item.label}</span>
      {item.badge && (
        <span className="ml-auto text-[10px] font-bold px-1.5 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300">
          {item.badge}
        </span>
      )}
      {isActive && !item.badge && <ChevronRight className="w-3 h-3 ml-auto text-white/40" />}
    </Link>
  );
}

export function AppSidebar({ onClose }: AppSidebarProps) {
  const [backendOnline, setBackendOnline] = useState(false);

  useEffect(() => {
    api.health
      .check()
      .then(() => setBackendOnline(true))
      .catch(() => setBackendOnline(false));
  }, []);

  return (
    <aside className="flex flex-col h-full bg-[#0F0F12] border-r border-white/6 w-60 shrink-0">
      {/* Brand Header */}
      <div className="h-16 px-4 flex items-center justify-between border-b border-white/6">
        <Link
          href="/app"
          className="flex items-center gap-2.5 group"
          onClick={onClose}
        >
          <div className="w-8 h-8 rounded-lg bg-[#635BFF] flex items-center justify-center shadow-lg group-hover:scale-105 transition-transform">
            <Award className="w-4 h-4 text-white" />
          </div>
          <span className="text-[15px] font-bold text-white tracking-tight">
            CertiFlow
          </span>
        </Link>
        {onClose && (
          <button
            onClick={onClose}
            aria-label="Close sidebar"
            className="p-1.5 rounded-lg text-[#6B6B80] hover:text-white hover:bg-white/6 transition-colors lg:hidden"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Organization Switcher */}
      <div className="px-3 py-3 border-b border-white/6">
        <OrganizationSwitcher />
      </div>

      {/* Navigation Sections */}
      <nav className="flex-1 px-3 py-4 overflow-y-auto space-y-6 scrollbar-thin">
        {NAVIGATION_CONFIG.map((section) => (
          <div key={section.section}>
            <p className="px-3 mb-1.5 text-[10px] font-bold uppercase tracking-widest text-[#4A4A60]">
              {section.section}
            </p>
            <div className="space-y-0.5">
              {section.items.map((item) => (
                <SidebarNavItem key={item.href} item={item} onClick={onClose} />
              ))}
            </div>
          </div>
        ))}
      </nav>

      {/* Backend Status & User Profile */}
      <div className="px-3 pb-4 space-y-2 border-t border-white/6 pt-3">
        {/* Backend Connectivity Status */}
        <div
          className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-[11px] font-medium ${
            backendOnline
              ? "bg-emerald-950/60 text-emerald-400 border border-emerald-900/50"
              : "bg-amber-950/60 text-amber-400 border border-amber-900/50"
          }`}
        >
          <Activity className="w-3.5 h-3.5" />
          <span>
            {backendOnline ? "FastAPI: Connected" : "Local / Demo Mode"}
          </span>
          <span
            className={`w-1.5 h-1.5 rounded-full ml-auto ${
              backendOnline ? "bg-emerald-400 animate-pulse" : "bg-amber-400"
            }`}
          />
        </div>

        {/* User Menu */}
        <UserMenu />
      </div>
    </aside>
  );
}
