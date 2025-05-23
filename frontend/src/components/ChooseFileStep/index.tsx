import { FC, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import UploadIcon from '@/icons/UploadIcon';

type ChooseFileStepProps = {
};

export const ChooseFileStep: FC<ChooseFileStepProps> = () => {
  const { getRootProps, getInputProps } = useDropzone({
  });

  return (
    <div
      className="group cursor-pointer rounded-xl border border-dashed border-gray-400 bg-white px-6 py-16"
      {...getRootProps()}
    >
      <input {...getInputProps()} />
      <div className="flex shrink-0 grow-0 flex-col items-center gap-2">
        <div className="mb-2 rounded-full bg-gray-100 p-2">
          <div className="grid place-items-center rounded-full bg-gray-200 p-2 [&>svg]:size-8">
            <UploadIcon />
          </div>
        </div>
        <p className="text-sm leading-8 text-gray-600">
          Drag and drop a PowerPoint file to convert to PDF.
        </p>
        <button
          type="button"
          className="rounded-lg bg-blue-50 px-4 py-2.5 text-sm text-blue-700 transition-colors group-hover:bg-blue-100"
        >
          Choose file
        </button>
      </div>
    </div>
  );
};
