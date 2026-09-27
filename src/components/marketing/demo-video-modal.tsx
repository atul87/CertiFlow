"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "motion/react";
import {
  Play,
  Pause,
  X,
  RotateCcw,
  CheckCircle2,
  FileSpreadsheet,
  Layers,
  Sparkles,
  Download,
  QrCode,
  Volume2,
  VolumeX,
} from "lucide-react";
import { Button } from "@/components/ui/button";

interface DemoVideoModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const scenes = [
  {
    range: [0, 8],
    title: "1. Upload Certificate Template",
    desc: "Import high-resolution background template (PDF, PNG, or Figma export).",
    badge: "00:00 - 00:08",
  },
  {
    range: [8, 16],
    title: "2. Connect Recipient CSV",
    desc: "Import student/attendee spreadsheet with 500 records.",
    badge: "00:08 - 00:16",
  },
  {
    range: [16, 26],
    title: "3. Map {{NAME}} & Dynamic Variables",
    desc: "Auto-detect columns and position dynamic placeholders.",
    badge: "00:16 - 00:26",
  },
  {
    range: [26, 38],
    title: "4. Live Recipient Preview",
    desc: "Cycle through real attendee records to verify text wrapping.",
    badge: "00:26 - 00:38",
  },
  {
    range: [38, 50],
    title: "5. Batch Generation Engine",
    desc: "Asynchronous parallel document rendering (45 certs/sec).",
    badge: "00:38 - 00:50",
  },
  {
    range: [50, 60],
    title: "6. Instant ZIP & Dynamic QR Verification",
    desc: "Download full archive & verify tamper-proof QR codes.",
    badge: "00:50 - 01:00",
  },
];

