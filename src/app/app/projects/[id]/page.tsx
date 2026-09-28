"use client";

import { use, useState } from "react";
import Link from "next/link";
import {
  FileSpreadsheet,
  FileImage,
  Layers,
  Sparkles,
  Award,
  CheckCircle2,
  Clock,
  ArrowRight,
  ArrowLeft,
  Settings,
  Download,
  Eye,
  Sliders,
  Play,
  RotateCcw,
  QrCode,
  ExternalLink,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";

export default function ProjectDetailsPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const [activeTab, setActiveTab] = useState("overview");

  // Mock project state
  const project = {
    id: id || "proj-ai-2026",
    name: "AI Workshop 2026",
    description: "Annual artificial intelligence practical summit certification",
    created: "Sep 27, 2026",
    template: "Academic Honors Landscape (3508 × 2480px)",
    recipientsCount: 500,
    status: "Ready for Generation",
  };

  return (
    <div className="min-h-screen bg-[var(--color-background)] flex flex-col">
      {/* Top App Bar */}
      <header className="border-b border-[var(--color-border)] bg-white sticky top-0 z-30">
        <div className="container-marketing h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Link
              href="/app"
              className="p-1.5 rounded-lg text-gray-400 hover:text-black hover:bg-gray-100 transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
            </Link>
            <div className="w-7 h-7 rounded-lg bg-[var(--color-primary)] text-white flex items-center justify-center font-bold">
              <Sparkles className="w-3.5 h-3.5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-[16px] font-bold text-[var(--color-text)]">
                  {project.name}
                </h1>
                <Badge variant="success" className="text-[11px]">
                  {project.status}
                </Badge>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Button size="sm" variant="secondary" asChild>
              <Link href={`/app/projects/${project.id}/editor`}>
                <Sliders className="w-3.5 h-3.5 mr-1.5" />
                Open Canvas Editor
              </Link>
            </Button>
            <Button size="sm" asChild>
              <Link href={`/app/projects/${project.id}/generate`}>
                <Play className="w-3.5 h-3.5 mr-1.5" />
                Generate Batch
              </Link>
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container-marketing py-8 flex-1">
        {/* Navigation Tabs (Overview, Template, Data, Mapping, Preview, Generate, Certificates, Settings) */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <div className="border-b border-[var(--color-border)] pb-3 mb-8 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <TabsList className="flex-wrap bg-white">
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="template">Template</TabsTrigger>
              <TabsTrigger value="data">Data (CSV)</TabsTrigger>
              <TabsTrigger value="mapping">Field Mapping</TabsTrigger>
              <TabsTrigger value="preview">Live Preview</TabsTrigger>
              <TabsTrigger value="generate">Generate</TabsTrigger>
              <TabsTrigger value="certificates">Issued Certs</TabsTrigger>
              <TabsTrigger value="settings">Settings</TabsTrigger>
            </TabsList>

            <span className="text-[12px] font-mono text-gray-500">
              500 Recipients loaded · 4 Fields mapped
            </span>
          </div>

          {/* TAB 1: OVERVIEW */}
          <TabsContent value="overview">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Left Column: Progress Checklist */}
              <div className="lg:col-span-2 space-y-6">
                {/* Project Setup Stepper */}
                <div className="bg-white rounded-2xl border border-[var(--color-border)] p-6 shadow-2xs">
                  <h3 className="text-[16px] font-bold text-[var(--color-text)] mb-1">
                    Project Setup Pipeline
                  </h3>
                  <p className="text-[13px] text-[var(--color-text-secondary)] mb-6">
                    Track configuration progress before triggering generation
                  </p>

                  <div className="space-y-4">
                    {[
                      { step: "Template Upload", desc: "Background design verified (300 DPI)", status: "done", action: () => setActiveTab("template") },
                      { step: "Recipient Data Import", desc: "students.csv loaded (500 records parsed)", status: "done", action: () => setActiveTab("data") },
                      { step: "Field Mapping", desc: "4 dynamic variables connected", status: "done", action: () => setActiveTab("mapping") },
                      { step: "Typography Preview", desc: "Verify long name wrapping & QR codes", status: "pending", action: () => setActiveTab("preview") },
                      { step: "Batch PDF Generation", desc: "Compile 500 vector PDFs & ZIP", status: "pending", action: () => setActiveTab("generate") },
                    ].map((st, i) => (
                      <div
                        key={st.step}
                        onClick={st.action}
                        className="p-4 rounded-xl border border-[var(--color-border)] bg-[var(--color-background)] hover:bg-white hover:border-[var(--color-border-hover)] transition-all flex items-center justify-between cursor-pointer"
                      >
                        <div className="flex items-center gap-3">
                          <div className={`w-7 h-7 rounded-full flex items-center justify-center text-[12px] font-bold ${
                            st.status === "done" ? "bg-emerald-100 text-emerald-700" : "bg-gray-200 text-gray-600"
                          }`}>
                            {st.status === "done" ? "✓" : i + 1}
                          </div>
                          <div>
                            <p className="text-[14px] font-semibold text-[var(--color-text)]">{st.step}</p>
                            <p className="text-[12px] text-[var(--color-text-secondary)]">{st.desc}</p>
                          </div>
                        </div>

                        <span className="text-[12px] text-[var(--color-primary)] font-semibold flex items-center gap-1">
                          Configure <ArrowRight className="w-3.5 h-3.5" />
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Quick Stats Grid */}
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  <div className="p-5 rounded-2xl bg-white border border-[var(--color-border)] shadow-2xs">
                    <p className="text-[12px] text-gray-500 font-semibold uppercase">Total Recipients</p>
                    <p className="text-[28px] font-bold text-[var(--color-text)] mt-1">500</p>
                  </div>
                  <div className="p-5 rounded-2xl bg-white border border-[var(--color-border)] shadow-2xs">
                    <p className="text-[12px] text-gray-500 font-semibold uppercase">Dynamic Fields</p>
                    <p className="text-[28px] font-bold text-[var(--color-primary)] mt-1">4</p>
                  </div>
                  <div className="p-5 rounded-2xl bg-white border border-[var(--color-border)] shadow-2xs">
                    <p className="text-[12px] text-gray-500 font-semibold uppercase">QR Signatures</p>
                    <p className="text-[28px] font-bold text-emerald-600 mt-1">Active</p>
                  </div>
                </div>
              </div>

              {/* Right Column: Mini Certificate Preview */}
              <div className="space-y-6">
                <div className="bg-white rounded-2xl border border-[var(--color-border)] p-6 shadow-2xs text-center">
                  <h4 className="text-[14px] font-bold mb-4 text-left">Canvas Preview</h4>
                  <div className="w-full aspect-[1.4/1] bg-[var(--color-background)] rounded-xl border-2 border-indigo-200/60 p-5 flex flex-col justify-between relative shadow-inner">
                    <div className="absolute inset-1.5 border border-dashed border-indigo-300 rounded pointer-events-none" />
                    <p className="text-[8px] uppercase tracking-widest text-gray-400 font-bold">Certificate</p>
                    <div>
                      <p className="text-[15px] font-serif font-bold text-[var(--color-text)]">Atul Kumar</p>
                      <p className="text-[9px] text-[var(--color-primary)] font-medium">AI Workshop 2026</p>
                    </div>
                    <div className="flex items-center justify-between text-[7px] text-gray-400 border-t pt-1">
                      <span>Sep 27, 2026</span>
                      <div className="w-3.5 h-3.5 border flex items-center justify-center font-mono text-[5px]">QR</div>
                      <span>#CERT-001</span>
                    </div>
                  </div>

                  <div className="mt-4 flex gap-2">
                    <Button size="sm" variant="secondary" className="w-full justify-center" asChild>
                      <Link href={`/app/projects/${project.id}/preview`}>
                        <Eye className="w-3.5 h-3.5 mr-1" />
                        Preview 500
                      </Link>
                    </Button>
                    <Button size="sm" className="w-full justify-center" asChild>
                      <Link href={`/app/projects/${project.id}/editor`}>
                        <Sliders className="w-3.5 h-3.5 mr-1" />
                        Edit Canvas
                      </Link>
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          </TabsContent>

          {/* TAB 2: TEMPLATE */}
          <TabsContent value="template">
            <div className="bg-white rounded-2xl border border-[var(--color-border)] p-8 max-w-3xl mx-auto text-center space-y-6">
              <div className="w-12 h-12 rounded-2xl bg-indigo-50 text-[var(--color-primary)] flex items-center justify-center mx-auto">
                <FileImage className="w-6 h-6" />
              </div>
              <div>
                <h3 className="text-[20px] font-bold">Current Template Background</h3>
                <p className="text-[14px] text-gray-500 mt-1">
                  academic_honors_master.pdf (3508 × 2480px, A4 Landscape @ 300 DPI)
                </p>
              </div>

              <div className="border-2 border-dashed border-[var(--color-border)] rounded-xl p-8 bg-[var(--color-background)]">
                <p className="text-[13px] font-medium text-gray-700">
                  Drop a new background template to replace the current design
                </p>
                <p className="text-[12px] text-gray-400 mt-1">Supports PDF, PNG, and JPG</p>
                <Button size="sm" variant="secondary" className="mt-4">
                  Browse Replacement File
                </Button>
              </div>
            </div>
          </TabsContent>

          {/* TAB 3: DATA (CSV) */}
          <TabsContent value="data">
            <div className="bg-white rounded-2xl border border-[var(--color-border)] overflow-hidden shadow-2xs">
              <div className="p-6 border-b border-[var(--color-border)] flex items-center justify-between">
                <div>
                  <h3 className="text-[18px] font-bold">Imported Recipient Data</h3>
                  <p className="text-[13px] text-gray-500">students.csv · 500 rows verified</p>
                </div>
                <div className="flex gap-2">
                  <Button size="sm" variant="secondary" asChild>
                    <Link href={`/app/projects/${project.id}/data`}>
                      Open Spreadsheet Workbench
                    </Link>
                  </Button>
                </div>
              </div>

              <div className="overflow-x-auto text-[13px]">
                <table className="w-full text-left">
                  <thead className="bg-[var(--color-background)] border-b border-[var(--color-border)] font-semibold text-gray-600">
                    <tr>
                      <th className="p-3.5">Row</th>
                      <th className="p-3.5">Full Name</th>
                      <th className="p-3.5">Course</th>
                      <th className="p-3.5">Completion Date</th>
                      <th className="p-3.5">Score</th>
                      <th className="p-3.5">Recipient Email</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[var(--color-border)]">
                    {[
                      { r: 1, name: "Atul Kumar", course: "AI Mastery 2026", date: "Sep 27, 2026", score: "98%", email: "atul@example.com" },
                      { r: 2, name: "Rahul Sharma", course: "AI Mastery 2026", date: "Sep 27, 2026", score: "92%", email: "rahul.s@edu.org" },
                      { r: 3, name: "Priya Singh", course: "AI Mastery 2026", date: "Sep 27, 2026", score: "95%", email: "priya.singh@corp.in" },
                      { r: 4, name: "Sneha Patel", course: "AI Mastery 2026", date: "Sep 27, 2026", score: "91%", email: "sneha.patel@gmail.com" },
                    ].map((row) => (
                      <tr key={row.r} className="hover:bg-gray-50">
                        <td className="p-3.5 font-mono text-gray-400">#{row.r}</td>
                        <td className="p-3.5 font-medium text-[var(--color-text)]">{row.name}</td>
                        <td className="p-3.5 text-gray-600">{row.course}</td>
                        <td className="p-3.5 text-gray-600">{row.date}</td>
                        <td className="p-3.5 font-bold text-emerald-600">{row.score}</td>
                        <td className="p-3.5 font-mono text-gray-500">{row.email}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </TabsContent>

          {/* TAB 4: MAPPING */}
          <TabsContent value="mapping">
            <div className="bg-white rounded-2xl border border-[var(--color-border)] p-6 sm:p-8 max-w-3xl mx-auto shadow-2xs space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-[18px] font-bold">Field Mapping</h3>
                  <p className="text-[13px] text-gray-500 mt-1">
                    Connect each certificate typography placeholder to a spreadsheet column
                  </p>
                </div>
                <Button size="sm" variant="secondary" asChild>
                  <Link href={`/app/projects/${project.id}/mapping`}>
                    Open Field Studio
                  </Link>
                </Button>
              </div>

              <div className="space-y-3">
                {[
                  { tag: "{{NAME}}", col: "Full Name", status: "Auto-matched" },
                  { tag: "{{COURSE}}", col: "Course", status: "Auto-matched" },
                  { tag: "{{DATE}}", col: "Completion Date", status: "Auto-matched" },
                  { tag: "{{SCORE}}", col: "Score", status: "Auto-matched" },
                  { tag: "{{CERTIFICATE_ID}}", col: "Auto Generate UUID + QR", status: "Dynamic System Field" },
                ].map((m) => (
                  <div key={m.tag} className="p-3 rounded-xl bg-[var(--color-background)] border border-[var(--color-border)] flex items-center justify-between text-[13px]">
                    <div className="flex items-center gap-3">
                      <span className="font-mono bg-[var(--color-primary-light)] text-[var(--color-primary)] font-bold px-2 py-0.5 rounded text-[12px]">
                        {m.tag}
                      </span>
                      <span className="text-gray-400">→</span>
                      <span className="font-medium text-[var(--color-text)]">{m.col}</span>
                    </div>
                    <span className="text-[11px] font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                      ✓ {m.status}
                    </span>
                  </div>
                ))}
              </div>

              <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-[13px] flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                <span>All required template placeholders successfully mapped to data columns.</span>
              </div>
            </div>
          </TabsContent>

          {/* TAB 5: PREVIEW */}
          <TabsContent value="preview">
            <div className="bg-white rounded-2xl border border-[var(--color-border)] p-6 sm:p-8 max-w-4xl mx-auto shadow-2xs">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h3 className="text-[18px] font-bold">Interactive Recipient Switcher</h3>
                  <p className="text-[13px] text-gray-500">Preview live rendering across 500 recipients</p>
                </div>
                <div className="flex gap-2">
                  <Button size="sm" variant="secondary" asChild>
                    <Link href={`/app/projects/${project.id}/preview`}>
                      Open Fullscreen Preview
                    </Link>
                  </Button>
                </div>
              </div>

              {/* Certificate preview */}
              <div className="aspect-[1.4/1] bg-[#FAFAF8] rounded-2xl border-2 border-[var(--color-border)] p-8 max-w-2xl mx-auto text-center flex flex-col justify-between relative shadow-sm">
                <p className="text-[10px] uppercase font-bold tracking-widest text-gray-400">Certificate of Completion</p>
                <div>
                  <h2 className="text-[28px] font-bold font-serif text-[var(--color-text)]">Atul Kumar</h2>
                  <p className="text-[13px] text-[var(--color-primary)] font-medium mt-1">AI Mastery 2026 · Score: 98%</p>
                </div>
                <div className="flex items-center justify-between pt-4 border-t border-gray-200 text-[11px] text-gray-500">
                  <span>Sep 27, 2026</span>
                  <div className="w-5 h-5 border flex items-center justify-center font-mono text-[7px]">QR</div>
                  <span>CERT-AF72K9</span>
                </div>
              </div>
            </div>
          </TabsContent>

          {/* TAB 6: GENERATE */}
          <TabsContent value="generate">
            <div className="bg-white rounded-2xl border border-[var(--color-border)] p-8 max-w-2xl mx-auto text-center shadow-2xs space-y-6">
              <div className="w-14 h-14 rounded-2xl bg-[var(--color-primary-light)] text-[var(--color-primary)] flex items-center justify-center mx-auto">
                <Sparkles className="w-7 h-7" />
              </div>
              <div>
                <h3 className="text-[22px] font-bold">Batch Generation Engine</h3>
                <p className="text-[14px] text-gray-500 mt-1">
                  Ready to produce 500 personalized vector certificates
                </p>
              </div>

              <div className="p-4 rounded-xl bg-[var(--color-background)] border border-[var(--color-border)] text-left text-[13px] space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-500">Batch Size:</span>
                  <span className="font-semibold text-gray-800">500 certificates</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Output Format:</span>
                  <span className="font-semibold text-gray-800">Print-Ready Vector PDF (300 DPI)</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">QR Code Signatures:</span>
                  <span className="font-semibold text-emerald-600">Enabled (Dynamic URL hash)</span>
                </div>
              </div>

              <Button size="lg" className="w-full justify-center h-12 text-[15px] shadow-md" asChild>
                <Link href={`/app/projects/${project.id}/generate`}>
                  Start 500-Batch Generation Now
                  <ArrowRight className="w-4 h-4 ml-1.5" />
                </Link>
              </Button>
            </div>
          </TabsContent>

          {/* TAB 7: CERTIFICATES */}
          <TabsContent value="certificates">
            <div className="bg-white rounded-2xl border border-[var(--color-border)] p-6 shadow-2xs">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-[16px] font-bold">Issued Certificates for this Batch</h3>
                <Button size="sm" variant="secondary">
                  <Download className="w-3.5 h-3.5 mr-1" />
                  Download All (ZIP)
                </Button>
              </div>
              <div className="divide-y divide-[var(--color-border)] text-[13px]">
                {[
                  { name: "Atul Kumar", id: "CERT-001", status: "Verified", date: "Sep 27, 2026" },
                  { name: "Rahul Sharma", id: "CERT-002", status: "Verified", date: "Sep 27, 2026" },
                  { name: "Priya Singh", id: "CERT-003", status: "Verified", date: "Sep 27, 2026" },
                ].map((c) => (
                  <div key={c.id} className="py-3 flex items-center justify-between">
                    <div>
                      <p className="font-medium text-[var(--color-text)]">{c.name}</p>
                      <p className="text-[11px] text-gray-400 font-mono">{c.id}</p>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-[11px] font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded">
                        ✓ {c.status}
                      </span>
                      <Link href={`/verify/${c.id}`} className="text-[var(--color-primary)] hover:underline flex items-center gap-1 text-[12px]">
                        Verify <ExternalLink className="w-3 h-3" />
                      </Link>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </TabsContent>

          {/* TAB 8: SETTINGS */}
          <TabsContent value="settings">
            <div className="bg-white rounded-2xl border border-[var(--color-border)] p-6 max-w-xl mx-auto shadow-2xs space-y-4">
              <h3 className="text-[18px] font-bold">Project Settings</h3>
              <div>
                <label className="block text-[13px] font-medium mb-1">Project Name</label>
                <input
                  type="text"
                  defaultValue={project.name}
                  className="w-full px-3 py-2 rounded-lg border border-[var(--color-border)] bg-[var(--color-background)] text-[14px]"
                />
              </div>
              <div>
                <label className="block text-[13px] font-medium mb-1">Description</label>
                <textarea
                  defaultValue={project.description}
                  rows={3}
                  className="w-full px-3 py-2 rounded-lg border border-[var(--color-border)] bg-[var(--color-background)] text-[14px]"
                />
              </div>
              <Button size="sm">Save Changes</Button>
            </div>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}
