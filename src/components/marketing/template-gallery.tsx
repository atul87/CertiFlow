"use client";

import { useState } from "react";
import { Sparkles } from "lucide-react";
import Link from "next/link";

interface Template {
  id: string;
  title: string;
  category: string;
  accent: string;
  fields: string;
}

const templates: Template[] = [
  { id: "acad-01", title: "Academic Achievement", category: "Academic", accent: "#1E3A8A", fields: "Name, Degree, Honors, Date" },
  { id: "part-01", title: "Global Summit Participation", category: "Participation", accent: "#635BFF", fields: "Name, Event, Track, Date" },
  { id: "achieve-01", title: "First Place Winner Award", category: "Achievement", accent: "#059669", fields: "Team Name, Project, Award, Year" },
  { id: "work-01", title: "AI Workshop Completion", category: "Workshop", accent: "#D97706", fields: "Attendee, Hours, Instructor, ID" },
  { id: "hack-01", title: "Hackathon Finalist", category: "Hackathon", accent: "#7C3AED", fields: "Participant, Track, Place, Mentor" },
  { id: "train-01", title: "Full-Stack Bootcamp", category: "Training", accent: "#2563EB", fields: "Student, Grade, Modules, Date" },
  { id: "conf-01", title: "Keynote Speaker Recognition", category: "Conference", accent: "#DC2626", fields: "Speaker, Topic, Conference, Year" },
  { id: "corp-01", title: "Leadership Excellence", category: "Corporate", accent: "#4B5563", fields: "Employee, Department, Recognition" },
];

const categories = [
  "All",
  "Academic",
  "Participation",
  "Achievement",
  "Workshop",
  "Hackathon",
  "Training",
  "Conference",
  "Corporate",
];

export function TemplateGallery() {
  const [activeCategory, setActiveCategory] = useState("All");

  const filtered = activeCategory === "All"
    ? templates
    : templates.filter((t) => t.category === activeCategory);

  return (
    <section className="section-padding bg-[#FAFAF8] border-t border-[var(--color-border)]">
      <div className="container-marketing">
        {/* Section Header */}
        <div className="max-w-2xl mx-auto text-center mb-12">
          <p className="text-[13px] font-semibold uppercase tracking-[0.15em] text-[var(--color-primary)] mb-3">
            Template Library
          </p>
          <h2 className="text-section text-[var(--color-text)] mb-3">
            Start with a template. Make it yours.
          </h2>
          <p className="text-body-lg text-[var(--color-text-secondary)]">
            High-DPI print-ready templates designed by typography experts. Fully customizable in studio.
          </p>

          {/* Filter Pills */}
          <div className="flex flex-wrap items-center justify-center gap-1.5 mt-8">
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => setActiveCategory(cat)}
                className={`px-3.5 py-1.5 rounded-full text-[13px] font-medium transition-all ${
                  activeCategory === cat
                    ? "bg-[var(--color-text)] text-white shadow-xs"
                    : "bg-white text-[var(--color-text-secondary)] border border-[var(--color-border)] hover:bg-gray-50"
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>

        {/* 4 Cards per row on desktop, 2 on tablet */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 max-w-6xl mx-auto">
          {filtered.map((tmpl) => (
            <div
              key={tmpl.id}
              className="group rounded-2xl border border-[var(--color-border)] bg-white overflow-hidden shadow-2xs hover:shadow-md hover:border-[var(--color-border-hover)] transition-all flex flex-col justify-between"
            >
              {/* Card visual preview */}
              <div className="p-5 bg-gray-50/70 border-b border-[var(--color-border)] flex items-center justify-center min-h-[170px] relative">
                <div
                  className="w-full aspect-[1.4/1] bg-white rounded-lg border shadow-xs p-4 flex flex-col justify-between text-center relative"
                  style={{ borderColor: tmpl.accent }}
                >
                  <p className="text-[7px] uppercase font-bold tracking-widest text-gray-400">Certificate</p>
                  <p className="text-[11px] font-bold font-serif text-[var(--color-text)]">
                    {"{{RECIPIENT_NAME}}"}
                  </p>
                  <div className="flex items-center justify-between text-[7px] text-gray-400 border-t border-gray-100 pt-1">
                    <span>2026-09-27</span>
                    <div className="w-3.5 h-3.5 border flex items-center justify-center font-mono text-[5px]">QR</div>
                    <span>#CERT-01</span>
                  </div>
                </div>

                {/* Hover overlay with use button */}
                <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2 backdrop-blur-[1px]">
                  <Link
                    href="/signup"
                    className="px-3.5 py-1.5 rounded-lg bg-[var(--color-primary)] text-white text-[12px] font-medium shadow-md hover:bg-[var(--color-primary-hover)] transition-colors flex items-center gap-1.5"
                  >
                    <Sparkles className="w-3.5 h-3.5" />
                    Use Template
                  </Link>
                </div>
              </div>

              {/* Card metadata */}
              <div className="p-4">
                <span className="text-[11px] font-semibold text-[var(--color-primary)] uppercase tracking-wider block mb-1">
                  {tmpl.category}
                </span>
                <h4 className="text-[15px] font-bold text-[var(--color-text)] mb-2">
                  {tmpl.title}
                </h4>
                <p className="text-[11px] text-gray-500 font-mono">
                  Fields: {tmpl.fields}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
