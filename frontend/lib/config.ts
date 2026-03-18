const rawApiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

export const API_URL = rawApiUrl
  .trim()
  .replace(/\/+$/, "")
  .replace(/\.onrender\.co(?=\/|$)/, ".onrender.com")

export const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL ?? ""
export const SUPABASE_ANON_KEY = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ?? ""
