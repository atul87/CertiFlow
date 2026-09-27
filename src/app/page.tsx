"use client";

import { useState } from "react";
import { AnnouncementBar } from "@/components/navigation/announcement-bar";
import { Navbar } from "@/components/navigation/navbar";
import { HeroSection } from "@/components/marketing/hero-section";
import { TrustStrip } from "@/components/marketing/trust-strip";
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
import { InteractiveDemoSection } from "@/components/marketing/interactive-demo-section";
import { UseCasesSection } from "@/components/marketing/use-cases-section";
import { TemplateGallery } from "@/components/marketing/template-gallery";
import { SecuritySection } from "@/components/marketing/security-section";
import { PricingSection } from "@/components/marketing/pricing-section";
import { FAQSection } from "@/components/marketing/faq-section";
import { FinalCTASection } from "@/components/marketing/final-cta-section";
import { Footer } from "@/components/marketing/footer";
import { DemoVideoModal } from "@/components/marketing/demo-video-modal";

export default function LandingPage() {
  const [isVideoModalOpen, setIsVideoModalOpen] = useState(false);

  return (
    <div className="min-h-screen flex flex-col bg-[var(--color-background)] text-[var(--color-text)] antialiased">
      {/* 1. Announcement Bar */}
      <AnnouncementBar />

      {/* 2. Navbar */}
      <Navbar onWatchDemo={() => setIsVideoModalOpen(true)} />

      {/* Main Page Flow */}
      <main className="flex-1">
        {/* 3. Hero Section (50/50 Desktop Two-Column Layout + Live Animation) */}
        <HeroSection onWatchDemo={() => setIsVideoModalOpen(true)} />

        {/* 4. Trust Strip */}
        <TrustStrip />

        {/* 5. Problem Section (Manual vs Automated) */}
        <ProblemSection />

        {/* 6. Three-Step Workflow */}
        <WorkflowSection />

        {/* 7. Feature Showcases (Large alternating 50/50 editorial sections) */}
        <div id="features">
          <FeatureBulk />
          <FeatureEditor />
          <FeatureDynamicFields />
          <FeatureAutoFit />
          <FeatureVerification />
          <FeatureDelivery />
          <FeatureBatchDashboard />
        </div>

        {/* 8. Interactive Demo (No signup required) */}
        <div id="demo">
          <InteractiveDemoSection />
        </div>

        {/* 9. Segmented Use Cases */}
        <div id="solutions">
          <UseCasesSection />
        </div>

        {/* 10. Template Gallery (4 cards/row desktop) */}
        <div id="templates">
          <TemplateGallery />
        </div>

        {/* 11. Security & Privacy Governance */}
        <div id="security">
          <SecuritySection />
        </div>

        {/* 12. Transparent Pricing */}
        <div id="pricing">
          <PricingSection />
        </div>

        {/* 13. FAQ Accordion */}
        <div id="faq">
          <FAQSection />
        </div>

        {/* 14. Final High-Conversion CTA */}
        <FinalCTASection />
      </main>

      {/* 15. SaaS Footer */}
      <Footer />

      {/* 60-Second Video Walkthrough Modal */}
      <DemoVideoModal
        isOpen={isVideoModalOpen}
        onClose={() => setIsVideoModalOpen(false)}
      />
    </div>
  );
}
