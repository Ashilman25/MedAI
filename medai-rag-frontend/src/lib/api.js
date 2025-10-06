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

export async function listDocuments(uid) {
  const API_BASE = import.meta.env.VITE_API_BASE_URL || "";
  const q = uid ? `?uid=${encodeURIComponent(uid)}` : "?uid="; // safe default: empty list server-side
  const r = await fetch(`${API_BASE}/documents${q}`, { method: "GET" });
  if (!r.ok) throw new Error(`API error: ${r.status}`);
  return r.json();
}


async function fetchWithRetry(url, options, retries = 3) {
  for (let i = 0; i <= retries; i++) {
    const res = await fetch(url, options);
    if (res.ok) return res;

    const retryable = res.status === 429 || res.status >= 500;
    if (!retryable || i === retries) {
      // surface original error when out of retries
      throw new Error(`API error: ${res.status}`);
    }

    const retryAfter = res.headers.get('retry-after');
    const delayMs = retryAfter ? Number(retryAfter) * 1000 : 500 * Math.pow(2, i);
    await new Promise((r) => setTimeout(r, delayMs));
  }
}

export async function expandSources(query, options = {}) {
  const body = {
    query,
    top_k: options.top_k ?? Number(import.meta.env.VITE_DEFAULT_TOP_K ?? 5),
    wide: options.wide ?? true,
    target_confidence:
      options.target_confidence ??
      Number(import.meta.env.VITE_CONFIDENCE_THRESHOLD ?? 0.62),
    max_passes: options.max_passes ?? 3,
    per_pass_retmax: options.per_pass_retmax ?? 60,
    mindate: options.mindate ?? 2018,
    fallback_mindate: options.fallback_mindate ?? 2010,
    lang: options.lang ?? 'en',
    types:
      options.types ??
      ['Guideline', 'Practice Guideline', 'Systematic Review', 'Review'],
    owner_uid: options.owner_uid ?? null,
  };

  const res = await fetchWithRetry(`${API_BASE}/expand-sources`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
    signal: options.signal,
  });
  return res.json();
}