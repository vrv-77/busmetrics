"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { BarChart3, Bell, Bus, FileSpreadsheet, Gauge, Home, MapPinned, Plug, ScrollText } from "lucide-react"

import { cn } from "@/lib/utils"

const links = [
  { href: "/", label: "Dashboard", icon: Home },
  { href: "/files", label: "Archivos", icon: FileSpreadsheet },
  { href: "/stations", label: "Estaciones", icon: MapPinned },
  { href: "/chargers", label: "Cargadores", icon: Plug },
  { href: "/buses", label: "Buses", icon: Bus },
  { href: "/alerts", label: "Alertas", icon: Bell },
  { href: "/reports", label: "Reportes", icon: ScrollText },
]

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  const isLoginPage = pathname?.startsWith("/login")

  return (
    <div className="min-h-screen">
      <div
        className={cn(
          "mx-auto grid max-w-[1600px] gap-4 px-3 py-4 md:px-6 lg:py-6",
          isLoginPage ? "grid-cols-1" : "grid-cols-1 md:grid-cols-[250px_1fr]"
        )}
      >
        {!isLoginPage ? (
          <aside className="energy-grid rounded-2xl border border-border/70 bg-card/70 p-4 backdrop-blur">
            <div className="mb-6 flex items-center gap-3">
              <div className="rounded-lg bg-accent/25 p-2 text-accent">
                <Gauge className="h-5 w-5" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Plataforma</p>
                <h2 className="font-bold tracking-wide">BusMetric Ops</h2>
              </div>
            </div>

            <nav className="space-y-1">
              {links.map(({ href, label, icon: Icon }) => {
                const active = pathname === href
                return (
                  <Link
                    key={href}
                    href={href}
                    className={cn(
                      "flex items-center gap-3 rounded-md px-3 py-2 text-sm transition",
                      active ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:bg-muted hover:text-foreground"
                    )}
                  >
                    <Icon className="h-4 w-4" />
                    {label}
                  </Link>
                )
              })}
            </nav>

            <div className="mt-8 rounded-lg border border-accent/35 bg-accent/10 p-3 text-xs text-accent-foreground">
              <div className="mb-1 flex items-center gap-2 font-semibold text-accent">
                <BarChart3 className="h-4 w-4" />
                Estado Operacional
              </div>
              <p>Seguimiento centralizado de sesiones, eficiencia y alertas de carga.</p>
            </div>
          </aside>
        ) : null}

        <main className="space-y-4">{children}</main>
      </div>
    </div>
  )
}
