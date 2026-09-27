"use client";

import { useState } from "react";
import { Plus, Minus } from "lucide-react";

interface FAQItem {
  question: string;
  answer: string;
}

const faqs: FAQItem[] = [
  {
    question: "How does bulk generation work?",
    answer: "Upload a certificate template and your recipient data spreadsheet. Map your spreadsheet columns to typography fields and generate the complete batch in under 2 minutes.",
  },
  {
    question: "Can I upload my own design?",
    answer: "Yes. You can upload custom certificate designs created in Figma, Canva, Illustrator, or Photoshop as high-resolution PDF, PNG, or JPG files.",
  },
  {
    question: "Can I use Excel?",
    answer: "Yes. CertiFlow supports Microsoft Excel spreadsheets (.xlsx, .xls) as well as standard comma-separated (.csv) files.",
  },
  {
    question: "Can I generate PDFs?",
    answer: "Yes. All exported certificates can be generated as crisp, print-ready 300 DPI vector PDFs or high-definition PNG images.",
  },
  {
    question: "Can I add QR codes?",
    answer: "Yes. CertiFlow automatically creates an encrypted, tamper-proof QR code for each recipient that redirects to a public verification page.",
  },
  {
    question: "Can I send certificates by email?",
    answer: "Yes. Pro and Organization plans allow you to send personalized emails with attached PDF certificates directly to all attendees in a single click.",
  },
  {
    question: "Is my data private?",
    answer: "Yes. Your participant spreadsheets and recipient lists are processed securely. We never sell, share, or broker your attendee data.",
  },
  {
    question: "Can I use this for my college?",
    answer: "Yes. Hundreds of schools, universities, hackathons, and training bootcamps use CertiFlow to issue certificates for thousands of students each semester.",
  },
];

export function FAQSection() {
  const [openIndex, setOpenIndex] = useState<number | null>(0);

  const toggle = (idx: number) => {
    setOpenIndex(openIndex === idx ? null : idx);
  };

  return (
    <section className="section-padding bg-[#FAFAF8] border-t border-[var(--color-border)]">
      <div className="container-marketing">
        {/* Section Header */}
        <div className="max-w-2xl mx-auto text-center mb-16">
          <p className="text-[13px] font-semibold uppercase tracking-[0.15em] text-[var(--color-primary)] mb-3">
            Got Questions?
          </p>
          <h2 className="text-section text-[var(--color-text)] mb-3">
            Frequently Asked Questions
          </h2>
          <p className="text-body-lg text-[var(--color-text-secondary)]">
            Everything you need to know about bulk certificate automation.
          </p>
        </div>

        {/* FAQ Accordion List */}
        <div className="max-w-3xl mx-auto space-y-3">
          {faqs.map((faq, i) => {
            const isOpen = openIndex === i;
            return (
              <div
                key={faq.question}
                className="rounded-xl border border-[var(--color-border)] bg-white overflow-hidden transition-colors"
              >
                <button
                  onClick={() => toggle(i)}
                  className="w-full text-left px-6 py-4.5 flex items-center justify-between gap-4 font-semibold text-[15px] text-[var(--color-text)] hover:text-[var(--color-primary)] transition-colors select-none"
                  aria-expanded={isOpen}
                >
                  <span>{faq.question}</span>
                  <div className="w-5 h-5 rounded flex items-center justify-center text-gray-400 shrink-0">
                    {isOpen ? <Minus className="w-4 h-4 text-[var(--color-primary)]" /> : <Plus className="w-4 h-4" />}
                  </div>
                </button>

                {isOpen && (
                  <div className="px-6 pb-5 pt-1 text-[14px] text-[var(--color-text-secondary)] leading-relaxed border-t border-[var(--color-border)]/60 bg-[#FAFAF8]/50">
                    {faq.answer}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
