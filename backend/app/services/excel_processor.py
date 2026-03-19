from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from hashlib import sha256
from io import BytesIO, StringIO
import json
import re
import unicodedata

import pandas as pd

from app.core.config import get_settings

settings = get_settings()


def _normalize_seed(value: object) -> str:
    if value is None:
        return ""
    text = str(value)
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text


EXPECTED_COLUMNS: list[str] = [
    "Turno",
    "Fecha",
    "Hora",
    "Terminal",
    "Numero interno",
    "Patente",
    "Cantidad litros",
    "Tipo",
    "Tapa",
    "Filtracion",
    "Modelo chasis",
    "Estanque",
    "Llenado",
    "Exeso",
    "Odometro",
    "RUT planillero",
    "Nombre planillero",
    "RUT supervisor",
    "Nombre supervisor",
    "RUT conductor",
    "Nombre conductor",
    "Surtidor",
    "Capturador",
    "Cargado por",
]

FIELD_DEFS: list[tuple[str, str, tuple[str, ...]]] = [
    ("turno", "Turno", ("turno", "jornada", "shift")),
    ("fecha", "Fecha", ("fecha", "date", "dia")),
    ("hora", "Hora", ("hora", "time", "hora carga")),
    ("terminal", "Terminal", ("terminal", "depot", "patio")),
    ("numero_interno", "Numero interno", ("numero interno", "num interno", "interno", "bus", "bus id")),
    ("patente", "Patente", ("patente", "placa", "matricula")),
    ("cantidad_litros", "Cantidad litros", ("cantidad litros", "litros", "cantidad", "liters")),
    ("tipo", "Tipo", ("tipo", "combustible")),
    ("tapa", "Tapa", ("tapa",)),
    ("filtracion", "Filtracion", ("filtracion", "filtracion?")),
    ("modelo_chasis", "Modelo chasis", ("modelo chasis", "chasis", "modelo")),
    ("estanque", "Estanque", ("estanque", "tanque")),
    ("llenado", "Llenado", ("llenado", "lleno")),
    ("exeso", "Exeso", ("exeso", "exceso")),
    ("odometro", "Odometro", ("odometro", "kilometraje", "km")),
    ("rut_planillero", "RUT planillero", ("rut planillero", "rut planillera", "rut planner")),
    ("nombre_planillero", "Nombre planillero", ("nombre planillero", "planillero", "planner")),
    ("rut_supervisor", "RUT supervisor", ("rut supervisor",)),
    ("nombre_supervisor", "Nombre supervisor", ("nombre supervisor", "supervisor")),
    ("rut_conductor", "RUT conductor", ("rut conductor", "rut chofer")),
    ("nombre_conductor", "Nombre conductor", ("nombre conductor", "conductor", "chofer")),
    ("surtidor", "Surtidor", ("surtidor", "dispensador", "pump")),
    ("capturador", "Capturador", ("capturador", "captura")),
    ("cargado_por", "Cargado por", ("cargado por", "usuario carga", "importado por")),
]

ALIASES_BY_FIELD: dict[str, set[str]] = {
    canonical: {_normalize_seed(alias) for alias in aliases} | {_normalize_seed(label), _normalize_seed(canonical)}
    for canonical, label, aliases in FIELD_DEFS
}
DISPLAY_BY_FIELD: dict[str, str] = {canonical: label for canonical, label, _ in FIELD_DEFS}
CANONICAL_FIELDS: list[str] = [canonical for canonical, _, _ in FIELD_DEFS]

CRITICAL_FIELDS = {"turno", "fecha", "hora", "terminal", "numero_interno", "patente", "cantidad_litros", "surtidor"}

SHIFT_RANGES = {
    "A": (0, 7),
    "B": (8, 15),
    "C": (16, 23),
}


@dataclass
class PreviewResult:
    detected_format: str
    header_row_index: int
    source_columns: list[str]
    suggested_mapping: dict[str, str]
    missing_columns: list[str]
    preview_rows: list[dict]


@dataclass
class ProcessedFile:
    raw_df: pd.DataFrame
    processed_df: pd.DataFrame
    alerts_df: pd.DataFrame
    logs_df: pd.DataFrame
    dashboard_snapshot: dict
    preview: PreviewResult


