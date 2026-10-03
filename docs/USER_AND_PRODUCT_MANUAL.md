# CertiFlow — Comprehensive Product & Operator Handbook

Welcome to the definitive user and operator manual for **CertiFlow**. This guide is designed for academic registrars, certification directors, conference organizers, corporate L&D leaders, and enterprise administrators who use CertiFlow to issue, manage, and verify high-stakes certificates and verifiable digital credentials.

---

## 1. Product Overview & Key Concepts

CertiFlow eliminates the manual chaos of issuing certificates by marrying **high-resolution 300 DPI vector design** with **decentralized, tamper-evident cryptographic proofs**.

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        The CertiFlow Pipeline                          │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │
      ┌────────────────────────────┼────────────────────────────┐
      ▼                            ▼                            ▼
1. Design Template          2. Ingest Data              3. Map & Validate
   Visual Drag-and-Drop        CSV or Excel Import         5-Tier Fuzzy Match
   Dynamic Placeholders        Delimiter Sniffing          Live Data Dry-Run
      │                            │                            │
      └────────────────────────────┼────────────────────────────┘
                                   │
      ┌────────────────────────────┼────────────────────────────┐
      ▼                            ▼                            ▼
4. Preview Batch            5. Authoritative Generate   6. Distribute & Verify
   Recipient Carousel          Distributed ARQ Workers     Automated Email Outbox
   Auto-Fit Overflow Check     300 DPI PDFs + ZIP Pack     Instant QR & SHA-256
```

### Core Terminology

- **Organization (Tenant)**: The top-level administrative boundary (e.g., "Stanford University" or "Acme Tech Academy"). All templates, datasets, certificates, and team members belong to an organization.
- **Project**: A single certificate campaign or cohort (e.g., "Full Stack Bootcamp - Fall 2026" or "AI Summit 2026 Attendees").
- **Template**: The visual canvas layout containing background graphics, text layers with dynamic placeholders, signatures, and dynamic QR code positioning.
- **Dataset**: The uploaded CSV or Excel spreadsheet containing recipient records (names, emails, grades, dates, courses).
- **Issuance Job**: A background task processed by distributed workers that generates hundreds or thousands of unique PDF documents and cryptographic credentials.
- **Digital Credential**: The machine-readable W3C Verifiable Credential (v2.0) and Open Badge (3.0) paired with the human-readable PDF.

---

## 2. Getting Started & Multi-Tenant Team Management

### 2.1 Account Creation & Onboarding
1. Navigate to [http://localhost:3000/signup](http://localhost:3000/signup).
2. Enter your full name, organization email address, organization name, and a secure password.
3. Upon registration, you are designated as the **Organization Owner**.
4. The Onboarding Wizard prompts you to set your default canvas orientation (Landscape/Portrait), upload your organization logo, and select your preferred certificate measurement unit (`mm` or `px`).

---

### 2.2 Roles & Permissions (RBAC)

CertiFlow enforces a fine-grained 4-tier Role-Based Access Control model:

| Role | Description | Permissions |
| :--- | :--- | :--- |
| **Owner** | Organization founder or lead administrator | Full access, billing management, API key rotation, organization deletion. |
| **Admin** | Department head or operations manager | Create/edit templates, run issuance jobs, invite team members, revoke certificates. |
| **Member** | Instructor, event coordinator, or designer | Create templates, upload datasets, run preview batches, initiate issuance jobs. |
| **Viewer** | Auditor, compliance officer, or support staff | Read-only access to analytics, audit logs, and issued certificate registries. |

To invite a new team member:
1. Navigate to **Control Hub $\to$ Settings $\to$ Team Management**.
2. Click **Invite Member**.
3. Enter their email address and select their role (`Admin`, `Member`, or `Viewer`).
4. An invitation token is generated with a 7-day expiration.

---

## 3. Visual Certificate Studio

The Certificate Studio (`/app/projects/[id]/editor`) provides a pixel-precise, drag-and-drop design environment.

### 3.1 Canvas Dimensions & Presets
Choose from international standard page dimensions:
- **A4 Landscape**: $297\text{ mm} \times 210\text{ mm}$ (Default for graduation diplomas)
- **A4 Portrait**: $210\text{ mm} \times 297\text{ mm}$
- **US Letter Landscape**: $11\text{ in} \times 8.5\text{ in}$
- **US Letter Portrait**: $8.5\text{ in} \times 11\text{ in}$
- **Custom Dimensions**: Arbitrary width and height specified in millimeters or pixels.

---

### 3.2 Dynamic Text Placeholders
To inject recipient data dynamically into your certificate, enclose variable names in double curly brackets:
- `{{recipient_name}}` — Full name of the recipient (e.g., "Eleanor Vance")
- `{{course_name}}` — Title of the course or achievement (e.g., "Advanced Kubernetes Operations")
- `{{issue_date}}` — Date formatted according to your regional preferences (e.g., "October 2, 2026")
- `{{certificate_id}}` — Unique serial number or credential UUID
- `{{custom_field_1}}` — Any arbitrary column header from your uploaded spreadsheet (e.g., "grade", "honors", "track")

---

### 3.3 Smart-Fit Dynamic Typography
One of the most common certificate production failures is a long name breaking onto multiple lines or overflowing the page. CertiFlow includes a **Smart-Fit Algorithm**:
1. When designing a text element, specify the maximum boundary width box.
2. Enable **Auto-Fit Typography** in the element inspector.
3. During rendering, if a recipient's name exceeds the boundary box, the engine dynamically recalculates the font size and letter spacing downward until the text fits perfectly inside the designated area without word clipping.

---

### 3.4 Dynamic QR Code Placement
1. In the left toolbar, click **Add QR Code**.
2. Position and resize the QR code element on your canvas (recommended minimum size: $25\text{ mm} \times 25\text{ mm}$ for optimal camera scanning).
3. The QR code automatically encodes the certificate's unique public verification URL (`https://certiflow.io/verify/{id}`).
4. When printed or viewed digitally, scanning this code opens the tamper-proof verification page.

