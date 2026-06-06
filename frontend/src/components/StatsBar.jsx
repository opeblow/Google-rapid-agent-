import { motion } from 'framer-motion'
import { useEffect, useState } from 'react'

const stats = [
  { value: 104, label: 'Matches', suffix: '' },
  { value: 48, label: 'Teams', suffix: '' },
  { value: 16, label: 'Host Cities', suffix: '' },
  { value: 3, label: 'Countries  🇺🇸🇨🇦🇲🇽', suffix: '' },
]

function CountUp({ end, duration = 2 }) {
  const [count, setCount] = useState(0)
  useEffect(() => {
    let startTime
    let raf
    const animate = (time) => {
      if (!startTime) startTime = time
      const progress = Math.min((time - startTime) / (duration * 1000), 1)
      setCount(Math.floor(progress * end))
      if (progress < 1) raf = requestAnimationFrame(animate)
    }
    raf = requestAnimationFrame(animate)
    return () => cancelAnimationFrame(raf)
  }, [end, duration])
  return count
}

export default function StatsBar() {
  return (
    <section className="py-16 bg-gray-50 dark:bg-gray-900/30 border-y border-gray-200 dark:border-gray-800">
      <div className="max-w-5xl mx-auto px-4">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 md:gap-12">
          {stats.map((s, i) => (
            <motion.div
              key={s.label}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: '-50px' }}
              transition={{ duration: 0.5, delay: i * 0.15 }}
              className="text-center"
            >
              <div className="font-display text-4xl sm:text-5xl font-black text-gray-900 dark:text-white tracking-tight tabular-nums">
                <CountUp end={s.value} duration={2 + i * 0.2} />
                {s.suffix}
              </div>
              <div className="text-xs font-semibold uppercase tracking-widest text-amber-600 dark:text-amber-400 mt-1.5">
                {s.label}
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
