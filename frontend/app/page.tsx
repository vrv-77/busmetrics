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
import { getErrorMessage } from "@/lib/errors"
import { useDashboard } from "@/lib/hooks"
import type { DashboardData } from "@/lib/types"
import { useFiltersStore } from "@/store/useFiltersStore"

const PIE_COLORS = ["#3eb2f5", "#20c997", "#ffc069", "#ff6b6b", "#7f8ea3"]

function toSafeNumber(value: unknown): number {
  return typeof value === "number" && Number.isFinite(value) ? value : 0
}

function toSafeArray<T>(value: unknown): T[] {
  return Array.isArray(value) ? (value as T[]) : []
}

export default function DashboardPage() {
  const filters = useFiltersStore((state) => ({
    file_id: state.file_id,
    estacion: state.estacion,
    date_from: state.date_from,
    date_to: state.date_to,
  }))

  const dashboardQuery = useDashboard(filters)
  const data = dashboardQuery.data

  const kpis: Partial<DashboardData["kpis"]> = data?.kpis ?? {}
  const cargasPorEstacion = toSafeArray<{ estacion: string; total_cargas: number }>(data?.cargas_por_estacion)
  const energiaPorEstacion = toSafeArray<{ estacion: string; energia_total: number }>(data?.energia_por_estacion)
  const cargasPorDia = toSafeArray<{ dia: string; total: number }>(data?.cargas_por_dia)
  const distribucionSoc = toSafeArray<{ rango: string; total: number }>(data?.distribucion_soc_inicial)
  const rankingCargadores = toSafeArray<object>(data?.ranking_cargadores)
  const rankingBuses = toSafeArray<object>(data?.ranking_buses)
  const alertas: Partial<DashboardData["alertas"]> = data?.alertas ?? { total: 0, rojo: 0, amarillo: 0, gris: 0 }

  return (
    <div className="space-y-4">
      <PageHeader
        title="Dashboard Operacional"
        subtitle="Monitoreo unificado de carga electrica, eficiencia y alertas criticas"
      />

      <FiltersPanel />

      {dashboardQuery.isLoading ? (
        <Card>
          <CardContent className="p-6 text-sm text-muted-foreground">Cargando metricas operacionales...</CardContent>
        </Card>
      ) : dashboardQuery.isError ? (
        <Card>
          <CardContent className="p-6 text-sm text-rose-300">Error: {getErrorMessage(dashboardQuery.error)}</CardContent>
        </Card>
      ) : data ? (
        <>
          <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
            <KpiCard label="Total sesiones" value={toSafeNumber(kpis.total_sesiones)} />
            <KpiCard label="Energia total (kWh)" value={toSafeNumber(kpis.energia_total_kwh).toLocaleString()} />
            <KpiCard label="Potencia promedio (kW)" value={toSafeNumber(kpis.potencia_promedio_kw)} />
            <KpiCard label="Potencia maxima (kW)" value={toSafeNumber(kpis.potencia_maxima_kw)} />
            <KpiCard label="Duracion promedio (min)" value={toSafeNumber(kpis.duracion_promedio_min)} />
            <KpiCard label="Buses unicos" value={toSafeNumber(kpis.buses_unicos)} />
            <KpiCard label="Cargadores activos" value={toSafeNumber(kpis.cargadores_activos)} />
            <KpiCard label="Alertas criticas" value={toSafeNumber(kpis.alertas_criticas)} />
          </section>

          <section className="grid gap-4 lg:grid-cols-2">
            <ChartCard title="Cargas por Estacion">
              <div className="h-72">
                <ResponsiveContainer>
                  <BarChart data={cargasPorEstacion}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#29425f" />
                    <XAxis dataKey="estacion" stroke="#97afc4" />
                    <YAxis stroke="#97afc4" />
                    <Tooltip />
                    <Bar dataKey="total_cargas" fill="#3eb2f5" radius={[6, 6, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </ChartCard>

            <ChartCard title="Energia por Estacion">
              <div className="h-72">
                <ResponsiveContainer>
                  <LineChart data={energiaPorEstacion}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#29425f" />
                    <XAxis dataKey="estacion" stroke="#97afc4" />
                    <YAxis stroke="#97afc4" />
                    <Tooltip />
                    <Line type="monotone" dataKey="energia_total" stroke="#20c997" strokeWidth={3} dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </ChartCard>

            <ChartCard title="Cargas por Dia">
              <div className="h-72">
                <ResponsiveContainer>
                  <BarChart data={cargasPorDia}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#29425f" />
                    <XAxis dataKey="dia" stroke="#97afc4" />
                    <YAxis stroke="#97afc4" />
                    <Tooltip />
                    <Bar dataKey="total" fill="#6998db" radius={[6, 6, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </ChartCard>

            <ChartCard title="Distribucion SOC Inicial">
              <div className="h-72">
                <ResponsiveContainer>
                  <PieChart>
                    <Pie data={distribucionSoc} dataKey="total" nameKey="rango" outerRadius={110}>
                      {distribucionSoc.map((_, idx) => (
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
                    { key: "estacion", label: "Estacion" },
                    { key: "energia_kwh", label: "Energia (kWh)" },
                  ]}
                  rows={rankingCargadores}
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
                    { key: "energia_kwh", label: "Energia (kWh)" },
                  ]}
                  rows={rankingBuses}
                />
              </CardContent>
            </Card>
          </section>

          <Card className="border-border/70">
            <CardHeader>
              <CardTitle>Resumen de Alertas</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-wrap items-center gap-3 text-sm">
              <span>Total: {toSafeNumber(alertas.total)}</span>
              <SeverityBadge severity="rojo" /> <span>{toSafeNumber(alertas.rojo)}</span>
              <SeverityBadge severity="amarillo" /> <span>{toSafeNumber(alertas.amarillo)}</span>
              <SeverityBadge severity="gris" /> <span>{toSafeNumber(alertas.gris)}</span>
            </CardContent>
          </Card>
        </>
      ) : null}
    </div>
  )
}
