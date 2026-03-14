# BusMetric Ops

Plataforma web empresarial para análisis operacional de cargas de buses eléctricos en electrolineras.

## Stack

- Frontend: Next.js 14 (App Router), TypeScript, Tailwind CSS, componentes estilo ShadCN, Recharts, React Query, Zustand
- Backend: FastAPI, Pandas, OpenPyXL, Pydantic, SQLAlchemy
- Datos: Supabase PostgreSQL + Supabase Storage + Supabase Auth
- Infraestructura objetivo: GitHub + Vercel (frontend) + Render (backend) + Supabase

## Estructura del proyecto

```txt
.
+-- backend/
¦   +-- app/
¦   ¦   +-- api/routes/
¦   ¦   +-- core/
¦   ¦   +-- db/
¦   ¦   +-- models/
¦   ¦   +-- schemas/
¦   ¦   +-- services/
¦   +-- tests/
¦   +-- requirements.txt
¦   +-- run.py
+-- frontend/
¦   +-- app/
¦   +-- components/
¦   +-- lib/
¦   +-- store/
+-- supabase/
¦   +-- schema.sql
+-- .github/workflows/ci.yml
+-- .env.example
```

## Flujo funcional

1. Usuario sube archivo Excel en `Archivos`
2. `POST /upload-file` guarda metadata y archivo en Supabase Storage (fallback local en dev)
3. `POST /process-file/{id}` ejecuta pipeline Pandas:
   - Lectura con `read_excel(header=2)` (encabezado en fila 3)
   - Conversión UTC -> `America/Santiago`
   - Cálculo de columnas:
     - `duracion_min`, `duracion_horas`
     - `alerta_soc_bajo`
     - `sesion_incompleta`
     - `hora_inicio_local`, `dia`, `semana`, `mes`, `hora_dia`
   - Validaciones y logs:
     - sesión sin término
     - duración negativa
     - SOC inicial inválido
     - energía negativa
     - potencia fuera de rango
     - bus sin ID
     - cargador sin estación
   - Generación de alertas (`rojo`, `amarillo`, `gris`)
4. Se persisten `charging_sessions`, `alerts`, `processing_logs`
5. Dashboard y vistas consumen API para KPIs, gráficas y tablas
6. Reportes exportables: Excel, CSV, PDF

## API principal

- `POST /upload-file`
- `POST /process-file/{id}`
- `GET /files`
- `GET /files/{id}/logs`
- `GET /dashboard`
- `GET /stations`
- `GET /chargers`
- `GET /buses`
- `GET /alerts`
- `GET /reports/export?scope=...&fmt=excel|csv|pdf`
- Swagger: `/docs`

## Levantar localmente

### 1) Variables de entorno

Copia `.env.example` y completa credenciales.

- Backend usa `backend/.env.example`
- Frontend usa `frontend/.env.local.example`

### 2) Backend

```bash
cd backend
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell
# .\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
cp .env.example .env
python run.py
```

API disponible en `http://localhost:8000`.

### 3) Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

UI disponible en `http://localhost:3000`.

## Base de datos Supabase

Ejecuta el SQL en `supabase/schema.sql`.

Tablas:
- `users`
- `uploaded_files`
- `charging_sessions`
- `alerts`
- `processing_logs`

## Despliegue

### Frontend en Vercel

1. Importa `frontend/` desde GitHub
2. Variables:
   - `NEXT_PUBLIC_API_URL`
   - `NEXT_PUBLIC_SUPABASE_URL`
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
3. Build command: `npm run build`
4. Output: Next.js default

### Backend en Render

1. Nuevo Web Service apuntando a `backend/`
2. Runtime: Python 3.11+
3. Build: `pip install -r requirements.txt`
4. Start: `python run.py`
5. Variables backend según `.env.example`

### Supabase

1. Crea proyecto
2. Ejecuta `supabase/schema.sql`
3. Crea bucket `charging-files`
4. Configura Auth y llaves en frontend/backend

## CI/CD

Pipeline en `.github/workflows/ci.yml`:
- Backend: instala dependencias + `pytest`
- Frontend: `npm install`, `npm run lint`, `npm run build`

## Notas de escalabilidad

- Pipeline Pandas vectorizado para 50k+ filas
- Inserciones bulk en DB
- Índices por `file_id`, `inicio`, `estacion`, `cargador`, `vehiculo`
- Filtros por fecha/estación para consultas operacionales

## Observabilidad y control

- Logs de calidad de datos en `processing_logs`
- Alertas operacionales normalizadas por severidad
- Historial de archivos y estado de procesamiento
