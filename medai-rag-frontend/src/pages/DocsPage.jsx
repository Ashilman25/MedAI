// src/pages/DocsPage.jsx
import { useEffect, useMemo, useState } from "react";
import { useRef } from "react";
import { listDocuments } from "../lib/api";
import { motion, useReducedMotion } from "framer-motion";
import { useAuth } from "../context/AuthContext"; 
import AddSourcesModal from "../components/Docs/AddSourcesModal";

const PAGE_SIZE = 20;

const badgeStyles = {
  pubmed: "text-teal-700 border-teal-300",
  local: "text-gray-700 border-gray-300",
  other: "text-blue-700 border-blue-300",
};

function SourceBadge({ source = "other" }) {
  const key = (source || "other").toLowerCase();
  const cls = badgeStyles[key] || badgeStyles.other;
  const label = key === "pubmed" ? "PubMed" : key === "local" ? "Local" : "Other";
  return (
    <span className={`inline-flex items-center px-2 py-0.5 text-xs border rounded-full ${cls}`}>
      {label}
    </span>
  );
}

export default function DocsPage() {
  const { user, authLoading } = useAuth();
  const reqIdRef = useRef(0);

  const [docs, setDocs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState(null);
  const [q, setQ] = useState("");
  const [srcFilter, setSrcFilter] = useState("all"); // all | pubmed | local | other
  const [page, setPage] = useState(1);
  const [showAdd, setShowAdd] = useState(false); 
  const prefersReducedMotion = useReducedMotion();


  async function refreshDocs() {
    const myReqId = ++reqIdRef.current;

    try {

      setLoading(true);
      const data = await listDocuments(user?.uid);
      if (myReqId !== reqIdRef.current) return;
      setDocs(Array.isArray(data.docs) ? data.docs : []);
      setErr(null);

    } catch (e) {

      if (myReqId !== reqIdRef.current) return;
      setErr(e?.message || "Failed to load documents");

    } finally {
      if (myReqId === reqIdRef.current) setLoading(false);
    }
  }

  useEffect(() => {
    if (!authLoading) {
      refreshDocs();
    }

  }, [authLoading, user?.uid]);

  useEffect(() => {
    if (showAdd) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }

    return () => {
      document.body.style.overflow = "";
    };
  }, [showAdd]);

  // Filter
  const filtered = useMemo(() => {
    const needle = q.trim().toLowerCase();
    return docs.filter((d) => {
      const matchesText =
        !needle ||
        (d.title || "").toLowerCase().includes(needle) ||
        (d.journal || "").toLowerCase().includes(needle) ||
        (d.snippet || "").toLowerCase().includes(needle) ||
        (String(d.pmid || "")).toLowerCase().includes(needle);
      const matchesSrc =
        srcFilter === "all" || (d.source || "other").toLowerCase() === srcFilter;
      return matchesText && matchesSrc;
    });
  }, [docs, q, srcFilter]);

  // Reset to page 1 when filters/search change
  useEffect(() => {
    setPage(1);
  }, [q, srcFilter]);

  // Pagination math
  const total = filtered.length;
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));
  const startIdx = (page - 1) * PAGE_SIZE;
  const endIdx = Math.min(startIdx + PAGE_SIZE, total);
  const pageItems = filtered.slice(startIdx, endIdx);

  // Scroll to top of list on page change
  useEffect(() => {
    const el = document.getElementById("docs-list-top");
    if (el) el.scrollIntoView({ behavior: prefersReducedMotion ? "auto" : "smooth", block: "start" });
  }, [page, prefersReducedMotion]);

  return (
    <div className="min-h-screen w-full bg-white dark:bg-gray-900">
      <div className="mx-auto max-w-5xl px-4 py-8">
        <header className="mb-6">
          <h1 className="text-3xl font-semibold tracking-tight text-gray-900 dark:text-gray-100">
            Indexed Documents
          </h1>
          <p className="mt-1 text-sm text-gray-500">Local &amp; PubMed Sources</p>
        </header>

        {/* Controls */}
        <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <input
            type="search"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Search title, journal, PMID, or snippet…"
            className="w-full sm:max-w-md rounded-lg border border-gray-300 bg-white/80 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-800 dark:border-gray-700 dark:text-gray-100"
          />
          <div className="flex items-center gap-2">
            {["all", "pubmed", "local", "other"].map((k) => (
              <button
                key={k}
                onClick={() => setSrcFilter(k)}
                className={`rounded-full border px-3 py-1 text-xs transition ${
                  srcFilter === k
                    ? "border-blue-500 text-blue-700 dark:text-blue-300"
                    : "border-gray-300 text-gray-600 dark:border-gray-700 dark:text-gray-300"
                }`}
              >
                {k[0].toUpperCase() + k.slice(1)}
              </button>
            ))}

            {/* Add Sources (signed-in only) */}
            {user && (
              <button
                onClick={() => setShowAdd(true)}
                className="ml-1 rounded-full border border-gray-300 px-3 py-1.5 text-xs font-medium text-gray-700 hover:bg-gray-100 dark:border-gray-700 dark:text-gray-200 dark:hover:bg-gray-800"
              >
                + Add Sources
              </button>
            )}
          </div>
        </div>

        {/* Status row */}
        {!loading && !err && (
          <div className="mb-2 flex items-center justify-between text-xs text-gray-500">
            <span>{total > 0 ? `Results ${startIdx + 1}–${endIdx} of ${total}` : "No results"}</span>
            <span>Page {page} / {totalPages}</span>
          </div>
        )}

        {/* Body */}
        {loading && (
          <div className="mt-10 text-center">
            <div className="mx-auto h-8 w-8 animate-spin rounded-full border-2 border-blue-500 border-t-transparent" />
            <p className="mt-3 text-sm text-gray-500">Loading documents…</p>
          </div>
        )}

        {err && !loading && (
          <div className="mt-6 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            {err}
          </div>
        )}

        {!loading && !err && filtered.length === 0 && (
          <div className="mt-10 rounded-xl border border-gray-200 bg-gray-50 p-8 text-center text-sm text-gray-600 dark:border-gray-800 dark:bg-gray-800/40 dark:text-gray-300">
            {user ? (
              "No documents yet. Try Add Sources or upload local files."
            ) : (
              "Sign in to add and view your sources."
            )}
          </div>
        )}

        {/* List */}
        <div id="docs-list-top" />
        <div className="mt-4 grid grid-cols-1 gap-3">
          {pageItems.map((d, i) => (
            <motion.a
              key={`${d.url || d.title || i}-${startIdx + i}`}
              href={d.url || "#"}
              target="_blank"
              rel="noreferrer"
              initial={prefersReducedMotion ? false : { opacity: 0, y: 6 }}
              animate={prefersReducedMotion ? {} : { opacity: 1, y: 0 }}
              transition={{ duration: 0.15 }}
              className="block rounded-xl border border-gray-200/60 bg-gradient-to-r from-white to-gray-50 p-4 shadow-sm transition hover:shadow-md dark:from-gray-900 dark:to-gray-800 dark:border-gray-800"
              whileHover={prefersReducedMotion ? {} : { scale: 1.01 }}
            >
              <div className="flex items-start justify-between gap-3">
                <h3 className="text-base font-medium text-gray-900 dark:text-gray-100">
                  {d.title || "Untitled"}
                </h3>
                <div className="flex items-center gap-2">
                  <SourceBadge source={d.source} />
                    {d.owner_scope && (
                      <span
                        className={`inline-flex items-center rounded-full border px-2 py-0.5 text-[10px] ${
                          d.owner_scope === "mine"
                          ? "border-emerald-300 text-emerald-700"
                          : "border-gray-300 text-gray-600"
                      }`}
                      title={d.owner_scope === "mine" ? "Visible only to you" : "Visible to everyone"}
                    >
                      {d.owner_scope === "mine" ? "Mine" : "Global"}
                    </span>
                  )}
                  </div>
              </div>
              <p className="mt-1 line-clamp-3 text-sm text-gray-600 dark:text-gray-300">
                {d.snippet || "—"}
              </p>
              <div className="mt-2 flex flex-wrap items-center gap-3 text-xs text-gray-500">
                {d.journal && <span className="truncate">{d.journal}</span>}
                {d.year && <span>• {d.year}</span>}
                {d.pmid && (
                  <span className="rounded border border-gray-200 px-1.5 py-0.5 dark:border-gray-700">
                    PMID: {d.pmid}
                  </span>
                )}
              </div>
            </motion.a>
          ))}
        </div>

        {/* Pagination controls */}
        {!loading && !err && totalPages > 1 && (
          <div className="mt-6 flex items-center justify-between">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              className={`rounded-lg px-3 py-1.5 text-sm border ${
                page === 1
                  ? "text-gray-400 border-gray-200 cursor-not-allowed"
                  : "text-gray-700 border-gray-300 hover:bg-gray-50 dark:text-gray-200 dark:border-gray-700"
              }`}
            >
              ← Prev
            </button>
            <div className="hidden sm:flex gap-1">
              {Array.from({ length: totalPages }).slice(0, 7).map((_, idx) => {
                const p = idx + 1;
                return (
                  <button
                    key={p}
                    onClick={() => setPage(p)}
                    className={`rounded-md px-2.5 py-1 text-sm border ${
                      p === page
                        ? "border-blue-500 text-blue-700 dark:text-blue-300"
                        : "border-gray-300 text-gray-600 hover:bg-gray-50 dark:border-gray-700 dark:text-gray-300"
                    }`}
                  >
                    {p}
                  </button>
                );
              })}
              {totalPages > 7 && (
                <span className="px-2 py-1 text-sm text-gray-500">… {totalPages}</span>
              )}
            </div>
            <button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              className={`rounded-lg px-3 py-1.5 text-sm border ${
                page === totalPages
                  ? "text-gray-400 border-gray-200 cursor-not-allowed"
                  : "text-gray-700 border-gray-300 hover:bg-gray-50 dark:text-gray-200 dark:border-gray-700"
              }`}
            >
              Next →
            </button>
          </div>
        )}
      </div>

      {/* Modal */}
      <AddSourcesModal
        open={!!showAdd}
        onClose={() => setShowAdd(false)}
        onComplete={refreshDocs}
      />
    </div>
  );
}
