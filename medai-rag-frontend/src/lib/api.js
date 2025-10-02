const API_BASE = import.meta.env.VITE_API_BASE_URL || ''
const MOCK = (import.meta.env.VITE_MOCK_MODE ?? 'true') === 'true'
const DEFAULT_TOP_K = Number(import.meta.env.VITE_DEFAULT_TOP_K ?? 5)

export async function ask(query, top_k = DEFAULT_TOP_K) {
  if (MOCK || !API_BASE) {
    const { mockAsk } = await import('./mock')
    return mockAsk(query, top_k)
  }
  const r = await fetch(`${API_BASE}/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, top_k })
  })
  if (!r.ok) throw new Error(`API error: ${r.status}`)
  return r.json()
}

export async function ingest(file) {
  if (MOCK || !API_BASE) {
    const { mockIngest } = await import('./mock')
    return mockIngest(file)
  }
  const form = new FormData()
  form.append('files', file)
  const r = await fetch(`${API_BASE}/ingest`, { method: 'POST', body: form })
  if (!r.ok) throw new Error(`API error: ${r.status}`)
  return r.json()
}
