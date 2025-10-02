import React from 'react'
export default function SourceList({ items=[] }) {
  return (
    <div className='space-y-3'>
      {items.map((s, idx) => (
        <a key={idx} href={s.url} target='_blank' rel='noreferrer'
           className='block rounded-xl border border-gray-200 bg-white p-3 hover:border-gray-300 shadow-sm'>
          <div className='flex items-start justify-between gap-3'>
            <div>
              <div className='text-sm font-semibold text-gray-900'>[{idx+1}] {s.title}</div>
              <div className='text-xs text-gray-600 mt-1'>{s.snippet}</div>
            </div>
            <span className='text-xs text-blue-600'>Open ↗</span>
          </div>
        </a>
      ))}
      {items.length === 0 && <div className='text-sm text-gray-500'>No sources yet. Ask a question.</div>}
    </div>
  )
}
