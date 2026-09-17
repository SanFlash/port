# Falguni Chauhan — Enhanced 3D Portfolio

Flask / Python 3.13 portfolio with native WebGL, CSS 3D visuals, responsive layouts,
and Render + Vercel deployment configurations. No Node.js build is required.

## Admin access

Admin sign-in is available at `/admin`. Configure `ADMIN_EMAIL` and either
`ADMIN_PASSWORD_HASH` or `ADMIN_PASSWORD` privately in your `.env` file or hosting
environment. No working admin credentials are included in this public repository.
A non-empty `ADMIN_PASSWORD` takes precedence over the hash.

Generate a hash without echoing your password:

```sh
python -c "from getpass import getpass; from werkzeug.security import generate_password_hash; print(generate_password_hash(getpass('Admin password: ')))"
```

Copy the output into `ADMIN_PASSWORD_HASH` in your hosting environment.

## Run on Windows

Open a terminal inside this extracted project folder:

```powershell
py -3.13 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python -m flask --app app init-db
python -m flask --app app seed-db
python app.py
```

Visit http://localhost:5000. Admin: http://localhost:5000/admin.
Set your admin environment variables in `.env` before signing in.
Local storage uses `instance/portfolio.db` when `DATABASE_URL` is blank.

On macOS/Linux use `python3.13 -m venv .venv`, `source .venv/bin/activate`,
and `cp .env.example .env`; all following Python commands are identical.

## What is included

- Pointer-responsive, ray-marched WebGL sculpture representing strategy, design,
  and connection; CSS 3D fallback if WebGL is unavailable.
- Layered 3D project visuals for TEEJH, TalkItOut Community, and Bhuttico.
- Project category filters, accessible detail dialogs, and expandable case studies.
- Animated research orbits, strategy objects, content layers, and YouTube visuals.
- Motion pause control, reduced-motion support, offscreen rendering suspension,
  mobile navigation, responsive layouts, and keyboard focus states.
- All supplied profile, project, skills, research, experience, education, contact,
  Behance, and YouTube facts. No invented project outcomes or campaign statistics.
- Downloadable text résumé generated from the supplied information.
- Contact form with confirmed success/failure feedback and PostgreSQL/SQLite storage.
- Admin sign-in/out and draft/create/publish/delete CMS actions.

Project artwork is a conceptual visual treatment, not supplied client artwork.
Original source files remain unchanged in `original-nextjs/`. Original data is
retained in `data/portfolio.json` and `data/database_seed.json`; new presentation
metadata is in `data/showcase.json`. Original CSS is retained; `enhanced.css`
adds the new visual layer. Google Fonts are optional with local system fallbacks;
3D objects and animation scripts are bundled locally and require no external model.

## Production database setup

Use persistent PostgreSQL for Render or Vercel. Set `DATABASE_URL` to the provider's
connection URL (use the recommended pooled URL for Vercel), for example:

```text
postgresql://USER:PASSWORD@HOST:5432/DBNAME?sslmode=require
```

From your local environment, with that URL configured, run once:

```sh
python -m flask --app app init-db
python -m flask --app app seed-db
```

These commands create missing tables and insert missing original seed records.
They never replace existing content. Original Prisma table/column names are retained.
A ZIP does not contain records from an external production database.

## Deploy to Render

1. Put the project files in a Git repository with `app.py` at the selected root.
2. Create a Render Blueprint from `render.yaml`, or a Python web service manually.
3. Build: `pip install -r requirements.txt`.
4. Start: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 60`.
5. Set `DATABASE_URL`, `SITE_URL`, and `APP_ENV=production`.
6. Set a random `AUTH_SECRET`; the Blueprint generates one automatically.
7. Deploy. `.python-version` selects Python 3.13.

The Blueprint asks for the admin email and password hash as private environment settings.

## Deploy to Vercel

1. Import the repository; select the folder containing `app.py` as Root Directory.
2. Use Flask framework detection; remove previous Next.js build/output overrides.
3. Set `DATABASE_URL`, `AUTH_SECRET`, `SITE_URL`, `APP_ENV=production`,
   `ADMIN_EMAIL`, and `ADMIN_PASSWORD_HASH`.
4. Deploy. `pyproject.toml` selects Python 3.13 and the `app:app` entrypoint.
5. `public/assets/` is served by Vercel's CDN at the same URLs as Flask.

Set the same admin email and password hash on Vercel before signing in.
Generate a session secret with:

```sh
python -c "import secrets; print(secrets.token_hex(32))"
```

| Setting | Purpose |
| --- | --- |
| `DATABASE_URL` | Persistent PostgreSQL storage in production |
| `AUTH_SECRET` | Stable random signing secret across workers |
| `SITE_URL` | Your full HTTPS deployment address |
| `APP_ENV` | `production` on hosted services |
| `ADMIN_EMAIL` | Your private admin sign-in email |
| `ADMIN_PASSWORD_HASH` | Your private admin password hash |
| `ADMIN_PASSWORD` | Private environment alternative to a hash; takes precedence |

`NEXT_PUBLIC_SITE_URL` is retained as a fallback for `SITE_URL`. Local SQLite
is rejected on hosted services so form submissions are not stored ephemerally.

## Editing and feature boundaries

Public content is generated from the supplied JSON files. The original CMS stores
collection drafts and publication status, but it is not a full visual page editor:
publishing a generic collection item does not automatically rewrite public sections.
The original eight-step onboarding is retained as a navigation-only interface.
Document import, media upload, email notifications, and external API sync adapters
are outside the original implementation and are not claimed as completed here.
Contact messages are stored in `ContactSubmission`; they are not sent by email.

## Verification

```sh
python -m unittest discover -s tests -v
```

See `VERIFICATION.md` for executed checks and remaining hosting limitations.

Deployment references:
- https://vercel.com/docs/frameworks/backend/flask
- https://vercel.com/docs/functions/runtimes/python
- https://render.com/docs/deploy-flask
- https://render.com/docs/python-version
