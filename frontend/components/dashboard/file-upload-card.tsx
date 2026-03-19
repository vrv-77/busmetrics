"use client"

import { useMemo, useState } from "react"
import { Loader2, UploadCloud } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Select } from "@/components/ui/select"
import { getErrorMessage } from "@/lib/errors"
import { usePreviewFile, useProcessFile, useUploadExcel } from "@/lib/hooks"

const EXPECTED_FIELDS: Array<{ key: string; label: string }> = [
  { key: "turno", label: "Turno" },
  { key: "fecha", label: "Fecha" },
  { key: "hora", label: "Hora" },
  { key: "terminal", label: "Terminal" },
  { key: "numero_interno", label: "Numero interno" },
  { key: "patente", label: "Patente" },
  { key: "cantidad_litros", label: "Cantidad litros" },
  { key: "tipo", label: "Tipo" },
  { key: "tapa", label: "Tapa" },
  { key: "filtracion", label: "Filtracion" },
  { key: "modelo_chasis", label: "Modelo chasis" },
  { key: "estanque", label: "Estanque" },
  { key: "llenado", label: "Llenado" },
  { key: "exeso", label: "Exeso" },
  { key: "odometro", label: "Odometro" },
  { key: "rut_planillero", label: "RUT planillero" },
  { key: "nombre_planillero", label: "Nombre planillero" },
  { key: "rut_supervisor", label: "RUT supervisor" },
  { key: "nombre_supervisor", label: "Nombre supervisor" },
  { key: "rut_conductor", label: "RUT conductor" },
  { key: "nombre_conductor", label: "Nombre conductor" },
  { key: "surtidor", label: "Surtidor" },
  { key: "capturador", label: "Capturador" },
  { key: "cargado_por", label: "Cargado por" },
]

export function FileUploadCard() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [uploadedFileId, setUploadedFileId] = useState<string | null>(null)
  const [isDragging, setIsDragging] = useState(false)
  const [columnMapping, setColumnMapping] = useState<Record<string, string>>({})

  const uploadMutation = useUploadExcel()
  const previewMutation = usePreviewFile()
  const processMutation = useProcessFile()

  const preview = previewMutation.data

  const canProcess = Boolean(uploadedFileId && preview)

  const visibleFields = useMemo(() => EXPECTED_FIELDS, [])

  const onUploadAndPreview = async () => {
    if (!selectedFile) return
    const uploaded = await uploadMutation.mutateAsync(selectedFile)
    setUploadedFileId(uploaded.file_id)

    const previewResult = await previewMutation.mutateAsync(uploaded.file_id)
    setColumnMapping(previewResult.suggested_mapping)
  }

  const onProcess = async () => {
    if (!uploadedFileId) return
    await processMutation.mutateAsync({
      fileId: uploadedFileId,
      columnMapping,
    })
  }

  const onDrop: React.DragEventHandler<HTMLDivElement> = (event) => {
    event.preventDefault()
    setIsDragging(false)

    const file = event.dataTransfer.files?.[0]
    if (!file) return
    setSelectedFile(file)
  }

  return (
    <Card className="border-primary/25 bg-gradient-to-br from-card via-card/95 to-card/70">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <UploadCloud className="h-5 w-5 text-primary" />
          Carga de Archivos Diesel
        </CardTitle>
        <CardDescription>
          Soporta .xlsx, .xls y .xls con tabla HTML. Se detecta formato real, columnas y estructura antes de procesar.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div
          className={`rounded-xl border border-dashed p-4 text-center transition ${
            isDragging ? "border-primary bg-primary/10" : "border-border bg-background/30"
          }`}
          onDragOver={(e) => {
            e.preventDefault()
            setIsDragging(true)
          }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={onDrop}
        >
          <p className="mb-2 text-sm text-muted-foreground">Arrastra y suelta el archivo aqui o seleccionalo manualmente</p>
          <Input type="file" accept=".xlsx,.xls" onChange={(e) => setSelectedFile(e.target.files?.[0] ?? null)} />
          {selectedFile ? <p className="mt-2 text-xs text-muted-foreground">Seleccionado: {selectedFile.name}</p> : null}
        </div>

        <div className="flex flex-wrap gap-2">
          <Button onClick={onUploadAndPreview} disabled={!selectedFile || uploadMutation.isPending || previewMutation.isPending}>
            {uploadMutation.isPending || previewMutation.isPending ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : null}
            Subir y previsualizar
          </Button>
          <Button variant="secondary" onClick={onProcess} disabled={!canProcess || processMutation.isPending}>
            {processMutation.isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
            Procesar archivo
          </Button>
        </div>

        {preview ? (
          <div className="space-y-3 rounded-lg border border-border/70 bg-background/35 p-3">
            <p className="text-xs text-muted-foreground">
              Formato detectado: <span className="font-semibold text-foreground">{preview.detected_format}</span>
            </p>
            {preview.missing_columns.length > 0 ? (
              <p className="text-xs text-amber-300">Columnas sin mapeo automatico: {preview.missing_columns.join(", ")}</p>
            ) : (
              <p className="text-xs text-emerald-300">Todas las columnas esperadas fueron detectadas.</p>
            )}

            <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
              {visibleFields.map((field) => (
                <div key={field.key} className="space-y-1">
                  <label className="text-xs text-muted-foreground">{field.label}</label>
                  <Select
                    value={columnMapping[field.key] ?? ""}
                    onChange={(e) =>
                      setColumnMapping((prev) => ({
                        ...prev,
                        [field.key]: e.target.value,
                      }))
                    }
                  >
                    <option value="">Sin asignar</option>
                    {preview.source_columns.map((column) => (
                      <option key={`${field.key}-${column}`} value={column}>
                        {column}
                      </option>
                    ))}
                  </Select>
                </div>
              ))}
            </div>

            {preview.preview_rows.length > 0 ? (
              <div className="overflow-x-auto rounded-md border border-border/70">
                <table className="min-w-full text-xs">
                  <thead className="bg-muted/40">
                    <tr>
                      {preview.source_columns.map((col) => (
                        <th key={col} className="px-2 py-1 text-left font-medium">
                          {col}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {preview.preview_rows.slice(0, 8).map((row, idx) => (
                      <tr key={idx} className="border-t border-border/40">
                        {preview.source_columns.map((col) => (
                          <td key={`${idx}-${col}`} className="px-2 py-1 text-muted-foreground">
                            {String(row[col] ?? "")}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : null}
          </div>
        ) : null}

        {uploadMutation.isError ? <p className="text-sm text-rose-300">Error de carga: {getErrorMessage(uploadMutation.error)}</p> : null}
        {previewMutation.isError ? (
          <p className="text-sm text-rose-300">Error de preview: {getErrorMessage(previewMutation.error)}</p>
        ) : null}
        {processMutation.isError ? (
          <p className="text-sm text-rose-300">Error de procesamiento: {getErrorMessage(processMutation.error)}</p>
        ) : null}

        {processMutation.isSuccess ? (
          <p className="text-sm text-emerald-300">
            Proceso completado. Insertados: {processMutation.data.rows_processed} | Duplicados evitados: {processMutation.data.duplicates_avoided}
          </p>
        ) : null}
      </CardContent>
    </Card>
  )
}
