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

## 2) Backend (Render Web Service)

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
  - `APP_PORT=10000`
  - `AUTO_INIT_DB=false`
  - `FAIL_ON_STARTUP_DB_ERROR=false`
  - `FRONTEND_URL=https://<your-frontend>.onrender.com`
  - `DATABASE_URL=postgresql+asyncpg://...`
  - `SUPABASE_URL=...`
  - `SUPABASE_ANON_KEY=...`
  - `SUPABASE_SERVICE_ROLE_KEY=...`
  - `SUPABASE_STORAGE_BUCKET=charging-files`
  - `AUTH_REQUIRED=true`

## 3) Frontend (Render Static Site)

- Service type: Static Site
- Root Directory: `frontend`
- Build Command:

```bash
npm ci && npm run build
```

- Publish Directory:

```bash
out
```

Environment variables:
- `NEXT_PUBLIC_API_URL=https://<your-backend>.onrender.com`
- `NEXT_PUBLIC_SUPABASE_URL=https://<project-ref>.supabase.co`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY=<anon-key>`

## 4) Why you see JSON in the browser

If you open the backend URL directly, this response is expected:

```json
{"service":"BusMetric API","status":"ok","docs":"/docs","health":"/health"}
```

That URL is the API service, not the web UI. Open the Static Site URL to see the dashboard.

## 5) Common CORS issue in Render

If browser console shows:
- `Redirect is not allowed for a preflight request`
- `Disallowed CORS origin`

Check both:
1. `NEXT_PUBLIC_API_URL` must use `.onrender.com` (not `.onrender.co`).
2. Backend `FRONTEND_URL` must match your static site origin exactly, for example:
   - `https://busmetrics-1.onrender.com`

## 6) Post deploy checks

1. `GET /health` returns `ok`
2. Login works with Supabase Auth
3. Excel upload stores file and metadata
4. Processing inserts sessions and alerts
5. Dashboard loads KPIs and charts
6. Exports (`csv`, `excel`, `pdf`) download correctly

## 7) Recommended hardening

- Add async worker (Celery/RQ) for heavy files
- Cache dashboard queries (Redis)
- Add versioned migrations (Alembic)
- Add tracing/monitoring
- Complete tenant/user RLS policies
