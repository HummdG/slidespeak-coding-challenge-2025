import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { ChooseFileStep } from "../ChooseFileStep";

describe("ChooseFileStep", () => {
  const mockOnSelect = jest.fn();

  beforeEach(() => {
    mockOnSelect.mockClear();
  });

  it("should render file upload interface", () => {
    render(<ChooseFileStep onSelect={mockOnSelect} />);

    expect(
      screen.getByText("Drag and drop a PowerPoint file to convert to PDF.")
    ).toBeInTheDocument();
    expect(screen.getByText("Choose file")).toBeInTheDocument();
  });

  it("should handle file input change", () => {
    render(<ChooseFileStep onSelect={mockOnSelect} />);

    const fileInput = screen.getByLabelText("Choose file") as HTMLInputElement;
    const mockFile = new File(["test"], "test.pptx", {
      type: "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    });

    fireEvent.change(fileInput, { target: { files: [mockFile] } });

    expect(mockOnSelect).toHaveBeenCalledWith(mockFile);
  });
});
