import { useState, useMemo } from 'react'
import { MagnifyingGlassIcon, XMarkIcon } from '@heroicons/react/24/outline'

const ALL_TEAMS = [
  'Argentina', 'Australia', 'Belgium', 'Brazil', 'Cameroon', 'Canada', 'Colombia',
  'Croatia', 'Denmark', 'Ecuador', 'Egypt', 'England', 'France', 'Germany', 'Ghana',
  'Iran', 'Italy', 'Japan', 'Mexico', 'Morocco', 'Netherlands', 'New Zealand',
  'Nigeria', 'Portugal', 'Saudi Arabia', 'Senegal', 'South Korea', 'Spain',
  'Switzerland', 'Tunisia', 'Uruguay', 'USA',
]

const COUNTRY_FLAGS = {
  Argentina: '🇦🇷', Australia: '🇦🇺', Belgium: '🇧🇪', Brazil: '🇧🇷',
  Cameroon: '🇨🇲', Canada: '🇨🇦', Colombia: '🇨🇴', Croatia: '🇭🇷',
  Denmark: '🇩🇰', Ecuador: '🇪🇨', Egypt: '🇪🇬', England: '🏴󠁧󠁢󠁥󠁮󠁧󠁿',
  France: '🇫🇷', Germany: '🇩🇪', Ghana: '🇬🇭', Iran: '🇮🇷',
  Italy: '🇮🇹', Japan: '🇯🇵', Mexico: '🇲🇽', Morocco: '🇲🇦',
  Netherlands: '🇳🇱', NewZealand: '🇳🇿', Nigeria: '🇳🇬', Portugal: '🇵🇹',
  SaudiArabia: '🇸🇦', Senegal: '🇸🇳', SouthKorea: '🇰🇷', Spain: '🇪🇸',
  Switzerland: '🇨🇭', Tunisia: '🇹🇳', Uruguay: '🇺🇾', USA: '🇺🇸',
}

const flag = (name) => COUNTRY_FLAGS[name.replace(/\s/g, '')] || '🏳️'

export default function TeamSelector({ selected, onChange }) {
  const [query, setQuery] = useState('')

  const filtered = useMemo(() => {
    if (!query) return ALL_TEAMS
    return ALL_TEAMS.filter(t => t.toLowerCase().includes(query.toLowerCase()))
  }, [query])

  const toggle = (team) => {
    if (selected.includes(team)) {
      onChange(selected.filter(t => t !== team))
    } else {
      onChange([...selected, team])
    }
  }

  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
        Pick your team(s) — who are you cheering for?
      </label>

      {selected.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-3">
          {selected.map(team => (
            <span
              key={team}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-gray-950/10 dark:bg-white/10 text-gray-950 dark:text-white rounded-full text-sm font-medium"
            >
              {flag(team)} {team}
              <button onClick={() => toggle(team)} className="ml-1 hover:text-blue-600">
                <XMarkIcon className="w-3.5 h-3.5" />
              </button>
            </span>
          ))}
        </div>
      )}

      <div className="relative mb-2">
        <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
        <input
          type="text"
          placeholder="Search teams..."
          value={query}
          onChange={e => setQuery(e.target.value)}
          className="w-full pl-9 pr-4 py-2.5 rounded-xl border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm focus:ring-2 focus:ring-gray-400 dark:focus:ring-gray-500 focus:border-transparent outline-none transition-all"
        />
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 max-h-60 overflow-y-auto">
        {filtered.map(team => {
          const isSelected = selected.includes(team)
          return (
            <button
              key={team}
              onClick={() => toggle(team)}
              className={`flex items-center gap-2 px-3 py-2 rounded-xl text-sm font-medium transition-all ${
                isSelected
                  ? 'bg-gray-950 dark:bg-white text-white dark:text-gray-950'
                  : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
              }`}
            >
              {flag(team)} {team}
            </button>
          )
        })}
      </div>
    </div>
  )
}
