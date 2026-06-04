const stats = [
  { value: '48', label: 'Matches' },
  { value: '16', label: 'Host Cities' },
  { value: '3', label: 'Countries' },
  { value: '32', label: 'Teams' },
]

export default function StatsBar() {
  return (
    <section className="py-12 bg-gray-50 dark:bg-gray-900/50">
      <div className="max-w-5xl mx-auto px-4">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          {stats.map(s => (
            <div key={s.label} className="text-center">
              <div className="text-3xl font-bold text-gray-900 dark:text-white">{s.value}</div>
              <div className="text-sm text-gray-500 dark:text-gray-400">{s.label}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