export function DemoVideoModal({ isOpen, onClose }: DemoVideoModalProps) {
  const [seconds, setSeconds] = useState(0);
  const [isPlaying, setIsPlaying] = useState(true);
  const [isMuted, setIsMuted] = useState(true);

  // Video playback timer
  useEffect(() => {
    let interval: any;
    if (isOpen && isPlaying) {
      interval = setInterval(() => {
        setSeconds((prev) => {
          if (prev >= 60) {
            return 0; // loop
          }
          return prev + 1;
        });
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isOpen, isPlaying]);

  if (!isOpen) return null;

  const currentScene = scenes.find((s) => seconds >= s.range[0] && seconds < s.range[1]) || scenes[0];

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-3 md:p-6"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.95, opacity: 0 }}
          onClick={(e) => e.stopPropagation()}
          className="bg-[#111111] text-white rounded-2xl max-w-4xl w-full overflow-hidden shadow-2xl border border-white/10 flex flex-col"
        >
          {/* Modal Header */}
          <div className="flex items-center justify-between px-6 py-4 border-b border-white/10 bg-[#161616]">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
              <h3 className="text-[14px] font-semibold tracking-wide">
                CertiFlow 60-Second Product Walkthrough
              </h3>
            </div>
            <button
              onClick={onClose}
              className="w-8 h-8 rounded-full bg-white/10 hover:bg-white/20 text-white flex items-center justify-center transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Interactive Screen Simulation Canvas */}
          <div className="relative aspect-[16/10] bg-[#0A0A0A] p-6 flex flex-col justify-between overflow-hidden">
            {/* Top Bar inside simulation */}
            <div className="flex items-center justify-between z-10">
              <div className="bg-white/10 backdrop-blur px-3 py-1 rounded-md text-[11px] font-mono text-white/80">
                Stage: {currentScene.title}
              </div>
              <div className="text-[12px] font-mono text-emerald-400 bg-emerald-950/60 border border-emerald-500/30 px-2.5 py-0.5 rounded">
                00:{seconds < 10 ? `0${seconds}` : seconds} / 01:00
              </div>
            </div>

            {/* Dynamic Stage Rendering based on timestamp */}
            <div className="my-auto flex items-center justify-center py-4">
              {/* Scene 1: Upload (0-8s) */}
              {seconds < 8 && (
                <motion.div
                  key="scene1"
                  initial={{ opacity: 0, scale: 0.92 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="w-full max-w-md bg-[#1c1c1c] border border-white/10 rounded-2xl p-6 text-center space-y-4 shadow-xl"
                >
                  <div className="w-12 h-12 rounded-xl bg-[var(--color-primary)] text-white flex items-center justify-center mx-auto">
                    <Sparkles className="w-6 h-6" />
                  </div>
                  <h4 className="text-[18px] font-bold">Uploading Certificate Template</h4>
                  <div className="border border-dashed border-white/20 rounded-xl p-4 bg-white/5">
                    <p className="text-[12px] text-emerald-400 font-mono">✓ university_diploma_2026.pdf (300 DPI)</p>
                    <p className="text-[11px] text-white/50 mt-1">Parsed canvas dimensions: 3508 × 2480px (A4 Landscape)</p>
                  </div>
                </motion.div>
              )}

              {/* Scene 2: Upload CSV (8-16s) */}
              {seconds >= 8 && seconds < 16 && (
                <motion.div
                  key="scene2"
                  initial={{ opacity: 0, scale: 0.92 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="w-full max-w-lg bg-[#1c1c1c] border border-white/10 rounded-2xl p-6 space-y-4 shadow-xl"
                >
                  <div className="flex items-center justify-between border-b border-white/10 pb-3">
                    <span className="text-[13px] font-bold text-white flex items-center gap-2">
                      <FileSpreadsheet className="w-4 h-4 text-emerald-400" />
                      500 Attendees Loaded
                    </span>
                    <span className="text-[11px] font-mono text-white/60">attendees_master.csv</span>
                  </div>
                  <div className="space-y-1.5 font-mono text-[11px]">
                    <div className="flex justify-between bg-white/5 p-2 rounded">
                      <span className="text-white">Atul Kumar</span>
                      <span className="text-white/60">AI Workshop 2026</span>
                      <span className="text-emerald-400">98% Score</span>
                    </div>
                    <div className="flex justify-between bg-white/5 p-2 rounded">
                      <span className="text-white">Rahul Sharma</span>
                      <span className="text-white/60">AI Workshop 2026</span>
                      <span className="text-emerald-400">92% Score</span>
                    </div>
                    <div className="flex justify-between bg-white/5 p-2 rounded">
                      <span className="text-white">Priya Singh</span>
                      <span className="text-white/60">AI Workshop 2026</span>
                      <span className="text-emerald-400">95% Score</span>
                    </div>
                  </div>
                </motion.div>
              )}

              {/* Scene 3: Map Name (16-26s) */}
              {seconds >= 16 && seconds < 26 && (
                <motion.div
                  key="scene3"
                  initial={{ opacity: 0, scale: 0.92 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="w-full max-w-md bg-[#1c1c1c] border border-white/10 rounded-2xl p-6 space-y-4 shadow-xl"
                >
                  <div className="text-center">
                    <h4 className="text-[16px] font-bold">Auto-Binding Template Tags</h4>
                    <p className="text-[12px] text-white/60">Connecting spreadsheet columns to typography layers</p>
                  </div>
                  <div className="space-y-2">
                    {[
                      { tag: "{{NAME}}", col: "Full Name Column" },
                      { tag: "{{COURSE}}", col: "Course Column" },
                      { tag: "{{DATE}}", col: "Completion Date Column" },
                      { tag: "{{QR_VERIFY}}", col: "Encrypted QR Code" },
                    ].map((m, i) => (
                      <div key={i} className="flex items-center justify-between p-2 rounded bg-white/5 text-[12px]">
                        <span className="text-[var(--color-primary-light)] font-mono">{m.tag}</span>
                        <span className="text-white/40">→</span>
                        <span className="text-emerald-400 font-medium">{m.col} ✓</span>
                      </div>
                    ))}
                  </div>
                </motion.div>
              )}

              {/* Scene 4: Preview (26-38s) */}
              {seconds >= 26 && seconds < 38 && (
                <motion.div
                  key="scene4"
                  initial={{ opacity: 0, scale: 0.92 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="w-full max-w-md bg-white text-black rounded-xl p-6 shadow-2xl border-4 border-amber-300 text-center relative"
                >
                  <p className="text-[8px] uppercase tracking-[0.2em] text-gray-500 font-bold">
                    Live Record #{seconds % 2 === 0 ? "001" : "002"}
                  </p>
                  <h3 className="text-[24px] font-bold font-serif my-2">
                    {seconds % 2 === 0 ? "Atul Kumar" : "Priya Singh"}
                  </h3>
                  <p className="text-[11px] text-gray-600">
                    has met all requirements for AI Engineering Certification
                  </p>
                  <div className="flex justify-between items-center pt-3 border-t border-gray-200 mt-4 text-[9px] text-gray-500 font-mono">
                    <span>Issued: Sep 2026</span>
                    <div className="w-5 h-5 bg-black text-white flex items-center justify-center font-bold text-[6px]">
                      QR
                    </div>
                    <span>ID: CERT-88910</span>
                  </div>
                </motion.div>
              )}

              {/* Scene 5: Generate (38-50s) */}
              {seconds >= 38 && seconds < 50 && (
                <motion.div
                  key="scene5"
                  initial={{ opacity: 0, scale: 0.92 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="w-full max-w-md bg-[#1c1c1c] border border-white/10 rounded-2xl p-6 text-center space-y-4 shadow-xl"
                >
                  <h4 className="text-[18px] font-bold">Rendering 500 Unique Certificates</h4>
                  <div className="h-4 bg-white/10 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-emerald-500 rounded-full transition-all duration-500"
                      style={{ width: `${((seconds - 38) / 12) * 100}%` }}
                    />
                  </div>
                  <div className="flex justify-between text-[12px] font-mono text-white/70">
                    <span>{Math.round(((seconds - 38) / 12) * 500)} / 500 produced</span>
                    <span className="text-emerald-400">42 certs/sec</span>
                  </div>
                </motion.div>
              )}

              {/* Scene 6: Finish + QR (50-60s) */}
              {seconds >= 50 && (
                <motion.div
                  key="scene6"
                  initial={{ opacity: 0, scale: 0.92 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="w-full max-w-md bg-[#1c1c1c] border border-emerald-500/40 rounded-2xl p-6 text-center space-y-4 shadow-xl"
                >
                  <div className="w-12 h-12 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center mx-auto">
                    <CheckCircle2 className="w-7 h-7" />
                  </div>
                  <h4 className="text-[18px] font-bold text-white">500 Certificates Ready!</h4>
                  <p className="text-[12px] text-white/70">
                    All vector PDFs compiled with embedded verification QRs.
                  </p>
                  <div className="flex justify-center gap-3">
                    <span className="px-4 py-2 rounded-lg bg-emerald-600 text-white text-[12px] font-semibold flex items-center gap-1.5">
                      <Download className="w-3.5 h-3.5" />
                      500_Certificates.zip (84 MB)
                    </span>
                  </div>
                </motion.div>
              )}
            </div>

            {/* Video Controls & Scrubber */}
            <div className="bg-black/60 backdrop-blur-md rounded-xl p-3 border border-white/10 space-y-2 z-10">
              <div className="h-1.5 bg-white/20 rounded-full overflow-hidden cursor-pointer">
                <div
                  className="h-full bg-[var(--color-primary)] transition-all duration-300"
                  style={{ width: `${(seconds / 60) * 100}%` }}
                />
              </div>

              <div className="flex items-center justify-between text-[12px]">
                <div className="flex items-center gap-3">
                  <button
                    onClick={() => setIsPlaying(!isPlaying)}
                    className="p-1.5 rounded hover:bg-white/10 text-white"
                  >
                    {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                  </button>
                  <button
                    onClick={() => setSeconds(0)}
                    className="p-1.5 rounded hover:bg-white/10 text-white/70 hover:text-white"
                  >
                    <RotateCcw className="w-3.5 h-3.5" />
                  </button>
                  <span className="text-[11px] font-mono text-white/70">
                    {currentScene.title}
                  </span>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setIsMuted(!isMuted)}
                    className="p-1.5 rounded hover:bg-white/10 text-white/70 hover:text-white"
                  >
                    {isMuted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
                  </button>
                  <span className="text-[11px] font-mono text-white/50">
                    {seconds}s / 60s
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Modal Footer */}
          <div className="px-6 py-4 bg-[#161616] border-t border-white/10 flex items-center justify-between">
            <span className="text-[13px] text-white/60">
              Want to test this with your own spreadsheet?
            </span>
            <Button size="sm" asChild>
              <a href="/signup">
                Start Free Now
              </a>
            </Button>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}
