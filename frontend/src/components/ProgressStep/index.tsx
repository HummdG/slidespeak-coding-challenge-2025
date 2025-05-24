// src/components/ProgressStep/index.tsx
"use client";

import React, { useEffect } from "react";
import { LoadingIndicatorIcon } from "@/icons/LoadingIndicatorIcon";

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
    <div className="max-w-md mx-auto">
      <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm">
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-1">
            Digital Marketing requirements.pptx
          </h3>
          <p className="text-sm text-gray-500">5.5 MB</p>
        </div>

        <div className="text-center mb-8">
          <div className="w-8 h-8 mx-auto mb-4">
            <div className="animate-spin">
              <LoadingIndicatorIcon />
            </div>
          </div>
          <p className="text-gray-700 font-medium select-none">
            Converting your file...
          </p>
        </div>

        <div className="flex gap-3">
          <button
            disabled
            className="flex-1 px-4 py-2 border border-gray-200 text-gray-400 rounded-lg cursor-not-allowed font-medium"
          >
            Cancel
          </button>
          <div className="flex-1"></div>
        </div>
      </div>
    </div>
  );
}
