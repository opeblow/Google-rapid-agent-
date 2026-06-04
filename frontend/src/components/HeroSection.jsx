import { Link } from 'react-router-dom'
import { ArrowRightIcon } from '@heroicons/react/24/outline'

export default function HeroSection() {
  return (
    <section className="relative min-h-[80vh] flex items-center justify-center overflow-hidden gradient-hero dark:gradient-hero-dark">
      <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmYiIGZpbGwtb3BhY2l0eT0iMC4wNSI+PHBhdGggZD0iTTM2IDM0djItSDI0di0yaDEyek0zNiAyNHYySDI0di0yaDEyeiIvPjwvZz48L2c+PC9zdmc+')] opacity-50" />
      <div className="relative z-10 max-w-5xl mx-auto px-4 text-center py-20">
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-white/15 backdrop-blur-sm text-white/80 text-xs font-medium mb-8 border border-white/10">
          Google Cloud Rapid Agent Hackathon — MongoDB Track
        </div>
        <h1 className="font-display text-5xl sm:text-6xl lg:text-7xl font-extrabold text-white leading-tight mb-6">
          Plan Your World Cup<br />
          <span className="bg-clip-text text-transparent bg-gradient-to-r from-yellow-300 via-white to-green-200">
            2026 Adventure
          </span>
        </h1>
        <p className="text-lg sm:text-xl text-white/80 max-w-2xl mx-auto mb-10 leading-relaxed">
          AI-powered trip planner across <strong className="text-white">16 host cities</strong> in USA, Canada &amp; Mexico.
          Your personal travel agent builds the perfect itinerary.
        </p>
        <Link
          to="/onboard"
          className="inline-flex items-center gap-2 px-8 py-4 bg-white text-gray-900 font-bold text-lg rounded-2xl
                     hover:bg-gray-100 active:scale-[0.97] transition-all duration-200 shadow-2xl shadow-black/20
                     hover:shadow-white/25 group"
        >
          Start Planning
          <ArrowRightIcon className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
        </Link>
        <div className="mt-12 flex items-center justify-center gap-6 sm:gap-10 text-white/50 text-sm">
          <span className="flex items-center gap-2">⚽ 48 Matches</span>
          <span className="w-px h-4 bg-white/20" />
          <span className="flex items-center gap-2">🏙️ 16 Cities</span>
          <span className="w-px h-4 bg-white/20" />
          <span className="flex items-center gap-2">🌎 3 Countries</span>
        </div>
      </div>
    </section>
  )
}
