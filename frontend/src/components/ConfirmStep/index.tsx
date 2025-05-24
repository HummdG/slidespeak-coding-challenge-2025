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
    <div className="max-w-md mx-auto">
      <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm">
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-1">
            {file.name}
          </h3>
          <p className="text-sm text-gray-500">
            {(file.size / 1024 / 1024).toFixed(2)} MB
          </p>
        </div>

        <div className="mb-6">
          <div className="flex items-start">
            <input
              type="radio"
              id="convert-pdf"
              checked
              readOnly
              className="mt-1 mr-3 text-blue-600"
            />
            <div>
              <label
                htmlFor="convert-pdf"
                className="font-medium text-gray-900 cursor-pointer"
              >
                Convert to PDF
              </label>
              <p className="text-sm text-gray-500 mt-1">
                Best quality, retains images and other assets.
              </p>
            </div>
          </div>
        </div>

        <div className="flex gap-3">
          <button
            onClick={onCancel}
            className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
          >
            Convert
          </button>
        </div>
      </div>
    </div>
  );
}
