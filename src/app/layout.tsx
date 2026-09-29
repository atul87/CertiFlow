import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "CertiFlow — Automated Bulk Certificate Generation from Spreadsheets",
  description:
    "Turn a certificate template and a spreadsheet into hundreds of personalized certificates in minutes. Built for schools, hackathons, training bootcamps, and organizations with instant QR verification.",
  keywords: [
    "bulk certificate generator",
    "certificate generator from CSV",
    "automatic certificate generator",
    "bulk certificate creation",
    "certificate automation",
    "QR certificate verification",
    "credential management",
  ],
  authors: [{ name: "CertiFlow Team" }],
  openGraph: {
    title: "CertiFlow — Bulk Certificate Generation Platform",
    description:
      "Generate hundreds of personalized credentials in minutes from any CSV or Excel spreadsheet with QR verification.",
    type: "website",
  },
};

import { QueryProvider } from "@/lib/query";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      suppressHydrationWarning
      data-scroll-behavior="smooth"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased scroll-smooth`}
    >
      <body
        suppressHydrationWarning
        className="min-h-full flex flex-col font-sans bg-[var(--color-background)] text-[var(--color-text)]"
      >
        <QueryProvider>{children}</QueryProvider>
      </body>
    </html>
  );
}
