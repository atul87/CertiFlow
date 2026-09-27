"use client";

import Link from "next/link";
import { Sparkles } from "lucide-react";

export function Footer() {
  return (
    <footer className="bg-white border-t border-[var(--color-border)] pt-16 pb-12">
      <div className="container-marketing">
        <div className="grid grid-cols-2 md:grid-cols-5 gap-8 pb-12 border-b border-[var(--color-border)]">
          {/* Brand Col */}
          <div className="col-span-2 md:col-span-1">
            <Link href="/" className="flex items-center gap-2 mb-3 group">
              <div className="w-7 h-7 rounded-lg bg-[var(--color-primary)] text-white flex items-center justify-center font-bold">
                <Sparkles className="w-3.5 h-3.5" />
              </div>
              <span className="text-[17px] font-bold tracking-tight text-[var(--color-text)]">
                CERTIFLOW
              </span>
            </Link>
            <p className="text-[13px] text-[var(--color-text-secondary)] leading-relaxed max-w-xs">
              Automate certificate creation.
            </p>
          </div>

          {/* Col 1: Product */}
          <div>
            <p className="text-[12px] font-bold uppercase tracking-wider text-gray-400 mb-4">
              Product
            </p>
            <ul className="space-y-2.5 text-[14px]">
              <li><Link href="/#features" className="text-[var(--color-text-secondary)] hover:text-black transition-colors">Features</Link></li>
              <li><Link href="/#templates" className="text-[var(--color-text-secondary)] hover:text-black transition-colors">Templates</Link></li>
              <li><Link href="/#pricing" className="text-[var(--color-text-secondary)] hover:text-black transition-colors">Pricing</Link></li>
              <li><Link href="/#demo" className="text-[var(--color-text-secondary)] hover:text-black transition-colors">Demo</Link></li>
            </ul>
          </div>

          {/* Col 2: Solutions */}
          <div>
            <p className="text-[12px] font-bold uppercase tracking-wider text-gray-400 mb-4">
              Solutions
            </p>
            <ul className="space-y-2.5 text-[14px]">
              <li><Link href="/#solutions" className="text-[var(--color-text-secondary)] hover:text-black transition-colors">Education</Link></li>
              <li><Link href="/#solutions" className="text-[var(--color-text-secondary)] hover:text-black transition-colors">Events</Link></li>
              <li><Link href="/#solutions" className="text-[var(--color-text-secondary)] hover:text-black transition-colors">Training</Link></li>
              <li><Link href="/#solutions" className="text-[var(--color-text-secondary)] hover:text-black transition-colors">Organizations</Link></li>
            </ul>
          </div>

          {/* Col 3: Resources */}
          <div>
            <p className="text-[12px] font-bold uppercase tracking-wider text-gray-400 mb-4">
              Resources
            </p>
            <ul className="space-y-2.5 text-[14px]">
              <li><Link href="/#demo" className="text-[var(--color-text-secondary)] hover:text-black transition-colors">Documentation</Link></li>
              <li><Link href="/#demo" className="text-[var(--color-text-secondary)] hover:text-black transition-colors">Guides</Link></li>
              <li><Link href="/#faq" className="text-[var(--color-text-secondary)] hover:text-black transition-colors">FAQ</Link></li>
              <li><Link href="/#demo" className="text-[var(--color-text-secondary)] hover:text-black transition-colors">Blog</Link></li>
            </ul>
          </div>

          {/* Col 4: Company */}
          <div>
            <p className="text-[12px] font-bold uppercase tracking-wider text-gray-400 mb-4">
              Company
            </p>
            <ul className="space-y-2.5 text-[14px]">
              <li><Link href="/about" className="text-[var(--color-text-secondary)] hover:text-black transition-colors">About</Link></li>
              <li><Link href="/contact" className="text-[var(--color-text-secondary)] hover:text-black transition-colors">Contact</Link></li>
              <li><Link href="/#security" className="text-[var(--color-text-secondary)] hover:text-black transition-colors">Security</Link></li>
              <li><Link href="/privacy" className="text-[var(--color-text-secondary)] hover:text-black transition-colors">Privacy</Link></li>
              <li><Link href="/terms" className="text-[var(--color-text-secondary)] hover:text-black transition-colors">Terms</Link></li>
            </ul>
          </div>
        </div>

        {/* Footer Bottom with Personality Line */}
        <div className="pt-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-[13px] text-gray-500">
          <p>© 2026 CertiFlow</p>
          <p className="text-[13px] text-gray-400 italic">
            Made for people who have better things to do than type 500 names.
          </p>
        </div>
      </div>
    </footer>
  );
}
