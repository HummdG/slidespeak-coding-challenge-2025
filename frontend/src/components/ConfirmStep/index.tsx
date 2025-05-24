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
    <div className="bg-white p-6 rounded-2xl shadow-md">
      <p className="font-medium">{file.name}</p>
      <p className="text-sm text-gray-500">
        {(file.size / 1024 / 1024).toFixed(2)} MB
      </p>
      <div className="mt-4">
        <label className="inline-flex items-center">
          <input type="radio" checked readOnly className="mr-2" />
          Convert to PDF
        </label>
        <p className="text-xs text-gray-400">
          High fidelity conversion with images & formatting
        </p>
      </div>
      <div className="mt-6 flex justify-between">
        <button
          onClick={onCancel}
          className="px-4 py-2 border rounded hover:bg-gray-50"
        >
          Cancel
        </button>
        <button
          onClick={onConfirm}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Convert
        </button>
      </div>
    </div>
  );
}
