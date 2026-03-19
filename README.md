# BusMetric FuelOps

Plataforma web empresarial para analisis operacional y ejecutivo de cargas de combustible DIESEL en buses.

## Stack

- Frontend: Next.js 14, TypeScript estricto, Tailwind, React Query, Zustand, Recharts
- Backend: FastAPI + Python ETL (Pandas)
- Datos: Supabase PostgreSQL + Supabase Storage + Supabase Auth
- Deploy: Render (frontend + backend)
- Versionado: GitHub

## Capacidades implementadas

- Carga de archivos `.xlsx`, `.xls` y `.xls` con tabla HTML
- Deteccion automatica de tipo real de archivo
- Preview de filas y deteccion de columnas faltantes
- Mapeo manual de columnas antes de procesar
- ETL con normalizacion, tipado, campos derivados y reglas de calidad
- Generacion de clave unica y deduplicacion historica
- Persistencia de archivo original y archivo procesado
- Historico acumulado con filtros avanzados
- Dashboard ejecutivo (KPI + graficos)
- Dashboard operacional (tabla detallada paginada)
- Analisis por terminal, turno, bus, personas y surtidor
- Dashboard de calidad de datos
- Alertas operacionales y de calidad
- Exportacion CSV / Excel / PDF

## Estructura

```txt
.
+-- backend/
|   +-- app/
|   |   +-- api/routes/
|   |   +-- core/
|   |   +-- db/
|   |   +-- models/
|   |   +-- schemas/
|   |   +-- services/
|   +-- tests/
|   +-- requirements.txt
|   +-- run.py
+-- frontend/
|   +-- app/
|   +-- components/
|   +-- lib/
|   +-- store/
+-- supabase/
|   +-- schema.sql
+-- .github/workflows/ci.yml
+-- render.yaml
```

## Flujo funcional

1. Usuario sube archivo en `Archivos`
2. API guarda archivo original en Supabase Storage (fallback local en dev)
3. `GET /files/{id}/preview` detecta formato real, encabezado, faltantes y preview
4. `POST /process-file/{id}` procesa con mapeo manual opcional
5. ETL genera:
   - normalizacion de campos
   - `datetime_carga`
   - `anio`, `mes`, `semana`, `dia_semana`, `franja_horaria`, `periodo`
   - `litros_redondeados`, `registro_duplicado`, `alerta_odometro`, `alerta_consumo`
   - `clave_unica_registro`, `dias_desde_ultima_carga`
6. Se insertan `fuel_loads_raw`, `fuel_loads_processed`, `alerts`, `processing_logs`
7. Dashboards y reportes consumen datos historicos filtrables

## API principal

- `POST /upload-file`
- `GET /files/{file_id}/preview`
- `POST /process-file/{file_id}`
- `GET /files`
- `GET /files/{file_id}/logs`
- `GET /dashboard`
- `GET /operations`
- `GET /terminals`
- `GET /shifts`
- `GET /dispensers`
- `GET /buses`
- `GET /people`
- `GET /quality`
- `GET /alerts`
- `GET /reports/export?scope=...&fmt=excel|csv|pdf`
- Swagger: `/docs`

## Levantar localmente

### 1) Variables de entorno

- Copia `.env.example` en la raiz y completa valores reales.
- Backend usa `backend/.env.example` como referencia.
- Frontend usa `frontend/.env.local.example` como referencia.

### 2) Backend

```bash
cd backend
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python run.py
```

Backend: `http://localhost:8000`

### 3) Frontend

```bash
cd frontend
npm install
copy .env.local.example .env.local
npm run dev
```

Frontend: `http://localhost:3000`

## Base de datos Supabase

Ejecuta `supabase/schema.sql`.

Incluye tablas:

- `users`, `roles`
- `uploaded_files`, `import_jobs`, `import_errors`, `processing_logs`
- `fuel_loads_raw`, `fuel_loads_processed`
- `terminals`, `shifts`, `buses`, `drivers`, `supervisors`, `planners`, `dispensers`, `capturers`
- `alerts`, `audit_logs`, `validation_rules`, `settings`

## Deploy en Render

Ver guia completa en `DEPLOYMENT.md`.

## CI/CD

`.github/workflows/ci.yml` ejecuta:

- Backend: instalacion + tests
- Frontend: lint + build

## Inicio rapido en Windows

```bat
scripts\start-local.cmd
```

Para detener:

```bat
scripts\stop-local.cmd
```
