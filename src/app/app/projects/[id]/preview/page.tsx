"use client";

import { use, useState } from "react";
import Link from "next/link";
import {
  ArrowLeft,
  ArrowRight,
  Eye,
  Download,
  ChevronLeft,
  ChevronRight,
  Search,
  Sparkles,
  ShieldCheck,
  Play,
  ZoomIn,
  ZoomOut,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

interface RecipientItem {
  id: string;
  row: number;
  name: string;
  course: string;
  date: string;
  score: string;
  certificateId: string;
}

const PREVIEW_RECIPIENTS: RecipientItem[] = [
  { id: "1", row: 1, name: "Atul Kumar", course: "Advanced Deep Learning & AI Systems", date: "September 28, 2026", score: "98% (Honors Distinction)", certificateId: "CERT-AF72K9" },
  { id: "2", row: 2, name: "Rahul Sharma", course: "Advanced Deep Learning & AI Systems", date: "September 28, 2026", score: "94% (First Class)", certificateId: "CERT-BM81L2" },
  { id: "3", row: 3, name: "Priya Singh", course: "Advanced Deep Learning & AI Systems", date: "September 28, 2026", score: "96% (Honors Distinction)", certificateId: "CERT-CX93M4" },
  { id: "4", row: 4, name: "Dr. Vikramaditya Chandrasekharan", course: "Advanced Deep Learning & AI Systems", date: "September 28, 2026", score: "99% (Summa Cum Laude)", certificateId: "CERT-DY04N5" },
  { id: "5", row: 5, name: "Sneha Patel", course: "Advanced Deep Learning & AI Systems", date: "September 28, 2026", score: "91% (Pass with Merit)", certificateId: "CERT-EZ15P6" },
  { id: "6", row: 6, name: "Aanya Sharma", course: "Advanced Deep Learning & AI Systems", date: "September 28, 2026", score: "95% (Honors Distinction)", certificateId: "CERT-FA26Q7" },
  { id: "7", row: 7, name: "Rohan Verma", course: "Advanced Deep Learning & AI Systems", date: "September 28, 2026", score: "89% (Pass)", certificateId: "CERT-GB37R8" },
];

export default function CertificatePreviewStudioPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [search, setSearch] = useState("");
  const [zoom, setZoom] = useState(1.0);

  const current = PREVIEW_RECIPIENTS[selectedIndex] || PREVIEW_RECIPIENTS[0];
  const isLongName = current.name.length > 25;

  const filtered = PREVIEW_RECIPIENTS.filter((r) =>
    r.name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="h-screen w-screen flex flex-col overflow-hidden bg-[var(--color-background)]">
      {/* Top Header */}
      <header className="h-14 border-b border-[var(--color-border)] bg-white px-4 flex items-center justify-between select-none z-30 shrink-0">
        <div className="flex items-center gap-3">
          <Link
            href={`/app/projects/${id || "proj-ai-2026"}/mapping`}
            className="p-1.5 rounded-lg text-gray-500 hover:text-black hover:bg-gray-100 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div className="h-4 w-px bg-gray-200" />
          <span className="font-semibold text-[14px] text-gray-900">
            Live Recipient Preview Studio
          </span>
          <Badge variant="outline" className="text-[10px] font-mono text-gray-500">
            500 Total Records
          </Badge>
        </div>

        {/* Recipient Stepper */}
        <div className="flex items-center gap-2 bg-gray-50 px-3 py-1 rounded-lg border border-[var(--color-border)]">
          <button
            onClick={() => selectedIndex > 0 && setSelectedIndex(selectedIndex - 1)}
            disabled={selectedIndex === 0}
            className="p-1 rounded text-gray-500 hover:text-black disabled:opacity-30"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          <span className="text-[12px] font-medium text-gray-700">
            Record {selectedIndex + 1} of {PREVIEW_RECIPIENTS.length}: <strong>{current.name}</strong>
          </span>
          <button
            onClick={() => selectedIndex < PREVIEW_RECIPIENTS.length - 1 && setSelectedIndex(selectedIndex + 1)}
            disabled={selectedIndex === PREVIEW_RECIPIENTS.length - 1}
            className="p-1 rounded text-gray-500 hover:text-black disabled:opacity-30"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2">
          {/* Zoom controls */}
          <div className="flex items-center bg-gray-100 rounded-lg p-0.5 text-[12px]">
            <button
              onClick={() => setZoom(Math.max(0.7, zoom - 0.15))}
              className="p-1.5 text-gray-600 hover:text-black"
              title="Zoom Out"
            >
              <ZoomOut className="w-3.5 h-3.5" />
            </button>
            <span className="px-2 font-mono text-gray-700">{Math.round(zoom * 100)}%</span>
            <button
              onClick={() => setZoom(Math.min(1.4, zoom + 0.15))}
              className="p-1.5 text-gray-600 hover:text-black"
              title="Zoom In"
            >
              <ZoomIn className="w-3.5 h-3.5" />
            </button>
          </div>

          <Button size="sm" asChild>
            <Link href={`/app/projects/${id || "proj-ai-2026"}/generate`}>
              <Play className="w-3.5 h-3.5 mr-1" />
              Batch Engine →
            </Link>
          </Button>
        </div>
      </header>

      {/* Main Studio Viewport */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Sidebar: Recipient List */}
        <aside className="w-72 bg-white border-r border-[var(--color-border)] flex flex-col shrink-0">
          <div className="p-3 border-b border-[var(--color-border)]">
            <div className="relative">
              <Search className="w-3.5 h-3.5 text-gray-400 absolute left-2.5 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search recipient..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full pl-8 pr-2.5 py-1.5 text-[12px] bg-gray-50 border border-[var(--color-border)] rounded-lg focus:outline-none"
              />
            </div>
          </div>

          <div className="flex-1 overflow-y-auto divide-y divide-gray-100">
            {filtered.map((r, i) => {
              const isSelected = r.id === current.id;
              return (
                <div
                  key={r.id}
                  onClick={() => setSelectedIndex(PREVIEW_RECIPIENTS.findIndex((x) => x.id === r.id))}
                  className={`p-3 text-[12px] cursor-pointer transition-colors ${
                    isSelected
                      ? "bg-indigo-50/70 border-l-3 border-[var(--color-primary)] font-semibold text-gray-900"
                      : "hover:bg-gray-50 text-gray-700"
                  }`}
                >
                  <div className="flex justify-between items-center">
                    <span className="truncate">{r.name}</span>
                    <span className="font-mono text-[10px] text-gray-400">#{r.row}</span>
                  </div>
                  <div className="flex justify-between items-center mt-0.5 text-[10px] text-gray-500 font-mono">
                    <span>{r.score}</span>
                    <span>{r.certificateId}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </aside>

        {/* Center: Certificate Preview Canvas */}
        <div className="flex-1 bg-[#ECECE9] overflow-auto flex items-center justify-center p-8 relative">
          <div
            style={{
              transform: `scale(${zoom})`,
              transformOrigin: "center center",
              transition: "transform 0.15s ease-out",
            }}
            className="shrink-0"
          >
            {/* A4 Landscape Preview Card */}
            <div
              className="w-[960px] h-[678px] bg-white rounded-lg shadow-2xl relative overflow-hidden flex flex-col justify-between p-12 text-center"
              style={{
                backgroundImage: "radial-gradient(circle at 50% 50%, #FAF9F5 0%, #F5F3EB 100%)",
              }}
            >
              {/* Ornate Gold Borders */}
              <div className="absolute inset-5 border-2 border-[#D4AF37] pointer-events-none rounded-sm" />
              <div className="absolute inset-7 border border-[#D4AF37]/50 pointer-events-none rounded-xs" />
              <div className="absolute top-6 left-6 w-10 h-10 border-t-2 border-l-2 border-[#D4AF37] pointer-events-none" />
              <div className="absolute top-6 right-6 w-10 h-10 border-t-2 border-r-2 border-[#D4AF37] pointer-events-none" />
              <div className="absolute bottom-6 left-6 w-10 h-10 border-b-2 border-l-2 border-[#D4AF37] pointer-events-none" />
              <div className="absolute bottom-6 right-6 w-10 h-10 border-b-2 border-r-2 border-[#D4AF37] pointer-events-none" />

              {/* Header */}
              <div className="space-y-2 mt-4">
                <p className="text-[14px] font-bold text-[var(--color-primary)] uppercase tracking-widest">
                  ACADEMY OF ADVANCED COMPUTING & RESEARCH
                </p>
                <h1 className="text-[40px] font-bold font-serif text-gray-900 tracking-tight">
                  Certificate of Excellence
                </h1>
                <p className="text-[12px] font-semibold text-gray-500 uppercase tracking-widest">
                  THIS CREDENTIAL IS PROUDLY CONFERRED UPON
                </p>
              </div>

              {/* Dynamic Recipient Name & Course */}
              <div className="space-y-3 my-auto">
                <div className="relative inline-block">
                  <h2
                    className={`font-serif font-bold text-gray-950 transition-all ${
                      isLongName ? "text-[32px]" : "text-[46px]"
                    }`}
                  >
                    {current.name}
                  </h2>
                  {isLongName && (
                    <div className="absolute -top-6 right-0 bg-emerald-600 text-white text-[9px] font-mono font-bold px-2 py-0.5 rounded shadow">
                      ✓ Smart Text Fit: Scaled 46px → 32px
                    </div>
                  )}
                </div>

                <p className="text-[14px] text-gray-600 max-w-xl mx-auto leading-relaxed">
                  for successfully mastering and completing the intensive technical curriculum in
                </p>

                <p className="text-[22px] font-bold text-[#1E1B4B]">
                  {current.course}
                </p>

                <p className="text-[14px] font-semibold text-emerald-700">
                  {current.score}
                </p>
              </div>

              {/* Bottom Row: Signatures, Seal & Scannable QR */}
              <div className="grid grid-cols-3 items-end pt-6 border-t border-gray-200 text-[12px]">
                {/* Dean Signature */}
                <div className="text-left space-y-1">
                  <p className="font-serif italic text-[22px] text-gray-800 leading-none">
                    Dr. Arthur Pendelton
                  </p>
                  <div className="w-36 h-px bg-gray-400" />
                  <p className="text-[10px] font-bold uppercase tracking-wider text-gray-800">
                    Dr. Arthur Pendelton
                  </p>
                  <p className="text-[9px] text-gray-500">
                    Chancellor & Dean of Engineering
                  </p>
                </div>

                {/* Golden Seal */}
                <div className="flex flex-col items-center">
                  <div className="w-16 h-16 rounded-full border-2 border-[#D97706] bg-[#FEF3C7] flex flex-col items-center justify-center text-[#B45309] shadow-sm">
                    <span className="text-[7px] font-extrabold uppercase tracking-tight">OFFICIAL</span>
                    <span className="text-[6px] font-bold tracking-widest">SEAL</span>
                  </div>
                  <span className="text-[10px] text-gray-400 mt-1">{current.date}</span>
                </div>

                {/* QR Code Verification */}
                <div className="text-right flex flex-col items-end space-y-1">
                  <div className="w-16 h-16 bg-white p-1 rounded border border-gray-300 shadow-2xs flex items-center justify-center">
                    <div className="w-14 h-14 border border-dashed border-gray-400 flex flex-col items-center justify-center text-[7px] font-mono">
                      <span>QR HASH</span>
                      <ShieldCheck className="w-4 h-4 text-[var(--color-primary)] mt-0.5" />
                    </div>
                  </div>
                  <span className="font-mono text-[9px] font-bold text-gray-800">
                    {current.certificateId}
                  </span>
                  <span className="text-[8px] text-[var(--color-primary)] font-semibold uppercase">
                    Scan to Verify
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
