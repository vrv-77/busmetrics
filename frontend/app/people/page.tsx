"use client"

import { FiltersPanel } from "@/components/dashboard/filters-panel"
import { SimpleTable } from "@/components/dashboard/simple-table"
import { PageHeader } from "@/components/layout/page-header"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { getErrorMessage } from "@/lib/errors"
import { usePeople } from "@/lib/hooks"
import { useFiltersStore } from "@/store/useFiltersStore"

export default function PeoplePage() {
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

  const peopleQuery = usePeople(filters)
  const people = peopleQuery.data

  return (
    <div className="space-y-4">
      <PageHeader title="Analisis por Personas" subtitle="Conductores, supervisores y planilleros con mayor actividad" />
      <FiltersPanel />

      {peopleQuery.isLoading ? (
        <Card>
          <CardContent className="p-6 text-sm text-muted-foreground">Cargando analisis de personas...</CardContent>
        </Card>
      ) : peopleQuery.isError ? (
        <Card>
          <CardContent className="p-6 text-sm text-rose-300">Error: {getErrorMessage(peopleQuery.error)}</CardContent>
        </Card>
      ) : (
        <section className="grid gap-4 lg:grid-cols-3">
          <Card>
            <CardHeader>
              <CardTitle>Conductores</CardTitle>
            </CardHeader>
            <CardContent>
              <SimpleTable
                columns={[
                  { key: "nombre_conductor", label: "Conductor" },
                  { key: "terminal", label: "Terminal" },
                  { key: "turno", label: "Turno" },
                  { key: "total_registros", label: "Registros" },
                  { key: "litros_totales", label: "Litros" },
                ]}
                rows={people?.conductores ?? []}
              />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Supervisores</CardTitle>
            </CardHeader>
            <CardContent>
              <SimpleTable
                columns={[
                  { key: "nombre_supervisor", label: "Supervisor" },
                  { key: "total_operaciones", label: "Operaciones" },
                  { key: "litros_totales", label: "Litros" },
                ]}
                rows={people?.supervisores ?? []}
              />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Planilleros</CardTitle>
            </CardHeader>
            <CardContent>
              <SimpleTable
                columns={[
                  { key: "nombre_planillero", label: "Planillero" },
                  { key: "total_registros", label: "Registros" },
                  { key: "litros_totales", label: "Litros" },
                ]}
                rows={people?.planilleros ?? []}
              />
            </CardContent>
          </Card>
        </section>
      )}
    </div>
  )
}
