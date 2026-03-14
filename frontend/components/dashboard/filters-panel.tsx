"use client"

import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { useFiltersStore } from "@/store/useFiltersStore"

export function FiltersPanel() {
  const { file_id, estacion, date_from, date_to, setFilter, clearFilters } = useFiltersStore()

  return (
    <Card className="border-border/70 bg-card/70">
      <CardContent className="grid gap-3 p-4 md:grid-cols-5">
        <Input
          placeholder="ID archivo"
          value={file_id ?? ""}
          onChange={(e) => setFilter("file_id", e.target.value)}
        />
        <Input
          placeholder="Estación"
          value={estacion ?? ""}
          onChange={(e) => setFilter("estacion", e.target.value)}
        />
        <Input type="date" value={date_from ?? ""} onChange={(e) => setFilter("date_from", e.target.value)} />
        <Input type="date" value={date_to ?? ""} onChange={(e) => setFilter("date_to", e.target.value)} />
        <Button variant="outline" onClick={clearFilters}>
          Limpiar filtros
        </Button>
      </CardContent>
    </Card>
  )
}
