import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useEffect, useState } from 'react'

const fadeInUp = {
  hidden: { opacity: 0, y: 40 },
  visible: (i = 0) => ({
    opacity: 1,
    y: 0,
    transition: { duration: 0.7, delay: i * 0.2, ease: [0.25, 0.1, 0.25, 1] },
  }),
}

function CountUp({ end, duration = 2 }) {
  const [count, setCount] = useState(0)
  useEffect(() => {
    let startTime; let raf
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

const steps = [
  {
    number: '01',
    title: 'Pick your teams & dates',
    desc: 'Choose who you\'re supporting, set your budget, and pick your travel window.',
  },
  {
    number: '02',
    title: 'AI builds your itinerary',
    desc: 'Matches, hotels, daily plans — generated across cities and countries.',
  },
  {
    number: '03',
    title: 'Refine & share',
    desc: 'Chat to tweak anything. Save your perfect trip and share it.',
  },
]

export default function Landing() {
  return (
    <div className="min-h-screen bg-gray-950 text-white">

      {/* ─── NAVBAR ─── */}
      <motion.nav
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5 }}
        className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-6 sm:px-10 py-5 bg-gray-950/80 backdrop-blur-md border-b border-gray-800"
      >
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-white/10 border border-white/20 flex items-center justify-center text-sm font-bold">WC</div>
          <span className="font-display font-bold text-white text-lg tracking-tight">2026 Agent</span>
        </div>
        <Link
          to="/onboard"
          className="px-5 py-2 rounded-xl bg-white text-gray-950 text-sm font-semibold hover:bg-gray-200 active:scale-95 transition-all duration-200"
        >
          Get Started
        </Link>
      </motion.nav>

      {/* ─── HERO ─── */}
      <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-gray-950">
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none select-none">
          <div className="w-[800px] h-[500px] max-w-full border-2 border-gray-800 rounded-[50%] opacity-40" />
          <div className="absolute w-[600px] h-[350px] max-w-[80%] border border-gray-800 rounded-[50%] opacity-20" />
        </div>

        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-[18vw] font-display font-black text-gray-800/20 pointer-events-none select-none leading-none">
          2026
        </div>

        <div
          className="absolute inset-0 opacity-[0.03] pointer-events-none"
          style={{
            backgroundImage: `linear-gradient(rgba(255,255,255,0.3) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.3) 1px, transparent 1px)`,
            backgroundSize: '60px 60px',
          }}
        />

        <div className="relative z-10 max-w-5xl mx-auto px-6 text-center py-32">
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-white/5 border border-white/10 text-white/50 text-[11px] font-medium tracking-widest uppercase mb-10"
          >
            Google Cloud Hackathon — MongoDB Track
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.3, ease: [0.25, 0.1, 0.25, 1] }}
            className="font-display text-6xl sm:text-7xl lg:text-8xl font-black text-white leading-[0.9] tracking-tight mb-6"
          >
            THE WORLD'S<br />
            <span className="text-amber-400">GAME.</span>
            <br />
            YOUR TRIP.
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.8 }}
            className="text-base sm:text-lg text-gray-400 max-w-xl mx-auto mb-10 leading-relaxed"
          >
            An AI travel agent that plans your 2026 World Cup adventure across{' '}
            <span className="text-white font-semibold">16 host cities</span> in{' '}
            <span className="text-white font-semibold">3 countries</span>
            <span className="inline-block ml-2">🇺🇸 🇨🇦 🇲🇽</span>.
            Matches, hotels, budget — handled.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 1.1 }}
          >
            <Link
              to="/onboard"
              className="inline-flex items-center gap-2 px-8 py-4 bg-white text-gray-950 font-bold text-lg rounded-xl
                         hover:bg-gray-200 active:scale-[0.97] transition-all duration-200"
            >
              Start Planning
              <span className="text-xl leading-none">→</span>
            </Link>
          </motion.div>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8, delay: 1.4 }}
            className="mt-14 flex items-center justify-center gap-6 sm:gap-10 text-gray-500 text-xs font-mono uppercase tracking-widest"
          >
            <span className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-amber-400/60" />
              104 Matches
            </span>
            <span className="w-px h-3 bg-gray-800" />
            <span className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-amber-400/60" />
              16 Cities
            </span>
            <span className="w-px h-3 bg-gray-800" />
            <span className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-amber-400/60" />
              48 Teams
            </span>
          </motion.div>
        </div>
      </section>

      {/* ─── STATS ─── */}
      <section className="py-20 border-t border-gray-800">
        <div className="max-w-5xl mx-auto px-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {[
              { value: 104, label: 'Matches' },
              { value: 48, label: 'Teams' },
              { value: 16, label: 'Host Cities' },
              { value: 3, label: 'Countries 🇺🇸🇨🇦🇲🇽' },
            ].map((s, i) => (
              <motion.div
                key={s.label}
                custom={i}
                variants={fadeInUp}
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true, margin: '-50px' }}
                className="text-center"
              >
                <div className="font-display text-4xl sm:text-5xl font-black text-white tracking-tight tabular-nums">
                  <CountUp end={s.value} duration={2.2 + i * 0.15} />
                </div>
                <div className="text-xs text-amber-400/80 font-semibold uppercase tracking-widest mt-1.5">{s.label}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ─── HOW IT WORKS ─── */}
      <section className="py-28 border-t border-gray-800">
        <div className="max-w-5xl mx-auto px-6">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="text-center mb-20"
          >
            <h2 className="font-display text-4xl sm:text-5xl font-black text-white tracking-tight mb-3">How It Works</h2>
            <p className="text-gray-500 max-w-md mx-auto">Three steps to your perfect World Cup trip</p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-0 md:gap-8 relative">
            <div className="hidden md:block absolute top-12 left-[calc(16.66%+2rem)] right-[calc(16.66%+2rem)] h-px bg-gray-800 z-0" />

            {steps.map((step, i) => (
              <motion.div
                key={i}
                custom={i}
                variants={fadeInUp}
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true, margin: '-50px' }}
                className="relative text-center group"
              >
                <div className="relative z-10 inline-flex items-center justify-center w-12 h-12 mb-6 rounded-full border-2 border-gray-700 bg-gray-900 group-hover:border-amber-400/50 transition-colors duration-300">
                  <span className="text-xs font-bold text-white">{step.number}</span>
                </div>
                <div className="text-[11px] font-mono text-amber-400/80 tracking-widest mb-2">{step.number}</div>
                <h3 className="font-display text-lg font-bold text-white mb-2">{step.title}</h3>
                <p className="text-sm text-gray-500 leading-relaxed max-w-xs mx-auto">{step.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ─── TESTIMONIAL ─── */}
      <motion.section
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6 }}
        className="py-20 border-t border-gray-800"
      >
        <div className="max-w-3xl mx-auto px-6">
          <div className="relative p-10 sm:p-14 rounded-2xl border border-gray-800 bg-gray-900/50">
            <span className="absolute -top-4 left-8 text-6xl text-gray-700 font-serif leading-none select-none">"</span>
            <blockquote className="text-lg sm:text-xl text-gray-300 leading-relaxed mb-5 relative z-10">
              I told the agent my team, budget, and dates — within seconds I had a full itinerary
              with matches, hotels, and a daily plan. This is the future of trip planning.
            </blockquote>
            <div className="flex items-center gap-3 text-sm">
              <div className="w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center text-xs font-bold text-gray-300">BT</div>
              <div>
                <p className="text-white font-medium">Beta Tester</p>
                <p className="text-gray-500 text-xs">New York City</p>
              </div>
            </div>
          </div>
        </div>
      </motion.section>

      {/* ─── POWERED BY ─── */}
      <motion.section
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6 }}
        className="py-16 border-t border-gray-800"
      >
        <div className="max-w-5xl mx-auto px-6 text-center">
          <p className="text-xs font-mono uppercase tracking-[0.2em] text-gray-600 mb-8">Powered By</p>
          <div className="flex flex-wrap justify-center gap-3">
            {['Gemini', 'MongoDB', 'Google Cloud', 'FastAPI', 'React'].map(name => (
              <span
                key={name}
                className="px-5 py-2.5 rounded-xl border border-gray-800 bg-gray-900 text-gray-400 text-sm font-semibold
                           hover:border-gray-600 hover:text-white transition-all duration-200 cursor-default"
              >
                {name}
              </span>
            ))}
          </div>
        </div>
      </motion.section>

      {/* ─── CTA ─── */}
      <motion.section
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6 }}
        className="py-28 border-t border-gray-800"
      >
        <div className="max-w-3xl mx-auto px-6 text-center">
          <h2 className="font-display text-4xl sm:text-5xl font-black text-white tracking-tight mb-4">
            Ready for the Cup?
          </h2>
          <p className="text-gray-500 mb-10 max-w-md mx-auto">
            Join thousands of fans planning their 2026 World Cup adventure across 16 host cities.
          </p>
          <Link
            to="/onboard"
            className="inline-flex items-center gap-2 px-8 py-4 bg-white text-gray-950 font-bold text-lg rounded-xl
                       hover:bg-gray-200 active:scale-[0.97] transition-all duration-200"
          >
            Start Planning Now
            <span className="text-xl leading-none">→</span>
          </Link>
        </div>
      </motion.section>

      {/* ─── FOOTER ─── */}
      <footer className="py-8 border-t border-gray-800 text-center">
        <p className="text-xs text-gray-600">
          &copy; {new Date().getFullYear()} WC2026 Agent — Google Cloud Rapid Agent Hackathon (MongoDB Track)
        </p>
      </footer>
    </div>
  )
}
