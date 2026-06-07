import { useState, useRef, useEffect } from 'react'
import { PaperAirplaneIcon } from '@heroicons/react/24/outline'
import MessageBubble from './MessageBubble'
import TypingIndicator from './TypingIndicator'
import SuggestedChips from './SuggestedChips'
import { sendMessage, getSessionHistory } from '../api'

export default function ChatInterface({ sessionId, onPlanUpdate }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [hydrating, setHydrating] = useState(true)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  // Rehydrate the dashboard from its session: the plan was already generated
  // (during onboarding or a prior visit) and lives in the session history.
  useEffect(() => {
    if (!sessionId) { setHydrating(false); return }
    let cancelled = false
    setHydrating(true)
    getSessionHistory(sessionId)
      .then(history => {
        if (cancelled || !Array.isArray(history)) return
        setMessages(
          history
            .filter(m => m.content)
            .map(m => ({ role: m.role === 'user' ? 'user' : 'assistant', content: m.content }))
        )
        const lastPlan = [...history].reverse().find(m => m.plan_data)?.plan_data
        if (lastPlan && onPlanUpdate) onPlanUpdate(lastPlan)
      })
      .catch(() => { /* new/empty session returns 404 — keep the empty state */ })
      .finally(() => { if (!cancelled) setHydrating(false) })
    return () => { cancelled = true }
  }, [sessionId, onPlanUpdate])

  const handleSend = async (text) => {
    const msg = (text || input).trim()
    if (!msg || loading) return
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: msg }])
    setLoading(true)
    try {
      const data = await sendMessage(msg, sessionId)
      setMessages(prev => [...prev, { role: 'assistant', content: data.reply }])
      if (data.plan_data && onPlanUpdate) onPlanUpdate(data.plan_data)
    } catch {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, I encountered an error. Please try again.' }])
    }
    setLoading(false)
  }

  return (
    <div className="flex flex-col h-full bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-800 overflow-hidden">
      <div className="flex items-center gap-2 px-4 py-3 border-b border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-900/50">
        <div className="w-8 h-8 rounded-full bg-gray-950 dark:bg-white flex items-center justify-center text-white dark:text-gray-950 text-sm font-bold">FF</div>
        <div>
          <p className="text-sm font-semibold text-gray-900 dark:text-white">Fanfare</p>
          <p className="text-xs text-gray-400">AI Travel Agent</p>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-3 scrollbar-thin">
        {hydrating && messages.length === 0 && (
          <div className="text-center py-12 text-gray-400 text-sm">Loading your conversation…</div>
        )}
        {!hydrating && messages.length === 0 && (
          <div className="text-center py-12 text-gray-400">
            <p className="font-medium text-gray-600 dark:text-gray-300">Ask me anything about your trip!</p>
            <p className="text-sm mt-1">Try searching for matches, building a plan, or getting recommendations.</p>
          </div>
        )}
        {messages.map((m, i) => (
          <MessageBubble key={i} role={m.role} content={m.content} />
        ))}
        {loading && <TypingIndicator />}
        <div ref={bottomRef} />
      </div>

      {!loading && messages.length > 0 && (
        <div className="px-4 py-2 border-t border-gray-100 dark:border-gray-800">
          <SuggestedChips onSelect={handleSend} />
        </div>
      )}

      <div className="px-4 py-3 border-t border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900">
        <div className="flex items-center gap-2">
          <input
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSend()}
            placeholder="Ask about matches, hotels, or your plan..."
            disabled={loading}
            className="flex-1 px-4 py-2.5 rounded-xl border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-800 text-sm focus:ring-2 focus:ring-gray-400 dark:focus:ring-gray-500 focus:border-transparent outline-none transition-all disabled:opacity-50"
          />
          <button
            onClick={() => handleSend()}
            disabled={loading || !input.trim()}
            className="p-2.5 rounded-xl bg-gray-950 dark:bg-white text-white dark:text-gray-950 hover:bg-gray-800 dark:hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition-all active:scale-95"
          >
            <PaperAirplaneIcon className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  )
}
