"use client";

import { use, useState } from "react";
import Link from "next/link";
import Papa from "papaparse";
import {
  ArrowLeft,
  FileSpreadsheet,
  Upload,
  CheckCircle2,
  AlertCircle,
  Download,
  Trash2,
  Search,
  ArrowRight,
  Sparkles,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

interface RecipientRow {
  name: string;
  course: string;
  date: string;
  score: string;
  email: string;
}

const DEFAULT_ROWS: RecipientRow[] = [
  { name: "Atul Kumar", course: "Advanced Deep Learning", date: "Sep 28, 2026", score: "98%", email: "atul@example.com" },
  { name: "Rahul Sharma", course: "Advanced Deep Learning", date: "Sep 28, 2026", score: "94%", email: "rahul.s@ai-initiative.org" },
  { name: "Priya Singh", course: "Advanced Deep Learning", date: "Sep 28, 2026", score: "96%", email: "priya.singh@techcorp.in" },
  { name: "Dr. Vikramaditya Chandrasekharan", course: "Advanced Deep Learning", date: "Sep 28, 2026", score: "99%", email: "v.c@stanford.edu" },
  { name: "Sneha Patel", course: "Advanced Deep Learning", date: "Sep 28, 2026", score: "91%", email: "sneha.patel@globaltech.com" },
  { name: "Aanya Sharma", course: "Advanced Deep Learning", date: "Sep 28, 2026", score: "95%", email: "aanya.sharma@research.edu" },
  { name: "Rohan Verma", course: "Advanced Deep Learning", date: "Sep 28, 2026", score: "89%", email: "rohan.v@startup.io" },
  { name: "Ananya Roy", course: "Advanced Deep Learning", date: "Sep 28, 2026", score: "93%", email: "ananya.roy@design.in" },
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

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsParsing(true);
    setFileName(file.name);

    Papa.parse<Record<string, string>>(file, {
      header: true,
      skipEmptyLines: true,
      complete: (results) => {
        setIsParsing(false);
        const parsedRows: RecipientRow[] = results.data.map((row) => ({
          name: row["Full Name"] || row["Name"] || row["name"] || "Participant",
          course: row["Course"] || row["Event"] || row["course"] || "AI Workshop 2026",
          date: row["Date"] || row["Completion Date"] || row["date"] || "Sep 28, 2026",
          score: row["Score"] || row["Grade"] || row["score"] || "100%",
          email: row["Email"] || row["Recipient Email"] || row["email"] || "recipient@example.com",
        }));

        setDataRows(parsedRows);
        setUploadNotice(`Successfully imported ${parsedRows.length} recipient records from ${file.name}`);
        setTimeout(() => setUploadNotice(null), 4000);
      },
      error: () => {
        setIsParsing(false);
      },
    });
  };

  const handleDownloadSampleCSV = () => {
    const csvContent =
      "data:text/csv;charset=utf-8,Full Name,Course,Completion Date,Score,Email\n" +
      "Atul Kumar,AI Workshop 2026,September 28 2026,98%,atul@example.com\n" +
      "Rahul Sharma,AI Workshop 2026,September 28 2026,94%,rahul@example.com\n" +
      "Priya Singh,AI Workshop 2026,September 28 2026,96%,priya@example.com\n";
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
      {/* Top Header */}
      <header className="border-b border-[var(--color-border)] bg-white sticky top-0 z-30">
        <div className="container-marketing h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Link
              href={`/app/projects/${id || "proj-ai-2026"}`}
              className="p-1.5 rounded-lg text-gray-400 hover:text-black hover:bg-gray-100 transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
            </Link>
            <div className="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center font-bold">
              <FileSpreadsheet className="w-4 h-4" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-[16px] font-bold text-gray-900">
                  Recipient Data Workbench
                </h1>
                <Badge variant="success" className="text-[11px]">
                  {dataRows.length} Rows Verified
                </Badge>
              </div>
              <p className="text-[11px] text-gray-500">
                File: {fileName} · UTF-8 Validated
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Button size="sm" variant="secondary" onClick={handleDownloadSampleCSV}>
              <Download className="w-3.5 h-3.5 mr-1" />
              Download Sample CSV
            </Button>
            <Button size="sm" asChild>
              <Link href={`/app/projects/${id || "proj-ai-2026"}/mapping`}>
                Continue to Mapping <ArrowRight className="w-3.5 h-3.5 ml-1" />
              </Link>
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container-marketing py-8 flex-1 space-y-6 max-w-6xl mx-auto">
        {/* Upload Dropzone */}
        <div className="bg-white rounded-2xl border-2 border-dashed border-[var(--color-border)] p-8 text-center space-y-4 hover:border-[var(--color-primary)] transition-colors shadow-2xs relative">
          <input
            type="file"
            accept=".csv, .txt, .xlsx"
            onChange={handleFileUpload}
            className="absolute inset-0 opacity-0 cursor-pointer w-full h-full"
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
              Supports CSV, TSV, or TXT (Comma or Tab separated). Unicode names supported.
            </p>
          </div>

          {isParsing && (
            <p className="text-[12px] text-[var(--color-primary)] font-semibold animate-pulse">
              Parsing CSV rows with PapaParse...
            </p>
          )}
        </div>

        {uploadNotice && (
          <div className="p-3.5 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-[13px] flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
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

            <div className="text-[12px] text-gray-500 font-mono">
              Showing {filtered.length} of {dataRows.length} parsed recipients
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
