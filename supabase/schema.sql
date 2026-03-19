-- BusMetric Fuel Platform schema
-- Execute in Supabase SQL Editor

create extension if not exists pgcrypto;

create table if not exists public.roles (
  id uuid primary key default gen_random_uuid(),
  name text not null unique,
  description text,
  created_at timestamptz not null default now()
);

create table if not exists public.users (
  id uuid primary key,
  email text,
  full_name text,
  role_id uuid references public.roles(id),
  is_active boolean not null default true,
  created_at timestamptz not null default now()
);

create table if not exists public.settings (
  key text primary key,
  value jsonb not null,
  description text,
  updated_at timestamptz not null default now()
);

create table if not exists public.validation_rules (
  id uuid primary key default gen_random_uuid(),
  rule_code text not null unique,
  description text not null,
  rule_config jsonb not null,
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.terminals (
  id uuid primary key default gen_random_uuid(),
  code text not null unique,
  name text not null,
  is_active boolean not null default true,
  created_at timestamptz not null default now()
);

create table if not exists public.shifts (
  id uuid primary key default gen_random_uuid(),
  code text not null unique,
  name text not null,
  start_hour integer not null,
  end_hour integer not null,
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  constraint shifts_hour_range check (start_hour between 0 and 23 and end_hour between 0 and 23)
);

create table if not exists public.buses (
  id uuid primary key default gen_random_uuid(),
  numero_interno text not null unique,
  patente text,
  terminal_id uuid references public.terminals(id),
  modelo_chasis text,
  is_active boolean not null default true,
  created_at timestamptz not null default now()
);

create table if not exists public.drivers (
  id uuid primary key default gen_random_uuid(),
  rut text not null unique,
  name text not null,
  terminal_id uuid references public.terminals(id),
  is_active boolean not null default true,
  created_at timestamptz not null default now()
);

create table if not exists public.supervisors (
  id uuid primary key default gen_random_uuid(),
  rut text not null unique,
  name text not null,
  terminal_id uuid references public.terminals(id),
  is_active boolean not null default true,
  created_at timestamptz not null default now()
);

create table if not exists public.planners (
  id uuid primary key default gen_random_uuid(),
  rut text not null unique,
  name text not null,
  terminal_id uuid references public.terminals(id),
  is_active boolean not null default true,
  created_at timestamptz not null default now()
);

create table if not exists public.dispensers (
  id uuid primary key default gen_random_uuid(),
  code text not null unique,
  terminal_id uuid references public.terminals(id),
  is_active boolean not null default true,
  created_at timestamptz not null default now()
);

create table if not exists public.capturers (
  id uuid primary key default gen_random_uuid(),
  code text not null unique,
  terminal_id uuid references public.terminals(id),
  is_active boolean not null default true,
  created_at timestamptz not null default now()
);

create table if not exists public.uploaded_files (
  id uuid primary key default gen_random_uuid(),
  filename text not null,
  storage_path text not null,
  processed_storage_path text,
  detected_format text,
  upload_date timestamptz not null default now(),
  user_id text not null,
  status text not null default 'uploaded',
  row_count integer not null default 0,
  processed_at timestamptz,
  error_message text
);

create table if not exists public.import_jobs (
  id uuid primary key default gen_random_uuid(),
  file_id uuid not null references public.uploaded_files(id) on delete cascade,
  started_at timestamptz not null default now(),
  finished_at timestamptz,
  status text not null default 'processing',
  row_count integer not null default 0,
  inserted_count integer not null default 0,
  duplicate_count integer not null default 0,
  warning_count integer not null default 0,
  error_count integer not null default 0,
  initiated_by text,
  metadata jsonb not null default '{}'::jsonb
);

create table if not exists public.import_errors (
  id bigserial primary key,
  job_id uuid not null references public.import_jobs(id) on delete cascade,
  file_id uuid not null references public.uploaded_files(id) on delete cascade,
  row_number integer,
  column_name text,
  error_code text not null,
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

create table if not exists public.fuel_loads_raw (
  id bigserial primary key,
  file_id uuid not null references public.uploaded_files(id) on delete cascade,
  row_number integer,
  source_payload text not null,
  normalized_payload text not null,
  created_at timestamptz not null default now()
);

create table if not exists public.fuel_loads_processed (
  id bigserial primary key,
  file_id uuid not null references public.uploaded_files(id) on delete cascade,

  turno text,
  fecha date,
  hora text,
  terminal text,
  numero_interno text,
  patente text,
  cantidad_litros double precision,
  tipo text,
  tapa text,
  filtracion text,
  modelo_chasis text,
  estanque text,
  llenado text,
  exeso text,
  odometro double precision,

  rut_planillero text,
  nombre_planillero text,
  rut_supervisor text,
  nombre_supervisor text,
  rut_conductor text,
  nombre_conductor text,

  surtidor text,
  capturador text,
  cargado_por text,

  datetime_carga timestamptz,
  anio integer,
  mes integer,
  nombre_mes text,
  semana integer,
  dia integer,
  dia_semana text,
  hora_numero integer,
  franja_horaria text,
  periodo text,

  litros_redondeados integer,
  registro_duplicado boolean not null default false,
  alerta_odometro boolean not null default false,
  alerta_consumo boolean not null default false,
  out_of_shift boolean not null default false,
  clave_unica_registro text not null unique,
  dias_desde_ultima_carga integer,

  data_quality_score double precision,
  validation_flags text,
  created_at timestamptz not null default now()
);

create table if not exists public.alerts (
  id bigserial primary key,
  load_id bigint references public.fuel_loads_processed(id) on delete set null,
  file_id uuid not null references public.uploaded_files(id) on delete cascade,
  type text not null,
  severity text not null,
  message text not null,
  created_at timestamptz not null default now()
);

create table if not exists public.audit_logs (
  id bigserial primary key,
  user_id text,
  action text not null,
  entity_name text not null,
  entity_id text,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index if not exists ix_uploaded_files_upload_date on public.uploaded_files(upload_date desc);
create index if not exists ix_import_jobs_file_id on public.import_jobs(file_id);
create index if not exists ix_import_errors_file_id on public.import_errors(file_id);
create index if not exists ix_processing_logs_file_id on public.processing_logs(file_id);
create index if not exists ix_fuel_loads_raw_file_id on public.fuel_loads_raw(file_id);
create index if not exists ix_fuel_loads_processed_file_id on public.fuel_loads_processed(file_id);
create index if not exists ix_fuel_loads_processed_datetime on public.fuel_loads_processed(datetime_carga);
create index if not exists ix_fuel_loads_processed_terminal on public.fuel_loads_processed(terminal);
create index if not exists ix_fuel_loads_processed_turno on public.fuel_loads_processed(turno);
create index if not exists ix_fuel_loads_processed_patente on public.fuel_loads_processed(patente);
create index if not exists ix_fuel_loads_processed_numero_interno on public.fuel_loads_processed(numero_interno);
create index if not exists ix_fuel_loads_processed_conductor on public.fuel_loads_processed(nombre_conductor);
create index if not exists ix_fuel_loads_processed_supervisor on public.fuel_loads_processed(nombre_supervisor);
create index if not exists ix_fuel_loads_processed_planillero on public.fuel_loads_processed(nombre_planillero);
create index if not exists ix_fuel_loads_processed_surtidor on public.fuel_loads_processed(surtidor);
create index if not exists ix_alerts_file_id on public.alerts(file_id);
create index if not exists ix_alerts_severity on public.alerts(severity);
create index if not exists ix_audit_logs_created_at on public.audit_logs(created_at desc);

-- RLS baseline
alter table public.uploaded_files enable row level security;
alter table public.import_jobs enable row level security;
alter table public.import_errors enable row level security;
alter table public.processing_logs enable row level security;
alter table public.fuel_loads_raw enable row level security;
alter table public.fuel_loads_processed enable row level security;
alter table public.alerts enable row level security;
alter table public.audit_logs enable row level security;
alter table public.validation_rules enable row level security;
alter table public.settings enable row level security;
alter table public.terminals enable row level security;
alter table public.shifts enable row level security;
alter table public.dispensers enable row level security;
alter table public.capturers enable row level security;

create policy if not exists "service role full access uploaded_files"
  on public.uploaded_files for all using (auth.role() = 'service_role') with check (auth.role() = 'service_role');
create policy if not exists "service role full access import_jobs"
  on public.import_jobs for all using (auth.role() = 'service_role') with check (auth.role() = 'service_role');
create policy if not exists "service role full access import_errors"
  on public.import_errors for all using (auth.role() = 'service_role') with check (auth.role() = 'service_role');
create policy if not exists "service role full access processing_logs"
  on public.processing_logs for all using (auth.role() = 'service_role') with check (auth.role() = 'service_role');
create policy if not exists "service role full access fuel_loads_raw"
  on public.fuel_loads_raw for all using (auth.role() = 'service_role') with check (auth.role() = 'service_role');
create policy if not exists "service role full access fuel_loads_processed"
  on public.fuel_loads_processed for all using (auth.role() = 'service_role') with check (auth.role() = 'service_role');
create policy if not exists "service role full access alerts"
  on public.alerts for all using (auth.role() = 'service_role') with check (auth.role() = 'service_role');
create policy if not exists "service role full access audit_logs"
  on public.audit_logs for all using (auth.role() = 'service_role') with check (auth.role() = 'service_role');
create policy if not exists "service role full access validation_rules"
  on public.validation_rules for all using (auth.role() = 'service_role') with check (auth.role() = 'service_role');
create policy if not exists "service role full access settings"
  on public.settings for all using (auth.role() = 'service_role') with check (auth.role() = 'service_role');
create policy if not exists "service role full access terminals"
  on public.terminals for all using (auth.role() = 'service_role') with check (auth.role() = 'service_role');
create policy if not exists "service role full access shifts"
  on public.shifts for all using (auth.role() = 'service_role') with check (auth.role() = 'service_role');
create policy if not exists "service role full access dispensers"
  on public.dispensers for all using (auth.role() = 'service_role') with check (auth.role() = 'service_role');
create policy if not exists "service role full access capturers"
  on public.capturers for all using (auth.role() = 'service_role') with check (auth.role() = 'service_role');

-- Seed catalogs and default rules
insert into public.roles(name, description)
values
  ('admin', 'Administrador plataforma'),
  ('operator', 'Operador de carga'),
  ('viewer', 'Consulta ejecutiva')
on conflict (name) do nothing;

insert into public.terminals(code, name)
values
  ('TERMINAL_NORTE', 'Terminal Norte'),
  ('TERMINAL_SUR', 'Terminal Sur'),
  ('TERMINAL_CENTRO', 'Terminal Centro')
on conflict (code) do nothing;

insert into public.shifts(code, name, start_hour, end_hour)
values
  ('A', 'Turno A', 0, 7),
  ('B', 'Turno B', 8, 15),
  ('C', 'Turno C', 16, 23)
on conflict (code) do nothing;

insert into public.validation_rules(rule_code, description, rule_config)
values
  ('LITROS_RANGO', 'Rango valido de litros por carga', '{"min":5,"max":550}'::jsonb),
  ('ODOMETRO_NUMERICO', 'Odometro debe ser numerico cuando existe', '{"required_numeric":true}'::jsonb),
  ('PATENTE_FORMATO', 'Formato estandar de patente', '{"regex":"^[A-Z0-9]{5,8}$"}'::jsonb),
  ('NO_DUPLICADOS', 'Evitar insercion de duplicados historicos', '{"unique_key":"clave_unica_registro"}'::jsonb)
on conflict (rule_code) do nothing;

insert into public.settings(key, value, description)
values
  ('timezone', '"America/Santiago"'::jsonb, 'Zona horaria operativa'),
  ('litros_min_validos', '5'::jsonb, 'Litros minimos permitidos'),
  ('litros_max_validos', '550'::jsonb, 'Litros maximos permitidos'),
  ('turnos_activos', '["A","B","C"]'::jsonb, 'Turnos habilitados para validacion')
on conflict (key) do nothing;
