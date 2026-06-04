export default function TypingIndicator() {
  return (
    <div className="flex justify-start animate-slide-up">
      <div className="chat-bubble-ai flex items-center gap-1.5 py-3 px-4">
        <span className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-pulse-dot" style={{ animationDelay: '0s' }} />
        <span className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-pulse-dot" style={{ animationDelay: '0.2s' }} />
        <span className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-pulse-dot" style={{ animationDelay: '0.4s' }} />
      </div>
    </div>
  )
}
