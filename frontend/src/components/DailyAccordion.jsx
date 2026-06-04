import { useState } from 'react'
import { ChevronDownIcon } from '@heroicons/react/24/outline'

export default function DailyAccordion({ days }) {
  const [open, setOpen] = useState(0)

  if (!days || days.length === 0) {
    return (
      <div className="text-center py-8 text-gray-400">
        <p className="text-sm">Your daily schedule will appear here once planned.</p>
      </div>
    )
  }

  return (
    <div className="space-y-2">
      {days.map((day, i) => {
        const isOpen = open === i
        return (
          <div key={i} className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden transition-all">
            <button
              onClick={() => setOpen(isOpen ? -1 : i)}
              className="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
            >
              <div className="flex items-center gap-3">
                <div className="w-7 h-7 rounded-full bg-gray-950 dark:bg-white text-white dark:text-gray-950 flex items-center justify-center text-xs font-bold">
                  {i + 1}
                </div>
                <div>
                  <p className="text-sm font-semibold text-gray-900 dark:text-white">
                    {day.title || `Day ${i + 1}`}
                  </p>
                  <p className="text-xs text-gray-400">{day.date || ''}</p>
                </div>
              </div>
              <ChevronDownIcon className={`w-4 h-4 text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
            </button>

            {isOpen && (
              <div className="px-4 pb-4 space-y-3 animate-slide-up">
                {day.match && (
                  <div className="flex items-center gap-2 px-3 py-2 bg-gray-100 dark:bg-gray-700/50 rounded-lg text-sm">
                    <span className="font-medium text-gray-900 dark:text-gray-100">{day.match}</span>
                  </div>
                )}

                {day.activities?.map((act, j) => (
                  <div key={j} className="flex items-start gap-3 text-sm">
                    <span className="text-base mt-0.5">{act.icon || '•'}</span>
                    <div>
                      <p className="text-gray-900 dark:text-white font-medium">{act.title}</p>
                      {act.desc && <p className="text-gray-500 dark:text-gray-400 text-xs">{act.desc}</p>}
                    </div>
                    {act.time && (
                      <span className="ml-auto text-xs text-gray-400 flex-shrink-0">{act.time}</span>
                    )}
                  </div>
                ))}

                {day.hotel && (
                  <div className="flex items-center gap-2 px-3 py-2 bg-gray-100 dark:bg-gray-700/50 rounded-lg text-sm">
                    <span className="text-gray-700 dark:text-gray-300">{day.hotel}</span>
                  </div>
                )}
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}
