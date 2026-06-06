import { useState, useEffect, useCallback } from 'react'
import { useParams } from 'react-router-dom'
import { ChatBubbleLeftRightIcon, MapIcon } from '@heroicons/react/24/outline'
import ChatInterface from '../components/ChatInterface'
import PlanSummary from '../components/PlanSummary'
import MatchTimeline from '../components/MatchTimeline'
import DailyAccordion from '../components/DailyAccordion'
import BudgetBreakdown from '../components/BudgetBreakdown'
import HotelCards from '../components/HotelCards'
import LoadingSpinner from '../components/LoadingSpinner'

const TABS = [
  { key: 'matches', label: 'Matches' },
  { key: 'daily', label: 'Daily Plan' },
  { key: 'budget', label: 'Budget' },
  { key: 'hotels', label: 'Hotels' },
]

export default function Dashboard() {
  const { sessionId } = useParams()
  const [activeTab, setActiveTab] = useState('matches')
  const [planData, setPlanData] = useState(null)
  const [planMeta, setPlanMeta] = useState(null)
  const [loading, setLoading] = useState(true)
  const [mobileView, setMobileView] = useState('chat')

  useEffect(() => {
    const saved = localStorage.getItem(`plan_${sessionId}`)
    if (saved) {
      try { setPlanMeta(JSON.parse(saved)) } catch {}
    }
    const savedPlanData = localStorage.getItem(`plan_data_${sessionId}`)
    if (savedPlanData) {
      try { setPlanData(JSON.parse(savedPlanData)) } catch {}
    }
    setLoading(false)
  }, [sessionId])

  const onPlanUpdate = useCallback((data) => {
    setPlanData(data)
  }, [])

  const plan = planData?.plan_data || planData || {}
  const matches = plan.matches || []
  const days = plan.daily_plan || plan.days || []
  const hotels = plan.hotels || []
  const budget = plan.budget || plan.total_budget || planMeta?.budget || 5000

  if (loading) return <LoadingSpinner text="Loading your trip..." />

  return (
    <div className="h-[calc(100vh-4rem)] flex flex-col">
      <div className="md:hidden flex border-b border-gray-200 dark:border-gray-800">
        <button
          onClick={() => setMobileView('chat')}
          className={`flex-1 py-3 text-sm font-medium text-center transition-colors ${
            mobileView === 'chat' ? 'text-gray-950 dark:text-white border-b-2 border-gray-950 dark:border-white' : 'text-gray-400'
          }`}
        >
          <ChatBubbleLeftRightIcon className="w-4 h-4 inline mr-1" /> Chat
        </button>
        <button
          onClick={() => setMobileView('plan')}
          className={`flex-1 py-3 text-sm font-medium text-center transition-colors ${
            mobileView === 'plan' ? 'text-gray-950 dark:text-white border-b-2 border-gray-950 dark:border-white' : 'text-gray-400'
          }`}
        >
          <MapIcon className="w-4 h-4 inline mr-1" /> Itinerary
        </button>
      </div>

      <div className="flex-1 flex flex-col md:flex-row overflow-hidden">
        <div className={`w-full md:w-2/5 border-r border-gray-200 dark:border-gray-800 flex flex-col ${mobileView === 'plan' ? 'hidden md:flex' : 'flex'}`}>
          <ChatInterface sessionId={sessionId} onPlanUpdate={onPlanUpdate} />
        </div>

        <div className={`w-full md:w-3/5 flex flex-col overflow-hidden bg-gray-50 dark:bg-gray-950 ${mobileView === 'chat' ? 'hidden md:flex' : 'flex'}`}>
          <div className="p-4 pb-0">
            <PlanSummary planData={planData || planMeta} />
          </div>

          <div className="flex-shrink-0 flex gap-1 px-4 pt-4 overflow-x-auto">
            {TABS.map(tab => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key)}
                className={`flex items-center gap-1.5 px-4 py-2 rounded-t-lg text-sm font-medium transition-all whitespace-nowrap ${
                  activeTab === tab.key
                    ? 'bg-white dark:bg-gray-800 text-gray-950 dark:text-white border border-b-0 border-gray-200 dark:border-gray-700'
                    : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          <div className="flex-1 overflow-y-auto p-4 scrollbar-thin">
            <div className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-4 animate-fade-in">
              {activeTab === 'matches' && <MatchTimeline matches={matches} />}
              {activeTab === 'daily' && <DailyAccordion days={days} />}
              {activeTab === 'budget' && <BudgetBreakdown budgetData={plan} totalBudget={budget} />}
              {activeTab === 'hotels' && <HotelCards hotels={hotels} />}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
