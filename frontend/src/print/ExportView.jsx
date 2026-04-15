// src/print/ExportView.jsx
import React, { useMemo } from 'react';
import './print.css';

function normalizeUrl(u) {
  try {
    const url = new URL(u);
    // strip common tracking params
    ['utm_source','utm_medium','utm_campaign','utm_term','utm_content','gclid','fbclid'].forEach(p => url.searchParams.delete(p));
    // remove trailing slash
    if (url.pathname.length > 1 && url.pathname.endsWith('/')) {
      url.pathname = url.pathname.slice(0, -1);
    }
    return url.toString();
  } catch {
    return (u || '').trim();
  }
}

function getTitleFromMessages(messages) {
  const firstUser = messages?.find?.(m => m.role === 'user');
  return (firstUser?.content || 'Untitled Chat').slice(0, 100);
}

export function ExportView({ chatId, title, messages }) {
  const exportedAt = new Date().toLocaleString('en-US');
  const safeTitle = title || getTitleFromMessages(messages || []);

  // Build consolidated reference index + per-message mapping
  const { refList, msgRefNums } = useMemo(() => {
    const map = new Map(); // normalizedUrl -> { index, title, url }
    const perMsg = [];
    let idx = 1;

    (messages || []).forEach((m) => {
      if (m.role !== 'assistant' || !Array.isArray(m.citations)) {
        perMsg.push([]);
        return;
      }
      const nums = [];
      m.citations.forEach((c) => {
        const norm = normalizeUrl(c?.url || '');
        if (!norm) return;
        if (!map.has(norm)) {
          map.set(norm, { index: idx++, title: c?.title || norm, url: norm });
        }
        nums.push(map.get(norm).index);
      });
      perMsg.push(nums);
    });

    const list = Array.from(map.values()).sort((a, b) => a.index - b.index);
    return { refList: list, msgRefNums: perMsg };
  }, [messages]);

  return (
    <div className="print-wrap">
      {/* Cover */}
      <section className="cover">
        <div className="app">Med-Pal AI — Chat Export</div>
        <h1 className="title">{safeTitle}</h1>
        <div className="meta">
          <div><strong>Chat ID:</strong> <code>{chatId || 'N/A'}</code></div>
          <div><strong>Exported:</strong> {exportedAt}</div>
          <div><strong>Total messages:</strong> {messages?.length ?? 0}</div>
        </div>
        <p className="disclaimer">
          This export summarizes an AI-assisted conversation. Verify sources before clinical decisions.
        </p>
      </section>

      {/* Optional header for subsequent pages (MVP: appears once; Chrome lacks true running headers) */}
      <div className="running-header">
        Med-Pal AI — Chat Export • {safeTitle}
      </div>

      {/* Thread */}
      <section className="thread">
        {(messages || []).map((m, i) => (
          <article key={i} className={`msg ${m.role}`}>
            <header className="msg-head">
              <span className="who">{m.role === 'user' ? 'User' : 'Assistant'}</span>
              {m.createdAt && (
                <time>
                  {new Date(m.createdAt).toLocaleString('en-US')}
                </time>
              )}
              {m.role === 'assistant' && typeof m.confidence === 'number' && (
                <span className="conf">Confidence: {Math.round(m.confidence * 100)}%</span>
              )}
              {m.updated && <span className="tag">Updated</span>}
            </header>

            <div className="msg-body">
              {/* React escapes by default; preserves safety. */}
              {m.content}
            </div>

            {m.role === 'assistant' && (msgRefNums[i]?.length > 0) && (
              <footer className="msg-citations">
                <div className="label">Citations</div>
                <ol>
                  {msgRefNums[i].map((n) => {
                    const ref = refList.find(r => r.index === n);
                    return (
                      <li key={n}>
                        <span>[{n}] </span>
                        <span>{ref?.title || 'Untitled'}</span>
                        {ref?.url && <> — <a href={ref.url}>{ref.url}</a></>}
                      </li>
                    );
                  })}
                </ol>
              </footer>
            )}
          </article>
        ))}
      </section>

      {/* References */}
      {refList.length > 0 && (
        <section className="references">
          <h2>References</h2>
          <ol>
            {refList.map((r) => (
              <li key={r.index}>
                <span>[{r.index}] </span>
                <span>{r.title}</span>{' '}
                {r.url && <a href={r.url}>{r.url}</a>}
              </li>
            ))}
          </ol>
        </section>
      )}

      {/* MVP footer note (Chrome can't do true running footers in print CSS) */}
      <div className="footer-note">
        Exported: {exportedAt}
      </div>
    </div>
  );
}

export default ExportView;
