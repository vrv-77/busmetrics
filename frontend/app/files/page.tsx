"use client"

import { Loader2, Play } from "lucide-react"

import { FileUploadCard } from "@/components/dashboard/file-upload-card"
import { PageHeader } from "@/components/layout/page-header"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { getErrorMessage } from "@/lib/errors"
import { useFiles, useProcessFile } from "@/lib/hooks"

function statusVariant(status: string): "success" | "warning" | "critical" | "neutral" {
  if (status === "processed") return "success"
  if (status === "processing") return "warning"
  if (status === "failed") return "critical"
  return "neutral"
}

export default function FilesPage() {
  const filesQuery = useFiles()
  const processMutation = useProcessFile()

  return (
    <div className="space-y-4">
      <PageHeader
        title="Gestion de Archivos"
        subtitle="Carga, validacion estructural, mapeo de columnas y reproceso de archivos de combustible"
      />

      <FileUploadCard />

      <Card>
        <CardHeader>
          <CardTitle>Historial de Archivos</CardTitle>
        </CardHeader>
        <CardContent>
          {filesQuery.isLoading ? (
            <p className="text-sm text-muted-foreground">Cargando archivos...</p>
          ) : filesQuery.isError ? (
            <p className="text-sm text-rose-300">Error: {getErrorMessage(filesQuery.error)}</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Archivo</TableHead>
                  <TableHead>Formato</TableHead>
                  <TableHead>Fecha de carga</TableHead>
                  <TableHead>Usuario</TableHead>
                  <TableHead>Estado</TableHead>
                  <TableHead>Filas</TableHead>
                  <TableHead>Acciones</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {(filesQuery.data ?? []).map((item) => (
                  <TableRow key={item.id}>
                    <TableCell>{item.filename}</TableCell>
                    <TableCell>{item.detected_format ?? "-"}</TableCell>
                    <TableCell>{new Date(item.upload_date).toLocaleString()}</TableCell>
                    <TableCell>{item.user_id}</TableCell>
                    <TableCell>
                      <Badge variant={statusVariant(item.status)}>{item.status}</Badge>
                    </TableCell>
                    <TableCell>{item.row_count}</TableCell>
                    <TableCell>
                      <Button
                        size="sm"
                        variant="secondary"
                        onClick={() => processMutation.mutate({ fileId: item.id })}
                        disabled={processMutation.isPending || item.status === "processing"}
                      >
                        {processMutation.isPending ? (
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        ) : (
                          <Play className="mr-2 h-4 w-4" />
                        )}
                        Reprocesar
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
