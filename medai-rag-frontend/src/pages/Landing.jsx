import React from 'react'
import { useNavigate } from 'react-router-dom'
import Logo from '../assets/logo.svg'




export default function Landing() {
  const nav = useNavigate()
  return (
    <section className='mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-16 grid md:grid-cols-2 gap-12 items-center'>
      <div className='space-y-6'>
        <div className='inline-flex items-center gap-3'>
          <img src={Logo} alt='logo' className='h-10 w-10'/>
          <h1 className='text-3xl font-bold'>MedAI‑RAG</h1>
        </div>
        <p className='text-gray-700 text-lg'>Your AI‑powered medical reference assistant with grounded, cited answers.</p>
        <div className='flex gap-3'>
          <button onClick={()=>nav('/chat')} className='px-5 py-3 rounded-2xl bg-medical-blue text-white font-medium'>Continue as Guest</button>
          <button onClick={()=>nav('/signin')} className='px-5 py-3 rounded-2xl border border-gray-300 bg-white font-medium'>Sign in</button>

        </div>
        <ul className='text-sm text-gray-600 list-disc pl-5'>
          <li>Cited sources in every response</li>
          <li>Confidence scores & uncertainty warnings</li>
          <li>No PHI uploads in MVP</li>
        </ul>
      </div>
      <div className='rounded-2xl border border-gray-200 bg-white p-6 shadow-card'>
        <div className='aspect-[16/10] rounded-xl bg-gradient-to-br from-medical-blue/10 to-medical-green/10 flex items-center justify-center'>
          <div className='text-center'>
            <div className='text-gray-600'>Preview</div>
            <div className='font-semibold text-gray-900'>Chat + Sources Dashboard</div>
          </div>
        </div>
        <div className='text-xs text-gray-500 mt-3'>Disclaimer: Not for patient use. For educational and research purposes only.</div>
      </div>
    </section>
  )
}
