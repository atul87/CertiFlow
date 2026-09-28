import Link from "next/link";
import {
  BookOpen,
  FileSpreadsheet,
  QrCode,
  ShieldCheck,
  Zap,
  ArrowRight,
  ExternalLink,
  Sparkles,
} from "lucide-react";
import { Navbar } from "@/components/navigation/navbar";
import { Footer } from "@/components/marketing/footer";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

export default function ResourcesPage() {
  const articles = [
    {
      category: "Guide",
      title: "How to Structure Your CSV for 100% Error-Free Bulk Generation",
      description:
        "Learn standard column formatting, Unicode name encoding, and date parsing tricks to prevent formatting bugs during automated PDF issuance.",
      readTime: "5 min read",
      date: "Sep 2026",
    },
    {
      category: "Security",
      title: "Understanding SHA-256 HMAC Signatures in Credential Verification",
      description:
        "A technical deep dive into how CertiFlow generates unforgeable tamper-proof QR codes and prevents Photoshop fraud.",
      readTime: "8 min read",
      date: "Sep 2026",
    },
    {
      category: "Design",
      title: "Typography Hierarchy for Print-Ready A4 Landscape Certificates",
      description:
        "Best practices for choosing serif titles, body lead-ins, calligraphic signatures, and setting auto-shrink boundaries.",
      readTime: "6 min read",
      date: "Aug 2026",
    },
    {
      category: "API & Dev",
      title: "Integrating CertiFlow REST Webhooks into Your LMS or Custom Backend",
      description:
        "Step-by-step tutorial on triggering automated certificate compilation on course completion events using Node.js and Python.",
      readTime: "7 min read",
      date: "Aug 2026",
    },
  ];

  return (
    <div className="min-h-screen bg-[var(--color-background)] flex flex-col">
      <Navbar />

      <main className="flex-1">
        {/* Header */}
        <section className="py-20 border-b border-[var(--color-border)] bg-white text-center">
          <div className="container-marketing max-w-3xl space-y-4">
            <Badge variant="primary" className="text-[12px] px-3 py-1">
              Documentation & Guides
            </Badge>
            <h1 className="text-[36px] sm:text-[48px] font-bold text-[var(--color-text)] tracking-tight">
              CertiFlow Knowledge Hub
            </h1>
            <p className="text-[16px] text-[var(--color-text-secondary)] leading-relaxed">
              In-depth articles, tutorials, and technical guides to help your organization automate high-volume credentials with confidence.
            </p>
          </div>
        </section>

        {/* Resources Grid */}
        <section className="py-16 container-marketing">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {articles.map((art) => (
              <div
                key={art.title}
                className="bg-white rounded-2xl border border-[var(--color-border)] p-8 shadow-2xs hover:border-[var(--color-border-hover)] hover:shadow-md transition-all flex flex-col justify-between space-y-6 group cursor-pointer"
              >
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-[11px] font-bold uppercase tracking-wider text-[var(--color-primary)] bg-indigo-50 px-2.5 py-0.5 rounded">
                      {art.category}
                    </span>
                    <span className="text-[11px] text-gray-400 font-mono">
                      {art.readTime} · {art.date}
                    </span>
                  </div>

                  <h3 className="text-[20px] font-bold text-gray-900 group-hover:text-[var(--color-primary)] transition-colors leading-snug">
                    {art.title}
                  </h3>

                  <p className="text-[14px] text-gray-600 leading-relaxed">
                    {art.description}
                  </p>
                </div>

                <div className="pt-4 border-t border-[var(--color-border)] flex items-center justify-between text-[13px] font-semibold text-[var(--color-primary)]">
                  <span>Read full guide</span>
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </div>
              </div>
            ))}
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}
