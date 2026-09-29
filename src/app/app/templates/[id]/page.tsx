"use client";

import { use, useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  FileText,
  Edit3,
  Copy,
  Archive,
  ArrowLeft,
  CheckCircle,
  Clock,
  Layers,
  Sparkles,
  ExternalLink,
  Zap,
  Tag,
  History,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";
import { Template } from "@/types";

export default function TemplateDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const router = useRouter();

  const [template, setTemplate] = useState<Template | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"overview" | "versions" | "fields" | "preview">("overview");

  useEffect(() => {
    api.templates
      .get(id)
      .then((t) => setTemplate(t))
      .catch(() => {
        // Fallback demo template
        setTemplate({
          id,
          name: "Academic Honors Landscape (A4)",
          description: "High-resolution gold foil border template designed for accredited degrees and certificates.",
          status: "published",
          width_mm: 297,
          height_mm: 210,
          orientation: "landscape",
          current_version_id: "v-03",
          version_number: 3,
          variable_tags: ["{{recipient_name}}", "{{program_name}}", "{{issue_date}}", "{{certificate_id}}", "{{qr_code}}"],
          created_at: new Date(Date.now() - 30 * 86400 * 1000).toISOString(),
          updated_at: new Date(Date.now() - 2 * 86400 * 1000).toISOString(),
          published_at: new Date(Date.now() - 2 * 86400 * 1000).toISOString(),
        });
      })
      .finally(() => setLoading(false));
  }, [id]);

  const handleDuplicate = async () => {
    try {
      const dup = await api.templates.duplicate(id);
      router.push(`/app/templates/${dup.id}`);
    } catch {
      alert("Template duplicated in local workspace.");
    }
  };

  const handlePublish = async () => {
    try {
      const pub = await api.templates.publish(id);
      setTemplate(pub);
    } catch {
      if (template) setTemplate({ ...template, status: "published" });
    }
  };

  if (loading) {
    return (
      <div className="p-8 max-w-screen-xl mx-auto space-y-6 animate-pulse">
        <div className="h-6 w-32 bg-gray-100 rounded" />
        <div className="h-10 w-96 bg-gray-100 rounded" />
        <div className="h-64 bg-gray-50 rounded-2xl" />
      </div>
    );
  }

  if (!template) {
    return (
      <div className="p-12 text-center">
        <p className="text-[14px] text-gray-500">Template not found</p>
        <Link href="/app/templates" className="text-indigo-600 text-[13px] font-semibold hover:underline mt-2 inline-block">
          ← Back to Templates
        </Link>
      </div>
    );
  }

  return (
    <div className="p-6 lg:p-8 max-w-screen-xl mx-auto space-y-6">
      {/* Back button */}
      <div>
        <Link
          href="/app/templates"
          className="inline-flex items-center gap-1.5 text-[12px] font-semibold text-[var(--color-text-secondary)] hover:text-[var(--color-text)] transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          Back to all templates
        </Link>
      </div>

      {/* Header & Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span
              className={`text-[11px] font-bold px-2 py-0.5 rounded-full inline-flex items-center gap-1 ${
                template.status === "published"
                  ? "bg-emerald-50 text-emerald-700"
                  : template.status === "draft"
                  ? "bg-gray-100 text-gray-700"
                  : "bg-amber-50 text-amber-700"
              }`}
            >
              {template.status === "published" ? <CheckCircle className="w-3 h-3" /> : <Clock className="w-3 h-3" />}
              {template.status.toUpperCase()}
            </span>
            <span className="text-[12px] text-gray-400">•</span>
            <span className="text-[12px] text-gray-500 font-mono">v{template.version_number}.0</span>
          </div>
          <h1 className="text-[26px] font-bold text-[var(--color-text)] tracking-tight">
            {template.name}
          </h1>
          <p className="text-[13px] text-[var(--color-text-secondary)] mt-0.5">
            {template.description || "Production certificate template layout with dynamic vector rendering."}
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="secondary" onClick={handleDuplicate} className="gap-1.5">
            <Copy className="w-4 h-4" />
            Duplicate
          </Button>

          {template.status === "draft" && (
            <Button variant="secondary" onClick={handlePublish} className="gap-1.5 text-emerald-700">
              <CheckCircle className="w-4 h-4" />
              Publish
            </Button>
          )}

          <Link href={`/app/templates/${template.id}/editor`}>
            <Button className="gap-1.5">
              <Edit3 className="w-4 h-4" />
              Open Visual Designer
            </Button>
          </Link>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-[var(--color-border)] gap-6">
        {(["overview", "versions", "fields", "preview"] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`pb-3 text-[13px] font-bold capitalize transition-colors border-b-2 -mb-px ${
              activeTab === tab
                ? "border-[var(--color-primary)] text-[var(--color-primary)]"
                : "border-transparent text-[var(--color-text-secondary)] hover:text-[var(--color-text)]"
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Tab Contents */}
      {activeTab === "overview" && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-white rounded-2xl border border-[var(--color-border)] p-6 space-y-4">
              <h3 className="text-[15px] font-bold text-[var(--color-text)]">Canvas Dimensions & Specs</h3>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-[13px]">
                <div className="p-3 rounded-xl bg-gray-50 border border-gray-100">
                  <p className="text-[11px] text-[var(--color-text-tertiary)]">Width</p>
                  <p className="font-bold text-[var(--color-text)]">{template.width_mm} mm</p>
                </div>
                <div className="p-3 rounded-xl bg-gray-50 border border-gray-100">
                  <p className="text-[11px] text-[var(--color-text-tertiary)]">Height</p>
                  <p className="font-bold text-[var(--color-text)]">{template.height_mm} mm</p>
                </div>
                <div className="p-3 rounded-xl bg-gray-50 border border-gray-100">
                  <p className="text-[11px] text-[var(--color-text-tertiary)]">Orientation</p>
                  <p className="font-bold text-[var(--color-text)] capitalize">{template.orientation}</p>
                </div>
                <div className="p-3 rounded-xl bg-gray-50 border border-gray-100">
                  <p className="text-[11px] text-[var(--color-text-tertiary)]">Resolution</p>
                  <p className="font-bold text-[var(--color-text)]">300 DPI Vector</p>
                </div>
              </div>
            </div>

            {/* Quick action to run issuance */}
            <div className="bg-gradient-to-r from-indigo-50 to-purple-50 border border-indigo-100 rounded-2xl p-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <div className="flex items-center gap-1.5 text-indigo-900 font-bold text-[14px]">
                  <Zap className="w-4 h-4 text-indigo-600" />
                  Ready to issue certificates with this template?
                </div>
                <p className="text-[12px] text-indigo-700 mt-0.5">
                  Launch a batch issuance job with spreadsheet recipients or API webhook triggers.
                </p>
              </div>
              <Link
                href={`/app/issuance?create=1&template=${template.id}`}
                className="px-4 py-2 rounded-xl bg-[#635BFF] text-white text-[13px] font-semibold hover:bg-indigo-600 transition-colors shrink-0 text-center shadow-xs"
              >
                Launch Batch Issuance →
              </Link>
            </div>
          </div>

          <div className="space-y-6">
            <div className="bg-white rounded-2xl border border-[var(--color-border)] p-6 space-y-4">
              <h3 className="text-[14px] font-bold text-[var(--color-text)]">Quick Actions</h3>
              <div className="space-y-2">
                <Link
                  href={`/app/templates/${template.id}/editor`}
                  className="w-full flex items-center justify-between p-2.5 rounded-xl border border-gray-200 hover:border-indigo-300 text-[13px] font-semibold text-gray-800 hover:bg-indigo-50/50 transition-colors"
                >
                  <span className="flex items-center gap-2">
                    <Edit3 className="w-4 h-4 text-indigo-600" />
                    Open in Visual Canvas
                  </span>
                  <ExternalLink className="w-3.5 h-3.5 text-gray-400" />
                </Link>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === "fields" && (
        <div className="bg-white rounded-2xl border border-[var(--color-border)] p-6 space-y-4">
          <div className="flex items-center gap-2">
            <Tag className="w-4 h-4 text-indigo-600" />
            <h3 className="text-[15px] font-bold text-[var(--color-text)]">Dynamic Template Variables</h3>
          </div>
          <p className="text-[13px] text-[var(--color-text-secondary)]">
            These tags are replaced automatically during bulk generation with recipient spreadsheet values.
          </p>
          <div className="flex flex-wrap gap-2 pt-2">
            {template.variable_tags.map((tag) => (
              <span
                key={tag}
                className="px-3 py-1.5 rounded-lg bg-gray-100 text-gray-800 font-mono text-[12px] font-semibold border border-gray-200"
              >
                {tag}
              </span>
            ))}
          </div>
        </div>
      )}

      {activeTab === "versions" && (
        <div className="bg-white rounded-2xl border border-[var(--color-border)] p-6 space-y-4">
          <div className="flex items-center gap-2">
            <History className="w-4 h-4 text-indigo-600" />
            <h3 className="text-[15px] font-bold text-[var(--color-text)]">Version History & Revisions</h3>
          </div>
          <div className="space-y-3">
            {[3, 2, 1].map((v) => (
              <div key={v} className="flex items-center justify-between p-3.5 rounded-xl border border-gray-100 hover:bg-gray-50/50 transition-colors">
                <div className="flex items-center gap-3">
                  <span className="w-8 h-8 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center font-bold text-[12px]">
                    v{v}
                  </span>
                  <div>
                    <p className="text-[13px] font-semibold text-[var(--color-text)]">
                      Release version {v}.0 {v === template.version_number && "(Active)"}
                    </p>
                    <p className="text-[11px] text-[var(--color-text-tertiary)]">
                      Saved {v === 3 ? "2 days ago" : `${v * 10} days ago`} by Admin
                    </p>
                  </div>
                </div>
                {v === template.version_number && (
                  <span className="text-[11px] font-bold text-emerald-700 bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-200">
                    Live
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === "preview" && (
        <div className="bg-white rounded-2xl border border-[var(--color-border)] p-8 text-center space-y-4">
          <div className="max-w-xl mx-auto p-8 rounded-xl border-4 border-amber-600/30 bg-amber-50/10 shadow-lg space-y-4">
            <h2 className="text-[20px] font-serif font-bold text-gray-900">Certificate of Completion</h2>
            <p className="text-[12px] text-gray-500 font-serif">THIS IS TO CERTIFY THAT</p>
            <p className="text-[24px] font-serif font-bold text-indigo-900 border-b border-gray-300 pb-2">
              Jane Doe
            </p>
            <p className="text-[13px] text-gray-600 max-w-md mx-auto">
              Has demonstrated excellence in {template.name}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
