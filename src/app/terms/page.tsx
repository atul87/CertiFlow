import { Navbar } from "@/components/navigation/navbar";
import { Footer } from "@/components/marketing/footer";
import { Badge } from "@/components/ui/badge";

export default function TermsPage() {
  return (
    <div className="min-h-screen bg-[var(--color-background)] flex flex-col">
      <Navbar />

      <main className="flex-1 py-16 container-marketing max-w-3xl space-y-8">
        <div>
          <Badge variant="outline" className="mb-2">
            Legal Agreement
          </Badge>
          <h1 className="text-[36px] font-bold text-gray-900 tracking-tight">
            Terms of Service
          </h1>
          <p className="text-[14px] text-gray-500 mt-1">
            Last updated: September 28, 2026 · CertiFlow Platform Inc.
          </p>
        </div>

        <div className="prose prose-gray max-w-none text-[15px] text-gray-700 space-y-6 leading-relaxed bg-white p-8 rounded-2xl border border-[var(--color-border)] shadow-2xs">
          <section className="space-y-2">
            <h2 className="text-[20px] font-bold text-gray-900">1. Acceptance of Terms</h2>
            <p>
              By accessing or using the CertiFlow platform, APIs, or verification services, you agree to be bound by these Terms of Service. If you are entering into this agreement on behalf of a school, university, or corporate entity, you represent that you possess the requisite authority to bind such entity.
            </p>
          </section>

          <section className="space-y-2">
            <h2 className="text-[20px] font-bold text-gray-900">2. Permitted Use & Credential Authenticity</h2>
            <p>
              CertiFlow is designed exclusively for legitimate credential issuance, academic accolades, event participation honors, and corporate professional certifications. You agree not to generate fraudulent, deceptive, or misleading degrees, diplomas, or medical licenses.
            </p>
          </section>

          <section className="space-y-2">
            <h2 className="text-[20px] font-bold text-gray-900">3. Service Levels & Uptime</h2>
            <p>
              We provide 99.9% scheduled uptime for public verification endpoints. We maintain automated multi-region backups to ensure cryptographic verification hashes remain perpetually accessible to credential verifiers worldwide.
            </p>
          </section>

          <section className="space-y-2">
            <h2 className="text-[20px] font-bold text-gray-900">4. Intellectual Property</h2>
            <p>
              You retain all ownership, copyright, and trademark rights to your certificate designs, background templates, institutional logos, and recipient databases. CertiFlow claims no intellectual property rights over materials you upload to our studio.
            </p>
          </section>
        </div>
      </main>

      <Footer />
    </div>
  );
}
