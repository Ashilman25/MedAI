import React, { useState } from 'react'
import { ingest } from '../lib/api'
import { useAuth } from '../context/AuthContext'

export default function Upload() {
  const { user } = useAuth()
  const [file, setFile] = useState(null)
  const [status, setStatus] = useState('idle')
  const [message, setMessage] = useState('')

  const MAX_FILE_SIZE = 25 * 1024 * 1024 // 25MB

  async function onUpload() {
    if (!file) return
    if (file.size > MAX_FILE_SIZE) {
      setStatus('error')
      setMessage('❌ File too large (max 25MB)')
      return
    }
    setStatus('uploading')
    setMessage('')

    try {
      const res = await ingest(file)
      setStatus('done')
      setMessage(`✅ Successfully ingested "${file.name}"`)
      console.log('Ingest result:', res)
    } catch (e) {
      setStatus('error')
      setMessage(`❌ Error ingesting "${file.name}": ${e.message}`)
      console.error('Ingest error:', e)
    }
  }

  return (
    <section className='mx-auto max-w-3xl px-4 sm:px-6 lg:px-8 py-10'>
      <h1 className='text-2xl font-bold mb-6'>Upload Clinical Docs</h1>
      <div className='rounded-2xl border border-dashed border-gray-300 bg-white p-8 shadow-card'>
        <input
          type='file'
          accept='.pdf,.txt,.csv'
          onChange={e => setFile(e.target.files?.[0] || null)}
          className='block w-full text-sm text-gray-700'
        />
        <div className='flex gap-2 mt-4'>
          <button
            onClick={onUpload}
            disabled={!file || status === 'uploading'}
            className='px-4 py-2 rounded-xl bg-medical-green text-white disabled:opacity-60'
          >
            {status === 'uploading' ? 'Ingesting…' : 'Ingest'}
          </button>
          <button
            onClick={() => { setFile(null); setMessage('') }}
            className='px-4 py-2 rounded-xl border border-gray-300 bg-white'
          >
            Reset
          </button>
        </div>

        {message && (
          <div
            className={`mt-4 text-sm font-medium p-3 rounded-xl border ${
              status === 'done'
                ? 'bg-green-50 border-green-300 text-green-700'
                : status === 'error'
                ? 'bg-red-50 border-red-300 text-red-700'
                : 'bg-gray-50 border-gray-200 text-gray-700'
            }`}
          >
            {message}
          </div>
        )}
      </div>
    </section>
  )
}
