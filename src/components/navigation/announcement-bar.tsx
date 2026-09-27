"use client";

import Link from "next/link";
import { ArrowRight, Sparkles } from "lucide-react";

export function AnnouncementBar() {
  return (
    <aside aria-label="Announcement" className="h-9 bg-[#111111] text-white flex items-center justify-center px-4 text-[13px] font-medium tracking-tight relative z-50">
      <Link
        href="/#demo"
        className="inline-flex items-center gap-2 hover:text-white/80 transition-colors group cursor-pointer"
      >
        <span className="flex items-center gap-1.5 text-[var(--color-primary-light)] font-semibold">
          <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
          <span>New:</span>
        </span>
        <span>Create hundreds of certificates from one CSV</span>
        <ArrowRight className="w-3.5 h-3.5 text-white/60 group-hover:translate-x-0.5 group-hover:text-white transition-all" />
      </Link>
    </aside>
  );
}
