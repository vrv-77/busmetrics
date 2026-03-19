from pydantic import BaseModel


class KPIMetrics(BaseModel):
    total_cargas: int
    total_litros_cargados: float
    litros_del_dia: float
    litros_del_mes: float
    litros_periodo_filtrado: float
    buses_unicos_atendidos: int
    terminales_activos: int
    surtidores_activos: int
    conductores_unicos: int
    promedio_litros_por_carga: float
    promedio_cargas_por_dia: float
    variacion_porcentual_periodo_anterior: float
    odometro_promedio: float
    carga_promedio_por_terminal: float
    carga_promedio_por_turno: float


class DashboardResponse(BaseModel):
    kpis: KPIMetrics
    litros_por_dia: list[dict]
    cargas_por_dia: list[dict]
    litros_por_terminal: list[dict]
    cargas_por_terminal: list[dict]
    turno_donut: list[dict]
    terminal_donut: list[dict]
    heatmap: list[dict]
    top_buses_por_cargas: list[dict]
    top_buses_por_litros: list[dict]
    ranking_terminales_consumo: list[dict]
    ranking_surtidores: list[dict]
    ranking_conductores: list[dict]
    alertas: dict
