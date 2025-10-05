// src/components/Landing/PreviewWindow.jsx
import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import Logo from "../../assets/logo.svg";

export default function PreviewWindow({ mode = "guest" }) {
  const isUser = mode === "user";
  return (
    <AnimatePresence mode="wait">
      {isUser ? <UserPreview key="user" /> : <GuestPreview key="guest" />}
    </AnimatePresence>
  );
}

/* ------------------------------- Guest View ------------------------------- */

function GuestPreview() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8, scale: 0.99 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: 6, scale: 0.99 }}
      transition={{ duration: 0.25 }}
      className="relative rounded-2xl border border-gray-200 bg-white p-4 shadow-card overflow-hidden animate-breath"
    >
      {/* Logo + ripple */}
      <div className="absolute left-4 top-4">
        <div className="relative group">
          <img src={Logo} alt="MedAI-RAG" className="h-8 w-8" />
          <div className="pointer-events-none absolute -inset-2 rounded-full opacity-0 group-hover:opacity-100 transition">
            <span className="absolute inset-0 rounded-full ring-2 ring-medical-blue/30 animate-ripple" />
            <span className="absolute inset-0 rounded-full ring-2 ring-medical-blue/20 animate-ripple delay-200" />
          </div>
        </div>
      </div>

      {/* 2-column mock: center chat + right sources */}
      <div className="grid lg:grid-cols-3 gap-4 mt-8">
        {/* Center: Chat mock */}
        <motion.div
          initial={{ opacity: 0, y: 6 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.05 }}
          className="lg:col-span-2 rounded-2xl border border-gray-200 bg-white/70 backdrop-blur p-4"
        >
          <div className="space-y-3">
            {/* User bubble (placeholder) */}
            <div className="max-w-[75%] rounded-2xl bg-gray-100 px-4 py-2 text-gray-500">
              <div className="h-4 w-48 bg-gray-200 rounded shimmer" />
            </div>
            {/* AI bubble (typewriter) */}
            <div className="max-w-[85%] rounded-2xl bg-gradient-to-br from-medical-blue/10 to-medical-green/10 px-4 py-3 border border-medical-blue/10 shadow-sm">
              <p className="typewriter text-sm text-gray-800">
                Generating a grounded answer with citations…
              </p>
              <div className="mt-1 text-[11px] text-gray-500">AI preview</div>
            </div>

            {/* Disabled input hint */}
            <div
              title="Start chatting — try guest mode!"
              className="mt-6 rounded-xl border border-gray-200 bg-gray-50 px-4 py-2 text-sm text-gray-400"
            >
              Message MedAI (preview)
            </div>
            <div className="text-xs text-gray-500 mt-1 animate-pulse">
              💬 Sign in to save your medical Q&A sessions.
            </div>
          </div>
        </motion.div>

        {/* Right: Sources skeleton */}
        <motion.aside
          initial={{ opacity: 0, x: 8 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
          className="rounded-2xl border border-gray-200 bg-white p-4"
        >
          <div className="text-sm font-semibold mb-3">Sources</div>
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div
                key={i}
                className="rounded-xl border border-gray-200 p-3 hover:border-gray-300 transition"
              >
                <div className="h-4 w-40 bg-gray-200 rounded shimmer" />
                <div className="mt-2 h-3 w-full bg-gray-100 rounded shimmer" />
                <div className="mt-1 h-3 w-2/3 bg-gray-100 rounded shimmer" />
                <div className="mt-2 text-[11px] text-gray-500">🔗 Source</div>
              </div>
            ))}
          </div>

          {/* Confidence (locked look) */}
          <div className="mt-4">
            <div className="flex items-center justify-between text-sm">
              <span className="font-medium">Confidence</span>
              <span className="text-gray-400">—</span>
            </div>
            <div className="mt-2 h-2 bg-gray-200 rounded-full overflow-hidden">
              <div className="h-full w-0 bg-medical-green" />
            </div>
            <div className="mt-1 text-xs text-gray-500">
              Sign in to view accuracy confidence.
            </div>
          </div>
        </motion.aside>
      </div>
    </motion.div>
  );
}

/* ------------------------------ Signed-in View ----------------------------- */

