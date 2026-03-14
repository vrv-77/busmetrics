import { Badge } from "@/components/ui/badge"
import type { Severity } from "@/lib/types"

export function SeverityBadge({ severity }: { severity: Severity }) {
  if (severity === "rojo") return <Badge variant="critical">Crítico</Badge>
  if (severity === "amarillo") return <Badge variant="warning">Advertencia</Badge>
  return <Badge variant="neutral">Incompleto</Badge>
}
