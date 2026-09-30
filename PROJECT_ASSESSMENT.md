# CertiFlow Project Assessment

Assessment date: 2026-09-30

## Executive Summary

CertiFlow is a substantial certificate and digital-credential SaaS prototype with a broad frontend, FastAPI backend, cryptographic verification code, bulk-import flows, and a useful automated test foundation. The repository is not currently production-ready, but it is beyond a basic prototype.

Recommended overall status: **feature-complete prototype / pre-production hardening**.

Estimated completion:

| Area | Estimate | Reason |
| --- | ---: | --- |
| Frontend visual product and demo flows | 85% | Major routes and core demo workflows exist and browser tests pass. |
| Frontend production integration | 60% | API clients exist, but live backend integration, error states, and auth behavior need hardening. |
| Backend domain implementation | 80% | The backend has broad modules, security code, services, and 279 passing tests. |
| Backend production operations | 60% | Database, Redis, email, billing, deployment, observability, and recovery need environment-backed validation. |
| Automated validation | 80% | Strong smoke coverage, 82% backend line coverage, root scripts, and CI gates now exist; some browser tests remain skipped. |
| Security readiness | 65% | Good security-oriented modules and tests, but browser token storage and demo auth fallback are serious concerns. |
| Overall product readiness | 70% | Good foundation; remaining work is mostly integration, security, operations, and release discipline. |

These percentages are engineering estimates from repository inspection and local checks, not a formal audit or certification.

## Validation Performed

All commands were run from this checkout on 2026-09-30.

| Check | Result | Notes |
| --- | --- | --- |
| `npm run typecheck` | PASS | TypeScript completed with no errors. |
| `npm run build` | PASS | Next.js 16.3.6 production build completed and generated 33 routes. |
| `npm run lint` | PASS with warnings | 0 errors and 356 warnings. Main categories are `any`, unused imports/variables, and `react-hooks/set-state-in-effect`. |
| `npm run test:e2e` | PASS with skips | 98 passed, 2 skipped, 100 total. Chromium and mobile projects ran. |
| `Backend\.venv\Scripts\python.exe -m pytest -q` | PASS | 279 passed in 156.39 seconds. |
| Backend `pytest -q` from PowerShell | NOT RUNNABLE directly | Global `pytest` is not installed; the repository virtual environment must be used. |
| Backend coverage | PASS | 82% line coverage across 13,886 statements; CI now enforces an 80% minimum. |

The repository documentation and CI badge now report the measured 279 backend tests. Coverage is measured with `pytest-cov` and enforced at 80%.

## Findings and Risks

### High priority

1. **Authentication failure is masked by a demo user fallback.**
   Resolved in the current working tree: `src/features/auth/auth-guard.tsx` now requires an explicit `certiflow_demo_mode` marker before using the demo user. Ordinary tokens are cleared when `/me` fails. Before production, replace browser demo markers with a server-controlled demo environment policy.

2. **Bearer tokens are stored in `localStorage`.**
   `src/lib/api/client.ts` stores access and refresh tokens in browser storage. Any successful XSS can read these tokens. Prefer secure, `HttpOnly`, `Secure`, `SameSite` cookies for refresh/session material, short-lived access tokens, CSRF protection where cookie-authenticated mutation requests are used, and strict CSP. Keep the current approach only for an explicitly isolated demo environment.

3. **Live frontend-backend workflows are not proven by the current browser suite.**
   The E2E tests heavily validate UI and demo behavior. They do not establish that a real MongoDB, Redis, email provider, Stripe webhook, worker, and frontend deployment work together. Add an environment-backed integration profile with seeded data and a disposable test tenant.

### Medium priority

1. **Lint debt is large even though lint exits successfully.**
   There are 356 warnings, including many `any` types, unused imports, and synchronous state updates in effects. Treat warnings as a tracked backlog and make new warnings fail CI. Start with API response types and auth/organization effects because they affect shared behavior.

2. **No coverage gate or coverage baseline exists.**
   Resolved for the backend: `pytest-cov` is declared, the baseline is 82%, and CI enforces 80%. Frontend unit coverage and branch coverage remain follow-up work.

