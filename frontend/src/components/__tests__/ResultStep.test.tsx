import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { ResultStep } from "../ResultStep";

// Mock window.open
const mockWindowOpen = jest.fn();
Object.defineProperty(window, "open", {
  value: mockWindowOpen,
  writable: true,
});

describe("ResultStep", () => {
  const mockOnReset = jest.fn();
  const testUrl = "https://example.com/file.pdf";

  beforeEach(() => {
    mockOnReset.mockClear();
    mockWindowOpen.mockClear();
  });

  it("should render success message and action buttons", () => {
    render(<ResultStep url={testUrl} onReset={mockOnReset} />);

    expect(
      screen.getByText("File converted successfully!")
    ).toBeInTheDocument();
    expect(screen.getByText("Convert another")).toBeInTheDocument();
    expect(screen.getByText("Download file")).toBeInTheDocument();
  });

  it("should handle convert another button click", () => {
    render(<ResultStep url={testUrl} onReset={mockOnReset} />);

    const convertAnotherButton = screen.getByText("Convert another");
    fireEvent.click(convertAnotherButton);

    expect(mockOnReset).toHaveBeenCalledTimes(1);
  });

  it("should handle download button click", () => {
    render(<ResultStep url={testUrl} onReset={mockOnReset} />);

    const downloadButton = screen.getByText("Download file");
    fireEvent.click(downloadButton);

    expect(mockWindowOpen).toHaveBeenCalledWith(testUrl, "_blank");
  });
});
