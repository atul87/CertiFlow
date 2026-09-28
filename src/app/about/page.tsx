import Link from "next/link";
import {
  Award,
  Sparkles,
  Zap,
  ShieldCheck,
  Users,
  Target,
  ArrowRight,
  Heart,
} from "lucide-react";
import { Navbar } from "@/components/navigation/navbar";
import { Footer } from "@/components/marketing/footer";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-[var(--color-background)] flex flex-col">
      <Navbar />

      <main className="flex-1">
        {/* Header */}
        <section className="py-20 border-b border-[var(--color-border)] bg-white text-center">
          <div className="container-marketing max-w-3xl space-y-4">
            <Badge variant="primary" className="text-[12px] px-3 py-1">
              About CertiFlow
            </Badge>
            <h1 className="text-[36px] sm:text-[48px] font-bold text-[var(--color-text)] tracking-tight">
              We Believe Credential Issuance Should Take Seconds, Not Weekends
            </h1>
            <p className="text-[16px] text-[var(--color-text-secondary)] leading-relaxed">
              Every month, thousands of educators, community organizers, and hackathon directors waste hours manually copying student names into design software. We built CertiFlow to automate the entire process.
            </p>
          </div>
        </section>

        {/* Mission & Story */}
        <section className="py-16 container-marketing max-w-4xl space-y-12">
          <div className="bg-white rounded-2xl border border-[var(--color-border)] p-8 shadow-2xs space-y-6">
            <h2 className="text-[22px] font-bold text-gray-900">Our Story</h2>
            <p className="text-[15px] text-gray-700 leading-relaxed">
              CertiFlow was born out of a simple frustration: organizing a 500-person AI hackathon and realizing that generating, renaming, and emailing 500 certificates took longer than judging the actual hackathon projects.
            </p>
            <p className="text-[15px] text-gray-700 leading-relaxed">
              Existing design tools treated bulk data as an afterthought, while enterprise credential platforms charged thousands of dollars per month with complicated contracts. We set out to create the fastest, cleanest, and most accessible certificate automation engine in the world.
            </p>
          </div>

          {/* Core Values Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white rounded-2xl border border-[var(--color-border)] p-6 space-y-3 shadow-2xs">
              <div className="w-10 h-10 rounded-xl bg-indigo-50 text-[var(--color-primary)] flex items-center justify-center">
                <Zap className="w-5 h-5" />
              </div>
              <h3 className="text-[16px] font-bold text-gray-900">Relentless Speed</h3>
              <p className="text-[13px] text-gray-600 leading-relaxed">
                48+ vector certificates per second. No spinning loaders, no waitlists, no sluggish DOM bloat.
              </p>
            </div>

            <div className="bg-white rounded-2xl border border-[var(--color-border)] p-6 space-y-3 shadow-2xs">
              <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
                <ShieldCheck className="w-5 h-5" />
              </div>
              <h3 className="text-[16px] font-bold text-gray-900">Cryptographic Integrity</h3>
              <p className="text-[13px] text-gray-600 leading-relaxed">
                Tamper-proof SHA-256 digital signatures that prevent counterfeit credentials and protect your institution&apos;s prestige.
              </p>
            </div>

            <div className="bg-white rounded-2xl border border-[var(--color-border)] p-6 space-y-3 shadow-2xs">
              <div className="w-10 h-10 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center">
                <Target className="w-5 h-5" />
              </div>
              <h3 className="text-[16px] font-bold text-gray-900">Design Precision</h3>
              <p className="text-[13px] text-gray-600 leading-relaxed">
                Pixel-perfect typography, curated font pairings, and smart auto-fit algorithms that guarantee long names never overflow.
              </p>
            </div>
          </div>
        </section>

        {/* Closing CTA */}
        <section className="py-16 border-t border-[var(--color-border)] bg-gray-900 text-white text-center">
          <div className="container-marketing max-w-2xl space-y-4">
            <h2 className="text-[28px] font-bold">Ready to see CertiFlow in action?</h2>
            <p className="text-gray-400 text-[14px]">
              Try the interactive sandbox or build your first batch of certificates free.
            </p>
            <Button size="lg" className="bg-[var(--color-primary)] text-white hover:bg-[var(--color-primary-hover)] mt-2" asChild>
              <Link href="/demo">Launch CertiFlow Studio</Link>
            </Button>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}
