"use client"

import { FiltersPanel } from "@/components/dashboard/filters-panel"
import { SeverityBadge } from "@/components/dashboard/severity-badge"
import { PageHeader } from "@/components/layout/page-header"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { getErrorMessage } from "@/lib/errors"
import { useAlerts } from "@/lib/hooks"
import { useFiltersStore } from "@/store/useFiltersStore"

export default function AlertsPage() {
  const filters = useFiltersStore((state) => ({
    file_id: state.file_id,
    estacion: state.estacion,
    date_from: state.date_from,
    date_to: state.date_to,
  }))

  const alertsQuery = useAlerts(filters)

  return (
    <div className="space-y-4">
      <PageHeader title="Alertas Operacionales" subtitle="Eventos críticos, advertencias e incompletos" />
      <FiltersPanel />

      <Card>
        <CardHeader>
          <CardTitle>Listado de Alertas</CardTitle>
        </CardHeader>
        <CardContent>
          {alertsQuery.isLoading ? (
            <p className="text-sm text-muted-foreground">Cargando alertas...</p>
          ) : alertsQuery.isError ? (
            <p className="text-sm text-rose-300">Error: {getErrorMessage(alertsQuery.error)}</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Fecha</TableHead>
                  <TableHead>Tipo</TableHead>
                  <TableHead>Severidad</TableHead>
                  <TableHead>Mensaje</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {(alertsQuery.data ?? []).map((item) => (
                  <TableRow key={item.id}>
                    <TableCell>{new Date(item.created_at).toLocaleString()}</TableCell>
                    <TableCell>{item.type}</TableCell>
                    <TableCell>
                      <SeverityBadge severity={item.severity} />
                    </TableCell>
                    <TableCell>{item.message}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
