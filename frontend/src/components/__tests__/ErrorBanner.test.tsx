// frontend/src/components/__tests__/ErrorBanner.test.tsx
import React from "react";
import { render, screen } from "@testing-library/react";
import { ErrorBanner } from "../ErrorBanner";

describe("ErrorBanner", () => {
  it("should render error message", () => {
    const errorMessage = "Something went wrong!";
    render(<ErrorBanner message={errorMessage} />);

    expect(screen.getByText(errorMessage)).toBeInTheDocument();
  });

  it("should have correct styling classes", () => {
    render(<ErrorBanner message="Test error" />);

    const errorBanner = screen.getByText("Test error").closest("div");
    expect(errorBanner).toHaveClass(
      "bg-red-50",
      "border-red-200",
      "text-red-800"
    );
  });
});
