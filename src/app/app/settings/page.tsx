"use client";

import { useState } from "react";
import Link from "next/link";
import {
  Sparkles,
  Building,
  Palette,
  ShieldCheck,
  Key,
  CreditCard,
  Check,
  Copy,
  ArrowLeft,
  Upload,
  Globe,
  Lock,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";

export default function OrganizationSettingsPage() {
  const [activeTab, setActiveTab] = useState("general");
  const [savedSuccess, setSavedSuccess] = useState(false);
  const [copiedKey, setCopiedKey] = useState<string | null>(null);

  const handleSave = () => {
    setSavedSuccess(true);
    setTimeout(() => setSavedSuccess(false), 2500);
  };

  const handleCopyKey = (key: string, label: string) => {
    navigator.clipboard.writeText(key);
    setCopiedKey(label);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  return (
    <div className="min-h-screen bg-[var(--color-background)] flex flex-col">
      {/* Top Header */}
      <header className="border-b border-[var(--color-border)] bg-white sticky top-0 z-30">
        <div className="container-marketing h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Link href="/app" className="font-bold flex items-center gap-2 text-[15px]">
              <span className="text-[var(--color-primary)]">✦</span> CERTIFLOW
            </Link>
            <div className="h-4 w-px bg-gray-200" />
            <span className="text-[13px] font-medium text-gray-500">
              Organization Settings & Branding Kit
            </span>
          </div>

          <div className="flex items-center gap-2">
            <Button size="sm" variant="secondary" asChild>
              <Link href="/app">
                <ArrowLeft className="w-3.5 h-3.5 mr-1" />
                Back to Dashboard
              </Link>
            </Button>
            <Button size="sm" onClick={handleSave}>
              Save All Changes
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container-marketing py-8 flex-1 max-w-4xl mx-auto space-y-6">
        <div>
          <h1 className="text-[24px] font-bold text-[var(--color-text)]">
            Organization Settings
          </h1>
          <p className="text-[13px] text-gray-500 mt-0.5">
            Configure your issuing organization branding, custom verification domain, API keys, and team permissions.
          </p>
        </div>

        {savedSuccess && (
          <div className="p-3.5 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-[13px] flex items-center gap-2">
            <Check className="w-4 h-4 text-emerald-600" />
            <span>Settings and branding kit successfully saved!</span>
          </div>
        )}

        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="bg-white border border-[var(--color-border)] p-1 rounded-xl mb-6">
            <TabsTrigger value="general" className="flex items-center gap-1.5 text-[13px]">
              <Building className="w-3.5 h-3.5" />
              General
            </TabsTrigger>
            <TabsTrigger value="branding" className="flex items-center gap-1.5 text-[13px]">
              <Palette className="w-3.5 h-3.5" />
              Branding Kit
            </TabsTrigger>
            <TabsTrigger value="domain" className="flex items-center gap-1.5 text-[13px]">
              <Globe className="w-3.5 h-3.5" />
              Custom Domain
            </TabsTrigger>
            <TabsTrigger value="api" className="flex items-center gap-1.5 text-[13px]">
              <Key className="w-3.5 h-3.5" />
              API & Webhooks
            </TabsTrigger>
            <TabsTrigger value="billing" className="flex items-center gap-1.5 text-[13px]">
              <CreditCard className="w-3.5 h-3.5" />
              Plan & Billing
            </TabsTrigger>
          </TabsList>

          {/* TAB 1: GENERAL */}
          <TabsContent value="general">
            <div className="bg-white rounded-2xl border border-[var(--color-border)] p-6 space-y-5 shadow-2xs">
              <h2 className="text-[16px] font-bold text-gray-900">Organization Profile</h2>

              <div className="space-y-4">
                <div>
                  <label className="block text-[13px] font-semibold text-gray-700 mb-1">
                    Organization Name
                  </label>
                  <input
                    type="text"
                    defaultValue="Academy of Advanced Computing"
                    className="w-full px-3 py-2 rounded-xl border border-[var(--color-border)] text-[14px]"
                  />
                  <p className="text-[11px] text-gray-400 mt-1">
                    Displayed on issued credentials and public verification badges.
                  </p>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-[13px] font-semibold text-gray-700 mb-1">
                      Organization Slug / URL
                    </label>
                    <div className="flex items-center">
                      <span className="px-3 py-2 bg-gray-100 border border-r-0 border-[var(--color-border)] rounded-l-xl text-gray-500 text-[13px] font-mono">
                        certiflow.app/org/
                      </span>
                      <input
                        type="text"
                        defaultValue="aac-edu"
                        className="w-full px-3 py-2 rounded-r-xl border border-[var(--color-border)] text-[13px] font-mono"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-[13px] font-semibold text-gray-700 mb-1">
                      Support Contact Email
                    </label>
                    <input
                      type="email"
                      defaultValue="credentials@aac.edu"
                      className="w-full px-3 py-2 rounded-xl border border-[var(--color-border)] text-[13px]"
                    />
                  </div>
                </div>
              </div>
            </div>
          </TabsContent>

          {/* TAB 2: BRANDING KIT */}
          <TabsContent value="branding">
            <div className="bg-white rounded-2xl border border-[var(--color-border)] p-6 space-y-6 shadow-2xs">
              <div>
                <h2 className="text-[16px] font-bold text-gray-900">Official Brand Assets</h2>
                <p className="text-[12px] text-gray-500 mt-0.5">
                  Defaults applied to new templates, email dispatches, and verification landing pages.
                </p>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                {/* Brand Colors */}
                <div className="space-y-3">
                  <label className="block text-[13px] font-semibold text-gray-700">
                    Primary Brand Color
                  </label>
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-[#635BFF] border border-black/10 shadow-xs" />
                    <input
                      type="text"
                      defaultValue="#635BFF"
                      className="w-32 px-3 py-2 rounded-xl border border-[var(--color-border)] text-[13px] font-mono uppercase"
                    />
                  </div>
                </div>

                <div className="space-y-3">
                  <label className="block text-[13px] font-semibold text-gray-700">
                    Accent / Seal Color
                  </label>
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-[#D97706] border border-black/10 shadow-xs" />
                    <input
                      type="text"
                      defaultValue="#D97706"
                      className="w-32 px-3 py-2 rounded-xl border border-[var(--color-border)] text-[13px] font-mono uppercase"
                    />
                  </div>
                </div>
              </div>

              {/* Default Signatory */}
              <div className="border-t border-[var(--color-border)] pt-5 space-y-4">
                <h3 className="text-[14px] font-bold text-gray-800">
                  Default Signatory & Credentials
                </h3>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-[12px] font-semibold text-gray-700 mb-1">
                      Signer Full Name
                    </label>
                    <input
                      type="text"
                      defaultValue="Dr. Arthur Pendelton"
                      className="w-full px-3 py-2 rounded-xl border border-[var(--color-border)] text-[13px]"
                    />
                  </div>

                  <div>
                    <label className="block text-[12px] font-semibold text-gray-700 mb-1">
                      Official Title
                    </label>
                    <input
                      type="text"
                      defaultValue="Chancellor & Dean of Engineering"
                      className="w-full px-3 py-2 rounded-xl border border-[var(--color-border)] text-[13px]"
                    />
                  </div>
                </div>
              </div>
            </div>
          </TabsContent>

          {/* TAB 3: CUSTOM DOMAIN */}
          <TabsContent value="domain">
            <div className="bg-white rounded-2xl border border-[var(--color-border)] p-6 space-y-5 shadow-2xs">
              <div>
                <h2 className="text-[16px] font-bold text-gray-900">Custom Verification Domain</h2>
                <p className="text-[12px] text-gray-500 mt-0.5">
                  Host your public QR verification page on your own subdomain with automatic SSL.
                </p>
              </div>

              <div className="p-4 rounded-xl bg-gray-50 border border-[var(--color-border)] space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-[13px] font-semibold text-gray-800">Custom Subdomain</span>
                  <Badge variant="success" className="text-[11px]">
                    SSL Active
                  </Badge>
                </div>
                <div className="flex items-center">
                  <input
                    type="text"
                    defaultValue="verify.aac.edu"
                    className="w-full px-3 py-2 rounded-xl border border-[var(--color-border)] text-[13px] font-mono bg-white"
                  />
                </div>
                <p className="text-[11px] text-gray-500">
                  Point a <strong>CNAME</strong> record for <code>verify.aac.edu</code> to <code>cname.certiflow.app</code> in your DNS provider (Cloudflare, AWS Route 53, GoDaddy).
                </p>
              </div>
            </div>
          </TabsContent>

          {/* TAB 4: API & WEBHOOKS */}
          <TabsContent value="api">
            <div className="bg-white rounded-2xl border border-[var(--color-border)] p-6 space-y-6 shadow-2xs">
              <div>
                <h2 className="text-[16px] font-bold text-gray-900">REST API & Programmatic Issuance</h2>
                <p className="text-[12px] text-gray-500 mt-0.5">
                  Integrate automated certificate issuance directly into your LMS, CRM, or backend code.
                </p>
              </div>

              <div className="space-y-4">
                {/* Live Key */}
                <div className="p-4 rounded-xl border border-[var(--color-border)] space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-[13px] font-semibold text-gray-800">Production Secret Key</span>
                    <Badge variant="primary" className="text-[10px]">
                      Live
                    </Badge>
                  </div>
                  <div className="flex items-center gap-2">
                    <input
                      type="password"
                      value="cf_live_948f2b719c834a90de81bc44"
                      readOnly
                      className="w-full px-3 py-2 rounded-lg bg-gray-50 border border-gray-200 text-[12px] font-mono text-gray-700"
                    />
                    <Button
                      size="sm"
                      variant="secondary"
                      onClick={() => handleCopyKey("cf_live_948f2b719c834a90de81bc44", "live")}
                    >
                      {copiedKey === "live" ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
                    </Button>
                  </div>
                </div>

                {/* Webhook Endpoint */}
                <div className="p-4 rounded-xl border border-[var(--color-border)] space-y-2">
                  <span className="text-[13px] font-semibold text-gray-800 block">
                    Webhook Destination URL
                  </span>
                  <input
                    type="url"
                    defaultValue="https://api.aac.edu/webhooks/certiflow"
                    className="w-full px-3 py-2 rounded-lg border border-[var(--color-border)] text-[12px] font-mono"
                  />
                  <p className="text-[11px] text-gray-400">
                    Events triggered: <code>certificate.generated</code>, <code>certificate.verified</code>, <code>certificate.revoked</code>
                  </p>
                </div>
              </div>
            </div>
          </TabsContent>

          {/* TAB 5: BILLING */}
          <TabsContent value="billing">
            <div className="bg-white rounded-2xl border border-[var(--color-border)] p-6 space-y-6 shadow-2xs">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-[16px] font-bold text-gray-900">Current Subscription</h2>
                  <p className="text-[12px] text-gray-500">Pro Creator Plan ($39 / month)</p>
                </div>
                <Badge variant="success">Active</Badge>
              </div>

              {/* Usage bar */}
              <div className="p-4 rounded-xl bg-gray-50 border border-gray-200 space-y-2">
                <div className="flex justify-between text-[13px] font-semibold">
                  <span>Monthly Certificate Quota</span>
                  <span>500 / 2,500 certs used (20%)</span>
                </div>
                <div className="w-full h-2.5 bg-gray-200 rounded-full overflow-hidden">
                  <div className="h-full bg-[var(--color-primary)] rounded-full w-[20%]" />
                </div>
                <p className="text-[11px] text-gray-400">Quota renews on October 28, 2026.</p>
              </div>

              <div className="flex justify-end gap-2">
                <Button variant="secondary" size="sm">
                  Change Plan
                </Button>
                <Button size="sm">
                  Manage Billing via Stripe
                </Button>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}
