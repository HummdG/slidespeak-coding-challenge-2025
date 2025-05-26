import React from "react";
import UploadIcon from "@/icons/UploadIcon";

export function ChooseFileStep({ onSelect }: { onSelect(file: File): void }) {
  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const { files } = e.dataTransfer;
    if (files[0] && files[0].name.endsWith(".pptx")) {
      onSelect(files[0]);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div
        className="border-2 border-dashed border-gray-300 rounded-2xl p-16 text-center bg-white"
        onDrop={handleDrop}
        onDragOver={handleDragOver}
      >
        <div className="w-20 h-20 mx-auto mb-8 bg-blue-100 rounded-full flex items-center justify-center">
          <UploadIcon />
        </div>

        <p className="text-lg text-gray-700 mb-8 select-none">
          Drag and drop a PowerPoint file to convert to PDF.
        </p>

        <input
          type="file"
          accept=".pptx"
          id="pptx-input"
          className="hidden"
          onChange={e => e.target.files?.[0] && onSelect(e.target.files[0])}
        />

        <label
          htmlFor="pptx-input"
          className="inline-flex items-center px-8 py-3 bg-blue-50 text-blue-600 rounded-xl hover:bg-blue-100 cursor-pointer font-medium select-none text-base"
        >
          Choose file
        </label>
      </div>
    </div>
  );
}
