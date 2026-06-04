const COUNTRY_COLORS = {
  USA: { dot: 'bg-blue-500', line: 'border-blue-300', badge: 'bg-blue-100 text-blue-700 dark:bg-blue-900/50 dark:text-blue-300' },
  Canada: { dot: 'bg-red-500', line: 'border-red-300', badge: 'bg-red-100 text-red-700 dark:bg-red-900/50 dark:text-red-300' },
  Mexico: { dot: 'bg-green-500', line: 'border-green-300', badge: 'bg-green-100 text-green-700 dark:bg-green-900/50 dark:text-green-300' },
}

export default function MatchTimeline({ matches }) {
  if (!matches || matches.length === 0) {
    return (
      <div className="text-center py-8 text-gray-400">
        <p className="text-sm">No matches added yet. Ask the agent to find matches for your trip!</p>
      </div>
    )
  }

  return (
    <div className="relative pl-6 space-y-6">
      {matches.map((match, i) => {
        const cc = COUNTRY_COLORS[match.country] || COUNTRY_COLORS.USA
        return (
          <div key={i} className="relative animate-fade-in" style={{ animationDelay: `${i * 0.05}s` }}>
            <div className={`absolute -left-6 top-1 w-4 h-4 rounded-full border-4 border-white dark:border-gray-900 shadow ${cc.dot}`} />
            {i < matches.length - 1 && (
              <div className={`absolute -left-[4.5px] top-5 bottom-[-1.5rem] w-0.5 bg-gray-200 dark:bg-gray-700 ${cc.line.split(' ')[1]}`} />
            )}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-200 dark:border-gray-700 card-hover">
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-bold text-sm text-gray-900 dark:text-white">
                      {match.home_team} vs {match.away_team}
                    </span>
                  </div>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {match.venue} · {match.city}, {match.country}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">{match.date} · {match.time}</p>
                </div>
                <span className={`flex-shrink-0 px-2 py-0.5 rounded text-xs font-medium ${cc.badge}`}>
                  {match.country}
                </span>
              </div>
              {match.stage && (
                <div className="mt-2 text-xs text-gray-400 dark:text-gray-500 font-medium">{match.stage}</div>
              )}
            </div>
          </div>
        )
      })}
    </div>
  )
}
