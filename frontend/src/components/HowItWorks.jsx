const steps = [
  {
    number: '01',
    title: 'Tell us your preferences',
    desc: 'Pick your favorite team, set your budget, choose travel dates — we do the rest.',
  },
  {
    number: '02',
    title: 'AI builds your itinerary',
    desc: 'Gemini-powered agent searches matches, finds hotels, and plans your daily schedule across host cities.',
  },
  {
    number: '03',
    title: 'Refine & share',
    desc: 'Chat with your agent to adjust anything. Save your perfect World Cup adventure.',
  },
]

export default function HowItWorks() {
  return (
    <section className="py-20 bg-white dark:bg-gray-950">
      <div className="max-w-5xl mx-auto px-4">
        <h2 className="text-3xl sm:text-4xl font-bold text-center text-gray-900 dark:text-white mb-4">
          How It Works
        </h2>
        <p className="text-center text-gray-500 dark:text-gray-400 mb-16 max-w-lg mx-auto">
          Three simple steps to your ultimate World Cup experience
        </p>
        <div className="grid md:grid-cols-3 gap-8">
          {steps.map((step, i) => (
            <div key={i} className="relative text-center group">
              <div className="w-16 h-16 mx-auto mb-4 rounded-full border-2 border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 flex items-center justify-center">
                <span className="text-xs font-bold text-gray-900 dark:text-white">{step.number}</span>
              </div>
              <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">{step.title}</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400 leading-relaxed">{step.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
