const CHAT_KEY = 'medai_chat_v1'
export function loadChat(){ try { return JSON.parse(localStorage.getItem(CHAT_KEY)) ?? [] } catch { return [] } }
export function saveChat(messages){ localStorage.setItem(CHAT_KEY, JSON.stringify(messages)) }
export function clearChat(){ localStorage.removeItem(CHAT_KEY) }
