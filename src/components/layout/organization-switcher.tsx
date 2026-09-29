"use client";

import { useState, useRef, useEffect } from "react";
import { Building2, ChevronDown, Check, Plus, Settings } from "lucide-react";
import { useOrganization } from "@/features/organization/organization-context";
import Link from "next/link";

export function OrganizationSwitcher() {
  const { organizations, currentOrganization, switchOrganization } = useOrganization();
  const [open, setOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center gap-2.5 px-2.5 py-2 rounded-lg hover:bg-white/6 transition-colors group text-left"
        aria-expanded={open}
        aria-haspopup="true"
      >
        <div className="w-6 h-6 rounded-md bg-indigo-600 flex items-center justify-center shrink-0 shadow-sm">
          <Building2 className="w-3.5 h-3.5 text-white" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-[12px] font-semibold text-white truncate">
            {currentOrganization?.name || "CertiFlow Org"}
          </p>
          <p className="text-[10px] text-[#6B6B80] truncate">
            {currentOrganization?.plan || "Professional"} Plan
          </p>
        </div>
        <ChevronDown className="w-3.5 h-3.5 text-[#6B6B80] group-hover:text-[#A0A0B0] shrink-0" />
      </button>

      {open && (
        <div className="absolute left-0 right-0 top-full mt-1.5 bg-[#16161A] border border-white/10 rounded-xl shadow-2xl py-1.5 z-50 animate-in fade-in zoom-in-95 duration-100">
          <div className="px-3 py-1.5 text-[10px] font-bold uppercase tracking-wider text-[#6B6B80]">
            Organizations
          </div>
          <div className="max-h-48 overflow-y-auto space-y-0.5 px-1.5">
            {organizations.map((org) => {
              const isSelected = org.id === currentOrganization?.id;
              return (
                <button
                  key={org.id}
                  onClick={() => {
                    switchOrganization(org.id);
                    setOpen(false);
                  }}
                  className={`w-full flex items-center justify-between px-2 py-1.5 rounded-lg text-[12px] transition-colors ${
                    isSelected
                      ? "bg-white/10 text-white font-medium"
                      : "text-[#A0A0B0] hover:text-white hover:bg-white/5"
                  }`}
                >
                  <div className="flex items-center gap-2 min-w-0">
                    <div className="w-4 h-4 rounded bg-indigo-500/20 text-indigo-400 flex items-center justify-center text-[10px] font-bold shrink-0">
                      {org.name[0]}
                    </div>
                    <span className="truncate">{org.name}</span>
                  </div>
                  {isSelected && <Check className="w-3.5 h-3.5 text-indigo-400 shrink-0" />}
                </button>
              );
            })}
          </div>

          <div className="my-1.5 border-t border-white/6" />

          <div className="px-1.5 space-y-0.5">
            <Link
              href="/app/settings?tab=organization"
              onClick={() => setOpen(false)}
              className="flex items-center gap-2 px-2 py-1.5 rounded-lg text-[11px] text-[#A0A0B0] hover:text-white hover:bg-white/5 transition-colors"
            >
              <Settings className="w-3.5 h-3.5 text-[#6B6B80]" />
              <span>Org Settings</span>
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}
