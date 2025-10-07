import React, { useState } from 'react'
import { ingest } from '../lib/api'
import { useAuth } from '../context/AuthContext'

export default function Upload() {
  const { user } = useAuth()
  const [file, setFile] = useState(null)
  const [status, setStatus] = useState('idle')
  const [result, setResult] = useState(null)
  async function onUpload() {
    if (!file) return
    setStatus('uploading')
    try {
      const res = await ingest(file, user?.uid)  // <-- pass uid so upload is PRIVATE to this user
      setResult(res); setStatus('done')
    } catch (e) {
      setResult({ error: e.message }); setStatus('error')
    }
  }
  return (
    <section className='mx-auto max-w-3xl px-4 sm:px-6 lg:px-8 py-10'>
      <h1 className='text-2xl font-bold mb-6'>Upload Clinical Docs (MVP)</h1>
      <div className='rounded-2xl border border-dashed border-gray-300 bg-white p-8 shadow-card'>
        <input type='file' accept='.pdf,.txt,.csv' onChange={e=>setFile(e.target.files?.[0]||null)} className='block w-full text-sm text-gray-700'/>
        <div className='flex gap-2 mt-4'>
        <button onClick={onUpload} disabled={!file || status==='uploading'} className='px-4 py-2 rounded-xl bg-medical-green text-white disabled:opacity-60'>
          {status==='uploading' ? 'Ingesting…' : 'Ingest'}
        </button>          <button onClick={()=>{setFile(null); setResult(null)}} className='px-4 py-2 rounded-xl border border-gray-300 bg-white'>Reset</button>
        </div>
        <div className='text-xs text-gray-500 mt-4'>Files stay local in mock mode and are sent to the backend when configured.</div>
        {status !== 'idle' && <pre className='mt-4 text-xs bg-gray-50 border border-gray-200 p-3 rounded-xl overflow-auto'>{JSON.stringify(result, null, 2)}</pre>}
      </div>
    </section>
  )
}
