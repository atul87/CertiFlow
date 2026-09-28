import { Navbar } from "@/components/navigation/navbar";
import { Footer } from "@/components/marketing/footer";
import { Badge } from "@/components/ui/badge";

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-[var(--color-background)] flex flex-col">
      <Navbar />

      <main className="flex-1 py-16 container-marketing max-w-3xl space-y-8">
        <div>
          <Badge variant="outline" className="mb-2">
            Legal & Compliance
          </Badge>
          <h1 className="text-[36px] font-bold text-gray-900 tracking-tight">
            Privacy Policy
          </h1>
          <p className="text-[14px] text-gray-500 mt-1">
            Last updated: September 28, 2026 · CertiFlow Platform Inc.
          </p>
        </div>

        <div className="prose prose-gray max-w-none text-[15px] text-gray-700 space-y-6 leading-relaxed bg-white p-8 rounded-2xl border border-[var(--color-border)] shadow-2xs">
          <section className="space-y-2">
            <h2 className="text-[20px] font-bold text-gray-900">1. Overview & Commitment to Data Privacy</h2>
            <p>
              At CertiFlow, data protection and confidentiality are paramount. We understand that educational institutions, corporations, and organizers entrust us with recipient rosters containing names, email addresses, and assessment scores.
            </p>
          </section>

          <section className="space-y-2">
            <h2 className="text-[20px] font-bold text-gray-900">2. Ephemeral Processing & Zero-Retention</h2>
            <p>
              When utilizing CertiFlow&apos;s client-side parsing mode, spreadsheets uploaded via CSV or XLSX are processed locally within your browser&apos;s memory environment. We do not persist raw recipient rosters in permanent server storage unless explicitly enabled for long-term credential registry management.
            </p>
          </section>

          <section className="space-y-2">
            <h2 className="text-[20px] font-bold text-gray-900">3. Information Collected</h2>
            <p>
              We collect information necessary to operate your organization account, including administrator names, billing email addresses, organization titles, and encrypted credentials. Public verification registries store only the minimal cryptographically signed payload (Certificate UUID, recipient name, course title, and issue date).
            </p>
          </section>

          <section className="space-y-2">
            <h2 className="text-[20px] font-bold text-gray-900">4. GDPR and FERPA Compliance</h2>
            <p>
              CertiFlow complies with the General Data Protection Regulation (GDPR) and the Family Educational Rights and Privacy Act (FERPA). Users possess the legal right to access, rectify, or purge their certificate records and revoked identifiers upon written request.
            </p>
          </section>

          <section className="space-y-2">
            <h2 className="text-[20px] font-bold text-gray-900">5. Contact Information</h2>
            <p>
              For privacy-related inquiries or Data Protection Officer communications, contact us at <code>privacy@certiflow.io</code>.
            </p>
          </section>
        </div>
      </main>

      <Footer />
    </div>
  );
}
