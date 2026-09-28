import Link from "next/link";
import {
  Sparkles,
  Zap,
  Layers,
  QrCode,
  Mail,
  ShieldCheck,
  CheckCircle2,
  ArrowRight,
  FileSpreadsheet,
  Sliders,
  Cpu,
  Lock,
  Download,
  Share2,
} from "lucide-react";
import { Navbar } from "@/components/navigation/navbar";
import { Footer } from "@/components/marketing/footer";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

export default function FeaturesPage() {
  const features = [
    {
      icon: Cpu,
      badge: "High-Throughput Core",
      title: "Batch PDF Compilation Engine",
      description:
        "Compile 500+ vector PDF certificates in under 5 seconds. CertiFlow renders directly to vector paths at 300 DPI print quality without heavy browser DOM bottlenecks.",
      highlights: [
        "48+ certificates per second rendering throughput",
        "Deterministic vector output with embedded fonts",
        "Automatic ZIP archive packaging with recipient index ledger",
        "Zero memory bloat, scales to 10,000+ rows effortlessly",
      ],
    },
    {
      icon: Sliders,
      badge: "Design Precision",
      title: "Full Canvas Studio & Auto-Fit Typography",
      description:
        "A desktop-class visual editor combining Canva simplicity with Figma precision. Drag dynamic variables, configure serif or sans-serif hierarchies, and let Smart-Fit prevent text overflows.",
      highlights: [
        "Smart auto-shrink: long names scale gracefully rather than clipping",
        "Dynamic tag bindings: {{NAME}}, {{COURSE}}, {{DATE}}, {{SCORE}}",
        "Curated Google Fonts: Playfair Display, Cinzel, Inter, Outfit",
        "Draggable elements with snapping guidelines & print safe margins",
      ],
    },
    {
      icon: QrCode,
      badge: "Anti-Fraud Architecture",
      title: "Cryptographic QR Code Verification",
      description:
        "Every certificate gets a unique, tamper-proof SHA-256 digital signature embedded into a scannable QR code. Employers and admissions officers verify authenticity instantly.",
      highlights: [
        "Direct scan to hosted verification portal (certiflow.app/verify/id)",
        "Cryptographic hash mismatch detection stops Photoshop fraud",
        "Instant one-click revocation from the admin dashboard",
        "White-label custom verification domains (verify.yourorg.edu)",
      ],
    },
    {
      icon: Mail,
      badge: "Fulfillment Automation",
      title: "Automated Email & Multi-Channel Delivery",
      description:
        "Skip manual email attachments. CertiFlow dispatches personalized emails with attached high-res PDFs and direct credential verification links via high-deliverability SMTP.",
      highlights: [
        "Customizable HTML/Plaintext email body templates",
        "Dynamic mail merge tags: {{NAME}}, {{COURSE}}, {{VERIFY_URL}}",
        "Real-time delivery telemetry (sent, opened, bounced)",
        "Direct export to bulk ZIP archive or CSV ledger",
      ],
    },
    {
      icon: Lock,
      badge: "Enterprise Security",
      title: "Zero-Retention Privacy & Compliance",
      description:
        "Your recipient data remains strictly confidential. Process spreadsheets in ephemeral client memory or purge data automatically post-generation to satisfy strict GDPR requirements.",
      highlights: [
        "Ephemeral client-side parsing via PapaParse",
        "Optional zero data retention mode",
        "SOC 2 Type II and GDPR compliant infrastructure",
        "Role-based access controls and audit logs",
      ],
    },
    {
      icon: Zap,
      badge: "Developer Platform",
      title: "REST API & Webhooks",
      description:
        "Trigger certificates on course completion or event check-in via our straightforward developer API. Integrate with Teachable, Canvas LMS, Eventbrite, or custom backends.",
      highlights: [
        "Idempotent POST /v1/certificates endpoint",
        "Real-time webhooks for certificate.verified and certificate.revoked",
        "Official SDKs for Node.js, Python, and Go",
        "Sandbox testing mode with zero quota consumption",
      ],
    },
  ];

  return (
    <div className="min-h-screen bg-[var(--color-background)] flex flex-col">
      <Navbar />

      <main className="flex-1">
        {/* Hero Header */}
        <section className="py-20 border-b border-[var(--color-border)] bg-white relative overflow-hidden">
          <div className="container-marketing max-w-4xl text-center space-y-4">
            <Badge variant="primary" className="text-[12px] px-3 py-1">
              Platform Architecture
            </Badge>
            <h1 className="text-[36px] sm:text-[48px] font-bold text-[var(--color-text)] tracking-tight">
              Engineered for Speed, Precision, and Absolute Credential Trust
            </h1>
            <p className="text-[16px] sm:text-[18px] text-[var(--color-text-secondary)] leading-relaxed max-w-2xl mx-auto">
              Explore how CertiFlow automates the entire lifecycle: from spreadsheet ingestion and canvas typography to cryptographic verification and automated email dispatch.
            </p>

            <div className="pt-4 flex flex-wrap items-center justify-center gap-3">
              <Button size="lg" asChild>
                <Link href="/demo">
                  Test the Interactive Sandbox
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Link>
              </Button>
              <Button size="lg" variant="secondary" asChild>
                <Link href="/pricing">View Pricing & Plans</Link>
              </Button>
            </div>
          </div>
        </section>

        {/* Feature Deep Dive Grid */}
        <section className="py-20 container-marketing">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {features.map((feat) => {
              const Icon = feat.icon;
              return (
                <div
                  key={feat.title}
                  className="bg-white rounded-2xl border border-[var(--color-border)] p-8 shadow-2xs hover:border-[var(--color-border-hover)] transition-all flex flex-col justify-between space-y-6"
                >
                  <div className="space-y-4">
                    <div className="w-12 h-12 rounded-xl bg-[var(--color-primary-light)] text-[var(--color-primary)] flex items-center justify-center">
                      <Icon className="w-6 h-6" />
                    </div>

                    <div>
                      <span className="text-[11px] font-bold uppercase tracking-wider text-[var(--color-primary)]">
                        {feat.badge}
                      </span>
                      <h2 className="text-[20px] font-bold text-[var(--color-text)] mt-1">
                        {feat.title}
                      </h2>
                      <p className="text-[14px] text-[var(--color-text-secondary)] mt-2 leading-relaxed">
                        {feat.description}
                      </p>
                    </div>
                  </div>

                  <div className="border-t border-[var(--color-border)] pt-4 space-y-2">
                    {feat.highlights.map((h) => (
                      <div key={h} className="flex items-start gap-2 text-[13px] text-gray-700">
                        <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                        <span>{h}</span>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </section>

        {/* Closing CTA */}
        <section className="py-20 border-t border-[var(--color-border)] bg-gray-900 text-white text-center">
          <div className="container-marketing max-w-2xl space-y-5">
            <h2 className="text-[30px] font-bold">Ready to automate your certificates?</h2>
            <p className="text-gray-400 text-[15px]">
              Join hundreds of universities, tech bootcamps, and global summits using CertiFlow.
            </p>
            <Button size="lg" className="bg-[var(--color-primary)] text-white hover:bg-[var(--color-primary-hover)]" asChild>
              <Link href="/demo">Launch CertiFlow Studio Free</Link>
            </Button>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}
