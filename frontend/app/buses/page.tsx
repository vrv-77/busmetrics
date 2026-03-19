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

  const busesQuery = useBuses(filters)

  return (
    <div className="space-y-4">
      <PageHeader title="Analisis por Bus" subtitle="Historico de cargas por numero interno y patente" />
      <FiltersPanel />

      <Card>
        <CardHeader>
          <CardTitle>Litros Acumulados por Bus</CardTitle>
        </CardHeader>
        <CardContent className="h-80">
          <ResponsiveContainer>
            <BarChart data={busesQuery.data?.slice(0, 15) ?? []}>
              <CartesianGrid strokeDasharray="3 3" stroke="#29425f" />
              <XAxis dataKey="numero_interno" stroke="#97afc4" />
              <YAxis stroke="#97afc4" />
              <Tooltip />
              <Bar dataKey="litros_acumulados" fill="#20c997" radius={[8, 8, 0, 0]} />
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
              { key: "numero_interno", label: "Numero interno" },
              { key: "patente", label: "Patente" },
              { key: "total_cargas", label: "Cargas" },
              { key: "litros_acumulados", label: "Litros acumulados" },
              { key: "promedio_litros", label: "Prom. litros" },
              { key: "frecuencia_dias", label: "Frecuencia (dias)" },
              { key: "ultima_carga", label: "Ultima carga" },
              { key: "tiempo_desde_ultima_carga_horas", label: "Horas desde ultima" },
              { key: "odometro_reciente", label: "Odometro reciente" },
              { key: "alertas_odometro", label: "Alertas odometro" },
              { key: "alertas_consumo", label: "Alertas consumo" },
            ]}
            rows={busesQuery.data ?? []}
          />
        </CardContent>
      </Card>
    </div>
  )
}
