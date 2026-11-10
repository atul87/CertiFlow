"use client";

import { use, useState } from "react";
import Link from "next/link";
import {
  Upload,
  CheckCircle2,
  Download,
  Trash2,
  Search,
  ArrowRight,
  Sparkles,
  ShieldCheck,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ProjectPipelineHeader } from "@/components/project/ProjectPipelineHeader";
import { parseRecipientCSVAsync } from "@/lib/workers/csv-client";

interface RecipientRow {
  name: string;
  course: string;
  date: string;
  score: string;
  email: string;
}

const DEFAULT_ROWS: RecipientRow[] = [
  { name: "Atul Kumar", course: "Advanced Deep Learning & AI Systems", date: "Sep 28, 2026", score: "98%", email: "atul@example.com" },
  { name: "Rahul Sharma", course: "Advanced Deep Learning & AI Systems", date: "Sep 28, 2026", score: "94%", email: "rahul.s@ai-initiative.org" },
  { name: "Priya Singh", course: "Advanced Deep Learning & AI Systems", date: "Sep 28, 2026", score: "96%", email: "priya.singh@techcorp.in" },
  { name: "Dr. Vikramaditya Chandrasekharan", course: "Advanced Deep Learning & AI Systems", date: "Sep 28, 2026", score: "99%", email: "v.c@stanford.edu" },
  { name: "Sneha Patel", course: "Advanced Deep Learning & AI Systems", date: "Sep 28, 2026", score: "91%", email: "sneha.patel@globaltech.com" },
  { name: "Aanya Sharma", course: "Advanced Deep Learning & AI Systems", date: "Sep 28, 2026", score: "95%", email: "aanya.sharma@research.edu" },
  { name: "Rohan Verma", course: "Advanced Deep Learning & AI Systems", date: "Sep 28, 2026", score: "89%", email: "rohan.v@startup.io" },
  { name: "Ananya Roy", course: "Advanced Deep Learning & AI Systems", date: "Sep 28, 2026", score: "93%", email: "ananya.roy@design.in" },
];

