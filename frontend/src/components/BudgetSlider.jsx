const LABELS = ['Backpacker', 'Budget', 'Comfort', 'Premium', 'Luxury']

export default function BudgetSlider({ value, onChange }) {
  const idx = Math.min(Math.floor(value / 4000), 4)

  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Budget</label>
        <div className="flex items-center gap-2">
          <span className="text-lg font-bold text-gray-950 dark:text-white">
            ${value.toLocaleString()}
          </span>
        </div>
      </div>
      <p className="text-xs text-gray-400 dark:text-gray-500 mb-3">{LABELS[idx]}</p>

      <input
        type="range"
        min="1000"
        max="20000"
        step="500"
        value={value}
        onChange={e => onChange(Number(e.target.value))}
        className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full appearance-none cursor-pointer
                   accent-gray-950 dark:accent-white
                   [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-5 [&::-webkit-slider-thumb]:h-5
                   [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-gray-950 dark:[&::-webkit-slider-thumb]:bg-white
                   [&::-webkit-slider-thumb]:cursor-pointer"
      />

      <div className="flex justify-between text-xs text-gray-400 dark:text-gray-500 mt-1">
        <span>$1,000</span>
        <span>$20,000</span>
      </div>
    </div>
  )
}
