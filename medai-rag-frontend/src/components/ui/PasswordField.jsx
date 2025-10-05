// src/components/ui/PasswordField.jsx
import React, { useState } from "react"
import { motion } from "framer-motion"

export default function PasswordField({
  value,
  onChange,
  placeholder = "Password",
  id,
  className = "",
  disabled = false,
}) {
  const [show, setShow] = useState(false)

  return (
    <div className={`relative ${className}`}>
      <input
        id={id}
        type={show ? "text" : "password"}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        disabled={disabled}
        className="w-full rounded-lg border border-gray-300 px-3 py-2 pr-11 text-sm focus:ring-2 focus:ring-blue-500"
        autoComplete="current-password"
      />

      {/* Toggle button */}
      <button
        type="button"
        aria-label={show ? "Hide password" : "Show password"}
        onClick={() => setShow(s => !s)}
        className="absolute right-2 top-1/2 -translate-y-1/2 inline-flex h-8 w-8 items-center justify-center rounded-full
                   border border-gray-200 bg-white/80 backdrop-blur hover:bg-white shadow-sm transition"
      >
        {/* Single SVG (avoids layout jump) */}
        <motion.svg
          viewBox="0 0 24 24"
          className="h-5 w-5 text-gray-700"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.6"
          strokeLinecap="round"
          strokeLinejoin="round"
          // keep the same bounding box; animate gently
          initial={false}
        >
          {/* Eye outline (static) */}
          <path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6S2 12 2 12Z" />

          {/* Iris/pupil (scale/opacity when hiding) */}
          <motion.circle
            cx="12"
            cy="12"
            r="3"
            animate={{
              scale: show ? 1 : 0.75,
              opacity: show ? 1 : 0.75,
            }}
            transition={{ type: "spring", stiffness: 260, damping: 18 }}
            style={{ transformOrigin: "12px 12px" }}
          />

          {/* Subtle eyelid accent (just a faint upper arc; static to avoid shift) */}
          <path d="M4 9.5c2.2-1.7 4.9-2.5 8-2.5s5.8.8 8 2.5" opacity=".25" />

          {/* Slash (animated show/hide) */}
          <motion.path
            d="M3 3l18 18"
            animate={{
              opacity: show ? 0 : 1,
              rotate: show ? 8 : 0, // tiny flourish when revealing
            }}
            transition={{ type: "spring", stiffness: 300, damping: 22 }}
            style={{ transformOrigin: "12px 12px" }}
          />
        </motion.svg>
      </button>
    </div>
  )
}
