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
import { useFiltersStore } from "@/store/useFiltersStore"

const PIE_COLORS = ["#3eb2f5", "#20c997", "#ffc069", "#ff6b6b", "#7f8ea3", "#76d7c4"]

function toSafeNumber(value: unknown): number {
  return typeof value === "number" && Number.isFinite(value) ? value : 0
}

function toSafeArray<T>(value: unknown): T[] {
  return Array.isArray(value) ? (value as T[]) : []
}

export default function DashboardPage() {
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

  const dashboardQuery = useDashboard(filters)
  const data = dashboardQuery.data

  const kpis = data?.kpis
  const litrosPorDia = toSafeArray<{ fecha: string; cantidad_litros: number }>(data?.litros_por_dia)
  const cargasPorDia = toSafeArray<{ fecha: string; total: number }>(data?.cargas_por_dia)
  const litrosPorTerminal = toSafeArray<{ terminal: string; litros: number }>(data?.litros_por_terminal)
  const cargasPorTerminal = toSafeArray<{ terminal: string; total_cargas: number }>(data?.cargas_por_terminal)
  const turnoDonut = toSafeArray<{ turno: string; total_cargas: number }>(data?.turno_donut)
  const rankingBuses = toSafeArray<object>(data?.top_buses_por_litros)
  const rankingSurtidores = toSafeArray<object>(data?.ranking_surtidores)
  const alertas = data?.alertas ?? { total: 0, rojo: 0, amarillo: 0, gris: 0 }

  return (
    <div className="space-y-4">
      <PageHeader
        title="Dashboard Ejecutivo"
        subtitle="Indicadores operacionales y consumo diesel por terminal, turno, bus y surtidor"
      />

      <FiltersPanel />

      {dashboardQuery.isLoading ? (
        <Card>
          <CardContent className="p-6 text-sm text-muted-foreground">Cargando metricas ejecutivas...</CardContent>
        </Card>
      ) : dashboardQuery.isError ? (
        <Card>
          <CardContent className="p-6 text-sm text-rose-300">Error: {getErrorMessage(dashboardQuery.error)}</CardContent>
        </Card>
      ) : data && kpis ? (
        <>
          <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
            <KpiCard label="Total cargas" value={toSafeNumber(kpis.total_cargas).toLocaleString()} />
            <KpiCard label="Total litros" value={toSafeNumber(kpis.total_litros_cargados).toLocaleString()} />
            <KpiCard label="Litros del dia" value={toSafeNumber(kpis.litros_del_dia).toLocaleString()} />
            <KpiCard label="Litros del mes" value={toSafeNumber(kpis.litros_del_mes).toLocaleString()} />
            <KpiCard label="Litros periodo" value={toSafeNumber(kpis.litros_periodo_filtrado).toLocaleString()} />
            <KpiCard label="Buses unicos" value={toSafeNumber(kpis.buses_unicos_atendidos)} />
            <KpiCard label="Terminales activas" value={toSafeNumber(kpis.terminales_activos)} />
            <KpiCard label="Surtidores activos" value={toSafeNumber(kpis.surtidores_activos)} />
            <KpiCard label="Conductores unicos" value={toSafeNumber(kpis.conductores_unicos)} />
            <KpiCard label="Prom. litros/carga" value={toSafeNumber(kpis.promedio_litros_por_carga)} />
          </section>

          <section className="grid gap-4 lg:grid-cols-2">
            <ChartCard title="Serie temporal de litros por dia">
              <div className="h-72">
                <ResponsiveContainer>
                  <LineChart data={litrosPorDia}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#29425f" />
                    <XAxis dataKey="fecha" stroke="#97afc4" />
                    <YAxis stroke="#97afc4" />
                    <Tooltip />
                    <Line type="monotone" dataKey="cantidad_litros" stroke="#20c997" strokeWidth={3} dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </ChartCard>

            <ChartCard title="Serie temporal de eventos por dia">
              <div className="h-72">
                <ResponsiveContainer>
                  <BarChart data={cargasPorDia}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#29425f" />
                    <XAxis dataKey="fecha" stroke="#97afc4" />
                    <YAxis stroke="#97afc4" />
                    <Tooltip />
                    <Bar dataKey="total" fill="#3eb2f5" radius={[6, 6, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </ChartCard>

            <ChartCard title="Litros por terminal">
              <div className="h-72">
                <ResponsiveContainer>
                  <BarChart data={litrosPorTerminal}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#29425f" />
                    <XAxis dataKey="terminal" stroke="#97afc4" />
                    <YAxis stroke="#97afc4" />
                    <Tooltip />
                    <Bar dataKey="litros" fill="#20c997" radius={[6, 6, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </ChartCard>

            <ChartCard title="Cargas por terminal">
              <div className="h-72">
                <ResponsiveContainer>
                  <BarChart data={cargasPorTerminal}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#29425f" />
                    <XAxis dataKey="terminal" stroke="#97afc4" />
                    <YAxis stroke="#97afc4" />
                    <Tooltip />
                    <Bar dataKey="total_cargas" fill="#6998db" radius={[6, 6, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </ChartCard>

            <ChartCard title="Participacion por turno">
              <div className="h-72">
                <ResponsiveContainer>
                  <PieChart>
                    <Pie data={turnoDonut} dataKey="total_cargas" nameKey="turno" outerRadius={110}>
                      {turnoDonut.map((_, idx) => (
                        <Cell key={`cell-${idx}`} fill={PIE_COLORS[idx % PIE_COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </ChartCard>

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
          </section>

          <section className="grid gap-4 lg:grid-cols-2">
            <Card className="border-border/70">
              <CardHeader>
                <CardTitle>Top 10 buses por litros</CardTitle>
              </CardHeader>
              <CardContent>
                <SimpleTable
                  columns={[
                    { key: "numero_interno", label: "Numero interno" },
                    { key: "patente", label: "Patente" },
                    { key: "litros_totales", label: "Litros" },
                  ]}
                  rows={rankingBuses}
                />
              </CardContent>
            </Card>

            <Card className="border-border/70">
              <CardHeader>
                <CardTitle>Ranking surtidores</CardTitle>
              </CardHeader>
              <CardContent>
                <SimpleTable
                  columns={[
                    { key: "surtidor", label: "Surtidor" },
                    { key: "total_cargas", label: "Cargas" },
                    { key: "litros_totales", label: "Litros" },
                  ]}
                  rows={rankingSurtidores}
                />
              </CardContent>
            </Card>
          </section>
        </>
      ) : null}
    </div>
  )
}
