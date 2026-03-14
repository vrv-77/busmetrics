# Deployment Guide

## 1) Supabase

1. Create a Supabase project.
2. Run `supabase/schema.sql` in SQL Editor.
3. Create bucket `charging-files`.
4. Copy:
   - Project URL
   - anon key
   - service_role key
5. Configure RLS according to your security model.

## 2) Backend (Render)

- Service type: Web Service
- Runtime: Python (not Docker)
- Root Directory: `backend`
- Build Command:

```bash
pip install -r requirements.txt
```

- Start Command:

```bash
python run.py
```

- Environment Variables:
  - `PYTHON_VERSION=3.11.9`
  - `APP_ENV=production`
  - `APP_HOST=0.0.0.0`
  - `APP_PORT=10000` (or Render port)
  - `FRONTEND_URL=https://<your-frontend>.vercel.app`
  - `DATABASE_URL=postgresql+asyncpg://...`
  - `SUPABASE_URL=...`
  - `SUPABASE_ANON_KEY=...`
  - `SUPABASE_SERVICE_ROLE_KEY=...`
  - `SUPABASE_STORAGE_BUCKET=charging-files`
  - `AUTH_REQUIRED=true`

## 3) Frontend (Vercel)

- Root Directory: `frontend`
- Framework: Next.js
- Build command: `npm run build`

Environment variables:
- `NEXT_PUBLIC_API_URL=https://<your-backend>.onrender.com`
- `NEXT_PUBLIC_SUPABASE_URL=https://<project-ref>.supabase.co`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY=<anon-key>`

## 4) Post deploy checks

1. `GET /health` returns `ok`
2. Login works with Supabase Auth
3. Excel upload stores file and metadata
4. Processing inserts sessions and alerts
5. Dashboard loads KPIs and charts
6. Exports (`csv`, `excel`, `pdf`) download correctly

## 5) Recommended hardening

- Add async worker (Celery/RQ) for heavy files
- Cache dashboard queries (Redis)
- Add versioned migrations (Alembic)
- Add tracing/monitoring
- Complete tenant/user RLS policies
