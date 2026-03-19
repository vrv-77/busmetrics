# Deployment Guide (Render + Supabase)

## 1) Supabase

1. Crea un proyecto en Supabase.
2. Ejecuta `supabase/schema.sql` en SQL Editor.
3. Crea bucket `fuel-files` en Storage.
4. Copia:
   - Project URL
   - anon key
   - service_role key
5. Configura politicas RLS segun tu modelo de seguridad.

## 2) Backend en Render (Web Service)

- Service type: Web Service
- Runtime: Python
- Root Directory: `backend`
- Build Command:

```bash
pip install -r requirements.txt
```

- Start Command:

```bash
python run.py
```

- Variables recomendadas:
  - `PYTHON_VERSION=3.11.9`
  - `APP_ENV=production`
  - `APP_HOST=0.0.0.0`
  - `APP_PORT=10000`
  - `AUTO_INIT_DB=false`
  - `FAIL_ON_STARTUP_DB_ERROR=false`
  - `FRONTEND_URL=https://<tu-frontend>.onrender.com`
  - `CORS_ALLOW_ORIGIN_REGEX=^https://.*\.onrender\.com$`
  - `CORS_EXTRA_ORIGINS=https://<tu-frontend>.onrender.com`
  - `DATABASE_URL=postgresql+asyncpg://...`
  - `SUPABASE_URL=...`
  - `SUPABASE_ANON_KEY=...`
  - `SUPABASE_SERVICE_ROLE_KEY=...`
  - `SUPABASE_STORAGE_BUCKET=fuel-files`
  - `AUTH_REQUIRED=true`
  - `LITROS_MIN_VALIDOS=5`
  - `LITROS_MAX_VALIDOS=550`

## 3) Frontend en Render (Web Service o Static Site)

Opcion recomendada: Web Service (Next.js)

- Root Directory: `frontend`
- Build Command:

```bash
npm ci && npm run build
```

- Start Command:

```bash
npm run start
```

Variables:
- `NEXT_PUBLIC_API_URL=https://<tu-backend>.onrender.com`
- `NEXT_PUBLIC_SUPABASE_URL=https://<project-ref>.supabase.co`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY=<anon-key>`

## 4) Validaciones post deploy

1. `GET /health` del backend retorna `ok`
2. Login con Supabase funciona
3. Carga de archivo guarda metadata y objeto en Storage
4. Preview detecta columnas/formato
5. Procesamiento inserta historico y evita duplicados
6. Dashboard ejecutivo y operacional cargan datos
7. Exportaciones (`csv`, `excel`, `pdf`) funcionan

## 5) Problemas comunes

- CORS bloqueado:
  - Verifica `FRONTEND_URL` exacto en backend
  - Verifica `CORS_EXTRA_ORIGINS` (o `CORS_EXTRA_ORIGIN` por compatibilidad) en backend
  - Verifica `NEXT_PUBLIC_API_URL` correcto en frontend
- Respuesta JSON en URL backend:
  - Es esperado, backend es API
  - Debes abrir la URL del frontend para la UI

## 6) Endurecimiento recomendado

- Worker async (Celery/RQ) para archivos pesados
- Cache para consultas agregadas
- Migraciones versionadas (Alembic)
- Monitoreo y trazas
- Politicas RLS por tenant/rol
