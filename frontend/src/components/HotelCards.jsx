export default function HotelCards({ hotels }) {
  if (!hotels || hotels.length === 0) {
    return (
      <div className="text-center py-8 text-gray-400">
        <p className="text-sm">Ask the agent to recommend hotels for your trip!</p>
      </div>
    )
  }

  return (
    <div className="grid sm:grid-cols-2 gap-3">
      {hotels.map((hotel, i) => (
        <div key={i} className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4 hover:border-gray-300 dark:hover:border-gray-600 transition-all">
          <div className="flex items-start justify-between mb-2">
            <div>
              <h4 className="font-semibold text-gray-900 dark:text-white text-sm">{hotel.name}</h4>
              <p className="text-xs text-gray-400">{hotel.location || hotel.city}</p>
            </div>
            <span className="text-yellow-500 text-xs">{'★'.repeat(hotel.stars || 3)}</span>
          </div>

          {hotel.amenities && (
            <div className="flex flex-wrap gap-1.5 mb-2">
              {hotel.amenities.map(a => (
                <span key={a} className="text-xs">{a}</span>
              ))}
            </div>
          )}

          <div className="flex justify-between items-center mt-2 pt-2 border-t border-gray-100 dark:border-gray-700">
            <span className="text-lg font-bold text-gray-950 dark:text-white">
              ${hotel.price_per_night || hotel.price || '—'}
              <span className="text-xs font-normal text-gray-400">/night</span>
            </span>
            <span className="text-xs text-gray-400 font-medium">View →</span>
          </div>
        </div>
      ))}
    </div>
  )
}
