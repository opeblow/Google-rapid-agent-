export default function StepIndicator({ current, total, labels }) {
  return (
    <div className="w-full">
      <div className="flex items-center justify-between mb-3">
        {Array.from({ length: total }, (_, i) => (
          <div key={i} className="flex items-center flex-1">
            <div
              className={`w-8 h-8 rounded-lg flex items-center justify-center text-sm font-semibold transition-all ${
                i <= current
                  ? 'bg-gray-950 dark:bg-white text-white dark:text-gray-950'
                  : 'bg-gray-100 dark:bg-gray-800 text-gray-400 dark:text-gray-500'
              }`}
            >
              {i < current ? '✓' : i + 1}
            </div>
            {i < total - 1 && (
              <div
                className={`flex-1 h-0.5 mx-2 rounded ${
                  i < current
                    ? 'bg-gray-950 dark:bg-white'
                    : 'bg-gray-200 dark:bg-gray-700'
                }`}
              />
            )}
          </div>
        ))}
      </div>
      {labels && (
        <div className="flex justify-between px-1">
          {labels.map((label, i) => (
            <span
              key={i}
              className={`text-xs font-medium ${
                i === current
                  ? 'text-gray-900 dark:text-white'
                  : 'text-gray-400 dark:text-gray-500'
              }`}
            >
              {label}
            </span>
          ))}
        </div>
      )}
    </div>
  )
}
