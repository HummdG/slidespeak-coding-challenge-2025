// src/components/ProgressStep/index.tsx
"use client";

import React, { useEffect } from "react";
import { LoadingIndicatorIcon } from "@/icons/LoadingIndicatorIcon";

export function ProgressStep({
  jobId,
  file,
  onDone,
  onError,
}: {
  jobId: string;
  file: File;
  onDone(url: string): void;
  onError(msg: string): void;
}) {
  const interval = Number(process.env.NEXT_PUBLIC_POLL_INTERVAL) || 2000;
  const timeout = Number(process.env.NEXT_PUBLIC_POLL_TIMEOUT) || 300000;

  useEffect(() => {
    const start = Date.now();
    const tick = setInterval(async () => {
      const elapsed = Date.now() - start;
      if (elapsed > timeout) {
        clearInterval(tick);
        return onError("Conversion timed out");
      }
      try {
        const res = await fetch(
          `${process.env.NEXT_PUBLIC_API_BASE_URL}/status/${jobId}`
        );
        const json = await res.json();
        if (json.status === "done" && json.url) {
          clearInterval(tick);
          onDone(json.url);
        } else if (json.status === "error") {
          clearInterval(tick);
          onError(json.error || "Conversion failed");
        }
      } catch {
        clearInterval(tick);
        onError("Network error while polling");
      }
    }, interval);
    return () => clearInterval(tick);
  }, [jobId]);

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div className="border-2 border-solid border-gray-300 rounded-2xl p-16 bg-white">
        {/* File info box */}
        <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6 text-center shadow-sm">
          <h3 className="text-lg font-medium text-gray-900 select-none">
            {file.name}
          </h3>
          <p className="text-sm text-gray-500 mt-2">
            {(file.size / 1024 / 1024).toFixed(2)} MB
          </p>
        </div>

        {/* Converting status with circular progress */}
        <div className="mb-8">
          <div className="bg-white border border-gray-200 rounded-lg p-6 text-left shadow-sm">
            <div className="flex items-center gap-3">
              {/* Circular progress ring */}
              <div className="bg-white select-none text-base flex items-center justify-center">
                <svg
                  className="w-8 h-8 animate-spin-pretty"
                  viewBox="0 0 24 24"
                  fill="none"
                >
                  <circle
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="#E5E7EB"
                    strokeWidth="3"
                  />
                  <circle
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="#3B82F6"
                    strokeWidth="3"
                    strokeLinecap="round"
                    strokeDasharray="31.416"
                    strokeDashoffset="23.562"
                    fill="none"
                  />
                </svg>
              </div>
              <span className="text-base text-gray-700 select-none">
                Converting your file
              </span>
            </div>
          </div>
        </div>

        {/* Action buttons - Cancel disabled, Convert with simple spinner */}
        <div className="flex gap-4">
          <button
            disabled
            className="flex-1 px-6 py-3 border border-gray-200 text-gray-400 rounded-lg cursor-not-allowed font-medium select-none text-base bg-gray-50"
          >
            Cancel
          </button>
          <div className="flex-1 px-6 py-3 bg-blue-300 rounded-lg font-medium select-none text-base flex items-center justify-center">
            <div className="animate-spin">
              <LoadingIndicatorIcon />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
