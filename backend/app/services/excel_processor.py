from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO

import numpy as np
import pandas as pd

from app.core.config import get_settings

settings = get_settings()

REQUIRED_COLUMNS = [
    "ID",
    "INICIO (UTC+00:00)",
    "T\u00c9RMINO (UTC+00:00)",
    "ACTIVO",
    "CARGADOR",
    "CONECTOR",
    "VEH\u00cdCULO",
    "SOC INICIAL (%)",
    "SOC FINAL (%)",
    "SOH (%)",
    "ENERGIA CARGADA (kWh)",
    "POTENCIA PROMEDIO (kW)",
    "POTENCIA M\u00c1XIMA (kW)",
    "RFID DE INICIO",
    "RFID DE T\u00c9RMINO",
    "OD\u00d3METRO (km)",
]

COLUMN_MAP = {
    "ID": "source_id",
    "INICIO (UTC+00:00)": "inicio",
    "T\u00c9RMINO (UTC+00:00)": "termino",
    "ACTIVO": "estacion",
    "CARGADOR": "cargador",
    "CONECTOR": "conector",
    "VEH\u00cdCULO": "vehiculo",
    "SOC INICIAL (%)": "soc_inicial",
    "SOC FINAL (%)": "soc_final",
    "SOH (%)": "soh",
    "ENERGIA CARGADA (kWh)": "energia_kwh",
    "POTENCIA PROMEDIO (kW)": "potencia_promedio",
    "POTENCIA M\u00c1XIMA (kW)": "potencia_maxima",
    "RFID DE INICIO": "rfid_inicio",
    "RFID DE T\u00c9RMINO": "rfid_termino",
    "OD\u00d3METRO (km)": "odometro_km",
}


@dataclass
class ProcessedFile:
    sessions_df: pd.DataFrame
    alerts_df: pd.DataFrame
    logs_df: pd.DataFrame
    dashboard_snapshot: dict


class ExcelProcessingError(Exception):
    pass


