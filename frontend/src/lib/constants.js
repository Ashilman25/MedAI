// Centralised constants — import these instead of reading env vars inline.
export const DEFAULT_TOP_K = Number(import.meta.env.VITE_DEFAULT_TOP_K ?? 5)
export const CONFIDENCE_THRESHOLD = Number(import.meta.env.VITE_CONFIDENCE_THRESHOLD ?? 0.55)
export const SHOW_SCAN_TERMS = (import.meta.env.VITE_SHOW_SCAN_TERMS ?? 'true') === 'true'
export const MAX_QUERY_LENGTH = 5000
export const MAX_FILE_SIZE = 25 * 1024 * 1024 // 25 MB
