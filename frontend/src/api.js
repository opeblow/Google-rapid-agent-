import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
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
