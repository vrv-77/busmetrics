import { API_URL } from "@/lib/config"
import type {
  AlertItem,
  BusMetric,
  DashboardData,
  DispenserMetric,
  FilePreview,
  OperationsResponse,
  PeopleMetrics,
  ProcessResult,
  QualityMetrics,
  ShiftMetric,
  TerminalMetric,
  UploadedFile,
} from "@/lib/types"

export interface QueryFilters {
  file_id?: string
  terminal?: string
  turno?: string
  patente?: string
  numero_interno?: string
  conductor?: string
  supervisor?: string
  planillero?: string
  surtidor?: string
  capturador?: string
  imported_user?: string
  search?: string
  date_from?: string
  date_to?: string
}

function buildQuery(filters?: QueryFilters): string {
  if (!filters) return ""

  const params = new URLSearchParams()
  Object.entries(filters).forEach(([key, value]) => {
    if (value) params.set(key, value)
  })

  const query = params.toString()
  return query ? `?${query}` : ""
}

function authHeaders() {
  if (typeof window === "undefined") {
    return {} as Record<string, string>
  }

  const token = localStorage.getItem("busmetric-access-token")
  if (!token) {
    return {} as Record<string, string>
  }

  return {
    Authorization: `Bearer ${token}`,
  }
}

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const headers = new Headers(init?.headers)

  if (!(init?.body instanceof FormData)) {
    headers.set("Content-Type", "application/json")
  }

  Object.entries(authHeaders()).forEach(([key, value]) => headers.set(key, value))

  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers,
    cache: "no-store",
  })

  if (!response.ok) {
    const text = await response.text()
    throw new Error(text || `HTTP ${response.status}`)
  }

  return response.json() as Promise<T>
}

export function getDashboard(filters?: QueryFilters) {
  return apiFetch<DashboardData>(`/dashboard${buildQuery(filters)}`)
}

export function getTerminals(filters?: QueryFilters) {
  return apiFetch<TerminalMetric[]>(`/terminals${buildQuery(filters)}`)
}

export function getShifts(filters?: QueryFilters) {
  return apiFetch<ShiftMetric[]>(`/shifts${buildQuery(filters)}`)
}

export function getDispensers(filters?: QueryFilters) {
  return apiFetch<DispenserMetric[]>(`/dispensers${buildQuery(filters)}`)
}

export function getBuses(filters?: QueryFilters) {
  return apiFetch<BusMetric[]>(`/buses${buildQuery(filters)}`)
}

export function getPeople(filters?: QueryFilters) {
  return apiFetch<PeopleMetrics>(`/people${buildQuery(filters)}`)
}

export function getQuality(filters?: QueryFilters) {
  return apiFetch<QualityMetrics>(`/quality${buildQuery(filters)}`)
}

export function getOperations(
  filters?: QueryFilters,
  options?: { page?: number; page_size?: number; sort_by?: string; sort_dir?: "asc" | "desc" }
) {
  const params = new URLSearchParams()
  if (filters) {
    Object.entries(filters).forEach(([key, value]) => {
      if (value) params.set(key, value)
    })
  }
  if (options?.page) params.set("page", String(options.page))
  if (options?.page_size) params.set("page_size", String(options.page_size))
  if (options?.sort_by) params.set("sort_by", options.sort_by)
  if (options?.sort_dir) params.set("sort_dir", options.sort_dir)

  const query = params.toString()
  return apiFetch<OperationsResponse>(`/operations${query ? `?${query}` : ""}`)
}

export function getAlerts(filters?: QueryFilters) {
  return apiFetch<AlertItem[]>(`/alerts${buildQuery(filters)}`)
}

export function getFiles() {
  return apiFetch<UploadedFile[]>("/files")
}

export function previewFile(fileId: string) {
  return apiFetch<FilePreview>(`/files/${fileId}/preview`)
}

export async function uploadExcel(file: File) {
  const formData = new FormData()
  formData.append("file", file)

  const response = await fetch(`${API_URL}/upload-file`, {
    method: "POST",
    body: formData,
    headers: {
      ...authHeaders(),
    },
  })

  if (!response.ok) {
    const text = await response.text()
    throw new Error(text || `HTTP ${response.status}`)
  }

  return response.json() as Promise<{ file_id: string; filename: string; status: string }>
}

export async function processFile(fileId: string, columnMapping: Record<string, string> = {}) {
  return apiFetch<ProcessResult>(`/process-file/${fileId}`, {
    method: "POST",
    body: JSON.stringify({ column_mapping: columnMapping }),
  })
}

export async function exportReport(
  scope: string,
  fmt: "csv" | "excel" | "pdf",
  filters?: QueryFilters
) {
  const query = new URLSearchParams()
  query.set("scope", scope)
  query.set("fmt", fmt)

  Object.entries(filters ?? {}).forEach(([key, value]) => {
    if (value) query.set(key, value)
  })

  const response = await fetch(`${API_URL}/reports/export?${query.toString()}`, {
    headers: {
      ...authHeaders(),
    },
  })

  if (!response.ok) {
    const text = await response.text()
    throw new Error(text || `HTTP ${response.status}`)
  }

  const blob = await response.blob()
  const disposition = response.headers.get("Content-Disposition")
  const filename = disposition?.match(/filename="(.+)"/)?.[1] ?? `reporte.${fmt}`

  return { blob, filename }
}
