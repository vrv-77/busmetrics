# Deployment Guide

## 1) Supabase

1. Crea un proyecto Supabase
2. Ejecuta `supabase/schema.sql` en SQL Editor
3. Crea bucket `charging-files`
4. Copia:
   - Project URL
   - anon key
   - service_role key
5. Configura RLS según políticas corporativas

## 2) Backend (Render)

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
  - `APP_ENV=production`
  - `APP_HOST=0.0.0.0`
  - `APP_PORT=10000` (o puerto de Render)
  - `FRONTEND_URL=https://<tu-frontend>.vercel.app`
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
- `NEXT_PUBLIC_API_URL=https://<tu-backend>.onrender.com`
- `NEXT_PUBLIC_SUPABASE_URL=https://<project-ref>.supabase.co`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY=<anon-key>`

## 4) Post deploy checks

1. `GET /health` responde `ok`
2. Login funciona con Supabase Auth
3. Subida de Excel guarda archivo y metadata
4. Procesamiento inserta sesiones y alertas
5. Dashboard carga KPIs y gráficos
6. Exportaciones (`csv`, `excel`, `pdf`) descargan correctamente

## 5) Escalabilidad y hardening recomendado

- Añadir worker asíncrono (Celery/RQ) para archivos grandes
- Cachear consultas de dashboard (Redis)
- Agregar migraciones versionadas (Alembic)
- Implementar tracing (OpenTelemetry)
- Completar políticas RLS por tenant/usuario
