-- BusMetric Supabase schema
-- Execute in Supabase SQL editor

create extension if not exists pgcrypto;

create table if not exists public.users (
  id uuid primary key,
  email text,
  full_name text,
  created_at timestamptz not null default now()
);

create table if not exists public.uploaded_files (
  id uuid primary key default gen_random_uuid(),
  filename text not null,
  storage_path text not null,
  upload_date timestamptz not null default now(),
  user_id text not null,
  status text not null default 'uploaded',
  row_count integer not null default 0,
  processed_at timestamptz,
  error_message text
);

create table if not exists public.charging_sessions (
  id bigserial primary key,
  file_id uuid not null references public.uploaded_files(id) on delete cascade,
  inicio timestamptz not null,
  termino timestamptz,
  estacion text,
  cargador text,
  conector text,
  vehiculo text,
  soc_inicial double precision,
  soc_final double precision,
  soh double precision,
  energia_kwh double precision,
  potencia_promedio double precision,
  potencia_maxima double precision,
  rfid_inicio text,
  rfid_termino text,
  odometro_km double precision,
  duracion_min double precision,
  duracion_horas double precision,
  alerta_soc_bajo boolean not null default false,
  sesion_incompleta boolean not null default false,
  hora_inicio_local text,
  dia date,
  semana integer,
  mes integer,
  hora_dia integer,
  created_at timestamptz not null default now()
);

create table if not exists public.alerts (
  id bigserial primary key,
  session_id bigint references public.charging_sessions(id) on delete set null,
  file_id uuid not null references public.uploaded_files(id) on delete cascade,
  type text not null,
  severity text not null,
  message text not null,
  created_at timestamptz not null default now()
);

create table if not exists public.processing_logs (
  id bigserial primary key,
  file_id uuid not null references public.uploaded_files(id) on delete cascade,
  level text not null,
  code text not null,
  message text not null,
  row_index integer,
  created_at timestamptz not null default now()
);

create index if not exists ix_uploaded_files_upload_date on public.uploaded_files(upload_date desc);
create index if not exists ix_charging_sessions_file_id on public.charging_sessions(file_id);
create index if not exists ix_charging_sessions_inicio on public.charging_sessions(inicio);
create index if not exists ix_charging_sessions_estacion on public.charging_sessions(estacion);
create index if not exists ix_charging_sessions_cargador on public.charging_sessions(cargador);
create index if not exists ix_charging_sessions_vehiculo on public.charging_sessions(vehiculo);
create index if not exists ix_alerts_file_id on public.alerts(file_id);
create index if not exists ix_alerts_severity on public.alerts(severity);
create index if not exists ix_processing_logs_file_id on public.processing_logs(file_id);

-- RLS (optional baseline)
alter table public.uploaded_files enable row level security;
alter table public.charging_sessions enable row level security;
alter table public.alerts enable row level security;
alter table public.processing_logs enable row level security;

-- Example permissive policy for service role usage.
create policy if not exists "service role full access uploaded_files"
  on public.uploaded_files for all using (auth.role() = 'service_role') with check (auth.role() = 'service_role');
create policy if not exists "service role full access charging_sessions"
  on public.charging_sessions for all using (auth.role() = 'service_role') with check (auth.role() = 'service_role');
create policy if not exists "service role full access alerts"
  on public.alerts for all using (auth.role() = 'service_role') with check (auth.role() = 'service_role');
create policy if not exists "service role full access logs"
  on public.processing_logs for all using (auth.role() = 'service_role') with check (auth.role() = 'service_role');