---

### 3.5 Asset Management (Logos, Signatures & Borders)
- Upload high-resolution PNG or SVG assets with transparent backgrounds.
- Upload scanned signatures with transparent alpha channels.
- Lock background decorative borders to prevent accidental movement while editing text elements.

---

## 4. Data Ingestion & Intelligent Column Mapping

CertiFlow supports importing recipient lists from standard spreadsheets (`.csv`, `.tsv`, `.xlsx`).

### 4.1 Ingestion & File Sniffing
1. Navigate to **Projects $\to$ [Project Name] $\to$ Data Ingestion**.
2. Drag and drop your spreadsheet into the upload zone.
3. CertiFlow automatically:
   - Sniffs the delimiter (comma `,`, semicolon `;`, tab `\t`, pipe `|`).
   - Detects the character encoding (UTF-8, Latin-1, Windows-1252) to preserve accents and international characters.
   - Parses the first 100 rows inside a browser Web Worker for instantaneous UI feedback.

---

### 4.2 5-Tier Fuzzy Column Matcher
CertiFlow automatically maps your spreadsheet headers to the placeholders in your template using a multi-tiered matching engine:

| Match Tier | Description | Example |
| :--- | :--- | :--- |
| **Tier 1: Exact Match** | Character-for-character match | Column `recipient_name` $\to$ Placeholder `{{recipient_name}}` |
| **Tier 2: Slug Normalization** | Strips punctuation, dashes, spaces | Column `Student-Name` $\to$ Placeholder `{{recipient_name}}` |
| **Tier 3: Synonym Dictionary** | Semantic alias resolution | Column `Learner`, `Attendee`, `Full Name` $\to$ `{{recipient_name}}` |
| **Tier 4: Data Type Heuristics** | Detects email formats or date structures | Column containing `@` $\to$ `{{recipient_email}}` |
| **Tier 5: Levenshtein Distance** | Fuzzy string proximity (>85% confidence) | Column `RecipentName` $\to$ `{{recipient_name}}` |

You can review confidence indicators (Green = High Confidence, Yellow = Review Needed) and manually reassign mappings using the dropdown menus.

---

## 5. Batch Preview & Quality Assurance

Before triggering batch generation, verify your data using the **Live Batch Preview Carousel**:
1. Navigate to **Projects $\to$ [Project Name] $\to$ Preview**.
2. The carousel interpolates actual spreadsheet rows into your canvas template in real time.
3. Click through the shortest, average, and longest recipient names.
4. **Boundary Alerts**: If any record causes an overflow or formatting warning, an alert badge appears at the top of the preview panel, allowing you to adjust text padding before issuing.

---

## 6. Authoritative Bulk Issuance

Once validation is complete, initiate the asynchronous generation job:
1. Navigate to **Projects $\to$ [Project Name] $\to$ Generate**.
2. Click **Start Batch Issuance**.
3. The job is queued into the distributed ARQ worker cluster:
   - **Throughput**: Generates up to 1,000 high-DPI PDF certificates per minute per worker node.
   - **Real-Time Progress**: The UI displays live progress bars, processing speed (certs/sec), completed count, and estimated time to completion.
   - **Error Isolation**: If a single row fails due to corrupted data, the worker records the specific error in an error ledger while successfully processing all remaining certificates.
4. Once completed, download:
   - **Single Master ZIP**: All rendered 300 DPI vector PDFs neatly named by recipient name and serial number.
   - **Issuance Manifest CSV**: Complete audit spreadsheet with certificate IDs, SHA-256 file hashes, and verification URLs.

---

## 7. Automated Email Distribution & Notifications

