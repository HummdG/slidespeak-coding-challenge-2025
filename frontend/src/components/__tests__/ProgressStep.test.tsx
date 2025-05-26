import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import { ProgressStep } from "../ProgressStep";

// Mock fetch globally
global.fetch = jest.fn();

describe("ProgressStep", () => {
  const mockOnDone = jest.fn();
  const mockOnError = jest.fn();
  const mockFile = new File(["test"], "test.pptx", {
    type: "application/vnd.openxmlformats-officedocument.presentationml.presentation",
  });

  Object.defineProperty(mockFile, "size", {
    value: 1024 * 1024 * 2.5, // 2.5 MB
    writable: false,
  });

  beforeEach(() => {
    mockOnDone.mockClear();
    mockOnError.mockClear();
    (fetch as jest.Mock).mockClear();
    process.env.NEXT_PUBLIC_API_BASE_URL = "http://localhost:8000";
    process.env.NEXT_PUBLIC_POLL_INTERVAL = "100"; // Fast polling for tests
    process.env.NEXT_PUBLIC_POLL_TIMEOUT = "5000"; // Short timeout for tests
  });

  it("should render file info and progress indicators", () => {
    render(
      <ProgressStep
        jobId="test-job"
        file={mockFile}
        onDone={mockOnDone}
        onError={mockOnError}
      />
    );

    expect(screen.getByText("test.pptx")).toBeInTheDocument();
    expect(screen.getByText("2.50 MB")).toBeInTheDocument();
    expect(screen.getByText("Converting your file")).toBeInTheDocument();
  });

  it("should show upload status when no jobId", () => {
    render(
      <ProgressStep file={mockFile} onDone={mockOnDone} onError={mockOnError} />
    );

    expect(screen.getByText("Uploading your file")).toBeInTheDocument();
  });

  it("should poll for job status and call onDone when complete", async () => {
    (fetch as jest.Mock).mockResolvedValue({
      json: () =>
        Promise.resolve({
          status: "done",
          url: "https://example.com/file.pdf",
        }),
    });

    render(
      <ProgressStep
        jobId="test-job"
        file={mockFile}
        onDone={mockOnDone}
        onError={mockOnError}
      />
    );

    await waitFor(
      () => {
        expect(mockOnDone).toHaveBeenCalledWith("https://example.com/file.pdf");
      },
      { timeout: 1000 }
    );
  });

  it("should call onError when job fails", async () => {
    (fetch as jest.Mock).mockResolvedValue({
      json: () =>
        Promise.resolve({ status: "error", error: "Conversion failed" }),
    });

    render(
      <ProgressStep
        jobId="test-job"
        file={mockFile}
        onDone={mockOnDone}
        onError={mockOnError}
      />
    );

    await waitFor(
      () => {
        expect(mockOnError).toHaveBeenCalledWith("Conversion failed");
      },
      { timeout: 1000 }
    );
  });

  it("should handle network errors", async () => {
    (fetch as jest.Mock).mockRejectedValue(new Error("Network error"));

    render(
      <ProgressStep
        jobId="test-job"
        file={mockFile}
        onDone={mockOnDone}
        onError={mockOnError}
      />
    );

    await waitFor(
      () => {
        expect(mockOnError).toHaveBeenCalledWith("Network error while polling");
      },
      { timeout: 1000 }
    );
  });
});
