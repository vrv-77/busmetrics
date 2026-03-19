"use client"

import { create } from "zustand"

export interface FiltersState {
  file_id?: string
  terminal?: string
  turno?: string
  patente?: string
  numero_interno?: string
  conductor?: string
  supervisor?: string
  planillero?: string
  surtidor?: string
  search?: string
  date_from?: string
  date_to?: string
  setFilter: (
    key:
      | "file_id"
      | "terminal"
      | "turno"
      | "patente"
      | "numero_interno"
      | "conductor"
      | "supervisor"
      | "planillero"
      | "surtidor"
      | "search"
      | "date_from"
      | "date_to",
    value?: string
  ) => void
  clearFilters: () => void
}

const initialState = {
  file_id: undefined,
  terminal: undefined,
  turno: undefined,
  patente: undefined,
  numero_interno: undefined,
  conductor: undefined,
  supervisor: undefined,
  planillero: undefined,
  surtidor: undefined,
  search: undefined,
  date_from: undefined,
  date_to: undefined,
}

export const useFiltersStore = create<FiltersState>((set) => ({
  ...initialState,
  setFilter: (key, value) => set(() => ({ [key]: value || undefined })),
  clearFilters: () => set(initialState),
}))
