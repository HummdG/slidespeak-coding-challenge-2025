import React from "react";

export function ErrorBanner({ message }: { message: string }) {
  return (
    <div className="w-full max-w-2xl mx-auto mb-6">
      <div className="bg-red-50 border border-red-200 text-red-800 p-4 rounded-lg">
        <p className="font-medium text-sm">{message}</p>
      </div>
    </div>
  );
}
