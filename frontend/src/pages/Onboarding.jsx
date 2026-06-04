import OnboardingWizard from '../components/OnboardingWizard'

export default function Onboarding() {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950 py-8">
      <div className="max-w-2xl mx-auto px-4 text-center mb-4">
        <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white">
          Build Your World Cup Trip
        </h1>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
          Answer a few questions and let AI do the rest
        </p>
      </div>
      <OnboardingWizard />
    </div>
  )
}
