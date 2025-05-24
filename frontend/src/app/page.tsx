import React from "react";
import { ConverterFlow } from "@/components/ConverterFlow";

export default function Page() {
  return (
    <main className="min-h-screen bg-gray-100 py-12 px-4">
      <div className="w-full max-w-4xl mx-auto">
        <ConverterFlow />
      </div>
    </main>
  );
}
