from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from uuid import UUID

import pandas as pd
from sqlalchemy import and_, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert import Alert
from app.models.charging_session import ChargingSession
from app.models.uploaded_file import UploadedFile
from app.services.excel_processor import build_dashboard_snapshot


@dataclass
class AnalyticsFilters:
    file_id: UUID | None = None
    estacion: str | None = None
    date_from: date | None = None
    date_to: date | None = None


def _apply_session_filters(stmt, filters: AnalyticsFilters):
    conditions = []

    if filters.file_id:
        conditions.append(ChargingSession.file_id == filters.file_id)
    if filters.estacion:
        conditions.append(ChargingSession.estacion == filters.estacion)
    if filters.date_from:
        conditions.append(ChargingSession.dia >= filters.date_from)
    if filters.date_to:
        conditions.append(ChargingSession.dia <= filters.date_to)

    if conditions:
        stmt = stmt.where(and_(*conditions))
    return stmt


async def _load_sessions_df(db: AsyncSession, filters: AnalyticsFilters) -> pd.DataFrame:
    stmt = select(
        ChargingSession.id,
        ChargingSession.file_id,
        ChargingSession.inicio,
        ChargingSession.termino,
        ChargingSession.estacion,
        ChargingSession.cargador,
        ChargingSession.conector,
        ChargingSession.vehiculo,
        ChargingSession.soc_inicial,
        ChargingSession.soc_final,
        ChargingSession.soh,
        ChargingSession.energia_kwh,
        ChargingSession.potencia_promedio,
        ChargingSession.potencia_maxima,
        ChargingSession.rfid_inicio,
        ChargingSession.rfid_termino,
        ChargingSession.odometro_km,
        ChargingSession.duracion_min,
        ChargingSession.duracion_horas,
        ChargingSession.alerta_soc_bajo,
        ChargingSession.sesion_incompleta,
        ChargingSession.hora_inicio_local,
        ChargingSession.dia,
        ChargingSession.semana,
        ChargingSession.mes,
        ChargingSession.hora_dia,
    )
    stmt = _apply_session_filters(stmt, filters)

    result = await db.execute(stmt)
    rows = result.mappings().all()
    if not rows:
        return pd.DataFrame(
            columns=[
                "id",
                "file_id",
                "inicio",
                "termino",
                "estacion",
                "cargador",
                "conector",
                "vehiculo",
                "soc_inicial",
                "soc_final",
                "soh",
                "energia_kwh",
                "potencia_promedio",
                "potencia_maxima",
                "rfid_inicio",
                "rfid_termino",
                "odometro_km",
                "duracion_min",
                "duracion_horas",
                "alerta_soc_bajo",
                "sesion_incompleta",
                "hora_inicio_local",
                "dia",
                "semana",
                "mes",
                "hora_dia",
            ]
        )
    return pd.DataFrame(rows)


async def get_dashboard_data(db: AsyncSession, filters: AnalyticsFilters) -> dict:
    sessions_df = await _load_sessions_df(db, filters)
    alerts_df = await _load_alerts_df(db, filters)

    if sessions_df.empty:
        return {
            "kpis": {
                "total_sesiones": 0,
                "energia_total_kwh": 0,
                "potencia_promedio_kw": 0,
                "potencia_maxima_kw": 0,
                "duracion_promedio_min": 0,
                "buses_unicos": 0,
                "cargadores_activos": 0,
                "estaciones_activas": 0,
                "alertas_criticas": 0,
            },
            "cargas_por_estacion": [],
            "energia_por_estacion": [],
            "potencia_promedio_por_estacion": [],
            "ranking_cargadores": [],
            "ranking_buses": [],
            "heatmap_horario": [],
            "cargas_por_dia": [],
            "distribucion_soc_inicial": [],
            "alertas": {"total": 0, "rojo": 0, "amarillo": 0, "gris": 0},
        }

    sessions_df = sessions_df.copy()
    sessions_df["source_id"] = sessions_df["id"]
    return build_dashboard_snapshot(sessions_df, alerts_df)


async def get_station_metrics(db: AsyncSession, filters: AnalyticsFilters) -> list[dict]:
    df = await _load_sessions_df(db, filters)
    if df.empty:
        return []

    grouped = (
        df.groupby("estacion", dropna=True, as_index=False)
        .agg(
            total_cargas=("id", "count"),
            energia_total=("energia_kwh", "sum"),
            potencia_promedio=("potencia_promedio", "mean"),
            potencia_maxima=("potencia_maxima", "max"),
            duracion_promedio=("duracion_min", "mean"),
            total_horas_cargando=("duracion_horas", "sum"),
            buses_atendidos=("vehiculo", pd.Series.nunique),
            alertas_soc_bajo=("alerta_soc_bajo", "sum"),
            sesiones_incompletas=("sesion_incompleta", "sum"),
        )
        .fillna(0)
    )

    for col in ["energia_total", "potencia_promedio", "potencia_maxima", "duracion_promedio", "total_horas_cargando"]:
        grouped[col] = grouped[col].round(2)

    grouped["alertas_soc_bajo"] = grouped["alertas_soc_bajo"].astype(int)
    grouped["sesiones_incompletas"] = grouped["sesiones_incompletas"].astype(int)

    return grouped.sort_values("energia_total", ascending=False).to_dict(orient="records")


