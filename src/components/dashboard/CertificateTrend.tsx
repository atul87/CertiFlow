"use client";

import { useState } from "react";
import { BarChart3, RefreshCw } from "lucide-react";
import { TimeSeriesPoint } from "@/types";

interface CertificateTrendProps {
  data?: TimeSeriesPoint[];
  isLoading?: boolean;
  isError?: boolean;
  onRetry?: () => void;
  onRangeChange?: (range: "7d" | "30d" | "90d") => void;
}

export function CertificateTrend({
  data,
  isLoading,
  isError,
  onRetry,
  onRangeChange,
}: CertificateTrendProps) {
  const [range, setRange] = useState<"7d" | "30d" | "90d">("30d");

  const handleRange = (r: "7d" | "30d" | "90d") => {
    setRange(r);
    onRangeChange?.(r);
  };

  const chartData = data && data.length > 0 ? data : [
    { date: "Day 1", value: 120 },
    { date: "Day 5", value: 340 },
    { date: "Day 10", value: 890 },
    { date: "Day 15", value: 650 },
    { date: "Day 20", value: 1420 },
    { date: "Day 25", value: 980 },
    { date: "Day 30", value: 2150 },
  ];

  const maxValue = Math.max(...chartData.map((d) => d.value), 100);

  return (
    <div className="bg-white rounded-2xl border border-[var(--color-border)] p-6 shadow-xs">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <h3 className="text-[15px] font-bold text-[var(--color-text)]">
            Issuance & Delivery Trend
          </h3>
          <p className="text-[12px] text-[var(--color-text-secondary)] mt-0.5">
            Daily credential issuance volume across all active templates
          </p>
        </div>

        {/* Range Selector */}
        <div className="flex items-center gap-1 bg-gray-100 p-1 rounded-xl">
          {(["7d", "30d", "90d"] as const).map((r) => (
            <button
              key={r}
              onClick={() => handleRange(r)}
              className={`px-3 py-1 rounded-lg text-[11px] font-bold transition-all ${
                range === r
                  ? "bg-white text-[var(--color-text)] shadow-xs"
                  : "text-[var(--color-text-tertiary)] hover:text-[var(--color-text)]"
              }`}
            >
              {r.toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      {isLoading ? (
        <div className="h-48 flex items-end gap-3 pt-6 animate-pulse">
          {[40, 65, 30, 85, 95, 60, 80].map((h, i) => (
            <div
              key={i}
              className="flex-1 bg-gray-100 rounded-t-lg"
              style={{ height: `${h}%` }}
            />
          ))}
        </div>
      ) : isError ? (
        <div className="h-48 flex flex-col items-center justify-center text-center">
          <p className="text-[13px] text-red-600 mb-2">Unable to load trend chart</p>
          {onRetry && (
            <button
              onClick={onRetry}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[12px] font-semibold bg-red-50 text-red-700 hover:bg-red-100"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              Retry
            </button>
          )}
        </div>
      ) : chartData.length === 0 ? (
        <div className="h-48 flex flex-col items-center justify-center text-center">
          <BarChart3 className="w-8 h-8 text-gray-300 mb-2" />
          <p className="text-[13px] font-medium text-[var(--color-text-secondary)]">No issuance data yet</p>
          <p className="text-[11px] text-[var(--color-text-tertiary)]">Issue your first batch to see trend metrics</p>
        </div>
      ) : (
        <div className="space-y-2">
          {/* Bar Chart Representation */}
          <div className="h-48 flex items-end gap-2.5 pt-6 pb-2">
            {chartData.map((point, idx) => {
              const heightPct = Math.max(12, Math.round((point.value / maxValue) * 100));
              return (
                <div key={idx} className="flex-1 flex flex-col items-center gap-1.5 group h-full justify-end">
                  <div className="relative w-full flex justify-center">
                    <span className="absolute -top-7 opacity-0 group-hover:opacity-100 transition-opacity bg-gray-900 text-white text-[10px] font-bold px-1.5 py-0.5 rounded pointer-events-none whitespace-nowrap shadow-md">
                      {point.value.toLocaleString()} certs
                    </span>
                    <div
                      className="w-full max-w-[36px] bg-gradient-to-t from-indigo-600 to-indigo-400 rounded-t-lg transition-all duration-300 group-hover:brightness-110"
                      style={{ height: `${heightPct}%` }}
                    />
                  </div>
                  <span className="text-[10px] font-medium text-[var(--color-text-tertiary)] truncate w-full text-center">
                    {point.date}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
