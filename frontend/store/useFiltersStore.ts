"use client"

import { create } from "zustand"

export interface FiltersState {
  file_id?: string
  estacion?: string
  date_from?: string
  date_to?: string
  setFilter: (key: "file_id" | "estacion" | "date_from" | "date_to", value?: string) => void
  clearFilters: () => void
}

export const useFiltersStore = create<FiltersState>((set) => ({
  file_id: undefined,
  estacion: undefined,
  date_from: undefined,
  date_to: undefined,
  setFilter: (key, value) => set(() => ({ [key]: value || undefined })),
  clearFilters: () =>
    set({
      file_id: undefined,
      estacion: undefined,
      date_from: undefined,
      date_to: undefined,
    }),
}))
