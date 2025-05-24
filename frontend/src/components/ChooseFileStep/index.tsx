import React from "react";

export function ChooseFileStep({ onSelect }: { onSelect(file: File): void }) {
  return (
    <div className="border-2 border-dashed rounded-2xl p-8 text-center">
      <input
        type="file"
        accept=".pptx"
        id="pptx-input"
        className="hidden"
        onChange={(e) => e.target.files?.[0] && onSelect(e.target.files[0])}
      />
      <label
        htmlFor="pptx-input"
        className="cursor-pointer px-4 py-2 bg-blue-100 text-blue-700 rounded"
      >
        Choose PowerPoint
      </label>
      <p className="mt-4 text-gray-500">
        Drag & drop or click to select a <code>.pptx</code> file.
      </p>
    </div>
  );
}
