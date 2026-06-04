const STARS = [2, 3, 4, 5]
const TRANSPORT = ['Flights', 'Bus', 'Car', 'Mixed']
const INTERESTS = ['Food tours', 'Landmarks', 'Shopping', 'Nightlife', 'Family activities']

export default function PreferenceForm({ preferences, onChange }) {
  const toggle = (key, val) => {
    const arr = preferences[key] || []
    const next = arr.includes(val) ? arr.filter(v => v !== val) : [...arr, val]
    onChange({ ...preferences, [key]: next })
  }

  return (
    <div className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Hotel Rating</label>
        <div className="flex gap-2">
          {STARS.map(s => (
            <button
              key={s}
              onClick={() => onChange({ ...preferences, hotelStars: s })}
              className={`flex-1 py-3 rounded-xl text-sm font-semibold transition-all ${
                preferences.hotelStars === s
                  ? 'bg-gray-950 dark:bg-white text-white dark:text-gray-950'
                  : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700'
              }`}
            >
              {'★'.repeat(s)}{'☆'.repeat(5 - s)}
            </button>
          ))}
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Transport</label>
        <div className="grid grid-cols-2 gap-2">
          {TRANSPORT.map(t => (
            <button
              key={t}
              onClick={() => onChange({ ...preferences, transport: t })}
              className={`py-3 rounded-xl text-sm font-medium transition-all ${
                preferences.transport === t
                  ? 'bg-gray-950 dark:bg-white text-white dark:text-gray-950'
                  : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700'
              }`}
            >
              {t}
            </button>
          ))}
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Interests</label>
        <div className="flex flex-wrap gap-2">
          {INTERESTS.map(interest => {
            const active = (preferences.interests || []).includes(interest)
            return (
              <button
                key={interest}
                onClick={() => toggle('interests', interest)}
                className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${
                  active
                    ? 'bg-gray-950 dark:bg-white text-white dark:text-gray-950'
                    : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700'
                }`}
              >
                {interest}
              </button>
            )
          })}
        </div>
      </div>
    </div>
  )
}
