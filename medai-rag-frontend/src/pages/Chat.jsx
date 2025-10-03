import React, { useEffect, useRef, useState } from 'react'
import MessageBubble from '../components/Chat/MessageBubble'
import SourceList from '../components/Sources/SourceList'
import ConfidenceBar from '../components/Sources/ConfidenceBar'
import { ask } from '../lib/api'
import { loadChat, saveChat, clearChat as clearStore } from '../store/localStore'
import { exportToPDF } from '../lib/export'

export default function Chat() {
  const [messages, setMessages] = useState(()=>loadChat())
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [lastAnswer, setLastAnswer] = useState(null)
  const scrollRef = useRef(null)

  useEffect(()=>{ saveChat(messages) }, [messages])
  useEffect(()=>{ scrollRef.current?.scrollTo(0, scrollRef.current.scrollHeight) }, [messages, loading])

  async function onSend() {
    const q = input.trim()
    if (!q) return
    setInput('')
    const id = crypto.randomUUID()
    const userMsg = { id, role: 'user', content: q }
    setMessages(m => [...m, userMsg])
    setLoading(true)
    try {
      const res = await ask(q)
      const aiMsg = { id: crypto.randomUUID(), role: 'assistant', content: res.answer, citations: res.citations, confidence: res.confidence }
      setMessages(m => [...m, aiMsg])
      setLastAnswer(res)
    } catch (e) {
      const aiMsg = { id: crypto.randomUUID(), role: 'assistant', content: `Error: ${e.message}` }
      setMessages(m => [...m, aiMsg])
      setLastAnswer(null)
    } finally {
      setLoading(false)
    }
  }

  function clearChat() {
    if (!confirm('Clear chat history?')) return
    setMessages([])
    setLastAnswer(null)
    clearStore()
  }

  return (
    <section className='mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-6'>
      <div className='grid lg:grid-cols-3 gap-6'>
        <div className='lg:col-span-2 rounded-2xl border border-gray-200 bg-white shadow-card flex flex-col h-[calc(100vh-200px)] print-area'>
          <header className='px-4 py-3 border-b border-gray-100 sticky top-0 bg-white z-10'>
            <div className='font-semibold'>Ask MedAI</div>
          </header>
          <div ref={scrollRef} className='flex-1 overflow-auto p-4 space-y-4'>
            {messages.length === 0 && <div className='text-sm text-gray-500'>Ask about treatments, drugs, or guidelines…</div>}
            {messages.map(m => (
              <MessageBubble key={m.id} role={m.role} content={m.content}>
                {m.role === 'assistant' && m.citations?.length > 0 && (
                  <div className='mt-3 space-y-1 text-xs'>
                    <div className='font-medium text-gray-900'>Citations:</div>
                    <ol className='list-decimal pl-5 space-y-1'>
                      {m.citations.map((c,i)=> (
                        <li key={i}><a className='text-blue-600 hover:underline' href={c.url} target='_blank' rel='noreferrer'>{c.title}</a></li>
                      ))}
                    </ol>
                  </div>
                )}
              </MessageBubble>
            ))}
            {loading && <div className='text-sm text-gray-500'>Thinking…</div>}
          </div>
          <div className='p-3 border-t border-gray-100'>
            <div className='flex items-end gap-2'>
              <textarea value={input} onChange={e => setInput(e.target.value)} onKeyDown={e => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault(); // stop new line
                  onSend();           // send message
                  }
                }} rows={2} placeholder="Ask about treatments, drugs, or guidelines…" className="w-full rounded-2xl border-gray-300 focus:border-medical-blue focus:ring-medical-blue text-sm" />
              <button onClick={onSend} className='px-4 py-2 rounded-2xl bg-medical-blue text-white font-medium'>Send</button>
            </div>
          </div>
        </div>

        <aside className='space-y-6'>
          <div className='rounded-2xl border border-gray-200 bg-white p-4 shadow-card'>
            <div className='text-sm font-semibold mb-3'>Sources</div>
            <SourceList items={lastAnswer?.citations ?? []} />
          </div>
          <div className='rounded-2xl border border-gray-200 bg-white p-4 shadow-card'>
            <ConfidenceBar value={lastAnswer?.confidence ?? 0} />
            <div className='text-xs text-gray-600 mt-2'>This answer is grounded in retrieved sources.</div>
          </div>
          <div className='rounded-2xl border border-gray-200 bg-white p-3 shadow-card no-print'>
            <div className='flex gap-2'>
              <button onClick={exportToPDF} className='flex-1 px-4 py-2 rounded-xl border border-gray-300 bg-white text-sm'>Export PDF</button>
              <button onClick={clearChat} className='flex-1 px-4 py-2 rounded-xl bg-gray-900 text-white text-sm'>Clear</button>
            </div>
          </div>
        </aside>
      </div>
    </section>
  )
}
