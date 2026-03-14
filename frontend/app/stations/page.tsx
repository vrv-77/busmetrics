"use client"

import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts"

import { FiltersPanel } from "@/components/dashboard/filters-panel"
import { SimpleTable } from "@/components/dashboard/simple-table"
import { PageHeader } from "@/components/layout/page-header"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { useStations } from "@/lib/hooks"
import { useFiltersStore } from "@/store/useFiltersStore"

export default function StationsPage() {
  const filters = useFiltersStore((state) => ({
    file_id: state.file_id,
    estacion: state.estacion,
    date_from: state.date_from,
    date_to: state.date_to,
  }))

  const stationsQuery = useStations(filters)

  return (
    <div className="space-y-4">
      <PageHeader title="Estaciones" subtitle="Métricas operacionales agregadas por electrolinera" />
      <FiltersPanel />

      <Card>
        <CardHeader>
          <CardTitle>Energía Total por Estación</CardTitle>
        </CardHeader>
        <CardContent className="h-80">
          <ResponsiveContainer>
            <BarChart data={stationsQuery.data ?? []}>
              <CartesianGrid strokeDasharray="3 3" stroke="#29425f" />
              <XAxis dataKey="estacion" stroke="#97afc4" />
              <YAxis stroke="#97afc4" />
              <Tooltip />
              <Bar dataKey="energia_total" fill="#20c997" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Detalle por Estación</CardTitle>
        </CardHeader>
        <CardContent>
          <SimpleTable
            columns={[
              { key: "estacion", label: "Estación" },
              { key: "total_cargas", label: "Cargas" },
              { key: "energia_total", label: "Energía (kWh)" },
              { key: "potencia_promedio", label: "Pot. Prom. (kW)" },
              { key: "potencia_maxima", label: "Pot. Máx. (kW)" },
              { key: "duracion_promedio", label: "Duración Prom. (min)" },
              { key: "alertas_soc_bajo", label: "SOC Bajo" },
              { key: "sesiones_incompletas", label: "Incompletas" },
            ]}
            rows={stationsQuery.data ?? []}
          />
        </CardContent>
      </Card>
    </div>
  )
}
