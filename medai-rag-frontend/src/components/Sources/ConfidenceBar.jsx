// src/components/Sources/ConfidenceBar.jsx
import React from "react";

export default function ConfidenceBar({
  value = 0,
  labelSuffix = null,
}) {
  const pct = Math.round((Number(value) || 0) * 100);

  // Map exact ranges to Tailwind classes (static strings to avoid purge issues)
  function colorClasses(p) {
    if (p <= 55) {
      return { text: "text-red-600", bar: "bg-red-500" };
    } else if (p <= 65) {
      return { text: "text-orange-600", bar: "bg-orange-500" };
    } else if (p <= 75) {
      return { text: "text-yellow-600", bar: "bg-yellow-400" };
    } else if (p <= 85) {
      return { text: "text-green-600", bar: "bg-green-500" };
    }
    // 86–100
    return { text: "text-blue-600", bar: "bg-blue-500" };
  }

  const { text: textColor, bar: barColor } = colorClasses(pct);

  return (
    <div>
      {/* Header row */}
      <div className="mb-1 flex items-center justify-between">
        <div className="flex items-center gap-1.5">
          <span className="text-sm font-semibold text-gray-900">Confidence</span>
          {labelSuffix}
        </div>
        <span className={`text-sm font-semibold ${textColor}`}>{pct}%</span>
      </div>

      {/* Bar */}
      <div className="h-2 w-full overflow-hidden rounded-full bg-gray-100">
        <div
          className={`h-full rounded-full transition-all ${barColor}`}
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
