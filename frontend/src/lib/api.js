import { getAuth } from 'firebase/auth';
import { DEFAULT_TOP_K, CONFIDENCE_THRESHOLD } from './constants'

const API_BASE = import.meta.env.VITE_API_BASE_URL || ''
const MOCK = (import.meta.env.VITE_MOCK_MODE ?? 'true') === 'true'

async function authHeaders() {
    const user = getAuth().currentUser;
    if (!user) return {};
    const token = await user.getIdToken();
    return { Authorization: `Bearer ${token}` };
}

export async function ask(query, top_k = DEFAULT_TOP_K, options = {}) {
  if (MOCK || !API_BASE) {
    const { mockAsk } = await import('./mock')
    return mockAsk(query, top_k)
  }
  const auth = await authHeaders();
  const r = await fetch(`${API_BASE}/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...auth },
    body: JSON.stringify({ query, top_k }),
    signal: options.signal,
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

  const auth = await authHeaders();
  const r = await fetch(`${API_BASE}/ingest`, { method: 'POST', headers: auth, body: form })

  if (!r.ok) throw new Error(`API error: ${r.status}`)
  return r.json()
}

export async function listDocuments() {
  const auth = await authHeaders();
  const r = await fetch(`${API_BASE}/documents`, { method: 'GET', headers: auth });
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
    top_k: options.top_k ?? DEFAULT_TOP_K,
    wide: options.wide ?? true,
    target_confidence: options.target_confidence ?? CONFIDENCE_THRESHOLD,
    max_passes: options.max_passes ?? 3,
    per_pass_retmax: options.per_pass_retmax ?? 60,
    mindate: options.mindate ?? 2018,
    fallback_mindate: options.fallback_mindate ?? 2010,
    lang: options.lang ?? 'en',
    types:
      options.types ??
      ['Guideline', 'Practice Guideline', 'Systematic Review', 'Review'],
  };

  if (options.query_terms?.length) body.query_terms = options.query_terms;
  if (options.intent) body.intent = options.intent;

  const auth = await authHeaders();
  const res = await fetchWithRetry(`${API_BASE}/expand-sources`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...auth },
    body: JSON.stringify(body),
    signal: options.signal,
  });
  return res.json();
}


export async function suggestTerms(message) {
  const auth = await authHeaders();
  const res = await fetch(`${API_BASE}/suggest-terms`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...auth },
    body: JSON.stringify({ message })
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