class ExcelProcessingError(Exception):
    pass


def preview_excel(payload: bytes, filename: str) -> PreviewResult:
    df, detected_format = _read_any_tabular(payload, filename)
    if df.empty:
        raise ExcelProcessingError("El archivo no contiene filas para analizar.")

    table_df, header_idx = _extract_table(df)
    source_columns = [str(col).strip() for col in table_df.columns]
    suggested_mapping = _suggest_mapping(source_columns)
    missing_columns = [DISPLAY_BY_FIELD[field] for field in CANONICAL_FIELDS if field not in suggested_mapping]

    preview_rows = (
        table_df.head(20)
        .fillna("")
        .astype(str)
        .to_dict(orient="records")
    )

    return PreviewResult(
        detected_format=detected_format,
        header_row_index=header_idx,
        source_columns=source_columns,
        suggested_mapping=suggested_mapping,
        missing_columns=missing_columns,
        preview_rows=preview_rows,
    )


def process_excel(payload: bytes, filename: str, column_mapping: dict[str, str] | None = None) -> ProcessedFile:
    preview = preview_excel(payload, filename)

    df_any, _ = _read_any_tabular(payload, filename)
    table_df, header_idx = _extract_table(df_any)

    resolved_mapping = _resolve_mapping(preview.source_columns, preview.suggested_mapping, column_mapping)

    missing_critical = [DISPLAY_BY_FIELD[field] for field in CRITICAL_FIELDS if field not in resolved_mapping]
    if missing_critical:
        raise ExcelProcessingError(
            "No se pueden mapear columnas criticas: " + ", ".join(sorted(missing_critical))
        )

    table_with_row = table_df.copy()
    table_with_row["__row_number__"] = table_with_row.index + int(header_idx) + 2

    normalized_df = _normalize_dataframe(table_df, resolved_mapping, header_idx)
    raw_df = _build_raw_dataframe(table_with_row, normalized_df)

    alerts_df, logs_df = _build_alerts_and_logs(normalized_df)
    dashboard_snapshot = build_dashboard_snapshot(normalized_df, alerts_df)

    return ProcessedFile(
        raw_df=raw_df,
        processed_df=normalized_df,
        alerts_df=alerts_df,
        logs_df=logs_df,
        dashboard_snapshot=dashboard_snapshot,
        preview=preview,
    )


