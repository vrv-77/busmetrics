from io import BytesIO

import pandas as pd

from app.services.excel_processor import process_excel


REQUIRED_COLS = {
    "ID": [1, 2],
    "INICIO (UTC+00:00)": ["2026-01-01T12:00:00Z", "2026-01-01T13:00:00Z"],
    "T\u00c9RMINO (UTC+00:00)": ["2026-01-01T12:45:00Z", None],
    "ACTIVO": ["Electrolinera A", "Electrolinera A"],
    "CARGADOR": ["C1", "C1"],
    "CONECTOR": ["CCS2", "CCS2"],
    "VEH\u00cdCULO": ["BUS-01", "BUS-02"],
    "SOC INICIAL (%)": [15, 40],
    "SOC FINAL (%)": [65, 80],
    "SOH (%)": [98, 97],
    "ENERGIA CARGADA (kWh)": [120, 85],
    "POTENCIA PROMEDIO (kW)": [160, 140],
    "POTENCIA M\u00c1XIMA (kW)": [220, 210],
    "RFID DE INICIO": ["R1", "R2"],
    "RFID DE T\u00c9RMINO": ["R1", "R2"],
    "OD\u00d3METRO (km)": [120000, 121000],
}


def build_excel_bytes() -> bytes:
    df = pd.DataFrame(REQUIRED_COLS)
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, startrow=2)
    return buffer.getvalue()


def test_excel_processor_generates_calculated_columns() -> None:
    payload = build_excel_bytes()
    result = process_excel(payload)

    assert len(result.sessions_df) == 2
    assert "duracion_min" in result.sessions_df.columns
    assert "duracion_horas" in result.sessions_df.columns
    assert "sesion_incompleta" in result.sessions_df.columns
    assert result.sessions_df["sesion_incompleta"].tolist() == [False, True]
    assert result.sessions_df["alerta_soc_bajo"].tolist() == [True, False]


def test_excel_processor_creates_alerts_and_kpis() -> None:
    payload = build_excel_bytes()
    result = process_excel(payload)

    assert len(result.alerts_df) >= 2
    assert result.dashboard_snapshot["kpis"]["total_sesiones"] == 2
    assert result.dashboard_snapshot["kpis"]["alertas_criticas"] >= 1
