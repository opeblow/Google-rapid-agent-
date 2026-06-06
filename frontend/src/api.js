import axios from 'axios'

const PRODUCTION_API = 'https://wc2026-backend-gh61.onrender.com'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || PRODUCTION_API,
  headers: { 'Content-Type': 'application/json' },
})

export async function sendMessage(message, sessionId = null) {
  const { data } = await api.post('/api/chat', { message, session_id: sessionId })
  return data
}

export async function getSessionHistory(sessionId) {
  const { data } = await api.get(`/api/history/${sessionId}`)
  return data
}

export async function getSessionInfo(sessionId) {
  const { data } = await api.get(`/api/sessions/${sessionId}`)
  return data
}

export async function getPlan(planId) {
  const { data } = await api.get(`/api/plans/${planId}`)
  return data
}

export async function updatePlan(planId, updates) {
  const { data } = await api.put(`/api/plans/${planId}`, { updates })
  return data
}

export default api
