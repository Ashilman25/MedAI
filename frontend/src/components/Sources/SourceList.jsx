import React from 'react'

export const Open = (props) => (
  <svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" viewBox="0 0 24 24" {...props}>
    <path fill="none" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2"
      d="M10 4H6a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-4m-8-2l8-8m0 0v5m0-5h-5" />
  </svg>
)

function SafeHost({ url }) {
  try { return <span>{new URL(url).hostname}</span> } catch { return null }
}

export default function SourceList({ items = [] }) {
  return (
    <div className="space-y-2">
      {items.map((s, idx) => (
        <a
          key={idx}
          href={s.url}
          target="_blank"
          rel="noreferrer"
          className="
            group relative block overflow-hidden
            rounded-xl border border-gray-200 bg-white p-4
            shadow-sm hover:border-gray-300 hover:shadow-md
            focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500
            transition
            min-h-[96px]
          "
        >
          {/* top-right open icon */}
          <span
            className="
              absolute right-3 top-3 inline-flex h-7 w-7 items-center justify-center
              rounded-md border border-gray-200 bg-gray-50 text-gray-600
              transition
              group-hover:border-gray-300 group-hover:bg-white group-hover:text-blue-600
            "
            aria-hidden="true"
          >
            <Open className="h-4 w-4" />
          </span>

          {/* left index badge + text stack */}
          <div className="flex items-start gap-3 pr-9">
            <div className="flex-none">
              <span
                className="
                  inline-flex h-6 w-6 items-center justify-center
                  rounded-lg bg-gray-100 text-[11px] font-semibold text-gray-700
                "
              >
                {idx + 1}
              </span>
            </div>

            <div className="min-w-0">
              <div className="text-sm font-semibold text-gray-900 leading-5 line-clamp-1 break-words">
                {s.title || s.url}
              </div>

              {s.snippet && (
                <div className="mt-1 text-xs text-gray-600 leading-5 line-clamp-2 break-words">
                  {s.snippet}
                </div>
              )}

              <div className="mt-2 text-[11px] text-gray-500 leading-4 line-clamp-1">
                <SafeHost url={s.url} />
              </div>
            </div>
          </div>
        </a>
      ))}

      {items.length === 0 && (
        <div className="text-sm text-gray-500">No sources yet. Ask a question.</div>
      )}
    </div>
  )
}
