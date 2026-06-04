export default function PlanSummary({ planData }) {
  if (!planData) return null
  const { plan_data } = planData
  const data = plan_data || planData

  const matches = data.matches || []
  const budget = data.budget || data.total_budget || '—'
  const travelers = data.travelers || data.traveler_count || '—'
  const dates = data.dates || data.travel_dates || {}

  return (
    <div className="bg-gray-950 rounded-2xl p-5 text-white border border-gray-800">
      <div className="mb-4">
        <h3 className="font-bold text-lg">Your World Cup Trip</h3>
        <p className="text-gray-400 text-xs">
          {matches.length > 0 ? `${matches.length} matches planned` : 'No matches yet'}
        </p>
      </div>

      <div className="grid grid-cols-2 gap-3 text-sm">
        {budget !== '—' && (
          <div className="bg-white/5 rounded-xl p-2.5 border border-gray-800">
            <p className="text-gray-400 text-xs">Budget</p>
            <p className="font-bold text-lg">${typeof budget === 'number' ? budget.toLocaleString() : budget}</p>
          </div>
        )}
        {travelers !== '—' && (
          <div className="bg-white/5 rounded-xl p-2.5 border border-gray-800">
            <p className="text-gray-400 text-xs">Travelers</p>
            <p className="font-bold text-lg">{travelers}</p>
          </div>
        )}
      </div>

      {matches.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-1.5">
          {matches.slice(0, 4).map((m, i) => (
            <span key={i} className="px-2 py-0.5 bg-white/10 rounded-full text-xs text-gray-300">
              {m.home_team || ''} vs {m.away_team || ''}
            </span>
          ))}
          {matches.length > 4 && (
            <span className="px-2 py-0.5 bg-white/10 rounded-full text-xs text-gray-300">+{matches.length - 4} more</span>
          )}
        </div>
      )}
    </div>
  )
}
