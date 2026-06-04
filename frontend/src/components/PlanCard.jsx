import { Link } from 'react-router-dom'

export default function PlanCard({ plan, sessionId }) {
  const data = plan?.plan_data || plan || {}
  const matches = data.matches || []
  const budget = data.budget || data.total_budget
  const dates = data.dates || {}

  return (
    <Link
      to={`/dashboard/${sessionId}`}
      className="block bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 overflow-hidden hover:border-gray-300 dark:hover:border-gray-700 transition-all duration-200"
    >
      <div className="h-28 bg-gray-950 relative flex items-end p-4">
        <div className="relative">
          <h3 className="font-semibold text-white text-base leading-tight">
            {matches.length > 0
              ? `${matches[0].home_team || 'Team'} vs ${matches[0].away_team || 'Team'}`
              : 'World Cup Adventure'}
          </h3>
          {matches.length > 0 && (
            <p className="text-gray-400 text-xs mt-0.5">{matches.length} match{matches.length > 1 ? 'es' : ''}</p>
          )}
        </div>
      </div>

      <div className="p-4 space-y-2">
        <div className="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
          <span>{dates.start || 'TBD'} — {dates.end || 'TBD'}</span>
        </div>
        {budget && (
          <div className="flex items-center gap-2 text-xs">
            <span className="text-gray-400">Budget:</span>
            <span className="font-semibold text-gray-900 dark:text-white">${budget.toLocaleString()}</span>
          </div>
        )}
        <div className="text-xs text-gray-400 pt-1">View Plan →</div>
      </div>
    </Link>
  )
}
