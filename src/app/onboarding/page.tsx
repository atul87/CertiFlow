"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  GraduationCap,
  Building,
  Trophy,
  BookOpen,
  Briefcase,
  Layers,
  Award,
  CheckCircle2,
  ArrowRight,
  ArrowLeft,
  Sparkles,
} from "lucide-react";
import { Button } from "@/components/ui/button";

const roles = [
  { id: "teacher", label: "Teacher / Educator", icon: GraduationCap, desc: "Classroom certificates & school rewards" },
  { id: "university", label: "College / University", icon: Building, desc: "Degrees, symposiums & formal diplomas" },
  { id: "event", label: "Event Organizer", icon: Trophy, desc: "Hackathons, conferences & summits" },
  { id: "training", label: "Training Provider", icon: BookOpen, desc: "Bootcamps, online courses & accreditations" },
  { id: "business", label: "Business / Enterprise", icon: Briefcase, desc: "Employee recognition & compliance" },
  { id: "other", label: "Other Organization", icon: Layers, desc: "Non-profit or custom issuance" },
];

const goals = [
  { id: "participation", label: "Participation Certificate", desc: "Recognize attendance & involvement" },
  { id: "achievement", label: "Achievement & Award", desc: "Honor top rankings, winners & distinctions" },
  { id: "completion", label: "Course Completion", desc: "Certify curriculum mastery with hours/scores" },
  { id: "workshop", label: "Workshop Credentials", desc: "Professional development & practical sessions" },
  { id: "custom", label: "Custom Credential", desc: "Build tailored layout from scratch" },
];

