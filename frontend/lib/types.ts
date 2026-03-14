export type Severity = "rojo" | "amarillo" | "gris"

export interface DashboardKpis {
  total_sesiones: number
  energia_total_kwh: number
  potencia_promedio_kw: number
  potencia_maxima_kw: number
  duracion_promedio_min: number
  buses_unicos: number
  cargadores_activos: number
  estaciones_activas: number
  alertas_criticas: number
}

export interface DashboardData {
  kpis: DashboardKpis
  cargas_por_estacion: Array<{ estacion: string; total_cargas: number }>
  energia_por_estacion: Array<{ estacion: string; energia_total: number }>
  potencia_promedio_por_estacion: Array<{ estacion: string; potencia_promedio: number }>
  ranking_cargadores: Array<{ cargador: string; estacion?: string; energia_kwh: number }>
  ranking_buses: Array<{ vehiculo: string; energia_kwh: number }>
  heatmap_horario: Array<{ dia: string; hour: number; total: number }>
  cargas_por_dia: Array<{ dia: string; total: number }>
  distribucion_soc_inicial: Array<{ rango: string; total: number }>
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
  upload_date: string
  processed_at: string | null
  error_message: string | null
}

export interface StationMetric {
  estacion: string
  total_cargas: number
  energia_total: number
  potencia_promedio: number
  potencia_maxima: number
  duracion_promedio: number
  total_horas_cargando: number
  buses_atendidos: number
  alertas_soc_bajo: number
  sesiones_incompletas: number
}

export interface ChargerMetric {
  cargador: string
  estacion: string | null
  total_sesiones: number
  energia_total: number
  potencia_promedio: number
  potencia_maxima: number
  duracion_promedio: number
  total_horas_operando: number
  buses_atendidos: number
  eficiencia_kwh_por_hora: number
  utilizacion: number
}

export interface BusMetric {
  vehiculo: string
  total_cargas: number
  soc_inicial_promedio: number
  soc_final_promedio: number
  energia_total_recibida: number
  duracion_promedio: number
  frecuencia_carga_horas: number
  cargas_criticas: number
}

export interface AlertItem {
  id: number
  session_id: number | null
  file_id: string
  type: string
  severity: Severity
  message: string
  created_at: string
}