def build_dashboard_snapshot(df: pd.DataFrame, alerts_df: pd.DataFrame) -> dict:
    if df.empty:
        return {
            "kpis": _empty_kpis(),
            "litros_por_dia": [],
            "cargas_por_dia": [],
            "litros_por_terminal": [],
            "cargas_por_terminal": [],
            "turno_donut": [],
            "terminal_donut": [],
            "heatmap": [],
            "top_buses_por_cargas": [],
            "top_buses_por_litros": [],
            "ranking_terminales_consumo": [],
            "ranking_surtidores": [],
            "ranking_conductores": [],
            "alertas": {"total": 0, "rojo": 0, "amarillo": 0, "gris": 0},
        }

    data = df.copy()

    total_cargas = int(len(data))
    total_litros = float(data["cantidad_litros"].fillna(0).sum())

    today_date = pd.Timestamp.now(tz=settings.timezone).date()
    litros_dia = float(data.loc[data["fecha"] == today_date, "cantidad_litros"].fillna(0).sum())

    now = pd.Timestamp.now(tz=settings.timezone)
    litros_mes = float(
        data.loc[
            (data["anio"] == int(now.year)) & (data["mes"] == int(now.month)),
            "cantidad_litros",
        ]
        .fillna(0)
        .sum()
    )

    cargas_por_dia_df = data.groupby("fecha", as_index=False).size().rename(columns={"size": "total"}).sort_values("fecha")
    litros_por_dia_df = (
        data.groupby("fecha", as_index=False)["cantidad_litros"].sum(min_count=1).fillna(0).sort_values("fecha")
    )

    prev_period_variation = _period_variation_pct(data)

    avg_cargas_dia = float(cargas_por_dia_df["total"].mean()) if not cargas_por_dia_df.empty else 0.0

    by_terminal = data.groupby("terminal", dropna=True, as_index=False).agg(
        total_cargas=("clave_unica_registro", "count"),
        litros_totales=("cantidad_litros", "sum"),
    )
    by_turno = data.groupby("turno", dropna=True, as_index=False).agg(
        total_cargas=("clave_unica_registro", "count"),
        litros_totales=("cantidad_litros", "sum"),
    )

    alerts_summary = {
        "total": int(len(alerts_df)),
        "rojo": int((alerts_df["severity"] == "rojo").sum()) if not alerts_df.empty else 0,
        "amarillo": int((alerts_df["severity"] == "amarillo").sum()) if not alerts_df.empty else 0,
        "gris": int((alerts_df["severity"] == "gris").sum()) if not alerts_df.empty else 0,
    }

    heatmap_df = (
        data.groupby(["dia_semana", "hora_numero"], as_index=False)
        .size()
        .rename(columns={"size": "total"})
        .sort_values(["dia_semana", "hora_numero"])
    )

    top_buses_cargas = (
        data.groupby(["numero_interno", "patente"], dropna=True, as_index=False)
        .size()
        .rename(columns={"size": "total_cargas"})
        .sort_values("total_cargas", ascending=False)
        .head(10)
    )

    top_buses_litros = (
        data.groupby(["numero_interno", "patente"], dropna=True, as_index=False)["cantidad_litros"]
        .sum(min_count=1)
        .fillna(0)
        .rename(columns={"cantidad_litros": "litros_totales"})
        .sort_values("litros_totales", ascending=False)
        .head(10)
    )

    ranking_surtidores = (
        data.groupby("surtidor", dropna=True, as_index=False)
        .agg(total_cargas=("clave_unica_registro", "count"), litros_totales=("cantidad_litros", "sum"))
        .sort_values(["total_cargas", "litros_totales"], ascending=False)
        .head(10)
    )

    ranking_conductores = (
        data.groupby("nombre_conductor", dropna=True, as_index=False)
        .agg(total_registros=("clave_unica_registro", "count"), litros_totales=("cantidad_litros", "sum"))
        .sort_values("total_registros", ascending=False)
        .head(10)
    )

    kpis = {
        "total_cargas": total_cargas,
        "total_litros_cargados": round(total_litros, 2),
        "litros_del_dia": round(litros_dia, 2),
        "litros_del_mes": round(litros_mes, 2),
        "litros_periodo_filtrado": round(total_litros, 2),
        "buses_unicos_atendidos": int(data["numero_interno"].dropna().nunique()),
        "terminales_activos": int(data["terminal"].dropna().nunique()),
        "surtidores_activos": int(data["surtidor"].dropna().nunique()),
        "conductores_unicos": int(data["nombre_conductor"].dropna().nunique()),
        "promedio_litros_por_carga": round(total_litros / max(total_cargas, 1), 2),
        "promedio_cargas_por_dia": round(avg_cargas_dia, 2),
        "variacion_porcentual_periodo_anterior": round(prev_period_variation, 2),
        "odometro_promedio": round(float(data["odometro"].dropna().mean()) if data["odometro"].notna().any() else 0.0, 2),
        "carga_promedio_por_terminal": round(float(by_terminal["litros_totales"].mean()) if not by_terminal.empty else 0.0, 2),
        "carga_promedio_por_turno": round(float(by_turno["litros_totales"].mean()) if not by_turno.empty else 0.0, 2),
    }

    return {
        "kpis": kpis,
        "litros_por_dia": _to_records(litros_por_dia_df, {"fecha": str}, round_cols={"cantidad_litros"}),
        "cargas_por_dia": _to_records(cargas_por_dia_df, {"fecha": str}),
        "litros_por_terminal": _to_records(by_terminal.rename(columns={"litros_totales": "litros"}), round_cols={"litros"}),
        "cargas_por_terminal": _to_records(by_terminal[["terminal", "total_cargas"]]),
        "turno_donut": _to_records(by_turno.rename(columns={"litros_totales": "litros"}), round_cols={"litros"}),
        "terminal_donut": _to_records(by_terminal.rename(columns={"litros_totales": "litros"}), round_cols={"litros"}),
        "heatmap": _to_records(heatmap_df),
        "top_buses_por_cargas": _to_records(top_buses_cargas),
        "top_buses_por_litros": _to_records(top_buses_litros, round_cols={"litros_totales"}),
        "ranking_terminales_consumo": _to_records(by_terminal.rename(columns={"litros_totales": "litros"}), round_cols={"litros"}),
        "ranking_surtidores": _to_records(ranking_surtidores, round_cols={"litros_totales"}),
        "ranking_conductores": _to_records(ranking_conductores, round_cols={"litros_totales"}),
        "alertas": alerts_summary,
    }


