"use client"

import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts"

import { FiltersPanel } from "@/components/dashboard/filters-panel"
import { SimpleTable } from "@/components/dashboard/simple-table"
import { PageHeader } from "@/components/layout/page-header"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { useBuses } from "@/lib/hooks"
import { useFiltersStore } from "@/store/useFiltersStore"

export default function BusesPage() {
  const filters = useFiltersStore((state) => ({
    file_id: state.file_id,
    estacion: state.estacion,
    date_from: state.date_from,
    date_to: state.date_to,
  }))

  const busesQuery = useBuses(filters)

  return (
    <div className="space-y-4">
      <PageHeader title="Buses" subtitle="Patrones de carga, SOC y criticidad por vehículo" />
      <FiltersPanel />

      <Card>
        <CardHeader>
          <CardTitle>Energía recibida por Bus</CardTitle>
        </CardHeader>
        <CardContent className="h-80">
          <ResponsiveContainer>
            <BarChart data={busesQuery.data?.slice(0, 15) ?? []}>
              <CartesianGrid strokeDasharray="3 3" stroke="#29425f" />
              <XAxis dataKey="vehiculo" stroke="#97afc4" />
              <YAxis stroke="#97afc4" />
              <Tooltip />
              <Bar dataKey="energia_total_recibida" fill="#20c997" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Detalle por Bus</CardTitle>
        </CardHeader>
        <CardContent>
          <SimpleTable
            columns={[
              { key: "vehiculo", label: "Bus" },
              { key: "total_cargas", label: "Cargas" },
              { key: "soc_inicial_promedio", label: "SOC Inicial %" },
              { key: "soc_final_promedio", label: "SOC Final %" },
              { key: "energia_total_recibida", label: "Energía" },
              { key: "duracion_promedio", label: "Duración Prom." },
              { key: "frecuencia_carga_horas", label: "Frecuencia (h)" },
              { key: "cargas_criticas", label: "Cargas Críticas" },
            ]}
            rows={busesQuery.data ?? []}
          />
        </CardContent>
      </Card>
    </div>
  )
}
