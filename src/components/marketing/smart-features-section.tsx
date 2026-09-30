"use client";

import { useState, useEffect } from "react";
import { motion } from "motion/react";
import { Type, Sparkles, Send, Search, ShieldCheck, Mail } from "lucide-react";
import { staggerContainer, staggerItem, viewportOnce } from "@/lib/motion";

export function SmartFeaturesSection() {
  /* Smart text fit animation state */
  const [fontSizeIndex, setFontSizeIndex] = useState(0);
  const fontSizes = [
    { size: 76, label: "76px", status: "Overflowing text boundary", alert: true },
    { size: 70, label: "70px", status: "Truncating margins...", alert: true },
    { size: 64, label: "64px", status: "Perfect calculated fit ✓", alert: false },
  ];

  useEffect(() => {
    const timer = setInterval(() => {
      setFontSizeIndex((prev) => (prev + 1) % fontSizes.length);
    }, 2400);
    return () => clearInterval(timer);
  }, [fontSizes.length]);

  /* Batch progress simulated state */
  const [batchCount, setBatchCount] = useState(874);

  useEffect(() => {
    const interval = setInterval(() => {
      setBatchCount((prev) => (prev >= 1000 ? 820 : prev + 9));
    }, 1200);
    return () => clearInterval(interval);
  }, []);

  return (
    <section className="section-padding border-t border-[var(--color-border)]">
      <div className="container-marketing">
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={viewportOnce}
          variants={staggerContainer}
          className="max-w-2xl mx-auto text-center mb-16"
        >
          <motion.p
            variants={staggerItem}
            className="text-[13px] font-semibold uppercase tracking-[0.15em] text-[var(--color-primary)] mb-3"
          >
            Engineering Excellence
          </motion.p>
          <motion.h2 variants={staggerItem} className="text-section mb-4">
            Signature features built for scale
          </motion.h2>
          <motion.p variants={staggerItem} className="text-body-lg text-[var(--color-text-secondary)]">
            Thoughtful micro-innovations that solve the everyday headaches of bulk document rendering.
          </motion.p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-5xl mx-auto">
          {/* Card 1: Smart Text Fit */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={viewportOnce}
            transition={{ duration: 0.5 }}
            className="rounded-2xl border border-[var(--color-border)] bg-white p-7 shadow-xs flex flex-col justify-between"
          >
            <div>
              <div className="flex items-center justify-between mb-4">
                <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-violet-50 text-[var(--color-primary)] text-[12px] font-semibold">
                  <Type className="w-3.5 h-3.5" />
                  Smart Text Fit
                </span>
                <span className="text-[12px] font-mono text-[var(--color-text-tertiary)]">Feature #4</span>
              </div>
              <h3 className="text-[20px] font-bold mb-2">Zero-overflow typography engine</h3>
              <p className="text-[14px] text-[var(--color-text-secondary)] mb-6">
                When someone has an unusually long name or academic title, CertiFlow automatically recalculates font-metrics and scales down without breaking your layout.
              </p>

              {/* Visual interactive preview */}
              <div className="rounded-xl border border-[var(--color-border)] bg-[var(--color-background)] p-6 text-center overflow-hidden">
                <div className="flex items-center justify-between text-[11px] font-mono text-[var(--color-text-tertiary)] mb-4">
                  <span>Target container: 520px</span>
                  <span className={fontSizes[fontSizeIndex].alert ? "text-amber-600 font-semibold" : "text-emerald-600 font-semibold"}>
                    Size: {fontSizes[fontSizeIndex].label} · {fontSizes[fontSizeIndex].status}
                  </span>
                </div>

                <div className="relative border-2 border-dashed border-[var(--color-primary)]/40 rounded-lg p-4 bg-white min-h-[90px] flex items-center justify-center">
                  <motion.p
                    key={fontSizeIndex}
                    initial={{ scale: 0.96, opacity: 0.7 }}
                    animate={{ scale: 1, opacity: 1 }}
                    transition={{ duration: 0.3 }}
                    style={{ fontSize: `${fontSizes[fontSizeIndex].size * 0.32}px` }}
                    className="font-bold text-[var(--color-text)] whitespace-nowrap tracking-tight font-serif"
                  >
                    Dr. Abhishek Kumar Choudhary Sharma
                  </motion.p>
                </div>

                <div className="flex justify-center gap-2 mt-4">
                  {fontSizes.map((f, i) => (
                    <button
                      key={f.size}
                      onClick={() => setFontSizeIndex(i)}
                      className={`px-3 py-1 text-[11px] font-mono rounded-md border transition-all ${
                        fontSizeIndex === i
                          ? "bg-[var(--color-primary)] text-white border-[var(--color-primary)] shadow-xs"
                          : "bg-white text-[var(--color-text-secondary)] border-[var(--color-border)]"
                      }`}
                    >
                      {f.label}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </motion.div>

          {/* Card 2: Batch Generation Telemetry */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={viewportOnce}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="rounded-2xl border border-[var(--color-border)] bg-white p-7 shadow-xs flex flex-col justify-between"
          >
            <div>
              <div className="flex items-center justify-between mb-4">
                <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-blue-50 text-blue-700 text-[12px] font-semibold">
                  <Sparkles className="w-3.5 h-3.5" />
                  Real-time Batch Engine
                </span>
                <span className="text-[12px] font-mono text-[var(--color-text-tertiary)]">Feature #7</span>
              </div>
              <h3 className="text-[20px] font-bold mb-2">Live progress telemetry & error handling</h3>
              <p className="text-[14px] text-[var(--color-text-secondary)] mb-6">
                Watch thousands of high-resolution certificates render asynchronously in memory with sub-second feedback and pinpoint validation.
              </p>

              {/* Progress UI Mockup */}
              <div className="rounded-xl border border-[var(--color-border)] bg-[var(--color-background)] p-5">
                <div className="flex items-center justify-between text-[13px] font-medium mb-2">
                  <span className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-blue-600 animate-pulse" />
                    Generating certificates...
                  </span>
                  <span className="font-mono font-bold text-[var(--color-primary)]">
                    {Math.round((batchCount / 1000) * 100)}%
                  </span>
                </div>

                {/* Progress bar */}
                <div className="h-3 w-full bg-gray-200 rounded-full overflow-hidden mb-3">
                  <div
                    className="h-full bg-[var(--color-primary)] rounded-full transition-all duration-300"
                    style={{ width: `${(batchCount / 1000) * 100}%` }}
                  />
                </div>

                <div className="grid grid-cols-2 gap-2 text-[12px] bg-white p-3 rounded-lg border border-[var(--color-border)]">
                  <div>
                    <span className="text-[var(--color-text-tertiary)]">Generated: </span>
                    <span className="font-bold text-emerald-600">{batchCount} / 1,000</span>
                  </div>
                  <div className="text-right">
                    <span className="text-[var(--color-text-tertiary)]">Throughput: </span>
                    <span className="font-mono text-[var(--color-text)]">42 certs/sec</span>
                  </div>
                  <div>
                    <span className="text-[var(--color-text-tertiary)]">Failures: </span>
                    <span className="font-bold text-emerald-600">0 records</span>
                  </div>
                  <div className="text-right">
                    <span className="text-[var(--color-text-tertiary)]">Est. remaining: </span>
                    <span className="font-mono text-[var(--color-text)]">{Math.max(1, Math.round((1000 - batchCount) / 42))}s</span>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>

          {/* Card 3: Direct Email Delivery Pipeline */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={viewportOnce}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="rounded-2xl border border-[var(--color-border)] bg-white p-7 shadow-xs flex flex-col justify-between"
          >
            <div>
              <div className="flex items-center justify-between mb-4">
                <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-50 text-amber-700 text-[12px] font-semibold">
                  <Mail className="w-3.5 h-3.5" />
                  Scheduled Email Delivery
                </span>
                <span className="text-[12px] font-mono text-[var(--color-text-tertiary)]">Feature #8</span>
              </div>
              <h3 className="text-[20px] font-bold mb-2">Automated distribution with tracking</h3>
              <p className="text-[14px] text-[var(--color-text-secondary)] mb-6">
                Send personalized emails with attached PDFs directly to each participant or schedule distribution for the exact end of your event.
              </p>

              {/* Email dispatch pipeline visual */}
              <div className="rounded-xl border border-[var(--color-border)] bg-[var(--color-background)] p-4 space-y-2">
                {[
                  { recipient: "atul@example.com", status: "Sent & Opened", time: "1m ago", badge: "bg-emerald-100 text-emerald-700" },
                  { recipient: "rahul.s@edu.org", status: "Delivered", time: "2m ago", badge: "bg-blue-100 text-blue-700" },
                  { recipient: "priya.singh@corp.in", status: "Queued (batch #2)", time: "Now", badge: "bg-amber-100 text-amber-700" },
                ].map((item, i) => (
                  <div key={i} className="flex items-center justify-between p-2.5 rounded-lg bg-white border border-[var(--color-border)] text-[12px]">
                    <div className="flex items-center gap-2">
                      <Send className="w-3.5 h-3.5 text-[var(--color-text-tertiary)]" />
                      <span className="font-mono text-[var(--color-text)]">{item.recipient}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${item.badge}`}>
                        {item.status}
                      </span>
                      <span className="text-[11px] text-[var(--color-text-tertiary)] font-mono">{item.time}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>

          {/* Card 4: Certificate Library & Management */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={viewportOnce}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="rounded-2xl border border-[var(--color-border)] bg-white p-7 shadow-xs flex flex-col justify-between"
          >
            <div>
              <div className="flex items-center justify-between mb-4">
                <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-50 text-emerald-700 text-[12px] font-semibold">
                  <ShieldCheck className="w-3.5 h-3.5" />
                  Registry & Credential Vault
                </span>
                <span className="text-[12px] font-mono text-[var(--color-text-tertiary)]">Feature #9</span>
              </div>
              <h3 className="text-[20px] font-bold mb-2">Centralized searchable record registry</h3>
              <p className="text-[14px] text-[var(--color-text-secondary)] mb-6">
                Never lose an issued certificate. Search by recipient name, ID, or course to re-issue, revoke, or inspect verification logs.
              </p>

              {/* Mini Table UI */}
              <div className="rounded-xl border border-[var(--color-border)] bg-[var(--color-background)] overflow-hidden">
                <div className="px-3 py-2 border-b border-[var(--color-border)] bg-white flex items-center justify-between">
                  <div className="flex items-center gap-1.5 text-[11px] text-[var(--color-text-tertiary)]">
                    <Search className="w-3 h-3" />
                    <span>Filter: All Projects</span>
                  </div>
                  <span className="text-[10px] font-mono text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded font-semibold">
                    1,284 Active Credentials
                  </span>
                </div>
                <div className="divide-y divide-[var(--color-border)] text-[12px]">
                  {[
                    { name: "Atul Kumar", id: "CERT-001", status: "Verified", date: "Sep 2026" },
                    { name: "Rahul Sharma", id: "CERT-002", status: "Verified", date: "Sep 2026" },
                    { name: "Priya Singh", id: "CERT-003", status: "Verified", date: "Sep 2026" },
                  ].map((row) => (
                    <div key={row.id} className="px-3.5 py-2 flex items-center justify-between bg-white hover:bg-[var(--color-background)] transition-colors">
                      <span className="font-medium text-[var(--color-text)]">{row.name}</span>
                      <span className="font-mono text-[11px] text-[var(--color-text-secondary)]">{row.id}</span>
                      <span className="text-[10px] font-bold text-emerald-700 bg-emerald-100/60 px-2 py-0.5 rounded flex items-center gap-1">
                        ✓ {row.status}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
