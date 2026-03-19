"use client"

import { useState } from "react"
import { Download, FileSpreadsheet, FileType2 } from "lucide-react"

import { FiltersPanel } from "@/components/dashboard/filters-panel"
import { PageHeader } from "@/components/layout/page-header"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Select } from "@/components/ui/select"
import { getErrorMessage } from "@/lib/errors"
import { useExportReport } from "@/lib/hooks"
import { useFiltersStore } from "@/store/useFiltersStore"

function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement("a")
  anchor.href = url
  anchor.download = filename
  anchor.click()
  URL.revokeObjectURL(url)
}

export default function ReportsPage() {
  const [scope, setScope] = useState("dashboard")
  const filters = useFiltersStore((state) => ({
    file_id: state.file_id,
    terminal: state.terminal,
    turno: state.turno,
    patente: state.patente,
    numero_interno: state.numero_interno,
    conductor: state.conductor,
    supervisor: state.supervisor,
    planillero: state.planillero,
    surtidor: state.surtidor,
    search: state.search,
    date_from: state.date_from,
    date_to: state.date_to,
  }))

  const exportMutation = useExportReport()

  const onExport = async (format: "csv" | "excel" | "pdf") => {
    const result = await exportMutation.mutateAsync({ scope, format, filters })
    downloadBlob(result.blob, result.filename)
  }

  return (
    <div className="space-y-4">
      <PageHeader title="Reportes" subtitle="Exportacion de metricas operacionales en Excel, CSV y PDF ejecutivo" />
      <FiltersPanel />

      <Card>
        <CardHeader>
          <CardTitle>Exportador de Reportes</CardTitle>
          <CardDescription>
            Selecciona el alcance del reporte y descarga el formato requerido para gestion operativa o comite ejecutivo.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="max-w-xs">
            <label className="mb-1 block text-sm text-muted-foreground">Alcance</label>
            <Select value={scope} onChange={(e) => setScope(e.target.value)}>
              <option value="dashboard">Dashboard ejecutivo</option>
              <option value="operations">Operacion detallada</option>
              <option value="terminals">Terminales</option>
              <option value="shifts">Turnos</option>
              <option value="dispensers">Surtidores</option>
              <option value="buses">Buses</option>
              <option value="people">Personas</option>
              <option value="quality">Calidad de datos</option>
              <option value="alerts">Alertas</option>
            </Select>
          </div>

          <div className="flex flex-wrap gap-2">
            <Button onClick={() => onExport("excel")} disabled={exportMutation.isPending}>
              <FileSpreadsheet className="mr-2 h-4 w-4" />
              Exportar Excel
            </Button>
            <Button variant="secondary" onClick={() => onExport("csv")} disabled={exportMutation.isPending}>
              <Download className="mr-2 h-4 w-4" />
              Exportar CSV
            </Button>
            <Button variant="outline" onClick={() => onExport("pdf")} disabled={exportMutation.isPending}>
              <FileType2 className="mr-2 h-4 w-4" />
              Exportar PDF
            </Button>
          </div>

          {exportMutation.isError ? <p className="text-sm text-rose-300">Error: {getErrorMessage(exportMutation.error)}</p> : null}
        </CardContent>
      </Card>
    </div>
  )
}
