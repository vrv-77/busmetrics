from io import BytesIO

import pandas as pd

from app.services.excel_processor import preview_excel, process_excel


def build_excel_bytes() -> bytes:
    df = pd.DataFrame(
        {
            "Turno": ["A", "B"],
            "Fecha": ["18-03-2026", "18-03-2026"],
            "Hora": ["06:30", "13:15"],
            "Terminal": ["Terminal Norte", "Terminal Norte"],
            "Numero interno": ["B-101", "B-102"],
            "Patente": ["ABCD12", "EFGH34"],
            "Cantidad litros": [120, 95],
            "Tipo": ["DIESEL", "DIESEL"],
            "Tapa": ["OK", "OK"],
            "Filtracion": ["NO", "NO"],
            "Modelo chasis": ["Volvo", "Volvo"],
            "Estanque": ["Principal", "Principal"],
            "Llenado": ["Completo", "Parcial"],
            "Exeso": ["0", "0"],
            "Odometro": [120000, 120500],
            "RUT planillero": ["12.345.678-5", "12.345.678-5"],
            "Nombre planillero": ["Ana", "Ana"],
            "RUT supervisor": ["11.111.111-1", "11.111.111-1"],
            "Nombre supervisor": ["Carlos", "Carlos"],
            "RUT conductor": ["22.222.222-2", "33.333.333-3"],
            "Nombre conductor": ["Pedro", "Luis"],
            "Surtidor": ["S1", "S2"],
            "Capturador": ["CAP-01", "CAP-02"],
            "Cargado por": ["OPERADOR", "OPERADOR"],
        }
    )

    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, startrow=2)
    return buffer.getvalue()


def build_html_xls_bytes() -> bytes:
    html = """
    <html><body>
      <table>
        <tr><td>Turno</td><td>Fecha</td><td>Hora</td><td>Terminal</td><td>Numero interno</td><td>Patente</td><td>Cantidad litros</td><td>Surtidor</td></tr>
        <tr><td>C</td><td>18-03-2026</td><td>21:10</td><td>Terminal Sur</td><td>B-200</td><td>IJKL56</td><td>140</td><td>S3</td></tr>
      </table>
    </body></html>
    """
    return html.encode("utf-8")


def test_excel_processor_generates_derived_columns() -> None:
    payload = build_excel_bytes()
    result = process_excel(payload, "cargas.xlsx")

    assert len(result.processed_df) == 2
    assert "datetime_carga" in result.processed_df.columns
    assert "clave_unica_registro" in result.processed_df.columns
    assert "alerta_consumo" in result.processed_df.columns
    assert result.dashboard_snapshot["kpis"]["total_cargas"] == 2


def test_excel_processor_detects_html_xls_and_generates_preview() -> None:
    payload = build_html_xls_bytes()

    preview = preview_excel(payload, "cargas.xls")
    assert preview.detected_format == "xls_html"
    assert "Turno" in preview.source_columns

    result = process_excel(payload, "cargas.xls")
    assert len(result.processed_df) == 1
    assert result.processed_df.iloc[0]["turno"] == "C"
