"use client"

import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts"

import { FiltersPanel } from "@/components/dashboard/filters-panel"
import { SimpleTable } from "@/components/dashboard/simple-table"
import { PageHeader } from "@/components/layout/page-header"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { useShifts } from "@/lib/hooks"
import { useFiltersStore } from "@/store/useFiltersStore"

export default function ShiftsPage() {
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

  const shiftsQuery = useShifts(filters)

  return (
    <div className="space-y-4">
      <PageHeader title="Analisis por Turno" subtitle="Comparacion, horas punta y participacion por turno" />
      <FiltersPanel />

      <Card>
        <CardHeader>
          <CardTitle>Litros por Turno</CardTitle>
        </CardHeader>
        <CardContent className="h-80">
          <ResponsiveContainer>
            <BarChart data={shiftsQuery.data ?? []}>
              <CartesianGrid strokeDasharray="3 3" stroke="#29425f" />
              <XAxis dataKey="turno" stroke="#97afc4" />
              <YAxis stroke="#97afc4" />
              <Tooltip />
              <Bar dataKey="litros_totales" fill="#ffc069" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Detalle por Turno</CardTitle>
        </CardHeader>
        <CardContent>
          <SimpleTable
            columns={[
              { key: "turno", label: "Turno" },
              { key: "total_cargas", label: "Cargas" },
              { key: "litros_totales", label: "Litros" },
              { key: "promedio_litros", label: "Promedio litros" },
              { key: "participacion_pct", label: "% participacion" },
              { key: "horas_punta", label: "Hora punta" },
              { key: "horas_valle", label: "Hora valle" },
            ]}
            rows={shiftsQuery.data ?? []}
          />
        </CardContent>
      </Card>
    </div>
  )
}
