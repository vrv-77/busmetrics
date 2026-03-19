from __future__ import annotations

from io import BytesIO
from uuid import uuid4

import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.analytics_service import (
    AnalyticsFilters,
    get_alerts,
    get_bus_metrics,
    get_dashboard_data,
    get_dispenser_metrics,
    get_operations_table,
    get_people_metrics,
    get_quality_metrics,
    get_shift_metrics,
    get_terminal_metrics,
)


async def build_report_bytes(
    db: AsyncSession,
    scope: str,
    fmt: str,
    filters: AnalyticsFilters,
) -> tuple[str, str, bytes]:
    payload_df = await _build_scope_dataframe(db, scope, filters)

    if fmt == "csv":
        return _to_csv(scope, payload_df)
    if fmt == "excel":
        return _to_excel(scope, payload_df)
    if fmt == "pdf":
        return _to_pdf(scope, payload_df)

    raise ValueError("Formato de exportacion no soportado")


async def _build_scope_dataframe(db: AsyncSession, scope: str, filters: AnalyticsFilters) -> pd.DataFrame:
    if scope == "terminals":
        return pd.DataFrame(await get_terminal_metrics(db, filters))
    if scope == "shifts":
        return pd.DataFrame(await get_shift_metrics(db, filters))
    if scope == "dispensers":
        return pd.DataFrame(await get_dispenser_metrics(db, filters))
    if scope == "buses":
        return pd.DataFrame(await get_bus_metrics(db, filters))
    if scope == "alerts":
        return pd.DataFrame(await get_alerts(db, filters, limit=5000))
    if scope == "quality":
        quality = await get_quality_metrics(db, filters)
        rows = [{"metrica": k, "valor": v} for k, v in quality.items() if not isinstance(v, list)]
        return pd.DataFrame(rows)
    if scope == "people":
        people = await get_people_metrics(db, filters)
        return pd.concat(
            [
                pd.DataFrame(people.get("conductores", [])).assign(categoria="conductores"),
                pd.DataFrame(people.get("supervisores", [])).assign(categoria="supervisores"),
                pd.DataFrame(people.get("planilleros", [])).assign(categoria="planilleros"),
            ],
            ignore_index=True,
        )
    if scope == "operations":
        table = await get_operations_table(db, filters, page=1, page_size=5000)
        return pd.DataFrame(table.get("rows", []))
    if scope == "dashboard":
        dashboard = await get_dashboard_data(db, filters)
        rows = [{"metrica": k, "valor": v} for k, v in dashboard["kpis"].items()]
        return pd.DataFrame(rows)

    raise ValueError("Scope de reporte no soportado")


def _to_csv(scope: str, df: pd.DataFrame) -> tuple[str, str, bytes]:
    content = df.to_csv(index=False).encode("utf-8")
    return f"{scope}-{uuid4().hex[:8]}.csv", "text/csv", content


def _to_excel(scope: str, df: pd.DataFrame) -> tuple[str, str, bytes]:
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="reporte", index=False)
    return (
        f"{scope}-{uuid4().hex[:8]}.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        buffer.getvalue(),
    )


def _to_pdf(scope: str, df: pd.DataFrame) -> tuple[str, str, bytes]:
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    pdf.setTitle(f"Reporte {scope}")
    pdf.setFont("Helvetica-Bold", 15)
    pdf.drawString(40, height - 40, f"Reporte Ejecutivo - {scope.title()}")

    pdf.setFont("Helvetica", 10)
    y = height - 80

    if df.empty:
        pdf.drawString(40, y, "Sin datos para el filtro seleccionado")
    else:
        preview_df = df.head(24).copy()
        text = pdf.beginText(40, y)
        text.setFont("Helvetica", 8)
        text.textLine("Vista resumida (primeras 24 filas)")
        text.textLine("")

        text.textLine(" | ".join(str(c) for c in preview_df.columns))
        text.textLine("-" * 120)
        for _, row in preview_df.iterrows():
            serialized = " | ".join(str(v)[:40] for v in row.values)
            text.textLine(serialized)
            if text.getY() < 70:
                pdf.drawText(text)
                pdf.showPage()
                text = pdf.beginText(40, height - 40)
                text.setFont("Helvetica", 8)

        pdf.drawText(text)

    pdf.showPage()
    pdf.save()

    return f"{scope}-{uuid4().hex[:8]}.pdf", "application/pdf", buffer.getvalue()
