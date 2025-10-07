// src/components/Docs/AddSourcesModal.jsx
import React, { useEffect, useMemo, useRef, useState } from "react";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import { useAuth } from "../../context/AuthContext";
import { expandSources } from "../../lib/api";
import { saveSourceSet } from "../../lib/db";


const PUB_TYPES = [
  "Guideline",
  "Practice Guideline",
  "Systematic Review",
  "Review",
  "Meta-Analysis",
  "Randomized Controlled Trial",
];

function parseKeywords(input) {
  return Array.from(
    new Set(
      (input || "")
        .split(/[\n,]/g)
        .map((s) => s.trim())
        .filter(Boolean)
    )
  );
}

// concurrency pool runner
async function runPool(items, limit, task, onStep) {
  const results = new Array(items.length);
  let nextIndex = 0;
  let active = 0;

  return await new Promise((resolve) => {
    function launch() {
      while (active < limit && nextIndex < items.length) {
        const i = nextIndex++;
        active++;
        onStep?.(i, "start");
        Promise.resolve(task(items[i], i))
          .then((res) => {
            results[i] = { ok: true, value: res };
            onStep?.(i, "done", res);
          })
          .catch((err) => {
            results[i] = { ok: false, error: err };
            onStep?.(i, "error", err);
          })
          .finally(() => {
            active--;
            if (nextIndex >= items.length && active === 0) resolve(results);
            else launch();
          });
      }
    }
    launch();
  });
}

function Chip({ children }) {
  return (
    <span className="inline-flex items-center rounded-full border border-gray-300 px-2 py-0.5 text-xs text-gray-600 dark:border-gray-700 dark:text-gray-300">
      {children}
    </span>
  );
}

function Spinner() {
  return (
    <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
  );
}

function InfoIcon({ className = "" }) {
  return (
    <svg
      viewBox="0 0 24 24"
      aria-hidden="true"
      className={`h-4 w-4 text-white ${className}`}
    >
      <circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" strokeWidth="2" />
      <path
        d="M9.5 9a2.5 2.5 0 1 1 4.1 1.9c-.7.5-1.1.9-1.1 1.6v.25"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        fill="none"
      />
      <circle cx="12" cy="17.2" r="1" fill="currentColor" />
    </svg>
  );
}

function Tooltip({ text, children }) {
  return (
    <span className="relative inline-flex items-center group" tabIndex={0}>
      {children}
      <span
        role="tooltip"
        className="
          pointer-events-none absolute left-1/2 top-full z-[100] mt-2 -translate-x-1/2
          whitespace-nowrap rounded-md border border-gray-200 bg-white px-2 py-1
          text-xs text-gray-700 opacity-0 shadow-lg transition-opacity duration-150
          group-hover:opacity-100 group-focus:opacity-100
          dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100
        "
      >
        {text}
      </span>
    </span>
  );
}


