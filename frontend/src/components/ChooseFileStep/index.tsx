import React from "react";
import UploadIcon from "@/icons/UploadIcon";

export function ChooseFileStep({ onSelect }: { onSelect(file: File): void }) {
  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const files = e.dataTransfer.files;
    if (files[0] && files[0].name.endsWith(".pptx")) {
      onSelect(files[0]);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  return (
    <div className="max-w-md mx-auto">
      <div
        className="border-2 border-dashed border-gray-300 rounded-2xl p-12 text-center bg-gray-50"
        onDrop={handleDrop}
        onDragOver={handleDragOver}
      >
        <div className="w-16 h-16 mx-auto mb-6 bg-blue-100 rounded-full flex items-center justify-center">
          <UploadIcon />
        </div>

        <h3 className="text-lg font-medium text-gray-900 mb-2">
          Drag and drop a PowerPoint file to convert to PDF.
        </h3>

        <input
          type="file"
          accept=".pptx"
          id="pptx-input"
          className="hidden"
          onChange={(e) => e.target.files?.[0] && onSelect(e.target.files[0])}
        />

        <label
          htmlFor="pptx-input"
          className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 cursor-pointer font-medium"
        >
          Choose file
        </label>
      </div>
    </div>
  );
}
