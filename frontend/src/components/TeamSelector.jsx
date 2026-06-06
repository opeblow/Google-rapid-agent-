import { useState, useMemo } from 'react'
import { MagnifyingGlassIcon, XMarkIcon } from '@heroicons/react/24/outline'

const TEAMS_BY_CONFEDERATION = {
  'Co-hosts': ['Canada', 'Mexico', 'USA'],
  'AFC': ['Australia', 'Iraq', 'IR Iran', 'Japan', 'Jordan', 'Korea Republic', 'Qatar', 'Saudi Arabia', 'Uzbekistan'],
  'CAF': ['Algeria', 'Cabo Verde', 'Congo DR', "Côte d'Ivoire", 'Egypt', 'Ghana', 'Morocco', 'Senegal', 'South Africa', 'Tunisia'],
  'Concacaf': ['Curaçao', 'Haiti', 'Panama'],
  'CONMEBOL': ['Argentina', 'Brazil', 'Colombia', 'Ecuador', 'Paraguay', 'Uruguay'],
  'OFC': ['New Zealand'],
  'UEFA': ['Austria', 'Belgium', 'Bosnia and Herzegovina', 'Croatia', 'Czechia', 'England', 'France', 'Germany', 'Netherlands', 'Norway', 'Portugal', 'Scotland', 'Spain', 'Sweden', 'Switzerland', 'Türkiye'],
}

const ALL_TEAMS = Object.values(TEAMS_BY_CONFEDERATION).flat()

const COUNTRY_CODES = {
  Canada: 'ca', Mexico: 'mx', USA: 'us',
  Australia: 'au', Iraq: 'iq', 'IR Iran': 'ir', Japan: 'jp', Jordan: 'jo',
  'Korea Republic': 'kr', Qatar: 'qa', 'Saudi Arabia': 'sa', Uzbekistan: 'uz',
  Algeria: 'dz', 'Cabo Verde': 'cv', 'Congo DR': 'cd', "Côte d'Ivoire": 'ci',
  Egypt: 'eg', Ghana: 'gh', Morocco: 'ma', Senegal: 'sn',
  'South Africa': 'za', Tunisia: 'tn',
  Curaçao: 'cw', Haiti: 'ht', Panama: 'pa',
  Argentina: 'ar', Brazil: 'br', Colombia: 'co', Ecuador: 'ec',
  Paraguay: 'py', Uruguay: 'uy',
  'New Zealand': 'nz',
  Austria: 'at', Belgium: 'be', 'Bosnia and Herzegovina': 'ba', Croatia: 'hr',
  Czechia: 'cz', England: 'gb-eng', France: 'fr', Germany: 'de',
  Netherlands: 'nl', Norway: 'no', Portugal: 'pt', Scotland: 'gb-sct',
  Spain: 'es', Sweden: 'se', Switzerland: 'ch', Türkiye: 'tr',
}

const FlagImg = ({ name }) => {
  const code = COUNTRY_CODES[name]
  if (!code) return <span className="text-base leading-none">🏳️</span>
  return (
    <img
      src={`https://flagcdn.com/24x18/${code}.png`}
      srcSet={`https://flagcdn.com/48x36/${code}.png 2x, https://flagcdn.com/72x54/${code}.png 3x`}
      alt={`${name} flag`}
      className="w-5 h-auto rounded-[2px] object-cover"
      loading="lazy"
    />
  )
}

export default function TeamSelector({ selected, onChange }) {
  const [query, setQuery] = useState('')

  const filteredConfs = useMemo(() => {
    if (!query) return TEAMS_BY_CONFEDERATION
    const lower = query.toLowerCase()
    const result = {}
    for (const [conf, teams] of Object.entries(TEAMS_BY_CONFEDERATION)) {
      const filtered = teams.filter(t => t.toLowerCase().includes(lower))
      if (filtered.length > 0) result[conf] = filtered
    }
    return result
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
              <FlagImg name={team} /> {team}
              <button onClick={() => toggle(team)} className="ml-1 hover:text-amber-500">
                <XMarkIcon className="w-3.5 h-3.5" />
              </button>
            </span>
          ))}
        </div>
      )}

      <div className="relative mb-3">
        <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
        <input
          type="text"
          placeholder="Search teams..."
          value={query}
          onChange={e => setQuery(e.target.value)}
          className="w-full pl-9 pr-4 py-2.5 rounded-xl border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm focus:ring-2 focus:ring-amber-400/50 focus:border-transparent outline-none transition-all"
        />
      </div>

      <div className="space-y-4 max-h-80 overflow-y-auto scrollbar-thin pr-1">
        {Object.entries(filteredConfs).map(([conf, teams]) => (
          <div key={conf}>
            <div className="flex items-center gap-2 mb-2">
              <span className="text-[11px] font-semibold uppercase tracking-widest text-amber-600 dark:text-amber-400">{conf}</span>
              <span className="h-px flex-1 bg-gray-200 dark:bg-gray-700" />
              <span className="text-[10px] text-gray-400 font-mono">{teams.length}</span>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-1.5">
              {teams.map(team => {
                const isSelected = selected.includes(team)
                return (
                  <button
                    key={team}
                    onClick={() => toggle(team)}
                    className={`flex items-center gap-2 px-3 py-2 rounded-xl text-sm font-medium transition-all ${
                      isSelected
                        ? 'bg-gray-950 dark:bg-white text-white dark:text-gray-950 shadow-sm'
                        : 'bg-gray-100 dark:bg-gray-800/60 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700 hover:scale-[1.02]'
                    }`}
                  >
                    <FlagImg name={team} />
                    <span className="truncate">{team}</span>
                  </button>
                )
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