def _empty_kpis() -> dict:
    return {
        "total_cargas": 0,
        "total_litros_cargados": 0,
        "litros_del_dia": 0,
        "litros_del_mes": 0,
        "litros_periodo_filtrado": 0,
        "buses_unicos_atendidos": 0,
        "terminales_activos": 0,
        "surtidores_activos": 0,
        "conductores_unicos": 0,
        "promedio_litros_por_carga": 0,
        "promedio_cargas_por_dia": 0,
        "variacion_porcentual_periodo_anterior": 0,
        "odometro_promedio": 0,
        "carga_promedio_por_terminal": 0,
        "carga_promedio_por_turno": 0,
    }


def _read_any_tabular(payload: bytes, filename: str) -> tuple[pd.DataFrame, str]:
    detected = detect_real_file_type(payload, filename)

    if detected == "xlsx":
        df = pd.read_excel(BytesIO(payload), header=None, engine="openpyxl", dtype=str)
        return df, detected

    if detected == "xls":
        df = pd.read_excel(BytesIO(payload), header=None, engine="xlrd", dtype=str)
        return df, detected

    if detected == "xls_html":
        text = _decode_bytes(payload)
        tables = pd.read_html(StringIO(text), header=None)
        if not tables:
            raise ExcelProcessingError("No se encontro ninguna tabla HTML en el archivo .xls.")
        df = max(tables, key=lambda x: x.shape[0] * x.shape[1]).copy()
        return df, detected

    raise ExcelProcessingError("Formato de archivo no soportado.")


def detect_real_file_type(payload: bytes, filename: str) -> str:
    head = payload[:4096]
    filename_lower = (filename or "").lower()

    if head.startswith(b"PK"):
        return "xlsx"

    if head.startswith(bytes.fromhex("D0CF11E0A1B11AE1")):
        return "xls"

    head_text = _decode_bytes(head).lower().strip()
    if "<html" in head_text or "<table" in head_text:
        return "xls_html"

    if filename_lower.endswith(".xlsx"):
        return "xlsx"
    if filename_lower.endswith(".xls"):
        return "xls"

    return "unknown"


