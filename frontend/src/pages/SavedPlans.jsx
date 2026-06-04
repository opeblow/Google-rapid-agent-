import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { PlusIcon } from '@heroicons/react/24/outline'
import SavedPlansGrid from '../components/SavedPlansGrid'
import LoadingSpinner from '../components/LoadingSpinner'

function getAllPlans() {
  const plans = []
  for (let i = 0; i < localStorage.length; i++) {
    const key = localStorage.key(i)
    if (key && key.startsWith('plan_')) {
      try {
        const sessionId = key.replace('plan_', '')
        const data = JSON.parse(localStorage.getItem(key))
        plans.push({ sessionId, data })
      } catch {}
    }
  }
  return plans
}

export default function SavedPlans() {
  const [plans, setPlans] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setPlans(getAllPlans())
    setLoading(false)
  }, [])

  if (loading) return <LoadingSpinner text="Loading plans..." />

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">My Plans</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            {plans.length > 0 ? `${plans.length} plan${plans.length > 1 ? 's' : ''} saved` : 'Start planning your adventure'}
          </p>
        </div>
        <Link
          to="/onboard"
          className="flex items-center gap-2 px-4 py-2 bg-gray-950 dark:bg-white text-white dark:text-gray-950 rounded-lg text-sm font-medium hover:bg-gray-800 dark:hover:bg-gray-200 transition-all active:scale-95"
        >
          <PlusIcon className="w-4 h-4" /> New Plan
        </Link>
      </div>

      <SavedPlansGrid plans={plans} />
    </div>
  )
}
