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

export async function listDocuments() {
  const API_BASE = import.meta.env.VITE_API_BASE_URL || "";
  const r = await fetch(`${API_BASE}/documents`, { method: "GET" });
  if (!r.ok) throw new Error(`API error: ${r.status}`);
  return r.json();
}


export async function expandSources(query, options = {}) {
  const API_BASE = import.meta.env.VITE_API_BASE_URL || "";
  const body = {
    query,
    top_k: options.top_k ?? Number(import.meta.env.VITE_DEFAULT_TOP_K ?? 5),
    wide: options.wide ?? true,
    target_confidence: options.target_confidence ?? Number(import.meta.env.VITE_CONFIDENCE_THRESHOLD ?? 0.62),
    max_passes: options.max_passes ?? 3,
    per_pass_retmax: options.per_pass_retmax ?? 60,
    mindate: options.mindate ?? 2018,
    fallback_mindate: options.fallback_mindate ?? 2010,
    lang: options.lang ?? "en",
    types: options.types ?? ["Guideline","Practice Guideline","Systematic Review","Review"],
  };
  const r = await fetch(`${API_BASE}/expand-sources`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error(`API error: ${r.status}`);
  return r.json();
}