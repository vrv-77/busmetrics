from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any
from uuid import UUID

import pandas as pd
from sqlalchemy import and_, desc, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert import Alert
from app.models.fuel_load_processed import FuelLoadProcessed
from app.models.uploaded_file import UploadedFile
from app.services.excel_processor import build_dashboard_snapshot


@dataclass
class AnalyticsFilters:
    file_id: UUID | None = None
    terminal: str | None = None
    turno: str | None = None
    patente: str | None = None
    numero_interno: str | None = None
    conductor: str | None = None
    supervisor: str | None = None
    planillero: str | None = None
    surtidor: str | None = None
    capturador: str | None = None
    imported_user: str | None = None
    date_from: date | None = None
    date_to: date | None = None
    search: str | None = None


def _apply_load_filters(stmt, filters: AnalyticsFilters):
    conditions = []

    if filters.file_id:
        conditions.append(FuelLoadProcessed.file_id == filters.file_id)
    if filters.terminal:
        conditions.append(FuelLoadProcessed.terminal.ilike(f"%{filters.terminal}%"))
    if filters.turno:
        conditions.append(FuelLoadProcessed.turno.ilike(f"%{filters.turno}%"))
    if filters.patente:
        conditions.append(FuelLoadProcessed.patente.ilike(f"%{filters.patente}%"))
    if filters.numero_interno:
        conditions.append(FuelLoadProcessed.numero_interno.ilike(f"%{filters.numero_interno}%"))
    if filters.conductor:
        conditions.append(FuelLoadProcessed.nombre_conductor.ilike(f"%{filters.conductor}%"))
    if filters.supervisor:
        conditions.append(FuelLoadProcessed.nombre_supervisor.ilike(f"%{filters.supervisor}%"))
    if filters.planillero:
        conditions.append(FuelLoadProcessed.nombre_planillero.ilike(f"%{filters.planillero}%"))
    if filters.surtidor:
        conditions.append(FuelLoadProcessed.surtidor.ilike(f"%{filters.surtidor}%"))
    if filters.capturador:
        conditions.append(FuelLoadProcessed.capturador.ilike(f"%{filters.capturador}%"))
    if filters.date_from:
        conditions.append(FuelLoadProcessed.fecha >= filters.date_from)
    if filters.date_to:
        conditions.append(FuelLoadProcessed.fecha <= filters.date_to)

    if filters.search:
        token = f"%{filters.search}%"
        conditions.append(
            or_(
                FuelLoadProcessed.numero_interno.ilike(token),
                FuelLoadProcessed.patente.ilike(token),
                FuelLoadProcessed.terminal.ilike(token),
                FuelLoadProcessed.turno.ilike(token),
                FuelLoadProcessed.nombre_conductor.ilike(token),
                FuelLoadProcessed.nombre_supervisor.ilike(token),
                FuelLoadProcessed.nombre_planillero.ilike(token),
                FuelLoadProcessed.surtidor.ilike(token),
            )
        )

    if filters.imported_user:
        conditions.append(UploadedFile.user_id.ilike(f"%{filters.imported_user}%"))

    if conditions:
        stmt = stmt.where(and_(*conditions))

    return stmt


