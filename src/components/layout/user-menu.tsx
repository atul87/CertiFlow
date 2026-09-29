"use client";

import { useState, useRef, useEffect } from "react";
import Link from "next/link";
import { User, Settings, Users, CreditCard, LogOut, ChevronUp } from "lucide-react";
import { useAuth } from "@/features/auth/auth-guard";

export function UserMenu() {
  const { user, logout } = useAuth();
  const [open, setOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const initials = user?.name ? user.name[0].toUpperCase() : "U";

  return (
    <div className="relative" ref={menuRef}>
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center gap-2.5 px-2.5 py-2 rounded-lg hover:bg-white/6 transition-colors group cursor-pointer text-left"
        aria-expanded={open}
        aria-haspopup="true"
      >
        <div className="w-7 h-7 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white text-[11px] font-bold shrink-0 shadow-sm">
          {initials}
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-[12px] font-semibold text-[#C0C0D0] truncate">
            {user?.name || "Admin User"}
          </p>
          <p className="text-[10px] text-[#6B6B80] truncate">
            {user?.email || "demo@certiflow.io"}
          </p>
        </div>
        <ChevronUp
          className={`w-3.5 h-3.5 text-[#6B6B80] group-hover:text-[#A0A0B0] transition-transform duration-150 ${
            open ? "" : "rotate-180"
          }`}
        />
      </button>

      {open && (
        <div className="absolute left-0 right-0 bottom-full mb-1.5 bg-[#16161A] border border-white/10 rounded-xl shadow-2xl py-1.5 z-50 animate-in fade-in slide-in-from-bottom-2 duration-100">
          <div className="px-3 py-1.5 border-b border-white/6">
            <p className="text-[11px] font-semibold text-white truncate">{user?.name || "Admin User"}</p>
            <p className="text-[10px] text-[#6B6B80] truncate">{user?.email || "demo@certiflow.io"}</p>
          </div>

          <div className="p-1 space-y-0.5">
            <Link
              href="/app/settings?tab=profile"
              onClick={() => setOpen(false)}
              className="flex items-center gap-2 px-2.5 py-1.5 rounded-lg text-[12px] text-[#A0A0B0] hover:text-white hover:bg-white/5 transition-colors"
            >
              <User className="w-3.5 h-3.5 text-[#6B6B80]" />
              <span>Profile Settings</span>
            </Link>
            <Link
              href="/app/team"
              onClick={() => setOpen(false)}
              className="flex items-center gap-2 px-2.5 py-1.5 rounded-lg text-[12px] text-[#A0A0B0] hover:text-white hover:bg-white/5 transition-colors"
            >
              <Users className="w-3.5 h-3.5 text-[#6B6B80]" />
              <span>Team Members</span>
            </Link>
            <Link
              href="/app/billing"
              onClick={() => setOpen(false)}
              className="flex items-center gap-2 px-2.5 py-1.5 rounded-lg text-[12px] text-[#A0A0B0] hover:text-white hover:bg-white/5 transition-colors"
            >
              <CreditCard className="w-3.5 h-3.5 text-[#6B6B80]" />
              <span>Subscription & Billing</span>
            </Link>
          </div>

          <div className="my-1 border-t border-white/6" />

          <div className="p-1">
            <button
              onClick={() => {
                setOpen(false);
                logout();
              }}
              className="w-full flex items-center gap-2 px-2.5 py-1.5 rounded-lg text-[12px] text-red-400 hover:text-red-300 hover:bg-red-950/30 transition-colors text-left"
            >
              <LogOut className="w-3.5 h-3.5" />
              <span>Sign Out</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
