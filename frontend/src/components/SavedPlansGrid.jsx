import PlanCard from './PlanCard'
import EmptyState from './EmptyState'

export default function SavedPlansGrid({ plans }) {
  if (!plans || plans.length === 0) {
    return (
      <EmptyState
        icon="📋"
        title="No plans yet"
        description="Start planning your World Cup adventure! Our AI agent will build a personalized itinerary."
        actionLabel="Create New Plan"
        actionTo="/onboard"
      />
    )
  }

  return (
    <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
      {plans.map((item, i) => (
        <PlanCard key={i} plan={item.data} sessionId={item.sessionId} />
      ))}
    </div>
  )
}
