"use client";

import { useState } from "react";
import Link from "next/link";
import {
  Award,
  Sparkles,
  Sliders,
  CheckCircle2,
  ArrowRight,
  Eye,
  Download,
} from "lucide-react";
import { Navbar } from "@/components/navigation/navbar";
import { Footer } from "@/components/marketing/footer";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Modal } from "@/components/ui/modal";

interface TemplateItem {
  id: string;
  name: string;
  category: "academic" | "tech" | "executive" | "minimal";
  aspect: "Landscape (A4)" | "Portrait (A4)";
  description: string;
  accent: string;
  recipientSample: string;
  courseSample: string;
}

const TEMPLATES: TemplateItem[] = [
  {
    id: "academic-gold",
    name: "Academic Honors & Excellence",
    category: "academic",
    aspect: "Landscape (A4)",
    description: "Traditional prestige layout featuring ornate guilloche fillets, classical Roman typography, and an official gold seal.",
    accent: "#D4AF37",
    recipientSample: "Atul Kumar",
    courseSample: "Master of Computer Science (AI & Robotics)",
  },
  {
    id: "modern-tech",
    name: "Modern Tech & Global Hackathon",
    category: "tech",
    aspect: "Landscape (A4)",
    description: "Designed for developer summits, hackathons, and web3 events. Futuristic layout with monospaced IDs and cyber-blue gradients.",
    accent: "#3B82F6",
    recipientSample: "Rahul Sharma",
    courseSample: "First Place Winner · Global AI Hackathon 2026",
  },
  {
    id: "executive-leadership",
    name: "Executive Leadership Summit",
    category: "executive",
    aspect: "Landscape (A4)",
    description: "Clean Swiss typography with high whitespace and rich charcoal typography for corporate workshops and executive masterclasses.",
    accent: "#18181B",
    recipientSample: "Priya Singh",
    courseSample: "Executive Strategic Leadership & Venture Finance",
  },
  {
    id: "data-science-bootcamp",
    name: "Data Science & Cloud Certificate",
    category: "tech",
    aspect: "Landscape (A4)",
    description: "Modern split layout with verification block, credential level badge, and digital signature line.",
    accent: "#635BFF",
    recipientSample: "Sneha Patel",
    courseSample: "Full-Stack Data Engineering & ML Ops",
  },
  {
    id: "minimalist-diploma",
    name: "Minimalist Modern Diploma",
    category: "minimal",
    aspect: "Landscape (A4)",
    description: "Understated elegance with subtle corner flourishes, centered serif hierarchy, and clean metadata ribbon.",
    accent: "#059669",
    recipientSample: "Marcus Vance",
    courseSample: "Applied Systems Architecture Certification",
  },
  {
    id: "conference-speaker",
    name: "Keynote Speaker & Presenter",
    category: "executive",
    aspect: "Landscape (A4)",
    description: "Bold presenter honor certificate acknowledging keynote speakers, panelists, and workshop instructors.",
    accent: "#D97706",
    recipientSample: "Dr. Vikramaditya Chandrasekharan",
    courseSample: "Distinguished Keynote Speaker · DevCon 2026",
  },
];