async def _load_processed_df(db: AsyncSession, filters: AnalyticsFilters) -> pd.DataFrame:
    stmt = select(
        FuelLoadProcessed.id,
        FuelLoadProcessed.file_id,
        FuelLoadProcessed.turno,
        FuelLoadProcessed.fecha,
        FuelLoadProcessed.hora,
        FuelLoadProcessed.terminal,
        FuelLoadProcessed.numero_interno,
        FuelLoadProcessed.patente,
        FuelLoadProcessed.cantidad_litros,
        FuelLoadProcessed.tipo,
        FuelLoadProcessed.tapa,
        FuelLoadProcessed.filtracion,
        FuelLoadProcessed.modelo_chasis,
        FuelLoadProcessed.estanque,
        FuelLoadProcessed.llenado,
        FuelLoadProcessed.exeso,
        FuelLoadProcessed.odometro,
        FuelLoadProcessed.rut_planillero,
        FuelLoadProcessed.nombre_planillero,
        FuelLoadProcessed.rut_supervisor,
        FuelLoadProcessed.nombre_supervisor,
        FuelLoadProcessed.rut_conductor,
        FuelLoadProcessed.nombre_conductor,
        FuelLoadProcessed.surtidor,
        FuelLoadProcessed.capturador,
        FuelLoadProcessed.cargado_por,
        FuelLoadProcessed.datetime_carga,
        FuelLoadProcessed.anio,
        FuelLoadProcessed.mes,
        FuelLoadProcessed.nombre_mes,
        FuelLoadProcessed.semana,
        FuelLoadProcessed.dia,
        FuelLoadProcessed.dia_semana,
        FuelLoadProcessed.hora_numero,
        FuelLoadProcessed.franja_horaria,
        FuelLoadProcessed.periodo,
        FuelLoadProcessed.litros_redondeados,
        FuelLoadProcessed.registro_duplicado,
        FuelLoadProcessed.alerta_odometro,
        FuelLoadProcessed.alerta_consumo,
        FuelLoadProcessed.out_of_shift,
        FuelLoadProcessed.clave_unica_registro,
        FuelLoadProcessed.dias_desde_ultima_carga,
        FuelLoadProcessed.data_quality_score,
        FuelLoadProcessed.validation_flags,
        UploadedFile.user_id.label("imported_user"),
    ).join(UploadedFile, UploadedFile.id == FuelLoadProcessed.file_id)

    stmt = _apply_load_filters(stmt, filters)

    result = await db.execute(stmt)
    rows = result.mappings().all()

    if not rows:
        return pd.DataFrame(
            columns=[
                "id",
                "file_id",
                "turno",
                "fecha",
                "hora",
                "terminal",
                "numero_interno",
                "patente",
                "cantidad_litros",
                "tipo",
                "tapa",
                "filtracion",
                "modelo_chasis",
                "estanque",
                "llenado",
                "exeso",
                "odometro",
                "rut_planillero",
                "nombre_planillero",
                "rut_supervisor",
                "nombre_supervisor",
                "rut_conductor",
                "nombre_conductor",
                "surtidor",
                "capturador",
                "cargado_por",
                "datetime_carga",
                "anio",
                "mes",
                "nombre_mes",
                "semana",
                "dia",
                "dia_semana",
                "hora_numero",
                "franja_horaria",
                "periodo",
                "litros_redondeados",
                "registro_duplicado",
                "alerta_odometro",
                "alerta_consumo",
                "out_of_shift",
                "clave_unica_registro",
                "dias_desde_ultima_carga",
                "data_quality_score",
                "validation_flags",
                "imported_user",
            ]
        )

    return pd.DataFrame(rows)


async def _load_alerts_df(db: AsyncSession, filters: AnalyticsFilters) -> pd.DataFrame:
    stmt = select(Alert.id, Alert.load_id, Alert.file_id, Alert.type, Alert.severity, Alert.message, Alert.created_at)

    if filters.file_id:
        stmt = stmt.where(Alert.file_id == filters.file_id)

    result = await db.execute(stmt)
    rows = result.mappings().all()

    if not rows:
        return pd.DataFrame(columns=["id", "load_id", "file_id", "type", "severity", "message", "created_at"])
    return pd.DataFrame(rows)


async def get_dashboard_data(db: AsyncSession, filters: AnalyticsFilters) -> dict:
    df = await _load_processed_df(db, filters)
    alerts_df = await _load_alerts_df(db, filters)

    if df.empty:
        return build_dashboard_snapshot(df, alerts_df)

    return build_dashboard_snapshot(df, alerts_df)


async def get_terminal_metrics(db: AsyncSession, filters: AnalyticsFilters) -> list[dict]:
    df = await _load_processed_df(db, filters)
    if df.empty:
        return []

    grouped = (
        df.groupby("terminal", dropna=True, as_index=False)
        .agg(
            total_cargas=("id", "count"),
            litros_totales=("cantidad_litros", "sum"),
            promedio_litros_por_carga=("cantidad_litros", "mean"),
            buses_unicos=("numero_interno", pd.Series.nunique),
            conductores_unicos=("nombre_conductor", pd.Series.nunique),
            surtidores_activos=("surtidor", pd.Series.nunique),
            actividad_reciente=("datetime_carga", "max"),
        )
        .fillna(0)
        .sort_values("litros_totales", ascending=False)
    )

    grouped["participacion_pct"] = (grouped["litros_totales"] / max(grouped["litros_totales"].sum(), 1)) * 100
    grouped["caida_operacional"] = grouped["total_cargas"] < grouped["total_cargas"].median()

    for col in ["litros_totales", "promedio_litros_por_carga", "participacion_pct"]:
        grouped[col] = grouped[col].round(2)

    return grouped.where(pd.notnull(grouped), None).to_dict(orient="records")


