import React from "react";

export function ConfirmStep({
  file,
  onCancel,
  onConfirm,
}: {
  file: File;
  onCancel(): void;
  onConfirm(): void;
}) {
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

        {/* Conversion option box */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-8">
          <div className="flex items-start">
            <input
              type="radio"
              id="convert-pdf"
              checked
              readOnly
              className="mt-1 mr-4 text-blue-600"
            />
            <div>
              <label
                htmlFor="convert-pdf"
                className="font-semibold text-blue-900 cursor-pointer select-none text-base"
              >
                Convert to PDF
              </label>
              <p className="text-sm text-blue-700 mt-2 select-none">
                Best quality, retains images and other assets.
              </p>
            </div>
          </div>
        </div>

        {/* Action buttons */}
        <div className="flex gap-4">
          <button
            type="button"
            onClick={onCancel}
            className="flex-1 px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium select-none text-base bg-white"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={onConfirm}
            className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium select-none text-base"
          >
            Convert
          </button>
        </div>
      </div>
    </div>
  );
}