export default function TemplatesPage() {
  const [activeCategory, setActiveCategory] = useState<string>("all");
  const [previewTemplate, setPreviewTemplate] = useState<TemplateItem | null>(null);

  const filtered = TEMPLATES.filter(
    (t) => activeCategory === "all" || t.category === activeCategory
  );

  return (
    <div className="min-h-screen bg-[var(--color-background)] flex flex-col">
      <Navbar />

      <main className="flex-1">
        {/* Header */}
        <section className="py-20 border-b border-[var(--color-border)] bg-white text-center">
          <div className="container-marketing max-w-3xl space-y-4">
            <Badge variant="primary" className="text-[12px] px-3 py-1">
              Template Showroom
            </Badge>
            <h1 className="text-[36px] sm:text-[48px] font-bold text-[var(--color-text)] tracking-tight">
              Pre-Designed, Print-Ready Certificate Templates
            </h1>
            <p className="text-[16px] text-[var(--color-text-secondary)] leading-relaxed">
              Every template is built with 300 DPI vector dimensions, dynamic CSV tag placeholders, and scannable QR verification spots.
            </p>
          </div>
        </section>

        {/* Categories Bar */}
        <section className="py-6 border-b border-[var(--color-border)] bg-white sticky top-16 z-20">
          <div className="container-marketing flex items-center justify-between overflow-x-auto gap-4">
            <div className="flex gap-2">
              {[
                { id: "all", label: "All Templates" },
                { id: "academic", label: "Academic & University" },
                { id: "tech", label: "Tech & Hackathons" },
                { id: "executive", label: "Corporate & Executive" },
                { id: "minimal", label: "Minimalist Modern" },
              ].map((c) => (
                <button
                  key={c.id}
                  onClick={() => setActiveCategory(c.id)}
                  className={`px-4 py-2 rounded-xl text-[13px] font-semibold transition-all whitespace-nowrap ${
                    activeCategory === c.id
                      ? "bg-[var(--color-primary)] text-white shadow-xs"
                      : "bg-gray-100 text-gray-600 hover:text-black hover:bg-gray-200"
                  }`}
                >
                  {c.label}
                </button>
              ))}
            </div>

            <span className="text-[12px] font-mono text-gray-500 hidden sm:inline">
              Showing {filtered.length} curated templates
            </span>
          </div>
        </section>

        {/* Template Cards Grid */}
        <section className="py-16 container-marketing">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {filtered.map((t) => (
              <div
                key={t.id}
                className="bg-white rounded-2xl border border-[var(--color-border)] overflow-hidden shadow-2xs hover:shadow-md hover:border-[var(--color-border-hover)] transition-all flex flex-col justify-between group"
              >
                {/* Visual Certificate Preview Canvas Thumbnail */}
                <div
                  className="aspect-[1.414/1] bg-[#FAF9F5] p-6 relative flex flex-col justify-between border-b border-[var(--color-border)] cursor-pointer"
                  onClick={() => setPreviewTemplate(t)}
                >
                  <div
                    className="absolute inset-3 border pointer-events-none rounded-xs"
                    style={{ borderColor: t.accent }}
                  />

                  <div className="flex justify-between items-center text-[9px] uppercase tracking-wider font-bold text-gray-400">
                    <span>CertiFlow Template</span>
                    <span className="font-mono">{t.aspect}</span>
                  </div>

                  <div className="text-center my-auto">
                    <p className="text-[10px] uppercase font-semibold text-gray-500 tracking-wider">
                      Presented to
                    </p>
                    <p className="text-[18px] font-bold font-serif text-gray-900 mt-0.5">
                      {t.recipientSample}
                    </p>
                    <p className="text-[11px] text-[var(--color-primary)] font-medium mt-1 truncate">
                      {t.courseSample}
                    </p>
                  </div>

                  <div className="flex justify-between items-center pt-2 border-t border-gray-200 text-[8px] text-gray-400">
                    <span>Sep 28, 2026</span>
                    <div className="w-4 h-4 border flex items-center justify-center font-mono text-[6px]">QR</div>
                    <span>#CERT-SAMPLE</span>
                  </div>

                  {/* Hover overlay */}
                  <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
                    <Button size="sm" variant="secondary" className="bg-white text-black shadow-lg">
                      <Eye className="w-3.5 h-3.5 mr-1" />
                      Preview
                    </Button>
                  </div>
                </div>

                {/* Info & Action */}
                <div className="p-5 space-y-3">
                  <div>
                    <h3 className="text-[16px] font-bold text-gray-900">{t.name}</h3>
                    <p className="text-[12px] text-gray-500 mt-1 line-clamp-2 leading-relaxed">
                      {t.description}
                    </p>
                  </div>

                  <div className="pt-2 flex items-center justify-between">
                    <span className="text-[11px] font-semibold text-gray-500 uppercase bg-gray-100 px-2 py-0.5 rounded">
                      {t.category}
                    </span>

                    <Button size="sm" asChild>
                      <Link href="/app/projects/proj-ai-2026/editor">
                        Use Template
                        <ArrowRight className="w-3 h-3 ml-1" />
                      </Link>
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>
      </main>

      {/* PREVIEW MODAL */}
      {previewTemplate && (
        <Modal
          isOpen={!!previewTemplate}
          onClose={() => setPreviewTemplate(null)}
          title={previewTemplate.name}
          description="High-resolution preview with sample recipient and dynamic placeholder mapping."
          size="lg"
        >
          <div className="space-y-4 py-2">
            <div className="aspect-[1.414/1] bg-[#FAF9F5] rounded-xl border-2 p-8 text-center flex flex-col justify-between relative shadow-lg" style={{ borderColor: previewTemplate.accent }}>
              <div className="absolute inset-3 border pointer-events-none rounded" style={{ borderColor: previewTemplate.accent }} />
              <p className="text-[11px] uppercase font-bold tracking-widest text-gray-500">
                Official Credential Presentation
              </p>
              <div>
                <h2 className="text-[28px] font-bold font-serif text-gray-900">
                  {previewTemplate.recipientSample}
                </h2>
                <p className="text-[14px] text-[var(--color-primary)] font-medium mt-1">
                  {previewTemplate.courseSample}
                </p>
              </div>
              <div className="flex items-center justify-between border-t border-gray-200 pt-3 text-[11px] text-gray-500">
                <span>Sep 28, 2026</span>
                <span className="font-mono font-bold">CERT-SAMPLE-2026</span>
                <span className="text-emerald-700 font-semibold">✓ Verified</span>
              </div>
            </div>

            <div className="flex justify-between items-center pt-2">
              <Button variant="secondary" onClick={() => setPreviewTemplate(null)}>
                Back
              </Button>
              <Button asChild>
                <Link href="/app/projects/proj-ai-2026/editor">
                  Open in Canvas Editor
                  <ArrowRight className="w-3.5 h-3.5 ml-1.5" />
                </Link>
              </Button>
            </div>
          </div>
        </Modal>
      )}

      <Footer />
    </div>
  );
}
