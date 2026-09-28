"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { motion, AnimatePresence } from "motion/react";
import { Menu, X, Play, ChevronRight, Award, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";

interface NavbarProps {
  onWatchDemo?: () => void;
}

const navLinks = [
  { label: "Product", href: "/#features" },
  { label: "Solutions", href: "/#solutions" },
  { label: "Templates", href: "/#templates" },
  { label: "Pricing", href: "/#pricing" },
];

export function Navbar({ onWatchDemo }: NavbarProps) {
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 40);
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  useEffect(() => {
    document.body.style.overflow = mobileOpen ? "hidden" : "";
    return () => {
      document.body.style.overflow = "";
    };
  }, [mobileOpen]);

  return (
    <>
      <header
        className={`
          sticky top-0 left-0 right-0 z-40 h-[72px]
          transition-all duration-200
          ${scrolled
            ? "bg-white/85 backdrop-blur-md border-b border-[var(--color-border)] shadow-xs"
            : "bg-transparent"
          }
        `}
      >
        <nav aria-label="Main Navigation" className="container-marketing flex items-center justify-between h-full">
          {/* Logo (24-28px height, modern mark) */}
          <Link
            href="/"
            className="flex items-center gap-2.5 group"
            aria-label="CertiFlow home"
          >
            <div className="w-8 h-8 rounded-lg bg-[var(--color-primary)] text-white flex items-center justify-center font-bold shadow-xs group-hover:scale-105 transition-transform">
              <Sparkles className="w-4 h-4" />
            </div>
            <span className="text-[20px] font-bold tracking-tight text-[var(--color-text)]">
              CERTIFLOW
            </span>
          </Link>

          {/* Desktop Navigation (14-15px) */}
          <div className="hidden md:flex items-center gap-1.5">
            {navLinks.map((link) => (
              <Link
                key={link.label}
                href={link.href}
                className="
                  px-3.5 py-2 text-[14px] font-medium
                  text-[var(--color-text-secondary)]
                  hover:text-[var(--color-text)]
                  hover:bg-black/[0.03]
                  rounded-lg
                  transition-colors
                "
              >
                {link.label}
              </Link>
            ))}
          </div>

          {/* Desktop Right (Demo, Log in, Create Certificates Free) */}
          <div className="hidden md:flex items-center gap-3">
            {onWatchDemo ? (
              <button
                onClick={onWatchDemo}
                className="
                  flex items-center gap-1.5 px-3 py-2
                  text-[14px] font-medium text-[var(--color-text-secondary)]
                  hover:text-[var(--color-text)]
                  transition-colors cursor-pointer
                "
              >
                <Play className="w-3.5 h-3.5 text-[var(--color-primary)]" />
                Demo
              </button>
            ) : (
              <Link
                href="/demo"
                className="
                  flex items-center gap-1.5 px-3 py-2
                  text-[14px] font-medium text-[var(--color-text-secondary)]
                  hover:text-[var(--color-text)]
                  transition-colors
                "
              >
                <Play className="w-3.5 h-3.5 text-[var(--color-primary)]" />
                Demo
              </Link>
            )}

            <Link
              href="/login"
              className="
                px-3 py-2 text-[14px] font-medium
                text-[var(--color-text-secondary)]
                hover:text-[var(--color-text)]
                transition-colors
              "
            >
              Log in
            </Link>

            <Button
              size="md"
              className="h-[44px] px-5 rounded-[10px] text-[14px] font-medium shadow-sm hover:shadow-md"
              asChild
            >
              <Link href="/signup">Create Certificates Free</Link>
            </Button>
          </div>

          {/* Mobile Hamburger */}
          <button
            onClick={() => setMobileOpen(!mobileOpen)}
            className="md:hidden p-2 text-[var(--color-text-secondary)] hover:text-[var(--color-text)] rounded-lg"
            aria-label={mobileOpen ? "Close menu" : "Open menu"}
          >
            {mobileOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </nav>
      </header>

      {/* Mobile Drawer */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            className="fixed inset-0 z-50 bg-white pt-20 px-6 pb-8 flex flex-col md:hidden"
          >
            <div className="flex justify-between items-center pb-6 border-b border-[var(--color-border)]">
              <span className="text-[18px] font-bold">CERTIFLOW</span>
              <button
                onClick={() => setMobileOpen(false)}
                aria-label="Close menu"
                className="p-2"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            <div className="flex flex-col gap-2 py-6 flex-1">
              {navLinks.map((link) => (
                <Link
                  key={link.label}
                  href={link.href}
                  onClick={() => setMobileOpen(false)}
                  className="py-3 text-[18px] font-medium border-b border-[var(--color-border)]/50 flex justify-between items-center"
                >
                  <span>{link.label}</span>
                  <ChevronRight className="w-4 h-4 text-gray-400" />
                </Link>
              ))}
              <Link
                href="/demo"
                onClick={() => setMobileOpen(false)}
                className="py-3 text-[18px] font-medium border-b border-[var(--color-border)]/50 flex justify-between items-center"
              >
                <span>Interactive Demo</span>
                <Play className="w-4 h-4 text-[var(--color-primary)]" />
              </Link>
            </div>

            <div className="space-y-3 pt-4">
              <Button
                size="lg"
                className="w-full justify-center h-12 rounded-xl text-[15px]"
                asChild
              >
                <Link href="/signup" onClick={() => setMobileOpen(false)}>
                  Create Certificates Free
                </Link>
              </Button>
              <Button
                variant="secondary"
                size="lg"
                className="w-full justify-center h-12 rounded-xl text-[15px]"
                asChild
              >
                <Link href="/login" onClick={() => setMobileOpen(false)}>
                  Log in
                </Link>
              </Button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
