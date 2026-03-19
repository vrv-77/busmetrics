"use client"

import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { useFiltersStore } from "@/store/useFiltersStore"

export function FiltersPanel() {
  const {
    file_id,
    terminal,
    turno,
    patente,
    numero_interno,
    conductor,
    supervisor,
    planillero,
    surtidor,
    search,
    date_from,
    date_to,
    setFilter,
    clearFilters,
  } = useFiltersStore()

  return (
    <Card className="border-border/70 bg-card/70">
      <CardContent className="grid gap-3 p-4 md:grid-cols-3 xl:grid-cols-6">
        <Input placeholder="Busqueda global" value={search ?? ""} onChange={(e) => setFilter("search", e.target.value)} />
        <Input placeholder="Terminal" value={terminal ?? ""} onChange={(e) => setFilter("terminal", e.target.value)} />
        <Input placeholder="Turno" value={turno ?? ""} onChange={(e) => setFilter("turno", e.target.value)} />
        <Input placeholder="Patente" value={patente ?? ""} onChange={(e) => setFilter("patente", e.target.value)} />
        <Input
          placeholder="Numero interno"
          value={numero_interno ?? ""}
          onChange={(e) => setFilter("numero_interno", e.target.value)}
        />
        <Input placeholder="Surtidor" value={surtidor ?? ""} onChange={(e) => setFilter("surtidor", e.target.value)} />
        <Input placeholder="Conductor" value={conductor ?? ""} onChange={(e) => setFilter("conductor", e.target.value)} />
        <Input
          placeholder="Supervisor"
          value={supervisor ?? ""}
          onChange={(e) => setFilter("supervisor", e.target.value)}
        />
        <Input
          placeholder="Planillero"
          value={planillero ?? ""}
          onChange={(e) => setFilter("planillero", e.target.value)}
        />
        <Input placeholder="ID archivo" value={file_id ?? ""} onChange={(e) => setFilter("file_id", e.target.value)} />
        <Input type="date" value={date_from ?? ""} onChange={(e) => setFilter("date_from", e.target.value)} />
        <Input type="date" value={date_to ?? ""} onChange={(e) => setFilter("date_to", e.target.value)} />

        <div className="md:col-span-3 xl:col-span-6">
          <Button variant="outline" onClick={clearFilters}>
            Limpiar filtros
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