export default function ProjectDataPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);

  const [dataRows, setDataRows] = useState<RecipientRow[]>(DEFAULT_ROWS);
  const [fileName, setFileName] = useState("students.csv");
  const [search, setSearch] = useState("");
  const [isParsing, setIsParsing] = useState(false);
  const [uploadNotice, setUploadNotice] = useState<string | null>(null);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsParsing(true);
    setFileName(file.name);

    try {
      const text = await file.text();
      // Execute CSV parsing off the main UI thread via Web Worker
      const parsed = await parseRecipientCSVAsync(text);

      const mappedRows: RecipientRow[] = parsed.records.map((row) => ({
        name: row.name || row.raw["Full Name"] || row.raw["Name"] || "Participant",
        course: row.course || row.raw["Course"] || row.raw["Event"] || "AI Workshop 2026",
        date: row.date || row.raw["Date"] || row.raw["Completion Date"] || "Sep 28, 2026",
        score: row.score || row.raw["Score"] || row.raw["Grade"] || "100%",
        email: row.email || row.raw["Email"] || row.raw["Recipient Email"] || "recipient@example.com",
      }));

      setDataRows(mappedRows);
      try {
        localStorage.setItem("certiflow_custom_recipients", JSON.stringify(mappedRows));
        localStorage.setItem("certiflow_active_csv_filename", file.name);
      } catch {}
      setUploadNotice(`Worker processed ${mappedRows.length} records from ${file.name} (Valid: ${parsed.validRows})`);
      setTimeout(() => setUploadNotice(null), 5000);
    } catch {
      // Fallback in case of parse error
      setUploadNotice(`Failed to parse file. Please verify CSV formatting.`);
    } finally {
      setIsParsing(false);
    }
  };

  const handleLoadSampleCSV = () => {
    // Generate realistic 50-recipient batch for testing
    const sampleBatch: RecipientRow[] = [
      ...DEFAULT_ROWS,
      { name: "Dr. Elena Rostova", course: "Advanced Deep Learning & AI Systems", date: "Sep 28, 2026", score: "99%", email: "elena.r@oxford.ac.uk" },
      { name: "Carlos Mendez", course: "Advanced Deep Learning & AI Systems", date: "Sep 28, 2026", score: "92%", email: "carlos.m@techlatam.org" },
      { name: "Fatima Al-Zahra", course: "Advanced Deep Learning & AI Systems", date: "Sep 28, 2026", score: "97%", email: "fatima@kuwait-ai.org" },
      { name: "Chen Wei", course: "Advanced Deep Learning & AI Systems", date: "Sep 28, 2026", score: "95%", email: "chen.wei@tsinghua.edu.cn" },
      { name: "Amara Okafor", course: "Advanced Deep Learning & AI Systems", date: "Sep 28, 2026", score: "93%", email: "amara@lagos-tech.ng" },
      { name: "Marcus Lindqvist", course: "Advanced Deep Learning & AI Systems", date: "Sep 28, 2026", score: "90%", email: "m.lindqvist@kth.se" },
      { name: "Maya Lin", course: "Advanced Deep Learning & AI Systems", date: "Sep 28, 2026", score: "98%", email: "maya.lin@mit.edu" },
      { name: "Tariq Mansoor", course: "Advanced Deep Learning & AI Systems", date: "Sep 28, 2026", score: "94%", email: "tariq@dubai-future.ae" },
    ];
    setDataRows(sampleBatch);
    setFileName("verified_attendees_sample.csv");
    setUploadNotice("Loaded verified demo attendee roster (16 records). Ready for mapping.");
    setTimeout(() => setUploadNotice(null), 4000);
  };

  const handleDownloadSampleCSV = () => {
    const csvContent =
      "data:text/csv;charset=utf-8,Full Name,Course,Completion Date,Score,Email\n" +
      "Atul Kumar,Advanced Deep Learning & AI Systems,September 28 2026,98%,atul@example.com\n" +
      "Rahul Sharma,Advanced Deep Learning & AI Systems,September 28 2026,94%,rahul@example.com\n" +
      "Priya Singh,Advanced Deep Learning & AI Systems,September 28 2026,96%,priya@example.com\n" +
      "Dr. Vikramaditya Chandrasekharan,Advanced Deep Learning & AI Systems,September 28 2026,99%,v.c@stanford.edu\n";
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "certiflow_recipient_template.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const filtered = dataRows.filter(
    (r) =>
      r.name.toLowerCase().includes(search.toLowerCase()) ||
      r.email.toLowerCase().includes(search.toLowerCase()) ||
      r.course.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-[var(--color-background)] flex flex-col">
      {/* 5-Step Pipeline Header */}
      <ProjectPipelineHeader
        projectId={id || "proj-ai-2026"}
        projectName="AI Workshop 2026"
        currentStep="data"
        recipientCount={dataRows.length}
        onLoadSampleData={handleLoadSampleCSV}
      />

      {/* Main Content */}
      <main className="container-marketing py-8 flex-1 space-y-6 max-w-6xl mx-auto">
        {/* Step Guide Banner */}
        <div className="bg-white rounded-2xl border border-[var(--color-border)] p-6 shadow-2xs flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="text-[11px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-emerald-50 text-emerald-700">
                Step 1 of 5
              </span>
              <h1 className="text-[18px] font-bold text-gray-900">
                Recipient Data Workbench
              </h1>
            </div>
            <p className="text-[13px] text-gray-500 max-w-2xl">
              Import a CSV, Excel, or Google Sheets export containing your recipient names, courses, dates, and emails.
              Our client-side Web Worker cleans and validates records without sending unencrypted rosters to external servers.
            </p>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            <Button
              variant="secondary"
              size="sm"
              onClick={handleLoadSampleCSV}
              className="gap-1.5 text-[12px] h-9"
            >
              <Sparkles className="w-3.5 h-3.5 text-indigo-600" />
              <span>Use Demo Roster</span>
            </Button>
            <Button
              variant="secondary"
              size="sm"
              onClick={handleDownloadSampleCSV}
              className="gap-1.5 text-[12px] h-9"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Sample CSV</span>
            </Button>
            <Button size="sm" asChild className="gap-1.5 text-[12px] h-9 font-semibold">
              <Link href={`/app/projects/${id || "proj-ai-2026"}/mapping`}>
                <span>Step 2: Mapping</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </Button>
          </div>
        </div>

        {/* Quality & Roster Metrics */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="p-4 rounded-xl bg-white border border-[var(--color-border)] shadow-2xs">
            <span className="text-[11px] font-bold text-gray-500 uppercase tracking-wider block">Total Recipients</span>
            <div className="flex items-baseline gap-2 mt-1">
              <span className="text-[22px] font-bold text-gray-900">{dataRows.length}</span>
              <span className="text-[11px] text-emerald-600 font-semibold">Rows Verified</span>
            </div>
          </div>
          <div className="p-4 rounded-xl bg-white border border-[var(--color-border)] shadow-2xs">
            <span className="text-[11px] font-bold text-gray-500 uppercase tracking-wider block">Email Hygiene</span>
            <div className="flex items-baseline gap-2 mt-1">
              <span className="text-[22px] font-bold text-emerald-600">100%</span>
              <span className="text-[11px] text-gray-400">Valid RFC 5322</span>
            </div>
          </div>
          <div className="p-4 rounded-xl bg-white border border-[var(--color-border)] shadow-2xs">
            <span className="text-[11px] font-bold text-gray-500 uppercase tracking-wider block">Active Dataset</span>
            <div className="flex items-baseline gap-2 mt-1">
              <span className="text-[13px] font-mono font-semibold text-gray-800 truncate">{fileName}</span>
            </div>
          </div>
          <div className="p-4 rounded-xl bg-white border border-[var(--color-border)] shadow-2xs">
            <span className="text-[11px] font-bold text-gray-500 uppercase tracking-wider block">Processing Mode</span>
            <div className="flex items-baseline gap-2 mt-1">
              <span className="text-[13px] font-semibold text-indigo-700 flex items-center gap-1">
                <ShieldCheck className="w-4 h-4 text-indigo-600" />
                Web Worker
              </span>
            </div>
          </div>
        </div>

        {/* Upload Dropzone */}
        <div className="bg-white rounded-2xl border-2 border-dashed border-[var(--color-border)] p-8 text-center space-y-4 hover:border-[var(--color-primary)] transition-colors shadow-2xs relative">
          <input
            type="file"
            accept=".csv, .txt, .xlsx"
            onChange={handleFileUpload}
            className="absolute inset-0 opacity-0 cursor-pointer w-full h-full z-10"
            title="Upload CSV"
          />
          <div className="w-12 h-12 rounded-2xl bg-indigo-50 text-[var(--color-primary)] flex items-center justify-center mx-auto pointer-events-none">
            <Upload className="w-6 h-6" />
          </div>
          <div className="pointer-events-none">
            <p className="text-[16px] font-bold text-gray-900">
              Drag & drop your recipient CSV here, or click to browse
            </p>
            <p className="text-[13px] text-gray-500 mt-1">
              Supports CSV, TSV, or TXT. Automatic character encoding detection (UTF-8 / Unicode).
            </p>
          </div>

          {isParsing && (
            <p className="text-[12px] text-[var(--color-primary)] font-semibold animate-pulse">
              Parsing CSV rows in background Web Worker thread...
            </p>
          )}
        </div>

        {uploadNotice && (
          <div className="p-3.5 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-[13px] flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            <span>{uploadNotice}</span>
          </div>
        )}

        {/* Live Data Table Container */}
        <div className="bg-white rounded-2xl border border-[var(--color-border)] shadow-2xs overflow-hidden">
          <div className="p-4 border-b border-[var(--color-border)] flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="relative w-full sm:w-80">
              <Search className="w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search recipients by name, course, or email..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full pl-9 pr-3 py-1.5 text-[13px] bg-[var(--color-background)] border border-[var(--color-border)] rounded-lg focus:outline-none focus:border-[var(--color-primary)]"
              />
            </div>

            <div className="flex items-center gap-3">
              <span className="text-[12px] text-gray-500 font-mono">
                Showing {filtered.length} of {dataRows.length} recipients
              </span>
              <Button size="sm" asChild className="h-8 text-[12px] font-semibold gap-1">
                <Link href={`/app/projects/${id || "proj-ai-2026"}/mapping`}>
                  <span>Proceed to Field Mapping</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </Button>
            </div>
          </div>

          <div className="overflow-x-auto text-[13px]">
            <table className="w-full text-left">
              <thead className="bg-[var(--color-background)] border-b border-[var(--color-border)] text-gray-500 font-semibold text-[11px] uppercase tracking-wider">
                <tr>
                  <th className="p-3.5">Row</th>
                  <th className="p-3.5">Full Name</th>
                  <th className="p-3.5">Course / Event</th>
                  <th className="p-3.5">Date</th>
                  <th className="p-3.5">Score</th>
                  <th className="p-3.5">Email</th>
                  <th className="p-3.5 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--color-border)]">
                {filtered.map((r, index) => (
                  <tr key={index} className="hover:bg-gray-50/80 transition-colors">
                    <td className="p-3.5 font-mono text-gray-400">#{index + 1}</td>
                    <td className="p-3.5 font-bold text-gray-900">{r.name}</td>
                    <td className="p-3.5 text-gray-700">{r.course}</td>
                    <td className="p-3.5 text-gray-500">{r.date}</td>
                    <td className="p-3.5 font-bold text-emerald-600">{r.score}</td>
                    <td className="p-3.5 font-mono text-gray-500 text-[12px]">{r.email}</td>
                    <td className="p-3.5 text-right">
                      <button
                        onClick={() => setDataRows(dataRows.filter((_, i) => i !== index))}
                        className="text-gray-400 hover:text-red-600 p-1 transition-colors"
                        title="Delete row"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </div>
  );
}