export default function OnboardingPage() {
  const router = useRouter();
  const [step, setStep] = useState<1 | 2 | 3>(1);
  const [selectedRole, setSelectedRole] = useState("university");
  const [selectedGoal, setSelectedGoal] = useState("completion");

  return (
    <div className="min-h-screen bg-[var(--color-background)] flex flex-col justify-between p-4 sm:p-8">
      {/* Top Brand Bar */}
      <header className="max-w-xl mx-auto w-full flex items-center justify-between pb-6">
        <Link href="/" className="flex items-center gap-2 group">
          <div className="w-8 h-8 rounded-lg bg-[var(--color-primary)] text-white flex items-center justify-center font-bold">
            <Sparkles className="w-4 h-4" />
          </div>
          <span className="text-[18px] font-bold text-[var(--color-text)]">
            CertiFlow
          </span>
        </Link>
        <span className="text-[12px] font-mono text-[var(--color-text-secondary)]">
          Step {step} of 3
        </span>
      </header>

      {/* Main Container */}
      <main className="max-w-xl mx-auto w-full bg-white rounded-2xl border border-[var(--color-border)] p-6 sm:p-10 shadow-sm my-auto">
        {/* Step 1: Role Selection */}
        {step === 1 && (
          <div className="space-y-6">
            <div>
              <span className="text-[12px] font-bold uppercase tracking-wider text-[var(--color-primary)]">
                Onboarding · Step 1
              </span>
              <h1 className="text-[24px] font-bold text-[var(--color-text)] mt-1">
                Welcome to CertiFlow 👋
              </h1>
              <p className="text-[14px] text-[var(--color-text-secondary)] mt-1">
                What best describes your role or organization?
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {roles.map((r) => {
                const Icon = r.icon;
                const isSelected = selectedRole === r.id;
                return (
                  <button
                    key={r.id}
                    type="button"
                    onClick={() => setSelectedRole(r.id)}
                    className={`
                      p-4 rounded-xl border text-left transition-all cursor-pointer select-none
                      ${
                        isSelected
                          ? "border-[var(--color-primary)] bg-[var(--color-primary-subtle)] ring-1 ring-[var(--color-primary)]"
                          : "border-[var(--color-border)] hover:border-[var(--color-border-hover)] bg-white"
                      }
                    `}
                  >
                    <Icon className={`w-5 h-5 mb-2 ${isSelected ? "text-[var(--color-primary)]" : "text-gray-500"}`} />
                    <p className="text-[14px] font-semibold text-[var(--color-text)]">{r.label}</p>
                    <p className="text-[12px] text-[var(--color-text-secondary)] mt-0.5">{r.desc}</p>
                  </button>
                );
              })}
            </div>

            <Button
              size="lg"
              className="w-full justify-center h-11 text-[15px]"
              onClick={() => setStep(2)}
            >
              Continue
              <ArrowRight className="w-4 h-4 ml-1.5" />
            </Button>
          </div>
        )}

        {/* Step 2: Goal Selection */}
        {step === 2 && (
          <div className="space-y-6">
            <div>
              <span className="text-[12px] font-bold uppercase tracking-wider text-[var(--color-primary)]">
                Onboarding · Step 2
              </span>
              <h1 className="text-[24px] font-bold text-[var(--color-text)] mt-1">
                What do you want to create?
              </h1>
              <p className="text-[14px] text-[var(--color-text-secondary)] mt-1">
                We will optimize the default fields and canvas layout for your workflow.
              </p>
            </div>

            <div className="space-y-2.5">
              {goals.map((g) => {
                const isSelected = selectedGoal === g.id;
                return (
                  <button
                    key={g.id}
                    type="button"
                    onClick={() => setSelectedGoal(g.id)}
                    className={`
                      w-full p-4 rounded-xl border text-left transition-all flex items-center justify-between cursor-pointer select-none
                      ${
                        isSelected
                          ? "border-[var(--color-primary)] bg-[var(--color-primary-subtle)] ring-1 ring-[var(--color-primary)]"
                          : "border-[var(--color-border)] hover:border-[var(--color-border-hover)] bg-white"
                      }
                    `}
                  >
                    <div>
                      <p className="text-[14px] font-semibold text-[var(--color-text)]">{g.label}</p>
                      <p className="text-[12px] text-[var(--color-text-secondary)] mt-0.5">{g.desc}</p>
                    </div>
                    <div className={`w-5 h-5 rounded-full border flex items-center justify-center ${isSelected ? "border-[var(--color-primary)] bg-[var(--color-primary)] text-white" : "border-gray-300"}`}>
                      {isSelected && <span className="text-[10px]">✓</span>}
                    </div>
                  </button>
                );
              })}
            </div>

            <div className="flex gap-3">
              <Button variant="secondary" size="lg" className="h-11" onClick={() => setStep(1)}>
                <ArrowLeft className="w-4 h-4 mr-1" />
                Back
              </Button>
              <Button size="lg" className="flex-1 justify-center h-11 text-[15px]" onClick={() => setStep(3)}>
                Continue
                <ArrowRight className="w-4 h-4 ml-1.5" />
              </Button>
            </div>
          </div>
        )}

        {/* Step 3: Ready */}
        {step === 3 && (
          <div className="space-y-6 text-center py-4">
            <div className="w-14 h-14 rounded-2xl bg-emerald-100 text-emerald-700 flex items-center justify-center mx-auto shadow-xs">
              <CheckCircle2 className="w-8 h-8" />
            </div>

            <div>
              <h1 className="text-[26px] font-bold text-[var(--color-text)]">
                You&apos;re ready.
              </h1>
              <p className="text-[14px] text-[var(--color-text-secondary)] mt-2 max-w-sm mx-auto">
                Your workspace is configured with template generators, dynamic variable mapping, and cryptographic QR signatures.
              </p>
            </div>

            <div className="p-4 rounded-xl bg-[var(--color-background)] border border-[var(--color-border)] text-left text-[13px] space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-500">Selected Profile:</span>
                <span className="font-semibold text-gray-800 capitalize">{selectedRole}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Target Credential:</span>
                <span className="font-semibold text-gray-800 capitalize">{selectedGoal}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Free Tier Quota:</span>
                <span className="font-semibold text-emerald-600">100 certificates / month</span>
              </div>
            </div>

            <Button
              size="lg"
              className="w-full justify-center h-12 text-[15px] shadow-md"
              onClick={() => router.push("/app")}
            >
              <Sparkles className="w-4 h-4 mr-1.5" />
              Create Your First Project
            </Button>
          </div>
        )}
      </main>

      <footer className="text-center text-[12px] text-[var(--color-text-tertiary)] pt-6">
        CertiFlow Onboarding · You can update these preferences anytime in Settings
      </footer>
    </div>
  );
}