async def get_shift_metrics(db: AsyncSession, filters: AnalyticsFilters) -> list[dict]:
    df = await _load_processed_df(db, filters)
    if df.empty:
        return []

    grouped = (
        df.groupby("turno", dropna=True, as_index=False)
        .agg(
            total_cargas=("id", "count"),
            litros_totales=("cantidad_litros", "sum"),
            promedio_litros=("cantidad_litros", "mean"),
            horas_punta=("hora_numero", lambda s: int(s.mode().iloc[0]) if not s.mode().empty else None),
        )
        .fillna(0)
        .sort_values("litros_totales", ascending=False)
    )

    grouped["participacion_pct"] = (grouped["litros_totales"] / max(grouped["litros_totales"].sum(), 1)) * 100
    grouped["horas_valle"] = grouped["horas_punta"].apply(lambda x: int((x + 6) % 24) if x is not None else None)

    for col in ["litros_totales", "promedio_litros", "participacion_pct"]:
        grouped[col] = grouped[col].round(2)

    return grouped.where(pd.notnull(grouped), None).to_dict(orient="records")


async def get_bus_metrics(db: AsyncSession, filters: AnalyticsFilters) -> list[dict]:
    df = await _load_processed_df(db, filters)
    if df.empty:
        return []

    df = df[df["numero_interno"].notna()].copy()
    if df.empty:
        return []

    grouped = (
        df.groupby(["numero_interno", "patente"], as_index=False)
        .agg(
            total_cargas=("id", "count"),
            litros_acumulados=("cantidad_litros", "sum"),
            promedio_litros=("cantidad_litros", "mean"),
            frecuencia_dias=("dias_desde_ultima_carga", "mean"),
            ultima_carga=("datetime_carga", "max"),
            odometro_reciente=("odometro", "max"),
            alertas_odometro=("alerta_odometro", "sum"),
            alertas_consumo=("alerta_consumo", "sum"),
        )
        .fillna(0)
        .sort_values("litros_acumulados", ascending=False)
    )

    now = pd.Timestamp.utcnow().tz_localize("UTC")
    if grouped["ultima_carga"].notna().any():
        grouped["tiempo_desde_ultima_carga_horas"] = (
            (now - pd.to_datetime(grouped["ultima_carga"], utc=True)).dt.total_seconds() / 3600
        ).round(2)
    else:
        grouped["tiempo_desde_ultima_carga_horas"] = None

    for col in ["litros_acumulados", "promedio_litros", "frecuencia_dias"]:
        grouped[col] = grouped[col].round(2)

    grouped["alertas_odometro"] = grouped["alertas_odometro"].astype(int)
    grouped["alertas_consumo"] = grouped["alertas_consumo"].astype(int)

    return grouped.where(pd.notnull(grouped), None).to_dict(orient="records")


async def get_people_metrics(db: AsyncSession, filters: AnalyticsFilters) -> dict[str, list[dict]]:
    df = await _load_processed_df(db, filters)
    if df.empty:
        return {"conductores": [], "supervisores": [], "planilleros": []}

    conductores = (
        df.groupby(["nombre_conductor", "terminal", "turno"], dropna=True, as_index=False)
        .agg(total_registros=("id", "count"), litros_totales=("cantidad_litros", "sum"))
        .sort_values("total_registros", ascending=False)
        .head(30)
    )

    supervisores = (
        df.groupby("nombre_supervisor", dropna=True, as_index=False)
        .agg(total_operaciones=("id", "count"), litros_totales=("cantidad_litros", "sum"))
        .sort_values("total_operaciones", ascending=False)
        .head(30)
    )

    planilleros = (
        df.groupby("nombre_planillero", dropna=True, as_index=False)
        .agg(total_registros=("id", "count"), litros_totales=("cantidad_litros", "sum"))
        .sort_values("total_registros", ascending=False)
        .head(30)
    )

    for frame in (conductores, supervisores, planilleros):
        if "litros_totales" in frame.columns:
            frame["litros_totales"] = frame["litros_totales"].round(2)

    return {
        "conductores": conductores.where(pd.notnull(conductores), None).to_dict(orient="records"),
        "supervisores": supervisores.where(pd.notnull(supervisores), None).to_dict(orient="records"),
        "planilleros": planilleros.where(pd.notnull(planilleros), None).to_dict(orient="records"),
    }


async def get_dispenser_metrics(db: AsyncSession, filters: AnalyticsFilters) -> list[dict]:
    df = await _load_processed_df(db, filters)
    if df.empty:
        return []

    grouped = (
        df.groupby(["surtidor", "capturador", "terminal", "turno"], dropna=True, as_index=False)
        .agg(total_cargas=("id", "count"), litros_totales=("cantidad_litros", "sum"))
        .sort_values(["total_cargas", "litros_totales"], ascending=False)
    )

    grouped["participacion_pct"] = (grouped["total_cargas"] / max(grouped["total_cargas"].sum(), 1)) * 100
    grouped["sin_actividad_reciente"] = grouped["total_cargas"] < grouped["total_cargas"].median()

    for col in ["litros_totales", "participacion_pct"]:
        grouped[col] = grouped[col].round(2)

    return grouped.where(pd.notnull(grouped), None).to_dict(orient="records")


