from pydantic import BaseModel


class KPIMetrics(BaseModel):
    total_sesiones: int
    energia_total_kwh: float
    potencia_promedio_kw: float
    potencia_maxima_kw: float
    duracion_promedio_min: float
    buses_unicos: int
    cargadores_activos: int
    estaciones_activas: int
    alertas_criticas: int


class DashboardResponse(BaseModel):
    kpis: KPIMetrics
    cargas_por_estacion: list[dict]
    energia_por_estacion: list[dict]
    potencia_promedio_por_estacion: list[dict]
    ranking_cargadores: list[dict]
    ranking_buses: list[dict]
    heatmap_horario: list[dict]
    cargas_por_dia: list[dict]
    distribucion_soc_inicial: list[dict]
    alertas: dict


class StationMetric(BaseModel):
    estacion: str
    total_cargas: int
    energia_total: float
    potencia_promedio: float
    potencia_maxima: float
    duracion_promedio: float
    total_horas_cargando: float
    buses_atendidos: int
    alertas_soc_bajo: int
    sesiones_incompletas: int


class ChargerMetric(BaseModel):
    cargador: str
    estacion: str | None
    total_sesiones: int
    energia_total: float
    potencia_promedio: float
    potencia_maxima: float
    duracion_promedio: float
    total_horas_operando: float
    buses_atendidos: int
    eficiencia_kwh_por_hora: float
    utilizacion: float


class BusMetric(BaseModel):
    vehiculo: str
    total_cargas: int
    soc_inicial_promedio: float
    soc_final_promedio: float
    energia_total_recibida: float
    duracion_promedio: float
    frecuencia_carga_horas: float
    cargas_criticas: int