async def get_charger_metrics(db: AsyncSession, filters: AnalyticsFilters) -> list[dict]:
    df = await _load_sessions_df(db, filters)
    if df.empty:
        return []

    max_end = df["termino"].fillna(df["inicio"]).max()
    min_start = df["inicio"].min()
    if pd.isna(max_end) or pd.isna(min_start):
        horas_disponibles = 1.0
    else:
        horas_disponibles = max(((max_end - min_start).total_seconds() / 3600), 1.0)

    grouped = (
        df.groupby(["cargador", "estacion"], dropna=True, as_index=False)
        .agg(
            total_sesiones=("id", "count"),
            energia_total=("energia_kwh", "sum"),
            potencia_promedio=("potencia_promedio", "mean"),
            potencia_maxima=("potencia_maxima", "max"),
            duracion_promedio=("duracion_min", "mean"),
            total_horas_operando=("duracion_horas", "sum"),
            buses_atendidos=("vehiculo", pd.Series.nunique),
        )
        .fillna(0)
    )

    grouped["eficiencia_kwh_por_hora"] = grouped.apply(
        lambda r: (r["energia_total"] / r["total_horas_operando"]) if r["total_horas_operando"] > 0 else 0,
        axis=1,
    )
    grouped["utilizacion"] = (grouped["total_horas_operando"] / horas_disponibles).clip(lower=0)

    for col in [
        "energia_total",
        "potencia_promedio",
        "potencia_maxima",
        "duracion_promedio",
        "total_horas_operando",
        "eficiencia_kwh_por_hora",
        "utilizacion",
    ]:
        grouped[col] = grouped[col].round(3)

    return grouped.sort_values("energia_total", ascending=False).to_dict(orient="records")


async def get_bus_metrics(db: AsyncSession, filters: AnalyticsFilters) -> list[dict]:
    df = await _load_sessions_df(db, filters)
    if df.empty:
        return []

    df = df[df["vehiculo"].notna()].copy()
    if df.empty:
        return []

    grouped = (
        df.groupby("vehiculo", as_index=False)
        .agg(
            total_cargas=("id", "count"),
            soc_inicial_promedio=("soc_inicial", "mean"),
            soc_final_promedio=("soc_final", "mean"),
            energia_total_recibida=("energia_kwh", "sum"),
            duracion_promedio=("duracion_min", "mean"),
            cargas_criticas=("alerta_soc_bajo", "sum"),
            inicio_min=("inicio", "min"),
            inicio_max=("inicio", "max"),
        )
        .fillna(0)
    )

    span_hours = (grouped["inicio_max"] - grouped["inicio_min"]).dt.total_seconds() / 3600
    grouped["frecuencia_carga_horas"] = grouped.apply(
        lambda r: (span_hours.iloc[r.name] / r["total_cargas"]) if r["total_cargas"] > 0 else 0,
        axis=1,
    )

    grouped = grouped.drop(columns=["inicio_min", "inicio_max"])

    for col in [
        "soc_inicial_promedio",
        "soc_final_promedio",
        "energia_total_recibida",
        "duracion_promedio",
        "frecuencia_carga_horas",
    ]:
        grouped[col] = grouped[col].round(2)

    grouped["cargas_criticas"] = grouped["cargas_criticas"].astype(int)
    return grouped.sort_values("energia_total_recibida", ascending=False).to_dict(orient="records")


async def _load_alerts_df(db: AsyncSession, filters: AnalyticsFilters) -> pd.DataFrame:
    stmt = select(Alert.id, Alert.session_id, Alert.file_id, Alert.type, Alert.severity, Alert.message, Alert.created_at)

    if filters.file_id:
        stmt = stmt.where(Alert.file_id == filters.file_id)

    result = await db.execute(stmt)
    rows = result.mappings().all()
    if not rows:
        return pd.DataFrame(columns=["id", "session_id", "file_id", "type", "severity", "message", "created_at"])
    return pd.DataFrame(rows)


async def get_alerts(db: AsyncSession, filters: AnalyticsFilters, limit: int = 500) -> list[dict]:
    stmt = select(Alert).order_by(desc(Alert.created_at)).limit(limit)
    if filters.file_id:
        stmt = stmt.where(Alert.file_id == filters.file_id)

    result = await db.execute(stmt)
    alerts = result.scalars().all()
    return [
        {
            "id": a.id,
            "session_id": a.session_id,
            "file_id": str(a.file_id),
            "type": a.type,
            "severity": a.severity,
            "message": a.message,
            "created_at": a.created_at,
        }
        for a in alerts
    ]


async def get_uploaded_files(db: AsyncSession, limit: int = 100) -> list[UploadedFile]:
    stmt = select(UploadedFile).order_by(desc(UploadedFile.upload_date)).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())
