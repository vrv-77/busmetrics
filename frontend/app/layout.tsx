import type { Metadata } from "next"
import { Manrope } from "next/font/google"

import { Providers } from "@/app/providers"
import { AppShell } from "@/components/layout/app-shell"

import "./globals.css"

const manrope = Manrope({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-manrope",
})

export const metadata: Metadata = {
  title: "BusMetric Ops",
  description: "Análisis operacional de cargas de buses eléctricos",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="es" className={manrope.variable}>
      <body className="font-sans">
        <Providers>
          <AppShell>{children}</AppShell>
        </Providers>
      </body>
    </html>
  )
}
