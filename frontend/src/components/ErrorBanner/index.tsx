import React from "react";

export function ErrorBanner({ message }: { message: string }) {
  return (
    <div className="bg-red-100 text-red-800 p-3 rounded mb-4">{message}</div>
  );
}
