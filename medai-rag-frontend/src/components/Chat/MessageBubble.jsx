import React from 'react'
export default function MessageBubble({ role, content, children }) {
  const mine = role === 'user'
  return (
    <div className={`w-full flex ${mine ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-[90%] md:max-w-[70%] rounded-2xl px-4 py-3 shadow-card whitespace-pre-wrap
        ${mine ? 'bg-blue-50 text-blue-900 border border-blue-200' : 'bg-white text-gray-900 border border-gray-200'}`}>
        {content}
        {children}
      </div>
    </div>
  )
}
