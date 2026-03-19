export type Severity = "rojo" | "amarillo" | "gris"

export interface DashboardKpis {
  total_cargas: number
  total_litros_cargados: number
  litros_del_dia: number
  litros_del_mes: number
  litros_periodo_filtrado: number
  buses_unicos_atendidos: number
  terminales_activos: number
  surtidores_activos: number
  conductores_unicos: number
  promedio_litros_por_carga: number
  promedio_cargas_por_dia: number
  variacion_porcentual_periodo_anterior: number
  odometro_promedio: number
  carga_promedio_por_terminal: number
  carga_promedio_por_turno: number
}

export interface DashboardData {
  kpis: DashboardKpis
  litros_por_dia: Array<{ fecha: string; cantidad_litros: number }>
  cargas_por_dia: Array<{ fecha: string; total: number }>
  litros_por_terminal: Array<{ terminal: string; litros: number; total_cargas?: number }>
  cargas_por_terminal: Array<{ terminal: string; total_cargas: number }>
  turno_donut: Array<{ turno: string; total_cargas: number; litros: number }>
  terminal_donut: Array<{ terminal: string; total_cargas: number; litros: number }>
  heatmap: Array<{ dia_semana: string; hora_numero: number; total: number }>
  top_buses_por_cargas: Array<{ numero_interno: string; patente: string; total_cargas: number }>
  top_buses_por_litros: Array<{ numero_interno: string; patente: string; litros_totales: number }>
  ranking_terminales_consumo: Array<{ terminal: string; litros: number; total_cargas: number }>
  ranking_surtidores: Array<{ surtidor: string; total_cargas: number; litros_totales: number }>
  ranking_conductores: Array<{ nombre_conductor: string; total_registros: number; litros_totales: number }>
  alertas: {
    total: number
    rojo: number
    amarillo: number
    gris: number
  }
}

export interface UploadedFile {
  id: string
  filename: string
  status: string
  row_count: number
  user_id: string
  detected_format: string | null
  upload_date: string
  processed_at: string | null
  error_message: string | null
}

export interface FilePreview {
  file_id: string
  filename: string
  detected_format: string
  header_row_index: number
  source_columns: string[]
  suggested_mapping: Record<string, string>
  missing_columns: string[]
  preview_rows: Array<Record<string, string>>
}

export interface ProcessResult {
  file_id: string
  status: string
  rows_processed: number
  rows_raw: number
  duplicates_avoided: number
  alerts_created: number
  warnings_logged: number
  dashboard_snapshot: DashboardData
}

export interface TerminalMetric {
  terminal: string
  total_cargas: number
  litros_totales: number
  promedio_litros_por_carga: number
  buses_unicos: number
  conductores_unicos: number
  surtidores_activos: number
  participacion_pct: number
  caida_operacional: boolean
}

export interface DispenserMetric {
  surtidor: string
  capturador: string
  terminal: string
  turno: string
  total_cargas: number
  litros_totales: number
  participacion_pct: number
  sin_actividad_reciente: boolean
}

export interface ShiftMetric {
  turno: string
  total_cargas: number
  litros_totales: number
  promedio_litros: number
  participacion_pct: number
  horas_punta: number | null
  horas_valle: number | null
}

export interface BusMetric {
  numero_interno: string
  patente: string
  total_cargas: number
  litros_acumulados: number
  promedio_litros: number
  frecuencia_dias: number
  ultima_carga: string
  tiempo_desde_ultima_carga_horas: number | null
  odometro_reciente: number
  alertas_odometro: number
  alertas_consumo: number
}

export interface PeopleMetrics {
  conductores: Array<Record<string, string | number | null>>
  supervisores: Array<Record<string, string | number | null>>
  planilleros: Array<Record<string, string | number | null>>
}

export interface QualityMetrics {
  total_registros: number
  porcentaje_registros_completos: number
  registros_con_nulos: number
  registros_patente_invalida: number
  registros_odometro_vacio: number
  registros_duplicados: number
  terminales_mal_homologados: number
  calidad_promedio: number
  errores_por_columna: Array<{ columna: string; nulos: number }>
  calidad_por_terminal: Array<{ terminal: string; calidad_promedio: number }>
}

export interface OperationsResponse {
  rows: Array<Record<string, unknown>>
  total: number
  page: number
  page_size: number
}

export interface AlertItem {
  id: number
  load_id: number | null
  file_id: string
  type: string
  severity: Severity
  message: string
  created_at: string
}
