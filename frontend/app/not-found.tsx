import Link from "next/link"

import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"

export default function NotFound() {
  return (
    <Card className="mx-auto mt-10 max-w-xl">
      <CardContent className="space-y-3 p-6 text-center">
        <h1 className="text-2xl font-bold">Vista no encontrada</h1>
        <p className="text-muted-foreground">La ruta solicitada no existe en la plataforma.</p>
        <Button asChild>
          <Link href="/">Volver al dashboard</Link>
        </Button>
      </CardContent>
    </Card>
  )
}