async def get_quality_metrics(db: AsyncSession, filters: AnalyticsFilters) -> dict:
    df = await _load_processed_df(db, filters)
    if df.empty:
        return {
            "total_registros": 0,
            "porcentaje_registros_completos": 0,
            "registros_con_nulos": 0,
            "registros_patente_invalida": 0,
            "registros_odometro_vacio": 0,
            "registros_duplicados": 0,
            "terminales_mal_homologados": 0,
            "calidad_promedio": 0,
            "errores_por_columna": [],
            "calidad_por_terminal": [],
        }

    total = len(df)

    critical_cols = ["turno", "fecha", "hora", "terminal", "numero_interno", "patente", "cantidad_litros", "surtidor"]
    null_critical = df[critical_cols].isna().any(axis=1)

    patente_invalid = ~df["patente"].fillna("").astype(str).str.match(r"^[A-Z0-9]{5,8}$")

    terminal_bad = df["terminal"].fillna("").str.contains(r"[^A-Z0-9\s\-]", regex=True)

    errors_by_column = []
    for col in critical_cols:
        errors_by_column.append({"columna": col, "nulos": int(df[col].isna().sum())})

    quality_by_terminal = (
        df.groupby("terminal", dropna=True, as_index=False)["data_quality_score"]
        .mean()
        .rename(columns={"data_quality_score": "calidad_promedio"})
    )
    quality_by_terminal["calidad_promedio"] = quality_by_terminal["calidad_promedio"].round(2)

    completos = int((~null_critical).sum())

    return {
        "total_registros": int(total),
        "porcentaje_registros_completos": round((completos / max(total, 1)) * 100, 2),
        "registros_con_nulos": int(null_critical.sum()),
        "registros_patente_invalida": int(patente_invalid.sum()),
        "registros_odometro_vacio": int(df["odometro"].isna().sum()),
        "registros_duplicados": int(df["registro_duplicado"].sum()),
        "terminales_mal_homologados": int(terminal_bad.sum()),
        "calidad_promedio": round(float(df["data_quality_score"].mean()), 2),
        "errores_por_columna": errors_by_column,
        "calidad_por_terminal": quality_by_terminal.where(pd.notnull(quality_by_terminal), None).to_dict(orient="records"),
    }


async def get_operations_table(
    db: AsyncSession,
    filters: AnalyticsFilters,
    page: int = 1,
    page_size: int = 50,
    sort_by: str = "datetime_carga",
    sort_dir: str = "desc",
) -> dict[str, Any]:
    df = await _load_processed_df(db, filters)

    if df.empty:
        return {"rows": [], "total": 0, "page": page, "page_size": page_size}

    sortable_columns = set(df.columns)
    if sort_by not in sortable_columns:
        sort_by = "datetime_carga"

    ascending = sort_dir.lower() == "asc"
    df = df.sort_values(sort_by, ascending=ascending, na_position="last")

    total = len(df)
    page = max(page, 1)
    page_size = min(max(page_size, 1), 1000)
    start = (page - 1) * page_size
    end = start + page_size

    page_df = df.iloc[start:end].copy()

    for col in ["datetime_carga", "fecha"]:
        if col in page_df.columns:
            page_df[col] = page_df[col].astype(str)

    return {
        "rows": page_df.where(pd.notnull(page_df), None).to_dict(orient="records"),
        "total": int(total),
        "page": int(page),
        "page_size": int(page_size),
    }


async def get_alerts(db: AsyncSession, filters: AnalyticsFilters, limit: int = 500) -> list[dict]:
    stmt = select(Alert).order_by(desc(Alert.created_at)).limit(limit)

    if filters.file_id:
        stmt = stmt.where(Alert.file_id == filters.file_id)

    result = await db.execute(stmt)
    alerts = result.scalars().all()

    return [
        {
            "id": a.id,
            "load_id": a.load_id,
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


# Compatibility aliases with previous route names
async def get_station_metrics(db: AsyncSession, filters: AnalyticsFilters) -> list[dict]:
    return await get_terminal_metrics(db, filters)


async def get_charger_metrics(db: AsyncSession, filters: AnalyticsFilters) -> list[dict]:
    return await get_dispenser_metrics(db, filters)
