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
  const interval = Number(process.env.NEXT_PUBLIC_POLL_INTERVAL);
  const timeout = Number(process.env.NEXT_PUBLIC_POLL_TIMEOUT);

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
    <div className="p-6 rounded-2xl bg-white shadow-md text-center">
      <p>Converting your file…</p>
      <div className="mt-4 animate-spin border-4 border-blue-500 border-t-transparent rounded-full w-8 h-8 mx-auto" />
    </div>
  );
}
