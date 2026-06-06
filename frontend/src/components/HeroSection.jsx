import { Link } from 'react-router-dom'
import { ArrowRightIcon } from '@heroicons/react/24/outline'
import { motion } from 'framer-motion'

const heroWords = ["THE", "WORLD'S", "GAME.", "YOUR", "TRIP."]

const container = {
  hidden: {},
  visible: {
    transition: { staggerChildren: 0.12, delayChildren: 0.3 },
  },
}

const wordAnim = {
  hidden: { opacity: 0, y: 40 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.6, ease: [0.25, 0.1, 0.25, 1] },
  },
}

export default function HeroSection() {
  return (
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
          variants={container}
          initial="hidden"
          animate="visible"
          className="font-display text-6xl sm:text-7xl lg:text-8xl font-black text-white leading-[0.9] tracking-tight mb-6"
        >
          {heroWords.map((word, i) => (
            <motion.span
              key={i}
              variants={wordAnim}
              className={`inline-block ${word === 'GAME.' ? 'text-amber-400' : ''} ${i > 2 ? 'ml-4' : ''}`}
            >
              {word}
              {i === 2 && <br />}
            </motion.span>
          ))}
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 1.2 }}
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
          transition={{ duration: 0.6, delay: 1.5 }}
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
          transition={{ duration: 0.8, delay: 1.8 }}
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
            3 Countries
            <span className="text-base leading-none ml-0.5">🇺🇸🇨🇦🇲🇽</span>
          </span>
        </motion.div>
      </div>
    </section>
  )
}
