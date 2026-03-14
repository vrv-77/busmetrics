"use client"

import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts"

import { FiltersPanel } from "@/components/dashboard/filters-panel"
import { SimpleTable } from "@/components/dashboard/simple-table"
import { PageHeader } from "@/components/layout/page-header"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { useChargers } from "@/lib/hooks"
import { useFiltersStore } from "@/store/useFiltersStore"

export default function ChargersPage() {
  const filters = useFiltersStore((state) => ({
    file_id: state.file_id,
    estacion: state.estacion,
    date_from: state.date_from,
    date_to: state.date_to,
  }))

  const chargersQuery = useChargers(filters)

  return (
    <div className="space-y-4">
      <PageHeader title="Cargadores" subtitle="Rendimiento, eficiencia y utilización por cargador" />
      <FiltersPanel />

      <Card>
        <CardHeader>
          <CardTitle>Ranking de Eficiencia (kWh/h)</CardTitle>
        </CardHeader>
        <CardContent className="h-80">
          <ResponsiveContainer>
            <BarChart data={chargersQuery.data?.slice(0, 12) ?? []}>
              <CartesianGrid strokeDasharray="3 3" stroke="#29425f" />
              <XAxis dataKey="cargador" stroke="#97afc4" />
              <YAxis stroke="#97afc4" />
              <Tooltip />
              <Bar dataKey="eficiencia_kwh_por_hora" fill="#3eb2f5" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Detalle por Cargador</CardTitle>
        </CardHeader>
        <CardContent>
          <SimpleTable
            columns={[
              { key: "cargador", label: "Cargador" },
              { key: "estacion", label: "Estación" },
              { key: "total_sesiones", label: "Sesiones" },
              { key: "energia_total", label: "Energía" },
              { key: "potencia_promedio", label: "Pot. Prom." },
              { key: "potencia_maxima", label: "Pot. Máx." },
              { key: "eficiencia_kwh_por_hora", label: "Eficiencia" },
              { key: "utilizacion", label: "Utilización" },
            ]}
            rows={chargersQuery.data ?? []}
          />
        </CardContent>
      </Card>
    </div>
  )
}
