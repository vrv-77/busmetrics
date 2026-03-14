import { API_URL } from "@/lib/config"
import type {
  AlertItem,
  BusMetric,
  ChargerMetric,
  DashboardData,
  StationMetric,
  UploadedFile,
} from "@/lib/types"

export interface QueryFilters {
  file_id?: string
  estacion?: string
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
    return {}
  }

  const token = localStorage.getItem("busmetric-access-token")
  if (!token) {
    return {}
  }

  return {
    Authorization: `Bearer ${token}`,
  }
}

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(),
      ...(init?.headers ?? {}),
    },
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

export function getStations(filters?: QueryFilters) {
  return apiFetch<StationMetric[]>(`/stations${buildQuery(filters)}`)
}

export function getChargers(filters?: QueryFilters) {
  return apiFetch<ChargerMetric[]>(`/chargers${buildQuery(filters)}`)
}

export function getBuses(filters?: QueryFilters) {
  return apiFetch<BusMetric[]>(`/buses${buildQuery(filters)}`)
}

export function getAlerts(filters?: QueryFilters) {
  return apiFetch<AlertItem[]>(`/alerts${buildQuery(filters)}`)
}

export function getFiles() {
  return apiFetch<UploadedFile[]>("/files")
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

export async function processFile(fileId: string) {
  return apiFetch(`/process-file/${fileId}`, { method: "POST" })
}

export async function exportReport(scope: string, fmt: "csv" | "excel" | "pdf", filters?: QueryFilters) {
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
