import React from 'react'
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom'
import Logo from './assets/logo.svg'
import { useAuth } from './context/AuthContext'

export default function App() {
  const { pathname } = useLocation()
  const { user, signOut } = useAuth()
  const nav = useNavigate()

  async function handleSignOut() {
    await signOut()
    nav('/')
  }

  return (
    <div className='min-h-screen flex flex-col bg-gray-50 text-gray-900'>
      <nav className='sticky top-0 z-40 bg-white/80 backdrop-blur border-b border-gray-200'>
        <div className='mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 h-14 flex items-center justify-between'>
          <Link to='/' className='flex items-center gap-2'>
            <img src={Logo} alt='MedAI-RAG' className='h-8 w-8'/>
            <span className='font-semibold'>MedAI-RAG</span>
          </Link>
          <div className='flex items-center gap-4 text-sm'>
            <Link to='/chat' className={navCls(pathname==='/chat')}>Chat</Link>
            <Link to='/upload' className={navCls(pathname==='/upload')}>Upload</Link>
            <Link to='/docs' className={navCls(pathname==='/docs')}>Docs</Link>

            {!user ? (
              <>
                <Link to='/signin' className='px-3 py-1.5 rounded-full text-gray-700 hover:bg-gray-100'>Sign in</Link>
                <Link to='/signup' className='px-3 py-1.5 rounded-full bg-gray-900 text-white'>Sign up</Link>
              </>
            ) : (
              <div className='flex items-center gap-2'>
                <span className='hidden sm:inline text-gray-600'>Hi, {user.name || user.email}</span>
                <button onClick={handleSignOut} className='px-3 py-1.5 rounded-full border border-gray-300 hover:bg-gray-100'>
                  Sign out
                </button>
              </div>
            )}
          </div>
        </div>
      </nav>
      <main className='flex-1'>
        <Outlet />
      </main>
      <footer className='border-t border-gray-200 bg-white text-xs text-gray-500'>
        <div className='mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-3 flex items-center justify-between'>
          <p>Not for patient use. For educational and research purposes only.</p>
          <p>© {new Date().getFullYear()} MedAI-RAG</p>
        </div>
      </footer>
    </div>
  )
}

function navCls(active) {
  return `px-3 py-1.5 rounded-full ${active ? 'bg-gray-900 text-white' : 'text-gray-700 hover:bg-gray-100'}`
}
