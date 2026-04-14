import React from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import './styles/index.css'
import App from './App'
import Landing from './pages/Landing'
import Chat from './pages/Chat'
import Upload from './pages/Upload'
import DocsPage from './pages/DocsPage'
import { AuthProvider } from './context/AuthContext'
import SignIn from './pages/SignIn'
import SignUp from './pages/SignUp'
import ForgotPassword from './pages/ForgotPassword'
import ProtectedRoute from './components/Auth/ProtectedRoute'

createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path='/' element={<App />}>
            <Route index element={<Landing />} />
            <Route path='chat' element={<Chat />} />
            <Route path='docs' element={<DocsPage />} />
            <Route
              path='upload'
              element={
                <ProtectedRoute>
                  <Upload />
                </ProtectedRoute>
              }
            />
            <Route path='signin' element={<SignIn />} />
            <Route path='signup' element={<SignUp />} />
            <Route path='forgot-password' element={<ForgotPassword />} />

            <Route path='*' element={<Navigate to='/' />} />
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>
)
