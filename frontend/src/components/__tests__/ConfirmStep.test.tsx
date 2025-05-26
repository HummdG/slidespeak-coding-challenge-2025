// frontend/src/components/__tests__/ConfirmStep.test.tsx (FIX THE TYPO)
import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { ConfirmStep } from "../ConfirmStep";

describe("ConfirmStep", () => {
  const mockOnCancel = jest.fn();
  const mockOnConfirm = jest.fn();
  const mockFile = new File(["test"], "test.pptx", {
    type: "application/vnd.openxmlformats-officedocument.presentationml.presentation",
  });

  Object.defineProperty(mockFile, "size", {
    value: 1024 * 1024 * 2.5, // 2.5 MB
    writable: false,
  });

  beforeEach(() => {
    mockOnCancel.mockClear();
    mockOnConfirm.mockClear();
  });

  it("should render file info and conversion options", () => {
    render(
      <ConfirmStep
        file={mockFile}
        onCancel={mockOnCancel}
        onConfirm={mockOnConfirm}
      />
    );

    expect(screen.getByText("test.pptx")).toBeInTheDocument();
    expect(screen.getByText("2.50 MB")).toBeInTheDocument();
    expect(screen.getByText("Convert to PDF")).toBeInTheDocument();
  });

  it("should handle cancel button click", () => {
    render(
      <ConfirmStep
        file={mockFile}
        onCancel={mockOnCancel}
        onConfirm={mockOnConfirm}
      />
    );

    const cancelButton = screen.getByText("Cancel");
    fireEvent.click(cancelButton);

    expect(mockOnCancel).toHaveBeenCalledTimes(1);
  });

  it("should handle convert button click", () => {
    render(
      <ConfirmStep
        file={mockFile}
        onCancel={mockOnCancel}
        onConfirm={mockOnConfirm}
      />
    );

    const convertButton = screen.getByText("Convert");
    fireEvent.click(convertButton);

    expect(mockOnConfirm).toHaveBeenCalledTimes(1);
  });
});
