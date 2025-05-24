// src/components/ProgressStep/index.tsx
"use client";

import React, { useEffect } from "react";

export function ProgressStep({
  jobId,
  onDone,
  onError,
}: {
  jobId: string;
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
            Digital Marketing requirements.pptx
          </h3>
          <p className="text-sm text-gray-500 mt-2">5.5 MB</p>
        </div>

        {/* Converting status with circular progress */}
        <div className="mb-8">
          <div className="bg-white border border-gray-200 rounded-lg p-6 text-left shadow-sm">
            <div className="flex items-center gap-3">
              {/* Circular progress ring */}
              <div className="relative w-6 h-6">
                <svg className="w-6 h-6 -rotate-90" viewBox="0 0 24 24">
                  <circle
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="2"
                    fill="none"
                    className="text-gray-200"
                  />
                  <circle
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="2"
                    fill="none"
                    strokeDasharray="62.83"
                    strokeDashoffset="20"
                    className="text-blue-600 animate-spin"
                    strokeLinecap="round"
                  />
                </svg>
              </div>
              <span className="text-base text-gray-700 select-none">
                Compressing your file...
              </span>
            </div>
          </div>
        </div>

        {/* Action buttons - Cancel disabled, Convert replaced with loading */}
        <div className="flex gap-4">
          <button
            disabled
            className="flex-1 px-6 py-3 border border-gray-200 text-gray-400 rounded-lg cursor-not-allowed font-medium select-none text-base bg-gray-50"
          >
            Cancel
          </button>
          <div className="flex-1 px-6 py-3 bg-blue-300 rounded-lg font-medium select-none text-base flex items-center justify-center">
            <svg
              className="w-5 h-5 mr-2 animate-spin"
              viewBox="0 0 24 24"
              fill="none"
            >
              <path
                fill="white"
                d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z"
                opacity="0.3"
              />
              <path
                fill="white"
                d="M12 2C17.52 2 22 6.48 22 12h-2C20 7.58 16.42 4 12 4V2z"
              />
            </svg>
            <span className="text-white text-base">Converting...</span>
          </div>
        </div>
      </div>
    </div>
  );
}