def _extract_table(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    if df.empty:
        return df, 0

    header_idx = _detect_header_row(df)
    header_values = [str(v).strip() for v in df.iloc[header_idx].tolist()]
    clean_columns: list[str] = []
    for i, raw_col in enumerate(header_values):
        col = raw_col if raw_col else f"column_{i + 1}"
        if col.lower().startswith("unnamed"):
            col = f"column_{i + 1}"
        clean_columns.append(col)

    table_df = df.iloc[header_idx + 1 :].copy()
    table_df.columns = clean_columns
    table_df = table_df.dropna(how="all")
    table_df = table_df.reset_index(drop=True)
    return table_df, int(header_idx)


def _detect_header_row(df: pd.DataFrame) -> int:
    max_scan = min(len(df), 30)
    best_idx = 0
    best_score = -1

    for idx in range(max_scan):
        values = [str(v).strip() for v in df.iloc[idx].tolist()]
        normalized_values = {_normalize_text(v) for v in values if v}
        score = 0
        for field_aliases in ALIASES_BY_FIELD.values():
            if normalized_values.intersection(field_aliases):
                score += 1
        if score > best_score:
            best_idx = idx
            best_score = score

    return int(best_idx)


def _suggest_mapping(source_columns: list[str]) -> dict[str, str]:
    source_norm = {col: _normalize_text(col) for col in source_columns}
    mapping: dict[str, str] = {}

    for field in CANONICAL_FIELDS:
        aliases = ALIASES_BY_FIELD[field]

        exact = next((col for col, norm in source_norm.items() if norm in aliases), None)
        if exact:
            mapping[field] = exact
            continue

        contains = next(
            (
                col
                for col, norm in source_norm.items()
                if any(alias and (alias in norm or norm in alias) for alias in aliases)
            ),
            None,
        )
        if contains:
            mapping[field] = contains

    return mapping


def _resolve_mapping(
    source_columns: list[str],
    suggested_mapping: dict[str, str],
    manual_mapping: dict[str, str] | None,
) -> dict[str, str]:
    mapping = dict(suggested_mapping)
    if not manual_mapping:
        return mapping

    source_set = set(source_columns)

    for k, v in manual_mapping.items():
        if k in CANONICAL_FIELDS and v in source_set:
            mapping[k] = v
        elif k in source_set and v in CANONICAL_FIELDS:
            mapping[v] = k

    return mapping


def _normalize_dataframe(table_df: pd.DataFrame, mapping: dict[str, str], header_idx: int) -> pd.DataFrame:
    normalized = pd.DataFrame(index=table_df.index)

    for field in CANONICAL_FIELDS:
        source_col = mapping.get(field)
        if source_col and source_col in table_df.columns:
            normalized[field] = table_df[source_col]
        else:
            normalized[field] = pd.NA

    normalized["row_number"] = table_df.index + int(header_idx) + 2

    for text_col in [
        "turno",
        "terminal",
        "numero_interno",
        "patente",
        "tipo",
        "tapa",
        "filtracion",
        "modelo_chasis",
        "estanque",
        "llenado",
        "exeso",
        "nombre_planillero",
        "nombre_supervisor",
        "nombre_conductor",
        "surtidor",
        "capturador",
        "cargado_por",
    ]:
        normalized[text_col] = normalized[text_col].map(_sanitize_text)

    normalized["patente"] = normalized["patente"].map(_normalize_patente)

    for rut_col in ["rut_planillero", "rut_supervisor", "rut_conductor"]:
        normalized[rut_col] = normalized[rut_col].map(_normalize_rut)

    normalized["cantidad_litros"] = normalized["cantidad_litros"].map(_to_float)
    normalized["odometro"] = normalized["odometro"].map(_to_float)

    date_series = pd.to_datetime(normalized["fecha"], errors="coerce", dayfirst=True)
    normalized["fecha"] = date_series.dt.date

    normalized["hora"] = normalized["hora"].map(_normalize_time_string)

    datetime_str = normalized["fecha"].astype("string") + " " + normalized["hora"].fillna("00:00")
    dt_series = pd.to_datetime(datetime_str, errors="coerce", dayfirst=False)
    if getattr(dt_series.dt, "tz", None) is None:
        normalized["datetime_carga"] = dt_series.dt.tz_localize(settings.timezone, nonexistent="shift_forward", ambiguous="NaT")
    else:
        normalized["datetime_carga"] = dt_series.dt.tz_convert(settings.timezone)

    normalized["anio"] = normalized["datetime_carga"].dt.year.astype("Int64")
    normalized["mes"] = normalized["datetime_carga"].dt.month.astype("Int64")
    normalized["nombre_mes"] = _month_name_es(normalized["datetime_carga"])
    normalized["semana"] = normalized["datetime_carga"].dt.isocalendar().week.astype("Int64")
    normalized["dia"] = normalized["datetime_carga"].dt.day.astype("Int64")
    normalized["dia_semana"] = _day_name_es(normalized["datetime_carga"])
    normalized["hora_numero"] = normalized["datetime_carga"].dt.hour.astype("Int64")
    normalized["franja_horaria"] = normalized["hora_numero"].map(_hour_bucket)
    normalized["periodo"] = normalized["datetime_carga"].dt.strftime("%Y-%m")

    normalized["litros_redondeados"] = normalized["cantidad_litros"].round().astype("Int64")

    normalized["clave_unica_registro"] = normalized.apply(_build_unique_key, axis=1)
    normalized["registro_duplicado"] = normalized.duplicated(subset=["clave_unica_registro"], keep=False)

    normalized["alerta_consumo"] = (
        (normalized["cantidad_litros"].notna())
        & (
            (normalized["cantidad_litros"] < settings.litros_min_validos)
            | (normalized["cantidad_litros"] > settings.litros_max_validos)
        )
    )

    normalized = normalized.sort_values(["numero_interno", "datetime_carga"], na_position="last").reset_index(drop=True)

    odometer_diff = normalized.groupby("numero_interno", dropna=False)["odometro"].diff()
    normalized["alerta_odometro"] = (odometer_diff < 0).fillna(False)

    day_gap = normalized.groupby("numero_interno", dropna=False)["datetime_carga"].diff().dt.total_seconds() / 86400
    normalized["dias_desde_ultima_carga"] = day_gap.round().astype("Int64")

    normalized["out_of_shift"] = normalized.apply(_is_out_of_shift, axis=1)

    normalized["validation_flags"] = normalized.apply(_build_validation_flags, axis=1)
    normalized["data_quality_score"] = normalized.apply(_quality_score, axis=1)

    return normalized


def _build_raw_dataframe(source_df: pd.DataFrame, normalized_df: pd.DataFrame) -> pd.DataFrame:
    records: list[dict] = []

    source_by_row: dict[int, dict] = {}
    for _, source_row in source_df.iterrows():
        row_number = source_row.get("__row_number__")
        if pd.isna(row_number):
            continue
        row_number_int = int(row_number)
        raw_values = source_row.drop(labels=["__row_number__"])
        raw_payload = raw_values.where(pd.notnull(raw_values), None).to_dict()
        source_by_row[row_number_int] = raw_payload

    for idx in range(len(normalized_df)):
        row_number = normalized_df.iloc[idx].get("row_number")
        row_number_int = int(row_number) if pd.notna(row_number) else None

        source_row = source_by_row.get(row_number_int, {})
        normalized_row = normalized_df.iloc[idx].where(pd.notnull(normalized_df.iloc[idx]), None).to_dict()

        source_payload = json.dumps(source_row, ensure_ascii=True, default=str)
        normalized_payload = json.dumps(normalized_row, ensure_ascii=True, default=str)

        records.append(
            {
                "row_number": row_number_int,
                "source_payload": source_payload,
                "normalized_payload": normalized_payload,
            }
        )

    return pd.DataFrame(records, columns=["row_number", "source_payload", "normalized_payload"])


def _build_alerts_and_logs(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    alerts: list[dict] = []
    logs: list[dict] = []

    for _, row in df.iterrows():
        row_index = int(row["row_number"]) if pd.notna(row["row_number"]) else None
        key = str(row["clave_unica_registro"])

        missing_critical = [field for field in CRITICAL_FIELDS if _is_missing(row.get(field))]
        if missing_critical:
            missing_labels = ", ".join(sorted(DISPLAY_BY_FIELD[f] for f in missing_critical))
            logs.append(
                {
                    "level": "error",
                    "code": "CRITICAL_NULLS",
                    "message": f"Campos criticos vacios: {missing_labels}",
                    "row_index": row_index,
                }
            )
            alerts.append(
                {
                    "row_number": row_index,
                    "clave_unica_registro": key,
                    "type": "CAMPOS_CRITICOS_VACIOS",
                    "severity": "rojo",
                    "message": "Registro con campos criticos vacios.",
                }
            )

        patente = row.get("patente")
        if patente and not _is_valid_patente(str(patente)):
            logs.append(
                {
                    "level": "warning",
                    "code": "INVALID_PATENTE",
                    "message": "Patente invalida o inconsistente.",
                    "row_index": row_index,
                }
            )
            alerts.append(
                {
                    "row_number": row_index,
                    "clave_unica_registro": key,
                    "type": "PATENTE_INVALIDA",
                    "severity": "amarillo",
                    "message": "Patente fuera de formato esperado.",
                }
            )

        if _is_missing(row.get("numero_interno")):
            alerts.append(
                {
                    "row_number": row_index,
                    "clave_unica_registro": key,
                    "type": "NUMERO_INTERNO_FALTANTE",
                    "severity": "rojo",
                    "message": "Numero interno faltante.",
                }
            )

        if bool(row.get("registro_duplicado")):
            alerts.append(
                {
                    "row_number": row_index,
                    "clave_unica_registro": key,
                    "type": "REGISTRO_DUPLICADO",
                    "severity": "amarillo",
                    "message": "Registro duplicado detectado en el archivo.",
                }
            )

        if bool(row.get("alerta_odometro")):
            alerts.append(
                {
                    "row_number": row_index,
                    "clave_unica_registro": key,
                    "type": "ODOMETRO_INCONSISTENTE",
                    "severity": "rojo",
                    "message": "Odometro menor al registro anterior del bus.",
                }
            )

        if bool(row.get("alerta_consumo")):
            alerts.append(
                {
                    "row_number": row_index,
                    "clave_unica_registro": key,
                    "type": "LITROS_FUERA_DE_RANGO",
                    "severity": "amarillo",
                    "message": "Cantidad de litros fuera de rango esperado.",
                }
            )

        if bool(row.get("out_of_shift")):
            alerts.append(
                {
                    "row_number": row_index,
                    "clave_unica_registro": key,
                    "type": "FUERA_DE_TURNO",
                    "severity": "amarillo",
                    "message": "Registro fuera de la franja horaria del turno.",
                }
            )

    alerts_df = pd.DataFrame(alerts, columns=["row_number", "clave_unica_registro", "type", "severity", "message"])
    logs_df = pd.DataFrame(logs, columns=["level", "code", "message", "row_index"])
    return alerts_df, logs_df


def _build_unique_key(row: pd.Series) -> str:
    raw = "|".join(
        [
            str(row.get("turno") or ""),
            str(row.get("terminal") or ""),
            str(row.get("numero_interno") or ""),
            str(row.get("patente") or ""),
            str(row.get("datetime_carga") or ""),
            str(row.get("cantidad_litros") or ""),
            str(row.get("surtidor") or ""),
        ]
    )
    return sha256(raw.encode("utf-8")).hexdigest()


def _build_validation_flags(row: pd.Series) -> str:
    flags: list[str] = []
    if bool(row.get("registro_duplicado")):
        flags.append("duplicado")
    if bool(row.get("alerta_odometro")):
        flags.append("odometro_inconsistente")
    if bool(row.get("alerta_consumo")):
        flags.append("consumo_fuera_rango")
    if bool(row.get("out_of_shift")):
        flags.append("fuera_turno")

    for field in sorted(CRITICAL_FIELDS):
        if _is_missing(row.get(field)):
            flags.append(f"nulo_{field}")

    return ";".join(flags)


def _quality_score(row: pd.Series) -> float:
    score = 100.0
    for field in CRITICAL_FIELDS:
        if _is_missing(row.get(field)):
            score -= 12

    if bool(row.get("registro_duplicado")):
        score -= 15
    if bool(row.get("alerta_odometro")):
        score -= 20
    if bool(row.get("alerta_consumo")):
        score -= 10
    if bool(row.get("out_of_shift")):
        score -= 8

    patente = row.get("patente")
    if patente and not _is_valid_patente(str(patente)):
        score -= 10

    return float(max(score, 0))


def _is_out_of_shift(row: pd.Series) -> bool:
    turno = _sanitize_text(row.get("turno"))
    if not turno:
        return False
    hour = row.get("hora_numero")
    if pd.isna(hour):
        return False

    normalized_turno = turno.upper()
    if normalized_turno.startswith("TURNO"):
        normalized_turno = normalized_turno.replace("TURNO", "").strip()

    slot = SHIFT_RANGES.get(normalized_turno)
    if not slot:
        return False

    start, end = slot
    return not (start <= int(hour) <= end)


def _period_variation_pct(df: pd.DataFrame) -> float:
    if df.empty or df["datetime_carga"].isna().all():
        return 0.0

    min_dt = df["datetime_carga"].min()
    max_dt = df["datetime_carga"].max()
    if pd.isna(min_dt) or pd.isna(max_dt):
        return 0.0

    span_seconds = max((max_dt - min_dt).total_seconds(), 86400.0)
    prev_start = min_dt - pd.to_timedelta(span_seconds, unit="s")
    prev_end = min_dt

    current_total = float(df["cantidad_litros"].fillna(0).sum())

    prev_mask = (df["datetime_carga"] >= prev_start) & (df["datetime_carga"] < prev_end)
    prev_total = float(df.loc[prev_mask, "cantidad_litros"].fillna(0).sum())

    if prev_total <= 0:
        return 0.0
    return ((current_total - prev_total) / prev_total) * 100.0


def _to_records(df: pd.DataFrame, formatters: dict[str, callable] | None = None, round_cols: set[str] | None = None) -> list[dict]:
    if df.empty:
        return []

    out = df.copy()
    if round_cols:
        for col in round_cols:
            if col in out.columns:
                out[col] = out[col].fillna(0).round(2)

    if formatters:
        for col, fmt in formatters.items():
            if col in out.columns:
                out[col] = out[col].map(lambda v: fmt(v) if pd.notna(v) else None)

    return out.where(pd.notnull(out), None).to_dict(orient="records")


def _sanitize_text(value: object) -> str | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    text = str(value).strip()
    text = re.sub(r"\s+", " ", text)
    if not text or text.lower() in {"nan", "none", "null", "<na>"}:
        return None
    return text.upper()


def _normalize_text(value: object) -> str:
    return _normalize_seed(value)


def _normalize_patente(value: object) -> str | None:
    text = _sanitize_text(value)
    if not text:
        return None
    text = re.sub(r"[^A-Z0-9]", "", text)
    return text or None


def _normalize_rut(value: object) -> str | None:
    text = _sanitize_text(value)
    if not text:
        return None
    text = text.replace(".", "").replace("-", "")
    text = re.sub(r"[^A-Z0-9]", "", text)
    return text or None


def _to_float(value: object) -> float | None:
    if value is None:
        return None
    text = str(value).strip().replace(" ", "")
    if not text:
        return None

    if "," in text and "." in text:
        text = text.replace(".", "").replace(",", ".")
    elif "," in text:
        text = text.replace(",", ".")

    try:
        return float(text)
    except ValueError:
        return None


def _normalize_time_string(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None

    dt = pd.to_datetime(text, errors="coerce")
    if pd.isna(dt):
        return None
    return dt.strftime("%H:%M:%S")


def _decode_bytes(payload: bytes) -> str:
    for encoding in ("utf-8", "latin-1", "cp1252"):
        try:
            return payload.decode(encoding)
        except UnicodeDecodeError:
            continue
    return payload.decode("utf-8", errors="ignore")


def _is_valid_patente(patente: str) -> bool:
    return bool(re.fullmatch(r"[A-Z0-9]{5,8}", patente))


def _is_missing(value: object) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    return bool(pd.isna(value))


def _month_name_es(series: pd.Series) -> pd.Series:
    try:
        return series.dt.month_name(locale="es_ES").str.upper()
    except Exception:
        fallback = {
            1: "ENERO",
            2: "FEBRERO",
            3: "MARZO",
            4: "ABRIL",
            5: "MAYO",
            6: "JUNIO",
            7: "JULIO",
            8: "AGOSTO",
            9: "SEPTIEMBRE",
            10: "OCTUBRE",
            11: "NOVIEMBRE",
            12: "DICIEMBRE",
        }
        return series.dt.month.map(fallback)


def _day_name_es(series: pd.Series) -> pd.Series:
    try:
        return series.dt.day_name(locale="es_ES").str.upper()
    except Exception:
        fallback = {
            0: "LUNES",
            1: "MARTES",
            2: "MIERCOLES",
            3: "JUEVES",
            4: "VIERNES",
            5: "SABADO",
            6: "DOMINGO",
        }
        return series.dt.dayofweek.map(fallback)


def _hour_bucket(hour: object) -> str | None:
    if hour is None or pd.isna(hour):
        return None
    h = int(hour)
    if 0 <= h <= 5:
        return "MADRUGADA"
    if 6 <= h <= 11:
        return "MANANA"
    if 12 <= h <= 17:
        return "TARDE"
    return "NOCHE"
