import { ArrowUpRight } from "lucide-react"

import { Card, CardContent } from "@/components/ui/card"

export function KpiCard({
  label,
  value,
  helper,
}: {
  label: string
  value: string | number
  helper?: string
}) {
  return (
    <Card className="animate-fade-up border-border/70">
      <CardContent className="space-y-2 p-4">
        <div className="flex items-center justify-between">
          <p className="text-xs uppercase tracking-[0.08em] text-muted-foreground">{label}</p>
          <ArrowUpRight className="h-4 w-4 text-primary" />
        </div>
        <p className="text-2xl font-bold leading-none">{value}</p>
        {helper ? <p className="text-xs text-muted-foreground">{helper}</p> : null}
      </CardContent>
    </Card>
  )
}
