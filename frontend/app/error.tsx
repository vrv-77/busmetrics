"use client"

import { useEffect } from "react"

import { Button } from "@/components/ui/button"

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    // Keeps visibility in browser console for production issues.
    console.error("BusMetric UI error:", error)
  }, [error])

  return (
    <div className="mx-auto mt-10 max-w-2xl rounded-lg border border-rose-400/30 bg-card p-6 text-card-foreground">
      <h2 className="text-xl font-semibold text-rose-300">Error en la interfaz web</h2>
      <p className="mt-2 text-sm text-muted-foreground">
        Ocurrio un error inesperado en el cliente. Reintenta y, si persiste, revisa variables del Static Site
        (NEXT_PUBLIC_API_URL y credenciales de Supabase).
      </p>
      <div className="mt-4">
        <Button onClick={reset}>Reintentar</Button>
      </div>
    </div>
  )
}
