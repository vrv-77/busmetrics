"use client"

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"

import {
  exportReport,
  getAlerts,
  getBuses,
  getChargers,
  getDashboard,
  getFiles,
  getStations,
  processFile,
  uploadExcel,
  type QueryFilters,
} from "@/lib/api"

export function useDashboard(filters?: QueryFilters) {
  return useQuery({
    queryKey: ["dashboard", filters],
    queryFn: () => getDashboard(filters),
  })
}

export function useStations(filters?: QueryFilters) {
  return useQuery({
    queryKey: ["stations", filters],
    queryFn: () => getStations(filters),
  })
}

export function useChargers(filters?: QueryFilters) {
  return useQuery({
    queryKey: ["chargers", filters],
    queryFn: () => getChargers(filters),
  })
}

export function useBuses(filters?: QueryFilters) {
  return useQuery({
    queryKey: ["buses", filters],
    queryFn: () => getBuses(filters),
  })
}

export function useAlerts(filters?: QueryFilters) {
  return useQuery({
    queryKey: ["alerts", filters],
    queryFn: () => getAlerts(filters),
  })
}

export function useFiles() {
  return useQuery({
    queryKey: ["files"],
    queryFn: getFiles,
    refetchInterval: 12000,
  })
}

export function useUploadExcel() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: uploadExcel,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["files"] })
    },
  })
}

export function useProcessFile() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (fileId: string) => processFile(fileId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["files"] })
      queryClient.invalidateQueries({ queryKey: ["dashboard"] })
      queryClient.invalidateQueries({ queryKey: ["stations"] })
      queryClient.invalidateQueries({ queryKey: ["chargers"] })
      queryClient.invalidateQueries({ queryKey: ["buses"] })
      queryClient.invalidateQueries({ queryKey: ["alerts"] })
    },
  })
}

export function useExportReport() {
  return useMutation({
    mutationFn: ({
      scope,
      format,
      filters,
    }: {
      scope: string
      format: "csv" | "excel" | "pdf"
      filters?: QueryFilters
    }) => exportReport(scope, format, filters),
  })
}