export default function AddSourcesModal({ open, onClose, onComplete }) {
  const { user } = useAuth();
  const prefersReducedMotion = useReducedMotion();
  const [phase, setPhase] = useState("form"); // 'form' | 'running' | 'done'
  const [keywordsInput, setKeywordsInput] = useState("");
  const [minDate, setMinDate] = useState(2018);
  const [lang, setLang] = useState("en");
  const [types, setTypes] = useState(() => new Set(PUB_TYPES.slice(0, 4))); // default: 4 checked
  

  
  
  const [targetConfidence, setTargetConfidence] = useState(
    Number(import.meta.env.VITE_CONFIDENCE_THRESHOLD ?? 0.62)
  );

  const [maxPasses, setMaxPasses] = useState(3);
  const [perPassRetmax, setPerPassRetmax] = useState(
    Number(import.meta.env.VITE_PER_PASS_RETMAX ?? 60)
  );

  const [topK, setTopK] = useState(
    Number(import.meta.env.VITE_DEFAULT_TOP_K ?? 5)
  );

  const [concurrency, setConcurrency] = useState(1); // nice-to-have
  const [saveSet, setSaveSet] = useState(false); // nice-to-have
  const [setName, setSetName] = useState("");
  const [expandedAdvanced, setExpandedAdvanced] = useState(false);
  const [progress, setProgress] = useState([]); // [{term,status,found,added,skipped,passes,error}]
  const [overallPct, setOverallPct] = useState(0);
  const [summary, setSummary] = useState({ found: 0, added: 0, skipped: 0, passes: 0 });

  const controllersRef = useRef([]); // for cancellation
  const cancelledRef = useRef(false);

  function handleCancel() {
    cancelledRef.current = true;
    controllersRef.current.forEach((c) => c?.abort?.());
    onClose?.();
  }


  const terms = useMemo(() => parseKeywords(keywordsInput), [keywordsInput]);
  const selectedTypes = useMemo(() => Array.from(types), [types]);

  useEffect(() => {
    if (!open) {
      // reset modal state when closed
      setPhase("form");
      setProgress([]);
      setOverallPct(0);
      setSummary({ found: 0, added: 0, skipped: 0, passes: 0 });
      controllersRef.current.forEach((c) => c?.abort?.());
      controllersRef.current = [];
    }
  }, [open]);

  if (!open) return null;

  function toggleType(t) {
    setTypes((prev) => {
      const next = new Set(prev);
      if (next.has(t)) next.delete(t);
      else next.add(t);
      return next;
    });
  }

  async function handleSearch() {
    if (!user) return;

    const queue = parseKeywords(keywordsInput);
    if (queue.length === 0) return;

    // Optional: save "source set" (unchanged)
    if (saveSet && setName.trim()) {
      try {
        await saveSourceSet(user.uid, {
          name: setName.trim(),
          keywords: queue,
          options: {
            minDate,
            lang,
            types: selectedTypes,
            targetConfidence,
            maxPasses,
            perPassRetmax,
            topK,
            concurrency: 1, // we force sequential now
          },
          createdAt: Date.now(),
        });
      } catch (_) {}
    }

    // Reset & enter running phase
    cancelledRef.current = false;
    controllersRef.current = [];
    setPhase("running");
    setProgress(queue.map((t) => ({ term: t, status: "Queued" })));
    setOverallPct(0);

    const totals = { found: 0, added: 0, skipped: 0, passes: 0 };

    // Sequential loop: strictly one keyword at a time
    for (let i = 0; i < queue.length; i++) {
      const term = queue[i];
      if (cancelledRef.current) break;

      // small helper to update one row
      const updateRow = (patch) =>
        setProgress((prev) => {
          const next = [...prev];
          next[i] = { ...next[i], ...patch };
          return next;
        });

      try {
        updateRow({ status: "Searching…" });

        const ctrl = new AbortController();
        controllersRef.current = [ctrl]; // only keep current one
        const res = await expandSources(term, {
          owner_uid: user.uid,
          wide: true,
          lang,
          mindate: minDate || undefined,
          types: selectedTypes.length ? selectedTypes : undefined,
          target_confidence: targetConfidence,
          max_passes: maxPasses,
          per_pass_retmax: perPassRetmax,
          top_k: topK,
          signal: ctrl.signal, // pass abort signal through
        });

        if (cancelledRef.current) break;

        updateRow({ status: `Found ${res.found}…` });
        updateRow({ status: "Ingesting…" });
        updateRow({
          status: `Added ${res.added} (Skipped ${res.skipped})`,
          found: res.found,
          added: res.added,
          skipped: res.skipped,
          passes: res.passes,
        });
        updateRow({ status: "Answering…" });
        updateRow({ status: "Done" });

        totals.found += Number(res.found || 0);
        totals.added += Number(res.added || 0);
        totals.skipped += Number(res.skipped || 0);
        totals.passes += Number(res.passes || 0);
      } catch (err) {
        updateRow({
          status: "Error",
          error: err?.message || "Request failed",
        });
      } finally {
        const pct = Math.round(((i + 1) / queue.length) * 100);
        setOverallPct(pct);
      }
    }

    if (!cancelledRef.current) {
      setSummary(totals);
      setPhase("done");
    }
  }


  async function handleCloseAndRefresh() {
    await onComplete?.();
    onClose?.();
  }

  return (
    <AnimatePresence>
      {open && (
        <>
          {/* Backdrop */}
          <motion.div
            key="backdrop"
            className="fixed inset-0 z-[80] bg-black/30 backdrop-blur-sm"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          />

          {/* Modal card */}
          <motion.div
            key="modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="add-sources-title"
            className="fixed inset-0 z-[90] grid place-items-center p-4"
            initial={prefersReducedMotion ? {} : { opacity: 0, scale: 0.98, y: 8 }}
            animate={prefersReducedMotion ? {} : { opacity: 1, scale: 1, y: 0 }}
            exit={prefersReducedMotion ? {} : { opacity: 0, scale: 0.98, y: 8 }}
            transition={{ duration: 0.18 }}
          >
            <div className="w-full max-w-2xl rounded-2xl border border-gray-200 bg-white shadow-xl dark:border-gray-800 dark:bg-gray-900">
              <div className="flex items-center justify-between border-b border-gray-200 px-5 py-4 dark:border-gray-800">
                <h2 id="add-sources-title" className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                  Add Sources (PubMed)
                </h2>
                <button
                  onClick={handleCancel}
                  className="rounded-full px-2 py-1 text-sm text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800"
                >
                  ✕
                </button>
              </div>

              {/* Body */}
              <div className="px-5 py-4">
                {phase === "form" && (
                  <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                    <div className="sm:col-span-2">
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-200">
                        Keywords
                      </label>
                      <textarea
                        value={keywordsInput}
                        onChange={(e) => setKeywordsInput(e.target.value)}
                        rows={3}
                        placeholder="Comma or newline separated. Each becomes its own PubMed search."
                        className="mt-1 w-full rounded-lg border border-gray-300 bg-white/80 p-2 text-sm outline-none focus:ring-2 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100"
                      />
                      <div className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                        Parsed: {parseKeywords(keywordsInput).length} term(s)
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-200">
                        Min Date (Year)
                      </label>
                      <input
                        type="number"
                        inputMode="numeric"
                        min="1900"
                        max={new Date().getFullYear()}
                        value={minDate}
                        onChange={(e) => setMinDate(Number(e.target.value || 0))}
                        className="mt-1 w-full rounded-lg border border-gray-300 bg-white/80 p-2 text-sm outline-none focus:ring-2 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-200">
                        Language
                      </label>
                      <select
                        value={lang}
                        onChange={(e) => setLang(e.target.value)}
                        className="mt-1 w-full rounded-lg border border-gray-300 bg-white/80 p-2 text-sm outline-none focus:ring-2 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100"
                      >
                        <option value="en">English</option>
                        <option value="es">Spanish</option>
                        <option value="fr">French</option>
                        <option value="de">German</option>
                        <option value="pt">Portuguese</option>
                        <option value="it">Italian</option>
                        <option value="zh">Chinese</option>
                        <option value="ja">Japanese</option>
                        <option value="ko">Korean</option>
                        <option value="ar">Arabic</option>
                      </select>
                    </div>

                    <div className="sm:col-span-2">
                      <div className="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-200">
                        Publication Types
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {PUB_TYPES.map((t) => (
                          <label key={t} className="inline-flex cursor-pointer items-center gap-2 rounded-full border border-gray-300 px-3 py-1 text-xs text-gray-700 dark:border-gray-700 dark:text-gray-200">
                            <input
                              type="checkbox"
                              className="h-3 w-3"
                              checked={types.has(t)}
                              onChange={() => toggleType(t)}
                            />
                            {t}
                          </label>
                        ))}
                      </div>
                    </div>

                    {/* Advanced */}
                    <div className="sm:col-span-2">
                      <button
                        type="button"
                        onClick={() => setExpandedAdvanced((v) => !v)}
                        className="flex w-full items-center justify-between rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-left text-sm font-medium text-gray-700 hover:bg-gray-100 dark:border-gray-800 dark:bg-gray-800/60 dark:text-gray-200 dark:hover:bg-gray-800"
                      >
                        Advanced options
                        <span className="text-xs text-gray-500">{expandedAdvanced ? "▲" : "▼"}</span>
                      </button>
                      <AnimatePresence initial={false}>
                        {expandedAdvanced && (
                          <motion.div
                            initial={{ height: 0, opacity: 0 }}
                            animate={{ height: "auto", opacity: 1 }}
                            exit={{ height: 0, opacity: 0 }}
                            className="mt-3 grid grid-cols-1 gap-3 sm:grid-cols-2"
                          >
                            <div>
                              <label className="block text-sm font-medium text-gray-700 dark:text-gray-200">
                                <div className="flex items-center justify-between">
                                  <span>Target confidence (0-1)</span>
                                  <Tooltip text="Minimum confidence to keep a source. Higher = stricter, fewer.">
                                    <InfoIcon className="ml-2" />
                                  </Tooltip>
                                </div>
                              </label>
                              <input
                                type="number"
                                step="0.01"
                                min="0"
                                max="1"
                                value={targetConfidence}
                                onChange={(e) =>
                                  setTargetConfidence(
                                    Math.max(0, Math.min(1, Number(e.target.value || 0)))
                                  )
                                }
                                className="mt-1 w-full rounded-lg border border-gray-300 bg-white/80 p-2 text-sm outline-none focus:ring-2 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100"
                              />
                            </div>
                            <div>
                              <label className="block text-sm font-medium text-gray-700 dark:text-gray-200">
                                <div className="flex items-center justify-between">
                                  <span>Max passes</span>
                                  <Tooltip text="How many search/refinement rounds per keyword.">
                                    <InfoIcon className="ml-2" />
                                  </Tooltip>
                                </div>
                              </label>
                              <input
                                type="number"
                                min="1"
                                max="5"
                                value={maxPasses}
                                onChange={(e) => setMaxPasses(Number(e.target.value || 1))}
                                className="mt-1 w-full rounded-lg border border-gray-300 bg-white/80 p-2 text-sm outline-none focus:ring-2 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100"
                              />
                            </div>
                            <div>
                              <label className="block text-sm font-medium text-gray-700 dark:text-gray-200">
                                <div className="flex items-center justify-between">
                                  <span>Per-pass retmax</span>
                                  <Tooltip text="Max PubMed results fetched per pass.">
                                    <InfoIcon className="ml-2" />
                                  </Tooltip>
                                </div>
                              </label>
                              <input
                                type="number"
                                min="10"
                                max="500"
                                value={perPassRetmax}
                                onChange={(e) => setPerPassRetmax(Number(e.target.value || 10))}
                                className="mt-1 w-full rounded-lg border border-gray-300 bg-white/80 p-2 text-sm outline-none focus:ring-2 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100"
                              />
                            </div>
                            <div>
                              <label className="block text-sm font-medium text-gray-700 dark:text-gray-200">
                                <div className="flex items-center justify-between">
                                  <span>Top-K</span>
                                  <Tooltip text="Number of top-scoring items kept for answering.">
                                    <InfoIcon className="ml-2" />
                                  </Tooltip>
                                </div>
                              </label>
                              <input
                                type="number"
                                min="1"
                                max="20"
                                value={topK}
                                onChange={(e) => setTopK(Number(e.target.value || 1))}
                                className="mt-1 w-full rounded-lg border border-gray-300 bg-white/80 p-2 text-sm outline-none focus:ring-2 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100"
                              />
                            </div>
                            <div className="sm:col-span-2 mt-2">
                              <label className="inline-flex items-center gap-2 text-sm text-gray-700 dark:text-gray-200">
                                <input
                                  type="checkbox"
                                  checked={saveSet}
                                  onChange={(e) => setSaveSet(e.target.checked)}
                                />
                                Save this configuration as a “Source Set”
                              </label>
                              {saveSet && (
                                <input
                                  type="text"
                                  placeholder="Source set name"
                                  value={setName}
                                  onChange={(e) => setSetName(e.target.value)}
                                  className="mt-2 w-full rounded-lg border border-gray-300 bg-white/80 p-2 text-sm outline-none focus:ring-2 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100"
                                />
                              )}
                            </div>
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </div>
                  </div>
                )}

                {phase === "running" && (
                  <div>
                    <div className="mb-3 text-sm text-gray-600 dark:text-gray-300">
                        Running {progress.length} search{progress.length !== 1 ? "es" : ""}…
                    </div>

                    <div className="mb-4 h-2 w-full overflow-hidden rounded-full bg-gray-100 dark:bg-gray-800">
                      <div
                        className="h-full bg-blue-600 transition-all dark:bg-blue-500"
                        style={{ width: `${overallPct}%` }}
                      />
                    </div>
                    <div className="space-y-2">
                      {progress.map((p, i) => (
                        <motion.div
                          key={p.term + i}
                          initial={{ opacity: 0, y: 6 }}
                          animate={{ opacity: 1, y: 0 }}
                          className="flex items-center justify-between rounded-lg border border-gray-200 bg-white p-3 text-sm dark:border-gray-800 dark:bg-gray-800/50"
                        >
                          <div className="min-w-0">
                            <div className="truncate font-medium text-gray-900 dark:text-gray-100">
                              {p.term}
                            </div>
                            <div className="mt-0.5 truncate text-xs text-gray-600 dark:text-gray-300">
                              {p.status}
                            </div>
                          </div>
                          <div className="flex shrink-0 items-center gap-2">
                            {p.status === "Done" ? (
                              <Chip>Added {p.added ?? 0}</Chip>
                            ) : p.status?.toLowerCase().includes("error") ? (
                              <Chip>Error</Chip>
                            ) : (
                              <Spinner />
                            )}
                          </div>
                        </motion.div>
                      ))}
                    </div>
                  </div>
                )}

                {phase === "done" && (
                  <div className="text-sm">
                    <div className="rounded-lg border border-green-200 bg-green-50 p-4 text-green-800 dark:border-green-900/50 dark:bg-green-900/20 dark:text-green-200">
                      <div className="font-medium">All searches complete.</div>
                      <div className="mt-1">
                        Fetched {summary.found}, added {summary.added}, skipped {summary.skipped} across {summary.passes} pass
                        {summary.passes === 1 ? "" : "es"}.
                      </div>
                    </div>
                    <div className="mt-4 flex flex-wrap gap-2">
                      <Chip>Lang: {lang}</Chip>
                      {minDate ? <Chip>Min date: {minDate}</Chip> : null}
                      {selectedTypes.map((t) => (
                        <Chip key={t}>{t}</Chip>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Footer */}
              <div className="flex items-center justify-end gap-3 border-t border-gray-200 px-5 py-3 dark:border-gray-800">
                {phase === "form" && (
                  <>
                    <button
                      onClick={handleCancel}
                      className="rounded-full border border-gray-300 px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-100 dark:border-gray-700 dark:text-gray-200 dark:hover:bg-gray-800"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleSearch}
                      disabled={!terms.length}
                      className={`rounded-full px-4 py-1.5 text-sm ${
                        terms.length
                          ? "bg-gray-900 text-white hover:opacity-95 dark:bg-gray-100 dark:text-gray-900"
                          : "cursor-not-allowed bg-gray-300 text-gray-600 dark:bg-gray-700 dark:text-gray-400"
                      }`}
                    >
                      Search
                    </button>
                  </>
                )}
                {phase === "running" && (
                  <>
                    <button
                      onClick={handleCancel}
                      className="rounded-full border border-gray-300 px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-100 dark:border-gray-700 dark:text-gray-200 dark:hover:bg-gray-800"
                    >
                      Cancel
                    </button>
                  </>
                )}
                {phase === "done" && (
                  <>
                    <button
                      onClick={handleCloseAndRefresh}
                      className="rounded-full bg-gray-900 px-4 py-1.5 text-sm text-white hover:opacity-95 dark:bg-gray-100 dark:text-gray-900"
                    >
                      Close &amp; Refresh Docs
                    </button>
                  </>
                )}
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
