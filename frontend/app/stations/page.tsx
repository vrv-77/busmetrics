"use client"

import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts"

import { FiltersPanel } from "@/components/dashboard/filters-panel"
import { SimpleTable } from "@/components/dashboard/simple-table"
import { PageHeader } from "@/components/layout/page-header"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { useFiltersStore } from "@/store/useFiltersStore"
import { useTerminals } from "@/lib/hooks"

export default function StationsPage() {
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

  const terminalsQuery = useTerminals(filters)

  return (
    <div className="space-y-4">
      <PageHeader title="Analisis por Terminal" subtitle="Consumo, actividad y comparacion entre terminales" />
      <FiltersPanel />

      <Card>
        <CardHeader>
          <CardTitle>Litros Totales por Terminal</CardTitle>
        </CardHeader>
        <CardContent className="h-80">
          <ResponsiveContainer>
            <BarChart data={terminalsQuery.data ?? []}>
              <CartesianGrid strokeDasharray="3 3" stroke="#29425f" />
              <XAxis dataKey="terminal" stroke="#97afc4" />
              <YAxis stroke="#97afc4" />
              <Tooltip />
              <Bar dataKey="litros_totales" fill="#20c997" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Detalle por Terminal</CardTitle>
        </CardHeader>
        <CardContent>
          <SimpleTable
            columns={[
              { key: "terminal", label: "Terminal" },
              { key: "total_cargas", label: "Cargas" },
              { key: "litros_totales", label: "Litros" },
              { key: "promedio_litros_por_carga", label: "Prom. litros/carga" },
              { key: "buses_unicos", label: "Buses unicos" },
              { key: "conductores_unicos", label: "Conductores unicos" },
              { key: "surtidores_activos", label: "Surtidores" },
              { key: "participacion_pct", label: "% participacion" },
              { key: "caida_operacional", label: "Caida operacional" },
            ]}
            rows={terminalsQuery.data ?? []}
          />
        </CardContent>
      </Card>
    </div>
  )
}
