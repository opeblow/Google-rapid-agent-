import { Routes, Route, useLocation } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import Navbar from './components/Navbar'
import Footer from './components/Footer'
import Landing from './pages/Landing'
import Onboarding from './pages/Onboarding'
import Dashboard from './pages/Dashboard'
import SavedPlans from './pages/SavedPlans'
import ErrorBoundary from './components/ErrorBoundary'

const pageVariants = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0, transition: { duration: 0.4, ease: [0.25, 0.1, 0.25, 1] } },
  exit: { opacity: 0, y: -10, transition: { duration: 0.2 } },
}

function AnimatedPage({ children }) {
  return (
    <motion.div variants={pageVariants} initial="initial" animate="animate" exit="exit">
      {children}
    </motion.div>
  )
}

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
          <AnimatePresence mode="wait">
            <Routes location={location} key={location.pathname}>
              <Route path="/" element={<AnimatedPage><Landing dark={dark} toggleDark={() => setDark(d => !d)} /></AnimatedPage>} />
              <Route path="/onboard" element={<AnimatedPage><Onboarding /></AnimatedPage>} />
              <Route path="/dashboard/:sessionId" element={<AnimatedPage><Dashboard /></AnimatedPage>} />
              <Route path="/plans" element={<AnimatedPage><SavedPlans /></AnimatedPage>} />
            </Routes>
          </AnimatePresence>
        </main>
        {!isLanding && <Footer />}
      </div>
    </ErrorBoundary>
  )
}