CertiFlow can automatically deliver certificates directly to recipients' inboxes:
1. Configure your email provider (SMTP, SendGrid, Amazon SES, or Mailgun) in **Settings $\to$ Email Outbox**.
2. Customize your email template using standard HTML and dynamic tags (`{{recipient_name}}`, `{{download_url}}`, `{{verification_url}}`).
3. Each email includes a **secure 7-day HMAC-authenticated download link** allowing the recipient to download their PDF directly without logging in.
4. Monitor email delivery status (Queued, Sent, Delivered, Bounced) from the **Email Outbox** dashboard.

---

## 8. Public Verification & Recipient Experience

CertiFlow provides a frictionless, trustless verification experience for recipients, prospective employers, and academic evaluators.

```text
                               Public Verification Flow
                                          │
                  ┌───────────────────────┴───────────────────────┐
                  ▼                                               ▼
         Option A: QR Code Scan                          Option B: PDF File Upload
                  │                                               │
                  ▼                                               ▼
         Load Public URL (/verify/ID)                    Compute SHA-256 Web Crypto
                  │                                               │
                  └───────────────────────┬───────────────────────┘
                                          │
                                          ▼
                            Compare Against Master Ledger
                                          │
                     ┌────────────────────┴────────────────────┐
                     ▼                                         ▼
            [Status: VALID]                           [Status: TAMPERED/REVOKED]
            • Recipient: Eleanor Vance                • Crimson Warning Banner
            • Issuer: Acme University                 • Reason: Altered Binary Content
            • Ed25519 Cryptographic Proof             • Invalid Digital Signature
            • W3C VC JSON-LD Download
            • 1-Click Add to LinkedIn
```

### 8.1 Verifying via Dynamic QR Code
- Scan the printed or digital certificate's QR code using any smartphone camera.
- The browser opens the verified credential portal displaying the recipient's name, course, issuing institution, issue date, and an active **Cryptographically Verified** badge.

### 8.2 Verifying via PDF Drag-and-Drop (SHA-256 Hash Matching)
- If an employer receives a PDF via email, they can verify it without contacting the university:
- Visit `https://certiflow.io/verify`.
- Drag and drop the PDF file onto the verification target.
- The browser uses the Web Crypto API to calculate the SHA-256 digest on the client side in milliseconds.
- If even one character or grade on the certificate has been modified, the calculated hash will not match the registered hash, immediately alerting the verifier to a forged document.

### 8.3 1-Click "Add to LinkedIn"
Recipients can click the **Add to LinkedIn Profile** button on their verification page. CertiFlow automatically fills the LinkedIn certification form with the credential name, issuing organization, issuance date, expiration date, and public credential URL.

---

## 9. Governance, Revocations & Audit Logs

CertiFlow provides complete institutional oversight and auditability:

### 9.1 Revoking a Certificate
If a credential was issued in error or revoked due to disciplinary action:
1. Navigate to **Certificates $\to$ Certificate Registry**.
2. Search by recipient name, email, or certificate ID.
3. Click the certificate row to view details, then select **Revoke Certificate**.
4. Select a revocation reason from the dropdown (e.g., "Honor Code Violation", "Administrative Error", "Course Incomplete") and enter an optional explanatory note.
5. Confirm revocation.
6. The public verification page immediately displays a prominent **REVOKED** warning banner, and the W3C Bitstring Status List is updated.

---

### 9.2 Immutable Audit Trail
Every significant action in CertiFlow is permanently recorded in the **Audit Log** (`/app/settings` $\to$ Audit Trail):
- User logins and failed authentication attempts.
- Template creations, edits, and deletions.
- Dataset uploads and column mappings.
- Batch issuance execution with total count and processing time.
- Certificate revocations with reason, user ID, and IP address.
- API key generation and revocation.

Logs can be filtered by date range, user, action type, or target resource, and exported to CSV for compliance audits.

---

## 10. Frequently Asked Questions (FAQ)

### Q: Can recipients download certificates without creating a CertiFlow account?
**A**: Yes. Recipients access their certificate via the unique public verification link or the direct email download token without requiring any user registration or login.

### Q: What happens if CertiFlow is offline? Can credentials still be verified?
**A**: Yes. Machine-readable W3C Verifiable Credentials and Open Badges contain self-describing cryptographic proofs signed with the issuer's private Ed25519 key. Any verifier can inspect the embedded `did:key` public key and verify the cryptographic signature offline using standard cryptographic libraries.

### Q: What is the maximum number of certificates I can issue in a single batch?
**A**: Standard plans support up to 10,000 certificates per batch. Enterprise plans running on multi-worker ARQ clusters support batches exceeding 100,000 certificates with streaming ZIP generation and direct S3 bucket streaming.

### Q: Can I use my own custom fonts?
**A**: Yes. CertiFlow supports standard Google Fonts out of the box and allows you to upload custom `.ttf`, `.otf`, `.woff`, and `.woff2` font files directly into your organization's font library.
