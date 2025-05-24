import React from "react";
import { ConverterFlow } from "@/components/ConverterFlow";

export default function Page() {
  return (
    <main className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-lg mx-auto">
        <ConverterFlow />
      </div>
    </main>
  );
}
