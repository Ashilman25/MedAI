import React, { useEffect, useRef, useState } from 'react'
import MessageBubble from '../components/Chat/MessageBubble'
import SourceList from '../components/Sources/SourceList'
import ConfidenceBar from '../components/Sources/ConfidenceBar'
import { ask, expandSources } from '../lib/api'
import { loadChat, saveChat, clearChat as clearStore } from '../store/localStore'
import { exportToPDF } from '../lib/export'
import { motion, AnimatePresence } from 'framer-motion'

export default function Chat() {
  const [messages, setMessages] = useState(()=>loadChat())
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [lastAnswer, setLastAnswer] = useState(null)
  const scrollRef = useRef(null)

  const [lastQuery, setLastQuery] = useState('')
  const [expandPrompt, setExpandPrompt] = useState(false)

  // scanning UX states
  const [scanning, setScanning] = useState(false)
  const [scanStep, setScanStep] = useState(0)        // 0 idle, 1..4 staged
  const [scanStats, setScanStats] = useState(null)   // { found, added, skipped }
  const [showScanSummary, setShowScanSummary] = useState(false) // linger after scan
  const CONF_T = Number(import.meta.env.VITE_CONFIDENCE_THRESHOLD ?? 0.55)

  useEffect(()=>{ saveChat(messages) }, [messages])
  useEffect(()=>{ scrollRef.current?.scrollTo(0, scrollRef.current.scrollHeight) }, [messages, loading, scanning, showScanSummary])

  async function onSend() {
    const q = input.trim()
    if (!q) return
    setInput('')
    setLastQuery(q)
    const id = crypto.randomUUID()
    const userMsg = { id, role: 'user', content: q }
    setMessages(m => [...m, userMsg])
    setLoading(true)
    try {
      const res = await ask(q)
      const aiMsg = { id: crypto.randomUUID(), role: 'assistant', content: res.answer, citations: res.citations, confidence: res.confidence }
      setMessages(m => [...m, aiMsg])
      setLastAnswer(res)
      setExpandPrompt(shouldOfferExpansion(res))
    } catch (e) {
      const aiMsg = { id: crypto.randomUUID(), role: 'assistant', content: `Error: ${e.message}` }
      setMessages(m => [...m, aiMsg])
      setLastAnswer(null)
      setExpandPrompt(false)
    } finally {
      setLoading(false)
    }
  }

  async function onScanNow() {
    setExpandPrompt(false)
    setScanning(true)
    setScanStats(null)
    setShowScanSummary(false)
    setScanStep(1)  // Querying PubMed…

    try {
      // staged progress purely for UX
      const t1 = setTimeout(() => setScanStep(2), 600)   // Fetching abstracts…
      const t2 = setTimeout(() => setScanStep(3), 1200)  // Embedding…

      // Backend scan (wide sweep)
      const resp = await expandSources(lastQuery, {
        wide: true,
        target_confidence: Number(import.meta.env.VITE_CONFIDENCE_THRESHOLD ?? 0.62),
        max_passes: 3,
        per_pass_retmax: 60,
        mindate: 2018,
        fallback_mindate: 2010,
        lang: 'en',
        types: ['Guideline','Practice Guideline','Systematic Review','Review'],
        top_k: Number(import.meta.env.VITE_DEFAULT_TOP_K ?? 5)
      })

      // Record stats and move to re-evaluate stage
      setScanStats({ found: resp.found, added: resp.added, skipped: resp.skipped })
      setScanStep(4)

      // Append refreshed answer
      const aiMsg = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: resp.answer,
        citations: resp.citations,
        confidence: resp.confidence,
        updated: true
      }
      setMessages(m => [...m, aiMsg])
      setLastAnswer(resp)

      // grace pause so the panel doesn’t blink away
      // then show a separate summary card that lingers
      setTimeout(() => {
        setScanning(false)
        setShowScanSummary(true)
        // auto-hide the summary after ~3s (feel free to tune)
        setTimeout(() => setShowScanSummary(false), 3000)
      }, 1200)

      return () => { clearTimeout(t1); clearTimeout(t2) }
    } catch (e) {
      const errMsg = { id: crypto.randomUUID(), role: 'assistant', content: `Source expansion failed: ${e.message}` }
      setMessages(m => [...m, errMsg])
      // still give a moment before hiding the panel
      setTimeout(() => {
        setScanning(false)
        setShowScanSummary(false)
      }, 800)
    }
  }

  function clearChat() {
    if (!confirm('Clear chat history?')) return
    setMessages([])
    setLastAnswer(null)
    clearStore()
  }

  function shouldOfferExpansion(res) {
    const lowConf = (res?.confidence ?? 0) < CONF_T
    const fewCites = (res?.citations?.length ?? 0) < 2
    return lowConf || fewCites
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
                {m.updated && (
                  <div className='mt-2 text-[11px] text-teal-700'>Updated answer (post-scan)</div>
                )}
              </MessageBubble>
            ))}

            {/* CTA — prettier + more deliberate */}
            <AnimatePresence>
              {expandPrompt && !scanning && (
                <motion.div
                  initial={{ opacity: 0, y: 8, scale: 0.98 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: 6, scale: 0.98 }}
                  className="relative overflow-hidden rounded-xl border border-amber-200 bg-gradient-to-r from-amber-50 to-white p-4 text-sm"
                >
                  <div className="absolute inset-y-0 left-0 w-1 bg-amber-400/70" />
                  <div className="flex items-start gap-3">
                    <div className="mt-0.5 h-2 w-2 rounded-full bg-amber-500 animate-pulse" />
                    <div>
                      <div className="font-medium text-amber-900">Confidence is low for this answer.</div>
                      <div className="mt-1 text-amber-800">
                        Would you like me to scan additional trusted sources (e.g., PubMed) for more up-to-date results?
                      </div>
                      <div className="mt-3 flex flex-wrap gap-2">
                        <button
                          onClick={onScanNow}
                          className="px-3 py-1.5 rounded-lg bg-blue-600 text-white text-sm hover:bg-blue-700 shadow-sm"
                        >
                          Scan Now
                        </button>
                        <button
                          onClick={()=>setExpandPrompt(false)}
                          className="px-3 py-1.5 rounded-lg border border-gray-300 text-gray-700 text-sm bg-white hover:bg-gray-50"
                        >
                          Dismiss
                        </button>
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Scanning panel — smoother visuals + grace pause */}
            <AnimatePresence>
              {scanning && (
                <motion.div
                  initial={{ opacity: 0, y: 8, scale: 0.98 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: 6, scale: 0.98 }}
                  className="rounded-xl border border-gray-200 bg-white p-4 text-sm shadow-sm"
                >
                  <div className="flex items-center gap-3">
                    <div className="relative">
                      <div className="h-5 w-5 animate-spin rounded-full border-2 border-teal-500 border-t-transparent" />
                      <div className="absolute inset-0 rounded-full animate-ping border border-teal-300" />
                    </div>
                    <div className="font-medium text-gray-900">Scanning additional sources…</div>
                  </div>

                  <ul className="mt-3 space-y-1 text-gray-700">
                    <li className={scanStep >= 1 ? "opacity-100" : "opacity-60"}>1) Querying PubMed…</li>
                    <li className={scanStep >= 2 ? "opacity-100" : "opacity-60"}>2) Fetching abstracts & guidelines…</li>
                    <li className={scanStep >= 3 ? "opacity-100" : "opacity-60"}>3) Embedding into knowledge base…</li>
                    <li className={scanStep >= 4 ? "opacity-100" : "opacity-60"}>4) Re-evaluating your question…</li>
                  </ul>

                  <div className="mt-3">
                    <div className="h-2 w-full rounded bg-gray-100 overflow-hidden">
                      <div
                        className="h-2 bg-teal-500 transition-all"
                        style={{ width: `${Math.min(100, scanStep * 25)}%` }}
                      />
                    </div>
                    <div className="mt-2 text-xs text-gray-500">
                      {scanStats
                        ? <>Found <span className="font-semibold text-teal-700">{scanStats.found}</span> items • Added <span className="font-semibold text-teal-700">{scanStats.added}</span></>
                        : "Working…"}
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Post-scan summary that lingers briefly */}
            <AnimatePresence>
              {showScanSummary && scanStats && (
                <motion.div
                  initial={{ opacity: 0, y: 8, scale: 0.98 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: 6, scale: 0.98 }}
                  className="rounded-xl border border-teal-200 bg-teal-50 p-3 text-xs text-teal-900"
                >
                  ✅ Scan complete. Found <span className="font-semibold">{scanStats.found}</span> new sources, added <span className="font-semibold">{scanStats.added}</span> to your library. View them on the <a href="/docs" className="text-blue-600 underline">Docs page</a>.
                </motion.div>
              )}
            </AnimatePresence>

            {loading && <div className='text-sm text-gray-500'>Thinking…</div>}
          </div>

          <div className='p-3 border-t border-gray-100'>
            <div className='flex items-end gap-2'>
              <textarea
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={e => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault()
                    onSend()
                  }
                }}
                rows={2}
                placeholder="Ask about treatments, drugs, or guidelines…"
                className="w-full rounded-2xl border-gray-300 focus:border-medical-blue focus:ring-medical-blue text-sm"
              />
              <button
                onClick={onSend}
                disabled={loading}
                className={`px-4 py-2 rounded-2xl text-white font-medium ${loading ? 'bg-gray-400 cursor-not-allowed' : 'bg-medical-blue'}`}
              >
                {loading ? '…' : 'Send'}
              </button>
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