def process_excel(payload: bytes) -> ProcessedFile:
    try:
        raw_df = pd.read_excel(BytesIO(payload), header=2, engine="openpyxl")
    except Exception as exc:  # pragma: no cover - pandas/openpyxl parse errors
        raise ExcelProcessingError(f"No se pudo leer el archivo Excel: {exc}") from exc

    if raw_df.empty:
        raise ExcelProcessingError("El archivo Excel no contiene registros para procesar.")

    raw_df.columns = [str(col).strip() for col in raw_df.columns]
    missing_columns = [col for col in REQUIRED_COLUMNS if col not in raw_df.columns]
    if missing_columns:
        missing = ", ".join(missing_columns)
        raise ExcelProcessingError(f"Faltan columnas requeridas en el Excel: {missing}")

    df = raw_df[REQUIRED_COLUMNS].rename(columns=COLUMN_MAP).copy()
    df["excel_row"] = df.index + 4

    _normalize_text_columns(df, ["estacion", "cargador", "conector", "vehiculo", "rfid_inicio", "rfid_termino"])
    _cast_numeric_columns(df, ["soc_inicial", "soc_final", "soh", "energia_kwh", "potencia_promedio", "potencia_maxima", "odometro_km"])
    _cast_datetime_columns(df, ["inicio", "termino"])

    df["sesion_incompleta"] = df["termino"].isna()
    df["duracion_minutos"] = (df["termino"] - df["inicio"]).dt.total_seconds() / 60
    df["duracion_horas"] = df["duracion_minutos"] / 60
    df["duracion_min"] = df["duracion_minutos"]
    df["alerta_soc_bajo"] = df["soc_inicial"].lt(20).fillna(False)

    df["hora_inicio_local"] = df["inicio"].dt.strftime("%H:%M")
    df["dia"] = df["inicio"].dt.date
    df["semana"] = df["inicio"].dt.isocalendar().week.astype("Int64")
    df["mes"] = df["inicio"].dt.month.astype("Int64")
    df["hora_dia"] = df["inicio"].dt.hour.astype("Int64")

    validation_logs = _build_validation_logs(df)
    alerts_df = _build_alerts(df)
    dashboard_snapshot = build_dashboard_snapshot(df, alerts_df)

    sessions_df = df[
        [
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
    ].copy()

    return ProcessedFile(
        sessions_df=sessions_df,
        alerts_df=alerts_df,
        logs_df=validation_logs,
        dashboard_snapshot=dashboard_snapshot,
    )


def _normalize_text_columns(df: pd.DataFrame, columns: list[str]) -> None:
    for col in columns:
        df[col] = (
            df[col]
            .astype("string")
            .str.strip()
            .replace({"": pd.NA, "nan": pd.NA, "None": pd.NA, "<NA>": pd.NA})
        )


def _cast_numeric_columns(df: pd.DataFrame, columns: list[str]) -> None:
    for col in columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")


def _cast_datetime_columns(df: pd.DataFrame, columns: list[str]) -> None:
    for col in columns:
        parsed = pd.to_datetime(df[col], utc=True, errors="coerce")
        df[col] = parsed.dt.tz_convert(settings.timezone)


def _build_validation_logs(df: pd.DataFrame) -> pd.DataFrame:
    logs: list[dict] = []

    def append_logs(mask: pd.Series, code: str, level: str, message: str) -> None:
        if not mask.any():
            return
        subset = df.loc[mask, ["excel_row"]]
        logs.extend(
            {
                "level": level,
                "code": code,
                "message": message,
                "row_index": int(row["excel_row"]),
            }
            for _, row in subset.iterrows()
        )

    append_logs(df["inicio"].isna(), "INVALID_START", "error", "Fecha de inicio invalida o faltante.")
    append_logs(df["sesion_incompleta"], "MISSING_END", "warning", "Sesion sin termino.")
    append_logs(df["duracion_minutos"].lt(0).fillna(False), "NEGATIVE_DURATION", "error", "Duracion negativa detectada.")
    append_logs(
        (~df["soc_inicial"].between(0, 100, inclusive="both")).fillna(True),
        "INVALID_SOC_INITIAL",
        "error",
        "SOC inicial fuera de rango [0, 100].",
    )
    append_logs(df["energia_kwh"].lt(0).fillna(False), "NEGATIVE_ENERGY", "error", "Energia cargada negativa.")
    append_logs(
        ((df["potencia_promedio"].lt(settings.power_min_kw)) | (df["potencia_promedio"].gt(settings.power_max_kw))).fillna(False),
        "POWER_OUT_OF_RANGE",
        "warning",
        "Potencia promedio fuera de rango operativo.",
    )
    append_logs(
        ((df["potencia_maxima"].lt(settings.power_min_kw)) | (df["potencia_maxima"].gt(settings.power_max_kw))).fillna(False),
        "MAX_POWER_OUT_OF_RANGE",
        "warning",
        "Potencia maxima fuera de rango operativo.",
    )
    append_logs(df["vehiculo"].isna(), "MISSING_BUS_ID", "warning", "Bus sin identificador.")
    append_logs(df["cargador"].notna() & df["estacion"].isna(), "MISSING_STATION", "warning", "Cargador sin estacion asociada.")

    energy_inconsistency = (
        df["duracion_horas"].gt(0)
        & df["energia_kwh"].notna()
        & df["potencia_maxima"].notna()
        & (df["energia_kwh"] > (df["potencia_maxima"] * df["duracion_horas"] * 1.25))
    )
    append_logs(energy_inconsistency.fillna(False), "INCONSISTENT_ENERGY", "warning", "Energia inconsistente con duracion/potencia.")

    return pd.DataFrame(logs, columns=["level", "code", "message", "row_index"])


def _build_alerts(df: pd.DataFrame) -> pd.DataFrame:
    alerts: list[dict] = []

    def append_alerts(mask: pd.Series, alert_type: str, severity: str, message: str) -> None:
        if not mask.any():
            return
        subset = df.loc[mask]
        alerts.extend(
            {
                "session_idx": int(idx),
                "type": alert_type,
                "severity": severity,
                "message": message,
            }
            for idx in subset.index
        )

    append_alerts(df["alerta_soc_bajo"], "SOC_BAJO", "rojo", "SOC inicial menor al 20%.")
    append_alerts(df["sesion_incompleta"], "SESION_INCOMPLETA", "gris", "Sesion sin registro de termino.")

    duration_anomaly = (
        df["duracion_minutos"].notna()
        & ((df["duracion_minutos"] < settings.duration_anomaly_min_minutes) | (df["duracion_minutos"] > settings.duration_anomaly_max_minutes))
    )
    append_alerts(duration_anomaly, "DURACION_ANOMALA", "amarillo", "Duracion fuera de umbrales operativos.")

    abnormal_power = (
        ((df["potencia_promedio"] < settings.power_min_kw) | (df["potencia_promedio"] > settings.power_max_kw))
        | ((df["potencia_maxima"] < settings.power_min_kw) | (df["potencia_maxima"] > settings.power_max_kw))
    )
    append_alerts(abnormal_power.fillna(False), "POTENCIA_ANORMAL", "amarillo", "Potencia promedio/maxima fuera de rango.")

    inconsistent_energy = (
        df["duracion_horas"].gt(0)
        & df["energia_kwh"].notna()
        & df["potencia_maxima"].notna()
        & (df["energia_kwh"] > (df["potencia_maxima"] * df["duracion_horas"] * 1.25))
    )
    append_alerts(inconsistent_energy.fillna(False), "ENERGIA_INCONSISTENTE", "amarillo", "Energia cargada inconsistente con duracion y potencia.")

    return pd.DataFrame(alerts, columns=["session_idx", "type", "severity", "message"])


def build_dashboard_snapshot(df: pd.DataFrame, alerts_df: pd.DataFrame) -> dict:
    df_valid = df.copy()

    total_sesiones = int(len(df_valid))
    energia_total = float(df_valid["energia_kwh"].fillna(0).sum())
    potencia_promedio = float(df_valid["potencia_promedio"].dropna().mean()) if df_valid["potencia_promedio"].notna().any() else 0.0
    potencia_maxima = float(df_valid["potencia_maxima"].dropna().max()) if df_valid["potencia_maxima"].notna().any() else 0.0
    duracion_promedio = float(df_valid["duracion_min"].dropna().mean()) if df_valid["duracion_min"].notna().any() else 0.0

    if "source_id" not in df_valid.columns:
        df_valid["source_id"] = df_valid.index

    cargas_por_estacion = _group_records(df_valid, "estacion", "source_id", "count", "total_cargas")
    energia_por_estacion = _group_records(df_valid, "estacion", "energia_kwh", "sum", "energia_total")
    potencia_promedio_por_estacion = _group_records(df_valid, "estacion", "potencia_promedio", "mean", "potencia_promedio")

    ranking_cargadores_df = (
        df_valid.groupby(["cargador", "estacion"], dropna=True, as_index=False)["energia_kwh"]
        .sum(min_count=1)
        .fillna({"energia_kwh": 0})
        .sort_values(by="energia_kwh", ascending=False)
        .head(10)
    )
    ranking_cargadores = ranking_cargadores_df.to_dict(orient="records")

    ranking_buses_df = (
        df_valid.groupby("vehiculo", dropna=True, as_index=False)["energia_kwh"]
        .sum(min_count=1)
        .fillna({"energia_kwh": 0})
        .sort_values(by="energia_kwh", ascending=False)
        .head(10)
    )
    ranking_buses = ranking_buses_df.to_dict(orient="records")

    day_map = {0: "Lun", 1: "Mar", 2: "Mie", 3: "Jue", 4: "Vie", 5: "Sab", 6: "Dom"}
    heatmap_df = (
        df_valid.assign(dow=df_valid["inicio"].dt.dayofweek, hour=df_valid["hora_dia"])
        .groupby(["dow", "hour"], as_index=False)
        .size()
        .rename(columns={"size": "total"})
    )
    heatmap_df["dia"] = heatmap_df["dow"].map(day_map)
    heatmap_horario = heatmap_df[["dia", "hour", "total"]].to_dict(orient="records")

    cargas_por_dia_df = (
        df_valid.groupby("dia", as_index=False)
        .size()
        .rename(columns={"size": "total"})
        .sort_values("dia")
    )
    cargas_por_dia_df["dia"] = cargas_por_dia_df["dia"].astype(str)

    bins = [0, 20, 40, 60, 80, 100]
    labels = ["0-20", "20-40", "40-60", "60-80", "80-100"]
    soc_cut = pd.cut(df_valid["soc_inicial"], bins=bins, labels=labels, include_lowest=True)
    soc_dist_df = soc_cut.value_counts(sort=False, dropna=True).reset_index()
    soc_dist_df.columns = ["rango", "total"]

    alert_summary = {
        "total": int(len(alerts_df)),
        "rojo": int((alerts_df["severity"] == "rojo").sum()) if not alerts_df.empty else 0,
        "amarillo": int((alerts_df["severity"] == "amarillo").sum()) if not alerts_df.empty else 0,
        "gris": int((alerts_df["severity"] == "gris").sum()) if not alerts_df.empty else 0,
    }

    return {
        "kpis": {
            "total_sesiones": total_sesiones,
            "energia_total_kwh": round(energia_total, 2),
            "potencia_promedio_kw": round(potencia_promedio, 2),
            "potencia_maxima_kw": round(potencia_maxima, 2),
            "duracion_promedio_min": round(duracion_promedio, 2),
            "buses_unicos": int(df_valid["vehiculo"].dropna().nunique()),
            "cargadores_activos": int(df_valid["cargador"].dropna().nunique()),
            "estaciones_activas": int(df_valid["estacion"].dropna().nunique()),
            "alertas_criticas": alert_summary["rojo"],
        },
        "cargas_por_estacion": cargas_por_estacion,
        "energia_por_estacion": energia_por_estacion,
        "potencia_promedio_por_estacion": potencia_promedio_por_estacion,
        "ranking_cargadores": ranking_cargadores,
        "ranking_buses": ranking_buses,
        "heatmap_horario": heatmap_horario,
        "cargas_por_dia": cargas_por_dia_df.to_dict(orient="records"),
        "distribucion_soc_inicial": soc_dist_df.to_dict(orient="records"),
        "alertas": alert_summary,
    }


def _group_records(df: pd.DataFrame, group_col: str, value_col: str, agg: str, output_col: str) -> list[dict]:
    grouped = df.groupby(group_col, dropna=True, as_index=False)[value_col].agg(agg)
    grouped = grouped.rename(columns={value_col: output_col})
    if grouped[output_col].dtype in (np.float64, np.float32):
        grouped[output_col] = grouped[output_col].round(2)
    return grouped.to_dict(orient="records")
