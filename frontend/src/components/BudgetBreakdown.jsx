const DEFAULT_CATEGORIES = [
  { label: 'Flights', amount: 0 },
  { label: 'Hotels', amount: 0 },
  { label: 'Tickets', amount: 0 },
  { label: 'Food', amount: 0 },
  { label: 'Transport', amount: 0 },
  { label: 'Activities', amount: 0 },
]

export default function BudgetBreakdown({ budgetData, totalBudget = 5000 }) {
  const categories = budgetData?.categories || DEFAULT_CATEGORIES
  const total = categories.reduce((sum, c) => sum + (c.amount || 0), 0) || 1
  const remaining = Math.max(0, totalBudget - categories.reduce((sum, c) => sum + (c.amount || 0), 0))

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <p className="text-sm text-gray-500 dark:text-gray-400">Total Budget</p>
        <p className="text-2xl font-bold text-gray-900 dark:text-white">${totalBudget.toLocaleString()}</p>
      </div>

      <div className="space-y-3">
        {categories.map((cat, i) => {
          const pct = ((cat.amount || 0) / totalBudget) * 100
          return (
            <div key={i}>
              <div className="flex justify-between items-center mb-1">
                <span className="text-sm text-gray-700 dark:text-gray-300">{cat.label}
                </span>
                <span className="text-sm font-medium text-gray-900 dark:text-white">
                  ${(cat.amount || 0).toLocaleString()}
                </span>
              </div>
              <div className="w-full h-2.5 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-700 bg-gray-950 dark:bg-white"
                  style={{ width: `${Math.min(pct, 100)}%` }}
                />
              </div>
            </div>
          )
        })}
      </div>

      <div className="mt-6 p-4 rounded-xl border border-gray-200 dark:border-gray-700 flex justify-between items-center">
        <span className="text-sm text-gray-600 dark:text-gray-400">Remaining Balance</span>
        <span className={`text-lg font-bold ${remaining > 0 ? 'text-gray-950 dark:text-white' : 'text-red-500'}`}>
          ${remaining.toLocaleString()}
        </span>
      </div>
    </div>
  )
}
