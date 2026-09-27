"use client";

import { ArrowRight, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import Link from "next/link";

export function FinalCTASection() {
  return (
    <section className="section-padding bg-[#111111] text-white relative overflow-hidden">
      {/* Background glow accent */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[400px] bg-[radial-gradient(ellipse_at_center,_rgba(99,91,255,0.2)_0%,_transparent_70%)] pointer-events-none" />

      <div className="container-marketing relative z-10">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="text-hero text-white mb-6 font-bold">
            Your next 500 certificates <br className="hidden sm:inline" />
            shouldn&apos;t take all day.
          </h2>

          <div className="flex justify-center mb-8">
            <Button
              size="lg"
              className="h-[52px] px-8 rounded-xl text-[16px] font-semibold bg-[var(--color-primary)] hover:bg-[var(--color-primary-hover)] text-white shadow-xl shadow-indigo-500/25"
              asChild
            >
              <Link href="/signup">
                Create Certificates Free
                <ArrowRight className="w-4 h-4 ml-2" />
              </Link>
            </Button>
          </div>

          {/* Simple Reassurance */}
          <p className="text-[14px] text-white/60 font-mono tracking-wide">
            Upload → Personalize → Generate
          </p>
        </div>
      </div>
    </section>
  );
}