function UserPreview() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8, scale: 0.99 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: 6, scale: 0.99 }}
      transition={{ duration: 0.25 }}
      // match guest sizing + vibe; disable all interaction
      className="relative rounded-2xl border border-gray-200 bg-white p-4 shadow-card overflow-hidden animate-breath pointer-events-none select-none"
      aria-hidden="true"
    >
      {/* Logo + ripple (same as guest) */}
      <div className="absolute left-4 top-4">
        <div className="relative group">
          <img src={Logo} alt="MedAI-RAG" className="h-8 w-8" />
          <div className="pointer-events-none absolute -inset-2 rounded-full opacity-0 group-hover:opacity-100 transition">
            <span className="absolute inset-0 rounded-full ring-2 ring-medical-blue/30 animate-ripple" />
            <span className="absolute inset-0 rounded-full ring-2 ring-medical-blue/20 animate-ripple delay-200" />
          </div>
        </div>
      </div>

      {/* Same grid as guest: center chat (2 cols) + right sources (1 col) */}
      <div className="grid lg:grid-cols-3 gap-4 mt-8">
        {/* Center: Chat mock with real-looking text */}
        <motion.div
          initial={{ opacity: 0, y: 6 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.05 }}
          className="lg:col-span-2 rounded-2xl border border-gray-200 bg-white/70 backdrop-blur p-4"
        >
          <div className="space-y-3">
            {/* User bubble */}
            <motion.div
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.10 }}
              className="max-w-[75%] rounded-2xl bg-gray-100 px-4 py-2"
            >
              <div className="text-sm text-gray-800">
                What’s the latest on hypertension treatment?
              </div>
            </motion.div>

            {/* AI bubble (styled like guest; clear text + subtle tag) */}
            <motion.div
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.15 }}
              className="max-w-[95%] rounded-2xl bg-gradient-to-br from-medical-blue/10 to-medical-green/10 px-4 py-3 border border-medical-blue/10 shadow-sm"
            >
              <p className="text-sm text-gray-900">
                According to 2023 ACC/AHA guidelines, first-line therapy often
                includes thiazide diuretics, ACE inhibitors/ARBs, or calcium
                channel blockers, tailored to comorbidities and tolerance.
              </p>
              <div className="mt-1 text-[11px] text-teal-700">
                Updated answer (post-scan)
              </div>
            </motion.div>

            {/* Disabled input hint for parity with guest */}
            <div className="mt-6 rounded-xl border border-gray-200 bg-gray-50 px-4 py-2 text-sm text-gray-400">
              Message MedAI (preview)
            </div>
            <div className="text-xs text-gray-500 mt-1">
              Your chats are saved when you're signed in.
            </div>
          </div>
        </motion.div>

        {/* Right: Sources + animated confidence (no hover/links) */}
        <motion.aside
          initial={{ opacity: 0, x: 8 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.12 }}
          className="rounded-2xl border border-gray-200 bg-white p-4"
        >
          <div className="text-sm font-semibold mb-3">Sources</div>
          <div className="space-y-3">
            {[
              "[1] PubMed: Hypertension Guidelines 2023",
              "[2] JAMA: Comparative Beta Blocker Study",
              "[3] NEJM: ACE Inhibitor Review",
            ].map((title, i) => (
              <div
                key={i}
                className="rounded-xl border border-gray-200 p-3 transition"
              >
                <div className="text-sm font-medium text-gray-900">{title}</div>
                <div className="mt-1 text-xs text-gray-600">Preview only</div>
              </div>
            ))}
          </div>

          {/* Confidence animated fill */}
          <div className="mt-4">
            <div className="flex items-center justify-between text-sm">
              <span className="font-medium">Confidence</span>
              <span className="text-gray-600">85%</span>
            </div>
            <div className="mt-2 h-2 bg-gray-200 rounded-full overflow-hidden">
              <motion.div
                initial={{ width: "0%" }}
                animate={{ width: "85%" }}
                transition={{ type: "spring", stiffness: 80, damping: 18 }}
                className="h-full bg-medical-green"
              />
            </div>
            <div className="mt-1 text-xs text-gray-600">
              Grounded in verified clinical sources.
            </div>
          </div>
        </motion.aside>
      </div>
    </motion.div>
  );
}