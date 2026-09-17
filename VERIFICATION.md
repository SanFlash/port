# Enhanced portfolio verification

## Python / backend

Validated on CPython 3.13.15 with the pinned dependencies installed.
The original enhancement passed 8 automated unittest groups:

- Public pages, supplied content, assets, and unknown-file protection.
- Admin authorization and create/publish/delete lifecycle.
- Invalid payloads and cross-origin write rejection.
- Contact/event persistence across app instances.
- Exact original seed values and repeated idempotent seeding.
- Requested admin credentials, password hash verification, and logout.
- Résumé download and asynchronous contact form response.
- Database CLI setup and SEO endpoints.

## Browser

Headless Chromium rendered the native WebGL sculpture successfully. Actual browser
interaction checks passed for project filtering, project dialogs, motion pause,
reduced-motion preference, contact submission, configured admin login, CMS draft
creation/publication/deletion, logout, and mobile navigation. No JavaScript page
errors were observed. No horizontal overflow was found at 320, 375, 390, 768,
1024, or 1440 pixel viewport widths. Screenshots were visually inspected; a hero typography
specificity issue was identified and fixed during review.

## Original content

Original source files remain in `original-nextjs/` with the SHA-256 inventory from
the source conversion. The original public and database seed JSON files are retained.
Expanded public sections use the supplied project, work history, education, research,
and contact facts. Artwork is conceptual; no client screenshots, campaign outcomes,
subscriber counts, or unsupported statistics were fabricated.

## Deployment boundary

The Flask app was exercised through Gunicorn locally. Render/Vercel configuration
is included, but no hosted deployment or live PostgreSQL integration was performed.
Tests use isolated SQLite databases. Configure and initialize PostgreSQL for hosted
CMS, contact submissions, and analytics storage. Google Fonts are optional; system
font fallbacks preserve readability if the font service is unavailable.

The retained generic CMS and onboarding limitations are described in README.md.

## Public repository preparation

Working admin credentials were removed from the public source and deployment
configuration. Admin login now requires private environment settings. Added a test
that unconfigured admin access is disabled.
