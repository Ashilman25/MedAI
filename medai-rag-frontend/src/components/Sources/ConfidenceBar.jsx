// src/components/Sources/ConfidenceBar.jsx
import React from "react";

export default function ConfidenceBar({
  value = 0,
  labelSuffix = null, 
}) {
  const pct = Math.round((Number(value) || 0) * 100);
  const color =
    pct >= 70 ? "text-emerald-600"
    : pct >= 40 ? "text-amber-600"
    : "text-red-600";

  return (
    <div>
      {/* Header row */}
      <div className="mb-1 flex items-center justify-between">
        <div className="flex items-center gap-1.5">
          <span className="text-sm font-semibold text-gray-900">Confidence</span>
          {labelSuffix}
        </div>
        <span className={`text-sm ${color}`}>{pct}%</span>
      </div>

      {/* Bar */}
      <div className="h-2 w-full overflow-hidden rounded-full bg-gray-100">
        <div
          className="h-full rounded-full bg-gray-400 transition-all"
          style={{ width: `${pct}%` }}
        />
      </div>

      {/* Hint */}
      <div className="mt-2 text-xs text-red-700">
        Some details may be uncertain. Verify in the sources below.
      </div>
    </div>
  );
}
