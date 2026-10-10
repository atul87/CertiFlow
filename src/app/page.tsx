"use client";

import { useState } from "react";
import dynamic from "next/dynamic";
import { AnnouncementBar } from "@/components/navigation/announcement-bar";
import { Navbar } from "@/components/navigation/navbar";
import { HeroSection } from "@/components/marketing/hero-section";
import { TrustStrip } from "@/components/marketing/trust-strip";
import { InteractiveDemoSection } from "@/components/marketing/interactive-demo-section";
import { ProblemSection } from "@/components/marketing/problem-section";
import { WorkflowSection } from "@/components/marketing/workflow-section";
import {
  FeatureBulk,
  FeatureEditor,
  FeatureDynamicFields,
  FeatureAutoFit,
  FeatureVerification,
  FeatureDelivery,
  FeatureBatchDashboard,
} from "@/components/marketing/feature-sections";
import { Footer } from "@/components/marketing/footer";

const UseCasesSection = dynamic(
  () => import("@/components/marketing/use-cases-section").then((mod) => mod.UseCasesSection)
);
const TemplateGallery = dynamic(
  () => import("@/components/marketing/template-gallery").then((mod) => mod.TemplateGallery)
);
const SecuritySection = dynamic(
  () => import("@/components/marketing/security-section").then((mod) => mod.SecuritySection)
);
const PricingSection = dynamic(
  () => import("@/components/marketing/pricing-section").then((mod) => mod.PricingSection)
);
const FAQSection = dynamic(
  () => import("@/components/marketing/faq-section").then((mod) => mod.FAQSection)
);
const FinalCTASection = dynamic(
  () => import("@/components/marketing/final-cta-section").then((mod) => mod.FinalCTASection)
);
const DemoVideoModal = dynamic(
  () => import("@/components/marketing/demo-video-modal").then((mod) => mod.DemoVideoModal),
  { ssr: false }
);

export default function LandingPage() {
  const [isVideoModalOpen, setIsVideoModalOpen] = useState(false);

  return (
    <div className="min-h-screen flex flex-col bg-[var(--color-background)] text-[var(--color-text)] antialiased">
      {/* 1. Announcement Bar */}
      <AnnouncementBar />

      {/* 2. Frosted / Sticky Navbar */}
      <Navbar onWatchDemo={() => setIsVideoModalOpen(true)} />

      {/* Main High-Conversion Page Flow */}
      <main className="flex-1">
        {/* 3. Hero Section (50/50 Desktop Two-Column Layout + Live Animation) */}
        <HeroSection onWatchDemo={() => setIsVideoModalOpen(true)} />

        {/* 4. Trust Strip */}
        <TrustStrip />

        {/* 5. Interactive Demo (Hero -> Interactive Demo instant hands-on preview) */}
        <div id="demo" className="scroll-mt-20">
          <InteractiveDemoSection />
        </div>

        {/* 6. Problem Section & Three-Step Workflow */}
        <ProblemSection />
        <div id="workflow" className="scroll-mt-20">
          <WorkflowSection />
        </div>

        {/* 7. Product Features (Editorial showcases: AutoFit, Dynamic Fields, Delivery, RBAC) */}
        <div id="features" className="scroll-mt-20">
          <FeatureBulk />
          <FeatureEditor />
          <FeatureDynamicFields />
          <FeatureAutoFit />
          <FeatureVerification />
          <FeatureDelivery />
          <FeatureBatchDashboard />
        </div>

        {/* 8. Segmented Solutions & Use Cases */}
        <div id="solutions" className="scroll-mt-20">
          <UseCasesSection />
        </div>

        {/* 9. Template Gallery (High-DPI Vector Previews) */}
        <div id="templates" className="scroll-mt-20">
          <TemplateGallery />
        </div>

        {/* 10. Security & Cryptographic Verification (SHA-256 + QR + W3C VC) */}
        <div id="security" className="scroll-mt-20">
          <SecuritySection />
        </div>

        {/* 11. Transparent Pricing (Correct ₹1,999/mo tier + 15-row comparison matrix) */}
        <div id="pricing" className="scroll-mt-20">
          <PricingSection />
        </div>

        {/* 12. Accessible FAQ Accordion */}
        <div id="faq" className="scroll-mt-20">
          <FAQSection />
        </div>

        {/* 13. High-Conversion Final CTA */}
        <FinalCTASection />
      </main>

      {/* 14. Enterprise Footer */}
      <Footer />

      {/* 60-Second Video Walkthrough Modal */}
      <DemoVideoModal
        isOpen={isVideoModalOpen}
        onClose={() => setIsVideoModalOpen(false)}
      />
    </div>
  );
}
