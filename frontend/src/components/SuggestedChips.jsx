const CHIPS = [
  'Add more matches to my trip',
  'Reduce budget to $3000',
  'Show hotel options in NYC',
  'Send me a daily schedule',
  'Plan a different trip',
]

export default function SuggestedChips({ onSelect }) {
  return (
    <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-thin -mx-1 px-1">
      {CHIPS.map(chip => (
        <button
          key={chip}
          onClick={() => onSelect(chip)}
          className="flex-shrink-0 px-3.5 py-2 text-xs font-medium rounded-full border border-gray-200 dark:border-gray-700
                     bg-white dark:bg-gray-800 text-gray-600 dark:text-gray-300
                     hover:bg-gray-100 dark:hover:bg-gray-700 hover:border-gray-300 dark:hover:border-gray-600 hover:text-gray-900 dark:hover:text-white
                     transition-all whitespace-nowrap"
        >
          {chip}
        </button>
      ))}
    </div>
  )
}
