"use client";

import { GraduationCap, Ticket, BookOpen, Building2, Check, ArrowRight } from "lucide-react";
import Link from "next/link";

const useCases = [
  {
    title: "Education",
    tagline: "Schools & Universities",
    icon: GraduationCap,
    description: "Issue graduation degrees, seminar credentials, academic achievement awards, and competition prizes for entire student bodies in minutes.",
    examples: ["Graduation diplomas", "Workshop completion", "Academic excellence", "Seminar attendance"],
  },
  {
    title: "Events",
    tagline: "Hackathons & Conferences",
    icon: Ticket,
    description: "Instantly create badges and certificates for attendees, keynote speakers, prize winners, sponsors, and community volunteers.",
    examples: ["Participation certificates", "Hackathon podium awards", "Speaker recognition", "Volunteer credentials"],
  },
  {
    title: "Training",
    tagline: "Bootcamps & Academies",
    icon: BookOpen,
    description: "Issue course completion credentials containing unique scores, grades, and hours with automated email delivery to students upon graduation.",
    examples: ["Curriculum certification", "Assessment scores", "Skill accreditation", "Professional development"],
  },
  {
    title: "Organizations",
    tagline: "Enterprises & Non-Profits",
    icon: Building2,
    description: "Recognize employee milestones, quarterly achievements, compliance training, and onboarding with branded tamper-proof credentials.",
    examples: ["Employee recognition", "Compliance training", "Years of service", "Leadership awards"],
  },
];

export function UseCasesSection() {
  return (
    <section className="section-padding bg-white border-t border-[var(--color-border)]">
      <div className="container-marketing">
        {/* Section Header */}
        <div className="max-w-2xl mx-auto text-center mb-16">
          <p className="text-[13px] font-semibold uppercase tracking-[0.15em] text-[var(--color-primary)] mb-3">
            Tailored Solutions
          </p>
          <h2 className="text-section text-[var(--color-text)] mb-3">
            Built for your specific organization
          </h2>
          <p className="text-body-lg text-[var(--color-text-secondary)]">
            Scalable certificate infrastructure designed for educational, event, and enterprise workflows.
          </p>
        </div>

        {/* 4 Large Use Case Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-5xl mx-auto">
          {useCases.map((uc) => (
            <div
              key={uc.title}
              className="rounded-2xl border border-[var(--color-border)] bg-[#FAFAF8] p-8 hover:border-[var(--color-border-hover)] hover:shadow-xs transition-all flex flex-col justify-between"
            >
              <div>
                <div className="w-12 h-12 rounded-xl bg-white border border-[var(--color-border)] flex items-center justify-center text-[var(--color-primary)] shadow-2xs mb-6">
                  <uc.icon className="w-6 h-6" />
                </div>
                <span className="text-[12px] font-bold text-[var(--color-primary)] uppercase tracking-wider block mb-1">
                  {uc.tagline}
                </span>
                <h3 className="text-[22px] font-bold text-[var(--color-text)] mb-3">
                  {uc.title}
                </h3>
                <p className="text-[14px] text-[var(--color-text-secondary)] leading-relaxed mb-6">
                  {uc.description}
                </p>
              </div>

              <div className="pt-4 border-t border-[var(--color-border)]">
                <p className="text-[11px] font-bold uppercase tracking-wider text-gray-400 mb-2">Common Workflows</p>
                <div className="grid grid-cols-2 gap-2 text-[12px] text-gray-700">
                  {uc.examples.map((ex) => (
                    <span key={ex} className="flex items-center gap-1.5">
                      <span className="w-1 h-1 rounded-full bg-[var(--color-primary)]" />
                      {ex}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
