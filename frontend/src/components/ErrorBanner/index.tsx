import React from "react";

export function ErrorBanner({ message }: { message: string }) {
  return (
    <div className="max-w-md mx-auto">
      <div className="bg-red-50 border border-red-200 text-red-800 p-4 rounded-lg">
        <p className="font-medium">{message}</p>
      </div>
    </div>
  );
}
