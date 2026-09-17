# Falguni Portfolio CMS

A single Next.js deployment and one PostgreSQL database, designed to work without configured integrations. The public portfolio is responsive; `/admin` has password-protected CMS collections, draft/publish/delete workflow and first-run onboarding.

## Deploy to Vercel + Supabase

1. Create a Supabase project, then copy its PostgreSQL **connection string** into `DATABASE_URL`.
2. In a local terminal, install dependencies and run `pnpm db:generate`, `pnpm prisma migrate deploy`, and `pnpm db:seed`.
3. Import this repository in Vercel. Add every required variable from `.env.example`: `DATABASE_URL`, `AUTH_SECRET`, `ADMIN_EMAIL`, `ADMIN_PASSWORD`, and `NEXT_PUBLIC_SITE_URL`.
4. Redeploy after setting `NEXT_PUBLIC_SITE_URL` to the production address. Visit `/admin` to sign in and `/onboarding` for the optional eight-step setup.

## Storage and integrations

Create a private Supabase Storage bucket named `portfolio-media`; set `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, and `SUPABASE_STORAGE_BUCKET` only when uploads are enabled. Media records store provider URLs so swapping to S3-compatible storage does not change content records. Configure `YOUTUBE_API_KEY` only for sync; manual channels and videos always work. Configure Resend variables only when an email delivery adapter is added; contact submissions are persisted regardless.

## Safety and workflow

Admin authentication requires explicit production credentials. Never use the example secret in production. Imported documents should create source-labelled drafts and be reviewed before publishing. The current seed uses only facts from the supplied CV plus the supplied Behance and YouTube links.

## Verification

Run `pnpm lint`, `pnpm typecheck`, and `pnpm build` before deployment. The build requires a reachable PostgreSQL URL for generated Prisma client/database-backed API routes.
