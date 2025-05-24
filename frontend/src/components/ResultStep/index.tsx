import React from "react";

export function ResultStep({ url, onReset }: { url: string; onReset(): void }) {
  return (
    <div className="p-6 rounded-2xl bg-white shadow-md text-center">
      <img src="/pdf-icon.svg" alt="PDF icon" className="w-12 mx-auto" />
      <p className="mt-4 font-medium">File converted successfully!</p>
      <div className="mt-6 flex justify-between">
        <button
          onClick={onReset}
          className="px-4 py-2 border rounded hover:bg-gray-50"
        >
          Convert another
        </button>
        <button
          onClick={() => window.open(url, "_blank")}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Download PDF
        </button>
      </div>
    </div>
  );
}
