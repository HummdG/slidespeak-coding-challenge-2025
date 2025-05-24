import React from "react";
import { PdfIcon } from "@/icons/PdfIcon";
import { CheckIcon } from "@/icons/CheckIcon";

export function ResultStep({ url, onReset }: { url: string; onReset(): void }) {
  return (
    <div className="max-w-md mx-auto">
      <div className="bg-white border border-gray-200 rounded-2xl p-8 shadow-sm text-center">
        <div className="relative inline-block mb-6">
          <PdfIcon />
          <div className="absolute -top-2 -right-2">
            <CheckIcon />
          </div>
        </div>

        <h3 className="text-lg font-semibold text-gray-900 mb-8">
          File converted successfully!
        </h3>

        <div className="flex gap-3">
          <button
            onClick={onReset}
            className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium"
          >
            Convert another
          </button>
          <button
            onClick={() => window.open(url, "_blank")}
            className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
          >
            Download file
          </button>
        </div>
      </div>
    </div>
  );
}
