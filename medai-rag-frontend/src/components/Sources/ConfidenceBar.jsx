import React from 'react'
export default function ConfidenceBar({ value }) {
  const pct = Math.round((value ?? 0) * 100)
  const low = (value ?? 0) < 0.6
  return (
    <div className='space-y-2'>
      <div className='flex items-center justify-between text-sm'>
        <span className='font-medium'>Confidence</span>
        <span className={low ? 'text-orange-600' : 'text-gray-600'}>{pct}%</span>
      </div>
      <div className='h-2 bg-gray-200 rounded-full overflow-hidden'>
        <div className={`h-full ${low ? 'bg-medical-warn' : 'bg-medical-green'}`} style={{ width: `${pct}%` }} />
      </div>
      {low && <p className='text-xs text-orange-700'>Some details may be uncertain. Verify in the sources below.</p>}
    </div>
  )
}
