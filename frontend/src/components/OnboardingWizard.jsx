import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { AnimatePresence, motion } from 'framer-motion'
import { ArrowLeftIcon, ArrowRightIcon } from '@heroicons/react/24/outline'
import StepIndicator from './StepIndicator'
import TeamSelector from './TeamSelector'
import BudgetSlider from './BudgetSlider'
import PreferenceForm from './PreferenceForm'
import { sendMessage } from '../api'

const STEPS = ['Team', 'Trip Details', 'Preferences']

const COUNTRIES = [
  'USA', 'Canada', 'Mexico', 'Brazil', 'Argentina', 'UK', 'Germany', 'France',
  'Spain', 'Italy', 'Japan', 'Korea Republic', 'Australia', 'Nigeria', 'South Africa', 'Other',
]

const stepVariants = {
  enter: { opacity: 0, x: 40 },
  center: { opacity: 1, x: 0, transition: { duration: 0.35, ease: [0.25, 0.1, 0.25, 1] } },
  exit: { opacity: 0, x: -40, transition: { duration: 0.2 } },
}

export default function OnboardingWizard() {
  const navigate = useNavigate()
  const [step, setStep] = useState(0)
  const [teams, setTeams] = useState([])
  const [budget, setBudget] = useState(5000)
  const [departure, setDeparture] = useState('')
  const [dateStart, setDateStart] = useState('')
  const [dateEnd, setDateEnd] = useState('')
  const [travelers, setTravelers] = useState(1)
  const [preferences, setPreferences] = useState({ hotelStars: 3, transport: 'Mixed', interests: [] })
  const [loading, setLoading] = useState(false)

  const canNext = () => {
    if (step === 0) return teams.length > 0
    if (step === 1) return true
    return true
  }

  const buildMessage = () => {
    return `Build a COMPLETE World Cup 2026 trip plan. I support ${teams.join(', ')}. ` +
      `Budget: $${budget}. Departure: ${departure || 'my home country'}. ` +
      `Dates: ${dateStart || 'flexible'} to ${dateEnd || 'flexible'}. ` +
      `Travelers: ${travelers}. Hotel: ${preferences.hotelStars}-star. Transport: ${preferences.transport}. ` +
      `Interests: ${(preferences.interests || []).join(', ') || 'anything fun'}. ` +
      `IMPORTANT: Call search_matches() to find my team's matches, then call save_plan() with matches, budget, hotel, transport, and daily schedule. Do it now.`
  }

  const handleGenerate = async () => {
    setLoading(true)
    try {
      const data = await sendMessage(buildMessage())
      const sid = data.session_id
      localStorage.setItem(`plan_${sid}`, JSON.stringify({
        teams, budget, departure, dateStart, dateEnd, travelers, preferences,
      }))
      navigate(`/dashboard/${sid}`)
    } catch {
      alert('Something went wrong. Please make sure the backend and agent are running.')
    }
    setLoading(false)
  }

  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      <StepIndicator current={step} total={3} labels={STEPS} />

      <div className="mt-10 bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-6 sm:p-8">
        <AnimatePresence mode="wait">
          <motion.div
            key={step}
            variants={stepVariants}
            initial="enter"
            animate="center"
            exit="exit"
          >
            {step === 0 && (
              <div>
                <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-1">Who are you supporting?</h2>
                <p className="text-sm text-gray-500 dark:text-gray-400 mb-6">Pick your favorite team(s) from the 48 qualified nations</p>
                <TeamSelector selected={teams} onChange={setTeams} />
              </div>
            )}

            {step === 1 && (
              <div className="space-y-6">
                <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-1">Your Trip Details</h2>
                <p className="text-sm text-gray-500 dark:text-gray-400 mb-6">Tell us about your travel plans</p>

                <BudgetSlider value={budget} onChange={setBudget} />

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Departure Country</label>
                  <select
                    value={departure}
                    onChange={e => setDeparture(e.target.value)}
                    className="w-full px-4 py-2.5 rounded-xl border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm focus:ring-2 focus:ring-amber-400/50 focus:border-transparent outline-none"
                  >
                    <option value="">Select country</option>
                    {COUNTRIES.map(c => <option key={c} value={c}>{c}</option>)}
                  </select>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Start Date</label>
                    <input
                      type="date"
                      min="2026-06-11"
                      max="2026-07-19"
                      value={dateStart}
                      onChange={e => setDateStart(e.target.value)}
                      className="w-full px-4 py-2.5 rounded-xl border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm focus:ring-2 focus:ring-amber-400/50 focus:border-transparent outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">End Date</label>
                    <input
                      type="date"
                      min={dateStart || '2026-06-11'}
                      max="2026-07-19"
                      value={dateEnd}
                      onChange={e => setDateEnd(e.target.value)}
                      className="w-full px-4 py-2.5 rounded-xl border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm focus:ring-2 focus:ring-amber-400/50 focus:border-transparent outline-none"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Number of Travelers</label>
                  <div className="flex gap-2 flex-wrap">
                    {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map(n => (
                      <button
                        key={n}
                        onClick={() => setTravelers(n)}
                        className={`w-10 h-10 rounded-xl text-sm font-medium transition-all ${
                          travelers === n
                            ? 'bg-gray-950 dark:bg-white text-white dark:text-gray-950'
                            : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-600'
                        }`}
                      >
                        {n}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {step === 2 && (
              <div>
                <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-1">Preferences</h2>
                <p className="text-sm text-gray-500 dark:text-gray-400 mb-6">Fine-tune your experience</p>
                <PreferenceForm preferences={preferences} onChange={setPreferences} />
              </div>
            )}
          </motion.div>
        </AnimatePresence>

        <div className="flex items-center justify-between mt-8 pt-6 border-t border-gray-200 dark:border-gray-700">
          <button
            onClick={() => setStep(s => s - 1)}
            disabled={step === 0}
            className="btn-ghost"
          >
            <ArrowLeftIcon className="w-4 h-4" /> Back
          </button>

          {step < 2 ? (
            <button
              onClick={() => setStep(s => s + 1)}
              disabled={!canNext()}
              className="flex items-center gap-1.5 px-5 py-2.5 bg-gray-950 dark:bg-white text-white dark:text-gray-950 rounded-xl text-sm font-semibold hover:bg-gray-800 dark:hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition-all active:scale-95"
            >
              Next <ArrowRightIcon className="w-4 h-4" />
            </button>
          ) : (
            <button
              onClick={handleGenerate}
              disabled={loading}
              className="flex items-center gap-2 px-6 py-2.5 bg-gray-950 dark:bg-white text-white dark:text-gray-950 rounded-xl text-sm font-semibold hover:bg-gray-800 dark:hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition-all active:scale-95"
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  Generate My Plan
                </>
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
