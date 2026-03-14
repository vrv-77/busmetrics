"use client"

import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"

import { ChartCard } from "@/components/dashboard/chart-card"
import { FiltersPanel } from "@/components/dashboard/filters-panel"
import { KpiCard } from "@/components/dashboard/kpi-card"
import { SeverityBadge } from "@/components/dashboard/severity-badge"
import { SimpleTable } from "@/components/dashboard/simple-table"
import { PageHeader } from "@/components/layout/page-header"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { useDashboard } from "@/lib/hooks"
import { useFiltersStore } from "@/store/useFiltersStore"

const PIE_COLORS = ["#3eb2f5", "#20c997", "#ffc069", "#ff6b6b", "#7f8ea3"]

export default function DashboardPage() {
  const filters = useFiltersStore((state) => ({
    file_id: state.file_id,
    estacion: state.estacion,
    date_from: state.date_from,
    date_to: state.date_to,
  }))

  const dashboardQuery = useDashboard(filters)
  const data = dashboardQuery.data

  return (
    <div className="space-y-4">
      <PageHeader
        title="Dashboard Operacional"
        subtitle="Monitoreo unificado de carga eléctrica, eficiencia y alertas críticas"
      />

      <FiltersPanel />

      {dashboardQuery.isLoading ? (
        <Card>
          <CardContent className="p-6 text-sm text-muted-foreground">Cargando métricas operacionales...</CardContent>
        </Card>
      ) : dashboardQuery.isError ? (
        <Card>
          <CardContent className="p-6 text-sm text-rose-300">Error: {dashboardQuery.error.message}</CardContent>
        </Card>
      ) : data ? (
        <>
          <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
            <KpiCard label="Total sesiones" value={data.kpis.total_sesiones} />
            <KpiCard label="Energía total (kWh)" value={data.kpis.energia_total_kwh.toLocaleString()} />
            <KpiCard label="Potencia promedio (kW)" value={data.kpis.potencia_promedio_kw} />
            <KpiCard label="Potencia máxima (kW)" value={data.kpis.potencia_maxima_kw} />
            <KpiCard label="Duración promedio (min)" value={data.kpis.duracion_promedio_min} />
            <KpiCard label="Buses únicos" value={data.kpis.buses_unicos} />
            <KpiCard label="Cargadores activos" value={data.kpis.cargadores_activos} />
            <KpiCard label="Alertas críticas" value={data.kpis.alertas_criticas} />
          </section>

          <section className="grid gap-4 lg:grid-cols-2">
            <ChartCard title="Cargas por Estación">
              <div className="h-72">
                <ResponsiveContainer>
                  <BarChart data={data.cargas_por_estacion}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#29425f" />
                    <XAxis dataKey="estacion" stroke="#97afc4" />
                    <YAxis stroke="#97afc4" />
                    <Tooltip />
                    <Bar dataKey="total_cargas" fill="#3eb2f5" radius={[6, 6, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </ChartCard>

            <ChartCard title="Energía por Estación">
              <div className="h-72">
                <ResponsiveContainer>
                  <LineChart data={data.energia_por_estacion}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#29425f" />
                    <XAxis dataKey="estacion" stroke="#97afc4" />
                    <YAxis stroke="#97afc4" />
                    <Tooltip />
                    <Line type="monotone" dataKey="energia_total" stroke="#20c997" strokeWidth={3} dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </ChartCard>

            <ChartCard title="Cargas por Día">
              <div className="h-72">
                <ResponsiveContainer>
                  <BarChart data={data.cargas_por_dia}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#29425f" />
                    <XAxis dataKey="dia" stroke="#97afc4" />
                    <YAxis stroke="#97afc4" />
                    <Tooltip />
                    <Bar dataKey="total" fill="#6998db" radius={[6, 6, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </ChartCard>

            <ChartCard title="Distribución SOC Inicial">
              <div className="h-72">
                <ResponsiveContainer>
                  <PieChart>
                    <Pie data={data.distribucion_soc_inicial} dataKey="total" nameKey="rango" outerRadius={110}>
                      {data.distribucion_soc_inicial.map((_, idx) => (
                        <Cell key={`cell-${idx}`} fill={PIE_COLORS[idx % PIE_COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </ChartCard>
          </section>

          <section className="grid gap-4 lg:grid-cols-2">
            <Card className="border-border/70">
              <CardHeader>
                <CardTitle>Ranking de Cargadores</CardTitle>
              </CardHeader>
              <CardContent>
                <SimpleTable
                  columns={[
                    { key: "cargador", label: "Cargador" },
                    { key: "estacion", label: "Estación" },
                    { key: "energia_kwh", label: "Energía (kWh)" },
                  ]}
                  rows={data.ranking_cargadores}
                />
              </CardContent>
            </Card>

            <Card className="border-border/70">
              <CardHeader>
                <CardTitle>Ranking de Buses</CardTitle>
              </CardHeader>
              <CardContent>
                <SimpleTable
                  columns={[
                    { key: "vehiculo", label: "Bus" },
                    { key: "energia_kwh", label: "Energía (kWh)" },
                  ]}
                  rows={data.ranking_buses}
                />
              </CardContent>
            </Card>
          </section>

          <Card className="border-border/70">
            <CardHeader>
              <CardTitle>Resumen de Alertas</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-wrap items-center gap-3 text-sm">
              <span>Total: {data.alertas.total}</span>
              <SeverityBadge severity="rojo" /> <span>{data.alertas.rojo}</span>
              <SeverityBadge severity="amarillo" /> <span>{data.alertas.amarillo}</span>
              <SeverityBadge severity="gris" /> <span>{data.alertas.gris}</span>
            </CardContent>
          </Card>
        </>
      ) : null}
    </div>
  )
}