3. **Repository setup is fragmented.**
   Root validation scripts and a broader CI workflow now exist, but Windows and container setup should still be documented and exercised in CI.

4. **Two browser tests are skipped.**
   The current run skipped a mobile navigation case and one marketing smoke case. Decide whether these are intentionally unsupported, flaky, or incorrectly selected, then either fix and re-enable them or document the reason and add a replacement assertion.

5. **Operational dependencies are not validated locally by the default test command.**
   Readiness depends on MongoDB and Redis, while the product also advertises workers, email, storage, and billing. Add a Docker Compose test profile and a health/readiness smoke test that exercises each required dependency.

### Lower priority

1. **Documentation is ahead of measured reality.**
   Test counts and backend coverage are now measured and documented. The broad P0-P11 feature claims still need to be split into implemented, partially integrated, and planned capabilities.

2. **Frontend typography and UX consistency need a product pass.**
    The root layout uses Next Geist fonts while the design instructions call for an intentional product typography system. This is not a blocker, but a final pass should standardize typography, loading/empty/error states, keyboard behavior, and responsive interaction across the authenticated app.

## What Looks Strong

- TypeScript compilation and production Next.js build are clean.
- Backend tests cover unit, integration, and security directories and currently pass 279 tests.
- Browser tests cover responsive rendering, accessibility basics, CSV parsing, smart-fit behavior, certificate verification, auth redirects, and key product journeys.
- The backend has clear separation for API routers, services, repositories, security, workers, credentials, and middleware.
- Cryptographic verification, spreadsheet formula-injection handling, XSS checks, and responsive smoke tests are already represented in automated tests.

## Recommended Next Steps

### Stage 1: Remove release blockers

1. Complete the demo-auth hardening by replacing the browser `certiflow_demo_mode` marker with a server-controlled demo environment policy before production.
2. Move refresh/session tokens out of `localStorage`; define cookie, CSRF, rotation, logout, expiry, and cross-site rules.
3. Add a real frontend-backend smoke test using a seeded test environment.
4. Add CI with the repository virtual environment and Node version pinned. Make typecheck, build, backend tests, and E2E tests required checks.

### Stage 2: Make the system operable

1. Run MongoDB, Redis, API, worker, and frontend through a documented Compose profile.
2. Test readiness, worker retry/recovery, file storage permissions, email delivery, Stripe webhook replay protection, and backup/restore procedures.
3. Add structured logs, request correlation checks, metrics scraping, alert thresholds, and a production incident runbook.
4. Add rate-limit, tenant-isolation, RBAC, upload, SSRF, and webhook tests against a running service, not only mocked or in-process code.

### Stage 3: Raise maintainability and UX quality

1. Replace shared API-layer `any` types with generated or shared schemas and typed error envelopes.
2. Reduce the 356 lint warnings, starting with shared API, auth, organization, and query modules.
3. Add frontend unit tests for token refresh, API error parsing, CSV edge cases, field matching, smart-fit, and editor store history.
4. Re-enable or explicitly justify the two skipped E2E tests.
5. Add loading, empty, offline, permission-denied, and backend-error states to every authenticated route.
6. Update README feature status and test counts from CI artifacts rather than hand-maintained claims.

### Stage 4: Release readiness

Before launch, complete a threat model and external security review, dependency/container scanning, secret scanning, privacy review, performance tests for large imports and bulk issuance, browser support verification, data retention policy, backup restore drill, and a staged deployment with rollback.

## Suggested Definition of Done

The project can reasonably be called production-ready when:

- CI is reproducible from a clean checkout on the supported Node and Python versions.
- Frontend and backend integration tests pass with real MongoDB and Redis test services.
- Production auth has no implicit demo path and no readable bearer tokens in web storage.
- Tenant isolation, RBAC, rate limits, uploads, webhooks, billing, and workers have running-service tests.
- Coverage is measured and gated, lint warnings are near zero, and skipped tests have documented reasons.
- Observability, backups, restore, incident response, and rollback have been exercised, not just documented.
- README and release notes describe verified behavior rather than intended architecture.
