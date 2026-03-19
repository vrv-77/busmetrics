"use client"

import { useState } from "react"

import { FiltersPanel } from "@/components/dashboard/filters-panel"
import { PageHeader } from "@/components/layout/page-header"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { getErrorMessage } from "@/lib/errors"
import { useOperations } from "@/lib/hooks"
import { useFiltersStore } from "@/store/useFiltersStore"

const COLUMNS = [
  "datetime_carga",
  "turno",
  "terminal",
  "numero_interno",
  "patente",
  "cantidad_litros",
  "odometro",
  "nombre_conductor",
  "nombre_supervisor",
  "nombre_planillero",
  "surtidor",
  "capturador",
  "imported_user",
]

export default function OperationsPage() {
  const [page, setPage] = useState(1)

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

  const operationsQuery = useOperations(filters, {
    page,
    page_size: 50,
    sort_by: "datetime_carga",
    sort_dir: "desc",
  })

  const data = operationsQuery.data

  return (
    <div className="space-y-4">
      <PageHeader title="Dashboard Operacional" subtitle="Tabla detallada con filtros avanzados, orden y paginacion" />

      <FiltersPanel />

      <Card>
        <CardHeader>
          <CardTitle>Registros de Carga</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {operationsQuery.isLoading ? (
            <p className="text-sm text-muted-foreground">Cargando registros...</p>
          ) : operationsQuery.isError ? (
            <p className="text-sm text-rose-300">Error: {getErrorMessage(operationsQuery.error)}</p>
          ) : (
            <>
              <div className="overflow-x-auto rounded-md border border-border/70">
                <Table>
                  <TableHeader>
                    <TableRow>
                      {COLUMNS.map((column) => (
                        <TableHead key={column}>{column}</TableHead>
                      ))}
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {(data?.rows ?? []).map((row, idx) => (
                      <TableRow key={idx}>
                        {COLUMNS.map((column) => (
                          <TableCell key={`${idx}-${column}`}>{String((row[column] ?? "-") as string)}</TableCell>
                        ))}
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>

              <div className="flex items-center justify-between">
                <p className="text-sm text-muted-foreground">
                  Total registros: {data?.total ?? 0} | Pagina {data?.page ?? 1}
                </p>
                <div className="flex gap-2">
                  <Button variant="outline" disabled={page <= 1} onClick={() => setPage((p) => Math.max(1, p - 1))}>
                    Anterior
                  </Button>
                  <Button
                    variant="outline"
                    disabled={Boolean(data && data.page * data.page_size >= data.total)}
                    onClick={() => setPage((p) => p + 1)}
                  >
                    Siguiente
                  </Button>
                </div>
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
