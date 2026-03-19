"use client"

import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts"

import { FiltersPanel } from "@/components/dashboard/filters-panel"
import { KpiCard } from "@/components/dashboard/kpi-card"
import { SimpleTable } from "@/components/dashboard/simple-table"
import { PageHeader } from "@/components/layout/page-header"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { getErrorMessage } from "@/lib/errors"
import { useFiltersStore } from "@/store/useFiltersStore"
import { useQuality } from "@/lib/hooks"

export default function QualityPage() {
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

  const qualityQuery = useQuality(filters)
  const quality = qualityQuery.data

  return (
    <div className="space-y-4">
      <PageHeader title="Calidad de Datos" subtitle="Completitud, consistencia y errores por columna" />
      <FiltersPanel />

      {qualityQuery.isLoading ? (
        <Card>
          <CardContent className="p-6 text-sm text-muted-foreground">Cargando calidad de datos...</CardContent>
        </Card>
      ) : qualityQuery.isError ? (
        <Card>
          <CardContent className="p-6 text-sm text-rose-300">Error: {getErrorMessage(qualityQuery.error)}</CardContent>
        </Card>
      ) : quality ? (
        <>
          <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
            <KpiCard label="Total registros" value={quality.total_registros} />
            <KpiCard label="% completos" value={quality.porcentaje_registros_completos} />
            <KpiCard label="Registros con nulos" value={quality.registros_con_nulos} />
            <KpiCard label="Patentes invalidas" value={quality.registros_patente_invalida} />
            <KpiCard label="Odometro vacio" value={quality.registros_odometro_vacio} />
            <KpiCard label="Duplicados" value={quality.registros_duplicados} />
            <KpiCard label="Terminales mal homologados" value={quality.terminales_mal_homologados} />
            <KpiCard label="Calidad promedio" value={quality.calidad_promedio} />
          </section>

          <section className="grid gap-4 lg:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Errores por Columna</CardTitle>
              </CardHeader>
              <CardContent>
                <SimpleTable
                  columns={[
                    { key: "columna", label: "Columna" },
                    { key: "nulos", label: "Nulos" },
                  ]}
                  rows={quality.errores_por_columna}
                />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Calidad por Terminal</CardTitle>
              </CardHeader>
              <CardContent className="h-80">
                <ResponsiveContainer>
                  <BarChart data={quality.calidad_por_terminal}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#29425f" />
                    <XAxis dataKey="terminal" stroke="#97afc4" />
                    <YAxis stroke="#97afc4" />
                    <Tooltip />
                    <Bar dataKey="calidad_promedio" fill="#3eb2f5" radius={[8, 8, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </section>
        </>
      ) : null}
    </div>
  )
}
