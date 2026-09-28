# CertiFlow — Frontend Web Application & Visual Studio

[![Framework](https://img.shields.io/badge/Framework-Next.js%2015%20%2F%20React%2019-black.svg?style=flat-square)](https://nextjs.org/)
[![Styling](https://img.shields.io/badge/Styling-Tailwind%20CSS%20v4-blue.svg?style=flat-square)](https://tailwindcss.com/)
[![State](https://img.shields.io/badge/State-Zustand%20v5-purple.svg?style=flat-square)](https://github.com/pmndrs/zustand)
[![E2E Tests](https://img.shields.io/badge/Tests-Playwright%201.63-green.svg?style=flat-square)](https://playwright.dev/)

The frontend of CertiFlow is an enterprise web application and visual certificate design studio built with **Next.js 15 (App Router)**, **React 19**, **Tailwind CSS v4**, and **Zustand v5**.

---

## 1. Directory Structure

```text
src/
├── app/                         # Next.js App Router Pages & Layouts
│   ├── (marketing)/             # Public Marketing & Conversion Pages
│   │   ├── page.tsx             # Landing Page (Hero, Demo, FAQ, Pricing)
│   │   ├── features/page.tsx    # Technical Feature Deep-Dives
│   │   ├── templates/page.tsx   # Certificate Template Gallery
│   │   ├── pricing/page.tsx     # Tier Comparison & Interactive Pricing
│   │   ├── about/page.tsx       # Mission & Company Info
│   │   ├── security/page.tsx    # Cryptographic & Compliance Whitepaper
│   │   ├── resources/page.tsx   # Documentation & API Guides
│   │   ├── demo/page.tsx        # Interactive Product Demo
│   │   ├── contact/page.tsx     # Enterprise Sales Inquiry
│   │   ├── terms/page.tsx       # Terms of Service
│   │   └── privacy/page.tsx     # Privacy Policy
│   ├── (auth)/                  # Authentication Routes
│   │   ├── signup/page.tsx      # Multi-Tenant Organization Registration
│   │   ├── login/page.tsx       # Secure User Login
│   │   ├── forgot-password/     # Enumeration-Safe Reset Request
│   │   ├── reset-password/      # Token-Based Password Reset Execution
│   │   └── onboarding/page.tsx  # Initial Organization Setup Wizard
│   ├── app/                     # Authenticated SaaS Workspace
│   │   ├── page.tsx             # Operational Dashboard & Metrics
│   │   ├── projects/page.tsx    # Projects Directory
│   │   ├── projects/[id]/       # Step-by-Step Certificate Pipeline:
│   │   │   ├── page.tsx         # Project Overview & Stage Progress
│   │   │   ├── editor/page.tsx  # Visual Canvas Studio
│   │   │   ├── data/page.tsx    # CSV/Excel Ingest & Column Profiling
│   │   │   ├── mapping/page.tsx # Fuzzy Column-to-Placeholder Mapping
│   │   │   ├── preview/page.tsx # Live Dynamic Batch Preview
│   │   │   └── generate/page.tsx# Bulk Issuance & Worker Progress
│   │   ├── certificates/        # Certificate Registry & Lifecycle Management
│   │   └── settings/page.tsx    # Org, RBAC, API Keys, Webhooks & Billing
│   ├── verify/[id]/page.tsx     # Public Dual Verification Portal
│   ├── layout.tsx               # Root Layout with Font & Metadata Configuration
│   └── globals.css              # Tailwind CSS v4 Theme & Base Directives
├── components/                  # Component Library
│   ├── marketing/               # Landing Sections (Hero, Features, Pricing, etc.)
│   ├── navigation/              # Navbar, Announcement Bar, Footer
│   └── ui/                      # Base Atoms (Button, Input, Modal, Badge, Card, Tabs)
├── features/editor/             # Visual Studio Engine
│   ├── components/              # EditorCanvas, EditorLeftSidebar, EditorRightInspector, EditorTopBar
│   ├── use-editor-store.ts      # Central Zustand Store for Canvas State
│   ├── types.ts                 # Element, Canvas, Variable & Template Interfaces
│   └── sample-data.ts           # Demo Certificate Elements & Sample Data
└── lib/                         # Client Utilities & Algorithmic Engines
    ├── csv-engine.ts            # Client-Side CSV Sniffing & Ingest
    ├── field-matcher.ts         # 5-Tier Fuzzy Column Matching Algorithm
    ├── smart-fit.ts             # Dynamic Text Bounding Box Calculations
    ├── crypto-verification.ts   # Client-Side SHA-256 PDF Hash Calculator
    ├── motion.ts                # Animation Transitions & Framer Heuristics
    └── utils.ts                 # Tailwind Class Merging & Formatting Helpers
```

---

## 2. Key Frontend Features

### 2.1 Visual Certificate Studio (`/app/projects/[id]/editor`)
- **Interactive SVG Canvas**: Millimeter and pixel precision coordinate space with zoom, pan, grid snapping, and element layering (z-index).
- **Element Library**:
  - Text elements with dynamic placeholder bindings (`{{recipient_name}}`, `{{course_name}}`, `{{issue_date}}`).
  - Dynamic QR codes linked to the certificate's unique public verification URL.
  - Logos, badges, decorative shapes, signatures, and borders.
- **Smart-Fit Typography**: Dynamic font autosizing ensures names of any length stay within assigned boundaries without clipping or wrapping awkwardly.
- **Font Engine**: Supports system fonts and custom uploaded `.ttf`, `.otf`, `.woff`, `.woff2` font families with instant preview.
- **Inspector Panel**: Real-time property controls for position (X, Y), size (W, H), rotation, font weight, line-height, letter spacing, alignment, fill colors, border styles, opacity, and drop shadows.

### 2.2 Intelligent Data Ingestion (`/app/projects/[id]/data`)
- **Drag-and-Drop Ingestion**: Powered by `csv-engine.ts` with PapaParse.
- **Automatic Sniffing**: Detects delimiters (comma, semicolon, tab, pipe) and file encodings (UTF-8, Latin-1, Windows-1252).
- **Column Profiling**: Detects data types (email, date, string, numeric) and checks for empty values or duplicate rows before submission.

### 2.3 Smart Column-to-Placeholder Mapping (`/app/projects/[id]/mapping`)
- **5-Tier Fuzzy Matching Engine** (`field-matcher.ts`):
  1. Exact Match (`"recipient_name"` $\to$ `"recipient_name"`)
  2. Normalized Slug (`"Student-Name"` $\to$ `"recipient_name"`)
  3. Synonym Dictionary (`"Full Name"`, `"Learner"`, `"Attendee"` $\to$ `"recipient_name"`)
  4. Data Type Heuristics (matches email column to `{{recipient_email}}`)
  5. Fuzzy Levenshtein Distance scoring
- **Visual Confidence Indicators**: Displays High (90-100%), Medium (70-89%), and Low (<70%) confidence tags with dropdown manual overrides.

### 2.4 Live Dynamic Batch Preview (`/app/projects/[id]/preview`)
- **Recipient Carousel**: Step through imported rows to inspect real-time variable interpolation before running batch issuance.
- **Overflow Warnings**: Detects if any recipient's name or title exceeds designated canvas boundaries.

### 2.5 High-Throughput Bulk Generation (`/app/projects/[id]/generate`)
- **Real-Time Progress**: Polling progress counters displaying completed rows, processing rate (certs/min), and ETA.
- **Error Isolation**: Failed rows are flagged without blocking the rest of the batch.
- **Streaming ZIP Download**: One-click download of all rendered 300 DPI PDFs.

### 2.6 Public Dual Verification Portal (`/verify/[id]`)
- **Instant QR Scan**: Validates certificate authenticity via public API code.
- **SHA-256 PDF Drag-and-Drop**: Computes SHA-256 hash client-side in Web Crypto (`crypto-verification.ts`) and matches against the blockchain/immutable ledger digest.
- **Open Badges 3.0 & W3C Verifiable Credentials**: Recipient can view the JSON-LD credential and export to supported digital wallets.

---

## 3. Client State Architecture (`use-editor-store.ts`)

CertiFlow uses **Zustand v5** to manage canvas state with high performance and zero unnecessary re-renders:

```typescript
interface EditorState {
  elements: CanvasElement[];
  selectedElementId: string | null;
  canvasConfig: {
    width: number;
    height: number;
    unit: 'mm' | 'px';
    orientation: 'landscape' | 'portrait';
    backgroundColor: string;
  };
  history: {
    past: CanvasElement[][];
    future: CanvasElement[][];
  };
  
  // Actions
  addElement: (element: CanvasElement) => void;
  updateElement: (id: string, updates: Partial<CanvasElement>) => void;
  removeElement: (id: string) => void;
  selectElement: (id: string | null) => void;
  undo: () => void;
  redo: () => void;
}
```

---

## 4. Local Development & Scripts

### Prerequisites
- Node.js 18.18+ or 20+
- npm or pnpm

### Development Commands
```bash
# Install dependencies
npm install

# Start development server with Turbopack / Next dev
npm run dev

# Run TypeScript type check
npm run typecheck

# Run ESLint validation
npm run lint

# Build production bundle
npm run build

# Start production server
npm start

# Run Playwright End-to-End Test Suite
npm run test:e2e
```

---

## 5. Playwright E2E Testing Harness

The frontend test suite is located under [`tests/e2e/`](file:///e:/Certificate/tests/e2e/):

- `master-journey.spec.ts`: Tests complete end-to-end journey from landing $\to$ editor $\to$ CSV ingest $\to$ mapping $\to$ preview $\to$ generation $\to$ public verification.
- `editor-interactions.spec.ts`: Tests canvas drag-and-drop, selection, resizing, auto-fit text calculation, and undo/redo.
- `marketing.spec.ts`: Validates navigation, pricing calculator, responsive layout, and CTA interactions.
- `responsive-and-a11y.spec.ts`: Tests accessibility compliance, keyboard navigation, and mobile viewports.
- `security-and-sanitization.spec.ts`: Validates XSS protection, SVG sanitization, and client-side input validation.
