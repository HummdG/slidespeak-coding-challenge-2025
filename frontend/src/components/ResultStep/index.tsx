import React from "react";
import { PdfIcon } from "@/icons/PdfIcon";
import { CheckIcon } from "@/icons/CheckIcon";

export function ResultStep({ url, onReset }: { url: string; onReset(): void }) {
  return (
    <div className="w-full max-w-2xl mx-auto">
      <div className="border-2 border-solid border-gray-300 rounded-2xl p-16 bg-white text-center">
        {/* PDF Icon with checkmark */}
        <div className="mb-8">
          <div className="relative inline-block">
            <PdfIcon />
            <div className="absolute -top-2 -right-2">
              <CheckIcon />
            </div>
          </div>
        </div>

        {/* Success message */}
        <h3 className="text-xl font-semibold text-gray-900 mb-12 select-none">
          File converted successfully!
        </h3>

        {/* Action buttons */}
        <div className="flex gap-4">
          <button
            onClick={onReset}
            className="flex-1 px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium select-none text-base bg-white"
          >
            Convert another
          </button>
          <button
            onClick={() => window.open(url, "_blank")}
            className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium select-none text-base"
          >
            Download file
          </button>
        </div>
      </div>
    </div>
  );
}
