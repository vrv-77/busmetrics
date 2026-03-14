"use client"

import { Download, FileSpreadsheet, FileType2 } from "lucide-react"

import { FiltersPanel } from "@/components/dashboard/filters-panel"
import { PageHeader } from "@/components/layout/page-header"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Select } from "@/components/ui/select"
import { useExportReport } from "@/lib/hooks"
import { useFiltersStore } from "@/store/useFiltersStore"
import { useState } from "react"

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
    estacion: state.estacion,
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
      <PageHeader title="Reportes" subtitle="Exportación de métricas operacionales en Excel, CSV y PDF ejecutivo" />
      <FiltersPanel />

      <Card>
        <CardHeader>
          <CardTitle>Exportador de Reportes</CardTitle>
          <CardDescription>Selecciona el alcance del reporte y descarga el formato requerido para gestión o directorio.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="max-w-xs">
            <label className="mb-1 block text-sm text-muted-foreground">Alcance</label>
            <Select value={scope} onChange={(e) => setScope(e.target.value)}>
              <option value="dashboard">Dashboard Ejecutivo</option>
              <option value="stations">Estaciones</option>
              <option value="chargers">Cargadores</option>
              <option value="buses">Buses</option>
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

          {exportMutation.isError ? <p className="text-sm text-rose-300">Error: {exportMutation.error.message}</p> : null}
        </CardContent>
      </Card>
    </div>
  )
}
