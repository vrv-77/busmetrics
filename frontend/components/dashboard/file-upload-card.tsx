"use client"

import { useState } from "react"
import { Loader2, UploadCloud } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { useProcessFile, useUploadExcel } from "@/lib/hooks"

export function FileUploadCard() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [uploadedFileId, setUploadedFileId] = useState<string | null>(null)
  const uploadMutation = useUploadExcel()
  const processMutation = useProcessFile()

  const onUpload = async () => {
    if (!selectedFile) return
    const result = await uploadMutation.mutateAsync(selectedFile)
    setUploadedFileId(result.file_id)
  }

  const onProcess = async () => {
    if (!uploadedFileId) return
    await processMutation.mutateAsync(uploadedFileId)
  }

  return (
    <Card className="border-primary/25 bg-gradient-to-br from-card via-card/95 to-card/70">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <UploadCloud className="h-5 w-5 text-primary" />
          Subir Excel Transaccional
        </CardTitle>
        <CardDescription>Encabezados en fila 3, fechas UTC. El backend convierte automáticamente a America/Santiago.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        <Input type="file" accept=".xlsx,.xls" onChange={(e) => setSelectedFile(e.target.files?.[0] ?? null)} />
        <div className="flex flex-wrap gap-2">
          <Button onClick={onUpload} disabled={!selectedFile || uploadMutation.isPending}>
            {uploadMutation.isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
            Cargar archivo
          </Button>
          <Button variant="secondary" onClick={onProcess} disabled={!uploadedFileId || processMutation.isPending}>
            {processMutation.isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
            Procesar archivo
          </Button>
        </div>

        {uploadMutation.isError ? <p className="text-sm text-rose-300">Error de carga: {uploadMutation.error.message}</p> : null}
        {processMutation.isError ? <p className="text-sm text-rose-300">Error de procesamiento: {processMutation.error.message}</p> : null}

        {uploadedFileId ? <p className="text-xs text-muted-foreground">Archivo subido: {uploadedFileId}</p> : null}
      </CardContent>
    </Card>
  )
}
