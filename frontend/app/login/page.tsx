"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"

import { PageHeader } from "@/components/layout/page-header"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { supabase } from "@/lib/supabase"

export default function LoginPage() {
  const router = useRouter()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setLoading(true)

    try {
      if (!supabase) {
        localStorage.setItem("busmetric-access-token", "dev-local-token")
        router.push("/")
        return
      }

      const { data, error: authError } = await supabase.auth.signInWithPassword({ email, password })
      if (authError) {
        throw authError
      }

      if (!data.session?.access_token) {
        throw new Error("No se obtuvo token de sesion")
      }

      localStorage.setItem("busmetric-access-token", data.session.access_token)
      router.push("/")
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error desconocido")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      <PageHeader title="Login" subtitle="Autenticacion Supabase para acceso a la plataforma FuelOps" />

      <Card className="mx-auto max-w-lg border-primary/30">
        <CardHeader>
          <CardTitle>Ingresar a BusMetric FuelOps</CardTitle>
          <CardDescription>Si no configuras Supabase en frontend, se usara modo local de desarrollo.</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleLogin} className="space-y-3">
            <Input
              type="email"
              placeholder="correo@empresa.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            <Input
              type="password"
              placeholder="********"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            <Button type="submit" disabled={loading}>
              {loading ? "Ingresando..." : "Ingresar"}
            </Button>
            {error ? <p className="text-sm text-rose-300">{error}</p> : null}
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
