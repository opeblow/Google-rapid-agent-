import { Routes, Route, useLocation } from 'react-router-dom'
import { useState, useEffect } from 'react'
import Navbar from './components/Navbar'
import Footer from './components/Footer'
import Landing from './pages/Landing'
import Onboarding from './pages/Onboarding'
import Dashboard from './pages/Dashboard'
import SavedPlans from './pages/SavedPlans'
import ErrorBoundary from './components/ErrorBoundary'

export default function App() {
  const [dark, setDark] = useState(() => {
    const saved = localStorage.getItem('theme')
    if (saved) return saved === 'dark'
    return window.matchMedia('(prefers-color-scheme: dark)').matches
  })
  const location = useLocation()
  const isLanding = location.pathname === '/'

  useEffect(() => {
    document.documentElement.classList.toggle('dark', dark)
    localStorage.setItem('theme', dark ? 'dark' : 'light')
  }, [dark])

  return (
    <ErrorBoundary>
      <div className="min-h-screen flex flex-col">
        {!isLanding && <Navbar dark={dark} toggleDark={() => setDark(d => !d)} />}
        <main className="flex-1">
          <Routes>
            <Route path="/" element={<Landing dark={dark} toggleDark={() => setDark(d => !d)} />} />
            <Route path="/onboard" element={<Onboarding />} />
            <Route path="/dashboard/:sessionId" element={<Dashboard />} />
            <Route path="/plans" element={<SavedPlans />} />
          </Routes>
        </main>
        {!isLanding && <Footer />}
      </div>
    </ErrorBoundary>
  )
}
