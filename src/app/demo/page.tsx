"use client";

import { useState } from "react";
import Link from "next/link";
import { ArrowLeft, Play, Sparkles, CheckCircle2, ArrowRight } from "lucide-react";
import { Navbar } from "@/components/navigation/navbar";
import { Footer } from "@/components/marketing/footer";
import { InteractiveDemoSection } from "@/components/marketing/interactive-demo-section";
import { DemoVideoModal } from "@/components/marketing/demo-video-modal";
import { Button } from "@/components/ui/button";

export default function DemoPage() {
  const [videoOpen, setVideoOpen] = useState(false);

  return (
    <div className="min-h-screen flex flex-col bg-[var(--color-background)]">
      <Navbar onWatchDemo={() => setVideoOpen(true)} />

      <main className="flex-1 pt-28 pb-20">
        <div className="container-marketing mb-8 text-center max-w-2xl mx-auto">
          <Link
            href="/"
            className="inline-flex items-center gap-1.5 text-[13px] text-[var(--color-text-secondary)] hover:text-[var(--color-text)] mb-6 transition-colors"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            Back to Overview
          </Link>

          <span className="text-[12px] font-bold uppercase tracking-[0.15em] text-[var(--color-primary)] block mb-2">
            Interactive Product Sandbox
          </span>
          <h1 className="text-section mb-4">
            Try CertiFlow live in your browser
          </h1>
          <p className="text-body-lg text-[var(--color-text-secondary)] mb-8">
            Experience our 4-step bulk generation pipeline or watch the full 60-second video walkthrough.
          </p>

          <div className="flex justify-center gap-3">
            <Button
              variant="secondary"
              size="md"
              className="gap-2"
              onClick={() => setVideoOpen(true)}
            >
              <Play className="w-4 h-4 text-[var(--color-primary)]" />
              Watch 60-Second Walkthrough
            </Button>
            <Button size="md" asChild>
              <Link href="/signup">
                Sign Up for Free
                <ArrowRight className="w-4 h-4 ml-1.5" />
              </Link>
            </Button>
          </div>
        </div>

        {/* In-page interactive sandbox */}
        <InteractiveDemoSection />
      </main>

      <Footer />

      <DemoVideoModal isOpen={videoOpen} onClose={() => setVideoOpen(false)} />
    </div>
  );
}
