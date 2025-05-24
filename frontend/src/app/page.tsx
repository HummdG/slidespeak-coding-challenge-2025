import React from "react";
import { useConvert } from "@/hooks/useConvert";
import { ChooseFileStep } from "@/components/ChooseFileStep";
import { ConfirmStep } from "@/components/ConfirmStep";
import { ProgressStep } from "@/components/ProgressStep";
import { ResultStep } from "@/components/ResultStep";
import { ErrorBanner } from "@/components/ErrorBanner";

export default function Home() {
  const [state, actions] = useConvert();

  return (
    <main className="p-4 max-w-md mx-auto space-y-4">
      {state.error && <ErrorBanner message={state.error} />}

      {state.status === "idle" && <ChooseFileStep onSelect={actions.select} />}

      {state.status === "ready" && state.file && (
        <ConfirmStep
          file={state.file}
          onCancel={actions.reset}
          onConfirm={actions.upload}
        />
      )}

      {(state.status === "uploading" || state.status === "processing") &&
        state.jobId && (
          <ProgressStep
            jobId={state.jobId}
            onDone={actions.complete}
            onError={actions.fail}
          />
        )}

      {state.status === "done" && state.url && (
        <ResultStep url={state.url} onReset={actions.reset} />
      )}
    </main>
  );
}
