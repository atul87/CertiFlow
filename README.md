# CertiFlow — Enterprise Portable Digital Credential & Certificate SaaS Platform

[![Tests Passing](https://img.shields.io/badge/Tests-440%2B%20Passed-brightgreen.svg?style=flat-square)](file:///e:/Certificate/PRODUCT_COMPLETION_STATUS.md)
[![Production Ready](https://img.shields.io/badge/Status-1.0.0--PROD%20Verified-success.svg?style=flat-square)](file:///e:/Certificate/DEPLOYMENT.md)
[![TypeScript](https://img.shields.io/badge/TypeScript-0%20Errors-blue.svg?style=flat-square)](https://www.typescriptlang.org/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI%200.115-blue.svg?style=flat-square)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Frontend-Next.js%2016%20Turbopack-black.svg?style=flat-square)](https://nextjs.org)
[![MongoDB](https://img.shields.io/badge/Database-MongoDB%207.0%2B-green.svg?style=flat-square)](https://www.mongodb.com)
[![Redis ARQ](https://img.shields.io/badge/Workers-Redis%207%20%2B%20ARQ-red.svg?style=flat-square)](https://arq-docs.helpmanual.io)
[![Standards](https://img.shields.io/badge/Standards-W3C%20VC%20v2.0%20%7C%20Open%20Badges%203.0-purple.svg?style=flat-square)](https://www.w3.org/TR/vc-data-model-2.0/)
[![License](https://img.shields.io/badge/License-Proprietary-orange.svg?style=flat-square)](#12-license--enterprise-support)

> **Transforming Certificate Issuance into a Decentralized, Cryptographically Verifiable, and Standards-Compliant Digital Credential Ecosystem.**

CertiFlow is a commercial multi-tenant SaaS platform built to design, issue, verify, and distribute high-fidelity physical certificates and portable digital credentials. It seamlessly bridges print-ready high-resolution documents with modern decentralized identity standards, adhering to **W3C Verifiable Credentials Data Model v2.0** and **1EdTech Open Badges 3.0**.

---

## Enterprise Documentation Suite

CertiFlow features an exhaustive, production-grade documentation suite located in the [`docs/`](file:///e:/Certificate/docs/) directory and repository root:

| Document | Description | Target Audience |
| :--- | :--- | :--- |
| [**Production Deployment Handbook**](file:///e:/Certificate/DEPLOYMENT.md) | Single-host Docker Compose, cloud scaling (Vercel, Fly.io, AWS ECS), reverse proxy, SSL, and disaster recovery. | DevOps, SysAdmins, SREs |
| [**Architecture & System Design**](file:///e:/Certificate/docs/ARCHITECTURE.md) | Client/Server separation of authority, data pipelines, state machines, and threat model. | Architects, Tech Leads, Security Teams |
| [**Unified API Reference**](file:///e:/Certificate/docs/API_REFERENCE.md) | Full specification across all 18 REST routers, standard `APIResponse[T]` envelope, and error codes. | Backend Developers, Integrators |
| [**Developer & Contributor Guide**](file:///e:/Certificate/docs/DEVELOPER_GUIDE.md) | Local setup (Windows/Linux), environment catalog, test execution commands, and Docker composition. | All Engineers & Contributors |
| [**Standards & Cryptography Spec**](file:///e:/Certificate/docs/STANDARDS_COMPLIANCE.md) | W3C VC v2.0, Open Badges 3.0, Ed25519 signing, RFC 8785 canonicalization, and SHA-256 sealing. | Cryptographers, Standards Auditors |
| [**Product & Operator Handbook**](file:///e:/Certificate/docs/USER_AND_PRODUCT_MANUAL.md) | End-to-end user manual: canvas editor, CSV ingestion, fuzzy mapping, bulk issuance, and verification. | Registrars, Operations, L&D Admins |
| [**Product Completion Audit**](file:///e:/Certificate/PRODUCT_COMPLETION_STATUS.md) | Comprehensive 100% completion verification audit, 440+ passing tests, and verification logs. | Engineering Leadership, Stakeholders |

---

## 1. Problem Space & Industry Challenges

Legacy certificate generation systems suffer from five fundamental architectural failures:
2. **Platform Lock-In**: Verification links depend completely on the issuing vendor staying online forever. If the vendor shuts down, the certificate link breaks.
3. **Lack of Machine Readability**: Legacy certificates cannot be imported into digital credential wallets (Apple Wallet, Google Wallet, Learner Wallets) or queried programmatically by recruitment and HR systems.
4. **Manual Bulk Chaos**: Issuing certificates to thousands of graduates or attendees via spreadsheets usually leads to broken layouts, overflowing names, encoding glitches, and tedious manual error fixing.
5. **Privacy Vulnerabilities**: Public verification pages frequently leak sensitive student emails, phone numbers, or internal database IDs.

### The CertiFlow Dual-Layer Architecture

CertiFlow solves these challenges by combining human-readable visual presentation with decentralized cryptographic proofs:

```text
                                  CertiFlow SaaS
                                        │
             ┌──────────────────────────┴──────────────────────────┐
             │                                                     │
             ▼                                                     ▼
      PDF Certificate                                      Digital Credential
      (Human-Readable)                                    (Machine-Readable)
             │                                                     │
             ├── P1  Template Canvas Engine                        ├── P11.2 Issuer Profiles
             ├── P2  CSV / Excel Intelligent Ingest                ├── P11.3 Achievement Models
             ├── P3  High-DPI PDF & PNG Renderer                   ├── P11.6 Open Badges 3.0
             ├── P4  Distributed ARQ Background Workers            ├── P11.7 W3C Verifiable Credentials
             ├── P5  Instant QR Verification & SHA-256             ├── P11.8 Ed25519 Cryptographic Signatures
             ├── P6  Transactional Email & Notifications           ├── P11.10 Real-Time Status Registry
             ├── P7  Analytics Dashboard & Aggregation             ├── P11.13 Public Verification & Privacy
             ├── P8  Teams, RBAC, API Keys & Webhooks              └── P11.16 Wallet Integration & Sharing
             ├── P9  Security Hardening & Rate Limiting
             └── P10 Multi-Tenant Billing & Usage Metering
```

- **Layer 1: Human-Readable Presentation (PDF & Web)**
  High-resolution (300 DPI) print-ready documents with precision typography, dynamic QR codes, and tamper-evident SHA-256 file fingerprints.
- **Layer 2: Machine-Readable Cryptographic Proof (Digital Credentials)**
  Portable JSON-LD credentials signed with **Ed25519** asymmetric keys, normalized using **RFC 8785** deterministic canonicalization, verifiable offline by third-party systems without contacting the issuer's private database.

---

## 2. Key Target Personas & Use Cases

| Target Persona | Key Pain Point | How CertiFlow Solves It |
| --- | --- | --- |
| **Universities & Colleges** | Transcript & degree forgery; accreditation compliance | Issues tamper-proof 300 DPI diplomas paired with W3C Verifiable Credentials that employers can instantly verify cryptographically. |
| **EdTech Platforms & Bootcamps** | Issuing thousands of certificates per cohort reliably | Automated CSV/Excel batch processing with intelligent column mapping, auto-fit typography, and bulk streaming ZIP exports. |
| **Professional Licensing Bodies** | Credential expiration, suspension, and license revocation | Real-time status registry synchronized across PDF QR verification and W3C VC status lists with instant cache invalidation. |
| **Enterprise L&D & HR** | Tracking internal compliance training and skill badges | Multi-tenant team management, granular RBAC (35+ permissions), scoped API keys (`ck_live_...`), and outbound HMAC webhooks. |
| **Hackathons & Conferences** | Rapid turnaround of attendee and winner certificates | One-click batch generation with instant email distribution featuring 7-day secure HMAC download tokens. |

---

## 3. Technology Stack

### Frontend Web Application

- **Framework**: [Next.js 15+](https://nextjs.org/) (App Router, Server & Client Components)
- **Runtime & UI**: [React 19](https://react.dev/), [Tailwind CSS v4](https://tailwindcss.com/)
- **Icons & Animation**: [Lucide React](https://lucide.dev/), [Motion](https://motion.dev/)
- **State Management**: [Zustand v5](https://github.com/pmndrs/zustand)
- **Forms & Validation**: [React Hook Form](https://react-hook-form.com/), [Zod](https://zod.dev/)
- **Client Processing**: [PapaParse](https://www.papaparse.com/) (browser CSV ingestion), HTML5 Canvas/SVG geometry engine
- **Testing**: [Playwright](https://playwright.dev/) for cross-browser end-to-end integration and accessibility suites

### Backend Microservice

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.13, ASGI, Uvicorn worker pool)
- **Database**: [MongoDB 7.0+](https://www.mongodb.com/) via [Motor](https://motor.readthedocs.io/) async driver (50+ compound & unique indexes)
- **Task Queue & Caching**: [Redis 7.0+](https://redis.io/) with [ARQ](https://arq-docs.helpmanual.io/) (Async Redis Queue)
- **Cryptography & Security**: `cryptography` (Ed25519 asymmetric keys, Fernet key encryption at rest), Argon2id (`argon2-cffi`), PyJWT, HMAC-SHA256
- **Standards Serializers**: RFC 8785 JSON Canonicalization, 1EdTech Open Badges 3.0, W3C Verifiable Credentials v2.0 (`Ed25519Signature2020`)
- **Document & PDF Engine**: Playwright, ReportLab, CairoSVG, Pillow, PyMuPDF, QRCodegen (Exact 300 DPI vector output)
- **Data Ingestion**: Streaming CSV parser with encoding and delimiter sniffing, OpenPyXL for Excel `.xlsx`
- **Email Delivery**: Pluggable provider adapters (SMTP with STARTTLS, SendGrid, Amazon SES, Mock) with Jinja2 templating
- **Billing & Subscriptions**: Stripe Checkout integration, inbound webhook pipeline with replay protection, multi-tier usage metering
- **Testing**: `pytest` + `pytest-asyncio` + `pytest-cov` + `httpx` + `playwright` (**375 automated tests passing: 247 Backend Pytest, 114 Full Playwright E2E, 14 Dedicated Auth E2E, 0 TypeScript errors**)

---

## 4. Full Phase-by-Phase Architecture (P0 to P11)

### **Phase 0 — Core Architecture, Multi-Tenant Authentication & Foundation**

- **Async API Lifespan**: FastAPI application factory with async database connection pooling and graceful shutdown.
- **Argon2id Password Security**: Modern password hashing resistant to GPU, FPGA, and ASIC brute-force attacks.
- **JWT & Session Management**: 15-minute access tokens paired with 7-day rotated refresh tokens stored as SHA-256 hashes in MongoDB.
- **Standardized API Envelope**: Unified `APIResponse[T]` schema with correlation request IDs (`req_...`) for tracing and structured error payloads.
- **Security Headers**: Strict Content-Security-Policy (CSP), `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, and HTTP Strict Transport Security (HSTS).

### **Phase 1 — Visual Template Studio, Immutability & Custom Font Engine**

- **Canvas Geometry**: Millimeter and pixel precision coordinate engine supporting custom width, height, and orientations (Landscape/Portrait).
- **Element Hierarchy**: Text elements with dynamic `{{placeholder}}` variables, dynamic QR codes, logos, decorative shapes, and barcodes.
- **Semantic Versioning & Immutability**: Templates follow semantic versioning (`v1`, `v2`, ...). Publishing a template version locks it as strictly immutable, guaranteeing historical certificate reproducibility.
- **Custom Font Registry**: Secure upload and auto-registration of `.ttf`, `.otf`, `.woff`, and `.woff2` font files with CSS `@font-face` generation and vector embedding.

### **Phase 2 — CSV/Excel Data Ingest & Intelligent Profiling**

- **Smart Delimiter & Encoding Sniffer**: Streaming ingestion supporting files with unknown encodings (UTF-8, Latin-1, CP1252) and delimiters (comma, semicolon, tab, pipe). Automatically rejects macro-enabled `.xlsm` files to prevent CVE exploits.
- **5-Tier Field Matching Algorithm**: Combines Exact Match $\to$ Normalized Slug $\to$ Synonym Dictionary (`"Full Name"` $\to$ `"recipient_name"`) $\to$ Data Type Heuristics $\to$ Fuzzy Levenshtein Distance with confidence scoring.
- **Row-Level Pre-Flight Validation**: Validates email syntax, date formats (ISO YYYY-MM-DD), required fields, and duplicate entries. Generates downloadable `errors.csv` reports.

### **Phase 3 — High-DPI PDF Rendering & Preview Engine**

- **300 DPI Print-Ready Vector Output**: Generates print-ready vector PDFs using ReportLab/CairoSVG with embedded font subsets and true CMYK/RGB color representation.
- **Smart-Fit Typography**: Dynamically calculates text bounding boxes and reduces font size for extra-long recipient names, preventing overflow or awkward line breaks.
- **Deterministic Sequence Generator**: Atomic sequence counter producing customizable certificate numbers (e.g. `CERT-2026-00042`).
- **Cryptographic Fingerprint**: SHA-256 digest calculated at render time and recorded for physical file tamper verification.

### **Phase 4 — Distributed Bulk Issuance & Worker Queue**

- **ARQ Worker Pool**: Redis-backed async workers processing batch jobs with chunked execution, atomic item claiming (`findOneAndUpdate`), and failure retry heuristics.
- **Real-Time Progress Tracking**: Redis atomic counters track completed rows, processing speed (certificates/minute), and elapsed time.
- **In-Memory Streaming ZIP Export**: On-the-fly streaming ZIP archive builder enabling instantaneous download of thousands of generated certificates without disk bottlenecks.

### **Phase 5 — QR Verification, Trust Lifecycle & Anti-Tamper Engine**

- **Dynamic QR Codes**: Every certificate embeds a scannable QR code pointing directly to its public verification URL.
- **Physical File Verification**: Public file upload allows anyone to upload a PDF and verify its SHA-256 hash against the immutable ledger record.
- **Lifecycle State Machine**: Formal state management (`active` $\to$ `suspended` $\to$ `revoked` $\to$ `restored`) with mandatory audit rationale.
- **Privacy-by-Default**: Public verification pages display recipient names and course achievements while strictly concealing email addresses, phone numbers, and database IDs.

### **Phase 6 — Transactional Email Delivery & Certificate Distribution**

- **Pluggable Email Adapters**: Integrated SMTP (with STARTTLS), SendGrid, Amazon SES, and Mock provider drivers.
- **Jinja2 HTML Templates**: Customizable transactional email templates supporting dynamic variables (`{{recipient_name}}`, `{{download_url}}`, `{{verification_code}}`).
- **HMAC-SHA256 Signed URLs**: Time-limited (7-day) signed download tokens allowing recipients 1-click certificate retrieval without login barriers.
- **Automated Bounce Suppression**: Inbound provider webhook receiver that automatically registers hard bounces and spam complaints to protect sender domain reputation.

### **Phase 7 — SaaS Dashboard, Telemetry & Analytics**

- **Telemetry Aggregation**: Scheduled background workers roll up daily issuance volumes, verification scans, delivery rates, and device categories.
- **Time-Series Charts**: 7, 30, and 90-day trend lines for operational intelligence.
- **Audit Activity Feed**: Comprehensive chronological audit trail of all administrative and system operations.
- **Automated Reports**: Background generation of downloadable CSV and ReportLab PDF analytics reports.

### **Phase 8 — Multi-Tenant Teams, RBAC & Developer APIs**

- **Strict Tenant Scoping**: Every database query is strictly filtered by `organization_id` to prevent cross-tenant data leaks.
- **Granular RBAC**: 35+ granular permissions with standard system roles (`owner`, `admin`, `member`, `viewer`) and custom organization roles.
- **Developer API Keys**: High-entropy keys prefixed with `ck_live_...` with custom scope restrictions and SHA-256 hash storage.
- **Outbound Webhooks**: Event-driven HTTP notifications signed with HMAC-SHA256 (`X-Webhook-Signature`) with SSRF private IP blocking and exponential backoff retry.

### **Phase 9 — Security Hardening, SSRF Defense & Production Reliability**

- **Sliding-Window Rate Limiting**: Redis-backed rate limiters protecting authentication, public verification, and developer API routes.
- **SSRF Defense Engine**: Deep IP resolution validator blocking requests to private networks (RFC 1918), loopback (`127.0.0.1`), link-local, and cloud metadata IPs (`169.254.169.254`).
- **Input Sanitization**: Magic byte validation for uploads, SVG sanitization stripping `<script>` and `<!ENTITY>` to block XXE attacks, and NoSQL query sanitization.
- **Observability**: Process liveness probe (`/health`), multi-dependency readiness probe (`/health/ready`), and native Prometheus exporter (`/metrics`).

### **Phase 10 — SaaS Subscriptions, Metering & Billing**

- **Subscription Tiers**: `Community (Free)`, `Starter`, `Professional`, `Business`, and `Enterprise` with feature matrices and 14-day trials.
- **Entitlement & Quota Engine**: Hard-quota and soft-quota enforcement before executing operations.
- **Atomic Monthly Metering**: MongoDB `$inc` counters tracking `certificates_generated`, `credentials_issued`, `emails_sent`, and `storage_bytes`.
- **Stripe Billing Pipeline**: Stripe Checkout sessions and inbound webhook processing with signature verification and replay protection.

### **Phase 11 — Open Badges 3.0 & W3C Verifiable Credentials**

- **Decoupled Identity Models**:
  - `issuer_profiles`: Public resolution, stable URLs, and key discovery endpoints.
  - `achievements`: Decoupled achievement definitions with skills, categories, and criteria.
  - `credentials`: Independent credential entities with opaque identifiers (`cred_...`).
  - `credential_status`: Real-time status registry for instant revocation checks.
- **Ed25519 Cryptography**: Asymmetric signatures with private keys encrypted at rest using Fernet (`settings.ENCRYPTION_KEY`).
- **RFC 8785 Canonicalization**: Deterministic JSON normalization for cross-platform signature verification.
- **Dual Representation**:
  - Open Badges 3.0: `GET /api/v1/public/credentials/{id}/badge`
  - W3C VC v2.0: `GET /api/v1/public/credentials/{id}/vc`
- **Synchronized Revocation**: Revoking a certificate automatically synchronizes revocation to the digital credential and dedicated status registry.
- **Independent Verifier**: Public verifier endpoint (`POST /api/v1/public/credentials/verify`) cryptographically validates external W3C VC payloads without requiring internal database records.

---

## 5. Frontend Application Experience & Pages Directory

CertiFlow includes a complete web application built with Next.js 15, React 19, Tailwind CSS v4, and Zustand.

```text
src/
├── app/
│   ├── (marketing)/             # Public Landing & Product Showcase
│   │   ├── page.tsx             # Main Landing Page (Hero, Demo, Pricing, FAQ)
│   │   ├── features/page.tsx    # In-depth Feature Breakdown
│   │   ├── templates/page.tsx   # Curated Template Showcase
│   │   ├── pricing/page.tsx     # Tier Comparison & Interactive Pricing
│   │   ├── about/page.tsx       # Mission & Company Info
│   │   ├── security/page.tsx    # Cryptographic & Security Whitepaper
│   │   ├── resources/page.tsx   # Documentation & Guides
│   │   ├── demo/page.tsx        # Interactive Product Demo
│   │   ├── contact/page.tsx     # Contact & Enterprise Inquiry
│   │   ├── terms/page.tsx       # Terms of Service
│   │   └── privacy/page.tsx     # Privacy Policy
│   ├── (auth)/                  # Authentication Flows
│   │   ├── signup/page.tsx      # Organization Registration
│   │   ├── login/page.tsx       # User Login & JWT Session Creation
│   │   ├── forgot-password/     # Password Reset Request (Enumeration-Safe)
│   │   ├── reset-password/      # Password Reset Execution (Token-Based)
│   │   └── onboarding/page.tsx  # Initial Organization Setup Wizard
│   ├── app/                     # Authenticated SaaS Dashboard
│   │   ├── page.tsx             # Operational Overview & KPI Summary
│   │   ├── projects/page.tsx    # Certificate Projects Directory
│   │   ├── projects/[id]/       # Project Pipeline Steps:
│   │   │   ├── editor/page.tsx  # Visual Canvas Studio
│   │   │   ├── data/page.tsx    # CSV/Excel Ingest & Profiling
│   │   │   ├── mapping/page.tsx # Column-to-Placeholder Mapping
│   │   │   ├── preview/page.tsx # Live Dynamic Batch Preview
│   │   │   └── generate/page.tsx# Bulk Issuance & Worker Progress
│   │   ├── certificates/        # Certificate Registry & Lifecycle Management
│   │   └── settings/page.tsx    # Organization, RBAC, API Keys, Webhooks & Billing
│   └── verify/[id]/page.tsx     # Public Dual Verification Portal
├── components/                  # Reusable UI & Marketing Components
│   ├── marketing/               # Hero, Before/After, FAQ, Pricing, Demo Modal
│   ├── navigation/              # Responsive Navbar, Announcement Bar, Footer
│   └── ui/                      # Button, Input, Modal, Badge, Card, Tabs
├── features/editor/             # Visual Studio Engine
│   ├── components/              # Canvas, Left Sidebar, Right Inspector, Top Bar
│   ├── use-editor-store.ts      # Zustand Central Canvas State Store
│   └── types.ts                 # Element, Canvas & Template Type Definitions
└── lib/                         # Client Utilities
    ├── csv-engine.ts            # Client-Side CSV Sniffing & Ingest
    ├── field-matcher.ts         # Fuzzy Field Matching Heuristics
    ├── smart-fit.ts             # Dynamic Text Bounding Box Calculations
    └── crypto-verification.ts   # SHA-256 PDF Checksum Calculator
```

---

## 6. Master REST API Directory

CertiFlow exposes 60+ modular REST API endpoints under `/api/v1/`:

### Authentication & Organization (P0 & P8)

| Method | Endpoint | Description | Auth Level |
| --- | --- | --- | --- |
| `POST` | `/api/v1/auth/register` | Register new organization & owner account | Public |
| `POST` | `/api/v1/auth/login` | Authenticate and obtain JWT access & refresh tokens | Public |
| `POST` | `/api/v1/auth/refresh` | Rotate refresh token and obtain fresh access token | Public |
| `POST` | `/api/v1/auth/logout` | Revoke active refresh token session | Bearer JWT |
| `POST` | `/api/v1/auth/forgot-password` | Request password reset token | Public |
| `POST` | `/api/v1/auth/reset-password` | Reset password using single-use token | Public |
| `GET` | `/api/v1/auth/me` | Retrieve authenticated user profile | Bearer JWT |
| `GET` | `/api/v1/organizations/me` | Retrieve current organization details | Bearer JWT |
| `PATCH` | `/api/v1/organizations/me` | Update organization profile & branding | Admin / Owner |

### Templates & Fonts (P1)

| Method | Endpoint | Description | Auth Level |
| --- | --- | --- | --- |
| `POST` | `/api/v1/templates` | Create certificate template | `templates.create` |
| `GET` | `/api/v1/templates` | List organization templates with pagination & search | `templates.read` |
| `GET` | `/api/v1/templates/{id}` | Retrieve template details and active version | `templates.read` |
| `POST` | `/api/v1/templates/{id}/versions` | Create new draft version of template | `templates.create` |
| `POST` | `/api/v1/templates/{id}/versions/{v_id}/publish` | Publish version (locks version as immutable) | `templates.create` |
| `POST` | `/api/v1/templates/{id}/duplicate` | Clone template design into new draft | `templates.create` |
| `POST` | `/api/v1/fonts/upload` | Upload custom TrueType/OpenType/WOFF font | `templates.create` |
| `GET` | `/api/v1/fonts` | List registered custom and system fonts | `templates.read` |

### Data Ingest & Profiling (P2)

| Method | Endpoint | Description | Auth Level |
| --- | --- | --- | --- |
| `POST` | `/api/v1/imports/upload` | Upload CSV or Excel spreadsheet for profiling | `imports.create` |
| `GET` | `/api/v1/imports/{id}` | Inspect detected columns, sample rows, and validation status | `imports.read` |
| `POST` | `/api/v1/imports/{id}/map` | Confirm column-to-template field mappings | `imports.create` |
| `GET` | `/api/v1/imports/{id}/errors/csv` | Download actionable CSV of rejected rows | `imports.read` |

### Certificate Generation & Lifecycle (P3 & P5)

| Method | Endpoint | Description | Auth Level |
| --- | --- | --- | --- |
| `POST` | `/api/v1/certificates/preview` | Render fast base64 PNG preview thumbnail | `certificates.create` |
| `POST` | `/api/v1/certificates/generate` | Officially render single high-DPI PDF certificate | `certificates.create` |
| `GET` | `/api/v1/certificates` | List organization generated certificates | `certificates.read` |
| `GET` | `/api/v1/certificates/{id}` | Retrieve certificate metadata and file references | `certificates.read` |
| `GET` | `/api/v1/certificates/{id}/pdf` | Secure binary stream download of certificate PDF | `certificates.read` |
| `POST` | `/api/v1/certificates/{id}/revoke` | Revoke certificate and sync digital credential status | `certificates.revoke` |
| `POST` | `/api/v1/certificates/{id}/restore` | Restore previously revoked certificate | `certificates.revoke` |
| `GET` | `/api/v1/certificates/{id}/integrity` | Internal SHA-256 physical storage integrity check | `certificates.read` |
| `GET` | `/api/v1/public/verify/{code}` | Public QR verification endpoint (privacy-safe) | Public |
| `POST` | `/api/v1/public/verify/file` | Public physical PDF checksum integrity verification | Public |

### Bulk Queue Issuance (P4)

| Method | Endpoint | Description | Auth Level |
| --- | --- | --- | --- |
| `POST` | `/api/v1/issuance-jobs` | Queue bulk issuance job from validated import | `certificates.create` |
| `GET` | `/api/v1/issuance-jobs/{id}` | Inspect real-time progress, processed counts, and errors | `certificates.read` |
| `POST` | `/api/v1/issuance-jobs/{id}/cancel` | Halt running issuance job | `certificates.create` |
| `GET` | `/api/v1/issuance-jobs/{id}/export/zip` | Download streaming ZIP archive of all generated PDFs | `certificates.read` |

### Transactional Email Delivery (P6)

| Method | Endpoint | Description | Auth Level |
| --- | --- | --- | --- |
| `POST` | `/api/v1/email/templates` | Create reusable Jinja2 email template | `settings.manage` |
| `GET` | `/api/v1/email/templates` | List organization email templates | `settings.manage` |
| `GET` | `/api/v1/email/settings` | Retrieve organization SMTP/Provider settings (secrets masked) | Admin / Owner |
| `PUT` | `/api/v1/email/settings` | Update SMTP/Provider configuration | Admin / Owner |
| `POST` | `/api/v1/certificates/{id}/email` | Queue certificate email delivery | `certificates.create` |
| `GET` | `/api/v1/email-deliveries` | List email delivery events and tracking status | `certificates.read` |
| `POST` | `/api/v1/webhooks/email/{provider}` | Inbound email provider webhook receiver | Public (HMAC) |

### Analytics & Reports (P7)

| Method | Endpoint | Description | Auth Level |
| --- | --- | --- | --- |
| `GET` | `/api/v1/analytics/dashboard` | Main dashboard KPIs, trends, and status distribution | `analytics.read` |
| `GET` | `/api/v1/analytics/certificates` | Certificate issuance trends by template and program | `analytics.read` |
| `GET` | `/api/v1/analytics/verification` | Verification scan attempts and validity breakdown | `analytics.read` |
| `POST` | `/api/v1/reports` | Create asynchronous background report job (CSV / PDF) | `reports.create` |
| `GET` | `/api/v1/reports/{id}/download` | Secure report download via signed token | `reports.read` |
| `GET` | `/api/v1/activity` | Paginated organization audit log feed | `analytics.read` |

### Teams, RBAC, API Keys & Webhooks (P8)

| Method | Endpoint | Description | Auth Level |
| --- | --- | --- | --- |
| `GET` | `/api/v1/organization/members` | List organization members and roles | `teams.read` |
| `PATCH` | `/api/v1/organization/members/{id}` | Update member role or suspension status | `teams.manage` |
| `POST` | `/api/v1/organization/invitations` | Invite new member by email | `teams.manage` |
| `POST` | `/api/v1/organization/invitations/accept` | Accept invitation token and join organization | Public |
| `GET` | `/api/v1/roles` | List system and custom roles | `roles.read` |
| `POST` | `/api/v1/roles` | Create custom role with specific permissions | `roles.manage` |
| `GET` | `/api/v1/api-keys` | List organization API keys (secrets omitted) | `apikeys.read` |
| `POST` | `/api/v1/api-keys` | Generate high-entropy API key (`ck_live_...`) | `apikeys.manage` |
| `POST` | `/api/v1/api-keys/{id}/revoke` | Revoke API key immediately | `apikeys.manage` |
| `GET` | `/api/v1/webhooks` | List outbound webhook subscriptions | `webhooks.read` |
| `POST` | `/api/v1/webhooks` | Register outbound webhook endpoint | `webhooks.manage` |
| `POST` | `/api/v1/webhooks/{id}/test` | Send test ping to verify endpoint connectivity | `webhooks.manage` |

### Subscriptions & Usage Metering (P10)

| Method | Endpoint | Description | Auth Level |
| --- | --- | --- | --- |
| `GET` | `/api/v1/plans` | Public subscription catalog with entitlement matrices | Public |
| `GET` | `/api/v1/subscription` | Current organization subscription status & tier | Bearer JWT |
| `POST` | `/api/v1/subscription/checkout` | Create Stripe checkout session for upgrade | Admin / Owner |
| `POST` | `/api/v1/subscription/cancel` | Schedule subscription cancellation | Admin / Owner |
| `GET` | `/api/v1/billing/usage` | Monthly usage progress meters and quota warnings | Bearer JWT |
| `GET` | `/api/v1/billing/invoices` | List payment receipts and invoices | Admin / Owner |
| `POST` | `/api/v1/billing/webhooks/{provider}` | Inbound billing webhook receiver (HMAC verified) | Public (HMAC) |

### Digital Credentials, Open Badges & W3C VC (P11)

| Method | Endpoint | Description | Auth Level |
| --- | --- | --- | --- |
| `GET` | `/api/v1/issuers/profile` | Retrieve issuer profile and active signing key | `issuers.read` |
| `PUT` | `/api/v1/issuers/profile` | Update legal issuer details and website | `issuers.manage` |
| `POST` | `/api/v1/issuers/keys/rotate` | Rotate active Ed25519 key while preserving history | `issuers.manage` |
| `POST` | `/api/v1/achievements` | Define reusable achievement model with criteria | `achievements.create` |
| `GET` | `/api/v1/achievements` | List organization achievements | `achievements.read` |
| `POST` | `/api/v1/credentials` | Issue and cryptographically sign digital credential | `credentials.create` |
| `GET` | `/api/v1/credentials` | List organization issued digital credentials | `credentials.read` |
| `GET` | `/api/v1/credentials/{id}` | Detailed credential view with Data Integrity proof | `credentials.read` |
| `POST` | `/api/v1/credentials/{id}/revoke` | Revoke digital credential with audit rationale | `credentials.revoke` |
| `GET` | `/api/v1/public/issuers/{id}` | Public issuer profile and public key discovery | Public |
| `GET` | `/api/v1/public/credentials/{id}` | Privacy-safe public presentation (omits emails & DB IDs) | Public |
| `GET` | `/api/v1/public/credentials/{id}/verify` | Real-time signature, status, and expiration validation | Public |
| `GET` | `/api/v1/public/credentials/{id}/badge` | 1EdTech Open Badges 3.0 JSON-LD document | Public |
| `GET` | `/api/v1/public/credentials/{id}/vc` | W3C Verifiable Credentials Data Model v2.0 JSON | Public |
| `GET` | `/api/v1/public/credentials/{id}/status` | Public status list entry for external verifiers | Public |
| `POST` | `/api/v1/public/credentials/verify` | Independent verifier for external W3C VC payloads | Public |

---

## 7. MongoDB Collections Reference

CertiFlow organizes platform state across 30+ collections categorized by domain:

```text
├── Identity & Security:        users, organizations, members, invitations, roles, teams, team_members
├── Templates & Assets:         templates, template_versions, assets, fonts
├── Ingestion & Profiling:      imports, import_rows, import_mappings, mapping_profiles
├── Certificate Documents:      certificates, sequences, verification_events
├── Distributed Workers:        issuance_jobs, issuance_job_items, worker_heartbeats
├── Notifications & Email:      email_templates, email_jobs, email_deliveries, email_events, email_suppressions
├── Analytics & Audits:         analytics_daily, reports, audit_logs
├── Developer & Integration:    api_keys, service_accounts, webhooks, webhook_deliveries, api_usage
├── SaaS Billing & Metering:    plans, subscriptions, invoices, usage_counters, usage_events
└── Digital Credentials (P11):  issuer_profiles, achievements, credentials, credential_keys, credential_status, credential_events
```

---

## 8. Local Setup & Quick Start

### System Prerequisites

- **Node.js**: v18.18+ or v20+
- **Python**: 3.12+ (or 3.13)
- **MongoDB**: 7.0+ (running locally on port `27017` or MongoDB Atlas)
- **Redis**: 7.0+ (for background queues, cache, and rate limiting)

### 1. Backend Setup

```powershell
cd E:\Certificate\Backend

# Create and activate Python virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Start FastAPI development server
uvicorn app.main:app --reload --port 8000
```

- Interactive Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc Documentation: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### 2. Background Worker Setup (Optional for Bulk Jobs)

```powershell
cd E:\Certificate\Backend
.\.venv\Scripts\Activate.ps1

# Run ARQ worker process
arq app.queue.worker.WorkerSettings
```

### 3. Frontend Setup

```powershell
cd E:\Certificate

# Install dependencies
npm install

# Start Next.js development server
npm run dev
```

- CertiFlow Web Portal: [http://localhost:3000](http://localhost:3000)

---

## 9. Automated Testing & Verification Suite

CertiFlow features an exhaustive test harness covering pure unit tests, multi-phase integration tests, cryptographic security tests, and automated browser end-to-end user journeys (over 440+ verified tests passing):

```powershell
# 1. Backend Pytest Suite (302/302 tests passing)
cd E:\Certificate\Backend
.\.venv\Scripts\Activate.ps1
pytest -v --tb=short

# 2. Go-Live Production Audit (112/112 checks passing)
python scripts/go_live_audit.py

# 3. Live 11-Stage End-to-End Workflow Audit
python scripts/e2e_backend_workflow_test.py
```

### Frontend E2E & Mobile Viewport Tests (Playwright)

```powershell
cd E:\Certificate

# Run full Playwright test suite (137 passed, 2 skipped, 0 failed across Desktop & Mobile)
npx playwright test

# Run real browser batch generation tests
node scripts/test_generate_10_certs.mjs
node scripts/test_csv_upload_and_generate_5.mjs
```

---

## 10. Environment Configuration

### Backend `.env` (Location: `Backend/.env`)

Template available in [`Backend/.env.production.example`](file:///e:/Certificate/Backend/.env.production.example):

```ini
# Application Identity
APP_NAME="CertiFlow Enterprise"
APP_ENV=production
DEBUG=false
API_V1_PREFIX=/api/v1
APP_BASE_URL=https://app.yourdomain.com
PUBLIC_VERIFY_URL=https://verify.yourdomain.com

# Cryptography & Security
JWT_SECRET_KEY=generate-secure-random-32-byte-hex-string
ENCRYPTION_KEY=fernet-32-byte-base64-encoded-key==
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=30

# Databases
MONGODB_URI="mongodb://localhost:27017"
MONGODB_DATABASE="certificate_platform"
REDIS_URL="redis://localhost:6379"

# Storage & Email
STORAGE_TYPE=local
STORAGE_DIR=/app/storage
EMAIL_PROVIDER=sendgrid
SENDGRID_API_KEY=SG.your_live_key
DEFAULT_FROM_EMAIL=no-reply@yourdomain.com
```

### Frontend `.env.production` (Location: `.env.production`)

```ini
NEXT_PUBLIC_API_URL="https://api.yourdomain.com"
NEXT_PUBLIC_APP_URL="https://app.yourdomain.com"
NODE_ENV="production"
```

---

## 11. Production Deployment & Operational Runbooks

CertiFlow is designed for zero-downtime, production containerized deployments. Refer to the complete [**Production Deployment Handbook**](file:///e:/Certificate/DEPLOYMENT.md) for step-by-step instructions:

- **Docker Compose Orchestration**: [`docker-compose.yml`](file:///e:/Certificate/docker-compose.yml) orchestrates isolated API, worker, Redis, and MongoDB containers with health checks, persistent volumes, and restart policies.
- **Multi-Stage Dockerfiles**: [`Dockerfile`](file:///e:/Certificate/Dockerfile) (Next.js standalone runner on Alpine with unprivileged user `nextjs:nodejs`), [`Backend/Dockerfile.api`](file:///e:/Certificate/Backend/Dockerfile.api), and [`Backend/Dockerfile.worker`](file:///e:/Certificate/Backend/Dockerfile.worker).
- **Incident Response Playbooks**: Located in [`Backend/docs/runbooks/`](file:///e:/Certificate/Backend/docs/runbooks/):
  - [api-outage.md](file:///e:/Certificate/Backend/docs/runbooks/api-outage.md): API triage, container diagnostics, and rolling restarts.
  - [billing-outage.md](file:///e:/Certificate/Backend/docs/runbooks/billing-outage.md): Stripe webhook desynchronization, HMAC troubleshooting, and grace period handling.
  - [disaster-recovery.md](file:///e:/Certificate/Backend/docs/runbooks/disaster-recovery.md): RPO $\le 1$h / RTO $\le 4$h database backup restoration and worker re-queueing procedures.
  - [worker-failure.md](file:///e:/Certificate/Backend/docs/runbooks/worker-failure.md): Queue backpressure, stalled job item recovery, and horizontal autoscaling.

---

## 12. License & Enterprise Support

Proprietary Software. Developed for enterprise certificate authorities, universities, and training institutes. For integration guides, custom key management (AWS KMS/HSM), and enterprise deployment architectures, contact the CertiFlow enterprise architecture team.
